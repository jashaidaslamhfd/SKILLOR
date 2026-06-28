"""
YouTube Automation System — MASTER ORCHESTRATOR (USA 2026 FINAL)
Complete End-to-End Pipeline with YouTube SEO Optimization & Analytics

FIXES APPLIED:
1. ✅ AI-generated titles with fallback (15-55 chars, USA optimized)
2. ✅ Dynamic descriptions with engagement hooks (comment-bait + polls)
3. ✅ Rotating tags (no spam signals - 2026 algorithm)
4. ✅ USA geo-targeting hints for YouTube algorithm
5. ✅ Facebook/Instagram optimized descriptions
6. ✅ End-screen hooks for session time boost
7. ✅ Proper duration validation (42-55s)
8. ✅ HD frame extraction for thumbnails
9. ✅ Unique titles every time (20+ templates)
10. ✅ No duplicate hashtags (spam-free)
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

        # Lazy imports to avoid circular dependency
        self._modules = {}
        self._init_modules()

        # Metrics
        self.metrics = None
        try:
            from core.metrics import MetricsTracker
            self.metrics = MetricsTracker()
            logger.info("✅ Metrics tracking enabled")
        except ImportError:
            logger.warning("⚠️ MetricsTracker not found")

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
        # UNIQUE TITLE TEMPLATES - USA 2026 (20+ variations)
        # NO warning/danger - curiosity-driven only
        # ============================================================
        self.title_templates = [
            # Type 1: "Your brain" hooks
            "Your brain does this with {topic} 🧠",
            "Your brain is hiding {topic} from you 🧠",
            "Your brain actually does this with {topic} 🧠",
            
            # Type 2: "Why" hooks
            "Why {topic} happens to you 🧠",
            "Why {topic} is more common than you think 🧠",
            "Why does {topic} even happen 🧠",
            
            # Type 3: "Hidden truth" hooks
            "The truth about {topic} nobody tells you 🧠",
            "The real reason behind {topic} 🧠",
            "What scientists found about {topic} 🧠",
            
            # Type 4: "What nobody tells you" hooks
            "What nobody explains about {topic} 🧠",
            "What your brain does with {topic} 🧠",
            "What {topic} actually means for you 🧠",
            
            # Type 5: "How" hooks
            "How {topic} affects your brain daily 🧠",
            "How {topic} really works inside you 🧠",
            "How your body creates {topic} 🧠",
            
            # Type 6: "Science/Explained" hooks
            "The science behind {topic} explained 🧠",
            "{topic} explained in 60 seconds 🧠",
            "The science you need to know about {topic} 🧠",
            
            # Type 7: Curiosity + Relatability (NO fear/danger)
            "You won't believe what causes {topic} 🧠",
            "This is why {topic} keeps happening 🧠",
            "The one reason behind {topic} 🧠",
            
            # Type 8: "Simple/Easy" hooks
            "The simple truth about {topic} 🧠",
            "The easy way to understand {topic} 🧠",
            "What {topic} really means for you 🧠",
            
            # USA-specific hooks
            "Every American experiences {topic} 🧠",
            "Why {topic} is happening to you right now 🧠",
        ]

        # ============================================================
        # DESCRIPTION TEMPLATES - USA 2026
        # ============================================================
        self.description_templates = [
            "🧠 The truth about {topic} that nobody tells you...",
            "🔬 Science reveals what actually happens with {topic}...",
            "💡 One simple fact about {topic} that changes everything...",
            "⚡ The hidden reason behind {topic} explained...",
            "🎯 What {topic} really means for your brain...",
            "🇺🇸 Every American should know this about {topic}...",
        ]

        logger.info("✅ System initialized (USA 2026)")

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
    # GENERATE YOUTUBE TITLE - AI FIRST, FALLBACK SECOND
    # ============================================================
    def _generate_youtube_title(self, topic: str, script: Dict) -> str:
        """
        Generate UNIQUE YouTube title - AI first, template fallback.
        USA 2026 optimized: 15-55 characters.
        """
        # ATTEMPT 1: AI-generated title
        try:
            ai_title = self._modules['content_gen'].generate_title(topic=topic)
            if ai_title and 15 <= len(ai_title) <= 55:
                logger.info(f"   ✅ AI title: {ai_title}")
                return ai_title
        except Exception as e:
            logger.warning(f"   ⚠️ AI title generation failed: {e}")
        
        # ATTEMPT 2: Smart template selection with short topic
        template = random.choice(self.title_templates)
        topic_short = ' '.join(topic.split()[:3])
        
        try:
            title = template.format(topic=topic_short)
        except (KeyError, IndexError):
            title = template.replace('{topic}', topic_short)
        
        # Hard cap at 55 chars (YouTube Shorts sweet spot)
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
    # GENERATE YOUTUBE DESCRIPTION - USA 2026
    # ============================================================
    def _generate_youtube_description(self, topic: str, script: Dict) -> str:
        """Generate UNIQUE YouTube description with engagement hooks."""
        hook = script.get('hook', '')
        story = script.get('story', '')
        shock = script.get('shock', '')
        
        intro = random.choice(self.description_templates).format(topic=topic)
        
        # Comment-bait questions (USA tested)
        comment_questions = [
            f"Has {topic} ever happened to you? Tell me below 👇",
            f"Do you experience {topic}? Drop a comment!",
            f"What's your biggest body mystery? Comment below!",
            f"Have you noticed {topic}? Let me know in the comments 👇",
            f"Tag someone who always experiences {topic} 😂",
            f"Americans - has this happened to you? Comment YES or NO!",
        ]
        comment_bait = random.choice(comment_questions)
        
        # Quick Poll (drives comments)
        poll_options = [
            f"🏟️ QUICK POLL: Has {topic} happened to you? Comment YES or NO!",
            f"🏟️ POLL: Did you know about {topic} before this? Comment knew or wow!",
            f"🏟️ POLL: How often does {topic} happen? Comment always, sometimes, or never!",
            f"🏟️ QUICK POLL: Be honest — has your body ever done this? Comment me if yes!",
        ]
        poll = random.choice(poll_options)
        
        # Dynamic topic-specific hashtags
        topic_words = [w for w in topic.lower().split() if len(w) > 3 and w not in 
                       ['your', 'body', 'brain', 'when', 'that', 'this', 'with', 'from', 'about']]
        topic_hashtag = '#' + topic_words[0].capitalize() if topic_words else '#BodyScience'
        
        # Rotating hashtag sets (spam-free)
        hashtag_sets = [
            f"#Shorts #{topic_hashtag.replace('#','')} #BrainFacts #BodyScience #healthtips",
            f"#Shorts #BrainHealth #{topic_hashtag.replace('#','')} #facts #science",
            f"#Shorts #{topic_hashtag.replace('#','')} #DidYouKnow #BodyFacts #health",
            f"#Shorts #BrainFacts #{topic_hashtag.replace('#','')} #BodyMysteries #tips",
            f"#Shorts #{topic_hashtag.replace('#','')} #ScienceExplained #facts #brain",
            f"#Shorts #{topic_hashtag.replace('#','')} #USA #health #wellness",
        ]
        hashtags = random.choice(hashtag_sets)

        description = f"""
{intro}

