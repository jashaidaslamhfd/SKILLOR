"""
METRICS TRACKER - PRODUCTION STABLE
FIXED: Removed invalid f-string syntax and implemented robust JSON logging.
"""

import logging
import json
from pathlib import Path

class MetricsTracker:
    def __init__(self):
        # Metrics file save location
        self.log_file = Path("metrics.json")
        self.logger = logging.getLogger("MetricsTracker")

    def log_video_success(self, duration: float, word_count: int, hook_score: float, platforms: list):
        """Logs successful run data using robust JSON serialization."""
        data = {
            "timestamp": "2026-06-30",
            "duration": duration,
            "word_count": word_count,
            "hook_score": hook_score,
            "platforms": platforms,
            "status": "success"
        }
        try:
            # Append data to metrics.json in a clean format
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            self.logger.info("Metrics successfully recorded for successful pipeline run.")
        except Exception as e:
            self.logger.error(f"Failed to write metrics: {str(e)}")

    def log_video_failure(self):
        """Logs failures without syntax-breaking string literals."""
        try:
            data = {"timestamp": "2026-06-30", "status": "failed"}
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            self.logger.info("Failure logged to metrics registry.")
        except Exception as e:
            self.logger.error(f"Could not log failure: {str(e)}")
