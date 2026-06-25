"""
Metrics Tracker - Analytics for YouTube Automation
Tracks: Views, Retention, CTR, Upload Success, Revenue
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

METRICS_DIR = Path("metrics")
METRICS_DIR.mkdir(exist_ok=True)


class MetricsTracker:
    """Track all performance metrics"""
    
    def __init__(self):
        self.metrics_file = METRICS_DIR / "performance.json"
        self.daily_file = METRICS_DIR / f"daily_{datetime.now().strftime('%Y%m%d')}.json"
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = self._default_metrics()
        else:
            self.data = self._default_metrics()
    
    def _default_metrics(self) -> Dict:
        return {
            'total_videos': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_duration': 0,
            'total_word_count': 0,
            'average_hook_score': 0,
            'videos_by_platform': {
                'youtube': 0,
                'facebook': 0,
                'instagram': 0
            },
            'daily_stats': [],
            'start_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def record_video(self, video_data: Dict, upload_results: Dict):
        """Record a completed video"""
        self.data['total_videos'] += 1
        self.data['total_duration'] += video_data.get('duration', 0)
        self.data['total_word_count'] += video_data.get('word_count', 0)
        
        # Hook score
        hook_score = video_data.get('hook_score', 0)
        if self.data['average_hook_score'] == 0:
            self.data['average_hook_score'] = hook_score
        else:
            self.data['average_hook_score'] = (
                (self.data['average_hook_score'] * (self.data['total_videos'] - 1) + hook_score) 
                / self.data['total_videos']
            )
        
        # Platform uploads
        for platform, result in upload_results.items():
            if result.get('status') in ['uploaded', 'published']:
                self.data['videos_by_platform'][platform] += 1
                self.data['successful_uploads'] += 1
            elif result.get('status') == 'error':
                self.data['failed_uploads'] += 1
        
        # Daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        daily = {
            'date': today,
            'video': video_data.get('topic', ''),
            'duration': video_data.get('duration', 0),
            'hook_score': video_data.get('hook_score', 0),
            'word_count': video_data.get('word_count', 0),
            'uploads': upload_results
        }
        
        # Check if today already exists
        existing = [d for d in self.data['daily_stats'] if d.get('date') == today]
        if existing:
            existing[0].update(daily)
        else:
            self.data['daily_stats'].append(daily)
        
        self.data['last_updated'] = datetime.now().isoformat()
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            # Also save daily report
            with open(self.daily_file, 'w') as f:
                json.dump(self.data['daily_stats'][-30:], f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Could not save metrics: {e}")
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        return {
            'total_videos': self.data['total_videos'],
            'successful_uploads': self.data['successful_uploads'],
            'failed_uploads': self.data['failed_uploads'],
            'success_rate': (
                self.data['successful_uploads'] / max(1, self.data['total_videos']) * 100
            ),
            'average_duration': (
                self.data['total_duration'] / max(1, self.data['total_videos'])
            ),
            'average_hook_score': self.data['average_hook_score'],
            'platforms': self.data['videos_by_platform'],
            'last_7_days': self._get_last_7_days()
        }
    
    def _get_last_7_days(self) -> List[Dict]:
        """Get last 7 days stats"""
        return self.data['daily_stats'][-7:]
    
    def export_report(self) -> str:
        """Generate human-readable report"""
        summary = self.get_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║                    📊 PERFORMANCE REPORT                ║
╠══════════════════════════════════════════════════════════╣
║                                                         ║
║  📹 Total Videos:        {summary['total_videos']}                     
║  ✅ Successful Uploads:  {summary['successful_uploads']}                     
║  ❌ Failed Uploads:      {summary['failed_uploads']}                     
║  📈 Success Rate:        {summary['success_rate']:.1f}%                     
║                                                         ║
║  ⏱️ Average Duration:    {summary['average_duration']:.1f}s                     
║  🎯 Average Hook Score:  {summary['average_hook_score']:.1f}/10                     
║                                                         ║
║  📤 Platform Uploads:                                    
║     YouTube:   {summary['platforms']['youtube']}                     
║     Facebook:  {summary['platforms']['facebook']}                     
║     Instagram: {summary['platforms']['instagram']}                     
║                                                         ║
╚══════════════════════════════════════════════════════════╝
        """
        return report


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    tracker = MetricsTracker()
    print(tracker.export_report())