🧠 What You'll Learn:
• Why {topic} happens and what causes it
• The science behind how your body and brain work
• What you can do about it

💡 Key Fact:
{shock}

{poll}
💬 {comment_bait}

👍 Like if this has happened to you!
🔔 Follow for daily body science nobody teaches you!

{hashtags}
""".strip()

        # Deduplicate hashtags (spam-free)
        import re as _re
        hashtag_pattern = _re.findall(r'#\w+', description)
        seen_hashtags = set()
        for ht in hashtag_pattern:
            ht_lower = ht.lower()
            if ht_lower in seen_hashtags:
                description = description.replace(ht, '', 1).replace('  ', ' ')
            else:
                seen_hashtags.add(ht_lower)

        return description[:5000]

    # ============================================================
    # GENERATE YOUTUBE TAGS - USA 2026 (Spam-Free)
    # ============================================================
    def _generate_youtube_tags(self, topic: str, script: Dict) -> List[str]:
        """Generate YouTube tags - DYNAMIC to avoid spam signals"""
        # Rotating base tag sets
        base_tag_sets = [
            ["brain science", "brain fog", "why do i forget", "brain health", "body science"],
            ["brain facts", "cognitive health", "why does my body", "brain fog causes", "health facts"],
            ["body secrets", "brain tips", "memory loss", "neuroscience", "health tips"],
            ["why does this happen", "brain explained", "body science", "mind facts", "did you know"],
            ["usa health", "american wellness", "body science", "brain facts", "explained"],
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
    # GENERATE FACEBOOK DESCRIPTION - USA 2026
    # ============================================================
    def _generate_facebook_description(self, topic: str, script: Dict) -> str:
        hook = script.get('hook', '')
        shock = script.get('shock', '')
        
        fb_questions = [
            f"Has this ever happened to you? Share your experience below!",
            f"Tag someone who ALWAYS experiences {topic}",
            f"Did you know this about {topic}? React if this is you!",
            f"Who else thought they were the only one? Comment below!",
            f"Americans - has this happened to you? React!",
        ]
        fb_question = random.choice(fb_questions)
        
        # Dynamic FB hashtags (spam-free)
        fb_hashtag_sets = [
            "#memory #brainhealth #BrainFacts #healthtips #shorts #reels",
            "#brainfog #BodyScience #facts #health #shorts #reels",
            "#BrainFacts #healthtips #DidYouKnow #brain #shorts #reels",
            "#bodyfacts #BrainFacts #health #science #shorts #reels",
            "#USA #health #wellness #BrainFacts #shorts #reels",
        ]
        fb_hashtags = random.choice(fb_hashtag_sets)
        
        return f"""{hook}

