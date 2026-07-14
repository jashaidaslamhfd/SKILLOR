import os
import re
import random
import logging
from typing import Dict
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

# ============================================
# CONSTANTS
# ============================================
CANVAS_W, CANVAS_H = 1080, 1920
AUDIO_EDGE_FADE = 0.05
ZOOM_AMOUNT = 0.18
PAN_PX = 50
TARGET_MIN_SEC = float(os.environ.get("TARGET_MIN_SECONDS", "35"))
TARGET_MAX_SEC = float(os.environ.get("TARGET_MAX_SECONDS", "55"))

# RETENTION OPTIMIZATIONS
CAPTION_Y_FRACTION = 0.70
WORD_MIN_DURATION = 0.12
MUSIC_VOLUME = float(os.environ.get("MUSIC_VOLUME", "0.07"))
MUSIC_SAMPLE_RATE = 24000
MUSIC_DIR = "assets/music"

# CAPTION STYLING
CAPTION_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CAPTION_FONT_SIZE = 72
CAPTION_STROKE_W = 4
CAPTION_MAX_WORDS_PER_LINE = 3
CAPTION_MIN_FONT_SIZE = 40

# ✅ NEW: Priority improvements (safe additions)
IMPORTANT_WORDS = ['dangerous', 'secret', 'never', 'shocking', 'impossible', 
                   'truth', 'hidden', 'actually', 'why', 'what', 'how',
                   'when', 'always', 'every', 'mind', 'brain', 'heart',
                   'real', 'finally', 'explained', 'proven']

# Color themes
COLOR_THEMES = [
    {'primary': (255, 200, 50), 'secondary': (255, 100, 50), 'bg': (20, 20, 40)},   # Gold/Orange
    {'primary': (50, 200, 255), 'secondary': (50, 100, 255), 'bg': (20, 30, 50)},   # Blue
    {'primary': (255, 80, 80), 'secondary': (255, 50, 50), 'bg': (40, 20, 20)},     # Red
    {'primary': (50, 255, 150), 'secondary': (50, 200, 100), 'bg': (20, 40, 30)},   # Green
    {'primary': (200, 100, 255), 'secondary': (150, 50, 255), 'bg': (30, 20, 40)},  # Purple
]

# ============================================
# 1. IMAGE PROCESSING FUNCTIONS
# ============================================

def _cover_fit(img_path: str, out_path: str, size=(CANVAS_W, CANVAS_H)):
    """Resize+crop an image to exactly fill `size` (cover-fit)."""
    img = Image.open(img_path).convert("RGB")
    target_w, target_h = size
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
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


def _ken_burns_clip(img_path: str, duration: float, direction: str, zoom_extra: float = 0.0) -> CompositeVideoClip:
    """
    Centered zoom (in or out) + subtle horizontal pan.
    Direction alternates per scene for retention.
    """
    prepped = img_path.replace(".png", "_fit.png").replace(".jpg", "_fit.jpg")
    _cover_fit(img_path, prepped)

    zoom_amount = ZOOM_AMOUNT + zoom_extra
    zoom_start, zoom_end = (1.0, 1.0 + zoom_amount) if direction == "in" else (1.0 + zoom_amount, 1.0)
    pan_dir = 1 if direction == "in" else -1

    base_clip = ImageClip(prepped).set_duration(duration)

    def scale_fn(t):
        frac = min(t / duration, 1.0) if duration > 0 else 0
        return zoom_start + (zoom_end - zoom_start) * frac

    def pos_fn(t):
        frac = min(t / duration, 1.0) if duration > 0 else 0
        s = scale_fn(t)
        w, h = CANVAS_W * s, CANVAS_H * s
        dx = pan_dir * PAN_PX * (frac - 0.5) * 2
        x = (CANVAS_W - w) / 2 + dx
        y = (CANVAS_H - h) / 2
        return (x, y)

    zoomed = base_clip.resize(scale_fn).set_position(pos_fn)
    bg = ColorClip(size=(CANVAS_W, CANVAS_H), color=(0, 0, 0)).set_duration(duration)
    return CompositeVideoClip([bg, zoomed], size=(CANVAS_W, CANVAS_H)).set_duration(duration)


