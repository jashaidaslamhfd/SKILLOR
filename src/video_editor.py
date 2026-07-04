from moviepy.editor import *
from PIL import Image

def build_video(image_paths, audio_path, scenes):
    """
    Fixed build_video function with:
    1. Zoom/Pan Effect (Ken Burns)
    2. Correct Captions (using actual scene text)
    3. Smooth Transitions
    """
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    duration_per_image = total_duration / len(image_paths)
    
    video_clips = []
    
    for i, img_path in enumerate(image_paths):
        # 1. Image Clip with Zoom Effect
        clip = ImageClip(img_path).set_duration(duration_per_image)
        # Ken Burns: 1x to 1.1x zoom
        clip = clip.resize(lambda t: 1 + 0.02 * t)
        
        # 2. Fix for Captions: Voiceover script segment use karein
        # 'scenes[i]['text']' mein aapka actual voiceover text hona chahiye
        txt = scenes[i].get('text', ' ') if i < len(scenes) else " "
        
        text_clip = TextClip(
            txt, 
            fontsize=50, 
            color='white', 
            font='DejaVu-Sans-Bold', # Ensure system font path is correct
            stroke_color='black', 
            stroke_width=2, 
            method='caption', 
            size=(1080 * 0.8, None), 
            align='center'
        ).set_position(('center', 0.85), relative=True).set_duration(duration_per_image)
        
        # 3. Combine Image + Text
        video = CompositeVideoClip([clip, text_clip])
        
        # 4. Smooth Transition
        if i > 0:
            video = video.crossfadein(0.5)
            
        video_clips.append(video)
        
    # Final Concatenation
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    output_path = "output/final_video.mp4"
    final_video.write_videofile(output_path, fps=24, codec="libx264")
    
    return output_path
