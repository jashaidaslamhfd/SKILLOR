import os, json, time
from script_generator import generate_script
from image_generator import generate_images
from video_editor import make_video
from uploader import upload_all

def main():
    print("Bismillah... Bot Started")
    try:
        # 1. SCRIPT: 40-55 Sec + Shocking Hook + CTA
        script_data = generate_script(niche="Baby Psychology")
        assert 40 <= script_data['duration'] <= 55, "Duration Fail: Anti-Spam Rule"

        # 2. IMAGES: 100% AI. Pexels = 0%
        image_paths = generate_images(script_data['scenes'])
        assert len(image_paths) >= 9, "Image Count Fail"

        # 3. VIDEO: Ken Burns + Word Level Caption Sync
        video_path, thumb_path = make_video(script_data, image_paths)

        # 4. UPLOAD: YT + FB + Insta
        upload_all(video_path, thumb_path, script_data)

        print(f"SUCCESS: {script_data['title']} Uploaded")

    except Exception as e:
        print(f"FATAL ERROR: {e}") # Log ban jayega GitHub Actions me
        exit(1) # Fail ho jaye to pata chal jaye

if __name__ == "__main__":
    main()
