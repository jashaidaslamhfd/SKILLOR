"""
YouTube Automation System — MAIN ENTRY POINT (PRODUCTION ROUTER 2026)
INTEGRATED PATH & SUB-MODULE ENGINE FIX:
- Solves 'ModuleNotFoundError: No module named core.topic_engine' permanently.
"""

import os
import sys
import shutil
import asyncio
import argparse
import json
from pathlib import Path

# 🚀 THE CRITICAL FIX: Absolute Multi-Layer Path Resolution
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent

# Inject the folder containing main.py as primary lookup index
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Forcefully find and append the parent folder of 'core' and 'config' to avoid import breaks
for folder_candidate in project_root.rglob('core'):
    if folder_candidate.is_dir():
        parent_dir = str(folder_candidate.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        break

# Load env configurations BEFORE any internal core engines boot up
from dotenv import load_dotenv
load_dotenv()

# Enforce system level core binary checks at entry point
if not shutil.which("ffmpeg"):
    raise RuntimeError("🚨 CRITICAL DEPENDENCY MISSING: FFmpeg is required for the video automation stack.")

# Import the native orchestrator class exactly as architected
try:
    from orchestrator import AutomationOrchestrator
except ImportError as e:
    print(f"❌ Core engine import map resolution failure: {e}")
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="🚀 ENTERPRISE SHORTS AUTOMATION FRAMEWORK MASTER CONSOLE (USA 2026)")
    parser.add_argument("--count", type=int, default=1, help="Total videos to batch produce.")
    parser.add_argument("--topic", type=str, default=None, help="Force override engine to target explicit topic query string.")
    parser.add_argument("--skip-upload", action="store_true", help="Generate only without publishing.")
    parser.add_argument("--health-check", action="store_true", help="Check system parameters configuration and exit.")
    
    args = parser.parse_args()
    
    # Initialize the actual master orchestrator suite
    orchestrator = AutomationOrchestrator()
    
    if args.health_check:
        print("\n📊 RUNNING HEALTH CHECK VERIFICATION...")
        if hasattr(orchestrator, 'health_check'):
            print(json.dumps(orchestrator.health_check(), indent=4, default=str))
        else:
            print("✅ System Core Binaries found in PATH. Ready for action.")
        return

    print(f"⚙️ Dispatching execution loops to AutomationOrchestrator.run_pipeline... Count: [{args.count}]")
    
    # Calling the exact function name and signature present inside your orchestrator.py
    results = await orchestrator.run_pipeline(
        count=args.count,
        specific_topic=args.topic,
        skip_upload=args.skip_upload
    )
    
    print("\n📊 PIPELINE RUN RESULTS SUMMARY:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Manual execution sequence halted via core interrupt breakout keys.")
        sys.exit(0)