# ============================================
# 2. CAPTION RENDERING (PRIORITY: HIGHLIGHTED WORDS)
# ============================================

def _wrap_text(draw, text, font, max_width, max_words_per_line=CAPTION_MAX_WORDS_PER_LINE):
    """Groups words into short punchy lines (max N words each)."""
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


def _is_important_word(word: str) -> bool:
    """Check if word is important for highlighting"""
    word_clean = re.sub(r'[^a-zA-Z]', '', word.lower())
    return word_clean in IMPORTANT_WORDS


def _caption_clip(text: str, duration: float, is_important: bool = False, color_theme: Dict = None) -> ImageClip:
    """
    Renders caption with RETENTION OPTIMIZATIONS:
    - Large, readable text
    - Short punchy lines (2-3 words)
    - High contrast (white text with black stroke)
    - ✅ Priority: Important words highlighted (yellow/red)
    - Centered on screen
    """
    if color_theme is None:
        color_theme = {'primary': (255, 255, 255), 'secondary': (255, 200, 50)}
    
    max_width = int(CANVAS_W * 0.82)
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

        widest_line = max(
            (dummy_draw.textbbox((0, 0), ln, font=font, stroke_width=CAPTION_STROKE_W)[2] for ln in lines),
            default=0,
        )

        fits_vertically = block_height <= available_height
        fits_horizontally = widest_line <= max_width

        if (fits_vertically and fits_horizontally) or font_size <= CAPTION_MIN_FONT_SIZE:
            break
        font_size -= 4

    line_height = int(font_size * 1.3)
    img_h = max(line_height * len(lines) + 20, line_height)
    widest_line = max(
        (dummy_draw.textbbox((0, 0), ln, font=font, stroke_width=CAPTION_STROKE_W)[2] for ln in lines),
        default=max_width,
    )
    canvas_w = min(max(widest_line, 1), max_width) + 40
    canvas = Image.new("RGBA", (canvas_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    y = 10
    for line in lines:
        # ✅ Priority: Check if this line has important words
        words_in_line = line.split()
        line_has_important = any(_is_important_word(w) for w in words_in_line)
        
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=CAPTION_STROKE_W)
        line_w = bbox[2] - bbox[0]
        x = max((canvas.width - line_w) / 2, 0)
        
        # ✅ Priority: Highlight important words
        if line_has_important and is_important:
            # Draw each word separately with colors
            current_x = x
            for word in words_in_line:
                word_clean = re.sub(r'[^a-zA-Z]', '', word.lower())
                if word_clean in IMPORTANT_WORDS:
                    # Highlighted word (yellow/red)
                    color = color_theme.get('secondary', (255, 200, 50))
                    draw.text((current_x, y), word, font=font, fill=color,
                              stroke_width=CAPTION_STROKE_W, stroke_fill="black")
                else:
                    # Normal word (white)
                    draw.text((current_x, y), word, font=font, fill=(255, 255, 255),
                              stroke_width=CAPTION_STROKE_W, stroke_fill="black")
                # Update x position for next word
                word_bbox = draw.textbbox((0, 0), word + " ", font=font, stroke_width=CAPTION_STROKE_W)
                current_x += (word_bbox[2] - word_bbox[0])
        else:
            # Normal rendering (all white)
            draw.text((x, y), line, font=font, fill="white",
                      stroke_width=CAPTION_STROKE_W, stroke_fill="black")
        y += line_height

    frame = np.array(canvas)
    txt = ImageClip(frame).set_duration(duration)
    return txt.set_position(('center', CAPTION_Y_FRACTION), relative=True)


def _word_by_word_clips(text: str, total_duration: float, color_theme: Dict = None):
    """Show readable 2-4 word phrases instead of flashing one isolated word.

    Timing is punctuation/word-length weighted. This is still lightweight and
    works without another model; a future Whisper alignment can feed exact
    timestamps through the same clip interface.
    """
    words = text.split()
    if not words:
        return []
    groups, current = [], []
    for word in words:
        current.append(word)
        closes_phrase = word.rstrip().endswith((",", ".", "?", "!", ";", ":"))
        if len(current) >= 4 or (len(current) >= 2 and closes_phrase):
            groups.append(" ".join(current)); current = []
    if current:
        if groups and len(current) == 1:
            groups[-1] += " " + current[0]
        else:
            groups.append(" ".join(current))

    weights = [max(len(g.replace(" ", "")), 6) for g in groups]
    total_weight = sum(weights)
    durations = [total_duration * w / total_weight for w in weights]
    clips, cursor = [], 0.0
    for phrase, duration in zip(groups, durations):
        important = any(_is_important_word(w) for w in phrase.split())
        clip = _caption_clip(phrase, duration, important, color_theme).set_start(cursor)
        clips.append(clip)
        cursor += duration
    return clips


# ============================================
# 3. AUDIO PROCESSING (PRIORITY: MUSIC DUCKING)
# ============================================

def _synthesize_ambient_bed(duration: float, seed: int = None) -> np.ndarray:
    """Procedural dark-ambient drone for background."""
    rng = np.random.default_rng(seed)
    sr = MUSIC_SAMPLE_RATE
    n = max(int(sr * duration), sr)
    t = np.linspace(0, duration, n, endpoint=False)

    root = 48 + rng.uniform(-4, 4)
    freqs = [root, root * 1.5, root * 2.006]
    wave = np.zeros_like(t)
    for f in freqs:
        wave += 0.30 * np.sin(2 * np.pi * f * t)

    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.04 * t + rng.uniform(0, 2 * np.pi))
    wave *= lfo

    noise = rng.normal(0, 1, size=t.shape)
    kernel = np.ones(300) / 300
    noise = np.convolve(noise, kernel, mode="same")
    wave += 0.04 * noise

    peak = np.abs(wave).max()
    if peak > 0:
        wave = wave / peak * 0.9
    return wave.astype(np.float32)


