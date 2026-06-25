"""
YouTube Automation System — MASTER ORCHESTRATOR (FIXED)
Complete End-to-End Pipeline with YouTube SEO Optimization
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import traceback
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Imports
from config.settings import API_KEYS, PLATFORM_CONFIG, SEO_CONFIG
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

# Directories
OUTPUT_DIR = Path("output")
AUDIO_DIR = OUTPUT_DIR / "audio"
FOOTAGE_DIR = OUTPUT_DIR / "footage"
VIDEO_DIR = OUTPUT_DIR / "videos"
THUMB_DIR = OUTPUT_DIR / "thumbnails"

for d in [OUTPUT_DIR, AUDIO_DIR, FOOTAGE_DIR, VIDEO_DIR, THUMB_DIR]:
    d.mkdir(exist_ok=True)

LATEST_VIDEO = OUTPUT_DIR / "latest_video.mp4"
LATEST_THUMB = OUTPUT_DIR / "latest_thumb.jpg"


class AutomationOrchestrator:
    """Complete End-to-End Automation Pipeline"""

    def __init__(self):
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

        self.stats = {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'topics_processed': []
        }
        logger.info("✅ System initialized")

    def health_check(self) -> Dict:
        api_status = API_KEYS.validate()
        missing = [k for k, v in api_status.items() if not v]
        return {
            'status': 'ok' if not missing else 'degraded',
            'apis': api_status,
            'missing': missing
        }

    # ============================================================
    # PIPELINE
    # ============================================================

    async def run_pipeline(self, count: int = 1, specific_topic: str = None,
                           skip_upload: bool = False) -> Dict:

        logger.info(f"\n{'#'*60}")
        logger.info(f"