{shock}

The science behind why this happens to your body and brain.

What you need to know:
- It's more common than you think
- There's a scientific reason
- You can do something about it

{fb_question}

React if this blew your mind!
Follow for more body science

{fb_hashtags}"""

    # ============================================================
    # GENERATE INSTAGRAM CAPTION - USA 2026
    # ============================================================
    def _generate_instagram_caption(self, topic: str, script: Dict) -> str:
        hook = script.get('hook', '')
        topic_words = topic.lower().replace('-', ' ').replace('?', '').split()
        topic_hashtag = '#' + topic_words[0].capitalize() if topic_words else '#BodyFacts'
        
        ig_hooks = [
            f"Save this for the next time {topic} happens to you! 📌",
            f"Double tap if {topic} has ever happened to you! 💛",
            f"Share this with someone who needs to know! 📤",
            'Comment YES if this is SO you 😂',
            f"Americans - has {topic} happened to you? Comment YES! 🇺🇸",
        ]
        ig_hook = random.choice(ig_hooks)
        
        # Dynamic IG hashtags (spam-free)
        ig_hashtag_sets = [
            f"#memory #{topic_hashtag.replace('#','')} #BrainFacts #healthtips #shorts #reels #explore",
            f"#brainfog #{topic_hashtag.replace('#','')} #facts #wellness #shorts #reels #explore",
            f"#BrainFacts #{topic_hashtag.replace('#','')} #DidYouKnow #brain #shorts #reels #viral",
            f"#{topic_hashtag.replace('#','')} #bodyfacts #health #science #shorts #reels #fyp",
            f"#{topic_hashtag.replace('#','')} #USA #health #wellness #shorts #reels #explore",
        ]
        ig_hashtags = random.choice(ig_hashtag_sets)
        
        return f"""🧠 {hook}

The science behind {topic} explained in 60 seconds!

💡 Why it happens
🔬 The science
✅ What you can do

{ig_hook}
Follow for more brain tips 👆

