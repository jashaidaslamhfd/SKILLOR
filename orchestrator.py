"""
YouTube Automation System — MASTER ORCHESTRATOR (FIXED)
Complete End-to-End Pipeline with YouTube SEO Optimization
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import traceback
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Imports
from config.settings import API_KEYS, PLATFORM_CONFIG, SEO_CONFIG
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.audio_generator import AudioGenerator
from core.footage_fetcher import FootageFetcher
from core.video_assembler import VideoAssembler
from core.caption_generator import CaptionGenerator
from core.thumbnail_generator import ThumbnailGenerator
from core.cloud_uploader import CloudUploader

from uploaders.youtube_uploader import YouTubeUploader
from uploaders.facebook_uploader import FacebookUploader
from uploaders.instagram_uploader import InstagramUploader

# Directories
OUTPUT_DIR = Path("output")
AUDIO_DIR = OUTPUT_DIR / "audio"
FOOTAGE_DIR = OUTPUT_DIR / "footage"
VIDEO_DIR = OUTPUT_DIR / "videos"
THUMB_DIR = OUTPUT_DIR / "thumbnails"

for d in [OUTPUT_DIR, AUDIO_DIR, FOOTAGE_DIR, VIDEO_DIR, THUMB_DIR]:
    d.mkdir(exist_ok=True)

LATEST_VIDEO = OUTPUT_DIR / "latest_video.mp4"
LATEST_THUMB = OUTPUT_DIR / "latest_thumb.jpg"


class AutomationOrchestrator:
    """Complete End-to-End Automation Pipeline"""

    def __init__(self):
        logger.info("🚀 Initializing Automation System...")

        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.caption_gen = CaptionGenerator()
        self.thumbnail_gen = ThumbnailGenerator()
        self.cloud_uploader = CloudUploader()

        self.youtube_uploader = YouTubeUploader()
        self.facebook_uploader = FacebookUploader()
        self.instagram_uploader = InstagramUploader()

        self.stats = {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'topics_processed': []
        }
        logger.info("✅ System initialized")

    def health_check(self) -> Dict:
        api_status = API_KEYS.validate()
        missing = [k for k, v in api_status.items() if not v]
        return {
            'status': 'ok' if not missing else 'degraded',
            'apis': api_status,
            'missing': missing
        }

    # ============================================================
    # PIPELINE
    # ============================================================

    async def run_pipeline(self, count: int = 1, specific_topic: str = None,
                           skip_upload: bool = False) -> Dict:

        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING PIPELINE")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"{'#'*60}\n")

        if specific_topic:
            topics = [{'query': specific_topic}]
        else:
            topics = self.topic_engine.get_daily_topics(count=count)

        if not topics:
            logger.error("❌ No topics available")
            return {'status': 'error', 'error': 'No topics available'}

        logger.info(f"📋 Topics: {[t.get('query') for t in topics]}")

        results = []
        for i, topic_data in enumerate(topics):
            topic = topic_data.get('query', '')
            logger.info(f"\n{'='*60}")
            logger.info(f"📹 Processing {i+1}/{len(topics)}: {topic}")
            logger.info(f"{'='*60}")
            try:
                result = await self._process_topic(topic, topic_data, skip_upload)
                results.append(result)
                self.stats['total_videos'] += 1
                if result.get('uploaded'):
                    self.stats['successful_uploads'] += 1
                else:
                    self.stats['failed_uploads'] += 1
            except Exception as e:
                logger.error(f"❌ Failed: {e}")
                logger.error(traceback.format_exc())
                results.append({'topic': topic, 'status': 'error', 'error': str(e)})
                self.stats['failed_uploads'] += 1

        logger.info(f"\n{'#'*60}")
        logger.info(f"🏁 PIPELINE COMPLETE")
        logger.info(f"   Success: {self.stats['successful_uploads']}")
        logger.info(f"   Failed:  {self.stats['failed_uploads']}")
        logger.info(f"{'#'*60}")

        return {'status': 'complete', 'results': results, 'stats': self.stats}

    # ============================================================
    # PROCESS ONE TOPIC
    # ============================================================

    async def _process_topic(self, topic: str, topic_data: Dict,
                              skip_upload: bool = False) -> Dict:

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe = topic[:40].replace(' ', '_').replace('/', '-')

        # ── 1. SCRIPT ──────────────────────────────────────────
        logger.info("📝 Step 1: Generating script...")
        script = self.content_gen.generate_script(topic=topic)
        logger.info(f"   ✅ Script: {script['word_count']} words | Hook: {script['hook_score']}/10")

        # ── 2. AUDIO ───────────────────────────────────────────
        logger.info("🎙️ Step 2: Generating audio...")
        audio_dir = str(AUDIO_DIR / f"{safe}_{ts}")
        audio_data = await self.audio_gen.generate_with_effects(
            script_segments=script['segments'],
            output_dir=audio_dir,
            topic=topic
        )

        # FIX: Get audio path correctly
        audio_path = audio_data.get('final_audio') or audio_data.get('audio_path') or ''
        logger.info(f"   ✅ Audio: {audio_data.get('total_duration', 0):.1f}s | Path: {audio_path}")

        # ── 3. FOOTAGE ─────────────────────────────────────────
        logger.info("🎬 Step 3: Fetching footage...")
        footage_dir = str(FOOTAGE_DIR / f"{safe}_{ts}")
        footage_clips = self.footage_fetcher.fetch_footage_for_script(
            script_segments=script['segments'],
            topic=topic
        )
        footage_paths = self.footage_fetcher.download_footage(
            clips=footage_clips,
            output_dir=footage_dir
        )
        logger.info(f"   ✅ Footage: {len(footage_paths)} clips")

        # ── 4. CAPTIONS ────────────────────────────────────────
        logger.info("💬 Step 4: Generating captions...")
        word_timings = audio_data.get('word_timings', [])
        captions = self.caption_gen.generate_captions(word_timings=word_timings)
        logger.info(f"   ✅ Captions: {len(captions)} lines")

        # ── 5. VIDEO ASSEMBLY ──────────────────────────────────
        logger.info("🎞️ Step 5: Assembling video...")
        video_path = str(VIDEO_DIR / f"{safe}_{ts}.mp4")
        self.video_assembler.create_video(
            script_segments=script['segments'],
            audio_data=audio_data,
            footage_clips=footage_paths,
            word_timings=word_timings,
            output_path=video_path
        )
        logger.info(f"   ✅ Video → {video_path}")

        # Copy to fixed output path
        shutil.copy2(video_path, str(LATEST_VIDEO))
        logger.info(f"   📋 Copied to {LATEST_VIDEO}")

        # ── 6. THUMBNAIL ───────────────────────────────────────
        logger.info("🖼️ Step 6: Generating thumbnail...")
        thumb_path = str(THUMB_DIR / f"{safe}_{ts}.jpg")
        thumb_words = self.content_gen.generate_thumbnail_words(topic=topic)
        self.thumbnail_gen.generate_thumbnail(
            words=thumb_words,
            topic=topic,
            output_path=thumb_path
        )
        shutil.copy2(thumb_path, str(LATEST_THUMB))
        logger.info(f"   ✅ Thumbnail → {thumb_path}")

        if skip_upload:
            logger.info("⏭️ Skipping uploads (--skip-upload)")
            return {
                'topic': topic, 'video_path': video_path,
                'thumb_path': thumb_path, 'script': script,
                'status': 'success', 'uploaded': False
            }

        # ── 7. CLOUD UPLOAD ────────────────────────────────────
        video_url = None
        if self.cloud_uploader.is_configured():
            logger.info("☁️ Step 7: Cloud upload...")
            video_url = self.cloud_uploader.upload_video(video_path)
            logger.info(f"   ✅ URL: {video_url}")
        else:
            logger.info("☁️ Step 7: Cloud not configured, skipping")

        # ── 8. YOUTUBE SEO OPTIMIZED ──────────────────────────
        title = self._generate_youtube_title(topic, script)
        description = self._generate_youtube_description(topic, script)
        tags = self._generate_youtube_tags(topic, script)

        logger.info(f"   📌 Title: {title}")
        logger.info(f"   🏷️ Tags: {len(tags)}")

        # ── 9. YOUTUBE ─────────────────────────────────────────
        yt_result = {'status': 'skipped'}
        logger.info("📺 Step 8: YouTube upload...")
        try:
            yt_result = self.youtube_uploader.upload_video(
                video_path=video_path,
                thumbnail_path=thumb_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status='public'
            )
            logger.info(f"   ✅ YouTube: {yt_result.get('video_id', 'done')}")
        except Exception as e:
            logger.error(f"   ❌ YouTube: {e}")
            yt_result = {'status': 'error', 'error': str(e)}

        # ── 10. FACEBOOK ───────────────────────────────────────
        fb_result = {'status': 'skipped'}
        logger.info("📘 Step 9: Facebook upload...")
        try:
            fb_result = self.facebook_uploader.upload_video(
                video_path=video_path,
                thumbnail_path=thumb_path,
                title=title[:60],
                description=self._generate_facebook_description(topic, script),
                privacy='PUBLIC'
            )
            logger.info(f"   ✅ Facebook: {fb_result.get('video_id', 'done')}")
        except Exception as e:
            logger.error(f"   ❌ Facebook: {e}")
            fb_result = {'status': 'error', 'error': str(e)}

        # ── 11. INSTAGRAM ──────────────────────────────────────
        ig_result = {'status': 'skipped'}
        if video_url:
            logger.info("📸 Step 10: Instagram upload...")
            try:
                caption = self._generate_instagram_caption(topic, script)
                ig_result = self.instagram_uploader.upload_reel(
                    video_url=video_url,
                    thumbnail_path=thumb_path,
                    caption=caption,
                    hashtags=tags[:10]
                )
                logger.info(f"   ✅ Instagram: {ig_result.get('media_id', 'done')}")
            except Exception as e:
                logger.error(f"   ❌ Instagram: {e}")
                ig_result = {'status': 'error', 'error': str(e)}
        else:
            logger.info("📸 Step 10: Instagram skipped (no cloud URL)")

        uploaded = any([
            yt_result.get('status') not in ['error', 'skipped'],
            fb_result.get('status') not in ['error', 'skipped'],
        ])

        return {
            'topic': topic, 'title': title,
            'video_path': video_path, 'thumb_path': thumb_path,
            'uploads': {
                'youtube': yt_result,
                'facebook': fb_result,
                'instagram': ig_result,
            },
            'status': 'success', 'uploaded': uploaded
        }

    # ============================================================
    # YOUTUBE SEO OPTIMIZED METHODS
    # ============================================================

    def _generate_youtube_title(self, topic: str, script: Dict) -> str:
        """YouTube SEO optimized title (max 60 chars, keyword first)"""
        hook = script.get('hook', '')
        clean_hook = hook.replace('...', '').strip()

        # Remove any existing emojis
        import re
        clean_hook = re.sub(r'[^\w\s]', '', clean_hook)

        # Format: Keyword | Hook | Emoji
        title_templates = [
            f"{topic[:30].title()} - {clean_hook[:25]} 🧠",
            f"{topic[:25].title()} | Why It Happens After 35 🧠",
            f"Stop {topic[:20]} Now - {clean_hook[:20]} 🧠",
            f"{topic[:30].title()} Explained in 60 Seconds 🧠",
        ]

        title = random.choice(title_templates)

        # Ensure max 60 chars
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    def _generate_youtube_description(self, topic: str, script: Dict) -> str:
        """YouTube SEO optimized description with timestamps"""
        hook = script.get('hook', '')
        story = script.get('story', '')

        description = f"""
{hook}

