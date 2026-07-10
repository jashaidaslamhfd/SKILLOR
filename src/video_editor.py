import os
import random
import logging
import numpy as np
import soundfile as sf
from moviepy.editor import (
    ImageClip, ColorClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, concatenate_audioclips,
    CompositeAudioClip,
)
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CANVAS_W, CANVAS_H = 1080, 1920
AUDIO_EDGE_FADE = 0.05       # tiny click-removal fade, does NOT change timing
ZOOM_AMOUNT = 0.18           # 1.0 -> 1.18 (or reverse) - clearly visible but not jarring
PAN_PX = 50                  # subtle horizontal drift in pixels
TARGET_MIN_SEC = 40
TARGET_MAX_SEC = 55

# ---------------------------------------------------------------------------
# Background music. Pure voiceover-over-silence reads as flat/lifeless,
# especially for a "dark mystery" tone where a low tension bed is expected.
# No real royalty-free-music CDN is reachable from this environment, so this
# synthesizes a procedural dark ambient drone (root + fifth + a slightly
# detuned layer for tension, plus a slow swell and a soft noise bed) instead
# of relying on an external audio library. If you later add real licensed
# tracks under assets/music/*.wav|mp3, drop them in - _get_music_track()
# prefers a real file when one exists and only falls back to the
# synthesized drone when the folder is empty.
# ---------------------------------------------------------------------------
MUSIC_DIR = "assets/music"
MUSIC_VOLUME = 0.15          # ducked well under the voice, just adds atmosphere
MUSIC_SAMPLE_RATE = 24000    # matches voice_generator.py's Kokoro output rate

# Caption safe-zone: Shorts/Reels UI (like/comment/share/follow buttons) sits
# on the right edge and bottom ~12-15% of the screen. Keep captions higher
# and centered so they're never covered by platform UI.
CAPTION_Y_FRACTION = 0.70


def _cover_fit(img_path: str, out_path: str, size=(CANVAS_W, CANVAS_H)):
    """Resize+crop an image to exactly fill `size` (cover-fit, like CSS
    background-size:cover), so every scene starts from an identical fixed
    canvas - required for Ken Burns zoom to stay centered instead of
    drifting off-frame."""
    img = Image.open(img_path).convert("RGB")
    target_w, target_h = size
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        # source wider than target -> match height, crop width
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))
    img.save(out_path)
    return out_path


def _ken_burns_clip(img_path: str, duration: float, direction: str) -> CompositeVideoClip:
    """Centered zoom (in or out) + a subtle horizontal pan, on a fixed
    1080x1920 canvas so the effect is clearly visible and never clips off
    the edge of frame."""
    prepped = img_path.replace(".png", "_fit.png").replace(".jpg", "_fit.jpg")
    _cover_fit(img_path, prepped)

    zoom_start, zoom_end = (1.0, 1.0 + ZOOM_AMOUNT) if direction == "in" else (1.0 + ZOOM_AMOUNT, 1.0)
    pan_dir = 1 if direction == "in" else -1

    base_clip = ImageClip(prepped).set_duration(duration)

    def scale_fn(t):
        frac = min(t / duration, 1.0) if duration > 0 else 0
        return zoom_start + (zoom_end - zoom_start) * frac

    def pos_fn(t):
        frac = min(t / duration, 1.0) if duration > 0 else 0
        s = scale_fn(t)
        w, h = CANVAS_W * s, CANVAS_H * s
        dx = pan_dir * PAN_PX * (frac - 0.5) * 2  # drifts from -PAN_PX to +PAN_PX (or reverse)
        x = (CANVAS_W - w) / 2 + dx
        y = (CANVAS_H - h) / 2
        return (x, y)

    zoomed = base_clip.resize(scale_fn).set_position(pos_fn)
    bg = ColorClip(size=(CANVAS_W, CANVAS_H), color=(0, 0, 0)).set_duration(duration)
    return CompositeVideoClip([bg, zoomed], size=(CANVAS_W, CANVAS_H)).set_duration(duration)


CAPTION_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CAPTION_FONT_SIZE = 72
CAPTION_STROKE_W = 4
CAPTION_MAX_WORDS_PER_LINE = 3  # punchy reels-style: short bursts, not full sentences


