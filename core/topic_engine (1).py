"""Topic Engine — Audience Matched: USA/UK Males 35-54, Credible Calm Topics"""

import time
import random
from datetime import datetime
from typing import List, Dict
from pytrends.request import TrendReq


class ViralTopicEngine:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

        # AUDIENCE MATCH: 35-54 male USA/UK search keywords
        # These are what this audience actually searches on Google
        self.niche_keywords = [
            "why do i forget things", "sleep problems after 40",
            "brain fog causes", "why am i always tired",
            "stress effects on body", "memory loss after 35",
            "why cant i focus", "cortisol effects men",
            "testosterone after 40", "why do i wake up at 3am",
            "gut brain connection", "why time feels faster",
            "chronic stress symptoms", "why hangovers get worse",
            "decision making brain", "why do i procrastinate",
            "belly fat after 35 men", "brain health after 40",
            "why do i feel anxious for no reason", "autopilot brain",
        ]

        # AUDIENCE MATCH: Viral patterns for 35-54 male
        # These are hooks that make a 40-year-old man stop scrolling
        self.viral_patterns = {
            'personal_aging': [
                "nobody warns men about this after 35",
                "what happens to your brain after 40",
                "this is why you feel different after 35",
                "your body does this differently after 40",
                "men over 35 experience this every day",
            ],
            'daily_problem': [
                "this is why you can't focus anymore",
                "the real reason you're always tired",
                "why you keep forgetting things explained",
                "what's actually causing your brain fog",
                "why you wake up exhausted every morning",
            ],
            'credible_surprise': [
                "doctors don't explain this part",
                "nobody tells you what this actually does",
                "the science behind why this keeps happening",
                "what's really going on when you feel this",
                "the reason is simpler than you think",
            ],
            'personal_stake': [
                "this is happening inside you right now",
                "your brain is doing this as you read this",
                "you experienced this today without knowing",
                "this explains why you feel that way",
                "your body has been doing this for years",
            ],
            'counter_intuitive': [
                "the thing you think helps is making it worse",
                "you've been doing this wrong your whole life",
                "what you believe about this is backwards",
                "the advice you got about this is wrong",
                "this common habit is hurting your brain",
            ],
        }

        # AUDIENCE MATCH: Suspense scores for 35-54 male topics
        # Higher = more personally relevant to this audience
        self.suspense_scores = {
            'memory': 92, 'forget': 90, 'sleep': 95, 'tired': 88,
            'stress': 89, 'brain': 87, 'focus': 86, 'fog': 88,
            'testosterone': 84, 'cortisol': 85, 'aging': 83,
            'belly': 80, 'weight': 79, 'heart': 86, 'anxiety': 87,
            'wake': 91, 'night': 89, 'energy': 82, 'decision': 81,
            'procrastin': 83, 'habit': 80, 'gut': 84, 'time': 78,
        }

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
                            query = str(row['query'])
                            cleaned = self._clean_topic(query)
                            suspense = self._calculate_suspense_score(cleaned)

                            trending.append({
                                'query': cleaned,
                                'keyword': keyword,
                                'growth': float(row.get('value', 0)),
                                'source': 'google_trends',
                                'timestamp': datetime.now().isoformat(),
                                'viral_score': min(100, int(row.get('value', 0))),
                                'suspense_score': suspense,
                                'pattern': self._select_viral_pattern(cleaned, suspense),
                            })
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")
                if "429" in str(e):
                    print("Rate limited, waiting 30s...")
                    time.sleep(30)
                continue

        return trending

    def _clean_topic(self, query: str) -> str:
        import re
        query = re.sub(r'^\d+\s+', '', query)
        query = re.sub(r'\s+(reasons|ways|things|facts|signs|tricks|hacks)\s+', ' ', query)
        query = query.strip()
        return query[0].upper() + query[1:] if query else query

    def _calculate_suspense_score(self, query: str) -> int:
        """Score how relevant this topic is to 35-54 male audience"""
        query_lower = query.lower()
        score = 50

        for keyword, value in self.suspense_scores.items():
            if keyword in query_lower:
                score = max(score, value)

        # Bonus for age-relevant words
        age_words = ['after 35', 'after 40', 'men', 'adult', 'age', 'older']
        personal_words = ['you', 'your', 'why do i', 'why am i', 'why cant']

        for word in age_words:
            if word in query_lower:
                score += 6
        for word in personal_words:
            if word in query_lower:
                score += 4

        return min(100, score)

    def _select_viral_pattern(self, query: str, suspense_score: int) -> str:
        """Select best hook pattern for 35-54 male audience"""
        query_lower = query.lower()

        # Age-related topics = personal aging pattern
        if any(w in query_lower for w in ['after 35', 'after 40', 'men', 'age', 'older']):
            return random.choice(self.viral_patterns['personal_aging'])

        # Sleep/energy/focus = daily problem pattern (very relatable)
        elif any(w in query_lower for w in ['sleep', 'tired', 'focus', 'fog', 'wake', 'energy']):
            return random.choice(self.viral_patterns['daily_problem'])

        # High suspense = credible surprise
        elif suspense_score > 85:
            return random.choice(self.viral_patterns['credible_surprise'])

        # Personal body/brain = personal stake
        elif any(w in query_lower for w in ['your', 'you', 'brain', 'body', 'mind']):
            return random.choice(self.viral_patterns['personal_stake'])

        # Default: counter-intuitive (always works for this audience)
        else:
            return random.choice(self.viral_patterns['counter_intuitive'])

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

        viral_topics.sort(
            key=lambda x: (x.get('viral_score', 0) + x.get('suspense_score', 50)) / 2,
            reverse=True
        )
        unique = list({t['query']: t for t in viral_topics}.values())
        random.shuffle(unique)
        return unique[:count]

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        return [
            t for t in topics
            if (t.get('growth', 0) > 30 or t.get('viral_score', 0) > 30)
            and t.get('suspense_score', 0) > 60
        ]

    def get_topic_angle(self, topic_data: Dict) -> str:
        """AUDIENCE MATCH: Angles that resonate with 35-54 males"""
        base_angles = [
            "why this keeps happening to men after 35",
            "the real science behind what you're experiencing",
            "what nobody explains about this daily problem",
            "how this silently affects your brain every day",
            "the truth about what your body is doing",
            "why this gets worse as you get older",
        ]
        pattern = topic_data.get('pattern', '')
        if pattern:
            return f"{pattern} — {topic_data['query']}"
        return f"{random.choice(base_angles)}: {topic_data['query']}"

    def get_shock_angle(self, topic_data: Dict) -> str:
        """AUDIENCE MATCH: Surprising but credible — not horror"""
        shock_angles = [
            f"your brain is quietly doing this with {topic_data['query']} right now",
            f"what {topic_data['query']} actually does inside your body",
            f"the part of {topic_data['query']} nobody warns you about",
            f"how {topic_data['query']} changes after you turn 35",
            f"what happens in your brain during {topic_data['query']}",
        ]
        return random.choice(shock_angles)

    def get_topic_metadata(self, topic_data: Dict) -> Dict:
        return {
            'topic': topic_data['query'],
            'angle': self.get_topic_angle(topic_data),
            'shock_angle': self.get_shock_angle(topic_data),
            'suspense_score': topic_data.get('suspense_score', 70),
            'viral_score': topic_data.get('viral_score', 50),
            'pattern': topic_data.get('pattern', 'personal_stake'),
            'growth': topic_data.get('growth', 0),
            'source': topic_data.get('source', 'unknown'),
        }

    def _get_fallback_topics(self) -> List[Dict]:
        """
        AUDIENCE MATCH: 40+ fallback topics for 35-54 male USA/UK.
        Every topic here is something a 40-year-old man personally experiences.
        NO horror topics. NO teen shock content. NO clickbait jargon.
        """
        fallbacks = [
            # Memory (Proven — Baby Memory Lost = 1.1K views)
            {"query": "Why you forget names right after hearing them", "keyword": "memory", "growth": 500, "source": "fallback", "viral_score": 95, "suspense_score": 92},
            {"query": "Why you walk into a room and forget why", "keyword": "memory", "growth": 490, "source": "fallback", "viral_score": 93, "suspense_score": 91},
            {"query": "Why short term memory gets worse after 35", "keyword": "memory", "growth": 485, "source": "fallback", "viral_score": 92, "suspense_score": 93},
            {"query": "What actually causes brain fog in adults", "keyword": "brain fog", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 90},
            {"query": "Why stress permanently damages your memory", "keyword": "memory", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 89},
            {"query": "Why you can't remember what you read", "keyword": "memory", "growth": 470, "source": "fallback", "viral_score": 89, "suspense_score": 88},
            {"query": "How your brain deletes memories while you sleep", "keyword": "memory", "growth": 465, "source": "fallback", "viral_score": 88, "suspense_score": 90},

            # Sleep (Massive pain point for 35-54 males)
            {"query": "Why you wake up at 3am every night", "keyword": "sleep", "growth": 510, "source": "fallback", "viral_score": 97, "suspense_score": 95},
            {"query": "Why sleep gets worse after 35 explained", "keyword": "sleep", "growth": 500, "source": "fallback", "viral_score": 95, "suspense_score": 94},
            {"query": "Why you feel tired even after 8 hours sleep", "keyword": "sleep", "growth": 495, "source": "fallback", "viral_score": 94, "suspense_score": 93},
            {"query": "Why you can't fall back asleep at 4am", "keyword": "sleep", "growth": 488, "source": "fallback", "viral_score": 92, "suspense_score": 92},
            {"query": "What poor sleep does to your brain after 40", "keyword": "sleep", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 91},
            {"query": "Why men sleep worse as they get older", "keyword": "sleep", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 90},

            # Stress / Work (Daily reality)
            {"query": "What chronic stress quietly does to your brain", "keyword": "stress", "growth": 490, "source": "fallback", "viral_score": 93, "suspense_score": 91},
            {"query": "Why stress feels physical in your chest", "keyword": "stress", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 89},
            {"query": "Why you feel mentally exhausted but can't sleep", "keyword": "stress", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 90},
            {"query": "What cortisol does to your body every single day", "keyword": "cortisol", "growth": 470, "source": "fallback", "viral_score": 89, "suspense_score": 88},
            {"query": "Why you feel anxious for no reason after 40", "keyword": "anxiety", "growth": 465, "source": "fallback", "viral_score": 88, "suspense_score": 87},
            {"query": "How work stress changes your personality over time", "keyword": "stress", "growth": 460, "source": "fallback", "viral_score": 87, "suspense_score": 86},

            # Focus / Productivity
            {"query": "Why you can't focus for more than 10 minutes", "keyword": "focus", "growth": 485, "source": "fallback", "viral_score": 92, "suspense_score": 90},
            {"query": "Why your brain makes the same mistakes repeatedly", "keyword": "brain", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 88},
            {"query": "What your brain does when you're on autopilot", "keyword": "brain", "growth": 468, "source": "fallback", "viral_score": 89, "suspense_score": 87},
            {"query": "Why procrastination gets worse with age", "keyword": "procrastination", "growth": 460, "source": "fallback", "viral_score": 87, "suspense_score": 85},
            {"query": "Why decisions feel harder after 40", "keyword": "decisions", "growth": 455, "source": "fallback", "viral_score": 86, "suspense_score": 84},

            # Body Changes (Personal + age-relevant)
            {"query": "Why men gain belly fat after 35 explained", "keyword": "body", "growth": 490, "source": "fallback", "viral_score": 93, "suspense_score": 91},
            {"query": "Why your body recovers slower after 35", "keyword": "body", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 89},
            {"query": "Why hangovers get so much worse with age", "keyword": "body", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 88},
            {"query": "What testosterone drop actually feels like after 40", "keyword": "testosterone", "growth": 470, "source": "fallback", "viral_score": 89, "suspense_score": 87},
            {"query": "Why your eyes get worse after 40 explained", "keyword": "body", "growth": 460, "source": "fallback", "viral_score": 87, "suspense_score": 85},
            {"query": "What your heart does when you're under stress", "keyword": "heart", "growth": 465, "source": "fallback", "viral_score": 88, "suspense_score": 86},

            # Gut / Brain Connection
            {"query": "How your gut controls your mood explained", "keyword": "gut", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 88},
            {"query": "Why gut feeling is actually real science", "keyword": "gut", "growth": 468, "source": "fallback", "viral_score": 89, "suspense_score": 87},

            # Time Perception
            {"query": "Why time feels faster as you get older", "keyword": "time", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 89},
            {"query": "Why weekends feel shorter than work days", "keyword": "time", "growth": 460, "source": "fallback", "viral_score": 87, "suspense_score": 85},

            # Kids / Parenting (Proven — Baby Memory Lost 1.1K)
            {"query": "Why babies forget everything before age 3", "keyword": "baby", "growth": 500, "source": "fallback", "viral_score": 95, "suspense_score": 92},
            {"query": "What parents do that affects their kids brain", "keyword": "parenting", "growth": 490, "source": "fallback", "viral_score": 93, "suspense_score": 90},
            {"query": "How stress affects your children without you knowing", "keyword": "parenting", "growth": 480, "source": "fallback", "viral_score": 91, "suspense_score": 89},
            {"query": "Why screen time affects kids brains differently", "keyword": "parenting", "growth": 470, "source": "fallback", "viral_score": 89, "suspense_score": 87},

            # Credible Curiosity (Shareable science)
            {"query": "Why your brain makes decisions before you do", "keyword": "brain", "growth": 485, "source": "fallback", "viral_score": 92, "suspense_score": 90},
            {"query": "Why some people never seem to get tired", "keyword": "brain", "growth": 470, "source": "fallback", "viral_score": 89, "suspense_score": 87},
            {"query": "Why men struggle to ask for help science", "keyword": "psychology", "growth": 465, "source": "fallback", "viral_score": 88, "suspense_score": 86},
            {"query": "What loneliness silently does to the male brain", "keyword": "psychology", "growth": 475, "source": "fallback", "viral_score": 90, "suspense_score": 89},
        ]

        for topic in fallbacks:
            topic['pattern'] = self._select_viral_pattern(topic['query'], topic['suspense_score'])

        return fallbacks
