"""Content Generator - Topic-Focused USA/UK Viral Scripts - 2026 Algorithm Optimized"""

import os
import json
import random
from typing import Dict, List
import re

try:
    from groq import Groq
except ImportError:
    Groq = None

from config.settings import API_KEYS, NICHE_CONFIG, SEO_CONFIG


class ContentGenerator:
    def __init__(self):
        self.api_key = API_KEYS.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        self.client = None
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        self._init_client()

    def _init_client(self):
        if not Groq or not self.api_key:
            return
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception:
            self.client = None

    def _generate(self, prompt: str, max_tokens: int = 600) -> str:
        msgs = [
            {"role": "system", "content": "You are a viral short-form video script writer for USA/UK dark psychology and science mystery channels. Every section must be tightly focused on ONE topic. Create content optimized for 2026 YouTube Shorts algorithm."},
            {"role": "user", "content": prompt}
        ]
        if self.client:
            try:
                r = self.client.chat.completions.create(
                    model=self.model, messages=msgs,
                    temperature=0.85, max_tokens=max_tokens, top_p=0.9
                )
                return r.choices[0].message.content.strip()
            except Exception as e:
                print(f"Groq SDK error: {e}")
        import requests
        try:
            r = requests.post(f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={"model": self.model, "messages": msgs,
                      "temperature": 0.85, "max_tokens": max_tokens},
                timeout=30)
            data = r.json()
            return data['choices'][0]['message']['content'].strip() if 'choices' in data else ""
        except Exception as e:
            print(f"HTTP error: {e}")
            return ""

    def generate_script(self, topic: str, angle: str) -> Dict:
        """
        Video structure optimized for 2026 Shorts algorithm:
        HOOK     0-3s   ~15 words  - instant pattern interrupt
        PAUSE    0.35s  - breath
        SUSPENSE 3-7s   ~12 words  - shocking twist
        PAUSE    0.3s   - breath
        STORY    7-40s  ~70 words  - science/truth, one mid-story breath
        PAUSE    0.3s   - breath
        CTR      40-45s ~12 words  - follow/subscribe CTA

        ALL sections must be about the SAME topic: {topic}
        """
        prompt = f"""Write a viral YouTube Shorts script about EXACTLY this topic: "{topic}"

Every section must be about "{topic}" only. Do NOT drift to other topics.

Write these 4 sections:

HOOK: (15-18 words)
A shocking curiosity question about "{topic}". 
Example format: "What if I told you [topic thing]... because scientists just discovered something terrifying."
End with "..."

SUSPENSE: (10-12 words)
A one-sentence shocking twist directly about "{topic}".
End with "..."

STORY: (65-70 words)
Explain the real science/psychology behind "{topic}".
Use "and", "but", "because", "which means" to connect sentences - NO full stops mid-story except ONE "..." naturally placed where narrator breathes.
Loop back to hook theme at the end.

CTR: (12-14 words)
Urgent follow/subscribe CTA. Example: "Follow right now because tomorrow we reveal the dark truth."

RULES:
- Second person "you/your"  
- USA/UK English only
- NO hashtags NO emojis
- Total 105-115 words across all 4 sections
- 2026 optimized: instant hook, no fluff, high retention"""

        raw = self._generate(prompt, max_tokens=450)

        hook     = self._extract("HOOK", raw)
        suspense = self._extract("SUSPENSE", raw)
        story    = self._extract("STORY", raw)
        ctr      = self._extract("CTR", raw)

        # Topic-specific fallbacks
        topic_lower = topic.lower()
        if not hook:
            hook = f"What if I told you {topic_lower} happens for a terrifying reason... because scientists just discovered the dark truth."
        if not suspense:
            suspense = f"And the terrifying truth about {topic_lower}... nobody is telling you."
        if not story:
            story = (f"The science behind {topic_lower} is more shocking than you realize and researchers have spent decades trying to understand exactly why it happens and what they found is that your brain is actually protecting you in the most bizarre way possible "
                    f"but this same mechanism... can be exploited by the wrong people and once you understand this you will never look at {topic_lower} the same way again.")
        if not ctr:
            ctr = "Follow right now because tomorrow we reveal exactly how to use this to your advantage."

        hook     = self._clean(hook)
        suspense = self._clean(suspense)
        story    = self._clean(story)
        ctr      = self._clean(ctr)

        # Build segments
        wps = 145 / 60.0  # 2026: Faster pace for retention
        segments = []
        t = 0.0

        def seg(stype, text, is_pause=False):
            nonlocal t
            if not str(text).strip():
                return
            dur = float(text) if is_pause else round(len(text.split()) / wps, 2)
            segments.append({
                'type': stype,
                'text': '' if is_pause else text.strip(),
                'duration': dur,
                'start': round(t, 2),
                'is_pause': is_pause
            })
            t += dur

        seg('hook', hook)
        seg('pause', '0.35', is_pause=True)
        seg('suspense', suspense)
        seg('pause', '0.3', is_pause=True)

        # Story - split at "..." if present, otherwise split at midpoint
        if '...' in story:
            parts = story.split('...', 1)
            seg('story', parts[0].strip() + '...')
            seg('pause', '0.3', is_pause=True)
            seg('story', parts[1].strip())
        else:
            sw = story.split()
            mid = len(sw) // 2
            seg('story', ' '.join(sw[:mid]))
            seg('pause', '0.3', is_pause=True)
            seg('story', ' '.join(sw[mid:]))

        seg('pause', '0.3', is_pause=True)
        seg('ctr', ctr)

        full = ' '.join(s['text'] for s in segments if not s.get('is_pause'))
        print(f"    📊 Topic: '{topic}' | {len(full.split())} words | ~{round(t,1)}s")

        return {
            'full_script': full,
            'segments': segments,
            'word_count': len(full.split()),
            'duration': round(t, 2),
            'hook': hook, 'suspense': suspense,
            'story': story, 'ctr': ctr
        }

    def _extract(self, label: str, text: str) -> str:
        if not text:
            return ""
        pattern = rf'{label}:\s*(.+?)(?=\n\s*(?:HOOK|SUSPENSE|STORY|CTR):|$)'
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    def _clean(self, text: str) -> str:
        text = re.sub(r'#\w+', '', text)
        # Keep ellipsis, remove other non-ASCII
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_title(self, topic: str) -> str:
        """2026: EXACTLY 4 words + 1 emoji for maximum viral impact"""
        prompt = f"""Write ONE viral YouTube Shorts title about: "{topic}"
STRICT RULES (2026 algorithm optimized):
- EXACTLY 4 words only (no more, no less)
- 1 emoji at the end (choose from: 🤯 ⚠️ 🧠 🚫 ❌ 💀)
- Max 60 characters
- Shocking/Curiosity hook
- USA/UK English
- Power words: Dark, Hidden, Banned, Secret, Illegal, Truth
- NO punctuation except the emoji

Examples: 
- "Your Brain Is Lying 🧠"
- "This Is Illegal Now 🚫" 
- "Dark Secret Revealed ⚠️"
- "Truth They Hide 🤯"

Return ONLY the title, nothing else."""
        
        title = self._generate(prompt, max_tokens=30)
        
        # Enforce 4 words + emoji
        if title:
            clean_title = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]', '', title).strip()
            words = clean_title.split()
            
            if len(words) > 4:
                clean_title = ' '.join(words[:4])
            elif len(words) < 4:
                power_words = ["Dark", "Hidden", "Secret", "Truth", "Shocking"]
                while len(words) < 4:
                    words.append(power_words[len(words) % len(power_words)])
                clean_title = ' '.join(words[:4])
            
            emojis = ['🤯', '⚠️', '🧠', '🚫', '❌', '💀', '🔥']
            title = f"{clean_title} {random.choice(emojis)}"
        else:
            title = f"Dark Truth About {topic.title()} 🤯"
        
        return title.strip()[:60]

    def generate_seo(self, topic: str, script: str) -> Dict:
        """2026 SEO optimized for YouTube Shorts algorithm"""
        tags = [
            "psychology shorts",
            "dark psychology",
            "brain science",
            "mind control",
            "shocking facts",
            "human behavior",
            "neuroscience",
            "psychology tricks",
            "mental health",
            "viral shorts",
            topic.replace(" ", ""),
            "2026 trending"
        ]
        
        description = (
            f"🤯 {topic.upper()} — The shocking truth nobody talks about.\n\n"
            f"Science reveals what really happens when {topic}. "
            f"Your brain will never be the same after this.\n\n"
            f"⏱️ 0:00 Hook\n"
            f"⏱️ 0:03 The Dark Truth\n" 
            f"⏱️ 0:15 Science Explained\n"
            f"⏱️ 0:40 The Solution\n\n"
            f"🔔 Subscribe for daily mind-blowing psychology facts!\n"
            f"💬 Comment 'YES' if this shocked you!\n"
            f"👇 Save this for later!\n\n"
            f"#shorts #psychology #darkpsychology #mindcontrol #brainhacks "
            f"#{topic.replace(' ','')} #viral #trending #2026 #fyp"
        )
        
        return {
            'description': description[:500],
            'tags': tags[:SEO_CONFIG.TAGS_COUNT],
            'keywords': f"psychology,{topic},brain,2026,viral,shorts,dark psychology"
        }

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Generate 3 big words for thumbnail"""
        words = topic.upper().split()[:2]
        fillers = ["TRUTH", "HIDDEN", "SECRET", "DARK", "BANNED"]
        while len(words) < 3:
            words.append(fillers[len(words) % len(fillers)])
        return words[:3]
