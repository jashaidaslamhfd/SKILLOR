"""
Topic Engine — REFINED: Memory & Brain Fog Only (FIXED WITH ROBUST 429 FALLBACK)
NICHE: Men 35-54 experiencing memory loss and brain fog
GOAL: Low competition, high demand topics
SOURCE: Google Trends + Fallback topics
"""

import time
import random
import re
import logging
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
    
    def __init__(self):
        # Initialize Google Trends
        self.pytrends = None
        if TrendReq:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
                print("✅ Google Trends initialized")
            except Exception as e:
                print(f"⚠️ Google Trends init failed: {e}")
        
        # Track used topics to prevent repetition
        self.used_topics = set()
        
        # ============================================================
        # REFINED: ONLY Memory & Brain Fog Keywords
        # ============================================================
        self.memory_keywords = [
            "why do i forget names",
            "why do i forget things easily",
            "why can't i remember anything",
            "why is my memory getting worse",
            "why do i walk into a room and forget",
            "why do i forget what i was saying",
            "why can't i remember names",
            "why do i forget words mid sentence",
            "why is my short term memory bad",
            "why do i forget things after 35",
            "why do i forget things after 40",
            "why can't i remember what i read",
            "why do i forget my train of thought",
            
            # Brain Fog
            "what causes brain fog in men",
            "why do i feel spaced out",
            "why can't i focus anymore",
            "why do i feel mentally slow",
            "why is my brain foggy all the time",
            "what causes brain fog after eating",
            "why do i have brain fog in the morning",
            "why does my brain feel foggy",
            "what causes mental fog",
            "why can't i concentrate anymore",
            
            # Memory Specific
            "why do i forget where i put things",
            "why do i forget appointments",
            "why do i forget dates",
            "why do i forget conversations",
            "why do i forget people's names",
        ]
        
        # ============================================================
        # VIRAL PATTERNS
        # ============================================================
        self.viral_patterns = {
            'memory_insight': [
                "why your brain deletes memories after 35",
                "nobody tells men what memory loss actually feels like",
                "your brain is quietly forgetting things right now",
                "the real reason you forget names after 40",
                "doctors don't explain memory loss to men",
            ],
            'brain_fog': [
                "what actually causes brain fog in adults",
                "why your brain feels foggy after 35",
                "the surprising reason you can't focus",
                "why you feel mentally exhausted all the time",
                "what your brain does when you have brain fog",
            ],
            'memory_science': [
                "the science behind why you forget things",
                "why your brain filters out memories you need",
                "how your memory actually works after 35",
                "why short term memory fails as you age",
                "the brain's secret to forgetting",
            ],
            'personal_stake': [
                "this is happening to your brain right now",
                "your memory is changing without you knowing",
                "you experienced this today and didn't realize",
                "your brain has been doing this for years",
                "this explains why you forget names",
            ]
        }
        
        # ============================================================
        # SUSPENSE SCORES
        # ============================================================
        self.suspense_scores = {
            'memory': 95, 'forget': 94, 'remember': 90, 'recall': 88,
            'brain fog': 93, 'foggy': 92, 'spaced': 90, 'mental': 85,
            'focus': 89, 'concentrate': 88, 'attention': 87,
            'name': 92, 'room': 91, 'word': 90, 'thought': 89,
            'short term': 94, 'cognitive': 86, 'decline': 85,
            'after 35': 95, 'after 40': 94, 'men': 90,
            'brain': 88, 'mind': 87, 'thinking': 85,
        }
        
        # ============================================================
        # EXTENSIVE FALLBACK TOPICS (100+ Unique Topics)
        # ============================================================
        self.fallback_topics = [
            # ── MEMORY — FORGETTING ─────────────────────────────
            {"query": "Why you forget names right after hearing them", "keyword": "memory", "growth": 520, "suspense": 95},
            {"query": "Why you walk into a room and forget why", "keyword": "memory", "growth": 500, "suspense": 93},
            {"query": "Why you forget what you were about to do", "keyword": "memory", "growth": 490, "suspense": 92},
            {"query": "Why you keep losing your train of thought", "keyword": "memory", "growth": 485, "suspense": 91},
            {"query": "Why short term memory gets worse after 35", "keyword": "memory", "growth": 480, "suspense": 94},
            {"query": "Why your memory gets worse after 40", "keyword": "memory", "growth": 475, "suspense": 93},
            {"query": "Why you forget things you just read", "keyword": "memory", "growth": 470, "suspense": 90},
            {"query": "Why you forget words while speaking", "keyword": "memory", "growth": 465, "suspense": 89},
            {"query": "Why you forget what you were saying mid-sentence", "keyword": "memory", "growth": 460, "suspense": 88},
            {"query": "Why men forget where they put things", "keyword": "memory", "growth": 455, "suspense": 87},
            {"query": "Why you forget appointments even when you wrote them down", "keyword": "memory", "growth": 450, "suspense": 86},
            {"query": "Why you forget phone numbers you once knew by heart", "keyword": "memory", "growth": 448, "suspense": 85},
            {"query": "Why you forget people's faces after meeting them", "keyword": "memory", "growth": 445, "suspense": 88},
            {"query": "Why you forget what you were just thinking", "keyword": "memory", "growth": 443, "suspense": 87},
            {"query": "Why familiar words suddenly feel unfamiliar", "keyword": "memory", "growth": 440, "suspense": 90},
            {"query": "Why you forget conversations you just had", "keyword": "memory", "growth": 438, "suspense": 88},
            {"query": "Why you re-read the same paragraph and still forget it", "keyword": "memory", "growth": 435, "suspense": 86},
            {"query": "Why your brain blanks out under pressure", "keyword": "memory", "growth": 430, "suspense": 91},
            {"query": "Why you can remember old memories but forget new ones", "keyword": "memory", "growth": 425, "suspense": 92},
            {"query": "Why stress makes you forget things faster", "keyword": "memory", "growth": 422, "suspense": 90},
            {"query": "Why you forget dreams within seconds of waking", "keyword": "memory", "growth": 420, "suspense": 88},
            {"query": "Why multitasking destroys your memory after 40", "keyword": "memory", "growth": 418, "suspense": 87},
            {"query": "Why alcohol erases memories even after small amounts", "keyword": "memory", "growth": 415, "suspense": 89},
            {"query": "Why you remember embarrassing moments forever", "keyword": "memory", "growth": 412, "suspense": 91},
            {"query": "Why negative memories stick stronger than good ones", "keyword": "memory", "growth": 410, "suspense": 90},
            {"query": "Why your memory is sharper in the morning", "keyword": "memory", "growth": 408, "suspense": 86},
            {"query": "Why you can recall song lyrics but forget a name", "keyword": "memory", "growth": 405, "suspense": 93},
            {"query": "Why your brain deletes memories while you sleep", "keyword": "memory", "growth": 450, "suspense": 88},
            {"query": "Why men forget things more as they age", "keyword": "memory", "growth": 445, "suspense": 87},
            {"query": "Why men experience cognitive decline after 35", "keyword": "memory", "growth": 460, "suspense": 87},
            
            # ── BRAIN FOG ──────────────────────────────────────────
            {"query": "What actually causes brain fog in men", "keyword": "brain fog", "growth": 490, "suspense": 93},
            {"query": "Why you feel mentally foggy after 35", "keyword": "brain fog", "growth": 480, "suspense": 91},
            {"query": "Why you feel spaced out and cannot focus", "keyword": "brain fog", "growth": 470, "suspense": 89},
            {"query": "What causes brain fog and memory loss together", "keyword": "brain fog", "growth": 465, "suspense": 90},
            {"query": "Why your brain fog gets worse in the afternoon", "keyword": "brain fog", "growth": 440, "suspense": 86},
            {"query": "Why your thinking feels slower than it used to", "keyword": "brain fog", "growth": 455, "suspense": 88},
            {"query": "Why you feel mentally exhausted without doing much", "keyword": "brain fog", "growth": 452, "suspense": 87},
            {"query": "Why your brain feels like it is running in slow motion", "keyword": "brain fog", "growth": 448, "suspense": 90},
            {"query": "Why you feel disconnected from your own thoughts", "keyword": "brain fog", "growth": 445, "suspense": 89},
            {"query": "Why brain fog gets worse after eating", "keyword": "brain fog", "growth": 442, "suspense": 88},
            {"query": "Why coffee stops working for brain fog after 40", "keyword": "brain fog", "growth": 438, "suspense": 91},
            {"query": "Why your mind goes blank in important meetings", "keyword": "brain fog", "growth": 435, "suspense": 92},
            {"query": "Why brain fog is a sign your body is inflamed", "keyword": "brain fog", "growth": 430, "suspense": 90},
            {"query": "Why dehydration causes immediate brain fog", "keyword": "brain fog", "growth": 428, "suspense": 88},
            {"query": "Why sugar crashes cause mental fog in men over 35", "keyword": "brain fog", "growth": 425, "suspense": 89},
            {"query": "Why screen time makes brain fog worse", "keyword": "brain fog", "growth": 422, "suspense": 87},
            {"query": "Why anxiety and brain fog always come together", "keyword": "brain fog", "growth": 420, "suspense": 88},
            {"query": "Why poor gut health causes brain fog", "keyword": "brain fog", "growth": 418, "suspense": 89},
            
            # ── SLEEP & BRAIN ──────────────────────────────────────
            {"query": "Why men wake up at 3am and cannot go back to sleep", "keyword": "sleep", "growth": 495, "suspense": 94},
            {"query": "Why poor sleep destroys your memory the next day", "keyword": "sleep", "growth": 485, "suspense": 92},
            {"query": "Why you wake up feeling more tired than when you slept", "keyword": "sleep", "growth": 480, "suspense": 91},
            {"query": "Why your brain needs deep sleep to clear toxic waste", "keyword": "sleep", "growth": 475, "suspense": 93},
            {"query": "Why one bad night of sleep makes you 40 percent less sharp", "keyword": "sleep", "growth": 470, "suspense": 95},
            {"query": "Why men sleep lighter as they get older", "keyword": "sleep", "growth": 465, "suspense": 89},
            {"query": "Why you dream less as you age and what it means", "keyword": "sleep", "growth": 460, "suspense": 88},
            {"query": "Why you cannot nap even when exhausted", "keyword": "sleep", "growth": 455, "suspense": 87},
            {"query": "Why your brain replays the day while you sleep", "keyword": "sleep", "growth": 450, "suspense": 90},
            {"query": "Why alcohol ruins your sleep quality even if you fall asleep fast", "keyword": "sleep", "growth": 445, "suspense": 91},
            {"query": "Why screen light before bed damages your memory", "keyword": "sleep", "growth": 435, "suspense": 88},
            {"query": "Why snoring is quietly destroying your brain", "keyword": "sleep", "growth": 430, "suspense": 92},
            {"query": "Why sleep deprivation looks exactly like early dementia", "keyword": "sleep", "growth": 428, "suspense": 94},
            {"query": "Why your body temperature controls how deep you sleep", "keyword": "sleep", "growth": 425, "suspense": 87},
            {"query": "Why sleeping less than 6 hours accelerates brain aging", "keyword": "sleep", "growth": 422, "suspense": 90},
            
            # ── FOCUS ──────────────────────────────────────────────
            {"query": "Why men cannot focus for more than 20 minutes after 40", "keyword": "focus", "growth": 488, "suspense": 92},
            {"query": "Why your attention span gets shorter every year", "keyword": "focus", "growth": 482, "suspense": 91},
            {"query": "Why you lose focus the moment something gets difficult", "keyword": "focus", "growth": 478, "suspense": 90},
            {"query": "Why your brain craves distraction when you need to focus", "keyword": "focus", "growth": 475, "suspense": 91},
            {"query": "Why dopamine addiction makes focusing impossible", "keyword": "focus", "growth": 470, "suspense": 92},
            {"query": "Why you can hyper focus on things you enjoy but not work", "keyword": "focus", "growth": 465, "suspense": 90},
            {"query": "Why background noise destroys your concentration after 35", "keyword": "focus", "growth": 460, "suspense": 88},
            {"query": "Why your brain takes 23 minutes to refocus after interruption", "keyword": "focus", "growth": 455, "suspense": 91},
            {"query": "Why afternoon is the worst time for deep thinking", "keyword": "focus", "growth": 450, "suspense": 87},
            {"query": "Why your focus collapses when you are slightly hungry", "keyword": "focus", "growth": 445, "suspense": 89},
            {"query": "Why chronic stress permanently reduces your focus", "keyword": "focus", "growth": 440, "suspense": 90},
            {"query": "Why exercise boosts focus better than caffeine", "keyword": "focus", "growth": 435, "suspense": 88},
            {"query": "Why your phone is rewiring your focus circuits", "keyword": "focus", "growth": 430, "suspense": 92},
            {"query": "Why silence is the most powerful focus tool your brain has", "keyword": "focus", "growth": 420, "suspense": 87},
            
            # ── AGING BRAIN ─────────────────────────────────────────
            {"query": "Why your reaction time slows down after 40", "keyword": "aging", "growth": 472, "suspense": 89},
            {"query": "Why your brain starts shrinking at 35 and what stops it", "keyword": "aging", "growth": 468, "suspense": 93},
            {"query": "Why learning new things gets harder after 40", "keyword": "aging", "growth": 462, "suspense": 90},
            {"query": "Why your vocabulary feels smaller than it used to", "keyword": "aging", "growth": 458, "suspense": 88},
            {"query": "Why processing speed drops in your 40s", "keyword": "aging", "growth": 455, "suspense": 87},
            {"query": "Why men become more forgetful in their 40s than women", "keyword": "aging", "growth": 450, "suspense": 89},
            {"query": "Why your brain needs more recovery time after 40", "keyword": "aging", "growth": 445, "suspense": 86},
            {"query": "Why men lose 1 percent of brain volume every year after 40", "keyword": "aging", "growth": 440, "suspense": 92},
            {"query": "Why testosterone drop affects memory in men over 40", "keyword": "aging", "growth": 430, "suspense": 91},
            {"query": "Why the brain is most vulnerable to aging between 45 and 55", "keyword": "aging", "growth": 428, "suspense": 90},
            {"query": "Why exercise is the only proven way to slow brain aging", "keyword": "aging", "growth": 425, "suspense": 89},
            {"query": "Why social isolation accelerates brain aging in men", "keyword": "aging", "growth": 422, "suspense": 88},
            
            # ── STRESS ──────────────────────────────────────────────
            {"query": "Why chronic stress physically shrinks your brain", "keyword": "stress", "growth": 485, "suspense": 93},
            {"query": "Why cortisol destroys memory in men over 35", "keyword": "stress", "growth": 478, "suspense": 92},
            {"query": "Why your mind races at night but goes blank during the day", "keyword": "stress", "growth": 472, "suspense": 91},
            {"query": "Why anxiety makes your memory worse", "keyword": "stress", "growth": 468, "suspense": 90},
            {"query": "Why high achievers are most at risk of brain burnout", "keyword": "stress", "growth": 462, "suspense": 92},
            {"query": "Why financial stress causes the same brain damage as trauma", "keyword": "stress", "growth": 458, "suspense": 93},
            {"query": "Why men bottle up stress and what it does to the brain", "keyword": "stress", "growth": 455, "suspense": 91},
            {"query": "Why work stress after 40 hits different than in your 30s", "keyword": "stress", "growth": 450, "suspense": 89},
        ]

    # ============================================================
    # FETCH TRENDING TOPICS
    # ============================================================
    
    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        """Fetch trending topics from Google Trends with rate limit handling"""
        trending = []
        
        if not self.pytrends:
            print("⚠️ Google Trends not available, using fallback")
            return self._get_fallback_topics()
        
        # Only fetch 3 keywords per run to avoid rate limits
        keywords = self.memory_keywords.copy()
        random.shuffle(keywords)
        keywords_to_fetch = keywords[:3]
        
        print(f"   🔍 Fetching {len(keywords_to_fetch)} keywords from Google Trends...")
        
        for keyword in keywords_to_fetch:
            try:
                print(f"   Fetching trends for: {keyword}")
                time.sleep(random.uniform(2, 4))
                
                self.pytrends.build_payload(
                    [keyword],
                    cat=14,
                    timeframe=timeframe,
                    geo='US'
                )
                
                related = self.pytrends.related_queries()
                
                if related and keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(3).iterrows():
                            query = str(row['query'])
                            cleaned = self._clean_topic(query)
                            
                            if cleaned in self.used_topics:
                                continue
                            
                            suspense = self._calculate_suspense_score(cleaned)
                            viral_score = int(row.get('value', 50))
                            
                            trending.append({
                                'query': cleaned,
                                'keyword': keyword,
                                'growth': float(row.get('value', 0)),
                                'source': 'google_trends',
                                'timestamp': datetime.now().isoformat(),
                                'viral_score': min(100, viral_score + 20),
                                'suspense_score': suspense,
                                'pattern': self._select_viral_pattern(cleaned, suspense),
                            })
                            
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    print(f"   ⚠️ Rate limited, waiting 60s...")
                    time.sleep(60)
                else:
                    print(f"   ⚠️ Error fetching {keyword}: {e}")
                continue
        
        if not trending:
            print("⚠️ No trending topics found, using fallback")
            return self._get_fallback_topics()
        
        return trending

    # ============================================================
    # CLEAN TOPICS
    # ============================================================
    
    def _clean_topic(self, query: str) -> str:
        """Clean and format topic"""
        if not query:
            return ""
        
        query = re.sub(r'^\d+\s+', '', query)
        query = re.sub(r'\s+(reasons|ways|things|facts|signs|tricks|hacks|tips)\s+', ' ', query)
        
        memory_terms = ['memory', 'forget', 'remember', 'recall', 'brain fog', 'fog', 'mental']
        if not any(term in query.lower() for term in memory_terms):
            query = f"why your memory {query}"
        
        return query.strip().capitalize()

    # ============================================================
    # CALCULATE SCORES
    # ============================================================
    
    def _calculate_suspense_score(self, query: str) -> int:
        """Calculate how relevant this topic is to memory/brain fog"""
        query_lower = query.lower()
        score = 50
        
        for keyword, value in self.suspense_scores.items():
            if keyword in query_lower:
                score = max(score, value)
        
        age_words = ['after 35', 'after 40', 'men', 'adult', 'older', 'age']
        for word in age_words:
            if word in query_lower:
                score += 5
        
        personal_words = ['you', 'your', 'why do i', 'why am i', 'why cant']
        for word in personal_words:
            if word in query_lower:
                score += 3
        
        return min(100, score)

    def _select_viral_pattern(self, query: str, suspense_score: int) -> str:
        """Select best viral pattern for the topic"""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ['brain fog', 'foggy', 'spaced', 'mental']):
            return random.choice(self.viral_patterns['brain_fog'])
        
        if any(w in query_lower for w in ['memory', 'forget', 'remember', 'recall']):
            return random.choice(self.viral_patterns['memory_insight'])
        
        if suspense_score > 85:
            return random.choice(self.viral_patterns['memory_science'])
        
        if any(w in query_lower for w in ['you', 'your', 'my']):
            return random.choice(self.viral_patterns['personal_stake'])
        
        return random.choice(self.viral_patterns['memory_insight'])

    # ============================================================
    # GET DAILY TOPICS
    # ============================================================
    
    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """Get daily topics with variety and fallback"""
        random.seed()
        
        # Clear used topics if too many
        if len(self.used_topics) > 100:
            self.used_topics.clear()
            print("🔄 Cleared used topics cache (limit reached)")
        
        topics = []
        
        # Try Google Trends (reduced calls)
        try:
            trending = self.fetch_trending_topics("now 1-d")
            if trending:
                topics = trending
        except Exception as e:
            print(f"⚠️ Google Trends failed: {e}")
        
        # If no topics, use fallback
        if not topics:
            print("⚠️ Using fallback topics")
            topics = self._get_fallback_topics()
        
        # Sort by viral score
        topics.sort(key=lambda x: (x.get('viral_score', 0) + x.get('suspense_score', 50)), reverse=True)
        unique = list({t['query']: t for t in topics}.values())
        
        # Filter used topics
        fresh_topics = [t for t in unique if t['query'] not in self.used_topics]
        
        if not fresh_topics and self.used_topics:
            self.used_topics.clear()
            fresh_topics = unique[:count]
        
        result_topics = fresh_topics[:count]
        
        # Mark as used
        for t in result_topics:
            self.used_topics.add(t['query'])
        
        random.shuffle(result_topics)
        
        return result_topics

    # ============================================================
    # FALLBACK TOPICS
    # ============================================================
    
    def _get_fallback_topics(self) -> List[Dict]:
        """Get fallback topics with variety"""
        fallbacks = self.fallback_topics.copy()
        random.shuffle(fallbacks)
        
        fresh_fallbacks = [t for t in fallbacks if t['query'] not in self.used_topics]
        
        if not fresh_fallbacks and self.used_topics:
            self.used_topics.clear()
            fresh_fallbacks = fallbacks
        
        for t in fresh_fallbacks:
            t['pattern'] = self._select_viral_pattern(t['query'], t.get('suspense', 70))
            t['source'] = 'fallback'
            t['viral_score'] = t.get('viral_score', 80)
        
        return fresh_fallbacks

    # ============================================================
    # GET TOPIC METADATA
    # ============================================================
    
    def get_topic_metadata(self, topic_data: Dict) -> Dict:
        """Return enriched metadata for a topic"""
        query = topic_data.get('query', '')
        suspense = self._calculate_suspense_score(query)
        pattern = self._select_viral_pattern(query, suspense)
        
        return {
            'query': query,
            'suspense_score': suspense,
            'viral_pattern': pattern,
            'keywords': [k for k in self.suspense_scores.keys() if k in query.lower()][:5],
            'estimated_views': '10K-100K',
            'difficulty': 'low',
            'timestamp': datetime.now().isoformat(),
        }

    def clear_used_topics(self):
        """Clear used topics cache"""
        self.used_topics.clear()
        print("🧹 Cleared used topics cache")

    def get_stats(self) -> Dict:
        """Get topic engine statistics"""
        return {
            'used_topics_count': len(self.used_topics),
            'fallback_topics_count': len(self.fallback_topics),
            'memory_keywords_count': len(self.memory_keywords),
            'trending_available': self.pytrends is not None,
        }


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING TOPIC ENGINE\n" + "="*60)
    
    engine = ViralTopicEngine()
    
    print("\n📊 Fetching 5 topics...")
    topics = engine.get_daily_topics(count=5)
    
    print(f"\n✅ Found {len(topics)} topics:\n")
    
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic.get('query')}")
        print(f"   Viral Score: {topic.get('viral_score', 0)}")
        print(f"   Suspense Score: {topic.get('suspense_score', 0)}")
        print(f"   Pattern: {topic.get('pattern', 'unknown')}")
        print(f"   Source: {topic.get('source', 'unknown')}")
        print()
    
    print("\n📊 STATS:")
    print(engine.get_stats())
    
    print("\n" + "="*60)
    print("✅ Topic Engine ready!")
