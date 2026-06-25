"""
YouTube Automation System — MASTER ORCHESTRATOR (FINAL FIXED)
Complete End-to-End Pipeline with YouTube SEO Optimization & Analytics

FIXES:
1. ✅ Audio path resolution (final_audio > audio_path)
2. ✅ YouTube SEO optimized titles, descriptions, tags
3. ✅ Facebook & Instagram optimized descriptions
4. ✅ Metrics tracking integration
5. ✅ Duration validation
6. ✅ Proper error handling
7. ✅ USA audience targeting
8. ✅ No AI look - natural content
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import traceback
import shutil
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ============================================================
# SETUP LOGGING
# ============================================================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# IMPORTS
# ============================================================
from config.settings import API_KEYS, PLATFORM_CONFIG, VIDEO_CONFIG, SEO_CONFIG
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.audio_generator import AudioGenerator
from core.footage_fetcher import FootageFetcher
from core.video_assembler import VideoAssembler
from core.caption_generator import CaptionGenerator
from core.thumbnail_generator import ThumbnailGenerator
from core.cloud_uploader import CloudUploader

# Try to import metrics, but don't fail if not available
try:
    from core.metrics import MetricsTracker
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False
    logger.warning("⚠️ MetricsTracker not found - metrics disabled")

from uploaders.youtube_uploader import YouTubeUploader
from uploaders.facebook_uploader import FacebookUploader
from uploaders.instagram_uploader import InstagramUploader

# ============================================================
# DIRECTORIES
# ============================================================
OUTPUT_DIR = Path("output")
AUDIO_DIR = OUTPUT_DIR / "audio"
FOOTAGE_DIR = OUTPUT_DIR / "footage"
VIDEO_DIR = OUTPUT_DIR / "videos"
THUMB_DIR = OUTPUT_DIR / "thumbnails"
CAPTIONS_DIR = OUTPUT_DIR / "captions"

for d in [OUTPUT_DIR, AUDIO_DIR, FOOTAGE_DIR, VIDEO_DIR, THUMB_DIR, CAPTIONS_DIR]:
    d.mkdir(exist_ok=True)

LATEST_VIDEO = OUTPUT_DIR / "latest_video.mp4"
LATEST_THUMB = OUTPUT_DIR / "latest_thumb.jpg"


# ============================================================
# ORCHESTRATOR CLASS
# ============================================================
class AutomationOrchestrator:
    """Complete End-to-End Automation Pipeline - FINAL"""

    def __init__(self):
        logger.info("🚀 Initializing Automation System...")

        # Core modules
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.caption_gen = CaptionGenerator()
        self.thumbnail_gen = ThumbnailGenerator()
        self.cloud_uploader = CloudUploader()

        # Uploaders
        self.youtube_uploader = YouTubeUploader()
        self.facebook_uploader = FacebookUploader()
        self.instagram_uploader = InstagramUploader()

        # Metrics
        self.metrics = MetricsTracker() if HAS_METRICS else None

        # Statistics
        self.stats = {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'topics_processed': [],
            'total_duration': 0,
            'total_hook_score': 0,
            'start_time': datetime.now().isoformat()
        }

        logger.info("✅ System initialized")

    # ============================================================
    # HEALTH CHECK
    # ============================================================

    def health_check(self) -> Dict:
        """Check all system components"""
        api_status = API_KEYS.validate()
        missing = [k for k, v in api_status.items() if not v]

        return {
            'status': 'ok' if not missing else 'degraded',
            'apis': api_status,
            'missing': missing,
            'timestamp': datetime.now().isoformat()
        }

    # ============================================================
    # SEO OPTIMIZED CONTENT GENERATORS
    # ============================================================

    def _generate_youtube_title(self, topic: str, script: Dict) -> str:
        """YouTube SEO optimized title (max 60 chars, keyword first)"""
        hook = script.get('hook', '')
        clean_hook = hook.replace('...', '').strip()

        # Remove emojis from hook
        import re
        clean_hook = re.sub(r'[^\w\s]', '', clean_hook)

        # Title templates - USA audience optimized
        title_templates = [
            f"{topic[:30].title()} - {clean_hook[:25]} 🧠",
            f"{topic[:25].title()} | Why It Happens After 35 🧠",
            f"Stop {topic[:20]} Now - {clean_hook[:20]} 🧠",
            f"{topic[:30].title()} Explained in 60 Seconds 🧠",
            f"Why {topic[:25]}? The Science Explained 🧠",
            f"{topic[:28].title()} - What Nobody Tells You 🧠",
        ]

        title = random.choice(title_templates)

        # Ensure max 60 chars
        if len(title) > 60:
            title = title[:57] + "..."

        return title

    def _generate_youtube_description(self, topic: str, script: Dict) -> str:
        """YouTube SEO optimized description with timestamps and hashtags"""
        hook = script.get('hook', '')
        story = script.get('story', '')
        shock = script.get('shock', '')

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

💡 Key Fact:
{shock}

✅ Follow for daily brain health tips!
🔔 Hit the bell for notifications!

#Shorts #shorts #memory #brainfog #brainhealth #memoryloss #menover35 #healthtips #science #facts
""".strip()

        return description[:5000]  # YouTube max 5000 chars

    def _generate_youtube_tags(self, topic: str, script: Dict) -> List[str]:
        """YouTube SEO optimized tags - USA audience search behavior"""
        # Primary tags (high volume)
        primary_tags = [
            "memory loss", "brain fog", "why do i forget",
            "brain health", "memory tips", "men over 35",
            "short term memory", "cognitive health",
            "memory after 40", "brain fog causes",
        ]

        # Secondary tags (specific)
        secondary_tags = [
            "how to improve memory", "memory problems",
            "brain exercises", "mental clarity",
            "forgetfulness", "memory issues",
        ]

        # Topic-specific tags
        topic_words = [w for w in topic.lower().split() if len(w) > 2]

        # Combine all tags
        all_tags = primary_tags + secondary_tags + topic_words

        # Remove duplicates (preserve order)
        seen = set()
        unique_tags = []
        for tag in all_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        # YouTube max 30 tags, 500 chars total
        tags = []
        total_len = 0
        for tag in unique_tags[:30]:
            if total_len + len(tag) + 1 <= 500:
                tags.append(tag)
                total_len += len(tag) + 1
            else:
                break

        return tags

    def _generate_facebook_description(self, topic: str, script: Dict) -> str:
        """Facebook optimized description - engagement focused"""
        hook = script.get('hook', '')
        shock = script.get('shock', '')

        return f"""{hook}

{shock}

🧠 The science behind why this happens to men after 35.

💡 What you need to know:
• It's more common than you think
• There's a scientific reason
• You can do something about it

What do you think? Comment below! 👇

#memory #brainhealth #menover35 #healthtips #brainfog #shorts #reels"""

    def _generate_instagram_caption(self, topic: str, script: Dict) -> str:
        """Instagram optimized caption - save for later"""
        hook = script.get('hook', '')

        return f"""🧠 {hook}

The science behind {topic} explained in 60 seconds!

💡 Why it happens
🔬 The science
✅ What you can do

Save this for later! 📌
Follow for more brain tips 👆

#memory #brainhealth #menover35 #health #brainfog #shorts #reels #explore"""

    # ============================================================
    # DURATION VALIDATION
    # ============================================================

    def _validate_duration(self, duration: float) -> bool:
        """Check if duration is within YouTube Shorts range"""
        min_dur = getattr(VIDEO_CONFIG, 'DURATION_MIN', 42)
        max_dur = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)

        if duration < min_dur or duration > max_dur:
            logger.warning(f"⚠️ Duration {duration:.1f}s outside {min_dur}-{max_dur}s range")
            return False
        return True

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

        hook_score = script.get('hook_score', 0)
        word_count = script.get('word_count', 0)

        logger.info(f"   ✅ Script: {word_count} words | Hook: {hook_score}/10")

        # ── 2. AUDIO ───────────────────────────────────────────
        logger.info("🎙️ Step 2: Generating audio...")
        audio_dir = str(AUDIO_DIR / f"{safe}_{ts}")

        try:
            audio_data = await self.audio_gen.generate_with_effects(
                script_segments=script['segments'],
                output_dir=audio_dir,
                topic=topic
            )
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            raise

        # FIX: Get audio path correctly
        audio_path = audio_data.get('final_audio') or audio_data.get('audio_path') or ''
        audio_duration = audio_data.get('total_duration', 0)

        logger.info(f"   ✅ Audio: {audio_duration:.1f}s | Path: {audio_path}")

        # Validate duration
        if not self._validate_duration(audio_duration):
            logger.warning(f"⚠️ Audio duration {audio_duration:.1f}s outside range")
            # Try to fix by adjusting script
            # (implement if needed)

        # ── 3. FOOTAGE ─────────────────────────────────────────
        logger.info("🎬 Step 3: Fetching footage...")
        footage_dir = str(FOOTAGE_DIR / f"{safe}_{ts}")

        try:
            footage_clips = self.footage_fetcher.fetch_footage_for_script(
                script_segments=script['segments'],
                topic=topic
            )
            footage_paths = self.footage_fetcher.download_footage(
                clips=footage_clips,
                output_dir=footage_dir
            )
        except Exception as e:
            logger.error(f"❌ Footage fetch failed: {e}")
            footage_paths = {}  # Continue with color backgrounds

        logger.info(f"   ✅ Footage: {len(footage_paths)} clips")

        # ── 4. CAPTIONS ────────────────────────────────────────
        logger.info("💬 Step 4: Generating captions...")
        word_timings = audio_data.get('word_timings', [])
        captions = self.caption_gen.generate_captions(word_timings=word_timings)
        logger.info(f"   ✅ Captions: {len(captions)} lines")

        # ── 5. VIDEO ASSEMBLY ──────────────────────────────────
        logger.info("🎞️ Step 5: Assembling video...")
        video_path = str(VIDEO_DIR / f"{safe}_{ts}.mp4")

        try:
            self.video_assembler.create_video(
                script_segments=script['segments'],
                audio_data=audio_data,
                footage_clips=footage_paths,
                word_timings=word_timings,
                output_path=video_path
            )
        except Exception as e:
            logger.error(f"❌ Video assembly failed: {e}")
            raise

        logger.info(f"   ✅ Video → {video_path}")

        # Copy to latest
        shutil.copy2(video_path, str(LATEST_VIDEO))
        logger.info(f"   📋 Copied to {LATEST_VIDEO}")

        # ── 6. THUMBNAIL ───────────────────────────────────────
        logger.info("🖼️ Step 6: Generating thumbnail...")
        thumb_path = str(THUMB_DIR / f"{safe}_{ts}.jpg")
        thumb_words = self.content_gen.generate_thumbnail_words(topic=topic)

        try:
            self.thumbnail_gen.generate_thumbnail(
                words=thumb_words,
                topic=topic,
                output_path=thumb_path
            )
            shutil.copy2(thumb_path, str(LATEST_THUMB))
            logger.info(f"   ✅ Thumbnail → {thumb_path}")
        except Exception as e:
            logger.warning(f"⚠️ Thumbnail generation failed: {e}")
            thumb_path = None

        if skip_upload:
            logger.info("⏭️ Skipping uploads (--skip-upload)")
            return {
                'topic': topic,
                'video_path': video_path,
                'thumb_path': thumb_path,
                'script': script,
                'status': 'success',
                'uploaded': False
            }

        # ── 7. CLOUD UPLOAD ────────────────────────────────────
        video_url = None
        if self.cloud_uploader.is_configured():
            logger.info("☁️ Step 7: Cloud upload...")
            try:
                video_url = self.cloud_uploader.upload_video(video_path)
                logger.info(f"   ✅ URL: {video_url}")
            except Exception as e:
                logger.warning(f"⚠️ Cloud upload failed: {e}")
                video_url = None
        else:
            logger.info("☁️ Step 7: Cloud not configured, skipping")

        # ── 8. SEO CONTENT ─────────────────────────────────────
        title = self._generate_youtube_title(topic, script)
        description = self._generate_youtube_description(topic, script)
        tags = self._generate_youtube_tags(topic, script)

        fb_description = self._generate_facebook_description(topic, script)
        ig_caption = self._generate_instagram_caption(topic, script)

        logger.info(f"   📌 Title: {title}")
        logger.info(f"   🏷️ Tags: {len(tags)}")

        # ── 9. YOUTUBE UPLOAD ──────────────────────────────────
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

        # ── 10. FACEBOOK UPLOAD ───────────────────────────────
        fb_result = {'status': 'skipped'}
        logger.info("📘 Step 9: Facebook upload...")
        try:
            fb_result = self.facebook_uploader.upload_video(
                video_path=video_path,
                thumbnail_path=thumb_path,
                title=title[:60],
                description=fb_description,
                privacy='PUBLIC'
            )
            logger.info(f"   ✅ Facebook: {fb_result.get('video_id', 'done')}")
        except Exception as e:
            logger.error(f"   ❌ Facebook: {e}")
            fb_result = {'status': 'error', 'error': str(e)}

        # ── 11. INSTAGRAM UPLOAD ──────────────────────────────
        ig_result = {'status': 'skipped'}
        if video_url:
            logger.info("📸 Step 10: Instagram upload...")
            try:
                ig_result = self.instagram_uploader.upload_reel(
                    video_url=video_url,
                    thumbnail_path=thumb_path,
                    caption=ig_caption,
                    hashtags=tags[:10]
                )
                logger.info(f"   ✅ Instagram: {ig_result.get('media_id', 'done')}")
            except Exception as e:
                logger.error(f"   ❌ Instagram: {e}")
                ig_result = {'status': 'error', 'error': str(e)}
        else:
            logger.info("📸 Step 10: Instagram skipped (no cloud URL)")

        # ── 12. UPDATE STATS ───────────────────────────────────
        uploaded = any([
            yt_result.get('status') not in ['error', 'skipped'],
            fb_result.get('status') not in ['error', 'skipped'],
            ig_result.get('status') not in ['error', 'skipped'],
        ])

        self.stats['total_videos'] += 1
        self.stats['total_duration'] += audio_duration
        self.stats['total_hook_score'] += hook_score
        self.stats['topics_processed'].append(topic)

        # ── 13. RECORD METRICS ─────────────────────────────────
        if self.metrics:
            try:
                self.metrics.record_video(
                    video_data={
                        'topic': topic,
                        'duration': audio_duration,
                        'hook_score': hook_score,
                        'word_count': word_count,
                        'title': title,
                        'video_id': yt_result.get('video_id', '')
                    },
                    upload_results={
                        'youtube': yt_result,
                        'facebook': fb_result,
                        'instagram': ig_result
                    }
                )
            except Exception as e:
                logger.warning(f"⚠️ Metrics recording failed: {e}")

        # ── 14. RETURN RESULT ──────────────────────────────────
        return {
            'topic': topic,
            'title': title,
            'video_path': video_path,
            'thumb_path': thumb_path,
            'script': script,
            'audio_duration': audio_duration,
            'hook_score': hook_score,
            'word_count': word_count,
            'uploads': {
                'youtube': yt_result,
                'facebook': fb_result,
                'instagram': ig_result,
            },
            'status': 'success',
            'uploaded': uploaded
        }

    # ============================================================
    # MAIN PIPELINE
    # ============================================================

    async def run_pipeline(self, count: int = 1, specific_topic: str = None,
                           skip_upload: bool = False) -> Dict:

        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING PIPELINE")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {'❌' if skip_upload else '✅'}")
        logger.info(f"{'#'*60}\n")

        # Health check first
        health = self.health_check()
        if health['status'] == 'degraded':
            logger.warning(f"⚠️ System degraded: {health['missing']}")

        # Get topics
        if specific_topic:
            topics = [{'query': specific_topic}]
        else:
            topics = self.topic_engine.get_daily_topics(count=count)

        if not topics:
            logger.error("❌ No topics available")
            return {'status': 'error', 'error': 'No topics available'}

        logger.info(f"📋 Topics: {[t.get('query') for t in topics]}")

        # Process each topic
        results = []
        for i, topic_data in enumerate(topics):
            topic = topic_data.get('query', '')
            logger.info(f"\n{'='*60}")
            logger.info(f"📹 Processing {i+1}/{len(topics)}: {topic}")
            logger.info(f"{'='*60}")

            try:
                result = await self._process_topic(topic, topic_data, skip_upload)
                results.append(result)

                if result.get('uploaded'):
                    self.stats['successful_uploads'] += 1
                else:
                    self.stats['failed_uploads'] += 1

            except Exception as e:
                logger.error(f"❌ Failed: {e}")
                logger.error(traceback.format_exc())
                results.append({
                    'topic': topic,
                    'status': 'error',
                    'error': str(e)
                })
                self.stats['failed_uploads'] += 1

            # Delay between videos
            if i < len(topics) - 1:
                delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)
                logger.info(f"\n⏳ Waiting {delay}s before next video...")
                await asyncio.sleep(delay)

        # ── FINAL SUMMARY ──────────────────────────────────────
        self.stats['end_time'] = datetime.now().isoformat()

        logger.info(f"\n{'#'*60}")
        logger.info(f"🏁 PIPELINE COMPLETE")
        logger.info(f"   Success: {self.stats['successful_uploads']}")
        logger.info(f"   Failed:  {self.stats['failed_uploads']}")
        logger.info(f"   Total Duration: {self.stats['total_duration']:.1f}s")
        avg_hook = self.stats['total_hook_score'] / max(1, self.stats['total_videos'])
        logger.info(f"   Avg Hook Score: {avg_hook:.1f}/10")
        logger.info(f"{'#'*60}")

        # Export metrics report
        if self.metrics:
            try:
                report = self.metrics.export_report()
                logger.info(report)
            except Exception as e:
                logger.warning(f"⚠️ Could not export metrics: {e}")

        return {
            'status': 'complete',
            'stats': self.stats,
            'results': results
        }


