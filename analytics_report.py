import os
import json
from datetime import datetime
from core.metrics import get_all_metrics

def generate_report():
    os.makedirs('reports', exist_ok=True)

    try:
        metrics = get_all_metrics()
    except Exception as e:
        print(f"Error loading metrics: {e}")
        metrics = []

    total = len(metrics)
    successful = sum(1 for m in metrics if m.get('status') == 'uploaded')

    report_data = {
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_videos": total,
        "successful_uploads": successful,
        "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
        "platforms": {
            "youtube": sum(1 for m in metrics if m.get('youtube')),
            "instagram": sum(1 for m in metrics if m.get('instagram')),
            "facebook": sum(1 for m in metrics if m.get('facebook'))
        },
        "avg_hook_score": round(sum(m.get('hook_score', 0) for m in metrics) / total, 1) if total > 0 else 0
    }

    report_path = f"reports/analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📊 ANALYTICS REPORT")
    print(f"{'='*50}")
    print(f"Total Videos: {report_data['total_videos']}")
    print(f"Success Rate: {report_data['success_rate']}%")
    print(f"Avg Hook Score: {report_data['avg_hook_score']}/10")
    print(f"\nPlatform Breakdown:")
    print(f" YouTube: {report_data['platforms']['youtube']}")
    print(f" Instagram: {report_data['platforms']['instagram']}")
    print(f" Facebook: {report_data['platforms']['facebook']}")
    print(f"\n✅ Report saved: {report_path}")
    return report_path

if __name__ == "__main__":
    generate_report()