def _wrap_text(draw, text, font, max_width, max_words_per_line=CAPTION_MAX_WORDS_PER_LINE):
    """Groups words into short punchy lines (max N words each), still
    falling back to width-based splitting for unusually long words/lines."""
    words = text.split()
    lines, current = [], []
    for w in words:
        candidate = current + [w]
        test = " ".join(candidate)
        bbox = draw.textbbox((0, 0), test, font=font, stroke_width=CAPTION_STROKE_W)
        too_wide = (bbox[2] - bbox[0]) > max_width
        too_many = len(candidate) > max_words_per_line
        if (too_wide or too_many) and current:
            lines.append(" ".join(current))
            current = [w]
        else:
            current = candidate
    if current:
        lines.append(" ".join(current))
    return lines


CAPTION_MIN_FONT_SIZE = 40  # never shrink below this, even for very long captions


def _caption_clip(text: str, duration: float) -> ImageClip:
    """Renders the caption with PIL (transparent RGBA) instead of MoviePy's
    ImageMagick-dependent TextClip - avoids CI/environment fragility
    (missing ImageMagick binary, policy.xml 'not authorized' errors, etc.).

    Uses short, punchy 2-3-word lines (reels style). Font size auto-shrinks
    for longer captions so the block never overflows into the platform-UI
    safe zone at the bottom of the screen."""
    max_width = int(CANVAS_W * 0.82)
    # Available vertical room between where captions start (CAPTION_Y_FRACTION)
    # and the platform-UI safe zone near the bottom of the screen.
    available_height = int(CANVAS_H * (0.90 - CAPTION_Y_FRACTION))

    font_size = CAPTION_FONT_SIZE
    dummy = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy)

    while True:
        try:
            font = ImageFont.truetype(CAPTION_FONT_PATH, font_size)
        except Exception:
            font = ImageFont.load_default()
            break

        lines = _wrap_text(dummy_draw, text, font, max_width)
        line_height = int(font_size * 1.3)
        block_height = line_height * len(lines) + 20

        # Check the widest actual rendered line too - a single long word
        # (no spaces to wrap on) could still exceed max_width on its own.
        widest_line = max(
            (dummy_draw.textbbox((0, 0), ln, font=font, stroke_width=CAPTION_STROKE_W)[2] for ln in lines),
            default=0,
        )

        fits_vertically = block_height <= available_height
        fits_horizontally = widest_line <= max_width

        if (fits_vertically and fits_horizontally) or font_size <= CAPTION_MIN_FONT_SIZE:
            break
        font_size -= 4  # step down and re-wrap/re-measure until it fits both ways

    line_height = int(font_size * 1.3)
    img_h = max(line_height * len(lines) + 20, line_height)
    # Canvas matches the actual widest line (capped at max_width) so text is
    # never cropped by a canvas that's narrower than the text itself.
    widest_line = max(
        (dummy_draw.textbbox((0, 0), ln, font=font, stroke_width=CAPTION_STROKE_W)[2] for ln in lines),
        default=max_width,
    )
    canvas_w = min(max(widest_line, 1), max_width) + 40
    canvas = Image.new("RGBA", (canvas_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    y = 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=CAPTION_STROKE_W)
        line_w = bbox[2] - bbox[0]
        x = max((canvas.width - line_w) / 2, 0)  # never draw at a negative x (would clip the start of the line)
        draw.text((x, y), line, font=font, fill="white",
                   stroke_width=CAPTION_STROKE_W, stroke_fill="black")
        y += line_height

    frame = np.array(canvas)
    txt = ImageClip(frame).set_duration(duration)
    return txt.set_position(('center', CAPTION_Y_FRACTION), relative=True)


WORD_MIN_DURATION = 0.12  # floor per word so short words don't flash imperceptibly


def _word_by_word_clips(text: str, total_duration: float):
    """Splits a scene's caption into individual words and returns a list of
    ImageClips, each timed (via set_start/set_duration) to appear one at a
    time across the scene's real audio duration - a karaoke-style reveal
    instead of one static multi-word block.

    Timing is approximated by word length (longer words get proportionally
    more on-screen time) since we don't have true phoneme-level timestamps
    from the TTS engine - this keeps it reasonably close to natural speech
    pacing without needing forced-alignment tooling.
    """
    words = text.split()
    if not words:
        return []

    weights = [max(len(w), 3) for w in words]
    total_weight = sum(weights)

    # Give every word a small guaranteed floor, then distribute the rest
    # proportionally to word length.
    floor_total = WORD_MIN_DURATION * len(words)
    if floor_total >= total_duration:
        # Extreme case: too many words for too short a clip - just split evenly.
        per_word = total_duration / len(words)
        durations = [per_word] * len(words)
    else:
        remaining = total_duration - floor_total
        durations = [WORD_MIN_DURATION + remaining * (w / total_weight) for w in weights]

    clips = []
    t = 0.0
    for word, dur in zip(words, durations):
        clip = _caption_clip(word, dur).set_start(t)
        clips.append(clip)
        t += dur

    return clips


def _synthesize_ambient_bed(duration: float, seed: int = None) -> np.ndarray:
    """Procedural dark-ambient drone: a low root note + a fifth + a slightly
    detuned layer (for tension/dissonance), a slow volume swell so it isn't
    a static hum, and a soft filtered noise bed for texture. Not a real
    music track, but far better than dead silence under the voiceover."""
    rng = np.random.default_rng(seed)
    sr = MUSIC_SAMPLE_RATE
    n = max(int(sr * duration), sr)
    t = np.linspace(0, duration, n, endpoint=False)

    root = 48 + rng.uniform(-4, 4)  # low, sub-100Hz-ish root for a "dark" register
    freqs = [root, root * 1.5, root * 2.006]  # root, perfect fifth, detuned octave
    wave = np.zeros_like(t)
    for f in freqs:
        wave += 0.30 * np.sin(2 * np.pi * f * t)

    # Slow amplitude swell so the drone breathes instead of sitting static.
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t + rng.uniform(0, 2 * np.pi))
    wave *= lfo

    # Soft low-passed noise bed (air/texture), kept very quiet.
    noise = rng.normal(0, 1, size=t.shape)
    kernel = np.ones(300) / 300
    noise = np.convolve(noise, kernel, mode="same")
    wave += 0.04 * noise

    peak = np.abs(wave).max()
    if peak > 0:
        wave = wave / peak * 0.9
    return wave.astype(np.float32)


