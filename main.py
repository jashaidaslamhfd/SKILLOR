"""
YouTube Automation System - Main Orchestrator
"""

import asyncio
import os
import traceback
from datetime import datetime

from config.settings import VIDEO_CONFIG, PLATFORM_CONFIG, API_KEYS
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.audio_generator import AudioGenerator
from core.footage_fetcher import FootageFetcher
from core.video_assembler import VideoAssembler
from core.thumbnail_generator import ThumbnailGenerator
from uploaders.youtube_uploader import YouTubeUploader
from uploaders.facebook_uploader import FacebookUploader
from uploaders.instagram_uploader import InstagramUploader

class YouTubeAutomationSystem:
    def __init__(self):
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.fb_uploader = FacebookUploader()
        self.ig_uploader = InstagramUploader()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def create_video(self, topic_data):
        topic = topic_data['query']
        angle = self.topic_engine.get_topic_angle(topic_data)
        
        print(f"\n🎬 Creating video for: {topic}")
        
        # 1. Generate Content
        script_data = self.content_gen.generate_script(topic, angle)

        # FIX: defensive fallback — if content_generator ever returns an
        # unexpected shape (missing keys, plain string, etc.) this keeps
        # the pipeline running instead of crashing with a KeyError.
        if not isinstance(script_data, dict):
            script_data = {'full_script': str(script_data), 'segments': [], 'word_count': 0, 'duration': 0}
        if not script_data.get('full_script'):
            script_data['full_script'] = (
                script_data.get('script') or script_data.get('text')
                or f"Discover the shocking truth behind {topic}."
            )
        if 'segments' not in script_data or not script_data['segments']:
            script_data['segments'] = [{'type': 'story', 'text': script_data['full_script'], 'is_pause': False}]
        script_data.setdefault('word_count', len(script_data['full_script'].split()))
        script_data.setdefault('duration', 0)

        title = self.content_gen.generate_title(topic)
        seo_data = self.content_gen.generate_seo(topic, script_data['full_script'])
        thumbnail_words = self.content_gen.generate_thumbnail_words(topic)
        
        print(f"    📝 Script: {script_data['word_count']} words, ~{script_data['duration']:.1f}s estimated")
        
        # 2. Generate Audio
        print("🎙️ Generating voice...")
        audio_dir = os.path.join(self.output_dir, "audio")
        loop = asyncio.get_event_loop()
        audio_data = await loop.run_in_executor(
            None, lambda: self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)
        )
        
        # DEBUG: Audio info
        actual_duration = audio_data['total_duration']
        print(f"    📊 Audio: {actual_duration:.1f}s ACTUAL duration")
        print(f"    📊 Words: {len(audio_data['word_timings'])} timings")
        if audio_data['word_timings']:
            first = audio_data['word_timings'][0]
            last = audio_data['word_timings'][-1]
            print(f"    📊 First: '{first['word']}' at {first['start']:.1f}s")
            print(f"    📊 Last: '{last['word']}' at {last['start']:.1f}s")
        
        if not (40 <= actual_duration <= 55):
            print(f"    ⚠️ WARNING: Duration {actual_duration:.1f}s is outside 40-55s target!")
        
        # 3. Fetch Footage
        print("📹 Fetching footage...")
        footage_dir = os.path.join(self.output_dir, "footage")
        footage_clips = self.footage_fetcher.fetch_footage_for_script(script_data['segments'], topic)
        self.footage_fetcher.download_footage(footage_clips, footage_dir)
        
        # 4. Assemble Video
        print("🎨 Assembling video...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_path = os.path.abspath(os.path.join(self.output_dir, f"video_{timestamp}.mp4"))
        self.video_assembler.create_video(
            script_data['segments'], 
            audio_data, 
            footage_clips, 
            audio_data['word_timings'], 
            video_path
        )
        
        # VERIFY: Check video created
        if not os.path.exists(video_path):
            raise Exception(f"Video file not created: {video_path}")
        
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"✅ Video created: {video_path} ({file_size:.1f} MB)")
        
        # FIX #3: Copy video to accessible location for viewing
        # Also save a copy with a predictable name for easy access
        latest_video_path = os.path.join(self.output_dir, "latest_video.mp4")
        import shutil
        shutil.copy2(video_path, latest_video_path)
        print(f"✅ Latest video copy: {latest_video_path}")
        
        # 5. Generate Thumbnail
        print("🖼️ Generating thumbnail...")
        thumbnail_path = os.path.join(self.output_dir, f"thumb_{timestamp}.jpg")
        self.thumbnail_gen.generate_thumbnail(thumbnail_words, topic, thumbnail_path)
        
        if not os.path.exists(thumbnail_path):
            print(f"⚠️ Thumbnail not created, continuing without it")
            thumbnail_path = None
        else:
            print(f"✅ Thumbnail created: {thumbnail_path}")
        
        return {
            'video_path': video_path,
            'latest_video_path': latest_video_path,
            'thumbnail_path': thumbnail_path,
            'title': title,
            'description': seo_data['description'],
            'tags': seo_data['tags'],
            'topic': topic,
            'duration': actual_duration,
        }
    
    async def upload_to_platforms(self, video_data):
        """Upload to all platforms — auto-upload where credentials exist, skip cleanly where they don't"""
        results = {}

        if not os.path.exists(video_data['video_path']):
            print(f"❌ Video file missing: {video_data['video_path']}")
            return {'error': 'Video file missing'}

        thumbnail_path = video_data.get('thumbnail_path')
        if thumbnail_path and not os.path.exists(thumbnail_path):
            print(f"⚠️ Thumbnail missing, uploading without it")
            thumbnail_path = None

        # FIX: Pre-flight credential checks — if a platform's keys aren't
        # set, skip it cleanly instead of attempting and throwing an error.
        # Platforms with valid credentials still auto-upload normally.
        yt_ready = bool(API_KEYS.REFRESH_TOKEN and API_KEYS.GOOGLE_CLIENT_ID and API_KEYS.GOOGLE_CLIENT_SECRET)
        fb_ready = bool(API_KEYS.FACEBOOK_ACCESS_TOKEN and API_KEYS.FACEBOOK_PAGE_ID)
        ig_ready = bool(API_KEYS.INSTAGRAM_ACCESS_TOKEN and API_KEYS.INSTAGRAM_USER_ID)

        # YouTube
        if yt_ready:
            print("📺 Uploading to YouTube...")
            try:
                yt_result = self.youtube_uploader.upload_video(
                    video_data['video_path'],
                    thumbnail_path,
                    video_data['title'],
                    video_data['description'],
                    video_data['tags']
                )
                results['youtube'] = yt_result
                print(f"  ✅ YouTube: {yt_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  ❌ YouTube failed: {e}")
                results['youtube'] = {'error': str(e)}
        else:
            print("⏭️  Skipping YouTube — credentials not set (REFRESH_TOKEN / GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)")
            results['youtube'] = {'status': 'skipped', 'reason': 'credentials not set'}

        # Facebook
        if fb_ready:
            print("📘 Uploading to Facebook...")
            try:
                fb_result = self.fb_uploader.upload_video(
                    video_data['video_path'],
                    thumbnail_path,
                    video_data['title'],
                    video_data['description']
                )
                results['facebook'] = fb_result
                print(f"  ✅ Facebook: {fb_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  ❌ Facebook failed: {e}")
                results['facebook'] = {'error': str(e)}
        else:
            print("⏭️  Skipping Facebook — credentials not set (FACEBOOK_ACCESS_TOKEN / FACEBOOK_PAGE_ID)")
            results['facebook'] = {'status': 'skipped', 'reason': 'credentials not set'}

        # Instagram
        if ig_ready:
            print("📸 Uploading to Instagram...")
            try:
                ig_result = self.ig_uploader.upload_reel(
                    video_data['video_path'],
                    thumbnail_path,
                    video_data['description'],
                    video_data['tags']
                )
                results['instagram'] = ig_result
                print(f"  ✅ Instagram: {ig_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  ❌ Instagram failed: {e}")
                results['instagram'] = {'error': str(e)}
        else:
            print("⏭️  Skipping Instagram — credentials not set (INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_USER_ID)")
            results['instagram'] = {'status': 'skipped', 'reason': 'credentials not set'}

        return results
    
    async def run_daily(self):
        print(f"\n🚀 Starting automation - {datetime.now()}")
        print(f"🎯 Target: 1 Short per run")

        # FIX: count=1 — exactly one video per run (was producing 2 before
        # due to a duplicate class definition in topic_engine.py)
        topics = self.topic_engine.get_daily_topics(count=1)

        if not topics:
            print("⚠️ No topics found! Using fallback.")
            topics = self.topic_engine._get_fallback_topics()[:1]

        successes = 0
        for i, topic in enumerate(topics):
            print(f"\n{'='*50}")
            print(f"Video {i+1}/{len(topics)}: {topic['query']}")
            print(f"{'='*50}")

            try:
                video_data = await self.create_video(topic)

                print(f"\n📤 Starting uploads...")
                upload_results = await self.upload_to_platforms(video_data)

                print(f"\n✅ Video {i+1} complete!")
                print(f"   📁 File: {video_data['video_path']}")
                print(f"   ⏱️  Duration: {video_data['duration']:.1f}s")

                for platform, result in upload_results.items():
                    status = result.get('status', 'unknown')
                    url = result.get('url', 'N/A')
                    if status in ['uploaded', 'published']:
                        print(f"  🟢 {platform.title()}: {url}")
                    else:
                        print(f"  🔴 {platform.title()}: {status} - {result.get('error', 'Unknown error')}")

                successes += 1

                if i < len(topics) - 1:
                    print(f"\n⏳ Waiting 60 seconds before next video...")
                    await asyncio.sleep(60)

            except Exception as e:
                # FIX: one failed video no longer stops the whole batch —
                # log it and move on to the next topic instead.
                print(f"❌ Error in video {i+1}: {e}")
                traceback.print_exc()
                continue

        print(f"\n{'='*50}")
        print(f"🏁 Run complete: {successes}/{len(topics)} videos succeeded")
        print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run_daily())
