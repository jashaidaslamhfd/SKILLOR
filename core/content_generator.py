"""Content Generator — Topic-Focused USA/UK Viral Scripts"""

import os
import json
import random
import re
from typing import Dict, List

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

    def generate_script(self, topic: str, angle: str, shock_angle: str = "", pattern: str = "curiosity_gap", suspense_score: int = 70) -> Dict:
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

        if pattern and pattern != "curiosity_gap":
            pattern_hooks = {
                'shock_visual': ('bold claim', f'A shocking visual statement about "{topic}" that makes eyes widen.'),
                'curiosity_gap': ('curiosity question', f'A direct "why does X happen" question about "{topic}".'),
                'contrarian': ('contrarian', f'Open by saying what people THINK about "{topic}" is wrong.'),
                'personal_stake': ('second-person callout', f'Start with "You" and describe something happening to viewer related to "{topic}".'),
                'countdown': ('countdown/list tease', f'Tease a specific number of signs about "{topic}".'),
            }
            if pattern in pattern_hooks:
                style_name, style_instruction = pattern_hooks[pattern]

        wps = AUDIO_CONFIG.WORDS_PER_MINUTE / 60.0

        # FIX: prompt now explicitly tells the model to output ONLY the raw
        # spoken line after each marker — no word-count hints, no style
        # labels, no instruction text repeated back. This is belt-and-
        # suspenders with the _extract()/_strip_leaked_instructions() fixes
        # below: even if the model still echoes some of this, the parser
        # now strips it before it ever reaches TTS.
        prompt = f"""Write a viral YouTube Shorts script about EXACTLY this topic: "{topic}"

Every section must be about "{topic}" only. Do NOT drift to other topics.

STYLE: Netflix mystery-documentary tone — dark curiosity and suspense about
the human body/brain/mind, NOT manipulation tactics or dark psychology
advice. Treat the topic like a mystery being unraveled, not a how-to.

VIRAL PATTERN: {pattern}
SUSPENSE LEVEL: {suspense_score}/100

Write these 5 sections. For EACH section, output ONLY the marker followed
by a colon and the FINAL SPOKEN LINE — nothing else. Do NOT include word
counts, style names, or any of these instructions in your answer.

### HOOK:
(Internally aim for 18-22 words. Style: {style_name}. {style_instruction}
Do NOT use "have you ever wondered" — vary opening words. End with "...")

### SHOCK:
(Internally aim for 8-10 words. One visual shock moment about "{topic}" —
makes eyes widen. Triggers glitch/shake effect in video. End with "...")

### SUSPENSE:
(Internally aim for 10-12 words. Shocking twist directly about "{topic}".
End with "...")

### STORY:
(Internally aim for 55-65 words. Explain real science behind "{topic}":
1) What's happening in body/brain — vivid, unsettling imagery
   (e.g. "your body is literally..." not dry textbook)
2) UNEXPECTED TWIST — surprising discovery that recontextualizes everything
Use "and", "but", "because", "which means" to connect — NO full stops mid-story
except ONE "..." for narrator breath. End by looping back to hook's exact theme.)

### CTR:
(Internally aim for 10-12 words. Style: {ctr_style}. {ctr_instruction})

CRITICAL RULES — FOLLOW EXACTLY:
- Second person "you/your"
- USA/UK English only
- NO hashtags, NO emojis
- TOTAL WORD COUNT across all 5 spoken lines: 100-115 words
- If under 100 words: EXPAND story with more vivid, unsettling details
- If over 115 words: TRIM story section
- Use "..." for pause markers (TTS breath timing)
- Word count calibrated to {AUDIO_CONFIG.WORDS_PER_MINUTE}wpm = 40-55s video
- Your answer must contain ONLY the 5 markers each followed by their final
  spoken line — no parenthetical notes, no word counts, no "Style:" labels"""

        raw = self._generate(prompt, max_tokens=500)

        hook     = self._extract("HOOK", raw)
        shock    = self._extract("SHOCK", raw)
        suspense = self._extract("SUSPENSE", raw)
        story    = self._extract("STORY", raw)
        ctr      = self._extract("CTR", raw)

        topic_lower = topic.lower()
        if not hook:
            hook = random.choice([
                f"Scientists just discovered something about {topic_lower} that changes everything you thought you knew...",
                f"Your brain does something with {topic_lower} that almost nobody talks about...",
                f"Most people get {topic_lower} completely wrong, and the real reason will surprise you...",
                f"Here's the one thing about {topic_lower} that experts rarely explain...",
            ])
        
        if not shock:
            if shock_angle:
                shock = shock_angle
            else:
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
        shock    = self._clean(shock)
        suspense = self._clean(suspense)
        story    = self._clean(story)
        ctr      = self._clean(ctr)

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
        seg('shock', shock)
        seg('pause', '0.3', is_pause=True)
        seg('suspense', suspense)
        seg('pause', '0.4', is_pause=True)

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

        # FIX: Strong warning if too short
        if word_count < 90:
            print(f"    ❌ CRITICAL: Only {word_count} words! Regenerating with expansion...")
            # Auto-expand story with more details
            expansion = f" And researchers discovered that this process involves your subconscious mind creating vivid neural pathways that feel completely real, which explains why {topic_lower} affects your memory so deeply."
            story += expansion
            # Rebuild segments
            segments = []
            t = 0.0
            seg('hook', hook)
            seg('pause', '0.5', is_pause=True)
            seg('shock', shock)
            seg('pause', '0.3', is_pause=True)
            seg('suspense', suspense)
            seg('pause', '0.4', is_pause=True)
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
            print(f"    📊 Expanded: {word_count} words | ~{round(t,1)}s")

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
        """
        FIX (root cause of voice reading out section labels/word-count
        hints/commas): the previous regex grabbed EVERYTHING right after
        "LABEL:" up to the next marker, with no filtering. The prompt
        itself puts parenthetical hints like "(18-22 words)" and lines
        like "Style: curiosity question." directly after each marker —
        and the LLM frequently echoes those instructions back verbatim
        instead of (or in addition to) the actual spoken line. That raw,
        unfiltered text — including word-count parentheticals and their
        internal commas — was going straight into segments[i]['text'] and
        therefore straight into the TTS voice. This is exactly the
        symptom described: "hook bhi parh raha, suspense bhi parh raha,
        comma bhi parh raha".

        Fix: after extracting the raw block for a label, we now run it
        through `_strip_leaked_instructions()` which removes parenthetical
        word-count/seconds hints, strips leaked "Style:"/instruction-style
        lines, and keeps only lines that look like real spoken content.
        """
        if not text:
            return ""
        pattern = rf'{label}:\s*(.+?)(?=\n\s*(?:###\s*)?(?:HOOK|SHOCK|SUSPENSE|STORY|CTR):|$)'
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        raw_block = m.group(1).strip() if m else ""
        return self._strip_leaked_instructions(raw_block)

    def _strip_leaked_instructions(self, block: str) -> str:
        """Remove any prompt-instruction residue from an extracted section
        before it can ever reach TTS."""
        if not block:
            return ""

        # Remove parenthetical hints anywhere, e.g. "(18-22 words)",
        # "(8-10 words, 3-4 seconds)", "(Internally aim for ...)"
        block = re.sub(r'\([^)]*\)', '', block)

        # Drop whole lines that are clearly leaked instructions rather
        # than spoken script content.
        instruction_line_patterns = [
            r'^\s*style\s*:', r'^\s*internally\b', r'^\s*aim for\b',
            r'^\s*do not\b', r'^\s*don\'t\b', r'^\s*end with\b',
            r'^\s*rules?\s*:', r'^\s*note\s*:', r'^\s*words?\s*:',
            r'^\s*seconds?\s*:', r'^\s*\d+\s*-\s*\d+\s*words\b',
            r'^\s*###',
        ]
        lines = block.split('\n')
        kept = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if any(re.search(p, stripped, re.IGNORECASE) for p in instruction_line_patterns):
                continue
            kept.append(stripped)

        result = ' '.join(kept).strip()

        # Final safety net: strip any stray standalone word-count/seconds
        # fragments that survived as inline text, e.g. "18-22 words, 6-8
        # seconds" appearing without parentheses.
        result = re.sub(r'\b\d+\s*-\s*\d+\s*(?:words?|seconds?)\b', '', result, flags=re.IGNORECASE)
        result = re.sub(r'\s+,', ',', result)
        result = re.sub(r',\s*,', ',', result)
        result = re.sub(r'\s+', ' ', result).strip()
        result = result.strip(',').strip()

        return result

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
            words = random.choice(fallback_phrases)

        return words[:4]