def _get_music_track(duration: float, output_dir: str) -> str:
    """Prefers a real licensed track from assets/music/ if one exists
    (random pick each video for variety); otherwise synthesizes an ambient
    drone bed sized to the video's duration."""
    if os.path.isdir(MUSIC_DIR):
        real_tracks = [
            os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR)
            if f.lower().endswith((".wav", ".mp3", ".m4a", ".ogg"))
        ]
        if real_tracks:
            return random.choice(real_tracks)

    os.makedirs(output_dir, exist_ok=True)
    music_path = os.path.join(output_dir, "bg_music.wav")
    bed = _synthesize_ambient_bed(duration, seed=random.randint(1, 999999))
    sf.write(music_path, bed, MUSIC_SAMPLE_RATE)
    return music_path


def build_video(image_paths, audio_segments, scenes, output_path="output/final_video.mp4"):
    """
    image_paths:   list of scene image file paths (len == len(scenes))
    audio_segments: list of {"path", "duration", "caption"} from
                     voice_generator.generate_voice_segments (len == len(scenes))
    scenes:        list of {"visual", "caption"} dicts

    Each clip's on-screen duration == its own audio segment's real duration,
    and its caption == the exact text spoken during that segment. This keeps
    voice + caption + clip locked together instead of guessing an even split.
    """
    assert len(image_paths) == len(audio_segments) == len(scenes), (
        "image_paths, audio_segments aur scenes ki length barabar honi chahiye "
        "warna sync toot jayega"
    )

    video_clips = []
    audio_clips = []

    for i, (img_path, seg) in enumerate(zip(image_paths, audio_segments)):
        duration = max(seg['duration'], 0.6)  # floor, avoid zero-length clips
        direction = "in" if i % 2 == 0 else "out"  # alternate zoom-in/zoom-out per scene

        scene_visual = _ken_burns_clip(img_path, duration, direction)
        caption_text = scenes[i].get('caption', seg.get('caption', ''))
        word_clips = _word_by_word_clips(caption_text, duration)

        combined = CompositeVideoClip([scene_visual] + word_clips, size=(CANVAS_W, CANVAS_H)).set_duration(duration)

        video_clips.append(combined)

        seg_audio = AudioFileClip(seg['path']).fx(afx.audio_fadein, AUDIO_EDGE_FADE).fx(afx.audio_fadeout, AUDIO_EDGE_FADE)
        audio_clips.append(seg_audio)

    logger.info("Concatenating video clips (hard-cut, matches the audio's hard-cut timing)...")
    final_video = concatenate_videoclips(video_clips, method="compose")

    logger.info("Concatenating audio segments (hard-cut, preserves exact voice timing)...")
    voice_audio = concatenate_audioclips(audio_clips)

    logger.info("Adding background music bed (ducked under the voice)...")
    music_path = _get_music_track(voice_audio.duration, os.path.dirname(output_path) or "output")
    music_clip = AudioFileClip(music_path).fx(afx.volumex, MUSIC_VOLUME)
    if music_clip.duration < voice_audio.duration:
        loops_needed = int(voice_audio.duration // music_clip.duration) + 1
        music_clip = concatenate_audioclips([music_clip] * loops_needed)
    music_clip = music_clip.subclip(0, voice_audio.duration).fx(afx.audio_fadein, 1.0).fx(afx.audio_fadeout, 1.0)

    final_audio = CompositeAudioClip([music_clip, voice_audio])
    final_video = final_video.set_audio(final_audio)

    # ---- Enforce 40-55s target by scaling video+audio together if needed ----
    duration = final_video.duration
    if duration < TARGET_MIN_SEC or duration > TARGET_MAX_SEC:
        target = TARGET_MIN_SEC if duration < TARGET_MIN_SEC else TARGET_MAX_SEC
        factor = duration / target
        factor = max(0.85, min(1.2, factor))  # keep the speed change subtle/natural
        logger.warning(f"Video duration {duration:.1f}s outside {TARGET_MIN_SEC}-{TARGET_MAX_SEC}s target - applying speedx factor {factor:.3f}")
        final_video = final_video.fx(vfx.speedx, factor)  # scales both video and its attached audio together
        logger.info(f"New duration after speed adjustment: {final_video.duration:.1f}s")
    else:
        logger.info(f"Video duration {duration:.1f}s within target range - no adjustment needed")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    logger.info(f"Writing video to {output_path}...")
    final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", bitrate="6000k")
    logger.info(f"Video created successfully: {output_path} ({final_video.duration:.1f}s)")

    return output_path


def generate_thumbnail(image_path: str, title: str, output_path: str = "output/thumbnail.jpg") -> str:
    """Was referenced by main.py but never defined - fixed here.
    Builds a 1280x720 YouTube-style thumbnail from the first scene image
    with the title overlaid."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    canvas = Image.new("RGB", (1280, 720), (0, 0, 0))
    src = Image.open(image_path).convert("RGB")

    # cover-fit the source image into the 16:9 thumbnail canvas
    src_ratio = src.width / src.height
    target_ratio = 1280 / 720
    if src_ratio > target_ratio:
        new_h = 720
        new_w = int(new_h * src_ratio)
    else:
        new_w = 1280
        new_h = int(new_w / src_ratio)
    src = src.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - 1280) // 2
    top = (new_h - 720) // 2
    src = src.crop((left, top, left + 1280, top + 720))
    canvas.paste(src, (0, 0))

    # Dark gradient strip at bottom so text stays legible
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    strip_top = 720 - 220
    for y in range(strip_top, 720):
        alpha = int(180 * (y - strip_top) / 220)
        draw.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(canvas)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 64)
    except Exception:
        font = ImageFont.load_default()

    # simple word-wrap
    words = title.upper().split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        if draw.textlength(test, font=font) > 1150:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)

    y = 720 - 40 - (len(lines) * 74)
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (1280 - w) / 2
        draw.text((x, y), line, font=font, fill="white", stroke_width=3, stroke_fill="black")
        y += 74

    canvas.save(output_path, quality=92)
    logger.info(f"Thumbnail saved: {output_path}")
    return output_path
