from moviepy.editor import *
import os
from PIL import Image, ImageDraw, ImageFont

PLACEHOLDER = "assets/placeholder.png"


def add_captions(video_clip, text):
    # Video par text overlay - method='caption' + size se text wrap hoti hai,
    # warna lambe captions 9:16 frame se bahar overflow ho jate the.
    txt_clip = TextClip(
        text,
        fontsize=50,
        color='white',
        # 'Arial-Bold' Ubuntu CI runner par installed nahi hota (crash deta tha).
        # Workflow mein 'fonts-dejavu-core' install hota hai, isliye wahi font use karo.
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(int(video_clip.w * 0.9), None),
        align='center',
    )
    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(video_clip.duration)
    return CompositeVideoClip([video_clip, txt_clip])


def build_video(image_paths, audio_path, scenes):
    if not image_paths or len(image_paths) == 0:
        if os.path.exists(PLACEHOLDER):
            image_paths = [PLACEHOLDER] * len(scenes)
        else:
            raise RuntimeError(
                f"Koi image generate nahi hui aur placeholder bhi missing hai ({PLACEHOLDER}). "
                "assets/placeholder.png check karo."
            )

    audio = AudioFileClip(audio_path)
    clips = []
    clip_duration = audio.duration / len(image_paths)

    for i, path in enumerate(image_paths):
        img_clip = ImageClip(path).set_duration(clip_duration)
        img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)

        if i < len(scenes):
            img_clip = add_captions(img_clip, scenes[i])

        clips.append(img_clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    if not os.path.exists("output"):
        os.makedirs("output")

    output_path = "output/final_video.mp4"
    video.write_videofile(output_path, fps=24)
    return output_path


def _load_font(size):
    # Multiple common paths try karo, warna PIL ka tiny default bitmap font
    # aa jata tha jo thumbnail par bilkul readable nahi hota.
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansBold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def generate_thumbnail(image_path, title):
    img = Image.open(image_path).convert("RGB")

    # Scene images 9:16 (vertical) hoti hain, thumbnail canvas 1280x720 (16:9,
    # horizontal) hai. Pehle wala code seedha .resize() kar deta tha jisse
    # image squish/stretch ho kar distorted dikhti thi. Ab center-crop karke
    # aspect ratio preserve karte hain.
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

    img = img.resize((target_w, target_h))
    draw = ImageDraw.Draw(img, "RGBA")
    font = _load_font(64)

    bbox = draw.textbbox((0, 0), title, font=font)
    text_h = bbox[3] - bbox[1]

    # Text ke peeche semi-transparent band, warna background busy hone par
    # title readable nahi hota
    draw.rectangle([0, target_h - text_h - 70, target_w, target_h], fill=(0, 0, 0, 160))
    draw.text(
        (40, target_h - text_h - 45),
        title,
        fill="white",
        font=font,
        stroke_width=2,
        stroke_fill="black",
    )

    if not os.path.exists("output"):
        os.makedirs("output")

    thumb_path = "output/thumbnail.jpg"
    img.save(thumb_path, quality=92)
    return thumb_path
