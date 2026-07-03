import os
import sys
sys.path.append('src')

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice
from video_editor import build_video, generate_thumbnail
from uploader import upload_all

def main():
    print("USA Shorts Bot v4.0 - Started 🇺🇸")

    topic = os.environ.get("VIDEO_TOPIC", "3 Scary True Stories That Happened at 3 AM")

    # 1. Script
    script_data = generate_script(topic)

    # 2. AI Images (Gemini first priority, HF fallback, placeholder as last resort)
    image_paths = generate_images(script_data['scenes'])
    if not image_paths:
        raise RuntimeError(
            "Koi bhi image nahi bani (Gemini, Hugging Face, placeholder sab fail) — "
            "pipeline rok rahe hain. GEMINI_API_KEY / HF_API_KEY aur assets/placeholder.png check karo."
        )

    # 3. Voice
    audio_path = generate_voice(script_data['voiceover'], voice="am_michael")

    # 4. Video build
    final_video = build_video(image_paths, audio_path, script_data['scenes'])

    # 5. Thumbnail
    thumb_path = generate_thumbnail(image_paths[0], script_data['title'])

    # 6. Upload
    upload_all(final_video, thumb_path, script_data)

    print("DONE. Video Live on YT + FB Shorts ✅")

if __name__ == "__main__":
    main()
