import os
import sys
import argparse
from datetime import datetime

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

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_pipeline(niche="auto", batch=1, dry_run=False, topic=None):
    log(f"🚀 Starting Pipeline | Niche: {niche} | Batch: {batch} | DryRun: {dry_run}")

    for i in range(batch):
        log(f"\n{'='*60}")
        log(f"BATCH {i+1}/{batch}")
        log(f"{'='*60}")
        try:
            # 1. Content Generation
            selected_topic = topic if topic else select_topic(niche)
            hook_data = generate_hook(selected_topic, niche)
            script_data = generate_script(selected_topic, hook_data, niche)
            script_data['niche'] = niche
            log(f"📝 Title: {script_data['title']}")
            log(f"🎯 Hook Score: {script_data.get('hook_score', '?')}/10")

            # 2. Media Generation
            log("🎙 Generating voiceover...")
            audio_path = generate_voiceover(script_data['script'])

            log("🎬 Fetching footage...")
            footage_path = fetch_stock_footage(niche, script_data['search_terms'])

            log("💬 Generating captions...")
            captions = generate_captions(script_data['script'], audio_path)

            log("🖼 Creating thumbnail...")
            thumb_path = create_thumbnail(script_data['thumbnail_text'], niche)

            log("🎞 Assembling video...")
            video_path = assemble_video(footage_path, audio_path, captions, hook_data, script_data)

            if dry_run:
                log(f"✅ [Dry Run] Video ready: {video_path}")
                continue

            # 3. Upload Flow
            log("☁ Uploading to Cloudinary...")
            video_url = upload_to_cloudinary(video_path, script_data['title'])
            thumb_url = upload_to_cloudinary(thumb_path, script_data['title'], resource_type="image")

            if not video_url:
                raise Exception("Cloudinary upload failed")

            log("📺 Uploading to YouTube...")
            yt_url = upload_to_youtube(video_url, script_data)

            caption = f"{script_data['title']}\n\n{script_data['script'][:200]}\n\n#shorts #viral #{niche}"

            log("📱 Uploading to Instagram...")
            ig_url = upload_to_instagram(video_url, caption, thumb_url)

            log("📘 Uploading to Facebook...")
            fb_url = upload_to_facebook(video_url, caption)

            result = {
                "youtube": yt_url,
                "instagram": ig_url,
                "facebook": fb_url,
                "cloudinary": video_url,
                "status": "uploaded"
            }
            log_metrics(script_data, result)
            log(f"✅ Batch {i+1} Complete: {yt_url}")

        except Exception as e:
            log(f"❌ Batch {i+1} Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1M Subs Shorts Pipeline 2026")
    parser.add_argument("--niche", default="auto", choices=['auto', 'mystery', 'science', 'human_behaviour'])
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--topic", default=None)
    args = parser.parse_args()
    run_pipeline(args.niche, args.batch, args.dry_run, args.topic)
