import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq

class ViralTopicEngine:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        # FIX: Expanded niche keywords — better Google Trends coverage
        self.niche_keywords = [
            "human body mystery", "brain mystery", "sleep science",
            "why do we dream", "strange body facts", "hidden science",
            "deja vu explained", "human behavior science", "weird body facts",
            "psychology of fear", "why does the brain", "unexplained body reactions",
            "what happens when you sleep", "why do we forget dreams",
            "brain tricks psychology", "body reacting without thinking",
            "why do we get goosebumps", "what causes intuition",
            "why do we laugh", "brain processing speed", "human memory tricks",
            "why do we cry", "what is consciousness", "brain vs mind",
            "why do we hiccup", "sleep paralysis science", "lucid dreaming facts",
            "why do we sneeze", "brain plasticity", "déjà vu psychology",
            "why do we itch", "muscle memory brain", "adrenaline body reaction",
        ]

        # FIX: Viral pattern library — current Shorts trends
        self.viral_patterns = {
            'shock_visual': [ # Triggers glitch/shake effect
                "the moment your brain realizes",
                "what your eyes are actually seeing",
                "the split second your body reacts",
                "when your brain finally connects",
                "the instant everything changes",
            ],
            'curiosity_gap': [ # High CTR hooks
                "scientists can't explain why",
                "your body does this every night",
                "nobody talks about this part",
                "the part they always skip",
                "what happens in the first 3 seconds",
            ],
            'contrarian': [ # Pattern interrupt
                "everything you know about X is wrong",
                "stop believing this myth",
                "the real reason isn't what you think",
                "doctors get this wrong every time",
                "the truth they don't want you to know",
            ],
            'personal_stake': [ # Viewer engagement - 35+ audience killer
                "this is happening to you right now",
                "your brain is doing this as you watch",
                "your body is hiding this from you",
                "you experienced this today",
                "this is why you feel that way",
            ],
            'countdown': [ # List format — high retention
                "3 signs your brain is",
                "the one thing that proves",
                "2 seconds before your body",
                "the only reason you",
                "5 things your mind does",
            ]
        }

        # FIX: Topic suspense scoring — which topics create visual shock
        self.suspense_scores = {
            'sleep': 95, 'dream': 92, 'brain': 90, 'fear': 88,
            'memory': 85, 'consciousness': 87, 'paralysis': 96,
            'adrenaline': 89, 'intuition': 84, 'déjà vu': 91,
            'lucid': 88, 'body': 82, 'mind': 80, 'psychology': 92,
            'personal': 94
        }

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        trending = []
        random.shuffle(self.niche_keywords)

        # FIX: Try more keywords for better coverage
        for keyword in self.niche_keywords[:3]:
            try:
                time.sleep(random.uniform(2, 4))

                self.pytrends.build_payload([keyword], cat=14, timeframe=timeframe, geo='US')
                related = self.pytrends.related_queries()

                if related and keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(5).iterrows(): # FIX: More results
                            query = str(row['query'])
                            # FIX: Clean and score
                            cleaned = self._clean_topic(query)
                            suspense = self._calculate_suspense_score(cleaned)

                            trending.append({
                                'query': cleaned,
                                'keyword': keyword,
                                'growth': float(row.get('value', 0)),
                                'source': 'google_trends',
                                'timestamp': datetime.now().isoformat(),
                                'viral_score': min(100, int(row.get('value', 0))),
                                'suspense_score': suspense, # NEW
                                'pattern': self._select_viral_pattern(cleaned, suspense), # NEW
                            })
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")
                if "429" in str(e):
                    print("Rate limited, waiting 30s...")
                    time.sleep(30)
                continue

        return trending

    def _clean_topic(self, query: str) -> str:
        """FIX: Clean trending query into usable topic"""
        import re
        query = re.sub(r'^\d+\s+', '', query) # Remove "10 " from "10 reasons..."
        query = re.sub(r'\s+(reasons|ways|things|facts|signs|tricks|hacks)\s+', ' ', query)
        query = query.strip()
        return query[0].upper() + query[1:] if query else query

    def _calculate_suspense_score(self, query: str) -> int:
        """FIX: Calculate how 'shock-worthy' a topic is (0-100)"""
        query_lower = query.lower()
        score = 50 # Base

        for keyword, value in self.suspense_scores.items():
            if keyword in query_lower:
                score = max(score, value)

        visual_words = ['see', 'watch', 'look', 'eyes', 'visual', 'dark', 'shadow']
        scary_words = ['terrifying', 'scary', 'shocking', 'creepy', 'unsettling', 'bizarre']

        for word in visual_words:
            if word in query_lower:
                score += 5
        for word in scary_words:
            if word in query_lower:
                score += 8

        return min(100, score)

    def _select_viral_pattern(self, query: str, suspense_score: int) -> str:
        """FIX: Select best viral pattern based on topic suspense score + SAFETY CHECK"""
        # SAFETY: Agar pattern list khali ho to backup use karo
        def safe_choice(pattern_key, fallback='curiosity_gap'):
            pattern_list = self.viral_patterns.get(pattern_key, [])
            if not pattern_list:
                pattern_list = self.viral_patterns.get(fallback, ["the truth about"])
            return random.choice(pattern_list)

        if suspense_score > 90:
            return safe_choice('shock_visual')
        elif suspense_score > 80:
            return safe_choice('curiosity_gap')
        elif 'myth' in query.lower() or 'wrong' in query.lower():
            return safe_choice('contrarian')
        elif 'you' in query.lower() or 'your' in query.lower():
            return safe_choice('personal_stake')
        else:
            return safe_choice('countdown')

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        viral_topics = []
        try:
            daily = self.fetch_trending_topics("now 1-d")
            viral_topics = self.filter_dead_topics(daily)

            if not viral_topics:
                raise Exception("Empty result")

        except Exception as e:
            print(f"⚠️ Google Trends failed: {e}. Switching to fallback.")
            viral_topics = self._get_fallback_topics()

        # FIX: Sort by combined viral + suspense score
        viral_topics.sort(key=lambda x: (x.get('viral_score', 0) + x.get('suspense_score', 50)) / 2, reverse=True)

        unique = list({t['query']: t for t in viral_topics}.values())
        random.shuffle(unique) # Randomize same-score items
        return unique[:count]

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        # FIX: Lower threshold to catch more topics, but require minimum suspense
        return [
            t for t in topics
            if (t.get('growth', 0) > 30 or t.get('viral_score', 0) > 30)
            and t.get('suspense_score', 0) > 75 # NEW: Minimum suspense requirement
        ]

    def get_topic_angle(self, topic_data: Dict) -> str:
        """FIX: Generate angle with viral pattern integration"""
        base_angles = [
            "why this happens and what it really means",
            "the hidden mystery behind",
            "what scientists only recently discovered about",
            "your body does this without you knowing",
            "the unexplained reason behind",
            "what they don't teach you about",
        ]

        pattern = topic_data.get('pattern', '')
        if pattern:
            return f"{pattern} {topic_data['query']}"

        return f"{random.choice(base_angles)} {topic_data['query']}"

    def get_shock_angle(self, topic_data: Dict) -> str:
        """NEW: Generate shock-specific angle for visual effect"""
        shock_angles = [
            f"the exact moment {topic_data['query']} happens to you",
            f"caught on camera: {topic_data['query']}",
            f"the split second before {topic_data['query']} kicks in",
            f"your body's reaction to {topic_data['query']} - visual proof",
            f"the visual proof that {topic_data['query']} is real",
        ]
        return random.choice(shock_angles)

    def get_topic_metadata(self, topic_data: Dict) -> Dict:
        """NEW: Complete topic metadata for content generator"""
        return {
            'topic': topic_data['query'],
            'angle': self.get_topic_angle(topic_data),
            'shock_angle': self.get_shock_angle(topic_data),
            'suspense_score': topic_data.get('suspense_score', 70),
            'viral_score': topic_data.get('viral_score', 50),
            'pattern': topic_data.get('pattern', 'curiosity_gap'),
            'growth': topic_data.get('growth', 0),
            'source': topic_data.get('source', 'unknown'),
        }

    def _get_fallback_topics(self) -> List[Dict]:
        # FIX: 30+ topics — 200+ videos tak no repeat
        fallbacks = [
            {"query": "Why do we dream", "keyword": "sleep science", "growth": 500, "source": "fallback", "viral_score": 95, "suspense_score": 92},
            {"query": "Sleep paralysis demons", "keyword": "sleep science", "growth": 520, "source": "fallback", "viral_score": 98, "suspense_score": 96},
            {"query": "Lucid dreaming secrets", "keyword": "sleep science", "growth": 480, "source": "fallback", "viral_score": 90, "suspense_score": 88},
            {"query": "Why do sleep jerks happen", "keyword": "sleep science", "growth": 455, "source": "fallback", "viral_score": 86, "suspense_score": 85},
            {"query": "What happens during REM sleep", "keyword": "sleep science", "growth": 470, "source": "fallback", "viral_score": 88, "suspense_score": 87},
            {"query": "Why does deja vu happen", "keyword": "brain mystery", "growth": 480, "source": "fallback", "viral_score": 92, "suspense_score": 91},
            {"query": "Why can't we remember being babies", "keyword": "brain mystery", "growth": 470, "source": "fallback", "viral_score": 90, "suspense_score": 89},
            {"query": "What is consciousness really", "keyword": "brain mystery", "growth": 490, "source": "fallback", "viral_score": 94, "suspense_score": 93},
            {"query": "Brain tricks your eyes play", "keyword": "brain mystery", "growth": 460, "source": "fallback", "viral_score": 87, "suspense_score": 86},
            {"query": "Why do we forget dreams instantly", "keyword": "brain mystery", "growth": 475, "source": "fallback", "viral_score": 89, "suspense_score": 88},
            {"query": "Why do we get goosebumps", "keyword": "human body mystery", "growth": 440, "source": "fallback", "viral_score": 84, "suspense_score": 82},
            {"query": "Why do we blush uncontrollably", "keyword": "human body mystery", "growth": 430, "source": "fallback", "viral_score": 83, "suspense_score": 81},
            {"query": "Adrenaline rush visual effects", "keyword": "human body mystery", "growth": 450, "source": "fallback", "viral_score": 85, "suspense_score": 89},
            {"query": "Why do we hiccup nonstop", "keyword": "human body mystery", "growth": 420, "source": "fallback", "viral_score": 80, "suspense_score": 78},
            {"query": "Muscle memory explained visually", "keyword": "human body mystery", "growth": 440, "source": "fallback", "viral_score": 84, "suspense_score": 83},
            {"query": "Psychology of fear response", "keyword": "psychology", "growth": 460, "source": "fallback", "viral_score": 86, "suspense_score": 88},
            {"query": "Why do we laugh at pain", "keyword": "psychology", "growth": 445, "source": "fallback", "viral_score": 85, "suspense_score": 84},
            {"query": "What intuition really is", "keyword": "psychology", "growth": 455, "source": "fallback", "viral_score": 87, "suspense_score": 85},
            {"query": "Why do we cry when happy", "keyword": "psychology", "growth": 435, "source": "fallback", "viral_score": 83, "suspense_score": 81},
            {"query": "Brain processing speed vs computer", "keyword": "brain science", "growth": 470, "source": "fallback", "viral_score": 88, "suspense_score": 86},
            {"query": "Hidden body functions you never notice", "keyword": "human body mystery", "growth": 480, "source": "fallback", "viral_score": 90, "suspense_score": 87},
            {"query": "Weird facts about human eyes", "keyword": "human body mystery", "growth": 465, "source": "fallback", "viral_score": 87, "suspense_score": 85},
            {"query": "Why do we sneeze with eyes open", "keyword": "human body mystery", "growth": 440, "source": "fallback", "viral_score": 84, "suspense_score": 82},
            {"query": "What happens when you hold sneeze", "keyword": "human body mystery", "growth": 450, "source": "fallback", "viral_score": 85, "suspense_score": 88},
            {"query": "Brain plasticity visual proof", "keyword": "brain science", "growth": 460, "source": "fallback", "viral_score": 86, "suspense_score": 84},
            {"query": "Déjà vu parallel universe theory", "keyword": "brain mystery", "growth": 500, "source": "fallback", "viral_score": 95, "suspense_score": 94},
            {"query": "Why do we forget names instantly", "keyword": "brain mystery", "growth": 445, "source": "fallback", "viral_score": 85, "suspense_score": 83},
            {"query": "Memory palace brain technique", "keyword": "brain science", "growth": 455, "source": "fallback", "viral_score": 87, "suspense_score": 85},
            {"query": "Why do we itch for no reason", "keyword": "human body mystery", "growth": 430, "source": "fallback", "viral_score": 82, "suspense_score": 80},
            {"query": "What causes brain freeze visually", "keyword": "human body mystery", "growth": 440, "source": "fallback", "viral_score": 84, "suspense_score": 86},
        ]

        for topic in fallbacks:
            topic['pattern'] = self._select_viral_pattern(topic['query'], topic['suspense_score'])

        return fallbacks
