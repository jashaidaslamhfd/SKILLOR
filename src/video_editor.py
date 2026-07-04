import os
import random
import logging
import numpy as np
from moviepy.editor import (
    ImageClip, ColorClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, concatenate_audioclips,
)
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CANVAS_W, CANVAS_H = 1080, 1920
CROSSFADE_SEC = 0.4          # visual overlap between scenes
AUDIO_EDGE_FADE = 0.05       # tiny click-removal fade, does NOT change timing
ZOOM_AMOUNT = 0.18           # 1.0 -> 1.18 (or reverse) - clearly visible but not jarring
PAN_PX = 50                  # subtle horizontal drift in pixels
TARGET_MIN_SEC = 40
TARGET_MAX_SEC = 55

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
CAPTION_FONT_SIZE = 58
CAPTION_STROKE_W = 3


def _wrap_text(draw, text, font, max_width):
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font, stroke_width=CAPTION_STROKE_W)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def _caption_clip(text: str, duration: float) -> ImageClip:
    """Renders the caption with PIL (transparent RGBA) instead of MoviePy's
    ImageMagick-dependent TextClip - avoids CI/environment fragility
    (missing ImageMagick binary, policy.xml 'not authorized' errors, etc.)."""
    max_width = int(CANVAS_W * 0.82)

    try:
        font = ImageFont.truetype(CAPTION_FONT_PATH, CAPTION_FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy)
    lines = _wrap_text(dummy_draw, text, font, max_width)

    line_height = int(CAPTION_FONT_SIZE * 1.3)
    img_h = max(line_height * len(lines) + 20, line_height)
    canvas = Image.new("RGBA", (max_width + 40, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    y = 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=CAPTION_STROKE_W)
        line_w = bbox[2] - bbox[0]
        x = (canvas.width - line_w) / 2
        draw.text((x, y), line, font=font, fill="white",
                   stroke_width=CAPTION_STROKE_W, stroke_fill="black")
        y += line_height

    frame = np.array(canvas)
    txt = ImageClip(frame).set_duration(duration)
    return txt.set_position(('center', CAPTION_Y_FRACTION), relative=True)


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
        caption = _caption_clip(caption_text, duration)

        combined = CompositeVideoClip([scene_visual, caption], size=(CANVAS_W, CANVAS_H)).set_duration(duration)

        if i > 0:
            combined = combined.crossfadein(CROSSFADE_SEC)
        video_clips.append(combined)

        seg_audio = AudioFileClip(seg['path']).fx(afx.audio_fadein, AUDIO_EDGE_FADE).fx(afx.audio_fadeout, AUDIO_EDGE_FADE)
        audio_clips.append(seg_audio)

    logger.info("Concatenating video clips (with crossfade overlap)...")
    final_video = concatenate_videoclips(video_clips, method="compose", padding=-CROSSFADE_SEC)

    logger.info("Concatenating audio segments (hard-cut, preserves exact voice timing)...")
    final_audio = concatenate_audioclips(audio_clips)

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
