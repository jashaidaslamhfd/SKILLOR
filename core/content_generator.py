"""
Content Generator — Unified Timeline Engine with AI Scoring (USA 2026)
INTEGRATES: 
1. 🧠 Centralized TimelineEngine Authority (Zero timing drift)
2. 🎯 Audience-Targeted Shock Banks (Neuroscience vs. Baby Development)
3. 🔄 Mid-Roll CTA Injection (Retention-aware pacing)
4. 📊 Hook A/B Feedback Loop & Heuristic Word/Syllable Weighting
5. 🧹 Optimized Sanitization & Cleaned Dependencies
"""

import re
import random
import logging
from typing import Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None

from config.settings import API_KEYS, AUDIO_CONFIG
from config.prompts import (
    VIRAL_TITLE_GENERATOR,
    VIRAL_SCRIPT_GENERATOR,
    SHOCK_MOMENT_GENERATOR,
    format_prompt
)
from core.hook_engine import HookEngine

logger = logging.getLogger(__name__)

# 🧠 Improvement 1 & Architecture Core: Unified Timeline Authority
class TimelineEngine:
    """Single source of truth for audio durations, pause offsets, and segment pacing models."""
    def __init__(self, words_per_minute: int = 160):
        self.wps = words_per_minute / 60.0

    def calculate_syllable_weight(self, word: str) -> float:
        """Improvement 2: Syllable/Phoneme weighting simulation for natural pacing."""
        # Simple vowel counting heuristic to estimate syllable count
        vowels = len(re.findall(r'[aeiouy]', word.lower()))
        base = max(0.12, 0.20 + (vowels * 0.03)) # Long words take longer to speak
        return round(base, 2)

    def build_timeline(self, script_segments: List[Dict]) -> List[Dict]:
        """
        Calculates word-level timestamps including pause segments.
        Prevents CaptionGenerator and AudioGenerator timing splits.
        """
        timeline = []
        current_time = 0.0
        
        for segment in script_segments:
            stype = segment.get('type')
            text = segment.get('text', '')
            is_pause = segment.get('is_pause', False)
            
            if is_pause:
                duration = segment.get('duration', 0.4)
                timeline.append({
                    'type': 'pause', 'text': '', 'is_pause': True,
                    'start': round(current_time, 2), 'end': round(current_time + duration, 2),
                    'duration': duration
                })
                current_time += duration
            else:
                words = text.split()
                if not words:
                    continue
                
                # Improvement 3: Dynamic retention-aware pacing profiles
                pacing_mult = 1.0
                if stype == 'hook':   pacing_mult = 0.85 # Faster hook delivery
                elif stype == 'shock':pacing_mult = 1.20 # Slow emphasis for shock
                
                for word in words:
                    word_dur = self.calculate_syllable_weight(word) * pacing_mult
                    timeline.append({
                        'type': stype, 'word': word, 'is_pause': False,
                        'start': round(current_time, 2),
                        'end': round(current_time + word_dur, 2),
                        'duration': word_dur
                    })
                    current_time += word_dur
                    
        return timeline


