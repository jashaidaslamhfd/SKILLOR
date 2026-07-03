from moviepy.editor import *
import os
from PIL import Image, ImageDraw

def add_captions(video_clip, text):
    # Video par text overlay
    txt_clip = TextClip(text, fontsize=50, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
    txt_clip = txt_clip.set_position('bottom').set_duration(video_clip.duration)
    return CompositeVideoClip([video_clip, txt_clip])

def build_video(image_paths, audio_path, scenes):
    if not image_paths or len(image_paths) == 0:
        placeholder = "assets/placeholder.png"
        image_paths = [placeholder] * len(scenes)

    audio = AudioFileClip(audio_path)
    clips = []
    clip_duration = audio.duration / len(image_paths)

    for i, path in enumerate(image_paths):
        img_clip = ImageClip(path).set_duration(clip_duration)
        img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)
        
        # Scenes ke mutabiq caption add karna
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

def generate_thumbnail(image_path, title):
    # Thumbnail generation
    img = Image.open(image_path).resize((1280, 720))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), title, fill="white")
    
    if not os.path.exists("output"):
        os.makedirs("output")
        
    thumb_path = "output/thumbnail.jpg"
    img.save(thumb_path)
    return thumb_path
