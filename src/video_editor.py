from moviepy.editor import *
import os
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PLACEHOLDER = "assets/placeholder.png"


def add_captions(video_clip, text):
    """Add captions to video clip with proper text wrapping and styling."""
    if not text:
        return video_clip
    
    try:
        txt_clip = TextClip(
            text,
            fontsize=50,
            color='white',
            font='DejaVu-Sans-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(int(video_clip.w * 0.9), None),
            align='center',
        )
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(video_clip.duration)
        return CompositeVideoClip([video_clip, txt_clip])
    except Exception as e:
        logger.error(f"Error adding captions: {e}")
        return video_clip


def build_video(image_paths, audio_path, scenes):
    """Build video from images and audio with improved error handling."""
    try:
        if not image_paths or len(image_paths) == 0:
            if os.path.exists(PLACEHOLDER):
                logger.warning("No images provided, using placeholder")
                image_paths = [PLACEHOLDER] * len(scenes)
            else:
                raise RuntimeError(
                    f"Koi image generate nahi hui aur placeholder bhi missing hai ({PLACEHOLDER}). "
                    "assets/placeholder.png check karo."
                )

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Loading audio from {audio_path}")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        logger.info(f"Audio duration: {audio_duration:.2f}s")

        clips = []
        clip_duration = audio_duration / len(image_paths)
        logger.info(f"Clip duration per image: {clip_duration:.2f}s")

        for i, path in enumerate(image_paths):
            try:
                if not os.path.exists(path):
                    logger.warning(f"Image not found: {path}, using placeholder")
                    if os.path.exists(PLACEHOLDER):
                        path = PLACEHOLDER
                    else:
                        raise FileNotFoundError(f"Image {path} not found and no placeholder available")

                logger.info(f"Processing image {i+1}/{len(image_paths)}: {path}")
                img_clip = ImageClip(path).set_duration(clip_duration)
                
                # Apply smooth zoom effect
                img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)

                # Add captions if available
                if i < len(scenes) and scenes[i]:
                    img_clip = add_captions(img_clip, scenes[i])

                clips.append(img_clip)
            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")
                raise

        logger.info("Concatenating video clips...")
        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio)

        # Create output directory
        os.makedirs("output", exist_ok=True)

        output_path = "output/final_video.mp4"
        logger.info(f"Writing video to {output_path}...")
        video.write_videofile(output_path, fps=24, verbose=False, logger=None)
        
        # Cleanup
        audio.close()
        for clip in clips:
            clip.close()
        video.close()
        
        logger.info(f"Video created successfully: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Video building failed: {e}")
        raise RuntimeError(f"Video building error: {e}")


def _load_font(size):
    """Load TrueType font with fallback to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansBold.ttf",
        "/System/Library/Fonts/Arial Bold.ttf",  # macOS
        "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                logger.warning(f"Failed to load font {path}: {e}")
    logger.warning("Using default font (no TrueType available)")
    return ImageFont.load_default()


def generate_thumbnail(image_path, title):
    """Generate thumbnail with proper aspect ratio handling."""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Generating thumbnail from {image_path}")
        img = Image.open(image_path).convert("RGB")

        # Center-crop to maintain aspect ratio
        target_w, target_h = 1280, 720
        src_w, src_h = img.size
        target_ratio = target_w / target_h
        src_ratio = src_w / src_h

        if src_ratio > target_ratio:
            new_w = int(src_h * target_ratio)
            left = (src_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, src_h))
        else:
            new_h = int(src_w / target_ratio)
            top = (src_h - new_h) // 2
            img = img.crop((0, top, src_w, top + new_h))

        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img, "RGBA")
        font = _load_font(64)

        # Calculate text bbox
        bbox = draw.textbbox((0, 0), title, font=font)
        text_h = bbox[3] - bbox[1]

        # Add semi-transparent background for text
        draw.rectangle(
            [0, target_h - text_h - 70, target_w, target_h],
            fill=(0, 0, 0, 160)
        )
        
        # Draw title text
        draw.text(
            (40, target_h - text_h - 45),
            title,
            fill="white",
            font=font,
            stroke_width=2,
            stroke_fill="black",
        )

        os.makedirs("output", exist_ok=True)

        thumb_path = "output/thumbnail.jpg"
        img.save(thumb_path, quality=92, optimize=True)
        logger.info(f"Thumbnail saved: {thumb_path}")
        return thumb_path
    
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        raise RuntimeError(f"Thumbnail generation error: {e}")
