from moviepy.editor import *
import os

def build_video(image_paths, audio_path, scenes):
    # --- SAFETY NET ---
    # Agar images nahi mili to placeholder use karo
    if not image_paths or len(image_paths) == 0:
        print("CRITICAL: Koi image nahi mili, placeholder use kar rahe hain.")
        placeholder = "assets/placeholder.png"
        image_paths = [placeholder] * len(scenes)

    # Audio load karo
    audio = AudioFileClip(audio_path)
    
    # Clips list banao
    clips = []
    clip_duration = audio.duration / len(image_paths)

    for path in image_paths:
        # Image clip load karo
        img_clip = ImageClip(path).set_duration(clip_duration)
        # Ken Burns effect (zoom)
        img_clip = img_clip.resize(lambda t: 1 + 0.02 * t)
        clips.append(img_clip)

    # Video Assemble
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    
    # Save video (Output folder zaroori hai)
    if not os.path.exists("output"):
        os.makedirs("output")
        
    output_path = "output/final_video.mp4"
    video.write_videofile(output_path, fps=24)
    
    return output_path