🧠 What You'll Learn:
• Why {topic} happens after 35
• The science behind memory loss
• What you can do about it

📝 Timestamps:
00:00 - Hook
00:08 - The Science
00:25 - Why It Happens
00:40 - What You Can Do

🔬 Science Explained:
{story[:200]}...

✅ Follow for daily brain health tips!
🔔 Hit the bell for notifications!

#Shorts #shorts #memory #brainfog #brainhealth #memoryloss #menover35 #healthtips
""".strip()

        return description[:5000]  # YouTube max

    def _generate_youtube_tags(self, topic: str, script: Dict) -> List[str]:
        """YouTube SEO optimized tags"""
        base_tags = [
            "memory loss", "brain fog", "why do i forget",
            "brain health", "memory tips", "men over 35",
            "short term memory", "cognitive health",
            "memory after 40", "brain fog causes",
            "how to improve memory", "memory problems",
            "youtube shorts", "shorts", "health shorts"
        ]

        topic_words = [w for w in topic.lower().split() if len(w) > 2]
        unique_tags = list(dict.fromkeys(topic_words + base_tags))

        # YouTube max 30 tags, 500 chars total
        tags = []
        total_len = 0
        for tag in unique_tags[:30]:
            if total_len + len(tag) + 1 <= 500:
                tags.append(tag)
                total_len += len(tag) + 1

        return tags

    def _generate_facebook_description(self, topic: str, script: Dict) -> str:
        """Facebook optimized description"""
        hook = script.get('hook', '')
        return f"""{hook}

Did you know this about {topic}? 🤔

🧠 Science behind why it happens
💡 What you can do about it
📌 Save this for later!

What do you think? Comment below! 👇

#memory #brainhealth #menover35 #healthtips #brainfog"""

    def _generate_instagram_caption(self, topic: str, script: Dict) -> str:
        """Instagram optimized caption"""
        hook = script.get('hook', '')
        return f"""🧠 {hook}

The science behind {topic} explained in 60 seconds!

💡 Why it happens
🔬 The science
✅ What you can do

Save this for later! 📌
Follow for more brain tips 👆

#memory #brainhealth #menover35 #health #brainfog #shorts"""


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description='YouTube Automation Pipeline')
    parser.add_argument('--count', '-c', type=int, default=1)
    parser.add_argument('--topic', '-t', type=str)
    parser.add_argument('--skip-upload', action='store_true')
    parser.add_argument('--health-check', '-hc', action='store_true')
    args = parser.parse_args()

    orchestrator = AutomationOrchestrator()

    if args.health_check:
        print(json.dumps(orchestrator.health_check(), indent=2))
        return

    results = await orchestrator.run_pipeline(
        count=args.count,
        specific_topic=args.topic,
        skip_upload=args.skip_upload
    )
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
