"""
Content Generator — Script Generation with Self-Correcting Hooks
INTEGRATES: HookEngine for perfect hooks every time
"""

import re
import time
import random
from typing import Dict, List, Optional, Tuple

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


class ContentGenerator:
    """Content Generator with Self-Correcting Hooks"""
    
    def __init__(self):
        self.api_key = API_KEYS.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        self.client = None
        self.hook_engine = HookEngine(use_cache=True)
        self._init_client()
        
        # ============================================================
        # FIX: SHOCK FACT FALLBACKS - 30+ UNIQUE FACTS
        # ============================================================
        self.shock_fact_fallbacks = [
            # Universal Brain Facts
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
            "It takes 23 minutes to fully refocus after a single interruption.",
            "Your brain's peak focus window is only 90 minutes at a time.",
            "Your brain uses 20% of your entire body's energy... just to think.",
            "Your brain is 73% water... even mild dehydration slows it down.",

            # Universal Body Facts
            "Your gut has 100 million neurons... almost as many as your entire spinal cord.",
            "Your heart sends more signals to your brain than your brain sends back.",
            "Your body replaces 96% of its atoms every single year.",
            "Your skin replaces itself completely every 2 to 4 weeks.",
            "Your body produces a completely new skeleton every 10 years.",
            "You blink 15 to 20 times a minute... and barely notice any of them.",
            "Your body has enough iron in it to make a small nail.",
            "Your nose can detect over 1 trillion different smells.",
            "Your eyes can distinguish over 10 million different colors.",
            "Your body produces about 25 million new cells every single second.",
            "Your heart beats roughly 100,000 times every single day.",
            "Your blood travels 12,000 miles through your body every day.",
            "Your lungs have 300 million tiny air sacs called alveoli.",
            "Your body has more bacterial cells than human cells right now.",
            "A sneeze travels at up to 100 miles per hour when it leaves your body.",
            "Your tongue print is as unique as your fingerprint.",
            "Your body generates enough heat to boil water in 30 minutes.",
            "The surface area of your lungs is roughly the size of a tennis court.",
            "Your body has around 37 trillion cells all working at once.",
            "Your bones are 5 times stronger than steel of the same density.",
        ]
        
        self.used_shock_facts = set()  # Track used facts to prevent repetition

    def _init_client(self):
        """Initialize Groq client"""
        if not Groq or not self.api_key:
            print("⚠️ Groq not configured")
            return
        try:
            self.client = Groq(api_key=self.api_key)
            print("✅ Groq client initialized")
        except Exception as e:
            print(f"⚠️ Groq init failed: {e}")
            self.client = None

    def _call_groq(self, prompt: str, max_tokens: int = 600) -> str:
        """Call Groq API"""
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
            print(f"⚠️ Groq error: {e}")
            return ""

    def _extract(self, label: str, text: str) -> str:
        """Extract section from AI response"""
        if not text:
            return ""
        pattern = rf'###\s*{label}:\s*(.+?)(?=\n\s*###\s*(?:HOOK|SHOCK|SUSPENSE|STORY|CTR|$))'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _clean(self, text: str) -> str:
        """Clean text for TTS"""
        if not text:
            return ""
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _generate_fallback_story(self, topic: str) -> str:
        """Generate fallback story"""
        templates = [
            f"The science behind {topic} is simpler than you'd think. "
            f"Your brain is actually trying to help you in a quiet, automatic way. "
            f"And the part that really matters is how deeply your brain pays attention to you, "
            f"even when you're not paying attention to yourself.",
            
            f"Here's what's actually happening with {topic}. "
            f"Your mind has been processing this your whole life without you realizing it. "
            f"The quiet truth is, your body knows exactly what it's doing. "
            f"And understanding that changes everything about how you see it."
        ]
        return random.choice(templates)

    # ============================================================
    # FIX: UNIQUE SHOCK FACT GENERATOR
    # ============================================================
    
    def _get_unique_shock_fact(self) -> str:
        """Get a unique shock fact - never repeats"""
        # Reset if all used
        if len(self.used_shock_facts) >= len(self.shock_fact_fallbacks):
            self.used_shock_facts.clear()
            print("   🔄 All shock facts used, resetting...")
        
        # Get available facts
        available = [f for f in self.shock_fact_fallbacks if f not in self.used_shock_facts]
        
        if not available:
            available = self.shock_fact_fallbacks.copy()
            self.used_shock_facts.clear()
        
        # Select random fact
        fact = random.choice(available)
        self.used_shock_facts.add(fact)
        
        return fact

    def generate_script(self, topic: str, angle: str = "", 
                        shock_angle: str = "", pattern: str = "memory_insight",
                        suspense_score: int = 70) -> Dict:
        """Generate complete script with perfect hook"""
        
        print(f"\n🎬 Generating script for: {topic}")
        
        # Step 1: Generate perfect hook
        hook_result = self.hook_engine.generate_perfect_hook(topic)
        hook = hook_result['hook']
        
        print(f"   Hook: '{hook}'")
        print(f"   Score: {hook_result['validation'].score}/10")
        print(f"   Status: {hook_result['status']}")
        
        # Step 2: Generate rest of script
        prompt = format_prompt(
            VIRAL_SCRIPT_GENERATOR,
            topic=topic,
            angle=angle or f"Understanding why {topic} happens",
            shock_angle=shock_angle or f"your brain is quietly processing {topic}",
            pattern=pattern,
            suspense_score=suspense_score
        )
        
        raw = self._call_groq(prompt, max_tokens=500)
        
        shock = self._clean(self._extract("SHOCK", raw))
        suspense = self._clean(self._extract("SUSPENSE", raw))
        story = self._clean(self._extract("STORY", raw))
        ctr = self._clean(self._extract("CTR", raw))
        
        # ============================================================
        # FIX: Fallbacks with UNIQUE facts
        # ============================================================
        if not shock:
            shock = self._get_unique_shock_fact()  # ✅ ALWAYS UNIQUE
            print(f"   💡 Using unique shock fact #{len(self.used_shock_facts)}")
        
        if not suspense:
            suspense = "And the reason behind this might explain a lot about your own life..."
        
        if not story:
            story = self._generate_fallback_story(topic)
        
        if not ctr:
            ctr = "Follow for more on why your brain works this way."
        
        # Build segments
        wps = AUDIO_CONFIG.WORDS_PER_MINUTE / 60.0
        segments = []
        t = 0.0
        
        def add_segment(stype, text, is_pause=False, dur=None):
            nonlocal t
            if not text and not is_pause:
                return
            if is_pause:
                duration = dur or 0.4
            else:
                duration = dur or round(len(text.split()) / wps, 2)
            segments.append({
                'type': stype,
                'text': '' if is_pause else text,
                'duration': duration,
                'start': round(t, 2),
                'is_pause': is_pause
            })
            t += duration
        
        add_segment('hook', hook)
        add_segment('pause', '', is_pause=True, dur=0.5)
        add_segment('shock', shock)
        add_segment('pause', '', is_pause=True, dur=0.3)
        add_segment('suspense', suspense)
        add_segment('pause', '', is_pause=True, dur=0.4)
        
        # Split story
        if '...' in story:
            parts = story.split('...', 1)
            add_segment('story', parts[0].strip() + '...')
            add_segment('pause', '', is_pause=True, dur=0.4)
            if parts[1].strip():
                add_segment('story', parts[1].strip())
        else:
            words = story.split()
            mid = len(words) // 2
            if mid > 3:
                add_segment('story', ' '.join(words[:mid]) + '...')
                add_segment('pause', '', is_pause=True, dur=0.35)
                add_segment('story', ' '.join(words[mid:]))
            else:
                add_segment('story', story)
        
        add_segment('pause', '', is_pause=True, dur=0.4)
        add_segment('ctr', ctr)
        
        full_script = ' '.join(s['text'] for s in segments if not s.get('is_pause'))
        word_count = len(full_script.split())
        
        print(f"   Words: {word_count}")
        print(f"   Duration: {round(t, 2)}s")
        
        return {
            'full_script': full_script,
            'segments': segments,
            'word_count': word_count,
            'duration': round(t, 2),
            'hook': hook,
            'hook_score': hook_result['validation'].score,
            'hook_status': hook_result['status'],
            'shock': shock,
            'suspense': suspense,
            'story': story,
            'ctr': ctr
        }

    def generate_title(self, topic: str) -> str:
        """Generate title - FIXED v2: No duplicates, no broken text, clean output"""
        prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic=topic)
        raw = self._call_groq(prompt, max_tokens=150)
        
        if raw:
            lines = [t.strip() for t in raw.split('\n') if t.strip()]
            
            for title in lines:
                # ✅ FIX 1: Remove numbering like "1.", "2.", "-", "*"
                title = title.lstrip('0123456789.-*) ').strip()
                
                # ✅ FIX 2: Skip lines that are headers or instructions
                skip_words = ['type', 'hook', 'rule', 'example', 'avoid', 'use:', 'must', 'return']
                if any(s in title.lower() for s in skip_words):
                    continue
                
                # ✅ FIX 3: Skip lines that are too short or too long
                words = title.split()
                if len(words) < 3 or len(words) > 12:
                    continue
                
                # ✅ FIX 4: Skip if title contains duplicate words back-to-back
                # e.g. "Why ignoring Why men..." — "Why" repeated
                title_words_lower = [w.lower() for w in words]
                has_duplicate = any(
                    title_words_lower[i] == title_words_lower[i+1]
                    for i in range(len(title_words_lower)-1)
                )
                if has_duplicate:
                    continue
                
                # ✅ FIX 5: Skip if title has broken/incomplete words (< 3 chars at end that arent emoji)
                last_word = words[-1]
                if len(last_word) < 3 and not any(c for c in last_word if ord(c) > 127):
                    continue
                
                # ✅ FIX 6: Ensure emoji at end (add if missing)
                has_emoji = any(ord(c) > 127 for c in title)
                if not has_emoji:
                    topic_emojis = {
                        'body': '🧬', 'brain': '🧠', 'memory': '🧠',
                        'forget': '🤔', 'heart': '❤️', 'gut': '💚',
                        'sleep': '😴', 'energy': '⚡', 'muscle': '💪',
                        'eye': '👁️', 'ear': '👂', 'skin': '✨',
                    }
                    emoji = '🧠'
                    for key, em in topic_emojis.items():
                        if key in topic.lower() or key in title.lower():
                            emoji = em
                            break
                    title = title + ' ' + emoji
                
                return title
        
        # ✅ FIX 7: Clean fallbacks — no topic variable in awkward positions
        topic_short = ' '.join(topic.split()[:4])  # max 4 words from topic
        fallbacks = [
            f"Nobody explains why your body does this 🧬",
            f"Your brain has been hiding this from you 🧠",
            f"This happens to your body every single day 🤔",
            f"The real reason your body does {topic_short} 👀",
            f"What your body is quietly doing right now ⚡",
        ]
        return random.choice(fallbacks)

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Generate 3 high-CTR words for thumbnail — FIXED v2"""
        topic_lower = topic.lower()
        
        # ✅ FIX: Topic-specific word sets — emotionally powerful, short
        TOPIC_WORD_MAP = {
            'jerk': ['BODY', 'FALLING', 'WHY'],
            'goosebump': ['CHILLS', 'YOUR', 'BODY'],
            'yawn': ['CONTAGIOUS', 'WHY', 'YAWN'],
            'deja vu': ['DEJA', 'VU', 'BRAIN'],
            'brain freeze': ['FREEZE', 'BRAIN', 'WHY'],
            'song stuck': ['STUCK', 'SONG', 'BRAIN'],
            'tickle': ['TICKLE', 'BRAIN', 'WHY'],
            'heart': ['HEART', 'SKIP', 'WHY'],
            'gut': ['GUT', 'BRAIN', 'HIDDEN'],
            'stomach growl': ['GROWL', 'HUNGER', 'WHY'],
            'dizzy': ['DIZZY', 'BODY', 'WHY'],
            'sneeze': ['SNEEZE', 'LIGHT', 'WHY'],
            'hiccup': ['HICCUP', 'BRAIN', 'WHY'],
            'twitch': ['TWITCH', 'BODY', 'WHY'],
            'forget name': ['FORGET', 'NAMES', 'WHY'],
            'forget': ['FORGET', 'BRAIN', 'WHY'],
            'memory': ['MEMORY', 'BRAIN', 'HIDDEN'],
            'brain fog': ['FOGGY', 'BRAIN', 'WHY'],
            'focus': ['FOCUS', 'BRAIN', 'LOST'],
            'tired': ['TIRED', 'ALWAYS', 'WHY'],
            'energy': ['ENERGY', 'CRASH', 'WHY'],
            'anxious': ['ANXIETY', 'BODY', 'WHY'],
            'scared': ['FREEZE', 'FEAR', 'WHY'],
            'emotional': ['EMOTION', 'BODY', 'WHY'],
            'smell': ['SMELL', 'MEMORY', 'WHY'],
            'music': ['MUSIC', 'CHILLS', 'WHY'],
            'time': ['TIME', 'FASTER', 'WHY'],
            'embarrass': ['REPLAY', 'BRAIN', 'WHY'],
            'watched': ['WATCHED', 'ALONE', 'BRAIN'],
            'cold': ['COLD', 'HANDS', 'WHY'],
            'sweat': ['SWEAT', 'NERVOUS', 'WHY'],
            'hungry': ['HUNGRY', 'AGAIN', 'WHY'],
            'bloat': ['BLOAT', 'BODY', 'WHY'],
        }
        
        # Match topic to word set
        for key, words in TOPIC_WORD_MAP.items():
            if key in topic_lower:
                return words
        
        # ✅ FIX: Generic fallback — extract meaningful words from topic
        stop_words = {'why', 'your', 'you', 'the', 'a', 'an', 'is', 'are',
                     'do', 'does', 'when', 'how', 'what', 'that', 'this',
                     'for', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of'}
        
        topic_words = [w.upper() for w in topic.split() 
                      if len(w) > 3 and w.lower() not in stop_words]
        
        base = ['BODY', 'BRAIN', 'WHY', 'HIDDEN', 'SECRET', 'REAL']
        
        result = topic_words[:2]
        for b in base:
            if b not in result:
                result.append(b)
            if len(result) >= 3:
                break
        
        return result[:3]

    def generate_seo(self, topic: str, script: str) -> Dict:
        """Generate SEO description and tags"""
        description = (
            f"The truth about {topic} explained simply. "
            f"Body and brain science nobody teaches you. "
            f"Follow for more science your body never explained. "
            f"#Shorts #BodyScience #BrainFacts"
        )
        
        tags = [
            "body science", "brain facts", "why does my body",
            "explained simply", "body mysteries", "brain science",
            "why do i feel", "youtube shorts", "health facts",
            "body facts", "science shorts", "did you know"
        ]
        
        return {
            'description': description[:250],
            'tags': tags[:15],
            'keywords': f"body science,brain facts,why does my body,explained,health"
        }

    def reset_used_shock_facts(self):
        """Reset used shock facts cache"""
        self.used_shock_facts.clear()
        print("🧹 Reset shock facts cache")


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING CONTENT GENERATOR (FIXED)\n" + "="*60)
    
    generator = ContentGenerator()
    
    # Test with multiple topics to verify uniqueness
    test_topics = [
        "forgetting names",
        "brain fog",
        "memory loss",
        "sleep problems",
        "stress effects"
    ]
    
    for topic in test_topics:
        print(f"\n📝 Generating for: {topic}")
        script = generator.generate_script(topic=topic)
        print(f"   Shock: {script['shock'][:50]}...")
    
    print(f"\n✅ Used {len(generator.used_shock_facts)} unique shock facts")