class ContentGenerator:
    """Content Generator with Feedback Loops, Audience Splitting, and Mid-Roll CTAs"""
    
    def __init__(self):
        self.api_key = API_KEYS.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        self.client = None
        self.hook_engine = HookEngine(use_cache=False)
        self.timeline_engine = TimelineEngine(AUDIO_CONFIG.WORDS_PER_MINUTE)
        self._init_client()
        
        # 🎯 Logic Risk Fix: Audience-Targeted Shock Fact Banks
        self.neuroscience_facts = [
            "Your brain can store 2.5 petabytes of information... that's 3 million hours of TV.",
            "You forget 50% of what you learn within an hour... and 90% within a week.",
            "Every time you remember something, your brain actually rewrites that memory.",
            "Your brain reorganizes itself every single time you learn something new.",
            "Your brain has 86 billion neurons... and each one connects to 10,000 others.",
            "Your brain generates 23 watts of power while awake... enough to light a bulb.",
            "Your brain processes information at speeds up to 120 meters per second.",
            "Your brain can form a new memory in just 0.1 seconds.",
            "Emotional memories are 3 times stronger than neutral ones.",
            "Your brain prioritizes negative experiences... it's wired for survival.",
            "Your brain can only truly focus on one complex task at a time.",
            "It takes 23 minutes to fully refocus after a single interruption."
        ]
        
        self.baby_development_facts = [
            "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
            "The first 1000 days decide your child's entire future brain power...",
            "Your newborn's brain has already started THIS incredible process...",
            "Your baby's brain has MORE connections than stars in the galaxy...",
            "Your baby's brain is ALREADY processing language before they speak...",
            "What happens in your baby's brain when you sing to them...",
            "Your baby's brain processes YOUR voice differently than others...",
        ]
        
        # 🔴 Hook A/B Testing storage
        self.hook_performance_scores = {}

        self.baby_ctas = [
            "👍 DOUBLE TAP if your baby does this!",
            "❤️ Like if you're AMAZED by your baby's brain!",
            "👇 Comment 'BABY' if your little one does this too!",
            "💬 Tag a NEW PARENT who needs to see this!",
            "📌 SAVE this — every parent needs to know this!"
        ]
        
        self.mid_roll_ctas = [
            "👇 Comment 'YES' if your baby does this!",
            "🔥 Hit subscribe for daily brain facts!",
        ]

    def _init_client(self):
        """Initialize Groq client"""
        if not Groq or not self.api_key:
            logger.warning("⚠️ Groq not configured")
            return
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info("✅ Groq client initialized")
        except Exception as e:
            logger.error(f"⚠️ Groq init failed: {e}")
            self.client = None

    def _call_groq(self, prompt: str, max_tokens: int = 600) -> str:
        """Call Groq API safely"""
        if not self.client:
            return ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"⚠️ Groq error: {e}")
            return ""

    def _extract(self, label: str, text: str) -> str:
        """Extract section from AI response"""
        if not text:
            return ""
        pattern = rf'###\s*{label}:\s*(.+?)(?=\n\s*###\s*(?:HOOK|SHOCK|SUSPENSE|STORY|CTR|$))'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _clean(self, text: str) -> str:
        """6. Retain statistical digits (e.g. 100,000) inside sanitization logic"""
        if not text:
            return ""
        text = re.sub(r'#\w+', '', text)
        # Retain digits, basic punctuation (. , ? !), strip weird ASCII controls
        text = re.sub(r'[^\x00-\x7F\s.,?!]', '', text) 
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _get_targeted_shock_fact(self, topic: str) -> str:
        """Selects shock bank based on audience context."""
        if 'baby' in topic.lower() or 'child' in topic.lower():
            return random.choice(self.baby_development_facts)
        return random.choice(self.neuroscience_facts)

    def _select_optimized_hook(self) -> str:
        """⭐ Improvement 2 & Hook Feedback Loop: Selects best performing hook via scoring."""
        if not self.hook_performance_scores:
            # Seed state - pick randomly from baseline bank
            candidates = self.baby_development_facts
        else:
            # Sort by execution performance score descending
            sorted_hooks = sorted(self.hook_performance_scores.keys(), 
                                  key=lambda h: self.hook_performance_scores[h], 
                                  reverse=True)
            candidates = sorted_hooks[:3] # Top 3 options
            
        selected_hook = random.choice(candidates)
        return selected_hook

    def register_hook_performance(self, hook_text: str, score: float):
        """Allows external analytics to inject CTR back into the generation matrix."""
        self.hook_performance_scores[hook_text] = score

    def generate_script(self, topic: str, angle: str = "",
                        shock_angle: str = "", pattern: str = "memory_insight",
                        suspense_score: int = 70) -> Dict:
        """Executes full pipeline generation with unified timeline compilation and Mid-roll CTRs."""
        
        logger.info(f"🎬 Generating script for: {topic}")
        
        hook = self._select_optimized_hook()
        logger.info(f"   Hook Selected: '{hook[:40]}...'")
        
        prompt = format_prompt(
            VIRAL_SCRIPT_GENERATOR,
            topic=topic,
            angle=angle or f"Understanding {topic} evolution",
            shock_angle=shock_angle or f"{topic} mechanism processing",
            pattern=pattern,
            suspense_score=suspense_score
        )
        
        raw = self._call_groq(prompt, max_tokens=500) if self.client else ""
        
        shock = self._clean(self._extract("SHOCK", raw))
        suspense = self._clean(self._extract("SUSPENSE", raw))
        story = self._clean(self._extract("STORY", raw))
        ctr = self._clean(self._extract("CTR", raw))
        
        # Apply fallbacks
        if not shock: shock = self._get_targeted_shock_fact(topic)
        if not suspense: suspense = "The biological reason behind this might surprise you..."
        if not story: story = f"The science of {topic} is deeper than it seems."
        if not ctr: ctr = random.choice(self.baby_ctas)
        
        # ═══════════════════════════════════════════════════════════
        # BUILD TIMELINE SEGMENT ARRAYS (Includes ⏸️ Pause events)
        # ═══════════════════════════════════════════════════════════
        raw_segments = []
        
        raw_segments.append({'type': 'hook', 'text': hook})
        raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.5})
        raw_segments.append({'type': 'shock', 'text': shock})
        raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.3})
        raw_segments.append({'type': 'suspense', 'text': suspense})
        raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.4})
        
        # Split narrative story blocks naturally
        if '...' in story:
            parts = story.split('...', 1)
            raw_segments.append({'type': 'story', 'text': parts[0].strip() + '...'})
            raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.4})
            if parts[1].strip():
                raw_segments.append({'type': 'story', 'text': parts[1].strip()})
        else:
            words = story.split()
            mid = len(words) // 2
            if mid > 3:
                raw_segments.append({'type': 'story', 'text': ' '.join(words[:mid]) + '...'})
                raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.35})
                raw_segments.append({'type': 'story', 'text': ' '.join(words[mid:])})
            else:
                raw_segments.append({'type': 'story', 'text': story})
        
        raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.3})
        
        # 🚨 Retention Fix: Mid-Roll CTA Injection before the final push or end-CTR
        mid_cta = random.choice(self.mid_roll_ctas)
        raw_segments.append({'type': 'ctr_mid', 'text': mid_cta})
        raw_segments.append({'type': 'pause', 'text': '', 'is_pause': True, 'duration': 0.3})
        
        # Terminal CTA
        raw_segments.append({'type': 'ctr_end', 'text': ctr})

        # 🧠 Compute timeline array containing exact timestamps from start to finish
        word_timeline = self.timeline_engine.build_timeline(raw_segments)
        total_duration = word_timeline[-1]['end'] if word_timeline else 0.0
        word_count = sum(1 for item in word_timeline if not item['is_pause'])

        logger.info(f"   Words compiled: {word_count} | Timeline duration: {total_duration}s")
        
        return {
            'full_script': " ".join(s['word'] for s in word_timeline if not s['is_pause']),
            'word_timeline': word_timeline, # Unified timing engine truth
            'raw_segments': raw_segments,
            'word_count': word_count,
            'duration': round(total_duration, 2),
            'hook': hook,
            'shock': shock,
            'suspense': suspense,
            'story': story,
            'ctr': ctr
        }

    def generate_title(self, topic: str) -> str:
        """Generate optimized title"""
        prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic=topic)
        raw = self._call_groq(prompt, max_tokens=150) if self.client else ""
        
        BAD_OPENERS = ['why ignoring', 'ignoring why', 'how ignoring', 'did you know', 'scientists', 'shocking', 'mind-blowing', 'have you ever', 'what if i told']
        GOOD_OPENERS = ['your baby', 'your child', 'nobody explains', 'nobody tells', 'why your', 'the real reason', 'this happens', 'what your baby', 'how your baby']
        
        if raw:
            lines = [t.strip() for t in raw.split('\n') if t.strip()]
            for title in lines:
                title = title.lstrip('0123456789.-*•) ').strip(' "').strip("'")
                skip_words = ['type', 'hook', 'rule', 'example', 'avoid', 'use:', 'must', 'return', 'opener', '✅', '❌', '🟢']
                if any(s in title.lower() for s in skip_words): continue
                
                title_lower = title.lower()
                if any(title_lower.startswith(bad) for bad in BAD_OPENERS): continue
                if not any(title_lower.startswith(good) for good in GOOD_OPENERS): continue
                
                words = title.split()
                non_emoji_words = [w for w in words if not any(ord(c) > 127 for c in w)]
                if not (4 <= len(non_emoji_words) <= 9): continue
                
                has_emoji = any(ord(c) > 127 for c in title)
                if not has_emoji: title += ' 🧠'
                return title
        
        return f"The real reason behind {topic} 🧠"

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Generate high-CTR keyword tokens"""
        topic_lower = topic.lower()
        TOPIC_MAP = {
            'baby': ['BABY', 'BRAIN', 'SCIENCE'], 'brain': ['BRAIN', 'BABY', 'GROWTH'],
            'sleep': ['SLEEP', 'BABY', 'BRAIN'], 'smile': ['SMILE', 'BABY', 'BRAIN'],
            'tummy': ['TUMMY', 'BABY', 'TIME'], 'talk': ['TALK', 'BABY', 'BRAIN'],
            'cry': ['CRY', 'BABY', 'SCIENCE'], 'play': ['PLAY', 'BABY', 'BRAIN'],
            'newborn': ['NEWBORN', 'BRAIN', 'FACTS']
        }
        for key, words in TOPIC_MAP.items():
            if key in topic_lower: return words
        return ['BABY', 'BRAIN', 'SCIENCE']

    def generate_seo(self, topic: str, script: str) -> Dict:
        """Generate SEO parameters"""
        intros = [f"The science behind {topic} explained simply.", f"Your baby's brain does {topic} for a reason. Here's the science.", f"What nobody explains about {topic} — until now."]
        desc = f"{random.choice(intros)} Follow for more baby brain science. #Shorts"
        words = [w for w in topic.lower().split() if len(w) > 3]
        tags = words[:4] + ["baby brain", "parenting tips", "child development", "baby science", "youtube shorts"]
        unique = list(dict.fromkeys(tags))
        
        return {
            'description': desc[:250], 'tags': unique[:15],
            'keywords': ",".join(words[:3] + ["explained", "science"])
        }
