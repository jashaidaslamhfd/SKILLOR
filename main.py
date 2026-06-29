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
VERSION: 2.1 (2026 Production Ready - Self-Healing Pipeline)
"""

import os
import sys
import json
import shutil
import asyncio
import argparse
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler # 🥇 Fix 5: Rotating file handler

# FIX H1: Load .env file BEFORE importing config/settings which reads env vars
from dotenv import load_dotenv
load_dotenv()

# 🥇 Fix 6: Fail immediately if FFmpeg is missing at system startup before running deeper components
if not shutil.which("ffmpeg"):
    raise RuntimeError("🚨 CRITICAL DEPENDENCY MISSING: FFmpeg is required for video assembly but could not be located in your system PATH.")

# ============================================================
# SETUP LOGGING (Rotating logs to protect VPS disk space)
# ============================================================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_filename, maxBytes=5_000_000, backupCount=5), # 5 MB per log file, max 5 backups
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
        self._orchestrator = None
        self.start_time = None
        self.end_time = None
        
        # Concurrency limits applied: 🥇 Fix 4
        self.pipeline_semaphore = asyncio.Semaphore(2) 
        
        # Banner
        self._print_banner()
        
    def _print_banner(self):
        """Print system banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎬 YOUTUBE AUTOMATION SYSTEM - PRODUCTION READY v2.1     ║
║                                                              ║
║   🎯 Niche: Brain & Body Science Facts (Universal)        ║
║   📱 Format: YouTube Shorts (1080x1920, 42-55s)            ║
║   🤖 AI: Groq LLM + Self-Correcting Hooks                  ║
║   🎙️ Voice: Groq Orpheus (troy)                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("🚀 System Initialized")

    def get_orchestrator(self) -> AutomationOrchestrator:
        """🥇 Fix 2: Lazy loading Orchestrator Singleton Pattern prevents reconnecting clients twice"""
        if self._orchestrator is None:
            logger.info("📦 Initializing orchestrator...")
            self._orchestrator = AutomationOrchestrator()
        return self._orchestrator

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
        
        missing_apis = [k for k, v in api_status.items() if not v or isinstance(v, str)]
        if missing_apis:
            results['warnings'].append(f"⚠️ Missing APIs: {', '.join(missing_apis)}")
            results['status'] = 'degraded'
        
        # Check FFmpeg
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
        
        # Check orchestrator lazy init
        try:
            _ = self.get_orchestrator()
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
        """Run the automation pipeline with 3-try minimum recovery safety"""
        
        self.start_time = datetime.now()
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 STARTING AUTOMATION")
        logger.info(f"   Time: {self.start_time}")
        logger.info(f"   Videos: {count}")
        logger.info(f"   Upload: {'❌' if skip_upload or upload_only else '✅'}")
        logger.info(f"{'#'*60}\n")
        
        try:
            orchestrator = self.get_orchestrator()
            
            # ============================================================
            # UPLOAD ONLY MODE (Safe Stateful Registry Implementation)
            # ============================================================
            if upload_only:
                logger.info("📤 Upload only mode using state registry...")
                state_file = Path("output/state.json")
                
                if not state_file.exists():
                    logger.error("❌ State file 'output/state.json' missing! Cannot trace previously generated videos.")
                    return {'status': 'error', 'error': 'State file missing'}
                
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                latest_video_path = state_data.get("latest_video")
                latest_thumb_path = state_data.get("latest_thumb")
                
                if not latest_video_path or not Path(latest_video_path).exists():
                    logger.error(f"❌ Target video path '{latest_video_path}' does not exist on disk.")
                    return {'status': 'error', 'error': 'Video path missing from state registry'}
                
                video_data = {
                    'video_path': latest_video_path,
                    'thumbnail_path': latest_thumb_path if latest_thumb_path and Path(latest_thumb_path).exists() else None,
                    'title': state_data.get("title", "Brain Science Short"),
                    'description': state_data.get("description", "Check out this brain science fact! #Shorts #BrainFacts"),
                    'tags': state_data.get("tags", ['#Shorts', '#BrainFacts', '#Memory']),
                }
                
                upload_results = await orchestrator.upload_to_platforms(video_data)
                
                logger.info(f"\n📤 Upload Results:")
                for platform, result in upload_results.items():
                    if isinstance(result, dict):
                        status = result.get('status', 'unknown')
                        url = result.get('url', 'N/A')
                        if status in ['uploaded', 'published']:
                            logger.info(f"   ✅ {platform.title()}: {url}")
                        else:
                            # 🥇 Fix 7: Log exact failure context rather than ignoring it silently
                            logger.error(f"   ❌ {platform.title()}: FAILED -> Status: {status} | Error Details: {result.get('error', 'Unknown error')}")
                
                return {'status': 'complete', 'uploads': upload_results}
            
            # ============================================================
            # FULL PIPELINE (Concurrent semaphore execution with 3-attempt recovery)
            # ============================================================
            logger.info("🎬 Running full pipeline with concurrency limitations...")
            
            async with self.pipeline_semaphore:
                results = None
                max_attempts = 3
                
                for attempt in range(max_attempts):
                    try:
                        logger.info(f"Running pipeline attempt {attempt + 1} of {max_attempts}...")
                        results = await orchestrator.run_pipeline(
                            count=count,
                            specific_topic=specific_topic,
                            skip_upload=skip_upload
                        )
                        break
                    except Exception as e:
                        logger.error(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < max_attempts - 1:
                            logger.info("Waiting 3 seconds before next retry attempt...")
                            await asyncio.sleep(3)
                        else:
                            logger.critical("All retry attempts exhausted for orchestrator pipeline.")
                            raise e

            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.info(f"\n{'#'*60}")
            logger.info(f"🏁 AUTOMATION COMPLETE")
            logger.info(f"   Time: {self.end_time}")
            logger.info(f"   Duration: {duration:.1f}s")
            logger.info(f"   Success: {results.get('successful', 0) if results else 0}")
            logger.info(f"   Failed: {results.get('failed', 0) if results else 0}")
            logger.info(f"{'#'*60}")
            
            return results or {'status': 'error', 'error': 'Pipeline execution yielded empty response'}
            
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
    """Main entry point with cleared up parser logic"""
    
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
    
    # 🥇 Fix 8: Remove conflicting/confusing CLI validation checks
    if args.upload_only and args.skip_upload:
        parser.error("🚨 CONFLICTING FLAGS: Cannot use both '--upload-only' and '--skip-upload' in the same run.")
    
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
