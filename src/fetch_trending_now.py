#!/usr/bin/env python3
"""
FETCH TRENDING NOW — Real US trending topics (body/science/health)
Run: python scripts/fetch_trending_now.py --count 10
"""
import os
import sys
import json
import feedparser
import requests
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# ============================================
# REAL TREND SOURCES (no API key needed)
# ============================================

TREND_SOURCES = {
    "google_trends_us": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
    "google_trends_health": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US&cat=45",  # Health
    "google_trends_sci": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US&cat=172",  # Science
    "reddit_science": "https://www.reddit.com/r/science/.rss?limit=20",
    "reddit_askscience": "https://www.reddit.com/r/askscience/.rss?limit=20",
    "reddit_biology": "https://www.reddit.com/r/biology/.rss?limit=20",
    "reddit_neuroscience": "https://www.reddit.com/r/neuroscience/.rss?limit=15",
    "pubmed_latest": "https://pubmed.ncbi.nlm.nih.gov/rss/search/1cVvJzKq9YmZ7wL8vVz5Kq9YmZ7wL8vVz5/",  # Recent papers
}

# Keywords that match our niche
NICHE_KEYWORDS = [
    'brain', 'sleep', 'memory', 'neuron', 'psychology', 'mental',
    'heart', 'blood', 'cardio', 'pulse', 'vein', 'artery',
    'eye', 'vision', 'twitch', 'sight', 'blind',
    'gut', 'stomach', 'digest', 'microbiome', 'bacteria',
    'muscle', 'bone', 'joint', 'pain', 'exercise',
    'hormone', 'cortisol', 'melatonin', 'dopamine', 'serotonin',
    'immune', 'virus', 'cell', 'dna', 'gene', 'aging',
    'breath', 'lung', 'oxygen', 'yawn', 'sneeze',
    'skin', 'hair', 'nail', 'sweat', 'touch',
    'dream', 'nightmare', 'lucid', 'rem', 'circadian',
]

def fetch_rss_feed(url: str, source_name: str) -> list:
    """Fetch and parse RSS feed"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; SkillorBot/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        return [{
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'summary': entry.get('summary', ''),
            'source': source_name,
            'published': entry.get('published', ''),
        } for entry in feed.entries[:20]]
    except Exception as e:
        print(f"⚠️ {source_name} failed: {e}")
        return []

def is_niche_relevant(text: str) -> bool:
    """Check if content matches our body/science niche"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in NICHE_KEYWORDS)

def extract_topic(title: str, summary: str) -> str:
    """Extract clean topic from title/summary"""
    # Remove common prefixes
    for prefix in ['Study: ', 'Research: ', 'Scientists ', 'Doctors ', 'New study ', 'Breaking: ']:
        if title.startswith(prefix):
            title = title[len(prefix):]
    
    # Clean up
    topic = title.strip()
    if topic.endswith('.'):
        topic = topic[:-1]
    
    return topic

def score_trending_relevance(item: dict) -> float:
    """Score how viral-ready this trend is"""
    score = 0
    text = (item['title'] + ' ' + item.get('summary', '')).lower()
    
    # Niche keyword matches
    for kw in NICHE_KEYWORDS:
        if kw in text:
            score += 2
    
    # Viral triggers
    viral_triggers = ['shocking', 'surprising', 'never knew', 'changes everything', 
                      'scientists discover', 'new study', 'reveals', 'proves',
                      'warning', 'urgent', 'critical', 'breakthrough']
    for trigger in viral_triggers:
        if trigger in text:
            score += 3
    
    # Recency bonus (prefer last 24h)
    return score

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fetch real-time trending topics for body/science niche")
    parser.add_argument("--count", type=int, default=10, help="Number of topics to return")
    parser.add_argument("--output", default="output/trending_topics.json", help="Output file")
    args = parser.parse_args()
    
    print("\n🔥 FETCHING REAL-TIME TRENDS (US, Body/Science/Health)")
    print("=" * 60)
    
    all_items = []
    for name, url in TREND_SOURCES.items():
        items = fetch_rss_feed(url, name)
        all_items.extend(items)
        print(f"  {name}: {len(items)} items")
    
    # Filter & score
    relevant = [item for item in all_items if is_niche_relevant(item['title'] + ' ' + item.get('summary', ''))]
    for item in relevant:
        item['relevance_score'] = score_trending_relevance(item)
        item['topic'] = extract_topic(item['title'], item.get('summary', ''))
    
    # Sort by score, deduplicate
    relevant.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    seen = set()
    unique = []
    for item in relevant:
        topic_key = item['topic'].lower().strip()
        if topic_key not in seen and len(topic_key) > 10:
            seen.add(topic_key)
            unique.append(item)
        if len(unique) >= args.count:
            break
    
    # Output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    output_data = {
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
        'topics': [{
            'topic': item['topic'],
            'source': item['source'],
            'source_url': item['link'],
            'relevance_score': item['relevance_score'],
            'summary': item.get('summary', '')[:200],
        } for item in unique]
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ TOP {len(unique)} TRENDING TOPICS FOR YOUR NICHE:")
    print("-" * 60)
    for i, item in enumerate(unique, 1):
        print(f"  {i}. {item['topic']}")
        print(f"     Source: {item['source']} | Score: {item['relevance_score']}")
        print(f"     URL: {item['source_url'][:80]}...")
        print()
    
    print(f"💾 Saved to {args.output}")
    print("\n💡 NEXT: Use one of these topics with growth_mode.py:")
    print(f"   python scripts/growth_mode.py --topic \"{unique[0]['topic'] if unique else 'your topic'}\"")

if __name__ == "__main__":
    main()
