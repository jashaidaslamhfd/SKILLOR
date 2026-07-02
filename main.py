import os
import sys
import argparse
from core.topic_engine import select_topic
from core.hook_engine import generate_hook
from core.content_generator import generate_script
from core.audio_generator import generate_voiceover
from core.footage_fetcher import fetch_stock_footage
from core.caption_generator import generate_captions
from core.thumbnail_generator import create_thumbnail
from core.video_assembler import assemble_video
from core.cloud_uploader import upload_to_cloudinary
from uploader.youtube_uploader import upload_to_youtube
from uploader.instagram_uploader import upload_to_instagram
from uploader.facebook_uploader import upload_to_facebook
from core.metrics import log_metrics

def run_pipeline(niche="auto", batch=1, dry_run=False):
    for i in range(batch):
        print(f"\n=== Batch {i+1}/{batch} ===")
        try:
            topic = select_topic(niche)
            hook_data = generate_hook(topic, niche)
            script_data = generate_script(topic, hook_data, niche)
            script_data['niche'] = niche

            audio_path = generate_voiceover(script_data['script'])
            footage_path = fetch_stock_footage(niche, script_data['search_terms'])
            captions = generate_captions(script_data['script'], audio_path)
            thumb_path = create_thumbnail(script_data['thumbnail_text'], niche)
            video_path = assemble_video(footage_path, audio_path, captions, hook_data, script_data)

            if dry_run:
                print(" [Dry Run] Skipping uploads")
                continue

            video_url = upload_to_cloudinary(video_path, script_data['title'])
            thumb_url = upload_to_cloudinary(thumb_path, script_data['title'], resource_type="image")

            yt_url = upload_to_youtube(video_url, script_data)
            caption = f"{script_data['title']}\n\n#shorts #viral"
            ig_url = upload_to_instagram(video_url, caption, thumb_url)
            fb_url = upload_to_facebook(video_url, caption)

            log_metrics(script_data, {"youtube": yt_url, "instagram": ig_url, "facebook": fb_url})
            print(f"✅ Success: {yt_url}")

        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--niche", default="auto")
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_pipeline(args.niche, args.batch, args.dry_run)
