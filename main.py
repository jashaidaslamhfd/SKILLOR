"""
YouTube Automation System - MAIN ENTRY POINT
Complete End-to-End Automation Pipeline

USAGE:
    python main.py                      # Generate and upload 1 video
    python main.py --count 3            # Generate 3 videos
    python main.py --topic "forgetting names"  # Specific topic
    python main.py --skip-upload        # Generate only (no upload)
    python main.py --upload-only        # Upload only existing video
    python main.py --health-check       # Check system health

AUTHOR: YouTube Automation System
VERSION: 2.0 (2026 Production Ready)
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ============================================================
# SETUP LOGGING
# ============================================================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
from config.settings import API_KEYS, PLATFORM_CONFIG, VIDEO_CONFIG, SEO_CONFIG
from orchestrator import AutomationOrchestrator


# ============================================================
# MAIN CLASS
# ============================================================
class YouTubeAutomation:
    """Main Entry Point for YouTube Automation System"""
    
    def __init__(self):
        self.orchestrator = None
        self.start_time = None
        self.end_time = None
        
        # Banner
        self._print_banner()
        
    def _print_banner(self):
        """Print system banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎬 YOUTUBE AUTOMATION SYSTEM - PRODUCTION READY v2.0     ║
║                                                              ║
║   🎯 Niche: Memory & Brain Fog Science for Men 35-54       ║
║   📱 Format: YouTube Shorts (1080x1920, 42-55s)            ║
║   🤖 AI: Groq LLM + Self-Correcting Hooks                  ║
║   🎙️ Voice: en-US-GuyNeural (Deep, Mature)                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("🚀 System Initialized")

    # ============================================================
    # HEALTH CHECK
    # ============================================================
    
    def health_check(self) -> Dict:
        """Check system health"""
        logger.info("🔍 Running health check...")
        
        results = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        # Check API Keys
        api_status = API_KEYS.validate()
        results['checks']['apis'] = api_status
        
        missing_apis = [k for k, v in api_status.items() if not v]
        if missing_apis:
            results['warnings'].append(f"⚠️ Missing APIs: {', '.join(missing_apis)}")
            results['status'] = 'degraded'
        
        # Check FFmpeg
        import shutil
        has_ffmpeg = shutil.which('ffmpeg') is not None
        results['checks']['ffmpeg'] = has_ffmpeg
        if not has_ffmpeg:
            results['errors'].append("❌ FFmpeg not found - REQUIRED for video assembly")
            results['status'] = 'error'
        
        # Check directories
        dirs = {
            'output': Path("output").exists(),
            'logs': LOG_DIR.exists(),
        }
        results['checks']['directories'] = dirs
        
        # Check orchestrator
        try:
            if self.orchestrator is None:
                self.orchestrator = AutomationOrchestrator()
            results['checks']['orchestrator'] = True
        except Exception as e:
            results['checks']['orchestrator'] = False
            results['errors'].append(f"❌ Orchestrator init failed: {e}")
            results['status'] = 'error'
        
        # Summary
        logger.info(f"📊 Health Check Status: {results['status'].upper()}")
        if results['warnings']:
            for w in results['warnings']:
                logger.warning(w)
        if results['errors']:
            for e in results['errors']:
                logger.error(e)
        
        return results

    # ============================================================
    # RUN
    # ============================================================
    
    async def run(self, count: int = 1, specific_topic: str = None,
                  skip_upload: bool = False, upload_only: bool = False):
        """Run the automation pipeline"""
        
        self.start_time = datetime.now()
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING AUTOMATION")
        logger.info(f"   Time: {self.start_time}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {'❌' if skip_upload or upload_only else '✅'}")
        logger.info(f"{'#'*60}\n")
        
        try:
            # Initialize orchestrator
            logger.info("📦 Initializing orchestrator...")
            self.orchestrator = AutomationOrchestrator()
            
            # ============================================================
            # UPLOAD ONLY MODE
            # ============================================================
            if upload_only:
                logger.info("📤 Upload only mode...")
                latest_video = Path("output/latest_video.mp4")
                latest_thumb = Path("output/latest_thumb.jpg")
                
                if not latest_video.exists():
                    logger.error("❌ No latest video found in output directory")
                    return {'status': 'error', 'error': 'No video found'}
                
                video_data = {
                    'video_path': str(latest_video),
                    'thumbnail_path': str(latest_thumb) if latest_thumb.exists() else None,
                    'title': "Brain Science Short",
                    'description': "Check out this brain science fact! #Shorts #BrainFacts",
                    'tags': ['#Shorts', '#BrainFacts', '#Memory'],
                }
                
                upload_results = await self.orchestrator.upload_to_platforms(video_data)
                
                logger.info(f"\n📤 Upload Results:")
                for platform, result in upload_results.items():
                    if isinstance(result, dict):
                        status = result.get('status', 'unknown')
                        url = result.get('url', 'N/A')
                        if status in ['uploaded', 'published']:
                            logger.info(f"   ✅ {platform.title()}: {url}")
                        else:
                            logger.info(f"   ⚪ {platform.title()}: {status}")
                
                return {'status': 'complete', 'uploads': upload_results}
            
            # ============================================================
            # FULL PIPELINE
            # ============================================================
            logger.info("🎬 Running full pipeline...")
            results = await self.orchestrator.run_pipeline(
                count=count,
                specific_topic=specific_topic,
                upload=True,
                skip_upload=skip_upload
            )
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"\n{'#'*60}")
            logger.info(f"🏁 AUTOMATION COMPLETE")
            logger.info(f"   Time: {self.end_time}")
            logger.info(f"   Duration: {duration:.1f}s")
            logger.info(f"   Success: {results.get('successful', 0)}")
            logger.info(f"   Failed: {results.get('failed', 0)}")
            logger.info(f"{'#'*60}")
            
            return results
            
        except KeyboardInterrupt:
            logger.warning("\n⏹️ Interrupted by user")
            return {'status': 'interrupted'}
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            logger.error(traceback.format_exc())
            return {'status': 'error', 'error': str(e)}

    # ============================================================
    # SUMMARY
    # ============================================================
    
    def print_summary(self, results: Dict):
        """Print summary of results"""
        if not results:
            return
        
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        status = results.get('status', 'unknown')
        if status == 'complete':
            print(f"✅ Status: COMPLETE")
            print(f"   Successful: {results.get('successful', 0)}")
            print(f"   Failed: {results.get('failed', 0)}")
        elif status == 'error':
            print(f"❌ Status: ERROR")
            print(f"   Error: {results.get('error', 'Unknown')}")
        elif status == 'interrupted':
            print(f"⏹️ Status: INTERRUPTED")
        else:
            print(f"⚠️ Status: {status}")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"   Duration: {duration:.1f}s")
        
        print("="*60)