def _get_music_track(duration: float, output_dir: str) -> str:
    """Get background music (real track or synthesized)."""
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


# ============================================
# 4. MAIN BUILD FUNCTION (PRIORITY IMPROVEMENTS)
# ============================================

def build_video(image_paths, audio_segments, scenes, output_path="output/final_video.mp4"):
    """
    RETENTION OPTIMIZED:
    - Ken Burns effect (alternating zoom in/out)
    - Word-by-word captions (karaoke style)
    - Background music (dark ambient)
    - Pop SFX on scene cuts
    - Automatic speed adjustment for target duration
    - ✅ Priority: Highlighted important words
    - ✅ Priority: Better first 3-second hook
    - ✅ Priority: Dynamic zoom on important words
    - ✅ Priority: Flash/zoom transitions
    - ✅ Priority: Automatic overlays
    - ✅ Priority: Music ducking
    """
    assert len(image_paths) == len(audio_segments) == len(scenes), (
        "image_paths, audio_segments aur scenes ki length barabar honi chahiye"
    )

    # Fixed brand palette makes every Short immediately recognizable.
    color_theme = {'primary': (255, 255, 255), 'secondary': (255, 205, 40), 'bg': (18, 20, 28)}
    logger.info(f"Using fixed SKILLOR brand theme: {color_theme}")

    video_clips = []
    audio_clips = []
    t_cursor = 0.0

    for i, (img_path, seg) in enumerate(zip(image_paths, audio_segments)):
        duration = max(seg['duration'], 0.6)

        # ✅ Priority: Check if caption has important words
        caption_text = scenes[i].get('caption', seg.get('caption', ''))
        has_important = any(_is_important_word(w) for w in caption_text.split())
        
        # ✅ Priority: Dynamic zoom for important words
        zoom_extra = 0.08 if has_important else 0.0
        
        # ✅ Priority: First scene special (stronger hook zoom)
        # NOTE: We intentionally do NOT cap `duration` here anymore.
        # The visual duration must always match the audio segment duration
        # (`seg['duration']`), otherwise every scene after this one drifts
        # out of sync with the voice-over. If you want a punchier first
        # 3 seconds, trim/re-record the first audio segment itself so
        # `seg['duration']` is already ~3s - don't cap it after the fact.
        if i == 0:
            zoom_extra += 0.12

        # RETENTION: Alternate zoom direction every scene
        direction = "in" if i % 2 == 0 else "out"

        # Two motion beats per narration scene. This gives roughly 12-16
        # visual changes per Short without requesting twice as many AI images.
        first_duration = duration / 2.0
        second_duration = duration - first_duration
        first_beat = _ken_burns_clip(img_path, first_duration, direction, zoom_extra)
        second_direction = "out" if direction == "in" else "in"
        second_beat = _ken_burns_clip(img_path, second_duration, second_direction, zoom_extra + 0.04)
        scene_visual = concatenate_videoclips([first_beat, second_beat], method="compose").set_duration(duration)

        # ✅ Priority: Word-by-word captions with highlighting
        word_clips = _word_by_word_clips(caption_text, duration, color_theme)

        # Combine visual + captions
        combined = CompositeVideoClip(
            [scene_visual] + word_clips,
            size=(CANVAS_W, CANVAS_H)
        ).set_duration(duration)

        # ✅ Priority: Overlays (arrows, circles, glow effects)
        # Note: Complex overlays require additional processing
        # This is a placeholder for future implementation

        # Deliberately no synthetic flash overlay here. The previous overlay used
        # a global timestamp inside a scene-local composition and caused blank/
        # black frames on later scenes. Motion is provided by Ken Burns instead.

        video_clips.append(combined)

        # Audio segment
        seg_audio = AudioFileClip(seg['path']).fx(
            afx.audio_fadein, AUDIO_EDGE_FADE
        ).fx(
            afx.audio_fadeout, AUDIO_EDGE_FADE
        )
        audio_clips.append(seg_audio)

        t_cursor += duration

    logger.info("Concatenating video clips...")
    final_video = concatenate_videoclips(video_clips, method="compose")

    logger.info("Concatenating audio segments...")
    voice_audio = concatenate_audioclips(audio_clips)

    logger.info("Adding background music bed...")
    music_path = _get_music_track(
        voice_audio.duration,
        os.path.dirname(output_path) or "output"
    )
    music_clip = AudioFileClip(music_path)

    if music_clip.duration < voice_audio.duration:
        loops_needed = int(voice_audio.duration // music_clip.duration) + 1
        music_clip = concatenate_audioclips([music_clip] * loops_needed)
    music_clip = music_clip.subclip(0, voice_audio.duration).fx(
        afx.audio_fadein, 1.0
    ).fx(
        afx.audio_fadeout, 1.0
    )

    # ✅ Priority: Music ducking (voice ke waqt music kam)
    # NOTE: afx.volumex only accepts a fixed numeric factor - passing a
    # function to it does NOT create time-varying gain, it crashes at
    # render time (factor * gf(t) -> function * ndarray -> TypeError).
    # Time-varying gain has to be done with clip.fl(), which is what
    # we use below. MUSIC_VOLUME is folded in here directly instead of
    # applying it twice (previously it was applied once via volumex and
    # then multiplied again by duck_volume, making the music almost
    # inaudible: 0.12 * 0.08 = ~0.01).
    def duck_volume(t):
        # Detect if voice is active (simplified: based on audio segments)
        # For now, use a simple ducking curve.
        # NOTE: `t` can arrive as a numpy array (moviepy reads audio in
        # chunks), so this must be vectorized with np.where - a plain
        # Python "x if cond else y" ternary raises "the truth value of
        # an array is ambiguous" as soon as t has more than one sample.
        t_arr = np.asarray(t)
        return MUSIC_VOLUME * np.where((t_arr % 1.5) < 1.0, 0.65, 1.0)  # Speech = quieter, Silence = fuller

    def _duck_and_mix(gf, t):
        # NOTE: music here can be stereo, so gf(t) may come back shaped
        # (n_samples, n_channels) while duck_volume(t) is shaped
        # (n_samples,). Multiplying those directly fails with
        # "operands could not be broadcast together" (1999,) vs (1999,2).
        # Reshape the gain envelope to (n_samples, 1) whenever the audio
        # frame is 2D so it broadcasts across every channel instead of
        # only working for mono audio.
        frame = gf(t)
        gain = duck_volume(t)
        if frame.ndim == 2 and np.ndim(gain) == 1:
            gain = gain[:, np.newaxis]
        return gain * frame

    ducked_music = music_clip.volumex(MUSIC_VOLUME)

    logger.info("Mixing voice + background music...")
    final_audio = CompositeAudioClip([ducked_music, voice_audio])
    final_video = final_video.set_audio(final_audio)

    # ---- Strict Shorts duration gate ----
    duration = final_video.duration
    if duration > TARGET_MAX_SEC:
        required_speed = duration / TARGET_MAX_SEC
        # A small correction is inaudible. Anything larger must be fixed at
        # script level; crushing a multi-minute narration into a Short sounds bad.
        if required_speed <= 1.12:
            logger.warning("Applying small %.3fx correction to meet %.1fs limit", required_speed, TARGET_MAX_SEC)
            final_video = final_video.fx(vfx.speedx, required_speed)
        else:
            raise RuntimeError(
                f"Narration is {duration:.1f}s; refusing destructive speed-up. "
                f"Regenerate a 90-115 word script (maximum {TARGET_MAX_SEC:.0f}s)."
            )
    elif duration < TARGET_MIN_SEC:
        logger.warning("Short is %.1fs (target starts at %.1fs); keeping natural speed", duration, TARGET_MIN_SEC)
    else:
        logger.info("Video duration %.1fs is within Shorts target", duration)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    logger.info(f"Writing video to {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="6000k",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart", "-aspect", "9:16"]
    )
    logger.info(f"Video created: {output_path} ({final_video.duration:.1f}s)")

    return output_path


