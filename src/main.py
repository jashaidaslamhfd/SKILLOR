import os
import sys
sys.path.append('src')

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice
from video_editor import build_video, generate_thumbnail # add_captions yahan se hataya
from uploader import upload_all

def main():
    print("USA Shorts Bot v4.0 - English Edition Started 🇺🇸")

    topic = os.environ.get("VIDEO_TOPIC", "3 Scary True Stories That Happened at 3 AM")

    # 1. Script
    script_data = generate_script(topic)
    
    # 2. AI Images
    image_paths = generate_images(script_data['scenes'])

    # 3. Voice
    audio_path = generate_voice(script_data['voiceover'], voice="am_michael")

    # 4. Video build (Captioning ab build_video ke andar handle ho rahi hai)
    # Humein sirf build_video call karna hai, add_captions alag se call nahi karna
    final_video = build_video(image_paths, audio_path, script_data['scenes'])
    
    # Thumbnail
    thumb_path = generate_thumbnail(image_paths[0], script_data['title'])

    # 5. Upload
    upload_all(final_video, thumb_path, script_data)

    print("DONE. Video Live on YT + FB Shorts ✅")

if __name__ == "__main__":
    main()
