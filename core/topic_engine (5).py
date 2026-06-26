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
            # ── MEMORY — FORGETTING ───────────────────────────────────────────
            {"query": "Why you forget names right after hearing them",                    "keyword": "memory",    "growth": 520, "suspense": 95},
            {"query": "Why you walk into a room and forget why",                          "keyword": "memory",    "growth": 500, "suspense": 93},
            {"query": "Why you forget what you were about to do",                         "keyword": "memory",    "growth": 490, "suspense": 92},
            {"query": "Why you keep losing your train of thought",                        "keyword": "memory",    "growth": 485, "suspense": 91},
            {"query": "Why short term memory gets worse after 35",                        "keyword": "memory",    "growth": 480, "suspense": 94},
            {"query": "Why your memory gets worse after 40",                              "keyword": "memory",    "growth": 475, "suspense": 93},
            {"query": "Why you forget things you just read",                              "keyword": "memory",    "growth": 470, "suspense": 90},
            {"query": "Why you forget words while speaking",                              "keyword": "memory",    "growth": 465, "suspense": 89},
            {"query": "Why you forget what you were saying mid-sentence",                 "keyword": "memory",    "growth": 460, "suspense": 88},
            {"query": "Why men forget where they put things",                             "keyword": "memory",    "growth": 455, "suspense": 87},
            {"query": "Why you forget appointments even when you wrote them down",        "keyword": "memory",    "growth": 450, "suspense": 86},
            {"query": "Why you forget phone numbers you once knew by heart",              "keyword": "memory",    "growth": 448, "suspense": 85},
            {"query": "Why you forget people faces after meeting them",                   "keyword": "memory",    "growth": 445, "suspense": 88},
            {"query": "Why you forget what you were just thinking",                       "keyword": "memory",    "growth": 443, "suspense": 87},
            {"query": "Why familiar words suddenly feel unfamiliar",                      "keyword": "memory",    "growth": 440, "suspense": 90},
            {"query": "Why you forget conversations you just had",                        "keyword": "memory",    "growth": 438, "suspense": 88},
            {"query": "Why you re-read the same paragraph and still forget it",          "keyword": "memory",    "growth": 435, "suspense": 86},
            {"query": "Why your brain blanks out under pressure",                         "keyword": "memory",    "growth": 430, "suspense": 91},
            {"query": "Why you can remember old memories but forget new ones",            "keyword": "memory",    "growth": 425, "suspense": 92},
            {"query": "Why stress makes you forget things faster",                        "keyword": "memory",    "growth": 422, "suspense": 90},
            {"query": "Why you forget dreams within seconds of waking",                   "keyword": "memory",    "growth": 420, "suspense": 88},
            {"query": "Why multitasking destroys your memory after 40",                   "keyword": "memory",    "growth": 418, "suspense": 87},
            {"query": "Why alcohol erases memories even after small amounts",             "keyword": "memory",    "growth": 415, "suspense": 89},
            {"query": "Why you remember embarrassing moments forever",                    "keyword": "memory",    "growth": 412, "suspense": 91},
            {"query": "Why negative memories stick stronger than good ones",              "keyword": "memory",    "growth": 410, "suspense": 90},
            {"query": "Why your memory is sharper in the morning",                        "keyword": "memory",    "growth": 408, "suspense": 86},
            {"query": "Why you can recall song lyrics but forget a name",                 "keyword": "memory",    "growth": 405, "suspense": 93},
            {"query": "Why your brain deletes memories while you sleep",                  "keyword": "memory",    "growth": 450, "suspense": 88},
            {"query": "Why men forget things more as they age",                           "keyword": "memory",    "growth": 445, "suspense": 87},
            {"query": "Why men experience cognitive decline after 35",                    "keyword": "memory",    "growth": 460, "suspense": 87},
            # ── BRAIN FOG ─────────────────────────────────────────────────────
            {"query": "What actually causes brain fog in men",                            "keyword": "brain fog", "growth": 490, "suspense": 93},
            {"query": "Why you feel mentally foggy after 35",                             "keyword": "brain fog", "growth": 480, "suspense": 91},
            {"query": "Why you feel spaced out and cannot focus",                         "keyword": "brain fog", "growth": 470, "suspense": 89},
            {"query": "What causes brain fog and memory loss together",                   "keyword": "brain fog", "growth": 465, "suspense": 90},
            {"query": "Why your brain fog gets worse in the afternoon",                   "keyword": "brain fog", "growth": 440, "suspense": 86},
            {"query": "Why your thinking feels slower than it used to",                   "keyword": "brain fog", "growth": 455, "suspense": 88},
            {"query": "Why you feel mentally exhausted without doing much",               "keyword": "brain fog", "growth": 452, "suspense": 87},
            {"query": "Why your brain feels like it is running in slow motion",           "keyword": "brain fog", "growth": 448, "suspense": 90},
            {"query": "Why you feel disconnected from your own thoughts",                 "keyword": "brain fog", "growth": 445, "suspense": 89},
            {"query": "Why brain fog gets worse after eating",                            "keyword": "brain fog", "growth": 442, "suspense": 88},
            {"query": "Why coffee stops working for brain fog after 40",                  "keyword": "brain fog", "growth": 438, "suspense": 91},
            {"query": "Why your mind goes blank in important meetings",                   "keyword": "brain fog", "growth": 435, "suspense": 92},
            {"query": "Why brain fog is a sign your body is inflamed",                    "keyword": "brain fog", "growth": 430, "suspense": 90},
            {"query": "Why dehydration causes immediate brain fog",                       "keyword": "brain fog", "growth": 428, "suspense": 88},
            {"query": "Why sugar crashes cause mental fog in men over 35",                "keyword": "brain fog", "growth": 425, "suspense": 89},
            {"query": "Why screen time makes brain fog worse",                            "keyword": "brain fog", "growth": 422, "suspense": 87},
            {"query": "Why anxiety and brain fog always come together",                   "keyword": "brain fog", "growth": 420, "suspense": 88},
            {"query": "Why poor gut health causes brain fog",                             "keyword": "brain fog", "growth": 418, "suspense": 89},
            # ── SLEEP & BRAIN ─────────────────────────────────────────────────
            {"query": "Why men wake up at 3am and cannot go back to sleep",              "keyword": "sleep",     "growth": 495, "suspense": 94},
            {"query": "Why poor sleep destroys your memory the next day",                "keyword": "sleep",     "growth": 485, "suspense": 92},
            {"query": "Why you wake up feeling more tired than when you slept",          "keyword": "sleep",     "growth": 480, "suspense": 91},
            {"query": "Why your brain needs deep sleep to clear toxic waste",             "keyword": "sleep",     "growth": 475, "suspense": 93},
            {"query": "Why one bad night of sleep makes you 40 percent less sharp",      "keyword": "sleep",     "growth": 470, "suspense": 95},
            {"query": "Why men sleep lighter as they get older",                          "keyword": "sleep",     "growth": 465, "suspense": 89},
            {"query": "Why you dream less as you age and what it means",                 "keyword": "sleep",     "growth": 460, "suspense": 88},
            {"query": "Why you cannot nap even when exhausted",                          "keyword": "sleep",     "growth": 455, "suspense": 87},
            {"query": "Why your brain replays the day while you sleep",                  "keyword": "sleep",     "growth": 450, "suspense": 90},
            {"query": "Why alcohol ruins your sleep quality even if you fall asleep fast","keyword": "sleep",    "growth": 445, "suspense": 91},
            {"query": "Why screen light before bed damages your memory",                 "keyword": "sleep",     "growth": 435, "suspense": 88},
            {"query": "Why snoring is quietly destroying your brain",                    "keyword": "sleep",     "growth": 430, "suspense": 92},
            {"query": "Why sleep deprivation looks exactly like early dementia",         "keyword": "sleep",     "growth": 428, "suspense": 94},
            {"query": "Why your body temperature controls how deep you sleep",           "keyword": "sleep",     "growth": 425, "suspense": 87},
            {"query": "Why sleeping less than 6 hours accelerates brain aging",          "keyword": "sleep",     "growth": 422, "suspense": 90},
            # ── FOCUS & CONCENTRATION ─────────────────────────────────────────
            {"query": "Why men cannot focus for more than 20 minutes after 40",          "keyword": "focus",     "growth": 488, "suspense": 92},
            {"query": "Why your attention span gets shorter every year",                 "keyword": "focus",     "growth": 482, "suspense": 91},
            {"query": "Why you lose focus the moment something gets difficult",          "keyword": "focus",     "growth": 478, "suspense": 90},
            {"query": "Why your brain craves distraction when you need to focus",        "keyword": "focus",     "growth": 475, "suspense": 91},
            {"query": "Why dopamine addiction makes focusing impossible",                "keyword": "focus",     "growth": 470, "suspense": 92},
            {"query": "Why you can hyper focus on things you enjoy but not work",        "keyword": "focus",     "growth": 465, "suspense": 90},
            {"query": "Why background noise destroys your concentration after 35",       "keyword": "focus",     "growth": 460, "suspense": 88},
            {"query": "Why your brain takes 23 minutes to refocus after interruption",   "keyword": "focus",     "growth": 455, "suspense": 91},
            {"query": "Why afternoon is the worst time for deep thinking",               "keyword": "focus",     "growth": 450, "suspense": 87},
            {"query": "Why your focus collapses when you are slightly hungry",           "keyword": "focus",     "growth": 445, "suspense": 89},
            {"query": "Why chronic stress permanently reduces your focus",               "keyword": "focus",     "growth": 440, "suspense": 90},
            {"query": "Why exercise boosts focus better than caffeine",                  "keyword": "focus",     "growth": 435, "suspense": 88},
            {"query": "Why your phone is rewiring your focus circuits",                  "keyword": "focus",     "growth": 430, "suspense": 92},
            {"query": "Why silence is the most powerful focus tool your brain has",      "keyword": "focus",     "growth": 420, "suspense": 87},
            # ── AGING BRAIN ───────────────────────────────────────────────────
            {"query": "Why your reaction time slows down after 40",                      "keyword": "aging",     "growth": 472, "suspense": 89},
            {"query": "Why your brain starts shrinking at 35 and what stops it",         "keyword": "aging",     "growth": 468, "suspense": 93},
            {"query": "Why learning new things gets harder after 40",                    "keyword": "aging",     "growth": 462, "suspense": 90},
            {"query": "Why your vocabulary feels smaller than it used to",               "keyword": "aging",     "growth": 458, "suspense": 88},
            {"query": "Why processing speed drops in your 40s",                          "keyword": "aging",     "growth": 455, "suspense": 87},
            {"query": "Why men become more forgetful in their 40s than women",           "keyword": "aging",     "growth": 450, "suspense": 89},
            {"query": "Why your brain needs more recovery time after 40",                "keyword": "aging",     "growth": 445, "suspense": 86},
            {"query": "Why men lose 1 percent of brain volume every year after 40",      "keyword": "aging",     "growth": 440, "suspense": 92},
            {"query": "Why testosterone drop affects memory in men over 40",             "keyword": "aging",     "growth": 430, "suspense": 91},
            {"query": "Why the brain is most vulnerable to aging between 45 and 55",    "keyword": "aging",     "growth": 428, "suspense": 90},
            {"query": "Why exercise is the only proven way to slow brain aging",         "keyword": "aging",     "growth": 425, "suspense": 89},
            {"query": "Why social isolation accelerates brain aging in men",             "keyword": "aging",     "growth": 422, "suspense": 88},
            # ── STRESS & ANXIETY ──────────────────────────────────────────────
            {"query": "Why chronic stress physically shrinks your brain",                "keyword": "stress",    "growth": 485, "suspense": 93},
            {"query": "Why cortisol destroys memory in men over 35",                     "keyword": "stress",    "growth": 478, "suspense": 92},
            {"query": "Why your mind races at night but goes blank during the day",      "keyword": "stress",    "growth": 472, "suspense": 91},
            {"query": "Why anxiety makes your memory worse",                             "keyword": "stress",    "growth": 468, "suspense": 90},
            {"query": "Why high achievers are most at risk of brain burnout",            "keyword": "stress",    "growth": 462, "suspense": 92},
            {"query": "Why financial stress causes the same brain damage as trauma",     "keyword": "stress",    "growth": 458, "suspense": 93},
            {"query": "Why men bottle up stress and what it does to the brain",          "keyword": "stress",    "growth": 455, "suspense": 91},
            {"query": "Why work stress after 40 hits different than in your 30s",        "keyword": "stress",    "growth": 450, "suspense": 89},
            {"query": "Why your brain stays in fight mode long after stress ends",       "keyword": "stress",    "growth": 445, "suspense": 90},
            {"query": "Why meditation physically changes the stressed brain",            "keyword": "stress",    "growth": 440, "suspense": 88},
            # ── NUTRITION & BRAIN ─────────────────────────────────────────────
            {"query": "Why what you eat for breakfast determines your memory all day",   "keyword": "nutrition", "growth": 475, "suspense": 90},
            {"query": "Why omega-3 deficiency causes memory loss in men",                "keyword": "nutrition", "growth": 468, "suspense": 89},
            {"query": "Why ultra-processed food causes brain fog within hours",          "keyword": "nutrition", "growth": 462, "suspense": 91},
            {"query": "Why vitamin B12 deficiency mimics early dementia",                "keyword": "nutrition", "growth": 458, "suspense": 92},
            {"query": "Why your gut microbiome controls your memory and mood",           "keyword": "nutrition", "growth": 455, "suspense": 90},
            {"query": "Why intermittent fasting boosts brain clarity",                   "keyword": "nutrition", "growth": 450, "suspense": 88},
            {"query": "Why magnesium deficiency causes anxiety and poor memory",         "keyword": "nutrition", "growth": 445, "suspense": 89},
            {"query": "Why dehydration by 2 percent crashes your cognition",             "keyword": "nutrition", "growth": 440, "suspense": 88},
            {"query": "Why creatine is the most overlooked brain supplement",            "keyword": "nutrition", "growth": 435, "suspense": 87},
            {"query": "Why the Mediterranean diet reduces dementia risk by 35 percent",  "keyword": "nutrition", "growth": 430, "suspense": 90},
            {"query": "Why eating too little protein causes brain fog in men over 40",    "keyword": "nutrition", "growth": 425, "suspense": 88},
            # ── BRAIN SCIENCE — INTERESTING FACTS ────────────────────────────
            {"query": "Why your brain uses 20 percent of your body energy",              "keyword": "brain",     "growth": 468, "suspense": 91},
            {"query": "Why your brain shrinks when you stop challenging it",              "keyword": "brain",     "growth": 462, "suspense": 92},
            {"query": "Why boredom is one of the most dangerous states for your brain",  "keyword": "brain",     "growth": 458, "suspense": 90},
            {"query": "Why your brain is more creative when you are slightly tired",     "keyword": "brain",     "growth": 452, "suspense": 89},
            {"query": "Why walking outside is better for your brain than the gym",       "keyword": "brain",     "growth": 448, "suspense": 88},
            {"query": "Why music you loved at 15 stays in your memory forever",          "keyword": "brain",     "growth": 445, "suspense": 91},
            {"query": "Why loneliness physically damages the male brain after 40",       "keyword": "brain",     "growth": 440, "suspense": 92},
            {"query": "Why your brain makes worse decisions when you are cold",          "keyword": "brain",     "growth": 435, "suspense": 89},
            {"query": "Why laughing is one of the best workouts for your brain",         "keyword": "brain",     "growth": 430, "suspense": 87},
            {"query": "Why reading a real book rewires your brain in 6 minutes",         "keyword": "brain",     "growth": 428, "suspense": 88},
            {"query": "Why your brain is actually most active when you do nothing",      "keyword": "brain",     "growth": 425, "suspense": 90},
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

    # ── KEYWORD FINGERPRINT ─────────────────────────────────────────────────
    # "Why you forget names right after hearing them" aur
    # "Why you can't remember names you just heard" — dono ka fingerprint = "forget_names"
    # Is se same topic ki variations bar bar nahi aayengi

    _KEYWORD_FINGERPRINTS = {
        "forget name":      "forget_names",
        "remember name":    "forget_names",
        "names you just":   "forget_names",
        "forget why":       "forget_room",
        "walk into a room": "forget_room",
        "train of thought": "train_of_thought",
        "short term memory":"short_term_memory",
        "memory gets worse":"memory_worse_age",
        "forget things you just read": "forget_reading",
        "forget words while": "forget_words",
        "mid-sentence":     "mid_sentence",
        "brain fog":        "brain_fog",
        "mentally foggy":   "brain_fog",
        "spaced out":       "brain_fog",
        "feel slow":        "brain_slow",
        "brain feels slow": "brain_slow",
        "wake up at 3":     "wake_3am",
        "3am":              "wake_3am",
        "deep sleep":       "deep_sleep",
        "poor sleep":       "poor_sleep",
        "sleep destroys":   "poor_sleep",
        "cognitive decline":"cognitive_decline",
        "brain shrink":     "brain_shrink",
        "reaction time":    "reaction_time",
        "attention span":   "attention_span",
        "can't focus":      "cant_focus",
        "lose focus":       "cant_focus",
        "cortisol":         "cortisol_stress",
        "chronic stress":   "chronic_stress",
        "testosterone":     "testosterone",
        "omega-3":          "omega3",
        "vitamin b12":      "b12",
        "gut":              "gut_brain",
        "mediterranean":    "mediterranean_diet",
    }

    def _get_topic_fingerprint(self, query: str) -> str:
        """Return a canonical fingerprint for a topic query"""
        q = query.lower()
        for phrase, fp in self._KEYWORD_FINGERPRINTS.items():
            if phrase in q:
                return fp
        # Fallback: first 3 significant words
        words = [w for w in q.split() if w not in {'why','what','how','do','does','the','a','an','is','are','your','you'}]
        return "_".join(words[:3])

    def _load_used_fingerprints(self) -> set:
        """Load used topic fingerprints from disk"""
        try:
            import os
            os.makedirs("state", exist_ok=True)
            path = "state/used_topics.txt"
            if os.path.exists(path):
                with open(path, 'r') as f:
                    fps = set(line.strip() for line in f if line.strip())
                if len(fps) > 200:
                    fps = set(list(fps)[-200:])
                return fps
        except Exception as e:
            print(f"⚠️ Could not load used fingerprints: {e}")
        return set()

    def _save_fingerprint(self, fp: str):
        """Save fingerprint to disk immediately"""
        try:
            import os
            os.makedirs("state", exist_ok=True)
            with open("state/used_topics.txt", 'a') as f:
                f.write(fp + "\n")
        except Exception as e:
            print(f"⚠️ Could not save fingerprint: {e}")

    def get_daily_topics(self, count: int = 1) -> List[Dict]:
        """
        FIXED v3: Keyword-fingerprint deduplication.
        "Why you forget names" and "Why you can't remember names" 
        are the SAME topic — both map to fingerprint 'forget_names'.
        Used fingerprints persist to disk across GitHub Actions runs.
        """
        random.seed()

        # Load used fingerprints from disk
        used_fps = self._load_used_fingerprints()
        print(f"📋 {len(used_fps)} used topic fingerprints loaded")

        topics = []
        try:
            topics = self.fetch_trending_topics("now 1-d")
        except Exception as e:
            print(f"⚠️ Trends failed: {e}")
            topics = self._get_fallback_topics()

        if not topics:
            topics = self._get_fallback_topics()

        # Deduplicate by exact query string first
        unique = list({t['query']: t for t in topics}.values())

        # FIX: Shuffle BEFORE filtering — breaks "highest score always wins"
        random.shuffle(unique)

        # FIX: Filter by FINGERPRINT not exact string
        fresh = []
        seen_fps = set()
        for t in unique:
            fp = self._get_topic_fingerprint(t['query'])
            if fp not in used_fps and fp not in seen_fps:
                fresh.append(t)
                seen_fps.add(fp)

        # If all fingerprints used — reset and start fresh
        if not fresh:
            print("♻️ All topic fingerprints used — resetting history")
            try:
                import os
                if os.path.exists("state/used_topics.txt"):
                    os.remove("state/used_topics.txt")
            except Exception:
                pass
            fresh = unique

        result_topics = fresh[:count]

        # Save fingerprints to disk
        for t in result_topics:
            fp = self._get_topic_fingerprint(t['query'])
            self._save_fingerprint(fp)
            self.used_topics.add(t['query'])
            print(f"   📌 Selected: {t['query']} [fp: {fp}]")

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
