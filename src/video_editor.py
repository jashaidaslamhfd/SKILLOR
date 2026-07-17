import os
import re
import random
import logging
from typing import Dict, List
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Compatibility shim for moviepy 1.x with modern Pillow
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

from moviepy.editor import (
    ImageClip, ColorClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, concatenate_audioclips,
    CompositeAudioClip,
)
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx

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

# IMPORTANT WORDS (highlighted for retention)
IMPORTANT_WORDS = ['dangerous', 'secret', 'never', 'shocking', 'impossible',
                   'truth', 'hidden', 'actually', 'why', 'what', 'how',
                   'when', 'always', 'every', 'mind', 'brain', 'heart',
                   'real', 'finally', 'explained', 'proven', 'terrifying',
                   'disturbing', 'nightmare', 'warning', 'deadly', 'killer',
                   'poison', 'toxic', 'cancer', 'disease', 'death', 'kill',
                   'destroy', 'damage', 'harm', 'risk', 'threat', 'danger']

# Color themes
COLOR_THEMES = [
    {'primary': (255, 200, 50), 'secondary': (255, 100, 50), 'bg': (20, 20, 40)},  # Gold/Orange
    {'primary': (50, 200, 255), 'secondary': (50, 100, 255), 'bg': (20, 30, 50)},  # Blue
    {'primary': (255, 80, 80), 'secondary': (255, 50, 50), 'bg': (40, 20, 20)},     # Red
    {'primary': (50, 255, 150), 'secondary': (50, 200, 100), 'bg': (20, 40, 30)},  # Green
    {'primary': (200, 100, 255), 'secondary': (150, 50, 255), 'bg': (30, 20, 40)},  # Purple
]

