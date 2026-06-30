"""
MASTER ORCHESTRATOR - PRODUCTION STABLE
ROOT-CAUSE FIX: the previous version of this file had its run_pipeline()
body replaced with a bare `...` placeholder. That meant calling main.py
never actually generated anything - no script, no audio, no footage, no
assembled video, no upload. This restores the real end-to-end wiring
between every module in core/ and uploaders/.
"""

import os
import sys
import asyncio
import logging
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

core_path = project_root / 'core'
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Orchestrator")

try:
    from topic_engine import ViralTopicEngine
    from video_assembler import RetentionVideoAssembler
    from youtube_analytics import YouTubeAnalytics
    from metrics import MetricsTracker
    from thumbnail_generator import ThumbnailGenerator
    from content_generator import ContentGenerator as ScriptAI
    from audio_generator import AudioGenerator
    from caption_generator import CaptionGenerator
    from footage_fetcher import FootageFetcher
    from cloud_uploader import CloudUploader
except ImportError:
    from core.topic_engine import ViralTopicEngine
    from core.video_assembler import RetentionVideoAssembler
    from core.youtube_analytics import YouTubeAnalytics
    from core.metrics import MetricsTracker
    from core.thumbnail_generator import ThumbnailGenerator
    from core.content_generator import ContentGenerator as ScriptAI
    from core.audio_generator import AudioGenerator
    from core.caption_generator import CaptionGenerator
    from core.footage_fetcher import FootageFetcher
    from core.cloud_uploader import CloudUploader

try:
    from config.settings import SEO_CONFIG, PLATFORM_CONFIG
except ImportError:
    SEO_CONFIG = PLATFORM_CONFIG = None


