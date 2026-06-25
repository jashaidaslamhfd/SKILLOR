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
                # 10s connect timeout, 25s read timeout
                self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
                print("✅ Google Trends initialized")
            except Exception as e:
                print(f"⚠️ Google Trends init failed: {e}")
        
        # Track used topics to prevent repetition across iterations
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
        # REFINED VIRAL PATTERNS — Memory & Brain Fog Only
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
        # SUSPENSE SCORES — Memory & Brain Fog Specific
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
        # FALLBACK TOPICS - ALL Memory & Brain Fog Focused
        # ============================================================
        self.fallback_topics = [
            {"query": "Why you forget names right after hearing them", "keyword": "memory", "growth": 520, "suspense": 95},
            {"query": "Why you can't remember names you just heard", "keyword": "memory", "growth": 510, "suspense": 94},
            {"query": "Why you walk into a room and forget why", "keyword": "memory", "growth": 500, "suspense": 93},
            {"query": "Why you forget what you were about to do", "keyword": "memory", "growth": 490, "suspense": 92},
            {"query": "Why you keep losing your train of thought", "keyword": "memory", "growth": 485, "suspense": 91},
            {"query": "Why short term memory gets worse after 35", "keyword": "memory", "growth": 480, "suspense": 94},
            {"query": "Why your memory gets worse after 40", "keyword": "memory", "growth": 475, "suspense": 93},
            {"query": "Why you forget things you just read", "keyword": "memory", "growth": 470, "suspense": 90},
            {"query": "Why you forget words while speaking", "keyword": "memory", "growth": 465, "suspense": 89},
            {"query": "Why you forget what you were saying mid-sentence", "keyword": "memory", "growth": 460, "suspense": 88},
            {"query": "What actually causes brain fog in men", "keyword": "brain fog", "growth": 490, "suspense": 93},
            {"query": "Why you feel mentally foggy after 35", "keyword": "brain fog", "growth": 480, "suspense": 91},
            {"query": "Why brain fog happens in adults", "keyword": "brain fog", "growth": 475, "suspense": 90},
            {"query": "Why you feel spaced out and can't focus", "keyword": "brain fog", "growth": 470, "suspense": 89},
            {"query": "What causes brain fog and memory loss", "keyword": "brain fog", "growth": 465, "suspense": 90},
            {"query": "Why men experience cognitive decline after 35", "keyword": "memory", "growth": 460, "suspense": 87},
            {"query": "Why your brain feels slow and tired", "keyword": "brain", "growth": 455, "suspense": 86},
            {"query": "Why your brain deletes memories while you sleep", "keyword": "memory", "growth": 450, "suspense": 88},
            {"query": "Why men forget things more as they age", "keyword": "memory", "growth": 445, "suspense": 87},
            {"query": "Why your brain fog gets worse in the afternoon", "keyword": "brain fog", "growth": 440, "suspense": 86},
        ]

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        """Fetch trending topics from Google Trends with instant 429 fallback switch"""
        trending = []
        
        if not self.pytrends:
            print("⚠️ Google Trends not available, using fallback directly")
            return self._get_fallback_topics()
        
        keywords = self.memory_keywords.copy()
        random.shuffle(keywords)
        
        for keyword in keywords[:5]:
            try:
                print(f"   Fetching live trends for: '{keyword}'")
                time.sleep(random.uniform(2, 4)) # Human-like gap
                
                self.pytrends.build_payload(
                    [keyword],
                    cat=14, # Health category
                    timeframe=timeframe,
                    geo='US'
                )
                
                related = self.pytrends.related_queries()
                
                if related and keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(5).iterrows():
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
                # CRITICAL BUG FIX: Agar 429 block detect ho, to mazeed loops chala kar time waste na karein
                # Seedha loop break kar ke local engine par fallback kar jayein
                print(f"⚠️ Error fetching trend data for '{keyword}': {e}")
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print("🛑 Google Trends API blocked us (Code 429). Instantly switching to Safe Local Fallbacks...")
                    break # Break the loop immediately and return what we have or fallbacks
                continue
        
        filtered = self.filter_dead_topics(trending)
        if not filtered:
            print("⚠️ No live trending data found, serving rich fallback niches.")
            return self._get_fallback_topics()
            
        return filtered

    def _clean_topic(self, query: str) -> str:
        """Clean and format topic text"""
        if not query:
            return ""
        query = re.sub(r'^\d+\s+', '', query)
        query = re.sub(r'\s+(reasons|ways|things|facts|signs|tricks|hacks|tips)\s+', ' ', query)
        
        memory_terms = ['memory', 'forget', 'remember', 'recall', 'brain fog', 'fog', 'mental']
        if not any(term in query.lower() for term in memory_terms):
            query = f"why your memory {query}"
        
        return query.strip().capitalize()

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
        return random.choice(self.viral_patterns['personal_stake'])

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        """Filter out low-quality topics"""
        filtered = []
        for t in topics:
            if t.get('viral_score', 0) < 40 or t.get('suspense_score', 0) < 65:
                continue
            query = t.get('query', '').lower()
            memory_terms = ['memory', 'forget', 'remember', 'recall', 'fog', 'mental']
            if not any(term in query for term in memory_terms):
                continue
            filtered.append(t)
        return filtered

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """Get daily topics with variety"""
        random.seed() # Hard reset seed for dynamic random choice on every cron run
        
        if len(self.used_topics) > 100:
            self.used_topics.clear()
            print("🔄 Cleared used topics cache (limit reached)")
        
        topics = []
        try:
            topics = self.fetch_trending_topics("now 1-d")
        except Exception as e:
            print(f"⚠️ Critical fetch engine crash bypass: {e}")
            topics = self._get_fallback_topics()
            
        # Ensure fallback if topics empty
        if not topics:
            topics = self._get_fallback_topics()
            
        # Sort by best potential performance
        topics.sort(key=lambda x: (x.get('viral_score', 0) + x.get('suspense_score', 50)), reverse=True)
        
        # Remove structural duplicates
        unique = list({t['query']: t for t in topics}.values())
        
        # Filter out fresh ones
        fresh_topics = [t for t in unique if t['query'] not in self.used_topics]
        
        if not fresh_topics:
            self.used_topics.clear()
            fresh_topics = unique[:count]
            
        result_topics = fresh_topics[:count]
        
        # Save to used stack
        for t in result_topics:
            self.used_topics.add(t['query'])
            
        random.shuffle(result_topics)
        return result_topics

    def get_trending_topic(self, specific_topic: str = None) -> str:
        """
        ORCHESTRATOR COMPATIBLE WRAPPER
        Resolves topic into a final string. Returns plain topic query text.
        """
        if specific_topic:
            print(f"🎯 Using manually passed topic: '{specific_topic}'")
            return specific_topic
            
        resolved_list = self.get_daily_topics(count=1)
        if resolved_list and len(resolved_list) > 0:
            final_topic = resolved_list[0].get('query')
            # Extra security layer in case formatting pattern gets appended
            pattern = resolved_list[0].get('pattern', '')
            if pattern and random.random() > 0.5: # 50% chance to mix with viral hooks
                # Extract hook modifier elegantly
                return f"{final_topic} ({pattern.lower()})"
            return final_topic
            
        return "Why short term memory gets worse after 35"

    def _get_fallback_topics(self) -> List[Dict]:
        """Get fallback topics with shuffling variety"""
        fallbacks = self.fallback_topics.copy()
        random.shuffle(fallbacks)
        
        fresh_fallbacks = [t for t in fallbacks if t['query'] not in self.used_topics]
        if not fresh_fallbacks:
            self.used_topics.clear()
            fresh_fallbacks = fallbacks
            
        for t in fresh_fallbacks:
            t['pattern'] = self._select_viral_pattern(t['query'], t.get('suspense', 70))
            t['source'] = 'fallback'
            t['viral_score'] = t.get('viral_score', 85)
            t['suspense_score'] = t.get('suspense', 90)
            
        return fresh_fallbacks

    def get_stats(self) -> Dict:
        return {
            'used_topics_count': len(self.used_topics),
            'fallback_topics_count': len(self.fallback_topics),
            'trending_available': self.pytrends is not None,
        }


if __name__ == "__main__":
    print("🚀 TESTING TOPIC ENGINE (FIXED)\n" + "="*60)
    engine = ViralTopicEngine()
    
    print("\n📊 Resolving direct orchestrator string topic:")
    print(f"👉 Topic: '{engine.get_trending_topic()}'")
    
    print("\n📊 Testing raw structure output:")
    topics = engine.get_daily_topics(count=2)
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic.get('query')} (Source: {topic.get('source')})")
