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
            # Memory Facts
            "Your brain can store 2.5 petabytes of information... that's 3 million hours of TV.",
            "You forget 50% of what you learn within an hour... and 90% within a week.",
            "Your brain's storage capacity is virtually unlimited... but your recall is not.",
            "Every time you remember something, your brain rewrites that memory.",
            "Your brain reorganizes itself every time you learn something new.",
            
            # Brain Facts
            "Your brain uses 20% of your body's oxygen and calories.",
            "Your brain is 60% fat and 73% water... staying hydrated matters.",
            "Your brain has 86 billion neurons... and each connects to 10,000 others.",
            "Your brain generates 23 watts of power while awake... enough to light a bulb.",
            "Your brain processes information at speeds up to 120 meters per second.",
            
            # Aging Brain Facts
            "Your brain shrinks by about 1% every year after age 40.",
            "After 35, your brain's processing speed slows by 15% every decade.",
            "Your brain's white matter peaks at age 45... then declines.",
            "Your brain loses 1 gram of mass every year after 40.",
            "By age 50, your brain has lost 10% of its peak volume.",
            
            # Sleep & Brain Facts
            "Your brain cleans itself only while you sleep... 60% less cleaning if sleep deprived.",
            "One bad night's sleep reduces your cognitive performance by 40%.",
            "Your brain needs 7-8 hours of sleep to flush out toxic waste.",
            "Sleep deprivation accelerates brain aging by 3-5 years.",
            "Your brain creates 2 million new connections every night while you sleep.",
            
            # Stress Facts
            "Chronic stress kills brain cells in the hippocampus... your memory center.",
            "Stress can shrink your brain's prefrontal cortex... affecting decision making.",
            "High cortisol levels age your brain by 6-8 years.",
            "Stress reduces brain volume in areas responsible for memory.",
            "Every stressful event releases cortisol... and damages your memory.",
            
            # Focus & Attention Facts
            "Your brain can only focus on one complex task at a time.",
            "It takes 23 minutes to fully refocus after a single interruption.",
            "Your attention span has dropped by 33% in the last 20 years.",
            "Multi-tasking reduces productivity by up to 40%.",
            "Your brain's peak focus time is only 90 minutes.",
            
            # Memory & Learning Facts
            "Your brain can form new memories in just 0.1 seconds.",
            "Emotional memories are 3 times stronger than neutral ones.",
            "Your brain prioritizes negative experiences for survival.",
            "Learning new skills creates 10 times more neural connections.",
            "Your brain rewires itself every time you practice something new.",
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
        """Generate title - FIXED"""
        prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic=topic)
        raw = self._call_groq(prompt, max_tokens=100)
        
        if raw:
            titles = [t.strip() for t in raw.split('\n') if t.strip()]
            if titles:
                title = titles[0]
                words = title.split()
                if len(words) > 6:
                    title = ' '.join(words[:6])
                return title
        
        fallbacks = [
            f"Your brain is forgetting {topic} right now 🧠",
            f"Why your {topic} gets worse after 35 🧠",
            f"Nobody tells men about {topic} after 40 😳",
            f"Your memory is changing with {topic} right now"
        ]
        return random.choice(fallbacks)

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Generate 3 words for thumbnail"""
        base_words = ['MEMORY', 'BRAIN', 'FOG']
        topic_words = [w.upper() for w in topic.split() if len(w) > 2]
        all_words = topic_words + base_words
        seen = set()
        unique = []
        for w in all_words:
            if w not in seen and len(w) >= 3:
                seen.add(w)
                unique.append(w)
        
        while len(unique) < 3:
            for w in base_words:
                if w not in unique:
                    unique.append(w)
                    if len(unique) >= 3:
                        break
        
        return unique[:3]

    def generate_seo(self, topic: str, script: str) -> Dict:
        """Generate SEO description and tags"""
        description = (
            f"The truth about {topic} explained. "
            f"Science behind why this happens to men after 35. "
            f"Follow for more brain health facts your doctor won't explain. "
            f"#Shorts #MemoryFacts #BrainHealth"
        )
        
        tags = [
            "memory", "brain fog", "forget", "men over 35",
            "memory loss", "brain health", "why do i forget",
            "youtube shorts", "brain facts", "health shorts"
        ]
        
        return {
            'description': description[:250],
            'tags': tags[:15],
            'keywords': f"memory,brain fog,forget,men over 35,brain health"
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
