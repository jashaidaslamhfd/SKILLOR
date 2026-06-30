"""
MASTER ORCHESTRATOR - PRODUCTION STABLE
FIXED: Path mapping, module discovery, and stable KPipeline initialization.
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# --- 1. ENVIRONMENT & PATH SETUP ---
load_dotenv()
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

core_path = project_root / 'core'
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

# --- 2. ROBUST MODULE IMPORTING ---
try:
    from topic_engine import ViralTopicEngine
    from video_assembler import RetentionVideoAssembler
    from youtube_analytics import YouTubeAnalytics
    from metrics import MetricsTracker
    from thumbnail_generator import ThumbnailGenerator
    from content_generator import ContentGenerator as ScriptAI
except ImportError as e:
    # Fallback to 'core' prefix if direct import fails
    try:
        from core.topic_engine import ViralTopicEngine
        from core.video_assembler import RetentionVideoAssembler
        from core.youtube_analytics import YouTubeAnalytics
        from core.metrics import MetricsTracker
        from core.thumbnail_generator import ThumbnailGenerator
        from core.content_generator import ContentGenerator as ScriptAI
    except ImportError as final_e:
        print(f"❌ CRITICAL IMPORT ERROR: {final_e}")
        sys.exit(1)

# --- 3. ORCHESTRATOR CLASS ---
class AutomationOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger("Orchestrator")
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ScriptAI(config={"hook_api_key": os.getenv("GROQ_API_KEY")})
        self.assembler = RetentionVideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        self.metrics = MetricsTracker()
        self.youtube_analytics = YouTubeAnalytics()
        self.kokoro_model = None

    def _init_voice_engine(self):
        """Lazy load Kokoro engine safely."""
        if self.kokoro_model is None:
            from kokoro import KPipeline
            self.kokoro_model = KPipeline(lang_code='a')
    async def run_pipeline(self, count: int = 1, specific_topic: str = None, skip_upload: bool = False):
        self._init_voice_engine()
        print(f"🚀 Starting pipeline (Count: {count}, Topic: {specific_topic})...")
        
        # Baki logic wahi rahega...
        for i in range(count):
            # Ab specific_topic variable yahan available hoga
            ...
if __name__ == "__main__":
    orchestrator = AutomationOrchestrator()
    asyncio.run(orchestrator.run_pipeline())
