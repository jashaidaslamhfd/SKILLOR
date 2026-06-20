"""Content Generator — Topic-Focused USA/UK Viral Scripts"""

import os
import json
from typing import Dict, List
import re

try:
    from groq import Groq
except ImportError:
    Groq = None

from config.settings import API_KEYS, NICHE_CONFIG, AUDIO_CONFIG


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
            {"role": "system", "content": "You are a viral short-form video script writer for USA/UK dark psychology and science mystery channels. Every section must be tightly focused on ONE topic."},
            {"role": "user", "content": prompt}
        ]
        if self.client:
            try:
                r = self.client.chat.completions.create(
                    model=self.model, messages=msgs,
                    temperature=0.85, max_tokens=max_tokens, top_p=0.9,
                    timeout=30
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
        Video structure:
        HOOK     6-8s   ~18-22 words  — curiosity question about THIS topic
        PAUSE    0.5s   — breath
        SHOCK    3-4s   ~8-10 words   — visual shock moment (NEW: for suspense effects)
        PAUSE    0.3s   — breath
        SUSPENSE 4-5s   ~10-12 words  — shocking twist about THIS topic
        PAUSE    0.4s   — breath
        STORY    25-30s ~55-65 words  — science/truth about THIS topic, one mid-story breath
        PAUSE    0.4s   — breath
        CTR      4-5s   ~10-12 words  — follow/subscribe CTA

        ALL sections must be about the SAME topic: {topic}
        """
        import random
        hook_styles = [
            ('curiosity question', f'A direct "why does X happen" question about "{topic}" — no "have you ever wondered" phrasing.'),
            ('bold claim', f'A bold, surprising factual claim about "{topic}" stated as a statement, not a question.'),
            ('second-person callout', f'Start with "You" and describe something the viewer does without realizing related to "{topic}".'),
            ('countdown/list tease', f'Tease a specific number of signs/reasons/facts about "{topic}" (e.g. "3 signs...", "the one reason...").'),
            ('contrarian', f'Open by saying what people THINK about "{topic}" is wrong, then tease the real explanation.'),
        ]
        style_name, style_instruction = random.choice(hook_styles)

        ctr_styles = [
            ('urgent follow', 'Tell them to follow now because tomorrow reveals more.'),
            ('curiosity continuation', 'Tease that part 2 explains the rest — follow so they don\'t miss it.'),
            ('direct ask', 'Plainly ask them to follow/like if this surprised them.'),
            ('community framing', 'Invite them to join others who follow for this content.'),
        ]
        ctr_style, ctr_instruction = random.choice(ctr_styles)

        # FIX: Increased word count target to 100-120 words for 40-55s video
        # 120 wpm = 2 words/sec → 100 words = 50s, 120 words = 60s
        # Target: 100-115 words = 42-48s (perfect range)
        prompt = f"""Write a viral YouTube Shorts script about EXACTLY this topic: "{topic}"

Every section must be about "{topic}" only. Do NOT drift to other topics.

STYLE: Netflix mystery-documentary tone — dark curiosity and suspense about
the human body/brain/mind, NOT manipulation tactics or dark psychology
advice. Treat the topic like a mystery being unraveled, not a how-to.

Write these 5 sections:

HOOK: (18-22 words)
Style: {style_name}. {style_instruction}
Do NOT use the phrase "have you ever wondered" — vary your opening words.
End with "..."

SHOCK: (8-10 words)
NEW: A one-sentence visual shock moment about "{topic}" — something that
makes the viewer's eyes widen. This triggers the glitch/shake visual effect.
End with "..."

SUSPENSE: (10-12 words)
A one-sentence shocking twist directly about "{topic}".
End with "..."

STORY: (55-65 words)
Explain the real science behind "{topic}", but structure it as:
1) what's actually happening in the body/brain (use vivid, almost
   unsettling imagery — e.g. "your body is literally..." rather than dry
   textbook phrasing)
2) an UNEXPECTED TWIST — a surprising reason/discovery the viewer wouldn't
   guess, that recontextualizes what they just heard
Use "and", "but", "because", "which means" to connect sentences — NO full
stops mid-story except ONE "..." naturally placed where narrator breathes.
End by looping back to the hook's exact theme/question so the story closes
like a loop — the viewer should feel like rewatching connects the ending
back to the beginning.

CTR: (10-12 words)
Style: {ctr_style}. {ctr_instruction}

