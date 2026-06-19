import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq

class ViralTopicEngine:
    def __init__(self):
        # FIX: retries/backoff_factor removed (incompatible with current urllib3)
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        self.niche_keywords = [
            "psychology", "brain science", "human behavior", "mind tricks",
            "dark psychology", "cognitive bias", "body language", "sleep science",
            "gaslighting", "narcissist traits", "red flags" # ADDED: USA/UK evergreen
        ]

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        trending = []
        random.shuffle(self.niche_keywords)

        for keyword in self.niche_keywords[:4]: # CHANGED: [:2] → [:4] more topics
            try:
                time.sleep(random.uniform(3, 5))

                self.pytrends.build_payload([keyword], cat=14, timeframe=timeframe, geo='US')
                related = self.pytrends.related_queries()

                if related and keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(3).iterrows():
                            trending.append({
                                'query': str(row['query']),
                                'keyword': keyword,
                                'growth': float(row.get('value', 0)),
                                'source': 'google_trends',
                                'timestamp': datetime.now().isoformat(),
                                'viral_score': min(100, int(row.get('value', 0)))
                            })
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")
                if "429" in str(e):
                    print("Rate limited, waiting 20s...")
                    time.sleep(20)
                continue

        return trending

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        # FIX: default count changed from 2 -> 1 so a single run produces
        # exactly one video unless the caller explicitly asks for more.
        viral_topics = []
        try:
            daily = self.fetch_trending_topics("now 1-d")
            viral_topics = self.filter_dead_topics(daily)

            if not viral_topics:
                raise Exception("Empty result")

        except Exception as e:
            print(f"⚠️ Google Trends failed: {e}. Switching to fallback.")
            viral_topics = self._get_fallback_topics()

        unique = list({t['query']: t for t in viral_topics}.values())
        random.shuffle(unique) # FIX: avoid always picking the same fallback topic first
        return unique[:count]

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        return [t for t in topics if t.get('growth', 0) > 50 or t.get('viral_score', 0) > 50]

    def get_topic_angle(self, topic_data: Dict) -> str:
        # FIXED: indentation error tha yahan
        angles = [
            "why you never noticed",
            "the psychology behind",
            "used by manipulative people",
            "your brain does this automatically",
            "the dark side of",
            "what they don't teach you"
        ]
        return random.choice(angles)

    def get_full_title(self, topic_data: Dict) -> str:
        """Topic + Angle se ready YouTube title"""
        angle = self.get_topic_angle(topic_data)
        query = topic_data['query']
        return f"{angle} {query}".title()

    def _get_fallback_topics(self) -> List[Dict]:
        return [
            {"query": "dark psychology secrets", "
