"""
YouTube Automation System — Main Orchestrator
"""

import asyncio
import os
import traceback
import time
from datetime import datetime
from typing import Dict, List

from config.settings import (
    VIDEO_CONFIG, PLATFORM_CONFIG, API_KEYS,
    AUDIO_CONFIG
)
from config.prompts import VIRAL_SCRIPT_GENERATOR
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.audio_generator import AudioGenerator
from core.footage_fetcher import FootageFetcher
from core.video_assembler import VideoAssembler
from core.caption_generator import CaptionGenerator
from core.thumbnail_generator import ThumbnailGenerator
from uploaders.youtube_uploader import YouTubeUploader
from uploaders.facebook_uploader import FacebookUploader
from uploaders.instagram_uploader import InstagramUploader
from core.cloud_uploader import CloudUploader


class YouTubeAutomationSystem:
    def __init__(self):
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.caption_gen = CaptionGenerator()
        self.thumbnail_gen = ThumbnailGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.fb_uploader = FacebookUploader()
        self.ig_uploader = InstagramUploader()
        self.cloud_uploader = CloudUploader()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    async def _validate_duration(self, audio_data: Dict, script_data: Dict, max_attempts: int = 2) -> Dict:
        """FIXED: async method — await generate_with_effects!"""
        duration = audio_data.get('total_duration', 0)
        word_count = audio_data.get('word_count', 0)

        if 40 <= duration <= 55:
            return audio_data

        print(f"    ⚠️ Duration {duration:.1f}s out of range (40-55s) — attempting fix...")

        for attempt in range(max_attempts):
            if duration < 35:
                print(f"    🔧 Fix attempt {attempt+1}: Adding words to script...")
                # Add expansion to story
                for seg in script_data['segments']:
                    if seg.get('type') == 'story':
                        seg['text'] += f" And researchers recently discovered this process is even more complex than previously thought, involving deep neural pathways that scientists are still mapping today."
                        seg['duration'] = round(len(seg['text'].split()) / (AUDIO_CONFIG.WORDS_PER_MINUTE / 60), 2)
                        break

                # Regenerate audio — FIX: await lagaya!
                audio_dir = os.path.join(self.output_dir, "audio")
                audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)
                duration = audio_data.get('total_duration', 0)

            elif duration > 60:
                print(f"    🔧 Fix attempt {attempt+1}: Trimming script...")
                story_segments = [i for i, s in enumerate(script_data['segments']) if s.get('type') == 'story']
                if len(story_segments) > 1:
                    idx = story_segments[-1]
                    removed = script_data['segments'].pop(idx)
                    print(f"    📝 Removed segment: {removed.get('type', 'unknown')}")

                # Regenerate audio — FIX: await lagaya!
                audio_dir = os.path.join(self.output_dir, "audio")
                audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)
                duration = audio_data.get('total_duration', 0)

            if 40 <= duration <= 55:
                print(f"    ✅ Fixed! Duration: {duration:.1f}s")
                return audio_data

        print(f"    ⚠️ Could not fix duration ({duration:.1f}s) — proceeding anyway")
        return audio_data

    def _enrich_segments(self, script_data: Dict, topic_metadata: Dict) -> Dict:
        segments = script_data.get('segments', [])
        suspense_score = topic_metadata.get('suspense_score', 70)

        has_shock = any(s.get('type') == 'shock' for s in segments)

        if not has_shock and suspense_score > 85:
            print(f"    🔥 High suspense score ({suspense_score}) — injecting SHOCK segment...")
            hook_idx = next((i for i, s in enumerate(segments) if s.get('type') == 'hook'), -1)
            if hook_idx >= 0:
                shock_text = topic_metadata.get('shock_angle', 'And what happens next... will terrify you.')
                shock_segment = {
                    'type': 'shock',
                    'text': shock_text,
                    'duration': 3.5,
                    'start': segments[hook_idx].get('end', 6.0),
                    'is_pause': False
                }
                segments.insert(hook_idx + 1, shock_segment)
                self._recalculate_segment_timings(segments)

        pattern = topic_metadata.get('pattern', 'curiosity_gap')
        for seg in segments:
            if seg.get('type') == 'hook' and pattern:
                current_text = seg.get('text', '')
                if 'POV' in pattern and 'POV' not in current_text:
                    seg['text'] = f"POV: {current_text}"
                elif 'Wait for it' in pattern and '...' not in current_text:
                    seg['text'] = f"{current_text}... wait for it."

        script_data['segments'] = segments
        return script_data

    def _recalculate_segment_timings(self, segments: List[Dict]):
        current_time = 0.0
        for seg in segments:
            seg['start'] = current_time
            duration = seg.get('duration', 2.0)
            seg['end'] = current_time + duration
            current_time += duration

    async def create_video(self, topic_data):
        topic_metadata = self.topic_engine.get_topic_metadata(topic_data)
        topic = topic_metadata['topic']
        angle = topic_metadata['angle']
        shock_angle = topic_metadata.get('shock_angle', '')
        pattern = topic_metadata.get('pattern', 'curiosity_gap')
        suspense_score = topic_metadata.get('suspense_score', 70)

        print(f"\n🎬 Creating video for: {topic}")
        print(f"    📊 Viral Pattern: {pattern} | Suspense Score: {suspense_score}/100")

        # Generate Content
        try:
            script_data = self.content_gen.generate_script(
                topic=topic,
                angle=angle,
                shock_angle=shock_angle,
                pattern=pattern,
                suspense_score=suspense_score
            )
        except TypeError as e:
            print(f"    ⚠️ Using legacy generate_script() — {e}")
            script_data = self.content_gen.generate_script(topic, angle)

        # Defensive fallback
        if not isinstance(script_data, dict):
            script_data = {'full_script': str(script_data), 'segments': [], 'word_count': 0, 'duration': 0}
        if not script_data.get('full_script'):
            script_data['full_script'] = f"Discover the shocking truth behind {topic}."
        if 'segments' not in script_data or not script_data['segments']:
            script_data['segments'] = [{'type': 'story', 'text': script_data['full_script'], 'is_pause': False}]

        script_data.setdefault('word_count', len(script_data['full_script'].split()))
        script_data.setdefault('duration', 0)

        # Enrich segments
        script_data = self._enrich_segments(script_data, topic_metadata)

        # Generate title, SEO, thumbnail words
        title = self.content_gen.generate_title(topic)
        seo_data = self.content_gen.generate_seo(topic, script_data['full_script'])
        thumbnail_words = self.content_gen.generate_thumbnail_words(topic)

        print(f"    📝 Script: {script_data['word_count']} words | {len(script_data['segments'])} segments")
        print(f"    📝 Segments: {[s.get('type', 'unknown') for s in script_data['segments']]}")

        # Generate Audio
        print("🎙️ Generating voice...")
        audio_dir = os.path.join(self.output_dir, "audio")
        # FIX: Removed loop.run_in_executor, direct await use karo!
        audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)

        # Validate duration — FIX: await lagaya!
        audio_data = await self._validate_duration(audio_data, script_data)

        actual_duration = audio_data['total_duration']
        print(f"    📊 Audio: {actual_duration:.1f}s | {len(audio_data['word_timings'])} word timings")

        # Fetch Footage
        print("📹 Fetching footage...")
        footage_dir = os.path.join(self.output_dir, "footage")
        footage_clips = self.footage_fetcher.fetch_footage_for_script(script_data['segments'], topic)
        self.footage_fetcher.download_footage(footage_clips, footage_dir)

        # Generate Captions
        print("📝 Generating karaoke captions...")
        ass_path = os.path.join(self.output_dir, f"captions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ass")
        self.caption_gen.generate_karaoke_ass(audio_data['word_timings'], ass_path)
        print(f"    ✅ Captions: {ass_path}")

        # Assemble Video
        print("🎨 Assembling video...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_path = os.path.abspath(os.path.join(self.output_dir, f"video_{timestamp}.mp4"))

        # FIX: Flexible caption parameter — try different names
        try:
            self.video_assembler.create_video(
                script_data['segments'],
                audio_data,
                footage_clips,
                audio_data['word_timings'],
                video_path,
                caption_ass_path=ass_path
            )
        except TypeError:
            try:
                self.video_assembler.create_video(
                    script_data['segments'],
                    audio_data,
                    footage_clips,
                    audio_data['word_timings'],
                    video_path,
                    ass_path=ass_path
                )
            except TypeError:
                try:
                    self.video_assembler.create_video(
                        script_data['segments'],
                        audio_data,
                        footage_clips,
                        audio_data['word_timings'],
                        video_path,
                        caption_path=ass_path
                    )
                except TypeError:
                    # Last resort: pass as positional argument
                    self.video_assembler.create_video(
                        script_data['segments'],
                        audio_data,
                        footage_clips,
                        audio_data['word_timings'],
                        video_path,
                        ass_path
                    )

        # Verify
        if not os.path.exists(video_path):
            raise Exception(f"Video file not created: {video_path}")

        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"✅ Video created: {video_path} ({file_size:.1f} MB)")

        # Copy to latest
        latest_video_path = os.path.join(self.output_dir, "latest_video.mp4")
        import shutil
        shutil.copy2(video_path, latest_video_path)
        print(f"✅ Latest video copy: {latest_video_path}")

        # Generate Thumbnail
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
            'pattern': pattern,
            'suspense_score': suspense_score,
        }

    async def upload_to_platforms(self, video_data):
        results = {}

        if not os.path.exists(video_data['video_path']):
            print(f"❌ Video file missing: {video_data['video_path']}")
            return {'error': 'Video file missing'}

        thumbnail_path = video_data.get('thumbnail_path')
        if thumbnail_path and not os.path.exists(thumbnail_path):
            print(f"⚠️ Thumbnail missing, uploading without it")
            thumbnail_path = None

        yt_ready = bool(API_KEYS.REFRESH_TOKEN and API_KEYS.GOOGLE_CLIENT_ID and API_KEYS.GOOGLE_CLIENT_SECRET)
        fb_ready = bool(API_KEYS.FACEBOOK_ACCESS_TOKEN and API_KEYS.FACEBOOK_PAGE_ID)
        ig_ready = bool(API_KEYS.INSTAGRAM_ACCESS_TOKEN and API_KEYS.INSTAGRAM_USER_ID)

        upload_delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)

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
            print("⏭️  Skipping YouTube — credentials not set")
            results['youtube'] = {'status': 'skipped', 'reason': 'credentials not set'}

        if yt_ready and (fb_ready or ig_ready):
            print(f"⏳ Waiting {upload_delay}s before next platform...")
            await asyncio.sleep(upload_delay)

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
            print("⏭️  Skipping Facebook — credentials not set")
            results['facebook'] = {'status': 'skipped', 'reason': 'credentials not set'}

        if fb_ready and ig_ready:
            print(f"⏳ Waiting {upload_delay}s before Instagram...")
            await asyncio.sleep(upload_delay)

        # Instagram
        if ig_ready:
            print("📸 Uploading to Instagram...")
            try:
                if not self.cloud_uploader.is_configured():
                    print("  ⚠️ Skipping Instagram — Cloudinary not configured")
                    results['instagram'] = {'status': 'skipped', 'reason': 'Cloudinary credentials not set'}
                else:
                    public_url = self.cloud_uploader.upload_video(
                        video_data['video_path'],
                        public_id=f"short_{os.path.splitext(os.path.basename(video_data['video_path']))[0]}",
                    )
                    if not public_url:
                        results['instagram'] = {'error': 'Cloudinary upload failed'}
                    else:
                        ig_result = self.ig_uploader.upload_reel(
                            public_url,
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
            print("⏭️  Skipping Instagram — credentials not set")
            results['instagram'] = {'status': 'skipped', 'reason': 'credentials not set'}

        return results

    async def run_daily(self):
        print(f"\n🚀 Starting automation - {datetime.now()}")
        print(f"🎯 Target: {getattr(PLATFORM_CONFIG, 'DAILY_SHORTS_COUNT', 1)} Short per run")

        topics_data = self.topic_engine.get_daily_topics(count=1)

        if not topics_data:
            print("⚠️ No topics found! Using fallback.")
            topics_data = self.topic_engine._get_fallback_topics()[:1]

        successes = 0
        for i, topic_data in enumerate(topics_data):
            print(f"\n{'='*60}")
            print(f"Video {i+1}/{len(topics_data)}: {topic_data.get('query', 'unknown')}")
            print(f"{'='*60}")

            try:
                video_data = await self.create_video(topic_data)

                print(f"\n📤 Starting uploads...")
                upload_results = await self.upload_to_platforms(video_data)

                print(f"\n✅ Video {i+1} complete!")
                print(f"   📁 File: {video_data['video_path']}")
                print(f"   ⏱️  Duration: {video_data['duration']:.1f}s")
                print(f"   🎯 Pattern: {video_data.get('pattern', 'unknown')}")
                print(f"   🔥 Suspense: {video_data.get('suspense_score', 0)}/100")

                for platform, result in upload_results.items():
                    status = result.get('status', 'unknown')
                    url = result.get('url', 'N/A')
                    if status in ['uploaded', 'published']:
                        print(f"  🟢 {platform.title()}: {url}")
                    elif status == 'skipped':
                        print(f"  ⏭️  {platform.title()}: {result.get('reason', 'skipped')}")
                    else:
                        print(f"  🔴 {platform.title()}: {status} - {result.get('error', 'Unknown')}")

                successes += 1

                if i < len(topics_data) - 1:
                    delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)
                    print(f"\n⏳ Waiting {delay}s before next video...")
                    await asyncio.sleep(delay)

            except Exception as e:
                print(f"❌ Error in video {i+1}: {e}")
                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"🏁 Run complete: {successes}/{len(topics_data)} videos succeeded")
        print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run_daily())
