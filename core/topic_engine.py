import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq


class ViralTopicEngine:
    def __init__(self):
        # FIX: retries/backoff_factor removed (incompatible with current urllib3)
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        # UPDATED: shifted from pure "dark psychology" (finite, repeats fast)
        # to Human/Brain/Body Mystery niche — same dark-curiosity feel but
        # practically infinite topic supply for long-term sustainability.
        self.niche_keywords = [
            "human body mystery", "brain mystery", "sleep science",
            "why do we dream", "strange body facts", "hidden science",
            "deja vu explained", "human behavior science", "weird body facts",
            "psychology of fear", "why does the brain", "unexplained body reactions"
        ]

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        trending = []
        random.shuffle(self.niche_keywords)

        for keyword in self.niche_keywords[:2]:
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
        # FIX: default count=1 so a single run produces exactly one video
        # unless the caller explicitly asks for more.
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
        random.shuffle(unique)  # avoid always picking the same fallback topic first
        return unique[:count]

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        return [t for t in topics if t.get('growth', 0) > 50 or t.get('viral_score', 0) > 50]

    def get_topic_angle(self, topic_data: Dict) -> str:
        # UPDATED: angles now drive "Human Mystery + Suspense + Twist + Loop"
        # storytelling instead of pure manipulation/dark-psych framing.
        angles = [
            "why this happens and what it really means",
            "the hidden mystery behind",
            "what scientists only recently discovered about",
            "your body does this without you knowing",
            "the unexplained reason behind",
            "what they don't teach you about",
        ]
        return random.choice(angles)

    def _get_fallback_topics(self) -> List[Dict]:
        # UPDATED: fallback pool now matches the Human/Brain Mystery niche —
        # practically infinite topic supply, won't repeat after 100-200 videos.
        return [
            {"query": "why do we dream", "keyword": "sleep science", "growth": 500, "source": "fallback", "viral_score": 95},
            {"query": "why does deja vu happen", "keyword": "brain mystery", "growth": 480, "source": "fallback", "viral_score": 92},
            {"query": "why do we yawn", "keyword": "human body mystery", "growth": 460, "source": "fallback", "viral_score": 88},
            {"query": "why can't we remember being babies", "keyword": "brain mystery", "growth": 470, "source": "fallback", "viral_score": 90},
            {"query": "why do fevers happen", "keyword": "human body mystery", "growth": 450, "source": "fallback", "viral_score": 85},
            {"query": "why do we blush", "keyword": "human body mystery", "growth": 440, "source": "fallback", "viral_score": 84},
            {"query": "why do sleep jerks happen", "keyword": "sleep science", "growth": 455, "source": "fallback", "viral_score": 86},
            {"query": "brain hacks for memory", "keyword": "brain science", "growth": 450, "source": "fallback", "viral_score": 85},
             ]
