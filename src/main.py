import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice
from video_editor import build_video, generate_thumbnail
from uploader import upload_all

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main pipeline for generating and uploading YouTube/Facebook Shorts.
    """
    try:
        logger.info("USA Shorts Bot v5.0 - Started 🇺🇸")
        logger.info("="*60)
        
        # Get video topic from environment
        topic = os.environ.get("VIDEO_TOPIC", "3 Scary True Stories That Happened at 3 AM")
        logger.info(f"Topic: {topic}")

        # 1. Generate Script
        logger.info("\n[STEP 1/6] Generating Script...")
        script_data = generate_script(topic)
        logger.info(f"✅ Script generated: {script_data['title']}")
        logger.info(f"   Scenes: {len(script_data['scenes'])}")

        # 2. Generate Images
        logger.info("\n[STEP 2/6] Generating Images...")
        image_paths = generate_images(script_data['scenes'])
        if not image_paths:
            raise RuntimeError(
                "Koi bhi image nahi bani (Gemini, Hugging Face, placeholder sab fail) — "
                "pipeline rok rahe hain. GEMINI_API_KEY / HF_API_KEY aur assets/placeholder.png check karo."
            )
        logger.info(f"✅ Images generated: {len(image_paths)} images")

        # 3. Generate Voice
        logger.info("\n[STEP 3/6] Generating Voice...")
        audio_path = generate_voice(script_data['voiceover'], voice="am_michael")
        logger.info(f"✅ Voice generated: {audio_path}")

        # 4. Build Video
        logger.info("\n[STEP 4/6] Building Video...")
        final_video = build_video(image_paths, audio_path, script_data['scenes'])
        logger.info(f"✅ Video built: {final_video}")

        # 5. Generate Thumbnail
        logger.info("\n[STEP 5/6] Generating Thumbnail...")
        thumb_path = generate_thumbnail(image_paths[0], script_data['title'])
        logger.info(f"✅ Thumbnail generated: {thumb_path}")

        # 6. Upload
        logger.info("\n[STEP 6/6] Uploading to Platforms...")
        upload_result = upload_all(final_video, thumb_path, script_data)
        logger.info(f"✅ Upload completed")

        logger.info("\n" + "="*60)
        logger.info("🎉 DONE. Video Live on YT + FB Shorts ✅")
        logger.info("="*60)
        
        return upload_result
    
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        logger.error("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
