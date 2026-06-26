"""
YouTube Automation System — MASTER ORCHESTRATOR (FINAL FIXED)
Complete End-to-End Pipeline with YouTube SEO Optimization & Analytics

FIXES:
1. ✅ Circular import fixed (Lazy Imports)
2. ✅ Audio path resolution (final_audio > audio_path)
3. ✅ YouTube SEO optimized titles, descriptions, tags
4. ✅ Facebook & Instagram optimized descriptions
5. ✅ Metrics tracking integration
6. ✅ Duration validation
7. ✅ Proper error handling
8. ✅ USA audience targeting
9. ✅ No AI look - natural content
10. ✅ UNIQUE titles every time (randomized templates)
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

        # ============================================================
        # FIX 1: LAZY IMPORTS to avoid circular dependency
        # ============================================================
        self._modules = {}
        self._init_modules()

        # Metrics (optional)
        self.metrics = None
        try:
            from core.metrics import MetricsTracker
            self.metrics = MetricsTracker()
            logger.info("✅ Metrics tracking enabled")
        except ImportError:
            logger.warning("⚠️ MetricsTracker not found - metrics disabled")

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

        # ============================================================
        # FIX 2: UNIQUE TITLE TEMPLATES (20+ variations)
        # ============================================================
        self.title_templates = [
            # Type 1: "Your brain" hooks
            "Your brain is forgetting {topic} right now 🧠",
            "Your brain is changing with {topic} right now 🧠",
            "Your brain is quietly deleting {topic} as you read this 🧠",
            
            # Type 2: "Why" hooks
            "Why your {topic} gets worse after 35 🧠",
            "Why {topic} happens to you every day 🧠",
            "Why {topic} is more common than you think 🧠",
            
            # Type 3: "Hidden truth" hooks
            "The hidden truth about {topic} after 40 🧠",
            "The surprising truth about {topic} 🧠",
            "The real reason behind {topic} 🧠",
            
            # Type 4: "What nobody tells you" hooks
            "What nobody explains about {topic} 🧠",
            "What your brain does with {topic} 🧠",
            "What {topic} actually means for you 🧠",
            
            # Type 5: "Stop/How" hooks
            "Stop {topic} now - Here's why 🧠",
            "How {topic} affects your brain daily 🧠",
            "How to stop {topic} in 30 days 🧠",
            
            # Type 6: "Science/Explained" hooks
            "The science behind {topic} explained 🧠",
            "{topic} explained in 60 seconds 🧠",
            "{topic} - The science you need to know 🧠",
            
            # Type 7: "Warning/Danger" hooks
            "Warning: {topic} is destroying your memory 🧠",
            "Why ignoring {topic} is dangerous 🧠",
            "The danger of {topic} after 35 🧠",
            
            # Type 8: "Simple/Easy" hooks
            "The simple truth about {topic} 🧠",
            "The easy way to understand {topic} 🧠",
            "What {topic} really means for you 🧠",
        ]

        # ============================================================
        # FIX 3: UNIQUE DESCRIPTIONS
        # ============================================================
        self.description_templates = [
            "🧠 The truth about {topic} that nobody tells you...",
            "🔬 Science reveals what actually happens with {topic}...",
            "💡 One simple fact about {topic} that changes everything...",
            "⚡ The hidden reason behind {topic} explained...",
            "🎯 What {topic} really means for your brain...",
        ]

        logger.info("✅ System initialized")

    # ============================================================
    # LAZY INITIALIZATION
    # ============================================================

    def _init_modules(self):
        """Lazy initialization to avoid circular imports"""
        try:
            from core.topic_engine import ViralTopicEngine
            self._modules['topic_engine'] = ViralTopicEngine()
        except ImportError as e:
            logger.error(f"❌ Failed to import topic_engine: {e}")
            raise

        try:
            from core.content_generator import ContentGenerator
            self._modules['content_gen'] = ContentGenerator()
        except ImportError as e:
            logger.error(f"❌ Failed to import content_generator: {e}")
            raise

        try:
            from core.audio_generator import AudioGenerator
            self._modules['audio_gen'] = AudioGenerator()
        except ImportError as e:
            logger.error(f"❌ Failed to import audio_generator: {e}")
            raise

        try:
            from core.footage_fetcher import FootageFetcher
            self._modules['footage_fetcher'] = FootageFetcher()
        except ImportError as e:
            logger.error(f"❌ Failed to import footage_fetcher: {e}")
            raise

        try:
            from core.video_assembler import VideoAssembler
            self._modules['video_assembler'] = VideoAssembler()
        except ImportError as e:
            logger.error(f"❌ Failed to import video_assembler: {e}")
            raise

        try:
            from core.caption_generator import CaptionGenerator
            self._modules['caption_gen'] = CaptionGenerator()
        except ImportError as e:
            logger.error(f"❌ Failed to import caption_generator: {e}")
            raise

        try:
            from core.thumbnail_generator import ThumbnailGenerator
            self._modules['thumbnail_gen'] = ThumbnailGenerator()
        except ImportError as e:
            logger.error(f"❌ Failed to import thumbnail_generator: {e}")
            raise

        try:
            from core.cloud_uploader import CloudUploader
            self._modules['cloud_uploader'] = CloudUploader()
        except ImportError as e:
            logger.error(f"❌ Failed to import cloud_uploader: {e}")
            raise

        try:
            from uploaders.youtube_uploader import YouTubeUploader
            self._modules['youtube_uploader'] = YouTubeUploader()
        except ImportError as e:
            logger.error(f"❌ Failed to import youtube_uploader: {e}")
            raise

        try:
            from uploaders.facebook_uploader import FacebookUploader
            self._modules['facebook_uploader'] = FacebookUploader()
        except ImportError as e:
            logger.error(f"❌ Failed to import facebook_uploader: {e}")
            raise

        try:
            from uploaders.instagram_uploader import InstagramUploader
            self._modules['instagram_uploader'] = InstagramUploader()
        except ImportError as e:
            logger.error(f"❌ Failed to import instagram_uploader: {e}")
            raise

    def __getattr__(self, name):
        """Allow direct access to modules"""
        if name in self._modules:
            return self._modules[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # ============================================================
    # HEALTH CHECK
    # ============================================================

    def health_check(self) -> Dict:
        """Check all system components"""
        try:
            from config.settings import API_KEYS
            api_status = API_KEYS.validate()
            missing = [k for k, v in api_status.items() if not v]
        except ImportError:
            api_status = {}
            missing = ['settings']

        return {
            'status': 'ok' if not missing else 'degraded',
            'apis': api_status,
            'missing': missing,
            'timestamp': datetime.now().isoformat()
        }

    # ============================================================
    # FIX 2: UNIQUE SEO OPTIMIZED CONTENT GENERATORS
    # ============================================================

    def _generate_youtube_title(self, topic: str, script: Dict) -> str:
        """Generate UNIQUE YouTube title (randomized)"""
        # Randomly select a template
        template = random.choice(self.title_templates)
        title = template.format(topic=topic[:25])
        
        # Ensure max 60 chars
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title

    def _generate_youtube_description(self, topic: str, script: Dict) -> str:
        """Generate UNIQUE YouTube description"""
        hook = script.get('hook', '')
        story = script.get('story', '')
        shock = script.get('shock', '')
        
        # Random description intro
        intro = random.choice(self.description_templates).format(topic=topic)

        description = f"""
{intro}

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

        return description[:5000]

    def _generate_youtube_tags(self, topic: str, script: Dict) -> List[str]:
        """Generate YouTube tags"""
        primary_tags = [
            "memory loss", "brain fog", "why do i forget",
            "brain health", "memory tips", "men over 35",
            "short term memory", "cognitive health",
            "memory after 40", "brain fog causes",
        ]
        
        topic_words = [w for w in topic.lower().split() if len(w) > 2]
        all_tags = primary_tags + topic_words
        
        seen = set()
        unique_tags = []
        for tag in all_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
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
        """Facebook optimized description"""
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
        """Instagram optimized caption"""
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
        try:
            from config.settings import VIDEO_CONFIG
            min_dur = getattr(VIDEO_CONFIG, 'DURATION_MIN', 42)
            max_dur = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)
        except ImportError:
            min_dur, max_dur = 42, 55

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
        script = self._modules['content_gen'].generate_script(topic=topic)

        hook_score = script.get('hook_score', 0)
        word_count = script.get('word_count', 0)

        logger.info(f"   ✅ Script: {word_count} words | Hook: {hook_score}/10")

        # ── 2. AUDIO ───────────────────────────────────────────
        logger.info("🎙️ Step 2: Generating audio...")
        audio_dir = str(AUDIO_DIR / f"{safe}_{ts}")

        try:
            audio_data = await self._modules['audio_gen'].generate_with_effects(
                script_segments=script['segments'],
                output_dir=audio_dir,
                topic=topic
            )
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            raise

        audio_path = audio_data.get('final_audio') or audio_data.get('audio_path') or ''
        audio_duration = audio_data.get('total_duration', 0)

        logger.info(f"   ✅ Audio: {audio_duration:.1f}s | Path: {audio_path}")

        # Validate duration
        if not self._validate_duration(audio_duration):
            logger.warning(f"⚠️ Audio duration {audio_duration:.1f}s outside range")

        # ── 3. FOOTAGE ─────────────────────────────────────────
        logger.info("🎬 Step 3: Fetching footage...")
        footage_dir = str(FOOTAGE_DIR / f"{safe}_{ts}")

        try:
            footage_clips = self._modules['footage_fetcher'].fetch_footage_for_script(
                script_segments=script['segments'],
                topic=topic
            )
            footage_paths = self._modules['footage_fetcher'].download_footage(
                clips=footage_clips,
                output_dir=footage_dir
            )
        except Exception as e:
            logger.error(f"❌ Footage fetch failed: {e}")
            footage_paths = {}

        logger.info(f"   ✅ Footage: {len(footage_paths)} clips")

        # ── 4. CAPTIONS ────────────────────────────────────────
        logger.info("💬 Step 4: Generating captions...")
        word_timings = audio_data.get('word_timings', [])
        captions = self._modules['caption_gen'].generate_captions(word_timings=word_timings)
        logger.info(f"   ✅ Captions: {len(captions)} lines")

        # ── 5. VIDEO ASSEMBLY ──────────────────────────────────
        logger.info("🎞️ Step 5: Assembling video...")
        video_path = str(VIDEO_DIR / f"{safe}_{ts}.mp4")

        try:
            self._modules['video_assembler'].create_video(
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
        shutil.copy2(video_path, str(LATEST_VIDEO))

        # ── 6. THUMBNAIL ───────────────────────────────────────
        logger.info("🖼️ Step 6: Generating thumbnail...")
        thumb_path = str(THUMB_DIR / f"{safe}_{ts}.jpg")
        thumb_words = self._modules['content_gen'].generate_thumbnail_words(topic=topic)

        try:
            self._modules['thumbnail_gen'].generate_thumbnail(
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
            logger.info("⏭️ Skipping uploads")
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
        if self._modules['cloud_uploader'].is_configured():
            logger.info("☁️ Step 7: Cloud upload...")
            try:
                video_url = self._modules['cloud_uploader'].upload_video(video_path)
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

        # ── 9. YOUTUBE UPLOAD ──────────────────────────────────
        yt_result = {'status': 'skipped'}
        logger.info("📺 Step 8: YouTube upload...")
        try:
            yt_result = self._modules['youtube_uploader'].upload_video(
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
            fb_result = self._modules['facebook_uploader'].upload_video(
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
                ig_result = self._modules['instagram_uploader'].upload_reel(
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
            topics = self._modules['topic_engine'].get_daily_topics(count=count)

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
                delay = 120
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