import os, json
from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice # gTTS hata diy
from video_generator import generate_video
from uploader import upload_all

def main():
    print("MrNextep Auto Shorts v3.0 = Kokoro Edition Started")
    
    # 1. Script from Groq
    script_data = generate_script()
    print(f"Topic: {script_data['title']}")
    
    # 2. 9 AI Images from HuggingFace SDXL
    image_paths = generate_images(script_data['scenes'])
    
    # 3. Kokoro Voice = US Male, 10/10 Human
    audio_path = generate_voice(script_data['voiceover'], voice="am_adam")
    
    # 4. WhisperX Captions = Word by Word Sync
    video_no_cap = build_video(image_paths, audio_path, script_data['title'])
    final_video = add_captions(video_no_cap, audio_path)
    
    # 5. Upload YT + FB
    upload_all(final_video, script_data['title'], script_data['desc'], script_data['tags'])
    
    print("DONE. Video Live on YT + FB")

if __name__ == "__main__":
    main()