RULES:
- Second person "you/your"  
- USA/UK English only
- NO hashtags NO emojis
- Total 100-115 words across all 5 sections
- FIX: word counts calibrated to {AUDIO_CONFIG.WORDS_PER_MINUTE}wpm voice speed
  so the finished video lands in the 40-55s target range."""

        raw = self._generate(prompt, max_tokens=500)

        hook     = self._extract("HOOK", raw)
        shock    = self._extract("SHOCK", raw)  # NEW
        suspense = self._extract("SUSPENSE", raw)
        story    = self._extract("STORY", raw)
        ctr      = self._extract("CTR", raw)

        # Topic-specific fallbacks with variety
        topic_lower = topic.lower()
        if not hook:
            hook = random.choice([
                f"Scientists just discovered something about {topic_lower} that changes everything you thought you knew...",
                f"Your brain does something with {topic_lower} that almost nobody talks about...",
                f"Most people get {topic_lower} completely wrong, and the real reason will surprise you...",
                f"Here's the one thing about {topic_lower} that experts rarely explain...",
            ])
        
        # NEW: SHOCK fallback
        if not shock:
            shock = random.choice([
                f"And what happens next with {topic_lower}... will terrify you.",
                f"But {topic_lower} has a dark side nobody mentions...",
                f"And the worst part about {topic_lower}... is still coming.",
                f"Wait until you see what {topic_lower} actually does...",
            ])
        
        if not suspense:
            suspense = f"And the terrifying truth about {topic_lower}... nobody is telling you."
        
        if not story:
            story = (f"The science behind {topic_lower} is more shocking than you realize, "
                    f"and your brain is actually protecting you in the most bizarre way possible "
                    f"but this same mechanism... can be exploited by the wrong people, "
                    f"and once you understand this you will never look at {topic_lower} the same way again.")
        
        if not ctr:
            ctr = random.choice([
                "Follow now because tomorrow we reveal exactly how to use this.",
                "Like and follow if this just changed how you see things.",
                "Follow for more — part two explains the rest tomorrow.",
            ])

        hook     = self._clean(hook)
        shock    = self._clean(shock)  # NEW
        suspense = self._clean(suspense)
        story    = self._clean(story)
        ctr      = self._clean(ctr)

        # Build segments with SHOCK type for visual effects
        wps = AUDIO_CONFIG.WORDS_PER_MINUTE / 60.0
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
        seg('pause', '0.5', is_pause=True)
        seg('shock', shock)  # NEW: triggers glitch/shake visual effect
        seg('pause', '0.3', is_pause=True)
        seg('suspense', suspense)
        seg('pause', '0.4', is_pause=True)

        # Story — split at "..." if present
        if '...' in story:
            parts = story.split('...', 1)
            seg('story', parts[0].strip() + '...')
            seg('pause', '0.4', is_pause=True)
            second_half = parts[1].replace('...', ',').strip()
            seg('story', second_half)
        else:
            sw = story.split()
            mid = len(sw) // 2
            seg('story', ' '.join(sw[:mid]))
            seg('pause', '0.35', is_pause=True)
            seg('story', ' '.join(sw[mid:]))

        seg('pause', '0.4', is_pause=True)
        seg('ctr', ctr)

        full = ' '.join(s['text'] for s in segments if not s.get('is_pause'))
        word_count = len(full.split())
        print(f"    📊 Topic: '{topic}' | {word_count} words | ~{round(t,1)}s")

        # FIX: Warn if word count is too low (will cause short video)
        if word_count < 90:
            print(f"    ⚠️ WARNING: Only {word_count} words — video will be <40s!")
        elif word_count > 130:
            print(f"    ⚠️ WARNING: {word_count} words — video may exceed 55s!")

        return {
            'full_script': full,
            'segments': segments,
            'word_count': word_count,
            'duration': round(t, 2),
            'hook': hook, 'shock': shock, 'suspense': suspense,
            'story': story, 'ctr': ctr
        }

    def _extract(self, label: str, text: str) -> str:
        if not text:
            return ""
        pattern = rf'{label}:\s*(.+?)(?=\n\s*(?:HOOK|SHOCK|SUSPENSE|STORY|CTR):|$)'
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    def _clean(self, text: str) -> str:
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'[^\x00-\x7F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = text.strip('"').strip("'").strip()
        return text

    def generate_title(self, topic: str) -> str:
        import re
        prompt = f"""Write ONE viral YouTube Shorts title about: {topic}
Rules: 2-4 real English words + 1 emoji at the end. Under 40 chars total.
The words must be readable text that explains the topic — NOT just emojis or symbols.
Do NOT wrap the title in quote marks.
Example format (without quotes): Dark Mind Secrets 🧠
Return ONLY the title, nothing else, no quote marks."""
        title = self._generate(prompt, max_tokens=60)

        if title:
            title = title.strip().strip('"').strip("'").strip()

        has_words = bool(title) and len(re.findall(r'[A-Za-z]{2,}', title)) >= 2

        if not has_words or len(title) > 80:
            import random
            title = random.choice([
                f"The Dark Truth About {topic.title()}",
                f"Why {topic.title()} Happens To You",
                f"The Science Behind {topic.title()} Nobody Tells You",
                f"What {topic.title()} Really Does To Your Brain",
            ])
        return title.strip()[:60]

    def generate_seo(self, topic: str, script: str) -> Dict:
        tags = [
            "psychology", "dark psychology", "brain science", "mind control",
            "science facts", "shocking facts", "human behavior", "neuroscience",
            topic.replace(" ", ""), "psychology facts", "mindblowing",
            "science mystery", "brain hacks", "psychology explained", "viral facts"
        ]
        return {
            'description': (
                f"The shocking truth about {topic} revealed. "
                f"Science explains what really happens and why nobody tells you. "
                f"Follow for daily mind-blowing psychology and science facts. "
                f"#psychology #darkpsychology #sciencefacts #mindblowing #{topic.replace(' ','')}"),
            'tags': tags[:15],
            'keywords': f"psychology,{topic},brain,dark psychology,science"
        }

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        prompt = f"""Write ONE short, complete, punchy thumbnail phrase (2-4 words)
that teases this topic: "{topic}"
Rules:
- Must read as a complete thought on its own, not a cut-off sentence
- ALL CAPS
- No periods, no emoji
- Example: "BRAIN'S DARK SECRET" or "THIS CHANGES EVERYTHING"
Return ONLY the phrase, nothing else."""
        phrase = self._generate(prompt, max_tokens=20)

        if phrase:
            phrase = phrase.strip().strip('"').strip("'").upper()
            words = [w for w in phrase.split() if w]
        else:
            words = []

        if not (2 <= len(words) <= 4) or any(len(w) < 2 for w in words):
            fallback_phrases = [
                ["HIDDEN", "TRUTH"],
                ["MIND", "SECRET", "REVEALED"],
                ["THIS", "CHANGES", "EVERYTHING"],
                ["WAIT", "FOR", "IT"],
            ]
            import random
            words = random.choice(fallback_phrases)

        return words[:4]
