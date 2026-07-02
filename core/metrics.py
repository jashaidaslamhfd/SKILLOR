import json
import os
from datetime import datetime

METRICS_FILE = "metrics.jsonl"

def log_metrics(script_data, result):
    os.makedirs(os.path.dirname(METRICS_FILE) or '.', exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "title": script_data.get('title'),
        "niche": script_data.get('niche'),
        "hook_score": script_data.get('hook_score', 0),
        "topic": script_data.get('topic'),
        **result
    }

    with open(METRICS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

def get_all_metrics():
    if not os.path.exists(METRICS_FILE):
        return []

    metrics = []
    with open(METRICS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                metrics.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return metrics
