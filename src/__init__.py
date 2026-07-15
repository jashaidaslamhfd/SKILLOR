"""
SKILLOR — Pakistan's AI-Powered IT Hub
=======================================

Automated YouTube Shorts / Facebook Reels pipeline that generates
dark-mystery body-science videos end-to-end:
  Script → Images → Voice → Video → SEO → Upload

Public API
----------
Main pipeline entry point::

    from src.main import SKILLORPipeline
    pipeline = SKILLORPipeline()
    pipeline.run_pipeline(topic="Why Your Brain Lies to You")

Individual modules (for testing / advanced use)::

    from src.script_generator import generate_script
    from src.image_providers import available_providers
    from src.voice_generator import generate_voice_segments
    from src.video_editor import build_video
    from src.uploader import upload_all
    from src.niche_strategy import get_random_topic
    from src.quality_checker import QualityChecker
    from src.scheduler import USAPeakTimeScheduler
    from src.anti_spam import AntiSpamSystem
    from src.seo_generator import generate_seo_package
    from src.seo_analytics import predict_ctr, score_thumbnail
    from src.shorts_enhancer import build_shorts_report, generate_srt
    from src.media_validator import validate_scene_image, probe_video
"""

__version__ = "1.0.0"
__author__ = "jashaidaslamhfd"

# ---------------------------------------------------------------------------
# Lazy public API — importing `src` alone does NOT pull in heavy deps
# (torch, moviepy, groq, etc.). Consumers can still do `from src.X import Y`
# directly for granular access; these convenience re-exports are optional.
# ---------------------------------------------------------------------------

__all__ = [
    # Pipeline
    "SKILLORPipeline",
    # Script
    "generate_script",
    # Image
    "available_providers",
    "RateLimitError",
    # Voice
    "generate_voice_segments",
    "generate_voice",
    # Video
    "build_video",
    "generate_thumbnail",
    # Upload
    "upload_all",
    # Niche / SEO
    "get_random_topic",
    "get_topic_category",
    "generate_seo_tags",
    "generate_seo_package",
    # Quality / Spam
    "QualityChecker",
    "USAPeakTimeScheduler",
    "AntiSpamSystem",
    # Analytics
    "predict_ctr",
    "score_thumbnail",
    # Shorts
    "build_shorts_report",
    "generate_srt",
    # Validation
    "validate_scene_image",
    "probe_video",
]

