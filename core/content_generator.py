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
            ('curiosity question', f'A short, direct "why does X happen" question about "{topic}" — no "have you ever wondered" phrasing.'),
            ('bold claim', f'A short, surprising statement about "{topic}" stated plainly, not as a question.'),
            ('second-person callout', f'Start with "You" and name something the viewer does without realizing, related to "{topic}".'),
            ('countdown/list tease', f'Tease a specific number of signs/reasons about "{topic}" (e.g. "3 signs...", "one reason...").'),
            ('contrarian', f'Open by saying what people THINK about "{topic}" is wrong, in one short line.'),
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
                'shock_visual': ('bold claim', f'A short, warm, surprising statement about "{topic}" that makes the listener feel recognized, not alarmed.'),
                'curiosity_gap': ('curiosity question', f'A short, direct "why does X happen" question about "{topic}".'),
                'contrarian': ('contrarian', f'Open by saying what people THINK about "{topic}" is wrong, in one short line.'),
                'personal_stake': ('second-person callout', f'Start with "You" and name something happening to the viewer related to "{topic}".'),
                'countdown': ('countdown/list tease', f'Tease a specific number of signs about "{topic}".'),
            }
            if pattern in pattern_hooks:
                style_name, style_instruction = pattern_hooks[pattern]

        wps = AUDIO_CONFIG.WORDS_PER_MINUTE / 60.0

        # FIX (swipe-away rate / retention): the hook was previously
        # 18-22 words, which at ~130wpm takes 8-10 seconds to fully land --
        # far too slow. Shorts/Reels retention lives or dies in the first
        # 1-2 seconds; if the curiosity payload doesn't land almost
        # immediately, viewers swipe before the hook even finishes. Cut
        # the hook to 10-14 words (roughly 4-6 seconds) so the curiosity
        # gap opens fast, and moved the "..." breath earlier so there's an
        # audible micro-pause right after the hook lands instead of a long
        # uninterrupted sentence.
        #
        # FIX: prompt now explicitly tells the model to output ONLY the raw
        # spoken line after each marker — no word-count hints, no style
        # labels, no instruction text repeated back. This is belt-and-
        # suspenders with the _extract()/_strip_leaked_instructions() fixes
        # below: even if the model still echoes some of this, the parser
        # now strips it before it ever reaches TTS.
        #
        # FIX (heart-touching tone): reframed from "shock/dark psychology"
        # toward warm, human storytelling — still curious and suspenseful,
        # but landing on empathy and connection rather than alarm.
        prompt = f"""Write a short, emotionally resonant YouTube Shorts script about EXACTLY this topic: "{topic}"

Every section must be about "{topic}" only. Do NOT drift to other topics.

STYLE: Warm, human, heart-touching storytelling tone -- like a thoughtful
friend sharing something quietly fascinating about being human. Curious and
gently suspenseful, NOT shocking, NOT dark-psychology, NOT clickbait-scary.
Treat the topic as something tender and relatable about the human
experience -- something that makes the listener feel SEEN and understood,
not alarmed. Avoid words like "terrifying", "bizarre", "shocking", "dark
side". Prefer words like "quietly", "gently", "without even realizing",
"the part of you that".

VIRAL PATTERN: {pattern}
EMOTIONAL DEPTH: {suspense_score}/100 (higher = more tender/vulnerable, not more shocking)

CRITICAL FOR RETENTION: the HOOK is the single most important line in this
script. A viewer decides whether to keep watching within 1-2 seconds. The
hook must be SHORT and land its curiosity instantly -- no warm-up, no
throat-clearing, no setup before the interesting part.

Write these 5 sections. For EACH section, output ONLY the marker followed
by a colon and the FINAL SPOKEN LINE -- nothing else. Do NOT include word
counts, style names, or any of these instructions in your answer.

### HOOK:
(STRICT: 10-14 words MAXIMUM -- this is non-negotiable. Style: {style_name}.
{style_instruction} Warm and inviting, not alarming. Do NOT use "have you
ever wondered". The very first 3-4 words must already contain the
curiosity hook -- do not spend words on setup. End with "..." right at the
natural breath after the line lands.)

### SHOCK:
(Internally aim for 8-10 words. Not a "shock" in the scary sense -- a small
moment of tender recognition about "{topic}" that makes the listener think
"that's so me". End with "..." as a soft breath before the next thought.)

### SUSPENSE:
(Internally aim for 10-12 words. A gentle turn toward the emotional truth
behind "{topic}" -- the human reason, not a scary twist. End with "..."
right before revealing why it matters.)

### STORY:
(Internally aim for 58-68 words. Explain the real science/reason behind
"{topic}" with warmth:
1) What's actually happening, explained simply and tenderly -- like
   explaining it to someone you care about, not a textbook
2) A touching reframe -- a detail that makes the listener feel more
   understood or less alone, not a "twist" for shock value
Use "and", "but", "because", "which means" to connect -- NO full stops
mid-story except ONE "..." placed at a natural emotional beat (e.g. right
before the touching reframe, like taking a breath before saying something
that matters). End by gently looping back to the hook's exact theme.)

### CTR:
(Internally aim for 10-12 words. Style: {ctr_style}. {ctr_instruction}
Warm invitation, not urgency/FOMO pressure.)

CRITICAL RULES -- FOLLOW EXACTLY:
- Second person "you/your"
- USA/UK English only
- NO hashtags, NO emojis
- HOOK is HARD-CAPPED at 14 words -- count it before answering
- TOTAL WORD COUNT across all 5 spoken lines: 100-115 words
- If under 100 words: EXPAND the story with one more tender, specific detail
  (never expand the hook past 14 words)
- If over 115 words: TRIM the story section
- Place "..." only where a real person would naturally pause to breathe --
  typically right after a complete thought and right before a shift in
  emotional weight. Never place "..." mid-clause.
- Word count calibrated to {AUDIO_CONFIG.WORDS_PER_MINUTE}wpm = 40-55s video
- Your answer must contain ONLY the 5 markers each followed by their final
  spoken line -- no parenthetical notes, no word counts, no "Style:" labels"""

        raw = self._generate(prompt, max_tokens=500)

        hook     = self._extract("HOOK", raw)
        shock    = self._extract("SHOCK", raw)
        suspense = self._extract("SUSPENSE", raw)
        story    = self._extract("STORY", raw)
        ctr      = self._extract("CTR", raw)

        topic_lower = topic.lower()
        if not hook:
            hook = random.choice([
                f"Nobody talks about why {topic_lower} really happens...",
                f"Your body has a quiet reason for {topic_lower}...",
                f"Here's what {topic_lower} is actually trying to tell you...",
                f"There's a gentle truth behind {topic_lower}...",
            ])
        
        if not shock:
            if shock_angle:
                shock = shock_angle
            else:
                shock = random.choice([
                    f"And the part nobody mentions about {topic_lower}... will make sense of so much.",
                    f"But {topic_lower} is quietly trying to protect you...",
                    f"And once you see it, {topic_lower} feels a lot less strange.",
                    f"It turns out {topic_lower} is your body's way of caring for you...",
                ])
        
        if not suspense:
            suspense = f"And the real reason behind {topic_lower}... is more human than you'd think."
        
        if not story:
            story = (f"The science behind {topic_lower} is gentler than you'd expect, "
                    f"and your brain is actually trying to look out for you in a quiet, automatic way "
                    f"but the part that really matters... is what it says about how deeply your body "
                    f"pays attention to you, even when you're not paying attention to yourself.")
        
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
            expansion = f" And the quiet truth is, your mind has been doing this for you your whole life, gently making sense of {topic_lower} long before you ever noticed it happening."
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
            "psychology", "human behavior", "brain science", "self discovery",
            "science facts", "relatable facts", "mental health awareness", "neuroscience",
            topic.replace(" ", ""), "psychology facts", "mindblowing",
            "science mystery", "emotional intelligence", "psychology explained", "viral facts"
        ]
        return {
            'description': (
                f"The gentle truth about {topic}, explained. "
                f"Science behind why this happens, and why it matters more than you'd think. "
                f"Follow for daily stories about the quiet science of being human. "
                f"#psychology #humanbehavior #sciencefacts #mindblowing #{topic.replace(' ','')}"),
            'tags': tags[:15],
            'keywords': f"psychology,{topic},brain,human behavior,science"
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
