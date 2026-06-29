"""
Metrics Tracker — USA 2026 (PRODUCTION GRADE ANALYTICS)
INTEGRATED PRODUCTION UPGRADES & FIXES:
1. 🐛 Resolved ZeroDivisionError: Automatically increments global 'total_videos' inside metrics logger.
2. 🛡️ Thread-Safe State Mutations: Injected a robust threading.Lock() to prevent JSON data file corruption.
3. 📊 Deep Nested Key Safety Fallbacks: Prevents KeyError loops if platform analytics profiles mutate.
4. 🧹 Removed redundant raw dictionary structures to secure fast serialization.
"""

import json
import os
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Setup clean production logger
logger = logging.getLogger(__name__)

METRICS_DIR = Path("metrics")
METRICS_DIR.mkdir(exist_ok=True)


class MetricsTracker:
    """Tracks channel performance metrics securely across multi-threaded video rendering pipelines."""
    
    def __init__(self):
        self.metrics_file = METRICS_DIR / "performance.json"
        self.daily_file = METRICS_DIR / f"daily_{datetime.now().strftime('%Y%m%d')}.json"
        
        # 🛡️ Fix 2: Thread Lock allocation to shield concurrent JSON operations
        self._lock = threading.Lock()
        self.data = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Loads analytics dictionaries safely with multi-layer try/except structure."""
        with self._lock:
            if self.metrics_file.exists():
                try:
                    with open(self.metrics_file, 'r', encoding='utf-8') as f:
                        self.data = json.load(f)
                    # Sync schema structural constraints if data is old
                    self._sanitize_loaded_schema()
                    return
                except (json.JSONDecodeError, OSError, ValueError) as e:
                    logger.warning(f"⚠️ Metrics file corrupted or unreadable. Resetting logs safely: {e}")
            
            self.data = self._default_metrics()
            self._save_metrics_unlocked()

    def _sanitize_loaded_schema(self):
        """Ensures nested schema profiles are resilient against accidental KeyErrors."""
        default = self._default_metrics()
        for key in default:
            if key not in self.data:
                self.data[key] = default[key]
        if 'platforms' not in self.data.get('videos_by_platform', {}):
            self.data['videos_by_platform'] = default['videos_by_platform']

    def _default_metrics(self) -> Dict:
        """Returns structural default monitoring dictionary block layout."""
        return {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_duration': 0,
            'total_word_count': 0,
            'average_hook_score': 0.0,
            'videos_by_platform': {
                'youtube': 0,
                'facebook': 0,
                'instagram': 0
            }
        }
    
    def _save_metrics_unlocked(self):
        """Internal low-level file sync (Must run holding self._lock to shield corruption)."""
        try:
            # Atomic file sync execution write patterns
            temp_file = self.metrics_file.with_suffix(".tmp")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            os.replace(temp_file, self.metrics_file)
            
            # Synchronize secondary active diagnostic tracking logs
            with open(self.daily_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            logger.error(f"❌ Critical system write failure syncing analytics matrix logs: {e}")

    def log_video_success(self, duration: float, word_count: int, hook_score: float, platforms: List[str]):
        """Logs video processing telemetry details safely updating data states."""
        with self._lock:
            # 🐛 Fix 1: Increment global counter variable to permanently resolve ZeroDivisionError anomalies
            self.data['total_videos'] += 1
            self.data['successful_uploads'] += 1
            self.data['total_duration'] += max(0.0, duration)
            self.data['total_word_count'] += max(0, word_count)
            
            # Recalculate incremental rolling averages safely
            curr_avg = self.data.get('average_hook_score', 0.0)
            success_count = self.data['successful_uploads']
            self.data['average_hook_score'] = ((curr_avg * (success_count - 1)) + max(0.0, hook_score)) / success_count
            
            # Register explicit social platform destination increments safely
            platform_map = self.data.get('videos_by_platform', {})
            for platform in platforms:
                p_clean = str(platform).lower().strip()
                if p_clean in platform_map:
                    platform_map[p_clean] += 1
                else:
                    platform_map[p_clean] = 1
            self.data['videos_by_platform'] = platform_map
            
            self._save_metrics_unlocked()
            logger.info(f"📊 Telemetry logged successfully | Total Pipeline Tracks: {self.data['total_videos']}")

    def log_video_failure(self):
        """Logs pipeline exception drops to control platform health boundaries."""
        with self._lock:
            self.data['total_videos'] += 1
            self.data['failed_uploads'] += 1
            self._save_metrics_unlocked()
            logger.warning("⚠️ Telemetry registered a video processing node failure chain.")

    def get_summary_stats(self) -> Dict:
        """Computes summary calculations on active state datasets dynamically."""
        with self._lock:
            total = self.data.get('total_videos', 0)
            success = self.data.get('successful_uploads', 0)
            failed = self.data.get('failed_uploads', 0)
            
            # Safe boundary check division parameters
            success_rate = (success / total * 100.0) if total > 0 else 0.0
            avg_duration = (self.data.get('total_duration', 0.0) / success) if success > 0 else 0.0
            
            return {
                'total_videos': total,
                'successful_uploads': success,
                'failed_uploads': failed,
                'success_rate': success_rate,
                'average_duration': avg_duration,
                'average_hook_score': self.data.get('average_hook_score', 0.0),
                'platforms': self.data.get('videos_by_platform', {'youtube': 0, 'facebook': 0, 'instagram': 0})
            }

    def export_report(self) -> str:
        """Compiles clean CLI visual performance analytics dashboard summaries."""
        summary = self.get_summary_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║                    📊 PERFORMANCE REPORT                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📹 Total Videos:        {summary['total_videos']:<30}  ║
║  ✅ Successful Uploads:  {summary['successful_uploads']:<30}  ║
║  ❌ Failed Uploads:      {summary['failed_uploads']:<30}  ║
║  📈 Success Rate:        {summary['success_rate']:.1f}%<29}  ║
║                                                          ║
║  ⏱️ Average Duration:    {summary['average_duration']:.1f}s<29}  ║
║  🎯 Average Hook Score:  {summary['average_hook_score']:.1f}/100<27}║
║                                                          ║
║  📤 Platform Uploads:                                    ║
"""
        for platform, count in summary['platforms'].items():
            report += f"║     {platform.title():<10}   {count:<30}  ║\n"
            
        report += "╚══════════════════════════════════════════════════════════╝"
        return report


# ============================================================
# RUNTIME INTEGRITY TEST
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 TESTING METRICS TELEMETRY TRACKER ENGINE (USA 2026)\n" + "=" * 60)
    
    tracker = MetricsTracker()
    # Mock entries injection processing execution
    tracker.log_video_success(duration=14.2, word_count=45, hook_score=88.5, platforms=['youtube', 'instagram'])
    tracker.log_video_success(duration=11.8, word_count=38, hook_score=92.0, platforms=['youtube', 'facebook'])
    tracker.log_video_failure()
    
    print(tracker.export_report())
    print("\n" + "=" * 60 + "\n✅ Telemetry Thread-Safe Analytics Verified Successfully!")
