"""
Topic Engine — REFINED: Brain & Body Science (FIXED WITH ROBUST 429 FALLBACK)
NICHE: Universal brain and body science facts (age-neutral)
GOAL: Low competition, high demand topics
SOURCE: Google Trends + Fallback topics
"""

import time
import random
import re
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None
    print("⚠️ pytrends not installed. Install with: pip install pytrends")


class ViralTopicEngine:
    """Topic Engine for Memory & Brain Fog Niche - FIXED"""
    
    # Disk par save hone wali used_topics file
    USED_TOPICS_FILE = "state/used_topics.json"
    
    def __init__(self):
        # Initialize Google Trends
        self.pytrends = None
        if TrendReq:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
                print("✅ Google Trends initialized")
            except Exception as e:
                print(f"⚠️ Google Trends init failed: {e}")
        
        # used_topics ko disk se load karo (session restart par bhi yaad rahe)
        self.used_topics = self._load_used_topics()
        
        # ============================================================
        # ALL-AGE: Body + Brain Science Keywords (Universal)
        # ============================================================
        self.memory_keywords = [
            "brain development",
            "infant sleep regression",
            "toddler growth spurts",
            "separation anxiety",
            "newborn reflexes",
            "language acquisition",
            "sensory processing",
            "motor skills",
            "emotional bonding"
        ]
        
        # Fallback topics pool to use if trends fail or hit rate limits (Cluster of 20+)
        self.fallback_topics = [
            {"query": "why do babies stare into space", "viral_score": 92, "suspense_score": 88, "pattern": "mystery"},
            {"query": "why do newborns grunt so much", "viral_score": 89, "suspense_score": 85, "pattern": "curiosity"},
            {"query": "why do babies clench their fists", "viral_score": 88, "suspense_score": 82, "pattern": "statement"},
            {"query": "why do babies curl their toes", "viral_score": 87, "suspense_score": 80, "pattern": "mystery"},
            {"query": "why do babies smile in their sleep", "viral_score": 95, "suspense_score": 90, "pattern": "emotional"},
            {"query": "why do babies suck their bottom lip", "viral_score": 85, "suspense_score": 78, "pattern": "curiosity"},
            {"query": "why do babies rub their eyes", "viral_score": 91, "suspense_score": 84, "pattern": "statement"},
            {"query": "why do babies grab their ears", "viral_score": 90, "suspense_score": 86, "pattern": "mystery"},
            {"query": "why do babies shake their heads", "viral_score": 93, "suspense_score": 89, "pattern": "curiosity"},
            {"query": "why do babies kick their legs", "viral_score": 86, "suspense_score": 80, "pattern": "statement"},
            {"query": "why do babies sneeze so much", "viral_score": 88, "suspense_score": 82, "pattern": "mystery"},
            {"query": "why do babies arch their backs", "viral_score": 92, "suspense_score": 87, "pattern": "curiosity"},
            {"query": "why do babies sweat while sleeping", "viral_score": 89, "suspense_score": 83, "pattern": "statement"},
            {"query": "why do babies stick their tongues out", "viral_score": 94, "suspense_score": 91, "pattern": "mystery"},
            {"query": "why do babies breathe fast while sleeping", "viral_score": 90, "suspense_score": 85, "pattern": "curiosity"},
            {"query": "why do babies hate tummy time", "viral_score": 87, "suspense_score": 81, "pattern": "statement"},
            {"query": "why do babies chew on their hands", "viral_score": 91, "suspense_score": 86, "pattern": "mystery"},
            {"query": "why do babies cross their eyes", "viral_score": 89, "suspense_score": 84, "pattern": "curiosity"},
            {"query": "why do babies lose hair", "viral_score": 85, "suspense_score": 79, "pattern": "statement"},
            {"query": "why do babies get hiccups", "viral_score": 93, "suspense_score": 88, "pattern": "mystery"}
        ]

    def _load_used_topics(self) -> List[str]:
        """Load used topics from disk storage"""
        os.makedirs("state", exist_ok=True)
        if os.path.exists(self.USED_TOPICS_FILE):
            try:
                with open(self.USED_TOPICS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading used topics: {e}")
        return []

    def _save_used_topics(self):
        """Save used topics to disk storage"""
        try:
            with open(self.USED_TOPICS_FILE, 'w') as f:
                json.dump(self.used_topics, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving used topics: {e}")

    def _get_trending_topics(self) -> List[Dict]:
        """Fetch trends via pytrends with robust rate-limit/429 fallback"""
        if not self.pytrends:
            return []
        
        topics = []
        try:
            # Pytrends realtime breakout/trending searches
            trending = self.pytrends.trending_searches(pn='united_states')
            if not trending.empty:
                queries = trending[0].tolist()
                for q in queries[:10]:
                    # Filter matching keywords or add directly
                    topics.append({
                        'query': q.lower(),
                        'viral_score': random.randint(85, 99),
                        'suspense_score': random.randint(75, 95),
                        'pattern': 'trends',
                        'source': 'google_trends'
                    })
        except Exception as e:
            # 429 Rate Limit Handled Gracefully
            if "429" in str(e) or "Too Many Requests" in str(e):
                print("⚠️ Google Trends rate limit hit (429). Using backup fallback pool.")
            else:
                print(f"⚠️ Google Trends fetch failed: {e}")
        return topics

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """Fetch daily topics, prioritizing fresh / unused trending searches"""
        all_trends = self._get_trending_topics()
        
        # Filter out already used items
        fresh_trends = [t for t in all_trends if t['query'] not in self.used_topics]
        
        # Shuffle fallbacks to avoid repeating same sequences
        random.shuffle(self.fallback_topics)
        fresh_fallbacks = [
            f for f in self.fallback_topics 
            if f['query'] not in self.used_topics
        ]
        
        # Merge lists
        pool = fresh_trends + fresh_fallbacks
        
        # If pool gets depleted, clear disk state & reset
        if len(pool) < count:
            print("⚠️ Topics pool nearly exhausted. Resetting used topics tracking cache.")
            self.clear_used_topics()
            pool = fresh_trends + self.fallback_topics
            random.shuffle(pool)
            
        selected = []
        for _ in range(count):
            if not pool:
                # Absolute fallback safety
                selected.append({
                    "query": f"why do babies {random.choice(self.memory_keywords)}",
                    "viral_score": 90,
                    "suspense_score": 85,
                    "pattern": "fallback",
                    "source": "safety_pool"
                })
                continue
                
            item = pool.pop(0)
            query = item.get('query', '')
            
            # Mark consumed
            self.used_topics.append(query)
            selected.append(item)
            
        # Persist consume status to disk
        self._save_used_topics()
        return selected

    def is_topic_viral(self, topic: str) -> bool:
        """Check if topic contains trigger words that spark high CTR"""
        personal_words = ["you", "your", "experience"]
        return any(w in topic.lower() for w in personal_words)

    def clear_used_topics(self):
        """Clear used topics cache (memory + disk)"""
        self.used_topics.clear()
        self._save_used_topics()  # Disk bhi clear karo
        print("🧹 Cleared used topics cache (memory + disk)")

    def get_stats(self) -> Dict:
        """Get topic engine statistics"""
        return {
            'used_topics_count': len(self.used_topics),
            'fallback_topics_count': len(self.fallback_topics),
            'memory_keywords_count': len(self.memory_keywords),
            'trending_available': self.pytrends is not None,
        }
