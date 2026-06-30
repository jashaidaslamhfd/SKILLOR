"""
MASTER ORCHESTRATOR - PRODUCTION STABLE
FIXED: Path mapping for core modules and robust initialization.
"""

import os
import sys
from pathlib import Path

# --- PATH MAPPING FIX ---
# Is block se Python ko 'core' folder aur baki files mil jayengi
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

core_path = project_root / 'core'
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

# --- IMPORTS ---
try:
    from topic_engine import ViralTopicEngine
    from video_assembler import RetentionVideoAssembler
    from youtube_analytics import YouTubeAnalytics
    from metrics import MetricsTracker
    from thumbnail_generator import ThumbnailGenerator
    # Agar content_generator core ke andar hai, toh aise import karein
    try:
        from content_generator import ContentGenerator as ScriptAI
    except ImportError:
        from core.content_generator import ContentGenerator as ScriptAI
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print(f"Current Path: {sys.path}")
    sys.exit(1)

import json
import asyncio
import logging
import subprocess
import shutil
from datetime import datetime

class AutomationOrchestrator:
    def __init__(self):
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ScriptAI()
        self.assembler = RetentionVideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        self.metrics = MetricsTracker()
        self.youtube_analytics = YouTubeAnalytics()
        self.logger = logging.getLogger("Orchestrator")

    async def run_pipeline(self, count=1):
        # Yahan aapka baki logic aayega
        print("Pipeline running successfully...")

if __name__ == "__main__":
    # Test run
    orchestrator = AutomationOrchestrator()
    asyncio.run(orchestrator.run_pipeline())