# Visual effects for retention
VISUAL_EFFECTS = [
    "zoom_in", "zoom_out", "pan_left", "pan_right",
    "pulse", "shake", "glitch", "flash"
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

# ============================================
# 2. VISUAL EFFECTS (RETENTION BOOSTERS)
# ============================================

def _apply_vignette(clip, intensity=0.3):
    """Apply vignette effect to draw attention to center."""
    def vignette(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        mask = 1 - np.clip(R * intensity, 0, 1)
        mask = np.dstack([mask] * 3)
        return (frame * mask).astype(np.uint8)
    
    return clip.fl(vignette)

def _apply_color_grade(clip, warmth=0.1, contrast=1.1):
    """Apply color grading for cinematic look."""
    def grade(get_frame, t):
        frame = get_frame(t).astype(np.float32)
        # Increase contrast
        frame = (frame - 128) * contrast + 128
        # Add warmth
        frame[:, :, 0] += warmth * 20  # Red channel
        frame[:, :, 2] -= warmth * 10  # Blue channel
        return np.clip(frame, 0, 255).astype(np.uint8)
    
    return clip.fl(grade)

def _apply_pulse(clip, frequency=2.0, amplitude=0.02):
    """Apply subtle pulse effect (heartbeat-like) for tension."""
    def pulse(get_frame, t):
        frame = get_frame(t)
        scale = 1.0 + amplitude * np.sin(2 * np.pi * frequency * t)
        h, w = frame.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        # Simple resize-based pulse
        from PIL import Image as PILImage
        img = PILImage.fromarray(frame)
        img = img.resize((new_w, new_h), PILImage.LANCZOS)
        
        # Crop back to original size (center)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img = img.crop((left, top, left + w, top + h))
        
        return np.array(img)
    
    return clip.fl(pulse)

def _apply_shake(clip, intensity=5):
    """Apply subtle shake effect for intensity."""
    def shake(get_frame, t):
        frame = get_frame(t)
        dx = int(intensity * np.sin(t * 10))
        dy = int(intensity * np.cos(t * 8))
        
        # Roll the frame
        frame = np.roll(frame, dy, axis=0)
        frame = np.roll(frame, dx, axis=1)
        return frame
    
    return clip.fl(shake)

def _apply_flash(clip, start_time=0.1, duration=0.05):
    """Apply flash effect at the start (attention grabber)."""
    def flash(get_frame, t):
        frame = get_frame(t)
        if start_time <= t <= start_time + duration:
            # White flash
            intensity = 1.0 - (t - start_time) / duration
            frame = (frame * (1 - intensity) + 255 * intensity).astype(np.uint8)
        return frame
    
    return clip.fl(flash)

def _apply_zoom_transition(clip, zoom_in=True, factor=0.15):
    """Apply smooth zoom transition."""
    duration = clip.duration
    if zoom_in:
        start_scale, end_scale = 1.0, 1.0 + factor
    else:
        start_scale, end_scale = 1.0 + factor, 1.0
    
    def scale_fn(t):
        frac = min(t / duration, 1.0) if duration > 0 else 0
        return start_scale + (end_scale - start_scale) * frac
    
    return clip.resize(scale_fn)

# ============================================
# 3. KEN BURNS CLIP WITH EFFECTS
# ============================================

def _ken_burns_clip(img_path: str, duration: float, direction: str, 
                     zoom_extra: float = 0.0, effect: str = None) -> CompositeVideoClip:
    """
    Centered zoom (in or out) + subtle horizontal pan + visual effects.
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
    clip = CompositeVideoClip([bg, zoomed], size=(CANVAS_W, CANVAS_H)).set_duration(duration)

    # Apply visual effect based on scene type
    if effect == "pulse":
        clip = _apply_pulse(clip, frequency=1.5, amplitude=0.01)
    elif effect == "shake":
        clip = _apply_shake(clip, intensity=3)
    elif effect == "vignette":
        clip = _apply_vignette(clip, intensity=0.4)
    elif effect == "flash":
        clip = _apply_flash(clip, start_time=0.05, duration=0.08)

    return clip

# ============================================
# 4. CAPTION RENDERING (RETENTION OPTIMIZED)
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
    """Check if word is important for highlighting."""
    word_clean = re.sub(r'[^a-zA-Z]', '', word.lower())
    return word_clean in IMPORTANT_WORDS

def _caption_clip(text: str, duration: float, is_important: bool = False, 
                  color_theme: Dict = None, effect: str = None) -> ImageClip:
    """
    Renders caption with RETENTION OPTIMIZATIONS:
    - Large, readable text
    - Short punchy lines (2-3 words)
    - High contrast (white text with black stroke)
    - Important words highlighted (yellow/red)
    - Centered on screen
    - Optional text effects (fade, slide, pop)
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
        words_in_line = line.split()
        line_has_important = any(_is_important_word(w) for w in words_in_line)

        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=CAPTION_STROKE_W)
        line_w = bbox[2] - bbox[0]
        x = max((canvas.width - line_w) / 2, 0)

        # Highlight important words
        if line_has_important:
            # Yellow/gold color for important lines
            color = color_theme.get('secondary', (255, 200, 50))
        else:
            color = color_theme.get('primary', (255, 255, 255))

        # Draw text with stroke
        draw.text((x, y), line, font=font, fill=color, stroke_width=CAPTION_STROKE_W, stroke_fill=(0, 0, 0))
        y += line_height

    # Position caption on screen
    caption_img = ImageClip(canvas, transparent=True)
    caption_y = int(CANVAS_H * CAPTION_Y_FRACTION)
    
    # Apply text effect
    if effect == "fade_in":
        caption_img = caption_img.set_position(('center', caption_y)).set_duration(duration).fadein(0.3)
    elif effect == "slide_up":
        def slide_pos(t):
            progress = min(t / 0.3, 1.0) if duration > 0 else 1
            offset = int(50 * (1 - progress))
            return ('center', caption_y + offset)
        caption_img = caption_img.set_position(slide_pos).set_duration(duration)
    elif effect == "pop":
        def pop_scale(t):
            if t < 0.1:
                return 1.0 + 0.2 * (1 - t / 0.1)
            return 1.0
        caption_img = caption_img.set_position(('center', caption_y)).set_duration(duration).resize(pop_scale)
    else:
        caption_img = caption_img.set_position(('center', caption_y)).set_duration(duration)

    return caption_img

# ============================================
# 5. THUMBNAIL GENERATION
# ============================================

def generate_thumbnail(img_path: str, title: str) -> str:
    """Generate eye-catching thumbnail."""
    out_path = "output/thumbnail.jpg"
    os.makedirs("output", exist_ok=True)
    
    try:
        img = Image.open(img_path).convert("RGB")
        img = _cover_fit(img_path, out_path)
        img = Image.open(out_path)
        
        # Add text overlay
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(CAPTION_FONT_PATH, 80)
        except Exception:
            font = ImageFont.load_default()
        
        # Wrap title
        words = title.split()
        lines = []
        current = []
        for w in words:
            test = " ".join(current + [w])
            bbox = draw.textbbox((0, 0), test, font=font, stroke_width=4)
            if (bbox[2] - bbox[0]) > CANVAS_W * 0.85 and current:
                lines.append(" ".join(current))
                current = [w]
            else:
                current.append(w)
        if current:
            lines.append(" ".join(current))
        
        # Draw text
        y = int(CANVAS_H * 0.1)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
            x = (CANVAS_W - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, font=font, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
            y += int((bbox[3] - bbox[1]) * 1.2)
        
        img.save(out_path)
        return out_path
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        return out_path

# ============================================
# 6. MAIN VIDEO BUILD FUNCTION
# ============================================

def build_video(image_paths: List[str], audio_segments: List[Dict], scenes: List[Dict]) -> str:
    """Build final video with visual effects for retention."""
    out_path = "output/final_video.mp4"
    os.makedirs("output", exist_ok=True)
    
    clips = []
    color_theme = random.choice(COLOR_THEMES)
    
    for i, (img_path, audio, scene) in enumerate(zip(image_paths, audio_segments, scenes)):
        duration = float(audio.get("duration", 0))
        if duration <= 0:
            duration = 5.0
        
        # Determine effect based on scene position
        if i == 0:
            # Hook scene - flash + zoom in
            direction = "in"
            effect = "flash"
        elif i == len(image_paths) - 1:
            # Final scene - zoom out + vignette
            direction = "out"
            effect = "vignette"
        elif i <= 2:
            # Suspense scenes - pulse
            direction = "in" if i % 2 == 0 else "out"
            effect = "pulse"
        else:
            # Problem/Solution - shake or zoom
            direction = "in" if i % 2 == 0 else "out"
            effect = random.choice(["shake", None, None])  # Less frequent shake
        
        # Create visual clip with Ken Burns + effect
        clip = _ken_burns_clip(img_path, duration, direction, effect=effect)
        
        # Add caption
        caption_text = scene.get("caption", "") or scene.get("text", "")
        if caption_text:
            caption = _caption_clip(
                caption_text, 
                duration, 
                color_theme=color_theme,
                effect="fade_in" if i == 0 else None
            )
            clip = CompositeVideoClip([clip, caption], size=(CANVAS_W, CANVAS_H))
        
        clips.append(clip)
    
    # Concatenate all clips
    final = concatenate_videoclips(clips, method="compose")
    
    # Add audio
    audio_clips = []
    for audio_seg in audio_segments:
        audio_path = audio_seg.get("path", "")
        if audio_path and os.path.isfile(audio_path):
            audio_clip = AudioFileClip(audio_path).set_start(sum(float(a.get("duration", 0)) for a in audio_segments[:audio_segments.index(audio_seg)]))
            audio_clips.append(audio_clip)
    
    if audio_clips:
        combined_audio = CompositeAudioClip(audio_clips)
        final = final.set_audio(combined_audio)
    
    # Write final video
    final.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", threads=2, logger=None)
    
    logger.info(f"Video created: {out_path} ({final.duration:.1f}s)")
    return out_path