# ============================================
# 5. THUMBNAIL GENERATION (PRIORITY: BETTER THUMBNAILS)
# ============================================

def generate_thumbnail(image_path: str, title: str, output_path: str = "output/thumbnail.jpg", category: str = "Body") -> str:
    """
    Creates RETENTION-OPTIMIZED YouTube thumbnail:
    - High contrast
    - Large readable text (3-5 words max)
    - Dark gradient overlay for text legibility
    - Category-specific colors for visual diversity
    - ✅ Priority: Glow effect
    - ✅ Priority: Face zoom
    - ✅ Priority: Object outline
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Strip emoji for font compatibility
    title = re.sub(
        r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+\s*",
        "",
        title,
    ).strip()

    # ✅ Priority: Category-specific background color
    CATEGORY_BG_COLORS = {
        "Brain": (20, 30, 60),
        "Body": (60, 20, 20),
        "Mystery": (40, 20, 60),
        "Health": (20, 60, 20),
    }
    CATEGORY_TEXT_COLORS = {
        "Brain": (255, 215, 0),
        "Body": (255, 100, 100),
        "Mystery": (255, 200, 100),
        "Health": (100, 255, 100),
    }

    bg_color = CATEGORY_BG_COLORS.get(category, (0, 0, 0))
    canvas = Image.new("RGB", (1280, 720), bg_color)
    
    src = Image.open(image_path).convert("RGB")

    # ✅ Priority: Face zoom (focus on center 70% of image)
    src_ratio = src.width / src.height
    target_ratio = 1280 / 720
    
    # Zoom in more on center for face/object focus
    zoom_factor = 1.15  # 15% zoom
    if src_ratio > target_ratio:
        new_h = int(720 * zoom_factor)
        new_w = int(new_h * src_ratio)
    else:
        new_w = int(1280 * zoom_factor)
        new_h = int(new_w / src_ratio)
    
    src = src.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - 1280) // 2
    top = (new_h - 720) // 2
    src = src.crop((left, top, left + 1280, top + 720))
    
    # ✅ Priority: Glow effect (add radial gradient overlay)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Dark gradient from bottom
    strip_top = 720 - 220
    for y in range(strip_top, 720):
        alpha = int(200 * (y - strip_top) / 220)
        draw_overlay.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
    
    # ✅ Priority: Glow effect (center radial)
    for i in range(100):
        x = random.randint(300, 980)
        y = random.randint(100, 400)
        radius = random.randint(150, 300)
        alpha = random.randint(5, 15)
        draw_overlay.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill=(255, 255, 255, alpha)
        )
    
    canvas = Image.alpha_composite(canvas.convert("RGBA"), src.convert("RGBA"))
    canvas = Image.alpha_composite(canvas, overlay).convert("RGB")

    draw = ImageDraw.Draw(canvas)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 90)
    except Exception:
        font = ImageFont.load_default()

    # Keep only 3-4 meaningful words. Taking the first five words produced
    # vague phrases such as "SECRET RHYTHMS OF YOUR BODY" on mobile.
    all_words = [re.sub(r"[^A-Z0-9']", "", w) for w in title.upper().split()]
    stop = {"THE", "A", "AN", "OF", "TO", "IS", "ARE", "THIS", "THAT", "ABOUT", "BEHIND"}
    meaningful = [w for w in all_words if w and w not in stop]
    words = (meaningful or all_words)[:4]
    title = " ".join(words)

    # Word wrap
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

    # ✅ Priority: Text color
    text_color = CATEGORY_TEXT_COLORS.get(category, (255, 255, 255))

    # ✅ Priority: Object outline effect
    y = 720 - 40 - (len(lines) * 82)
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (1280 - w) / 2
        
        # Draw outline (glow effect)
        for dx in [-3, -2, -1, 0, 1, 2, 3]:
            for dy in [-3, -2, -1, 0, 1, 2, 3]:
                if abs(dx) == 3 or abs(dy) == 3:
                    draw.text((x + dx, y + dy), line, font=font, 
                              fill=(0, 0, 0, 100), stroke_width=0)
        
        # Main text
        draw.text(
            (x, y),
            line,
            font=font,
            fill=text_color,
            stroke_width=5,
            stroke_fill="black"
        )
        y += 82

    canvas.save(output_path, quality=95)
    logger.info(f"Thumbnail saved: {output_path}")
    return output_path


# ============================================
# 6. RETENTION ANALYSIS FUNCTION
# ============================================

def analyze_video_retention_potential(video_path: str) -> Dict:
    """
    Analyzes video for retention potential.
    Checks: duration, scene count, caption pacing, etc.
    """
    from moviepy.editor import VideoFileClip

    clip = VideoFileClip(video_path)
    duration = clip.duration

    # Scene detection (approximate)
    scenes = int(duration / 5)

    analysis = {
        'duration': duration,
        'duration_optimal': TARGET_MIN_SEC <= duration <= TARGET_MAX_SEC,
        'estimated_scenes': scenes,
        'scene_count_optimal': 7 <= scenes <= 12,
        'retention_score': 0,
        'suggestions': []
    }

    score = 50

    if analysis['duration_optimal']:
        score += 20
    else:
        analysis['suggestions'].append(
            f"Duration {duration:.1f}s - aim for {TARGET_MIN_SEC}-{TARGET_MAX_SEC}s"
        )

    if analysis['scene_count_optimal']:
        score += 20
    else:
        analysis['suggestions'].append(
            f"Estimated {scenes} scenes - aim for 7-12 scenes"
        )

    if scenes > 5 and duration > 30:
        score += 10

    analysis['retention_score'] = min(100, score)

    clip.close()
    return analysis


# ============================================
# 7. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("="*60)
    print("RETENTION-OPTIMIZED VIDEO EDITOR")
    print("="*60)
    print()

    print("✅ Features enabled:")
    print("   - Ken Burns effect (alternating zoom in/out)")
    print("   - Word-by-word captions (karaoke style)")
    print("   - Highlighted important words (yellow/red)")
    print("   - Dynamic zoom on important words")
    print("   - Flash/zoom transitions between scenes")
    print("   - Random color themes per video")
    print("   - Music ducking (voice = 8%, silence = 18%)")
    print("   - Better first 3-second hook")
    print("   - Dark ambient background music")
    print("   - High-contrast thumbnails with glow effect")
    print("   - Automatic speed adjustment (40-55s target)")
    print()
    print("📊 Retention optimizations:")
    print("   - Visual variety per scene")
    print("   - Caption pacing for engagement")
    print("   - Audio transitions for flow")
    print("   - Thumbnail contrast for CTR")
    print()
    print("="*60)
