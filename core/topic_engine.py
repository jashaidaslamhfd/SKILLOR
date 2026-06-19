import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq


class ViralTopicEngine:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        self.niche_keywords = [
            "psychology", "brain science", "human behavior", "mind tricks",
            "dark psychology", "cognitive bias", "body language", "sleep science",
            "2026 trends", "viral psychology"
        ]

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        trending = []
        random.shuffle(self.niche_keywords)

        for keyword in self.niche_keywords[:3]:
            try:
                time.sleep(random.uniform(2, 4))

                self.pytrends.build_payload([keyword], cat=14, timeframe=timeframe, geo='US')
                related = self.pytrends.related_queries()

                if related and keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(5).iterrows():
                            trending.append({
                                'query': str(row['query']),
                                'keyword': keyword,
                                'growth': float(row.get('value', 0)),
                                'source': 'google_trends',
                                'timestamp': datetime.now().isoformat(),
                                'viral_score': min(100, int(row.get('value', 0))),
                                'audience': 'US/UK/CA/AU'
                            })
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")
                if "429" in str(e):
                    print("Rate limited, waiting 30s...")
                    time.sleep(30)
                continue

        return trending

    def get_daily_topics(self, count: int = 3) -> List[Dict]:
        viral_topics = []
        try:
            daily = self.fetch_trending_topics("now 1-d")
            weekly = self.fetch_trending_topics("now 7-d")
            
            all_topics = daily + weekly
            viral_topics = self.filter_dead_topics(all_topics)

            if not viral_topics:
                raise Exception("Empty result")

        except Exception as e:
            print(f"⚠️ Google Trends failed: {e}. Switching to fallback.")
            viral_topics = self._get_fallback_topics()

        unique = {t['query']: t for t in viral_topics}.values()
        return list(unique)[:count]

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        return [t for t in topics if t.get('growth', 0) > 30 or t.get('viral_score', 0) > 30]

    def get_topic_angle(self, topic_data: Dict) -> str:
        angles = [
            "shocking truth revealed",
            "what experts don't tell you", 
            "the dark side",
            "hidden science",
            "banned knowledge",
            "what they hide from you"
        ]
        return random.choice(angles)

    def _get_fallback_topics(self) -> List[Dict]:
        return [
            {"query": "dark psychology secrets 2026", "keyword": "psychology", "growth": 500, "source": "fallback", "viral_score": 90, "audience": "US/UK"},
            {"query": "brain hacks for memory", "keyword": "brain science", "growth": 450, "source": "fallback", "viral_score": 85, "audience": "US/UK"},
            {"query": "why you cant stop scrolling", "keyword": "dark psychology", "growth": 600, "source": "fallback", "viral_score": 95, "audience": "US/UK"}
                                                ]