# ============================================================
# MAIN ENTRY POINT
# ============================================================
async def main():
    """Main entry point with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description='YouTube Automation System - Complete Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python main.py                       # Generate and upload 1 video
  python main.py --count 3             # Generate 3 videos
  python main.py --topic "forgetting names"  # Specific topic
  python main.py --skip-upload         # Generate only (no upload)
  python main.py --upload-only         # Upload only existing video
  python main.py --health-check        # Check system health
        """
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
        '--skip-upload', '-s',
        action='store_true',
        help='Create video but skip uploading to platforms'
    )
    
    parser.add_argument(
        '--upload-only', '-u',
        action='store_true',
        help='Only upload existing latest video (skip creation)'
    )
    
    parser.add_argument(
        '--health-check', '-hc',
        action='store_true',
        help='Run health check and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize automation
    automation = YouTubeAutomation()
    
    # Health check
    if args.health_check:
        health = automation.health_check()
        print("\n📊 HEALTH CHECK RESULTS:")
        print(json.dumps(health, indent=2, default=str))
        return
    
    # Upload only
    if args.upload_only:
        if not args.skip_upload:
            args.skip_upload = False  # upload-only implies upload
        results = await automation.run(
            upload_only=True
        )
        automation.print_summary(results)
        return
    
    # Run pipeline
    results = await automation.run(
        count=args.count,
        specific_topic=args.topic,
        skip_upload=args.skip_upload
    )
    
    automation.print_summary(results)
    
    # Return appropriate exit code
    if results.get('status') == 'error':
        sys.exit(1)
    else:
        sys.exit(0)


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
