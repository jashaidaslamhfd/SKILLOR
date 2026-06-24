"""
Topic Engine — REFINED: Memory & Brain Fog Only
NICHE: Men 35-54 experiencing memory loss and brain fog
GOAL: Low competition, high demand topics
SOURCE: Google Trends + Fallback topics
"""

import time
import random
import re
from datetime import datetime
from typing import List, Dict, Optional

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None
    print("⚠️ pytrends not installed. Install with: pip install pytrends")


class ViralTopicEngine:
    """Topic Engine for Memory & Brain Fog Niche"""
    
    def __init__(self):
        # Initialize Google Trends
        self.pytrends = None
        if TrendReq:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
                print("✅ Google Trends initialized")
            except Exception as e:
                print(f"⚠️ Google Trends init failed: {e}")
        
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
            "why do i forget where i put things",
            "why do i forget appointments",
            "why do i forget dates",
            "why do i forget conversations",
            "why do i forget people's names",
        ]
        
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
        
        self.suspense_scores = {
            'memory': 95, 'forget': 94, 'remember': 90, 'recall': 88,
            'brain fog': 93, 'foggy': 92, 'spaced': 90, 'mental': 85,
            'focus': 89, 'concentrate': 88, 'attention': 87,
            'name': 92, 'room': 91, 'word': 90, 'thought': 89,
            'short term': 94, 'cognitive': 86, 'decline': 85,
            'after 35': 95, 'after 40': 94, 'men': 90,
            'brain': 88, 'mind': 87, 'thinking': 85,
        }

    def fetch_trending_topics(self, timeframe: str = "now 1-d") -> List[Dict]:
        """Fetch trending topics from Google Trends"""
        trending = []
        
        if not self.pytrends:
            print("⚠️ Google Trends not available, using fallback")
            return self._get_fallback_topics()
        
        keywords = self.memory_keywords.copy()
        random.shuffle(keywords)
        
        for keyword in keywords[:5]:
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
                        for _, row in rising.head(5).iterrows():
                            query = str(row['query'])
                            cleaned = self._clean_topic(query)
                            
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
                print(f"   ⚠️ Error fetching {keyword}: {e}")
                if "429" in str(e):
                    print("   ⏳ Rate limited, waiting 30s...")
                    time.sleep(30)
                continue
        
        filtered = self.filter_dead_topics(trending)
        
        if not filtered:
            print("⚠️ No trending topics found, using fallback")
            return self._get_fallback_topics()
        
        return filtered

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

    def filter_dead_topics(self, topics: List[Dict]) -> List[Dict]:
        """Filter out low-quality topics"""
        filtered = []
        
        for t in topics:
            if t.get('viral_score', 0) < 40:
                continue
            if t.get('suspense_score', 0) < 65:
                continue
            
            query = t.get('query', '').lower()
            memory_terms = ['memory', 'forget', 'remember', 'recall', 'fog', 'mental']
            if not any(term in query for term in memory_terms):
                continue
            
            filtered.append(t)
        
        return filtered

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """Get daily topics with fallback"""
        topics = []
        
        try:
            trending = self.fetch_trending_topics("now 1-d")
            if trending:
                topics = trending
        except Exception as e:
            print(f"⚠️ Google Trends failed: {e}")
        
        if not topics:
            print("⚠️ Using fallback topics")
            topics = self._get_fallback_topics()
        
        topics.sort(key=lambda x: (x.get('viral_score', 0) + x.get('suspense_score', 50)), reverse=True)
        
        unique = list({t['query']: t for t in topics}.values())
        
        random.shuffle(unique)
        
        return unique[:count]

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

    def _get_fallback_topics(self) -> List[Dict]:
        """Fallback topics - ALL memory & brain fog focused"""
        return [
            {
                "query": "Why you forget names right after hearing them",
                "keyword": "memory", "growth": 520, "source": "fallback",
                "viral_score": 95, "suspense_score": 95,
                "pattern": "why your brain deletes memories after 35"
            },
            {
                "query": "Why you can't remember names you just heard",
                "keyword": "memory", "growth": 510, "source": "fallback",
                "viral_score": 94, "suspense_score": 94,
                "pattern": "nobody tells men what memory loss actually feels like"
            },
            {
                "query": "Why you walk into a room and forget why",
                "keyword": "memory", "growth": 500, "source": "fallback",
                "viral_score": 93, "suspense_score": 93,
                "pattern": "your brain is quietly forgetting things right now"
            },
            {
                "query": "Why you forget what you were about to do",
                "keyword": "memory", "growth": 490, "source": "fallback",
                "viral_score": 92, "suspense_score": 92,
                "pattern": "the real reason you forget things after 40"
            },
            {
                "query": "Why you keep losing your train of thought",
                "keyword": "memory", "growth": 485, "source": "fallback",
                "viral_score": 91, "suspense_score": 91,
                "pattern": "doctors don't explain memory loss to men"
            },
            {
                "query": "Why short term memory gets worse after 35",
                "keyword": "memory", "growth": 480, "source": "fallback",
                "viral_score": 90, "suspense_score": 94,
                "pattern": "why your brain filters out memories you need"
            },
            {
                "query": "Why your memory gets worse after 40",
                "keyword": "memory", "growth": 475, "source": "fallback",
                "viral_score": 89, "suspense_score": 93,
                "pattern": "how your memory actually works after 35"
            },
            {
                "query": "Why you forget things you just read",
                "keyword": "memory", "growth": 470, "source": "fallback",
                "viral_score": 88, "suspense_score": 90,
                "pattern": "the science behind why you forget things"
            },
            {
                "query": "Why you forget words while speaking",
                "keyword": "memory", "growth": 465, "source": "fallback",
                "viral_score": 87, "suspense_score": 89,
                "pattern": "your brain is quietly forgetting things right now"
            },
            {
                "query": "Why you forget what you were saying mid-sentence",
                "keyword": "memory", "growth": 460, "source": "fallback",
                "viral_score": 86, "suspense_score": 88,
                "pattern": "the real reason you forget names after 40"
            },
            {
                "query": "What actually causes brain fog in men",
                "keyword": "brain fog", "growth": 490, "source": "fallback",
                "viral_score": 92, "suspense_score": 93,
                "pattern": "what actually causes brain fog in adults"
            },
            {
                "query": "Why you feel mentally foggy after 35",
                "keyword": "brain fog", "growth": 480, "source": "fallback",
                "viral_score": 90, "suspense_score": 91,
                "pattern": "why your brain feels foggy after 35"
            },
            {
                "query": "Why brain fog happens in adults",
                "keyword": "brain fog", "growth": 475, "source": "fallback",
                "viral_score": 89, "suspense_score": 90,
                "pattern": "the surprising reason you can't focus"
            },
            {
                "query": "Why you feel spaced out and can't focus",
                "keyword": "brain fog", "growth": 470, "source": "fallback",
                "viral_score": 88, "suspense_score": 89,
                "pattern": "why you feel mentally exhausted all the time"
            },
            {
                "query": "What causes brain fog and memory loss",
                "keyword": "brain fog", "growth": 465, "source": "fallback",
                "viral_score": 87, "suspense_score": 90,
                "pattern": "what your brain does when you have brain fog"
            },
            {
                "query": "Why men experience cognitive decline after 35",
                "keyword": "memory", "growth": 460, "source": "fallback",
                "viral_score": 86, "suspense_score": 87,
                "pattern": "this is happening to your brain right now"
            },
            {
                "query": "Why your brain feels slow and tired",
                "keyword": "brain", "growth": 455, "source": "fallback",
                "viral_score": 85, "suspense_score": 86,
                "pattern": "your memory is changing without you knowing"
            },
            {
                "query": "Why your brain deletes memories while you sleep",
                "keyword": "memory", "growth": 450, "source": "fallback",
                "viral_score": 84, "suspense_score": 88,
                "pattern": "the brain's secret to forgetting"
            },
            {
                "query": "Why men forget things more as they age",
                "keyword": "memory", "growth": 445, "source": "fallback",
                "viral_score": 83, "suspense_score": 87,
                "pattern": "nobody tells men what memory loss actually feels like"
            },
            {
                "query": "Why your brain fog gets worse in the afternoon",
                "keyword": "brain fog", "growth": 440, "source": "fallback",
                "viral_score": 82, "suspense_score": 86,
                "pattern": "you experienced this today and didn't realize"
            },
        ]
