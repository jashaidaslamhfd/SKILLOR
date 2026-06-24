"""
YouTube Automation System — MASTER ORCHESTRATOR
Complete End-to-End Pipeline

USAGE:
    python orchestrator.py                    # Run with default settings
    python orchestrator.py --count 3          # Generate 3 videos
    python orchestrator.py --topic "forgetting names"  # Specific topic
    python orchestrator.py --upload-only      # Only upload existing video

FLOW:
    1. Fetch topics from ViralTopicEngine
    2. Generate script with ContentGenerator (self-correcting hooks)
    3. Generate audio with AudioGenerator
    4. Fetch footage with FootageFetcher
    5. Assemble video with VideoAssembler
    6. Generate thumbnail with ThumbnailGenerator
    7. Upload to YouTube, Facebook, Instagram
    8. Save logs and history
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import traceback
import time
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
from config.settings import (
    VIDEO_CONFIG, PLATFORM_CONFIG, API_KEYS,
    AUDIO_CONFIG, SEO_CONFIG, NICHE_CONFIG
)

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

# ============================================================
# CONFIGURATION
# ============================================================
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio"
FOOTAGE_DIR = OUTPUT_DIR / "footage"
CAPTIONS_DIR = OUTPUT_DIR / "captions"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"
HISTORY_DIR = OUTPUT_DIR / "history"

for dir_path in [VIDEO_DIR, AUDIO_DIR, FOOTAGE_DIR, CAPTIONS_DIR, THUMBNAILS_DIR, HISTORY_DIR]:
    dir_path.mkdir(exist_ok=True)


# ============================================================
# ORCHESTRATOR CLASS
# ============================================================
class AutomationOrchestrator:
    """Complete End-to-End Automation Pipeline"""
    
    def __init__(self):
        # Initialize all modules
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
        
        # Statistics
        self.stats = {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_duration': 0,
            'start_time': None,
            'end_time': None,
            'topics_processed': [],
            'errors': []
        }
        
        # Pending topics file
        self.pending_file = HISTORY_DIR / "pending_topics.json"
        self.completed_file = HISTORY_DIR / "completed_topics.json"
        
        # Load history
        self._load_history()
        
        logger.info("✅ System initialized successfully")

    # ============================================================
    # HISTORY MANAGEMENT
    # ============================================================
    
    def _load_history(self):
        """Load history from files"""
        # Load completed topics
        if self.completed_file.exists():
            try:
                with open(self.completed_file, 'r') as f:
                    self.stats = json.load(f)
                logger.info(f"📊 Loaded history: {self.stats.get('total_videos', 0)} videos")
            except Exception as e:
                logger.warning(f"Could not load history: {e}")
        
        # Load pending topics
        self.pending_topics = []
        if self.pending_file.exists():
            try:
                with open(self.pending_file, 'r') as f:
                    self.pending_topics = json.load(f)
                logger.info(f"📋 Loaded {len(self.pending_topics)} pending topics")
            except Exception as e:
                logger.warning(f"Could not load pending topics: {e}")

    def _save_history(self):
        """Save history to files"""
        try:
            with open(self.completed_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
            logger.info("💾 History saved")
        except Exception as e:
            logger.warning(f"Could not save history: {e}")

    def _save_pending(self):
        """Save pending topics"""
        try:
            with open(self.pending_file, 'w') as f:
                json.dump(self.pending_topics, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save pending topics: {e}")

    def _add_to_history(self, topic: str, result: Dict):
        """Add completed topic to history"""
        self.stats['total_videos'] += 1
        self.stats['topics_processed'].append({
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        self._save_history()

    # ============================================================
    # HEALTH CHECK
    # ============================================================
    
    def health_check(self) -> Dict:
        """Check all system components"""
        results = {
            'status': 'ok',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        # Check APIs
        api_status = API_KEYS.validate()
        results['checks']['apis'] = api_status
        
        missing_apis = [k for k, v in api_status.items() if not v]
        if missing_apis:
            results['warnings'].append(f"⚠️ Missing APIs: {', '.join(missing_apis)}")
            results['status'] = 'degraded'
        
        # Check ffmpeg
        import shutil
        has_ffmpeg = shutil.which('ffmpeg') is not None
        results['checks']['ffmpeg'] = has_ffmpeg
        if not has_ffmpeg:
            results['errors'].append("❌ ffmpeg not found - required for video assembly")
            results['status'] = 'error'
        
        # Check directories
        dirs = {
            'output': OUTPUT_DIR.exists(),
            'videos': VIDEO_DIR.exists(),
            'audio': AUDIO_DIR.exists(),
        }
        results['checks']['directories'] = dirs
        
        # Check modules
        modules = {
            'topic_engine': self.topic_engine is not None,
            'content_gen': self.content_gen is not None,
            'audio_gen': self.audio_gen is not None,
        }
        results['checks']['modules'] = modules
        
        return results

    # ============================================================
    # TOPIC MANAGEMENT
    # ============================================================
    
    def get_topics(self, count: int = 1, specific_topic: str = None) -> List[Dict]:
        """Get topics from engine or pending queue"""
        
        # If specific topic provided
        if specific_topic:
            logger.info(f"📝 Using specific topic: {specific_topic}")
            return [{'query': specific_topic, 'source': 'manual'}]
        
        # Check pending queue first
        if self.pending_topics:
            logger.info(f"📋 Using {len(self.pending_topics)} pending topics")
            topics = self.pending_topics[:count]
            self.pending_topics = self.pending_topics[count:]
            self._save_pending()
            return topics
        
        # Fetch from engine
        logger.info(f"🔍 Fetching {count} topics from engine...")
        topics = self.topic_engine.get_daily_topics(count=count * 2)  # Get extra for filtering
        
        # Filter out already completed topics
        completed = [t['topic'] for t in self.stats.get('topics_processed', [])]
        topics = [t for t in topics if t.get('query') not in completed]
        
        # Return requested count
        return topics[:count]

    # ============================================================
    # VIDEO CREATION
    # ============================================================
    
    async def create_video(self, topic_data: Dict) -> Optional[Dict]:
        """Create a complete video from topic data"""
        topic = topic_data.get('query', '')
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🎬 Creating video for: {topic}")
            logger.info(f"{'='*60}")
            
            # ============================================================
            # Step 1: Get Topic Metadata
            # ============================================================
            logger.info("📊 Getting topic metadata...")
            metadata = self.topic_engine.get_topic_metadata(topic_data)
            
            logger.info(f"   Pattern: {metadata.get('pattern', 'unknown')}")
            logger.info(f"   Suspense Score: {metadata.get('suspense_score', 70)}/100")
            logger.info(f"   Viral Score: {metadata.get('viral_score', 50)}/100")
            
            # ============================================================
            # Step 2: Generate Script
            # ============================================================
            logger.info("📝 Generating script with self-correcting hooks...")
            script_data = self.content_gen.generate_script(
                topic=topic,
                angle=metadata.get('angle', ''),
                shock_angle=metadata.get('shock_angle', ''),
                pattern=metadata.get('pattern', 'memory_insight'),
                suspense_score=metadata.get('suspense_score', 70)
            )
            
            logger.info(f"   Words: {script_data.get('word_count', 0)}")
            logger.info(f"   Segments: {len(script_data.get('segments', []))}")
            logger.info(f"   Hook Score: {script_data.get('hook_score', 0)}/10")
            logger.info(f"   Hook Status: {script_data.get('hook_status', 'unknown')}")
            
            # ============================================================
            # Step 3: Generate Audio
            # ============================================================
            logger.info("🎙️ Generating audio...")
            audio_data = await self.audio_gen.generate_with_effects(
                script_data['segments'],
                str(AUDIO_DIR),
                topic=topic
            )
            
            duration = audio_data.get('total_duration', 0)
            logger.info(f"   Duration: {duration:.1f}s")
            logger.info(f"   Word Timings: {len(audio_data.get('word_timings', []))}")
            
            # Fix duration if needed
            if duration < 38 or duration > 58:
                logger.info(f"   ⚠️ Duration {duration:.1f}s outside 40-55s range, fixing...")
                audio_data = await self._fix_duration(audio_data, script_data)
                duration = audio_data.get('total_duration', 0)
                logger.info(f"   ✅ Fixed duration: {duration:.1f}s")
            
            # ============================================================
            # Step 4: Fetch Footage
            # ============================================================
            logger.info("📹 Fetching stock footage...")
            footage_clips = self.footage_fetcher.fetch_footage_for_script(
                script_data['segments'], topic
            )
            footage_paths = self.footage_fetcher.download_footage(
                footage_clips, str(FOOTAGE_DIR)
            )
            
            real_clips = sum(1 for p in footage_paths.values() if p)
            logger.info(f"   Clips: {real_clips}/{len(footage_clips)} downloaded")
            
            # ============================================================
            # Step 5: Generate Captions
            # ============================================================
            logger.info("📝 Generating captions...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ass_path = str(CAPTIONS_DIR / f"captions_{timestamp}.ass")
            
            self.caption_gen.generate_karaoke_ass(
                audio_data.get('word_timings', []),
                ass_path,
                max_duration=duration
            )
            logger.info(f"   ✅ Captions saved: {ass_path}")
            
            # ============================================================
            # Step 6: Assemble Video
            # ============================================================
            logger.info("🎨 Assembling video...")
            video_path = str(VIDEO_DIR / f"video_{timestamp}.mp4")
            
            self.video_assembler.create_video(
                script_data['segments'],
                audio_data,
                footage_paths,
                audio_data.get('word_timings', []),
                video_path,
                caption_ass_path=ass_path
            )
            
            if not os.path.exists(video_path):
                raise Exception("Video file not created")
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"   ✅ Video created: {file_size:.1f} MB")
            
            # Copy to latest
            latest_path = OUTPUT_DIR / "latest_video.mp4"
            import shutil
            shutil.copy2(video_path, latest_path)
            logger.info(f"   📁 Latest video: {latest_path}")
            
            # ============================================================
            # Step 7: Generate Thumbnail
            # ============================================================
            logger.info("🖼️ Generating thumbnail...")
            thumbnail_words = self.content_gen.generate_thumbnail_words(topic)
            thumbnail_path = str(THUMBNAILS_DIR / f"thumb_{timestamp}.jpg")
            
            self.thumbnail_gen.generate_thumbnail(
                thumbnail_words, topic, thumbnail_path
            )
            
            has_thumbnail = os.path.exists(thumbnail_path)
            logger.info(f"   Thumbnail: {'✅' if has_thumbnail else '❌'}")
            
            # ============================================================
            # Step 8: Generate SEO
            # ============================================================
            logger.info("🏷️ Generating SEO...")
            title = self.content_gen.generate_title(topic)
            seo_data = self.content_gen.generate_seo(topic, script_data.get('full_script', ''))
            
            logger.info(f"   Title: {title}")
            logger.info(f"   Tags: {len(seo_data.get('tags', []))}")
            
            # ============================================================
            # Step 9: Return Video Data
            # ============================================================
            video_data = {
                'video_path': video_path,
                'latest_video_path': str(latest_path),
                'thumbnail_path': thumbnail_path if has_thumbnail else None,
                'title': title,
                'description': seo_data.get('description', ''),
                'tags': seo_data.get('tags', []),
                'topic': topic,
                'duration': duration,
                'pattern': metadata.get('pattern', 'unknown'),
                'suspense_score': metadata.get('suspense_score', 70),
                'hook_score': script_data.get('hook_score', 0),
                'hook_status': script_data.get('hook_status', 'unknown'),
                'word_count': script_data.get('word_count', 0),
                'file_size_mb': file_size,
                'timestamp': timestamp
            }
            
            logger.info(f"\n✅ Video creation complete!")
            logger.info(f"   📹 {video_path}")
            logger.info(f"   ⏱️  {duration:.1f}s")
            logger.info(f"   📊 Hook Score: {script_data.get('hook_score', 0)}/10")
            
            return video_data
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            logger.error(traceback.format_exc())
            return None

    # ============================================================
    # DURATION FIX
    # ============================================================
    
    async def _fix_duration(self, audio_data: Dict, script_data: Dict) -> Dict:
        """Fix audio duration if out of range"""
        duration = audio_data.get('total_duration', 0)
        
        if duration < 38:
            logger.info("   🔧 Adding words to script...")
            for seg in script_data['segments']:
                if seg.get('type') == 'story':
                    seg['text'] += " And that's the quiet truth about your brain... it's always working, always filtering, always deciding what to keep and what to let go. You just don't notice it happening until you walk into a room and forget why you're there."
                    seg['duration'] = round(len(seg['text'].split()) / (AUDIO_CONFIG.WORDS_PER_MINUTE / 60), 2)
                    break
            
            audio_data = await self.audio_gen.generate_with_effects(
                script_data['segments'],
                str(AUDIO_DIR),
                topic=script_data.get('topic', '')
            )
        
        elif duration > 58:
            logger.info("   🔧 Trimming script...")
            for seg in script_data['segments']:
                if seg.get('type') == 'story':
                    words = seg['text'].split()
                    if len(words) > 20:
                        seg['text'] = ' '.join(words[:20])
                        seg['duration'] = round(len(seg['text'].split()) / (AUDIO_CONFIG.WORDS_PER_MINUTE / 60), 2)
                    break
            
            audio_data = await self.audio_gen.generate_with_effects(
                script_data['segments'],
                str(AUDIO_DIR),
                topic=script_data.get('topic', '')
            )
        
        return audio_data

    # ============================================================
    # UPLOAD TO PLATFORMS
    # ============================================================
    
    async def upload_to_platforms(self, video_data: Dict) -> Dict:
        """Upload video to all configured platforms"""
        results = {}
        
        logger.info(f"\n📤 Starting uploads...")
        
        # ============================================================
        # YouTube Upload
        # ============================================================
        if API_KEYS.REFRESH_TOKEN and API_KEYS.GOOGLE_CLIENT_ID:
            logger.info("📺 Uploading to YouTube...")
            try:
                result = self.youtube_uploader.upload_video(
                    video_data['video_path'],
                    video_data.get('thumbnail_path'),
                    video_data['title'],
                    video_data['description'],
                    video_data.get('tags', []),
                    privacy_status=getattr(SEO_CONFIG, 'PRIVACY_STATUS', 'public')
                )
                results['youtube'] = result
                if result.get('url'):
                    logger.info(f"   ✅ YouTube: {result['url']}")
                else:
                    logger.warning(f"   ⚠️ YouTube: {result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ YouTube failed: {e}")
                results['youtube'] = {'status': 'error', 'error': str(e)}
        else:
            logger.info("⏭️ Skipping YouTube - credentials not set")
            results['youtube'] = {'status': 'skipped'}
        
        # Delay between uploads
        delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)
        
        # ============================================================
        # Facebook Upload
        # ============================================================
        if API_KEYS.FACEBOOK_ACCESS_TOKEN and API_KEYS.FACEBOOK_PAGE_ID:
            if len(results) > 1:
                await asyncio.sleep(delay)
            
            logger.info("📘 Uploading to Facebook...")
            try:
                result = self.facebook_uploader.upload_video(
                    video_path=video_data['video_path'],
                    thumbnail_path=video_data.get('thumbnail_path'),
                    title=video_data['title'],
                    description=video_data['description'],
                    privacy='PUBLIC'
                )
                results['facebook'] = result
                if result.get('url'):
                    logger.info(f"   ✅ Facebook: {result['url']}")
                else:
                    logger.warning(f"   ⚠️ Facebook: {result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ Facebook failed: {e}")
                results['facebook'] = {'status': 'error', 'error': str(e)}
        else:
            logger.info("⏭️ Skipping Facebook - credentials not set")
            results['facebook'] = {'status': 'skipped'}
        
        # ============================================================
        # Instagram Upload
        # ============================================================
        if API_KEYS.INSTAGRAM_ACCESS_TOKEN and API_KEYS.INSTAGRAM_USER_ID:
            if len(results) > 2:
                await asyncio.sleep(delay)
            
            logger.info("📸 Uploading to Instagram...")
            try:
                if not self.cloud_uploader.is_configured():
                    logger.warning("   ⚠️ Cloudinary not configured - skipping Instagram")
                    results['instagram'] = {'status': 'skipped', 'reason': 'Cloudinary not configured'}
                else:
                    # Upload to Cloudinary
                    video_url = self.cloud_uploader.upload_video(
                        video_data['video_path'],
                        public_id=f"short_{int(time.time())}"
                    )
                    
                    if not video_url:
                        results['instagram'] = {'status': 'error', 'error': 'Cloudinary upload failed'}
                    else:
                        result = self.instagram_uploader.upload_reel(
                            video_url=video_url,
                            thumbnail_path=video_data.get('thumbnail_path'),
                            caption=video_data['description'],
                            hashtags=video_data.get('tags', [])
                        )
                        results['instagram'] = result
                        if result.get('url'):
                            logger.info(f"   ✅ Instagram: {result['url']}")
                        else:
                            logger.warning(f"   ⚠️ Instagram: {result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ Instagram failed: {e}")
                results['instagram'] = {'status': 'error', 'error': str(e)}
        else:
            logger.info("⏭️ Skipping Instagram - credentials not set")
            results['instagram'] = {'status': 'skipped'}
        
        return results

    # ============================================================
    # MAIN PIPELINE
    # ============================================================
    
    async def run_pipeline(self, count: int = 1, 
                           specific_topic: str = None,
                           upload: bool = True,
                           skip_upload: bool = False) -> Dict:
        """
        Run the complete automation pipeline
        
        Args:
            count: Number of videos to generate
            specific_topic: Specific topic to use (optional)
            upload: Whether to upload to platforms
            skip_upload: Skip upload even if credentials exist
        """
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING AUTOMATION PIPELINE")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {upload and not skip_upload}")
        logger.info(f"{'#'*60}\n")
        
        # Health check
        health = self.health_check()
        if health['status'] == 'error':
            logger.error(f"❌ System health check failed: {health['errors']}")
            return {'status': 'error', 'errors': health['errors']}
        
        if health['warnings']:
            logger.warning(f"⚠️ System warnings: {health['warnings']}")
        
        # Get topics
        topics = self.get_topics(count, specific_topic)
        
        if not topics:
            logger.error("❌ No topics available")
            return {'status': 'error', 'error': 'No topics available'}
        
        logger.info(f"📋 Topics: {[t.get('query') for t in topics]}")
        
        # Process each topic
        results = []
        successful = 0
        failed = 0
        
        for i, topic_data in enumerate(topics):
            logger.info(f"\n{'─'*60}")
            logger.info(f"📹 Processing video {i+1}/{len(topics)}")
            logger.info(f"{'─'*60}")
            
            # Create video
            video_data = await self.create_video(topic_data)
            
            if not video_data:
                logger.error(f"❌ Failed to create video for: {topic_data.get('query')}")
                failed += 1
                self.stats['failed_uploads'] += 1
                continue
            
            # Upload if enabled
            upload_results = {}
            if upload and not skip_upload:
                upload_results = await self.upload_to_platforms(video_data)
                self.stats['successful_uploads'] += 1
            
            # Save to history
            self._add_to_history(topic_data.get('query'), {
                'video': video_data,
                'uploads': upload_results
            })
            
            results.append({
                'topic': topic_data.get('query'),
                'video_data': video_data,
                'upload_results': upload_results,
                'status': 'success'
            })
            
            successful += 1
            
            # Delay between videos
            if i < len(topics) - 1:
                delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)
                logger.info(f"\n⏳ Waiting {delay}s before next video...")
                await asyncio.sleep(delay)
        
        # Final summary
        logger.info(f"\n{'#'*60}")
        logger.info(f"🏁 PIPELINE COMPLETE")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Successful: {successful}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"{'#'*60}")
        
        return {
            'status': 'complete',
            'successful': successful,
            'failed': failed,
            'results': results,
            'stats': self.stats
        }


# ============================================================
# MAIN ENTRY POINT
# ============================================================
async def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='YouTube Automation System - Complete Pipeline'
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Number of videos to generate (default: 1)'
    )
    parser.add_argument(
        '--topic', '-t',
        type=str,
        help='Specific topic to use (overrides topic fetching)'
    )
    parser.add_argument(
        '--upload-only', '-u',
        action='store_true',
        help='Only upload existing latest video (skip creation)'
    )
    parser.add_argument(
        '--skip-upload', '-s',
        action='store_true',
        help='Create video but skip uploading'
    )
    parser.add_argument(
        '--health-check', '-hc',
        action='store_true',
        help='Run health check and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = AutomationOrchestrator()
    
    # Health check only
    if args.health_check:
        health = orchestrator.health_check()
        print("\n📊 HEALTH CHECK RESULTS:")
        print(json.dumps(health, indent=2, default=str))
        return
    
    # Upload only mode
    if args.upload_only:
        latest_video = OUTPUT_DIR / "latest_video.mp4"
        if not latest_video.exists():
            print("❌ No latest video found in output directory")
            return
        
        # Load video data from history
        video_data = {
            'video_path': str(latest_video),
            'thumbnail_path': str(THUMBNAILS_DIR / "latest_thumb.jpg"),
            'title': "Brain Science Short",
            'description': "Check out this brain science fact!",
            'tags': ['#Shorts', '#BrainFacts'],
        }
        
        upload_results = await orchestrator.upload_to_platforms(video_data)
        print("\n📤 Upload Results:")
        print(json.dumps(upload_results, indent=2, default=str))
        return
    
    # Run pipeline
    results = await orchestrator.run_pipeline(
        count=args.count,
        specific_topic=args.topic,
        upload=True,
        skip_upload=args.skip_upload
    )
    
    print("\n📊 FINAL RESULTS:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        traceback.print_exc()