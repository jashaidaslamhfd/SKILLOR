import os
import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq

from config.settings import NICHE_CONFIG


class ViralTopicEngine:
    def __init__(self, state_dir: str = "state"):
        # FIX: retries/backoff_factor removed (incompatible with current urllib3)
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        # FIX: settings.py already defines NICHE_CONFIG.KEYWORDS (12 terms)
        # but it was never used here — this had its own separate, smaller
        # hardcoded list. Now reads from the one source of truth.
        self.niche_keywords = list(NICHE_CONFIG.KEYWORDS)
        # FIX: dedup log moved from output/ (wiped on every fresh GitHub
        # Actions checkout — see workflow) to state/, which the workflow now
        # commits back to the repo after each run so it actually survives
        # between runs.
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self._used_log_path = os.path.join(self.state_dir, "used_topics.txt")

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

    def _load_used_topics(self) -> set:
        if os.path.exists(self._used_log_path):
            with open(self._used_log_path) as f:
                return set(l.strip() for l in f if l.strip())
        return set()

    def _save_used_topics(self, queries: List[str]):
        used = self._load_used_topics()
        used.update(queries)
        # Keep the log bounded so it doesn't grow forever.
        entries = list(used)[-500:]
        with open(self._used_log_path, 'w') as f:
            f.write('\n'.join(entries))

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
            print(f"Google Trends failed: {e}. Switching to fallback.")
            viral_topics = self._get_fallback_topics()

        unique = list({t['query']: t for t in viral_topics}.values())
        random.shuffle(unique)  # FIX: avoid always picking the same fallback topic first

        # FIX: skip topics already used recently (persisted in state/) so
        # the same topic — and therefore the same title/hook — doesn't keep
        # reappearing video after video.
        used = self._load_used_topics()
        fresh = [t for t in unique if t['query'] not in used]
        if not fresh:
            print("    Full topic rotation used - resetting topic history.")
            fresh = unique
            try:
                os.remove(self._used_log_path)
            except FileNotFoundError:
                pass

        chosen = fresh[:count]
        if chosen:
            self._save_used_topics([t['query'] for t in chosen])
        return chosen

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        return [t for t in topics if t.get('growth', 0) > 50 or t.get('viral_score', 0) > 50]

    def get_topic_angle(self, topic_data: Dict) -> str:
        angles = ["shocking truth revealed", "what experts don't tell you", "the dark side", "hidden science"]
        return random.choice(angles)

    def _get_fallback_topics(self) -> List[Dict]:
        # FIX: this used to return only 2 hardcoded topics. Since pytrends
        # (an unofficial, heavily rate-limited API) fails often — especially
        # from shared GitHub Actions IP ranges — the channel was effectively
        # stuck picking between 2 topics over and over. settings.py already
        # defines a 25-topic + 6-sub-niche pool (NICHE_CONFIG) that was never
        # actually used anywhere in the codebase — now it is.
        pool = list(NICHE_CONFIG.TOPICS) + [
            f"the dark psychology of {s}" for s in NICHE_CONFIG.SUB_NICHES
        ]
        random.shuffle(pool)
        return [
            {
                "query": q,
                "keyword": "psychology",
                "growth": random.randint(400, 600),
                "source": "fallback",
                "viral_score": random.randint(80, 95),
            }
            for q in pool
        ]