{ig_hashtags}"""

    # ============================================================
    # GENERATE ENDSCREEN HOOK - USA 2026
    # ============================================================
    def _generate_endscreen_hook(self, topic: str) -> str:
        endscreen_hooks = [
            "🔔 SUBSCRIBE for daily body science nobody teaches you!",
            "🔔 Follow for Part 2 — your body has more secrets like this!",
            "🔔 Hit the bell — next video reveals why your body does THIS at 3am!",
            "🔔 Subscribe — tomorrow: the body trick 90% of people don't know!",
            "🔔 Follow for more — next Short reveals what your gut is hiding!",
            "🔔 Subscribe — every American should know this!",
        ]
        return random.choice(endscreen_hooks)

    # ============================================================
    # VALIDATE DURATION
    # ============================================================
    def _validate_duration(self, duration: float) -> bool:
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

        # Karaoke ASS
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
        logger.info("🖼️ Step 6: Generating thumbnail from video frame...")
        thumb_path = str(THUMB_DIR / f"{safe}_{ts}.jpg")
        thumb_words = self._modules['content_gen'].generate_thumbnail_words(topic=topic)
        frame_path = None

        # Step 6a: Extract HD frame
        try:
            frame_path = self._modules['video_assembler'].extract_hd_frame(
                video_path=video_path,
                output_path=str(THUMB_DIR / f"{safe}_{ts}_frame.png")
            )
            if frame_path:
                logger.info(f"   ✅ HD frame extracted → {frame_path}")
        except Exception as e:
            logger.warning(f"⚠️ Frame extraction failed: {e}")
            frame_path = None

        # Step 6b: Generate thumbnail FROM video frame (PRIMARY)
        if frame_path and os.path.exists(frame_path):
            try:
                self._modules['thumbnail_gen'].generate_thumbnail_from_frame(
                    frame_path=frame_path,
                    words=thumb_words,
                    topic=topic,
                    output_path=thumb_path,
                    platform="youtube",
                    script=script.get('script', '') if isinstance(script, dict) else str(script),
                    hook=script.get('hook', '') if isinstance(script, dict) else ''
                )
                shutil.copy2(thumb_path, str(LATEST_THUMB))
                logger.info(f"   ✅ Frame-based thumbnail → {thumb_path}")
            except Exception as e:
                logger.warning(f"⚠️ Frame-based thumbnail failed: {e}")
                frame_path = None

        # Step 6c: Fallback to PIL-only
        if not frame_path or not os.path.exists(thumb_path):
            try:
                self._modules['thumbnail_gen'].generate_thumbnail(
                    words=thumb_words,
                    topic=topic,
                    output_path=thumb_path
                )
                shutil.copy2(thumb_path, str(LATEST_THUMB))
                logger.info(f"   ✅ Fallback thumbnail → {thumb_path}")
            except Exception as e:
                logger.warning(f"⚠️ All thumbnail generation failed: {e}")
                thumb_path = None

        # Clean up frame
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

        # ── 7. CLOUD UPLOAD ──
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

        # ── 8. SEO CONTENT ──
        title = self._generate_youtube_title(topic, script)
        description = self._generate_youtube_description(topic, script)
        endscreen = self._generate_endscreen_hook(topic)
        description = description + '\n\n' + endscreen
        tags = self._generate_youtube_tags(topic, script)

        fb_description = self._generate_facebook_description(topic, script)
        ig_caption = self._generate_instagram_caption(topic, script)

        logger.info(f"   📌 Title: {title}")

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
    # UPLOAD TO PLATFORMS (For --upload-only mode)
    # ============================================================
    async def upload_to_platforms(self, video_data: Dict) -> Dict:
        """Upload an existing video to all platforms."""
        results = {}
        video_path = video_data.get('video_path', '')
        thumbnail_path = video_data.get('thumbnail_path')
        title = video_data.get('title', 'Brain Science Short')
        description = video_data.get('description', '')
        tags = video_data.get('tags', [])
        fb_description = video_data.get('fb_description', description)
        ig_caption = video_data.get('ig_caption', description)

        # YouTube
        yt_result = {'status': 'skipped'}
        try:
            yt_result = self._modules['youtube_uploader'].upload_video(
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                title=title,
                description=description,
                tags=tags if isinstance(tags, list) else [],
                privacy_status='public'
            )
            logger.info(f"   ✅ YouTube: {yt_result.get('video_id', 'done')}")
        except Exception as e:
            logger.error(f"   ❌ YouTube: {e}")
            yt_result = {'status': 'error', 'error': str(e)}
        results['youtube'] = yt_result

        # Facebook
        fb_result = {'status': 'skipped'}
        try:
            fb_result = self._modules['facebook_uploader'].upload_video(
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                title=title[:60],
                description=fb_description,
                privacy='PUBLIC'
            )
            logger.info(f"   ✅ Facebook: {fb_result.get('video_id', 'done')}")
        except Exception as e:
            logger.error(f"   ❌ Facebook: {e}")
            fb_result = {'status': 'error', 'error': str(e)}
        results['facebook'] = fb_result

        # Instagram
        ig_result = {'status': 'skipped'}
        video_url = None
        if self._modules['cloud_uploader'].is_configured():
            try:
                video_url = self._modules['cloud_uploader'].upload_video(video_path)
            except Exception as e:
                logger.warning(f"⚠️ Cloud upload failed: {e}")
        
        if video_url:
            try:
                ig_result = self._modules['instagram_uploader'].upload_reel(
                    video_url=video_url,
                    thumbnail_path=thumbnail_path,
                    caption=ig_caption,
                    hashtags=tags[:10] if isinstance(tags, list) else []
                )
                logger.info(f"   ✅ Instagram: {ig_result.get('media_id', 'done')}")
            except Exception as e:
                logger.error(f"   ❌ Instagram: {e}")
                ig_result = {'status': 'error', 'error': str(e)}
        results['instagram'] = ig_result

        return results

    # ============================================================
    # MAIN PIPELINE
    # ============================================================
    async def run_pipeline(self, count: int = 1, specific_topic: str = None,
                           skip_upload: bool = False) -> Dict:

        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING PIPELINE (USA 2026)")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {'❌' if skip_upload else '✅'}")
        logger.info(f"{'#'*60}\n")

        # Health check
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

        # ── FINAL SUMMARY ──
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
        description='YouTube Automation Pipeline - USA 2026',
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
