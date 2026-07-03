import os
import sys
sys.path.append('src') # src folder ko path me add kiya

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice
from video_editor import build_video, add_captions
from uploader import upload_all

def main():
    print("USA Shorts Bot v4.0 = English Edition Started 🇺🇸")

    # 1. TOPIC YAHAN LIKHO - USA Viral Topic
    topic = "3 Scary True Stories That Happened at 3 AM" 
    
    # 1. Script from Groq - English
    script_data = generate_script(topic)
    print(f"Topic: {script_data['title']}")
    print(f"Script: {script_data['voiceover'][:100]}...")

    # 2. 9 AI Images from SDXL
    image_paths = generate_images(script_data['scenes'])

    # 3. Kokoro Voice = US Male, 10/10 Human
    audio_path = generate_voice(script_data['voiceover'], voice="am_michael") # USA Voice

    # 4. WhisperX Captions = Word by Word Sync, English
    video_no_cap = build_video(image_paths, audio_path, script_data['scenes'])
    final_video = add_captions(video_no_cap, audio_path)

    # 5. Upload YT + FB Shorts
    upload_all(final_video, script_data['title'], script_data['voiceover'])
    
    print("DONE. Video Live on YT + FB Shorts ✅")

if __name__ == "__main__":
    main()
