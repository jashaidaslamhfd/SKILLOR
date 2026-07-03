from moviepy.editor import *
import os

def add_captions(video_clip, text):
    # Yeh function video ke upar text likhega
    txt_clip = TextClip(text, fontsize=50, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
    txt_clip = txt_clip.set_position('bottom').set_duration(video_clip.duration)
    return CompositeVideoClip([video_clip, txt_clip])

def build_video(image_paths, audio_path, scenes):
    # --- SAFETY NET ---
    if not image_paths or len(image_paths) == 0:
        print("CRITICAL: Koi image nahi mili, placeholder use kar rahe hain.")
        placeholder = "assets/placeholder.png"
        image_paths = [placeholder] * len(scenes)

    # Audio load karo
    audio = AudioFileClip(audio_path)
    
    # Clips list banao
    clips = []
    clip_duration = audio.duration / len(image_paths)

    for i, path in enumerate(image_paths):
        # Image clip load karo
        img_clip = ImageClip(path).set_duration(clip_duration)
        
        # Ken Burns effect (zoom)
        img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)
        
        # Agar captions hain to add karo (yahan scenes list se text le rahe hain)
        if i < len(scenes):
            img_clip = add_captions(img_clip, scenes[i])
            
        clips.append(img_clip)

    # Video Assemble
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    
    # Save video
    if not os.path.exists("output"):
        os.makedirs("output")
        
    output_path = "output/final_video.mp4"
    video.write_videofile(output_path, fps=24)
    
    return output_path
