"""
Analytics Report Generator
Generates daily/weekly performance reports
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from core.metrics import MetricsTracker

try:
    from core.youtube_analytics import YouTubeAnalytics
except:
    YouTubeAnalytics = None


def generate_daily_report():
    """Generate daily performance report"""
    tracker = MetricsTracker()
    
    print("\n" + "="*60)
    print("📊 DAILY PERFORMANCE REPORT")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)
    
    # Today's stats
    today = datetime.now().strftime('%Y-%m-%d')
    today_stats = [d for d in tracker.data['daily_stats'] if d.get('date') == today]
    
    if today_stats:
        stats = today_stats[0]
        print(f"\n📹 Today's Video: {stats.get('video', 'N/A')}")
        print(f"   Duration: {stats.get('duration', 0):.1f}s")
        print(f"   Hook Score: {stats.get('hook_score', 0)}/10")
        print(f"   Word Count: {stats.get('word_count', 0)}")
    
    # Summary
    summary = tracker.get_summary()
    print(f"\n📊 Overall Stats:")
    print(f"   Total Videos: {summary['total_videos']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Avg Hook Score: {summary['average_hook_score']:.1f}/10")
    
    # YouTube Analytics (if available)
    if YouTubeAnalytics:
        try:
            yt = YouTubeAnalytics()
            channel = yt.get_channel_stats()
            if channel and 'subscribers' in channel:
                print(f"\n📈 Channel Stats:")
                print(f"   Subscribers: {channel['subscribers']:,}")
                print(f"   Total Views: {channel['views']:,}")
        except:
            pass
    
    print("\n" + "="*60)


def generate_weekly_report():
    """Generate weekly performance report"""
    tracker = MetricsTracker()
    
    print("\n" + "="*60)
    print("📊 WEEKLY PERFORMANCE REPORT")
    print(f"   Week: {datetime.now().strftime('%Y-W%W')}")
    print("="*60)
    
    # Last 7 days
    last_7 = tracker._get_last_7_days()
    
    if last_7:
        print("\n📹 Last 7 Days:")
        for day in last_7:
            print(f"   {day.get('date')}: {day.get('video', 'N/A')} | "
                  f"Score: {day.get('hook_score', 0)}/10")
    
    # Summary
    summary = tracker.get_summary()
    print(f"\n📊 Weekly Stats:")
    print(f"   Videos: {len(last_7)}")
    print(f"   Avg Hook Score: {summary['average_hook_score']:.1f}/10")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--daily', action='store_true', help='Daily report')
    parser.add_argument('--weekly', action='store_true', help='Weekly report')
    args = parser.parse_args()
    
    if args.weekly:
        generate_weekly_report()
    else:
        generate_daily_report()
