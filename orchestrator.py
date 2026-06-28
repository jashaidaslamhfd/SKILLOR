"""
YouTube Automation System — MASTER ORCHESTRATOR (USA 2026)
Complete End-to-End Pipeline with YouTube SEO Optimization & Analytics

FIXES:
1. ✅ Baby-focused topics and hooks
2. ✅ Forced engagement CTAs (Like + Comment + Share)
3. ✅ 100% free audio (edge-tts)
4. ✅ First segment uses footage (no blank clips)
5. ✅ Color grading for vibrant videos
6. ✅ Swipe stopper on first 0.8s
"""

import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

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
    """Complete End-to-End Automation Pipeline - USA 2026"""

    def __init__(self):
        logger.info("🚀 Initializing Automation System (USA 2026)...")

        self._modules = {}
        self._init_modules()

        self.metrics = None
        try:
            from core.metrics import MetricsTracker
            self.metrics = MetricsTracker()
            logger.info("✅ Metrics tracking enabled")
        except ImportError:
            logger.warning("⚠️ MetricsTracker not found")

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
        # BABY TITLE TEMPLATES
        # ============================================================
        self.title_templates = [
            "Your baby's brain does this with {topic} 🧠",
            "The real reason behind {topic} 🧠",
            "What nobody explains about {topic} 🧠",
            "How {topic} affects your baby's brain 🧠",
            "The science behind {topic} explained 🧠",
            "Your baby's brain is hiding {topic} from you 🧠",
            "Why {topic} happens to your baby 🧠",
            "What scientists found about {topic} 🧠",
            "The truth about {topic} nobody tells parents 🧠",
            "Every parent should know this about {topic} 🧠",
            "Your baby's brain does THIS with {topic} 🧠",
            "The hidden reason behind {topic} 🧠",
        ]

        # ============================================================
        # FORCED ENGAGEMENT DESCRIPTION TEMPLATES
        # ============================================================
        self.description_force_templates = [
            "👍 LIKE if you want more baby brain science!\n🗣️ SHARE with a new parent!\n👇 Comment YOUR baby's milestone!",
            "❤️ DOUBLE TAP if you love your baby!\n📌 SAVE for later!\n👶 TAG a parent who needs to see this!",
            "👍 LIKE if this blew your mind!\n🗣️ SHARE with every mom you know!\n💬 Comment 'BABY' if this is your little one!",
            "❤️ LIKE for more baby science!\n📌 SHARE with a new mom!\n👇 Comment what YOUR baby does that amazes you!",
            "👍 LIKE if you're AMAZED!\n🗣️ SHARE with a parent!\n💬 Comment 'WOW' if this is your baby!",
        ]

        self.poll_templates = [
            "🏟️ POLL: Does your baby do this? Comment YES or NO!",
            "🏟️ POLL: Are you amazed by baby brain science? Comment WOW!",
            "🏟️ POLL: Did you know this about your baby? Comment KNEW or WOW!",
        ]

        logger.info("✅ System initialized (USA 2026 - BABY NICHE)")

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
        if name in self._modules:
            return self._modules[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # ============================================================
    # HEALTH CHECK
    # ============================================================
    def health_check(self) -> Dict:
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
    # GENERATE YOUTUBE TITLE - BABY FOCUSED
    # ============================================================
    def _generate_youtube_title(self, topic: str, script: Dict) -> str:
        """Generate BABY-FOCUSED YouTube title"""
        
        # Try AI first
        try:
            ai_title = self._modules['content_gen'].generate_title(topic=topic)
            if ai_title and 15 <= len(ai_title) <= 55:
                logger.info(f"   ✅ AI title: {ai_title}")
                return ai_title
        except Exception as e:
            logger.warning(f"   ⚠️ AI title generation failed: {e}")
        
        # Fallback to templates
        template = random.choice(self.title_templates)
        topic_short = ' '.join(topic.split()[:3])
        
        try:
            title = template.format(topic=topic_short)
        except (KeyError, IndexError):
            title = template.replace('{topic}', topic_short)
        
        if len(title) > 55:
            topic_shorter = ' '.join(topic.split()[:2])
            try:
                title = template.format(topic=topic_shorter)
            except (KeyError, IndexError):
                title = template.replace('{topic}', topic_shorter)
        
        if len(title) > 55:
            title = title[:52] + "..."
        
        return title

    # ============================================================
    # GENERATE YOUTUBE DESCRIPTION - FORCED ENGAGEMENT
    # ============================================================
    def _generate_youtube_description(self, topic: str, script: Dict) -> str:
        """Generate description with FORCED engagement (Like + Comment + Share)"""
        
        force_engagement = random.choice(self.description_force_templates)
        poll = random.choice(self.poll_templates)
        
        topic_words = [w for w in topic.lower().split() if len(w) > 3]
        topic_hashtag = '#' + topic_words[0].capitalize() if topic_words else '#BabyScience'
        
        hashtag_sets = [
            f"#Shorts #{topic_hashtag.replace('#','')} #BabyBrain #ParentingTips #ChildDevelopment",
            f"#Shorts #BabyScience #{topic_hashtag.replace('#','')} #BrainDevelopment #ParentingHacks",
            f"#Shorts #{topic_hashtag.replace('#','')} #NewbornFacts #ToddlerLife #BabyFacts",
            f"#Shorts #ParentingJourney #{topic_hashtag.replace('#','')} #BabyLove #ChildPsychology",
        ]
        hashtags = random.choice(hashtag_sets)
        
        description = f"""
🧠 Your baby's brain is doing something INCREDIBLE right now...

What you need to know:
• How your baby's brain grows
• The science behind baby development
• What you can do to help

{poll}

{force_engagement}

🔔 Follow for more baby brain science!

{hashtags}
""".strip()
        
        return description[:5000]

    # ============================================================
    # GENERATE FACEBOOK DESCRIPTION
    # ============================================================
    def _generate_facebook_description(self, topic: str, script: Dict) -> str:
        """Generate Facebook description with forced engagement"""
        hook = script.get('hook', '')
        shock = script.get('shock', '')
        
        fb_questions = [
            f"Has this ever happened to your baby? Share below!",
            f"Tag a NEW PARENT who needs to see this!",
            f"Did you know this about {topic}? React if this is you!",
            f"Who else thought they were the only one? Comment below!",
            f"Parents - has this happened to your little one? React!",
        ]
        fb_question = random.choice(fb_questions)
        
        fb_hashtag_sets = [
            "#BabyBrain #ParentingTips #ChildDevelopment #shorts #reels",
            "#BabyScience #BrainDevelopment #ParentingHacks #shorts #reels",
            "#NewbornFacts #ToddlerLife #BabyFacts #shorts #reels",
        ]
        fb_hashtags = random.choice(fb_hashtag_sets)
        
        return f"""{hook}

{shock}

The science behind why this happens to your baby's brain.

What you need to know:
- It's more common than you think
- There's a scientific reason
- You can help your baby's brain grow

{fb_question}

React if this blew your mind!
Follow for more baby science

{fb_hashtags}"""

    # ============================================================
    # GENERATE INSTAGRAM CAPTION
    # ============================================================
    def _generate_instagram_caption(self, topic: str, script: Dict) -> str:
        """Generate Instagram caption with forced engagement"""
        hook = script.get('hook', '')
        topic_words = topic.lower().replace('-', ' ').replace('?', '').split()
        topic_hashtag = '#' + topic_words[0].capitalize() if topic_words else '#BabyFacts'
        
        ig_hooks = [
            f"Save this for when your baby does {topic}! 📌",
            f"Double tap if your baby does this! 💛",
            f"Share this with a new parent! 📤",
            'Comment YES if this is YOUR baby 😂',
            f"Parents - has {topic} happened to you? Comment YES!",
        ]
        ig_hook = random.choice(ig_hooks)
        
        ig_hashtag_sets = [
            f"#BabyBrain #{topic_hashtag.replace('#','')} #ParentingTips #shorts #reels #explore",
            f"#BabyScience #{topic_hashtag.replace('#','')} #ChildDevelopment #shorts #reels #viral",
            f"#{topic_hashtag.replace('#','')} #NewbornFacts #ToddlerLife #shorts #reels #fyp",
        ]
        ig_hashtags = random.choice(ig_hashtag_sets)
        
        return f"""🧠 {hook}

The science behind {topic} explained in 60 seconds!

💡 Why it happens to your baby
🔬 The science behind it
✅ What you can do

{ig_hook}
Follow for more baby science 👆

{ig_hashtags}"""

    # ============================================================
    # GENERATE YOUTUBE TAGS
    # ============================================================
    def _generate_youtube_tags(self, topic: str, script: Dict) -> List[str]:
        """Generate YouTube tags"""
        base_tag_sets = [
            ["baby brain", "parenting tips", "child development", "baby science", "brain growth"],
            ["baby facts", "newborn milestones", "toddler psychology", "parenting advice"],
            ["baby learning", "child brain", "mom life", "parenting hacks", "baby milestones"],
        ]
        primary_tags = random.choice(base_tag_sets)
        
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

    # ============================================================
    # VALIDATE DURATION
    # ============================================================
    def _validate_duration(self, duration: float) -> bool:
        try:
            from config.settings import VIDEO_CONFIG
            min_dur = getattr(VIDEO_CONFIG, 'DURATION_MIN', 42)
            max_dur = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)
        except ImportError:
            min_dur, max_dur = 35, 55

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

        # ── 1. SCRIPT ──
        logger.info("📝 Step 1: Generating script...")
        script = self._modules['content_gen'].generate_script(topic=topic)
        hook_score = script.get('hook_score', 0)
        word_count = script.get('word_count', 0)
        logger.info(f"   ✅ Script: {word_count} words | Hook: {hook_score}/10")

        # ── 2. AUDIO ──
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
        logger.info(f"   ✅ Audio: {audio_duration:.1f}s")

        if not self._validate_duration(audio_duration):
            logger.warning(f"⚠️ Audio duration {audio_duration:.1f}s outside range")

        # ── 3. FOOTAGE ──
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

        # ── 4. CAPTIONS ──
        logger.info("💬 Step 4: Generating captions...")
        word_timings = audio_data.get('word_timings', [])
        captions = self._modules['caption_gen'].generate_captions(word_timings=word_timings)
        logger.info(f"   ✅ Captions: {len(captions)} lines")

        caption_ass_path = str(VIDEO_DIR / f"{safe}_{ts}_captions.ass")
        total_duration = audio_data.get('total_duration', 48.0)
        try:
            self._modules['caption_gen'].generate_karaoke_ass(
                word_timings=word_timings,
                ass_path=caption_ass_path,
                max_duration=total_duration
            )
            logger.info(f"   ✅ Karaoke ASS captions generated")
        except Exception as e:
            logger.warning(f"⚠️ Karaoke ASS generation failed: {e}")
            caption_ass_path = None

        # ── 5. VIDEO ASSEMBLY ──
        logger.info("🎞️ Step 5: Assembling video...")
        video_path = str(VIDEO_DIR / f"{safe}_{ts}.mp4")
        try:
            self._modules['video_assembler'].create_video(
                script_segments=script['segments'],
                audio_data=audio_data,
                footage_clips=footage_paths,
                word_timings=word_timings,
                caption_ass_path=caption_ass_path,
                output_path=video_path
            )
        except Exception as e:
            logger.error(f"❌ Video assembly failed: {e}")
            raise

        logger.info(f"   ✅ Video → {video_path}")
        shutil.copy2(video_path, str(LATEST_VIDEO))

        # ── 6. THUMBNAIL ──
        logger.info("🖼️ Step 6: Generating thumbnail...")
        thumb_path = str(THUMB_DIR / f"{safe}_{ts}.jpg")
        thumb_words = self._modules['content_gen'].generate_thumbnail_words(topic=topic)
        
        frame_path = None
        try:
            frame_path = self._modules['video_assembler'].extract_hd_frame(
                video_path=video_path,
                output_path=str(THUMB_DIR / f"{safe}_{ts}_frame.png")
            )
            if frame_path:
                logger.info(f"   ✅ HD frame extracted")
        except Exception as e:
            logger.warning(f"⚠️ Frame extraction failed: {e}")

        if frame_path and os.path.exists(frame_path):
            try:
                self._modules['thumbnail_gen'].generate_thumbnail_from_frame(
                    frame_path=frame_path,
                    words=thumb_words,
                    topic=topic,
                    output_path=thumb_path,
                    platform="youtube",
                    script=script.get('full_script', ''),
                    hook=script.get('hook', '')
                )
                shutil.copy2(thumb_path, str(LATEST_THUMB))
                logger.info(f"   ✅ Frame-based thumbnail")
            except Exception as e:
                logger.warning(f"⚠️ Frame-based thumbnail failed: {e}")

        if not os.path.exists(thumb_path):
            try:
                self._modules['thumbnail_gen'].generate_thumbnail(
                    words=thumb_words,
                    topic=topic,
                    output_path=thumb_path
                )
                shutil.copy2(thumb_path, str(LATEST_THUMB))
                logger.info(f"   ✅ Fallback thumbnail")
            except Exception as e:
                logger.warning(f"⚠️ Thumbnail failed: {e}")

        if frame_path and os.path.exists(frame_path):
            try:
                os.remove(frame_path)
            except OSError:
                pass

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

        # ── 7. SEO CONTENT ──
        title = self._generate_youtube_title(topic, script)
        description = self._generate_youtube_description(topic, script)
        tags = self._generate_youtube_tags(topic, script)
        fb_description = self._generate_facebook_description(topic, script)
        ig_caption = self._generate_instagram_caption(topic, script)

        logger.info(f"   📌 Title: {title}")
        logger.info(f"   💬 Forced CTA included in description")

        # ── 8. CLOUD UPLOAD ──
        video_url = None
        if self._modules['cloud_uploader'].is_configured():
            logger.info("☁️ Step 7: Cloud upload...")
            try:
                video_url = self._modules['cloud_uploader'].upload_video(video_path)
                logger.info(f"   ✅ URL: {video_url}")
            except Exception as e:
                logger.warning(f"⚠️ Cloud upload failed: {e}")

        # ── 9. YOUTUBE UPLOAD ──
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

        # ── 10. FACEBOOK UPLOAD ──
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

        # ── 11. INSTAGRAM UPLOAD ──
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

        # ── 12. UPDATE STATS ──
        uploaded = any([
            yt_result.get('status') not in ['error', 'skipped'],
            fb_result.get('status') not in ['error', 'skipped'],
            ig_result.get('status') not in ['error', 'skipped'],
        ])

        self.stats['total_videos'] += 1
        self.stats['total_duration'] += audio_duration
        self.stats['total_hook_score'] += hook_score
        self.stats['topics_processed'].append(topic)

        # ── 13. RECORD METRICS ──
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
        logger.info(f"🚀 STARTING PIPELINE (USA 2026 - BABY NICHE)")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {'❌' if skip_upload else '✅'}")
        logger.info(f"{'#'*60}\n")

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

            if i < len(topics) - 1:
                delay = 120
                logger.info(f"\n⏳ Waiting {delay}s before next video...")
                await asyncio.sleep(delay)

        self.stats['end_time'] = datetime.now().isoformat()

        logger.info(f"\n{'#'*60}")
        logger.info(f"🏁 PIPELINE COMPLETE")
        logger.info(f"   Success: {self.stats['successful_uploads']}")
        logger.info(f"   Failed:  {self.stats['failed_uploads']}")
        logger.info(f"   Total Duration: {self.stats['total_duration']:.1f}s")
        avg_hook = self.stats['total_hook_score'] / max(1, self.stats['total_videos'])
        logger.info(f"   Avg Hook Score: {avg_hook:.1f}/10")
        logger.info(f"{'#'*60}")

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
        description='YouTube Automation Pipeline - USA 2026 (BABY NICHE)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python orchestrator.py                    # Generate 1 video
  python orchestrator.py --count 3          # Generate 3 videos
  python orchestrator.py --topic "baby brain"  # Specific topic
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

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    orchestrator = AutomationOrchestrator()

    if args.health_check:
        health = orchestrator.health_check()
        print("\n📊 HEALTH CHECK RESULTS:")
        print(json.dumps(health, indent=2, default=str))
        return

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
