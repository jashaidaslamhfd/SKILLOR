"""
YouTube Automation System â€” Main Orchestrator
"""

import asyncio
import os
import traceback
import time
from datetime import datetime
from typing import Dict, List

from config.settings import (
    VIDEO_CONFIG, PLATFORM_CONFIG, API_KEYS,
    AUDIO_CONFIG, SEO_CONFIG
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
        """Async method â€” await generate_with_effects!"""
        duration = audio_data.get('total_duration', 0)
        word_count = audio_data.get('word_count', 0)

        if 40 <= duration <= 55:
            return audio_data

        print(f"    âš ï¸ Duration {duration:.1f}s out of range (40-55s) â€” attempting fix...")

        for attempt in range(max_attempts):
            if duration < 35:
                print(f"    ðŸ”§ Fix attempt {attempt+1}: Adding words to script...")
                for seg in script_data['segments']:
                    if seg.get('type') == 'story':
                        seg['text'] += f" And researchers recently discovered this process is even more complex than previously thought, involving deep neural pathways that scientists are still mapping today."
                        seg['duration'] = round(len(seg['text'].split()) / (AUDIO_CONFIG.WORDS_PER_MINUTE / 60), 2)
                        break

                audio_dir = os.path.join(self.output_dir, "audio")
                audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)
                duration = audio_data.get('total_duration', 0)

            elif duration > 60:
                print(f"    ðŸ”§ Fix attempt {attempt+1}: Trimming script...")
                story_segments = [i for i, s in enumerate(script_data['segments']) if s.get('type') == 'story']
                if len(story_segments) > 1:
                    idx = story_segments[-1]
                    removed = script_data['segments'].pop(idx)
                    print(f"    ðŸ“ Removed segment: {removed.get('type', 'unknown')}")

                audio_dir = os.path.join(self.output_dir, "audio")
                audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)
                duration = audio_data.get('total_duration', 0)

            if 40 <= duration <= 55:
                print(f"    âœ… Fixed! Duration: {duration:.1f}s")
                return audio_data

        print(f"    âš ï¸ Could not fix duration ({duration:.1f}s) â€” proceeding anyway")
        return audio_data

    def _enrich_segments(self, script_data: Dict, topic_metadata: Dict) -> Dict:
        """
        FIX: shock-segment injection happens BEFORE audio/word_timings exist
        (always did, in call order â€” audio is generated after this). We now
        also re-derive word_count here so downstream consumers that read
        script_data['word_count'] right after enrichment see the
        post-insertion word count, not the stale pre-insertion one. This
        keeps the segment list and any word-count-derived estimate in sync
        before audio_gen ever slices word_boundaries against it.
        """
        segments = script_data.get('segments', [])
        suspense_score = topic_metadata.get('suspense_score', 70)

        has_shock = any(s.get('type') == 'shock' for s in segments)

        if not has_shock and suspense_score > 85:
            print(f"    ðŸ”¥ High suspense score ({suspense_score}) â€” injecting SHOCK segment...")
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
        # FIX: recompute word_count from the (possibly shock-augmented)
        # segments now, so it reflects what will actually be sent to TTS.
        script_data['word_count'] = sum(
            len(s.get('text', '').split()) for s in segments if not s.get('is_pause')
        )
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

        print(f"\nðŸŽ¬ Creating video for: {topic}")
        print(f"    ðŸ“Š Viral Pattern: {pattern} | Suspense Score: {suspense_score}/100")

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
            print(f"    âš ï¸ Using legacy generate_script() â€” {e}")
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

        # Enrich segments (shock injection happens BEFORE audio generation,
        # so word_timings produced by audio_gen always match this final
        # segment list â€” see _enrich_segments docstring)
        script_data = self._enrich_segments(script_data, topic_metadata)

        # Generate title, SEO, thumbnail words
        title = self.content_gen.generate_title(topic)
        seo_data = self.content_gen.generate_seo(topic, script_data['full_script'])
        thumbnail_words = self.content_gen.generate_thumbnail_words(topic)

        print(f"    ðŸ“ Script: {script_data['word_count']} words | {len(script_data['segments'])} segments")
        print(f"    ðŸ“ Segments: {[s.get('type', 'unknown') for s in script_data['segments']]}")

        # Generate Audio
        print("ðŸŽ™ï¸ Generating voice...")
        audio_dir = os.path.join(self.output_dir, "audio")
        audio_data = await self.audio_gen.generate_with_effects(script_data['segments'], audio_dir)

        # Validate duration
        audio_data = await self._validate_duration(audio_data, script_data)

        actual_duration = audio_data['total_duration']
        print(f"    ðŸ“Š Audio: {actual_duration:.1f}s | {len(audio_data['word_timings'])} word timings")

        # Fetch Footage
        print("ðŸ“¹ Fetching footage...")
        footage_dir = os.path.join(self.output_dir, "footage")
        footage_clips = self.footage_fetcher.fetch_footage_for_script(script_data['segments'], topic)
        # FIX: download_footage now returns a dict keyed by ORIGINAL segment
        # index (not a re-indexed list) â€” this is what the video assembler
        # uses to look up each segment's clip without index drift.
        footage_clip_paths = self.footage_fetcher.download_footage(footage_clips, footage_dir)

        # Generate Captions
        print("ðŸ“ Generating karaoke captions...")
        ass_path = os.path.join(self.output_dir, f"captions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ass")
        self.caption_gen.generate_karaoke_ass(audio_data['word_timings'], ass_path)
        print(f"    âœ… Captions: {ass_path}")

        # Assemble Video
        print("ðŸŽ¨ Assembling video...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_path = os.path.abspath(os.path.join(self.output_dir, f"video_{timestamp}.mp4"))

        # FIX: flexible caption parameter retained for backward compat, but
        # footage_clip_paths (dict) is now always passed â€” the assembler
        # supports both shapes defensively either way.
        try:
            self.video_assembler.create_video(
                script_data['segments'],
                audio_data,
                footage_clip_paths,
                audio_data['word_timings'],
                video_path,
                caption_ass_path=ass_path
            )
        except TypeError:
            try:
                self.video_assembler.create_video(
                    script_data['segments'],
                    audio_data,
                    footage_clip_paths,
                    audio_data['word_timings'],
                    video_path,
                    ass_path=ass_path
                )
            except TypeError:
                try:
                    self.video_assembler.create_video(
                        script_data['segments'],
                        audio_data,
                        footage_clip_paths,
                        audio_data['word_timings'],
                        video_path,
                        caption_path=ass_path
                    )
                except TypeError:
                    self.video_assembler.create_video(
                        script_data['segments'],
                        audio_data,
                        footage_clip_paths,
                        audio_data['word_timings'],
                        video_path,
                        ass_path
                    )

        # Verify
        if not os.path.exists(video_path):
            raise Exception(f"Video file not created: {video_path}")

        file_size = os.path.getsize(video_path) / (1024 * 1024)
        print(f"âœ… Video created: {video_path} ({file_size:.1f} MB)")

        # Copy to latest
        latest_video_path = os.path.join(self.output_dir, "latest_video.mp4")
        import shutil
        shutil.copy2(video_path, latest_video_path)
        print(f"âœ… Latest video copy: {latest_video_path}")

        # Generate Thumbnail
        print("ðŸ–¼ï¸ Generating thumbnail...")
        thumbnail_path = os.path.join(self.output_dir, f"thumb_{timestamp}.jpg")
        self.thumbnail_gen.generate_thumbnail(thumbnail_words, topic, thumbnail_path)

        if not os.path.exists(thumbnail_path):
            print(f"âš ï¸ Thumbnail not created, continuing without it")
            thumbnail_path = None
        else:
            print(f"âœ… Thumbnail created: {thumbnail_path}")

        # FIX: re-probe the actual rendered file's real duration instead of
        # trusting audio_data['total_duration'] alone for the returned
        # 'duration' field â€” this is what the quality gate checks against,
        # so it must reflect what's really on disk after the assembler's
        # hard `-t` cap, not the pre-render audio estimate.
        real_duration = self._probe_duration(video_path)
        final_duration = real_duration if real_duration > 0 else actual_duration

        return {
            'video_path': video_path,
            'latest_video_path': latest_video_path,
            'thumbnail_path': thumbnail_path,
            'title': title,
            'description': seo_data['description'],
            'tags': seo_data['tags'],
            'topic': topic,
            'duration': final_duration,
            'pattern': pattern,
            'suspense_score': suspense_score,
        }

    def _probe_duration(self, path: str) -> float:
        try:
            import subprocess
            r = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return float(r.stdout.strip())
        except Exception:
            pass
        return 0.0

    async def upload_to_platforms(self, video_data):
        results = {}

        if not os.path.exists(video_data['video_path']):
            print(f"âŒ Video file missing: {video_data['video_path']}")
            return {'youtube': {'status': 'skipped', 'reason': 'video file missing'},
                    'facebook': {'status': 'skipped', 'reason': 'video file missing'},
                    'instagram': {'status': 'skipped', 'reason': 'video file missing'}}

        duration = video_data.get('duration', 0)
        file_size_mb = os.path.getsize(video_data['video_path']) / (1024 * 1024)
        dur_min = getattr(VIDEO_CONFIG, 'DURATION_MIN', 40)
        dur_max = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)
        hard_min = dur_min - 10
        hard_max = dur_max + 25

        if duration <= 0 or not (hard_min <= duration <= hard_max) or file_size_mb < 1:
            print(f"  âŒ QUALITY GATE FAILED â€” duration {duration:.1f}s "
                  f"(expected {dur_min}-{dur_max}s, hard limit {hard_min}-{hard_max}s) "
                  f"| size {file_size_mb:.1f}MB")
            print(f"  â­ï¸  Skipping ALL uploads â€” video kept locally for review: {video_data['video_path']}")
            # FIX: this used to return a flat {'error': ..., 'status': ...}
            # dict whose top-level values are strings. run_daily() then did
            # `for platform, result in upload_results.items(): result.get(...)`
            # and crashed with 'str' object has no attribute 'get' because
            # `result` here was a plain string. We now always return a dict
            # of per-platform dicts (the shape run_daily() actually expects),
            # even in the blocked case, so the loop never sees a bare string.
            blocked_reason = f'blocked_quality_gate: duration={duration:.1f}s size={file_size_mb:.1f}MB'
            return {
                'youtube': {'status': 'blocked_quality_gate', 'reason': blocked_reason},
                'facebook': {'status': 'blocked_quality_gate', 'reason': blocked_reason},
                'instagram': {'status': 'blocked_quality_gate', 'reason': blocked_reason},
            }

        thumbnail_path = video_data.get('thumbnail_path')
        if thumbnail_path and not os.path.exists(thumbnail_path):
            print(f"âš ï¸ Thumbnail missing, uploading without it")
            thumbnail_path = None

        yt_ready = bool(API_KEYS.REFRESH_TOKEN and API_KEYS.GOOGLE_CLIENT_ID and API_KEYS.GOOGLE_CLIENT_SECRET)
        fb_ready = bool(API_KEYS.FACEBOOK_ACCESS_TOKEN and API_KEYS.FACEBOOK_PAGE_ID)
        ig_ready = bool(API_KEYS.INSTAGRAM_ACCESS_TOKEN and API_KEYS.INSTAGRAM_USER_ID)

        upload_delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)

        # YouTube
        if yt_ready:
            print("ðŸ“º Uploading to YouTube...")
            try:
                yt_result = self.youtube_uploader.upload_video(
                    video_data['video_path'],
                    thumbnail_path,
                    video_data['title'],
                    video_data['description'],
                    video_data['tags'],
                    privacy_status=getattr(SEO_CONFIG, 'PRIVACY_STATUS', 'public')
                )
                results['youtube'] = yt_result
                print(f"  âœ… YouTube: {yt_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  âŒ YouTube failed: {e}")
                results['youtube'] = {'status': 'error', 'error': str(e)}
        else:
            print("â­ï¸  Skipping YouTube â€” credentials not set")
            results['youtube'] = {'status': 'skipped', 'reason': 'credentials not set'}

        if yt_ready and (fb_ready or ig_ready):
            print(f"â³ Waiting {upload_delay}s before next platform...")
            await asyncio.sleep(upload_delay)

        # Facebook
        if fb_ready:
            print("ðŸ“˜ Uploading to Facebook...")
            try:
                fb_result = self.fb_uploader.upload_video(
                    video_data['video_path'],
                    thumbnail_path,
                    video_data['title'],
                    video_data['description']
                )
                results['facebook'] = fb_result
                print(f"  âœ… Facebook: {fb_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  âŒ Facebook failed: {e}")
                results['facebook'] = {'status': 'error', 'error': str(e)}
        else:
            print("â­ï¸  Skipping Facebook â€” credentials not set")
            results['facebook'] = {'status': 'skipped', 'reason': 'credentials not set'}

        if fb_ready and ig_ready:
            print(f"â³ Waiting {upload_delay}s before Instagram...")
            await asyncio.sleep(upload_delay)

        # Instagram
        if ig_ready:
            print("ðŸ“¸ Uploading to Instagram...")
            try:
                if not self.cloud_uploader.is_configured():
                    print("  âš ï¸ Skipping Instagram â€” Cloudinary not configured")
                    results['instagram'] = {'status': 'skipped', 'reason': 'Cloudinary credentials not set'}
                else:
                    public_url = self.cloud_uploader.upload_video(
                        video_data['video_path'],
                        public_id=f"short_{os.path.splitext(os.path.basename(video_data['video_path']))[0]}",
                    )
                    if not public_url:
                        results['instagram'] = {'status': 'error', 'error': 'Cloudinary upload failed'}
                    else:
                        ig_result = self.ig_uploader.upload_reel(
                            public_url,
                            thumbnail_path,
                            video_data['description'],
                            video_data['tags']
                        )
                        results['instagram'] = ig_result
                        print(f"  âœ… Instagram: {ig_result.get('url', 'N/A')}")
            except Exception as e:
                print(f"  âŒ Instagram failed: {e}")
                results['instagram'] = {'status': 'error', 'error': str(e)}
        else:
            print("â­ï¸  Skipping Instagram â€” credentials not set")
            results['instagram'] = {'status': 'skipped', 'reason': 'credentials not set'}

        return results

    async def run_daily(self):
        print(f"\nðŸš€ Starting automation - {datetime.now()}")
        print(f"ðŸŽ¯ Target: {getattr(PLATFORM_CONFIG, 'DAILY_SHORTS_COUNT', 1)} Short per run")

        topics_data = self.topic_engine.get_daily_topics(count=1)

        if not topics_data:
            print("âš ï¸ No topics found! Using fallback.")
            topics_data = self.topic_engine._get_fallback_topics()[:1]

        successes = 0
        for i, topic_data in enumerate(topics_data):
            print(f"\n{'='*60}")
            print(f"Video {i+1}/{len(topics_data)}: {topic_data.get('query', 'unknown')}")
            print(f"{'='*60}")

            try:
                video_data = await self.create_video(topic_data)

                print(f"\nðŸ“¤ Starting uploads...")
                upload_results = await self.upload_to_platforms(video_data)

                print(f"\nâœ… Video {i+1} complete!")
                print(f"   ðŸ“ File: {video_data['video_path']}")
                print(f"   â±ï¸  Duration: {video_data['duration']:.1f}s")
                print(f"   ðŸŽ¯ Pattern: {video_data.get('pattern', 'unknown')}")
                print(f"   ðŸ”¥ Suspense: {video_data.get('suspense_score', 0)}/100")

                # FIX: upload_to_platforms() now always returns a dict of
                # per-platform dicts (see fix above), so this loop can
                # safely call .get() on every value without type-checking
                # first. Kept a defensive isinstance check anyway in case
                # any uploader ever returns something unexpected.
                for platform, result in upload_results.items():
                    if not isinstance(result, dict):
                        print(f"  âš ï¸  {platform.title()}: unexpected result type ({type(result).__name__}): {result}")
                        continue
                    status = result.get('status', 'unknown')
                    url = result.get('url', 'N/A')
                    if status in ['uploaded', 'published']:
                        print(f"  ðŸŸ¢ {platform.title()}: {url}")
                    elif status == 'skipped':
                        print(f"  â­ï¸  {platform.title()}: {result.get('reason', 'skipped')}")
                    elif status == 'blocked_quality_gate':
                        print(f"  ðŸš« {platform.title()}: blocked by quality gate â€” {result.get('reason', '')}")
                    else:
                        print(f"  ðŸ”´ {platform.title()}: {status} - {result.get('error', 'Unknown')}")

                successes += 1

                if i < len(topics_data) - 1:
                    delay = getattr(PLATFORM_CONFIG, 'UPLOAD_DELAY_SECONDS', 120)
                    print(f"\nâ³ Waiting {delay}s before next video...")
                    await asyncio.sleep(delay)

            except Exception as e:
                print(f"âŒ Error in video {i+1}: {e}")
                traceback.print_exc()
                continue

        print(f"\n{'='*60}")
        print(f"ðŸ Run complete: {successes}/{len(topics_data)} videos succeeded")
        print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run_daily())