# ============================================================
# MAIN ENTRY POINT
# ============================================================

async def main():
    parser = argparse.ArgumentParser(
        description='YouTube Automation Pipeline - FINAL FIXED',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python orchestrator.py                    # Generate 1 video
  python orchestrator.py --count 3          # Generate 3 videos
  python orchestrator.py --topic "forgetting names"  # Specific topic
  python orchestrator.py --skip-upload      # Generate only (no upload)
  python orchestrator.py --health-check     # Check system health
        """
    )

    parser.add_argument('--count', '-c', type=int, default=1,
                        help='Number of videos to generate (default: 1)')
    parser.add_argument('--topic', '-t', type=str,
                        help='Specific topic to use')
    parser.add_argument('--skip-upload', action='store_true',
                        help='Skip uploading to platforms')
    parser.add_argument('--health-check', '-hc', action='store_true',
                        help='Check system health and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize orchestrator
    orchestrator = AutomationOrchestrator()

    # Health check
    if args.health_check:
        health = orchestrator.health_check()
        print("\n📊 HEALTH CHECK RESULTS:")
        print(json.dumps(health, indent=2, default=str))
        return

    # Run pipeline
    results = await orchestrator.run_pipeline(
        count=args.count,
        specific_topic=args.topic,
        skip_upload=args.skip_upload
    )

    print("\n📊 FINAL RESULTS:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
