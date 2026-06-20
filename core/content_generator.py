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
                # FIX: timeout added — Groq SDK call had none, could hang
                # indefinitely on slow/throttled responses.
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
        HOOK     6-8s  ~20 words  — curiosity question about THIS topic
        PAUSE    0.6s  — breath
        SUSPENSE 4s    ~12 words  — shocking twist about THIS topic
        PAUSE    0.4s  — breath
        STORY    30s   ~65 words  — science/truth about THIS topic, one mid-story breath
        PAUSE    0.4s  — breath
        CTR      5s    ~15 words  — follow/subscribe CTA

        ALL sections must be about the SAME topic: {topic}
        """
        # FIX: a single hardcoded example in the prompt caused the model to
        # near-copy that exact phrasing ("Have you ever wondered why X...
        # because science just revealed something terrifying.") on almost
        # every video. Viewers pattern-recognize an identical-sounding hook
        # within the first second and swipe away — this is very likely the
        # main driver of the 65% swipe-away rate. Rotating through several
        # structurally different hook styles forces real variety.
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

        prompt = f"""Write a viral YouTube Shorts script about EXACTLY this topic: "{topic}"

Every section must be about "{topic}" only. Do NOT drift to other topics.

STYLE: Netflix mystery-documentary tone — dark curiosity and suspense about
the human body/brain/mind, NOT manipulation tactics or dark psychology
advice. Treat the topic like a mystery being unraveled, not a how-to.

Write these 4 sections:

HOOK: (16-18 words)
Style: {style_name}. {style_instruction}
Do NOT use the phrase "have you ever wondered" — vary your opening words.
End with "..."

SUSPENSE: (9-11 words)
A one-sentence shocking twist directly about "{topic}".
End with "..."

STORY: (48-54 words)
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
- Total 85-95 words across all 4 sections
- FIX: word counts calibrated to {AUDIO_CONFIG.WORDS_PER_MINUTE}wpm voice speed
  so the finished video lands in the 40-55s target range — going over
  these counts pushes the video past 55s."""

        raw = self._generate(prompt, max_tokens=450)

        hook     = self._extract("HOOK", raw)
        suspense = self._extract("SUSPENSE", raw)
        story    = self._extract("STORY", raw)
        ctr      = self._extract("CTR", raw)

        # Topic-specific fallbacks — FIX: rotate fallback hook phrasing too,
        # so even a Groq/parsing failure doesn't always produce the exact
        # same generic hook sentence.
        topic_lower = topic.lower()
        if not hook:
            hook = random.choice([
                f"Scientists just discovered something about {topic_lower} that changes everything you thought you knew...",
                f"Your brain does something with {topic_lower} that almost nobody talks about...",
                f"Most people get {topic_lower} completely wrong, and the real reason will surprise you...",
                f"Here's the one thing about {topic_lower} that experts rarely explain...",
            ])
        if not suspense:
            suspense = f"And the terrifying truth about {topic_lower}... nobody is telling you."
        if not story:
            # FIX: shortened to match the new ~48-54 word story target —
            # the old fallback was 66 words, which alone would push videos
            # past the 55s ceiling whenever Groq parsing failed.
            story = (f"The science behind {topic_lower} is more shocking than you realize, "
                    f"and your brain is actually protecting you in the most bizarre way possible "
                    f"but this same mechanism... can be exploited by the wrong people, "
                    f"and once you understand this you will never look at {topic_lower} the same way again.")
        if not ctr:
            # FIX: shortened to match the new ~10-12 word CTR target
            ctr = random.choice([
                "Follow now because tomorrow we reveal exactly how to use this.",
                "Like and follow if this just changed how you see things.",
                "Follow for more — part two explains the rest tomorrow.",
            ])

        hook     = self._clean(hook)
        suspense = self._clean(suspense)
        story    = self._clean(story)
        ctr      = self._clean(ctr)

        # Build segments
        # FIX: was hardcoded to 130 wpm, but AUDIO_CONFIG.WORDS_PER_MINUTE
        # (used by the actual TTS voice) is 120 — the mismatch meant these
        # estimated segment durations didn't match real speech length.
        # (video_assembler.py now re-aligns durations to real word_timings
        # anyway, but keeping this consistent avoids confusing estimates.)
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
        seg('pause', '0.6', is_pause=True)
        seg('suspense', suspense)
        seg('pause', '0.4', is_pause=True)

        # Story — split at "..." if present, otherwise split at midpoint
        if '...' in story:
            parts = story.split('...', 1)
            seg('story', parts[0].strip() + '...')
            seg('pause', '0.4', is_pause=True)
            # FIX: if the model included a second "..." later in the story,
            # strip it so it doesn't read as an extra unintended pause point
            # that the caption/video timing isn't actually accounting for.
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
        text = text.strip()
        # FIX: Groq sometimes wraps generated lines in quote marks copied
        # from prompt examples — strip any leading/trailing quotes so they
        # don't end up spoken aloud or burned into captions/title text.
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

        # FIX: Groq was literally copying the quotes from the example
        # format ("Dark Mind Secrets 🧠") into its output, producing titles
        # like '"Dark Psychology 🧠"' with literal quote marks shown on
        # YouTube. Strip any leading/trailing quote characters.
        if title:
            title = title.strip().strip('"').strip("'").strip()

        # FIX: validate the title actually contains real words, not just
        # emoji/symbols. Without this check, an emoji-only response (e.g.
        # "🤐🤯") slipped straight to YouTube as the video title — this is
        # what was causing titles with no searchable text at all.
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
        # FIX: previously this just split the raw topic string into pieces
        # (e.g. "your right" -> "YOUR", "RIGHT"), which produced broken,
        # incomplete-looking phrases on the thumbnail ("YOUR" / "RIGHT" /
        # "DIDN'T INCLUDE"). Now we ask the model for a short, complete,
        # standalone hook phrase instead of fragmenting the topic.
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

        # Validate: 2-4 real words, no leftover fragments
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
