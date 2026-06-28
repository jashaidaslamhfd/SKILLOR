"""
Content Generator — Script Generation with Self-Correcting Hooks
INTEGRATES: HookEngine for perfect hooks every time
FIXED: Baby hooks + forced CTAs
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
        self.hook_engine = HookEngine(use_cache=False)
        self._init_client()
        
        # ============================================================
        # SHOCK FACT FALLBACKS - 30+ UNIQUE FACTS
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
        
        self.used_shock_facts = set()

        # ============================================================
        # BABY HOOKS - FORCED ATTENTION
        # ============================================================
        self.baby_hooks = [
            "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
            "The first 1000 days decide your child's entire future brain power...",
            "What your baby's brain is secretly doing while they sleep will AMAZE you...",
            "Your newborn's brain has already started THIS incredible process...",
            "The one thing that builds your baby's brain faster than ANYTHING else...",
            "Your baby's brain has MORE connections than stars in the galaxy...",
            "This simple activity TRIPLES your baby's brain growth...",
            "Your baby's brain is ALREADY processing language before they speak...",
            "The surprising reason your baby cries — it's brain development...",
            "Your child's brain is doing THIS every single night without fail...",
            "Nobody tells you what your baby's brain is doing RIGHT NOW...",
            "What your baby's brain does during tummy time is INCREDIBLE...",
            "The science behind your baby's first smile is BRAIN GROWTH...",
            "Your toddler's brain is wired for THIS — and it's AMAZING...",
            "Your baby's brain is built through play — here's HOW...",
            "The first year of brain development changes EVERYTHING...",
            "Your baby's brain can do THIS before they can even talk...",
            "What happens in your baby's brain when you sing to them...",
            "Your baby's brain processes YOUR voice differently than others...",
        ]

        # ============================================================
        # BABY CTAS - FORCED ENGAGEMENT (Like + Comment + Share)
        # ============================================================
        self.baby_ctas = [
            "👍 DOUBLE TAP if your baby does this!",
            "❤️ Like if you're AMAZED by your baby's brain!",
            "👍 Hit LIKE if you knew this about your baby!",
            "❤️ Like if this BLEW YOUR MIND about babies!",
            "👇 Comment 'BABY' if your little one does this too!",
            "💬 What does YOUR baby do that amazes you? Comment below!",
            "👇 Does YOUR baby do this? Comment YES or NO!",
            "💬 Tag a NEW PARENT who needs to see this!",
            "👇 Comment 'ME' if this is YOUR baby!",
            "💬 Share YOUR baby's milestone in the comments!",
            "📌 SAVE this — every parent needs to know this!",
            "🗣️ SHARE this with every new mom you know!",
            "📌 SHARE with a parent who has a baby under 1!",
            "🗣️ TAG someone who needs to see this baby science!",
            "👍 Like AND Comment 'BRAIN' if you love baby science!",
            "❤️ Like AND Share if you want more baby brain tips!",
            "👍 Like AND Tag a new parent in the comments!",
        ]

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
            f"Your baby's brain is actually building thousands of new connections every single second. "
            f"And the part that really matters is how deeply your baby learns from you, "
            f"even when you're not trying to teach them.",
            
            f"Here's what's actually happening with {topic}. "
            f"Your baby's mind has been processing this since birth without you realizing it. "
            f"The quiet truth is, your baby's brain knows exactly what it's doing. "
            f"And understanding that changes everything about how you see them."
        ]
        return random.choice(templates)

    def _get_unique_shock_fact(self) -> str:
        """Get a unique shock fact - never repeats"""
        if len(self.used_shock_facts) >= len(self.shock_fact_fallbacks):
            self.used_shock_facts.clear()
            print("   🔄 All shock facts used, resetting...")
        
        available = [f for f in self.shock_fact_fallbacks if f not in self.used_shock_facts]
        if not available:
            available = self.shock_fact_fallbacks.copy()
            self.used_shock_facts.clear()
        
        fact = random.choice(available)
        self.used_shock_facts.add(fact)
        return fact

    def generate_script(self, topic: str, angle: str = "",
                        shock_angle: str = "", pattern: str = "memory_insight",
                        suspense_score: int = 70) -> Dict:
        """Generate complete script with FORCED engagement hooks"""
        
        print(f"\n🎬 Generating script for: {topic}")
        
        # ═══════════════════════════════════════════════════════════
        # FIX: Use BABY hooks (strong, emotional, curiosity-driven)
        # ═══════════════════════════════════════════════════════════
        hook = random.choice(self.baby_hooks)
        print(f"   Hook: '{hook}'")
        
        # ── Generate rest of script ──
        prompt = format_prompt(
            VIRAL_SCRIPT_GENERATOR,
            topic=topic,
            angle=angle or f"Understanding your baby's brain development",
            shock_angle=shock_angle or f"your baby's brain is quietly processing everything",
            pattern=pattern,
            suspense_score=suspense_score
        )
        
        raw = self._call_groq(prompt, max_tokens=500) if self.client else ""
        
        shock = self._clean(self._extract("SHOCK", raw))
        suspense = self._clean(self._extract("SUSPENSE", raw))
        story = self._clean(self._extract("STORY", raw))
        ctr = self._clean(self._extract("CTR", raw))
        
        # ── Fallbacks ──
        if not shock:
            shock = self._get_unique_shock_fact()
            print(f"   💡 Using unique shock fact #{len(self.used_shock_facts)}")
        
        if not suspense:
            suspense = "And the reason behind this might explain everything about your baby's development..."
        
        if not story:
            story = self._generate_fallback_story(topic)
        
        if not ctr:
            ctr = random.choice(self.baby_ctas)
        
        # ── Build segments with FORCED CTAs ──
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
        
        # ═══════════════════════════════════════════════════════════
        # FIX: Add FORCED CTA (Like + Comment + Share)
        # ═══════════════════════════════════════════════════════════
        cta = random.choice(self.baby_ctas)
        add_segment('ctr', cta)
        
        full_script = ' '.join(s['text'] for s in segments if not s.get('is_pause'))
        word_count = len(full_script.split())
        
        print(f"   Words: {word_count}")
        print(f"   Duration: {round(t, 2)}s")
        print(f"   CTA: '{cta}'")
        
        return {
            'full_script': full_script,
            'segments': segments,
            'word_count': word_count,
            'duration': round(t, 2),
            'hook': hook,
            'hook_score': 9,
            'shock': shock,
            'suspense': suspense,
            'story': story,
            'ctr': cta
        }

    def generate_title(self, topic: str) -> str:
        """Generate title - USA optimized"""
        prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic=topic)
        raw = self._call_groq(prompt, max_tokens=150) if self.client else ""
        
        BAD_OPENERS = [
            'why ignoring', 'ignoring why', 'how ignoring',
            'did you know', 'scientists', 'shocking', 'mind-blowing',
            'have you ever', 'what if i told',
        ]
        
        GOOD_OPENERS = [
            'your baby', 'your child', 'nobody explains', 'nobody tells',
            'why your', 'the real reason', 'this happens',
            'what your baby', 'how your baby',
        ]
        
        if raw:
            lines = [t.strip() for t in raw.split('\n') if t.strip()]
            for title in lines:
                title = title.lstrip('0123456789.-*•) ').strip()
                title = title.strip('"').strip("'").strip()
                
                skip_words = ['type', 'hook', 'rule', 'example', 'avoid',
                              'use:', 'must', 'return', 'opener', '✅', '❌', '🟢']
                if any(s in title.lower() for s in skip_words):
                    continue
                
                title_lower = title.lower()
                if any(title_lower.startswith(bad) for bad in BAD_OPENERS):
                    continue
                
                if not any(title_lower.startswith(good) for good in GOOD_OPENERS):
                    continue
                
                words = title.split()
                non_emoji_words = [w for w in words if not any(ord(c) > 127 for c in w)]
                if len(non_emoji_words) < 4 or len(non_emoji_words) > 9:
                    continue
                
                has_emoji = any(ord(c) > 127 for c in title)
                if not has_emoji:
                    title = title + ' 🧠'
                
                return title
        
        # Fallback titles
        fallbacks = [
            f"Your baby's brain does THIS with {topic} 🧠",
            f"The real reason behind {topic} 🧠",
            f"What nobody explains about {topic} 🧠",
            f"How {topic} affects your baby's brain 🧠",
            f"The science behind {topic} explained 🧠",
        ]
        return random.choice(fallbacks)

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Generate 3 high-CTR words for thumbnail"""
        topic_lower = topic.lower()
        
        TOPIC_WORD_MAP = {
            'baby': ['BABY', 'BRAIN', 'SCIENCE'],
            'brain': ['BRAIN', 'BABY', 'GROWTH'],
            'sleep': ['SLEEP', 'BABY', 'BRAIN'],
            'smile': ['SMILE', 'BABY', 'BRAIN'],
            'tummy': ['TUMMY', 'BABY', 'TIME'],
            'talk': ['TALK', 'BABY', 'BRAIN'],
            'cry': ['CRY', 'BABY', 'SCIENCE'],
            'play': ['PLAY', 'BABY', 'BRAIN'],
            'first': ['FIRST', 'BABY', 'MILESTONE'],
            'newborn': ['NEWBORN', 'BRAIN', 'FACTS'],
            'toddler': ['TODDLER', 'BRAIN', 'GROWTH'],
            'parent': ['PARENT', 'BABY', 'SCIENCE'],
        }
        
        for key, words in TOPIC_WORD_MAP.items():
            if key in topic_lower:
                return words
        
        return ['BABY', 'BRAIN', 'SCIENCE']

    def generate_seo(self, topic: str, script: str) -> Dict:
        """Generate SEO description and tags"""
        description_intros = [
            f"The science behind {topic} explained simply.",
            f"Your baby's brain does {topic} for a reason. Here's the science.",
            f"What nobody explains about {topic} — until now.",
        ]
        description = (
            f"{random.choice(description_intros)} "
            f"Follow for more baby brain science. "
            f"#Shorts"
        )
        
        topic_words = [w for w in topic.lower().split() if len(w) > 3]
        base_tags = ["baby brain", "parenting tips", "child development", "baby science"]
        tags = topic_words[:4] + base_tags + ["youtube shorts"]
        
        seen = set()
        unique_tags = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)
        
        return {
            'description': description[:250],
            'tags': unique_tags[:15],
            'keywords': ",".join(topic_words[:3] + ["explained", "science"])
        }

    def reset_used_shock_facts(self):
        """Reset used shock facts cache"""
        self.used_shock_facts.clear()
        print("🧹 Reset shock facts cache")


if __name__ == "__main__":
    print("🚀 TESTING CONTENT GENERATOR")
    generator = ContentGenerator()
    
    test_topics = ["baby brain development", "baby sleep science", "baby first words"]
    for topic in test_topics:
        print(f"\n📝 Generating for: {topic}")
        script = generator.generate_script(topic=topic)
        print(f"   Hook: {script['hook'][:50]}...")
        print(f"   CTA: {script['ctr']}")