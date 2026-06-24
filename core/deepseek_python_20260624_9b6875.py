"""
YouTube Automation System — MASTER ORCHESTRATOR
Complete End-to-End Pipeline
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
from config.settings import API_KEYS, PLATFORM_CONFIG
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.cloud_uploader import CloudUploader

from uploaders.youtube_uploader import YouTubeUploader
from uploaders.facebook_uploader import FacebookUploader
from uploaders.instagram_uploader import InstagramUploader

# Directories
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


class AutomationOrchestrator:
    """Complete End-to-End Automation Pipeline"""
    
    def __init__(self):
        logger.info("🚀 Initializing Automation System...")
        
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
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
        """Check all system components"""
        api_status = API_KEYS.validate()
        missing = [k for k, v in api_status.items() if not v]
        
        return {
            'status': 'ok' if not missing else 'degraded',
            'apis': api_status,
            'missing': missing
        }

    async def run_pipeline(self, count: int = 1, specific_topic: str = None,
                           skip_upload: bool = False) -> Dict:
        """Run the complete automation pipeline"""
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING PIPELINE")
        logger.info(f"   Time: {datetime.now()}")
        logger.info(f"   Videos: {count}")
        logger.info(f"{'#'*60}\n")
        
        # Health check
        health = self.health_check()
        if health['status'] == 'error':
            return {'status': 'error', 'errors': health.get('missing', [])}
        
        # Get topics
        if specific_topic:
            topics = [{'query': specific_topic}]
        else:
            topics = self.topic_engine.get_daily_topics(count=count)
        
        if not topics:
            logger.error("❌ No topics available")
            return {'status': 'error', 'error': 'No topics available'}
        
        logger.info(f"📋 Topics: {[t.get('query') for t in topics]}")
        
        results = []
        
        for i, topic_data in enumerate(topics):
            topic = topic_data.get('query', '')
            
            logger.info(f"\n📹 Processing {i+1}/{len(topics)}: {topic}")
            
            # Generate script only (for now - audio/video assembly pending)
            script = self.content_gen.generate_script(topic=topic)
            
            logger.info(f"   ✅ Script generated: {script['word_count']} words")
            logger.info(f"   Hook: {script['hook']}")
            logger.info(f"   Hook Score: {script['hook_score']}/10")
            
            results.append({
                'topic': topic,
                'script': script,
                'status': 'success'
            })
            
            self.stats['total_videos'] += 1
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"🏁 PIPELINE COMPLETE")
        logger.info(f"   Success: {len(results)}")
        logger.info(f"{'#'*60}")
        
        return {'status': 'complete', 'results': results}


async def main():
    parser = argparse.ArgumentParser(description='YouTube Automation Pipeline')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of videos')
    parser.add_argument('--topic', '-t', type=str, help='Specific topic')
    parser.add_argument('--health-check', '-hc', action='store_true', help='Health check')
    
    args = parser.parse_args()
    
    orchestrator = AutomationOrchestrator()
    
    if args.health_check:
        health = orchestrator.health_check()
        print(json.dumps(health, indent=2))
        return
    
    results = await orchestrator.run_pipeline(
        count=args.count,
        specific_topic=args.topic
    )
    
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())