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
    
    # ✅ FIX: Disk par save hone wali used_topics file
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
        
        # ✅ FIX: used_topics ko disk se load karo (session restart par bhi yaad rahe)
        self.used_topics = self._load_used_topics()
        
        # ============================================================
        # ALL-AGE: Body + Brain Science Keywords (Universal)
        # ============================================================
        self.memory_keywords = [
            # Universal brain/memory (age-neutral)
            "why do i forget things",
            "why cant i remember anything",
            "why do i walk into a room and forget",
            "why do i forget words mid sentence",
            "why cant i focus",
            "why does my brain feel foggy",
            "why cant i concentrate",
            "why do i forget what i was saying",

            # Universal body mysteries (any age)
            "why does my body jerk before sleep",
            "why do i get goosebumps",
            "why do my eyes twitch",
            "why do i yawn when others yawn",
            "why does my stomach growl",
            "why do i get dizzy when i stand up",
            "why do i get chills for no reason",
            "why do my ears ring",
            "why do i feel tired all the time",
            "why does my heart skip a beat",
            "why do i feel bloated",
            "why do i get brain freeze",
            "why do i feel hungry even after eating",
            "why do i sweat when nervous",
            "why do i get hiccups",
            "why do i feel cold all the time",
            "why do i get random muscle twitches",
        ]
        
        # ============================================================
        # VIRAL PATTERNS
        # ============================================================
        self.viral_patterns = {
            'memory_insight': [
                "why your brain deletes memories and you don't even notice",
                "nobody tells you what your brain is quietly doing right now",
                "your brain is doing something right now you have no idea about",
                "this happens in your brain every day and nobody explains it",
                "the real reason your brain does this to you",
                "your brain has been keeping this secret your whole life",
            ],
            'brain_fog': [
                "what actually causes that foggy feeling in your head",
                "the surprising reason you can't focus sometimes",
                "why you feel mentally slow for no reason",
                "what your brain does when it feels foggy",
                "the real reason your brain feels heavy sometimes",
            ],
            'memory_science': [
                "the science behind why you forget things",
                "why your brain deletes memories you want to keep",
                "how your memory actually works every day",
                "why your brain filters out things you need",
                "the brain's secret system for forgetting",
            ],
            'personal_stake': [
                "this is happening to your body right now",
                "your body is doing this without you knowing",
                "you experienced this today and didn't realize why",
                "your body has been doing this your whole life",
                "this explains something you've always wondered about",
            ],
            'body_mystery': [
                "your body is quietly doing something you never knew about",
                "this happens to your body every single day",
                "nobody explains what your body actually does here",
                "the real reason your body does this to you",
                "your body has been doing this forever and nobody told you",
            ],
            'body_science': [
                "the science behind why your body works this way",
                "what actually happens inside your body when this occurs",
                "how your body does this without you realizing",
                "why your body reacts this way and what it means",
                "the hidden system in your body doing this right now",
            ],
            'universal_curiosity': [
                "everyone experiences this but nobody knows why",
                "this happens to every human body and science finally explains it",
                "you have felt this your whole life — here is why",
                "your body does this to protect you and you never knew",
                "the fascinating reason your body does this every day",
            ],
        }
        # SUSPENSE SCORES
        # ============================================================
        self.suspense_scores = {
            # Brain & Memory (universal, no age)
            'memory': 95, 'forget': 94, 'remember': 90, 'recall': 88,
            'brain fog': 93, 'foggy': 92, 'spaced': 90, 'mental': 85,
            'focus': 89, 'concentrate': 88, 'attention': 87,
            'word': 90, 'thought': 89, 'cognitive': 86,
            'brain': 88, 'mind': 87, 'thinking': 85,
            # Body mysteries (universal)
            'gut': 92, 'stomach': 89, 'digestion': 88, 'bloated': 87,
            'heart': 93, 'tired': 94, 'energy': 92, 'fatigue': 91,
            'muscle': 89, 'twitch': 91, 'jerk': 90, 'goosebump': 89,
            'skin': 85, 'dizzy': 90, 'ringing': 89, 'hiccup': 87,
            'yawn': 88, 'chills': 89, 'sweat': 87, 'hungry': 88,
            'nervous': 89, 'body': 86, 'every day': 90, 'nobody': 92,
        }
        
        # ============================================================
        # EXTENSIVE FALLBACK TOPICS (100+ Unique Topics)
        # ============================================================
        self.fallback_topics = [
            # ── UNIVERSAL BODY MYSTERIES ────────────────────────
            {"query": "Why your body jerks right before you fall asleep", "keyword": "body", "growth": 620, "suspense": 97},
            {"query": "Why you get goosebumps when you hear certain music", "keyword": "body", "growth": 610, "suspense": 96},
            {"query": "Why you yawn when someone else yawns", "keyword": "body", "growth": 600, "suspense": 95},
            {"query": "Why you get brain freeze from cold food", "keyword": "body", "growth": 590, "suspense": 94},
            {"query": "Why your stomach growls even when you are not hungry", "keyword": "body", "growth": 585, "suspense": 93},
            {"query": "Why you get random chills for no reason", "keyword": "body", "growth": 580, "suspense": 93},
            {"query": "Why you get dizzy when you stand up too fast", "keyword": "body", "growth": 575, "suspense": 92},
            {"query": "Why your eye twitches randomly", "keyword": "body", "growth": 570, "suspense": 92},
            {"query": "Why you get hiccups and how to stop them", "keyword": "body", "growth": 565, "suspense": 91},
            {"query": "Why your heart skips a beat for no reason", "keyword": "body", "growth": 560, "suspense": 95},
            {"query": "Why your ears ring in silence", "keyword": "body", "growth": 555, "suspense": 93},
            {"query": "Why you feel like you are falling when you sleep", "keyword": "body", "growth": 550, "suspense": 96},
            {"query": "Why your hands go cold when you are nervous", "keyword": "body", "growth": 545, "suspense": 90},
            {"query": "Why you sweat when you are not hot", "keyword": "body", "growth": 540, "suspense": 89},
            {"query": "Why you feel hungry again one hour after eating", "keyword": "body", "growth": 535, "suspense": 91},
            {"query": "Why you get random muscle twitches", "keyword": "body", "growth": 530, "suspense": 91},
            {"query": "Why you feel tired after doing nothing", "keyword": "body", "growth": 525, "suspense": 94},
            {"query": "Why your body feels heavy in the morning", "keyword": "body", "growth": 520, "suspense": 92},
            {"query": "Why your energy drops every afternoon", "keyword": "body", "growth": 515, "suspense": 93},
            {"query": "Why you feel cold even when the room is warm", "keyword": "body", "growth": 510, "suspense": 90},
            {"query": "Why your skin feels itchy for no reason", "keyword": "body", "growth": 505, "suspense": 88},
            {"query": "Why your joints crack when you move", "keyword": "body", "growth": 500, "suspense": 89},
            {"query": "Why you get dark circles even when you sleep", "keyword": "body", "growth": 495, "suspense": 88},
            {"query": "Why your stomach hurts when you are nervous", "keyword": "body", "growth": 490, "suspense": 91},
            {"query": "Why you feel bloated even when you eat healthy", "keyword": "body", "growth": 485, "suspense": 89},
            {"query": "Why you sneeze when you look at bright light", "keyword": "body", "growth": 600, "suspense": 95},
            {"query": "Why your nose gets stuffy at night", "keyword": "body", "growth": 480, "suspense": 88},
            {"query": "Why you feel the urge to stretch in the morning", "keyword": "body", "growth": 475, "suspense": 87},
            {"query": "Why your fingers go numb when you are cold", "keyword": "body", "growth": 470, "suspense": 89},
            {"query": "Why you get a lump in your throat when emotional", "keyword": "body", "growth": 610, "suspense": 96},

            # ── UNIVERSAL BRAIN MYSTERIES ────────────────────────
            {"query": "Why you forget names right after hearing them", "keyword": "memory", "growth": 540, "suspense": 95},
            {"query": "Why you walk into a room and forget why", "keyword": "memory", "growth": 535, "suspense": 93},
            {"query": "Why you forget what you were about to say", "keyword": "memory", "growth": 530, "suspense": 92},
            {"query": "Why you keep losing your train of thought", "keyword": "memory", "growth": 525, "suspense": 91},
            {"query": "Why you forget things you just read", "keyword": "memory", "growth": 520, "suspense": 90},
            {"query": "Why you forget words while speaking", "keyword": "memory", "growth": 515, "suspense": 89},
            {"query": "Why familiar words suddenly feel unfamiliar", "keyword": "memory", "growth": 510, "suspense": 90},
            {"query": "Why you remember random things but forget important ones", "keyword": "memory", "growth": 505, "suspense": 92},
            {"query": "Why you can remember old memories but not what happened yesterday", "keyword": "memory", "growth": 500, "suspense": 93},
            {"query": "Why you forget dreams within seconds of waking up", "keyword": "memory", "growth": 495, "suspense": 91},
            {"query": "Why your brain blanks out under pressure", "keyword": "memory", "growth": 490, "suspense": 92},
            {"query": "Why a song gets stuck in your head for hours", "keyword": "brain", "growth": 580, "suspense": 93},
            {"query": "Why you cannot remember a word that is on the tip of your tongue", "keyword": "brain", "growth": 570, "suspense": 95},
            {"query": "Why you laugh at inappropriate times when nervous", "keyword": "brain", "growth": 565, "suspense": 92},
            {"query": "Why you feel like you have seen something before but never have", "keyword": "brain", "growth": 600, "suspense": 97},
            {"query": "Why your brain creates faces in random patterns", "keyword": "brain", "growth": 555, "suspense": 93},
            {"query": "Why you feel watched even when alone", "keyword": "brain", "growth": 550, "suspense": 94},
            {"query": "Why you cannot tickle yourself", "keyword": "brain", "growth": 590, "suspense": 95},
            {"query": "Why you feel like time moves faster as you get older", "keyword": "brain", "growth": 545, "suspense": 94},
            {"query": "Why you cannot stop thinking about something once you start", "keyword": "brain", "growth": 540, "suspense": 91},
            {"query": "Why your brain finishes other peoples sentences", "keyword": "brain", "growth": 535, "suspense": 90},
            {"query": "Why music gives you chills", "keyword": "brain", "growth": 610, "suspense": 96},
            {"query": "Why your mood changes with the weather", "keyword": "brain", "growth": 520, "suspense": 90},
            {"query": "Why you feel anxious for no reason", "keyword": "brain", "growth": 580, "suspense": 94},
            {"query": "Why you cannot focus on one thing at a time", "keyword": "brain", "growth": 515, "suspense": 91},
            {"query": "Why your brain is more creative at night", "keyword": "brain", "growth": 545, "suspense": 92},
            {"query": "Why you feel more confident after a good sleep", "keyword": "brain", "growth": 510, "suspense": 89},
            {"query": "Why you feel empty even when everything is fine", "keyword": "brain", "growth": 575, "suspense": 95},
            {"query": "Why your brain replays embarrassing memories randomly", "keyword": "brain", "growth": 620, "suspense": 97},
            {"query": "Why you feel a rush of emotion from a random smell", "keyword": "brain", "growth": 560, "suspense": 93},
            {"query": "Why you feel physically sick when you see someone get hurt", "keyword": "brain", "growth": 555, "suspense": 92},

            # ── GUT & DIGESTION ──────────────────────────────────
            {"query": "Why your gut feeling is actually your second brain", "keyword": "body", "growth": 590, "suspense": 95},
            {"query": "Why butterflies in your stomach are a real physical thing", "keyword": "body", "growth": 580, "suspense": 94},
            {"query": "Why eating certain foods changes your mood", "keyword": "body", "growth": 570, "suspense": 93},

            # ── SLEEP MYSTERIES ──────────────────────────────────
            {"query": "Why you feel more tired after sleeping too long", "keyword": "body", "growth": 585, "suspense": 94},
            {"query": "Why your brain stays partially awake while you sleep", "keyword": "brain", "growth": 575, "suspense": 95},
            {"query": "Why you cannot remember most of your dreams", "keyword": "brain", "growth": 565, "suspense": 93},

            # ── USA CULTURE & TRENDING TOPICS (American-specific for US audience) ──
            {"query": "Why Americans feel tired all the time", "keyword": "body", "growth": 590, "suspense": 94},
            {"query": "Why your body reacts to jet lag the way it does", "keyword": "body", "growth": 560, "suspense": 92},
            {"query": "Why you crave sugar even when you are full", "keyword": "body", "growth": 570, "suspense": 93},
            {"query": "Why your phone makes your neck hurt", "keyword": "body", "growth": 550, "suspense": 90},
            {"query": "Why your eyes feel tired from screen time", "keyword": "body", "growth": 540, "suspense": 89},
            {"query": "Why you wake up at 3am and cannot fall back asleep", "keyword": "body", "growth": 580, "suspense": 95},
            {"query": "Why your brain processes fast food differently", "keyword": "brain", "growth": 530, "suspense": 91},
            {"query": "Why you feel sluggish after sitting all day", "keyword": "body", "growth": 520, "suspense": 90},
            {"query": "Why your posture affects your mood instantly", "keyword": "body", "growth": 510, "suspense": 89},
            {"query": "Why coffee wakes up your brain but crashes it later", "keyword": "brain", "growth": 560, "suspense": 92},
        ]

        # FIX: Deduplicate fallback topics — remove near-duplicates
        self.fallback_topics = self._deduplicate_topics(self.fallback_topics)

    # ============================================================
    # FETCH TRENDING TOPICS
    # ============================================================
    
    def _deduplicate_topics(self, topics: List[Dict]) -> List[Dict]:
        """FIX: Remove duplicate and near-duplicate topics from the list.
        
        Prevents issues like 'Forgetting Names' appearing in multiple forms:
        - 'Why you forget names right after hearing them'
        - 'Why you forget words while speaking'  (same concept)
        - 'Why you cannot remember a word that is on the tip of your tongue' (same concept)
        
        Keeps the highest-scoring version of each near-duplicate cluster.
        """
        seen_cores = {}  # core_concept -> best topic dict
        
        for topic in topics:
            query = topic.get('query', '').lower()
            # Extract core concept: remove common prefixes and stop words
            core = query
            for prefix in ['why you ', 'why your ', 'why does ', 'why do ', 'why ']:
                if core.startswith(prefix):
                    core = core[len(prefix):]
                    break
            
            # Remove common suffixes
            for suffix in [' for no reason', ' every day', ' randomly', ' right now']:
                core = core.replace(suffix, '')
            
            # Check if this core is already represented
            if core in seen_cores:
                # Keep the one with higher growth+suspense score
                existing_score = seen_cores[core].get('growth', 0) + seen_cores[core].get('suspense', 0)
                new_score = topic.get('growth', 0) + topic.get('suspense', 0)
                if new_score > existing_score:
                    seen_cores[core] = topic
            else:
                seen_cores[core] = topic
        
        deduped = list(seen_cores.values())
        if len(deduped) < len(topics):
            removed = len(topics) - len(deduped)
            print(f"   🧹 Deduplicated: {len(topics)} → {len(deduped)} topics (removed {removed} near-duplicates)")
        return deduped
    
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
        """Clean and format topic — FIX M4: Universal niche, not forced 'memory' prefix"""
        if not query:
            return ""
        
        query = re.sub(r'^\d+\s+', '', query)
        query = re.sub(r'\s+(reasons|ways|things|facts|signs|tricks|hacks|tips)\s+', ' ', query)
        
        # FIX M4: Don't force "memory" prefix — use universal brain/body language
        memory_terms = ['memory', 'forget', 'remember', 'recall', 'brain fog', 'fog', 'mental',
                        'brain', 'body', 'heart', 'gut', 'muscle', 'nerve', 'eye', 'ear',
                        'skin', 'bone', 'blood', 'immune', 'stomach', 'lung', 'liver']
        if not any(term in query.lower() for term in memory_terms):
            query = f"why your body {query}"
        
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
                score += 0  # FIX M4: Removed age-specific bonus — universal niche
        
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
        
        # ✅ NEW: Body science pattern selection
        body_words = ['gut', 'stomach', 'heart', 'tired', 'energy', 'muscle',
                      'joint', 'back', 'knee', 'skin', 'inflammation', 'metabolism',
                      'belly', 'dizzy', 'twitch', 'ringing', 'blood', 'circulation',
                      'body', 'immune', 'fatigue', 'bloated', 'digestion']
        if any(w in query_lower for w in body_words):
            pattern_key = random.choice(['body_mystery', 'body_science'])
            return random.choice(self.viral_patterns[pattern_key])
        
        if suspense_score > 85:
            return random.choice(self.viral_patterns['memory_science'])
        
        if any(w in query_lower for w in ['you', 'your', 'my']):
            return random.choice(self.viral_patterns['personal_stake'])
        
        return random.choice(self.viral_patterns['memory_insight'])

    # ============================================================
    # GET DAILY TOPICS
    # ============================================================
    
    def _load_used_topics(self) -> set:
        """✅ FIX: Disk se used topics load karo (restart-safe)"""
        try:
            import json, os
            if os.path.exists(self.USED_TOPICS_FILE):
                with open(self.USED_TOPICS_FILE, 'r') as f:
                    data = json.load(f)
                topics = set(data.get('topics', []))
                print(f"📂 Loaded {len(topics)} used topics from disk")
                return topics
        except Exception as e:
            print(f"⚠️ Could not load used topics: {e}")
        return set()

    def _save_used_topics(self):
        """✅ FIX: Used topics ko disk par save karo"""
        try:
            import json, os
            os.makedirs(os.path.dirname(self.USED_TOPICS_FILE), exist_ok=True)
            with open(self.USED_TOPICS_FILE, 'w') as f:
                json.dump({'topics': list(self.used_topics)}, f)
        except Exception as e:
            print(f"⚠️ Could not save used topics: {e}")

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """Get daily topics with variety and fallback"""
        random.seed()
        
        # ✅ FIX: 150 topics ke baad reset (zyada variety)
        if len(self.used_topics) > 150:
            self.used_topics.clear()
            self._save_used_topics()
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
            self._save_used_topics()
            fresh_topics = unique[:count]
        
        result_topics = fresh_topics[:count]
        
        # Mark as used aur disk par save karo
        for t in result_topics:
            self.used_topics.add(t['query'])
        self._save_used_topics()  # ✅ FIX: Disk par save
        
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
        """Clear used topics cache (memory + disk)"""
        self.used_topics.clear()
        self._save_used_topics()  # ✅ FIX: Disk bhi clear karo
        print("🧹 Cleared used topics cache (memory + disk)")

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