class AutomationOrchestrator:
    def __init__(self):
        self.logger = logger
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ScriptAI(config={"hook_api_key": os.getenv("GROQ_API_KEY")})
        self.audio_gen = AudioGenerator()
        self.caption_gen = CaptionGenerator()
        self.footage_fetcher = FootageFetcher()
        self.assembler = RetentionVideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        self.cloud_uploader = CloudUploader()
        self.metrics = MetricsTracker()
        try:
            self.youtube_analytics = YouTubeAnalytics()
        except Exception as e:
            self.logger.warning(f"YouTubeAnalytics unavailable: {e}")
            self.youtube_analytics = None

    def health_check(self) -> dict:
        from config.settings import API_KEYS
        return API_KEYS.validate()

    def _extract_thumbnail_frame(self, video_path: str, out_dir: str) -> str:
        import subprocess
        frame_path = os.path.join(out_dir, "thumb_frame.jpg")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", video_path, "-ss", "00:00:01.000",
                 "-vframes", "1", frame_path],
                capture_output=True, timeout=20
            )
        except Exception as e:
            self.logger.warning(f"Thumbnail frame extraction failed: {e}")
        return frame_path

    def _build_hashtags(self, topic: str) -> list:
        base = list(SEO_CONFIG.DEFAULT_HASHTAGS) if SEO_CONFIG else ["#Shorts", "#Parenting"]
        topic_tag = "#" + "".join(w.capitalize() for w in topic.split()[:3])
        tags = base + [topic_tag]
        seen = set()
        out = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                out.append(t)
        max_tags = SEO_CONFIG.MAX_HASHTAGS if SEO_CONFIG else 6
        return out[:max_tags]

    async def run_single_video(self, specific_topic: str, skip_upload: bool, run_dir: str) -> dict:
        os.makedirs(run_dir, exist_ok=True)

        if specific_topic:
            topic_packet = {"raw_topic": specific_topic}
        else:
            trends = self.topic_engine.fetch_live_trends()
            topic_packet = self.topic_engine.extract_perfect_topic(trends)
        topic = topic_packet["raw_topic"]
        self.logger.info(f"Topic locked: {topic}")

        script_segments = self.content_gen.generate_script(topic)
        title = self.content_gen.generate_title(topic)

        audio_result = await self.audio_gen.generate_with_effects(
            script_segments, output_dir=run_dir, topic=topic
        )
        audio_path = audio_result["audio_path"]
        word_timings = audio_result["word_timings"]
        total_duration = audio_result["total_duration"]
        segment_timeline = audio_result["segment_timeline"]

        ass_path = os.path.join(run_dir, "captions.ass")
        self.caption_gen.generate_karaoke_ass(word_timings, ass_path, max_duration=total_duration)

        clips_by_segment = self.footage_fetcher.fetch_footage_for_script(script_segments, topic)
        clips_dir = os.path.join(run_dir, "clips")
        downloaded_by_segment = self.footage_fetcher.download_footage(clips_by_segment, clips_dir)
        if not downloaded_by_segment:
            raise RuntimeError("No footage could be downloaded for this script - aborting render.")

        output_path = os.path.join(run_dir, "final_short.mp4")
        self.assembler.assemble_final_video(
            segment_clips=downloaded_by_segment,
            audio_path=audio_path,
            ass_path=ass_path if os.path.exists(ass_path) else None,
            output_path=output_path,
            segment_timeline=segment_timeline,
        )

        frame_path = self._extract_thumbnail_frame(output_path, run_dir)
        thumb_words = topic.split()[:3] or ["WATCH", "THIS"]
        thumb_path = os.path.join(run_dir, "thumbnail.jpg")
        self.thumbnail_gen.generate_youtube_thumbnail(frame_path, thumb_words, topic, thumb_path)

        result = {
            "topic": topic,
            "title": title,
            "video_path": output_path,
            "thumbnail_path": thumb_path,
            "duration": total_duration,
            "word_count": audio_result.get("word_count", 0),
            "platforms": {},
        }

        if skip_upload:
            self.logger.info("skip_upload set - generation complete, not publishing.")
            self.metrics.log_video_success(total_duration, result["word_count"], 0.0, [])
            return result

        hashtags = self._build_hashtags(topic)
        description = f"{topic}\n\n" + " ".join(hashtags)
        platforms_done = []

        if PLATFORM_CONFIG is None or PLATFORM_CONFIG.YOUTUBE_ENABLED:
            try:
                from uploaders.youtube_uploader import YouTubeUploader
                yt = YouTubeUploader()
                yt_res = yt.upload_video(
                    video_path=output_path, thumbnail_path=thumb_path,
                    title=title, description=description, tags=[h.lstrip('#') for h in hashtags],
                )
                result["platforms"]["youtube"] = yt_res
                platforms_done.append("youtube")
            except Exception as e:
                self.logger.error(f"YouTube upload failed: {e}\n{traceback.format_exc()}")

        if PLATFORM_CONFIG is None or PLATFORM_CONFIG.FACEBOOK_ENABLED:
            try:
                from uploaders.facebook_uploader import FacebookUploader
                fb = FacebookUploader()
                fb_res = fb.upload_video(
                    video_path=output_path, thumbnail_path=thumb_path,
                    title=title, description=description,
                )
                result["platforms"]["facebook"] = fb_res
                platforms_done.append("facebook")
            except Exception as e:
                self.logger.error(f"Facebook upload failed: {e}\n{traceback.format_exc()}")

        if PLATFORM_CONFIG is None or PLATFORM_CONFIG.INSTAGRAM_ENABLED:
            try:
                from uploaders.instagram_uploader import InstagramUploader
                public_url = self.cloud_uploader.upload_video(output_path)
                if public_url:
                    ig = InstagramUploader()
                    ig_res = ig.upload_reel(video_url=public_url, caption=description)
                    result["platforms"]["instagram"] = ig_res
                    platforms_done.append("instagram")
                else:
                    self.logger.warning("Skipping Instagram - Cloudinary not configured / upload failed (Instagram needs a public URL).")
            except Exception as e:
                self.logger.error(f"Instagram upload failed: {e}\n{traceback.format_exc()}")

        self.metrics.log_video_success(total_duration, result["word_count"], 0.0, platforms_done)
        return result

    async def run_pipeline(self, count: int = 1, specific_topic: str = None, skip_upload: bool = False):
        results = []
        base_dir = Path("output_runs")
        for i in range(count):
            run_dir = str(base_dir / datetime.now().strftime(f"run_{i}_%Y%m%d_%H%M%S"))
            self.logger.info(f"Producing video {i + 1}/{count} -> {run_dir}")
            try:
                res = await self.run_single_video(specific_topic, skip_upload, run_dir)
                res["status"] = "success"
                results.append(res)
            except Exception as e:
                self.logger.error(f"Pipeline run {i + 1} failed: {e}\n{traceback.format_exc()}")
                self.metrics.log_video_failure()
                results.append({"status": "failed", "error": str(e)})
        return results


if __name__ == "__main__":
    orchestrator = AutomationOrchestrator()
    asyncio.run(orchestrator.run_pipeline())
