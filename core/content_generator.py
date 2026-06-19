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

# IMPORT ALL DYNAMIC CONFIGS AND REMOVE HARDCODED PROMPTS
from config.settings import API_KEYS, NICHE_CONFIG, SEO_CONFIG
from config import prompts as pr


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
            {"role": "system", "content": "You are a viral short-form video content strategist for USA/UK audiences. Your target is absolute uniqueness based strictly on the user topic. Never output intro/outro filler context."},
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
        Uses VIRAL_SCRIPT_GENERATOR from prompts.py to maintain 45-55 seconds strict duration flow.
        """
        # Dynamic prompt allocation from prompts.py
        prompt = pr.VIRAL_SCRIPT_GENERATOR.format(topic=topic, angle=angle)
        raw_script = self._generate(prompt, max_tokens=500)
        
        if not raw_script or len(raw_script.split()) < 100:
            # Topic-specific solid high-retention fallback
            topic_lower = topic.lower()
            raw_script = (
                f"What if I told you that {topic_lower} is hiding a dark truth that scientists just uncovered. "
                f"Imagine walking into a room and realizing your mind has been quietly manipulated without your consent. "
                f"But here's what they don't tell you... it is happening right now inside your subconscious brain. "
                f"Picture this, your neural pathways are constantly receiving secret signals forcing you to react. "
                f"This shocking mechanism completely overrides your logical thinking system which means you are not in control. "
                f"Most people think they are safe but this psychological trigger is secretly being exploited by elite architects. "
                f"Once you understand this forbidden loop... your perception of reality will be shattered forever. "
                f"Comment if you experienced this and watch this loop twice because tomorrow we expose the dangerous group behind it."
            )

        raw_script = self._clean(raw_script)
        
        # Split into analytical blocks for the timeline assembly
        words_list = raw_script.split()
        total_w = len(words_list)
        
        # Dynamic calculation based on settings 145WPM conversation limits
        wps = 2.6  
        
        segments = []
        # Breakdown script into structured sub-components natively mapped for rendering loops
        h_end = int(total_w * 0.15)
        s_end = h_end + int(total_w * 0.12)
        st_end = s_end + int(total_w * 0.60)
        
        hook_text = " ".join(words_list[:h_end])
        suspense_text = " ".join(words_list[h_end:s_end])
        story_text = " ".join(words_list[s_end:st_end])
        ctr_text = " ".join(words_list[st_end:])
        
        t = 0.0
        def add_seg(stype, text, is_pause=False, pause_dur=0.15):
            nonlocal t
            if not is_pause and not text.strip():
                return
            dur = pause_dur if is_pause else round(len(text.split()) / wps, 2)
            segments.append({
                'type': stype,
                'text': '' if is_pause else text.strip(),
                'duration': dur,
                'start': round(t, 2),
                'is_pause': is_pause
            })
            t += dur

        add_seg('hook', hook_text)
        add_seg('pause', '', is_pause=True, pause_dur=0.15)
        add_seg('suspense', suspense_text)
        add_seg('pause', '', is_pause=True, pause_dur=0.15)
        
        # Split story segments safely to prevent speech overlap drops
        s_words = story_text.split()
        mid = len(s_words) // 2
        add_seg('story', " ".join(s_words[:mid]))
        add_seg('pause', '', is_pause=True, pause_dur=0.15)
        add_seg('story', " ".join(s_words[mid:]))
        
        add_seg('pause', '', is_pause=True, pause_dur=0.15)
        add_seg('ctr', ctr_text)

        print(f"    📊 Script Synchronized: '{topic}' | {total_w} words | Dynamic Target: {round(t,1)}s")

        return {
            'full_script': raw_script,
            'segments': segments,
            'word_count': total_w,
            'duration': round(t, 2),
            'hook': hook_text, 'suspense': suspense_text,
            'story': story_text, 'ctr': ctr_text
        }

    def _clean(self, text: str) -> str:
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\[.*?\]', '', text)  # Removes text inside brackets [Hook], [Story] etc
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'[^\x00-\x7F]', '', text) # Removes non-ASCII symbols
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_title(self, topic: str) -> str:
        """2026: UNIQUE search-optimized script titles matching USA/UK algorithms"""
        prompt = pr.VIRAL_TITLE_GENERATOR.format(topic=topic)
        raw_titles = self._generate(prompt, max_tokens=100)
        
        # Parse output down to extract the best option safely
        lines = [l.strip() for l in raw_titles.split('\n') if l.strip()]
        selected = lines[0] if lines else f"Dark Secret Of {topic}"
        
        # Strip prefixes like "1.", "-", "Title:"
        selected = re.sub(r'^\d+[\s\.\)]+', '', selected)
        selected = re.sub(r'^[-\s]+', '', selected)
        selected = re.sub(r'(?i)title:\s*', '', selected)
        
        # Enforce structural integrity of 4 words + emoji rule dynamically
        clean_words = [w for w in selected.split() if not any(c in w for c in ['🤯', '⚠️', '🧠', '🚫', '❌', '💀', '🔥'])]
        
        if len(clean_words) > 4:
            clean_words = clean_words[:4]
        elif len(clean_words) < 2:
            clean_words = clean_words + ["Secret", "Truth", "Exposed"][:4-len(clean_words)]
            
        final_clean = " ".join(clean_words[:4])
        emojis = ['🤯', '⚠️', '🧠', '🚫', '❌', '💀']
        
        return f"{final_clean} {random.choice(emojis)}"

    def generate_seo(self, topic: str, script: str) -> Dict:
        """Dynamic generator syncing description structure directly with AI prompts"""
        # Formulate keywords out of topic organically to prevent keyword stuffing penalties
        kw_base = f"psychology, {topic}, brain, 2026, viral shorts, dark truth, neuroscience, human behavior"
        
        desc_prompt = pr.SEO_DESCRIPTION_GENERATOR.format(topic=topic, keywords=kw_base)
        description = self._generate(desc_prompt, max_tokens=250)
        
        tags_prompt = pr.TAGS_GENERATOR.format(topic=topic, keywords=kw_base)
        tags_raw = self._generate(tags_prompt, max_tokens=150)
        
        # Cleanup response tags into clean python lists
        tags = [t.strip().lower() for t in tags_raw.replace('\n', ',').split(',') if t.strip()]
        if not tags or len(tags) < 5:
            tags = ["dark psychology", "shorts facts", "2026 science mystery", topic.lower().replace(" ", "")]
            
        if not description or len(description.split()) < 50:
            description = (
                f"🤯 {topic.upper()} — This hidden psychology insight changes everything.\n\n"
                f"Today we break down the shocking facts behind {topic} and its dark reality.\n\n"
                f"⏱️ Timestamps:\n0:00 Hook\n0:06 Suspense\n0:11 The Dark Truth\n0:48 The Loop\n\n"
                f"🔔 Subscribe to track hidden psychology parameters daily!\n"
                f"#shorts #darkpsychology #neuroscience #mindhacks #{topic.replace(' ', '')}"
            )

        return {
            'description': description.strip(),
            'tags': tags[:14],  # Max 14 tags strict constraint
            'keywords': kw_base
        }

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Reads rules directly from standard thumbnail structure layout"""
        words = [w.replace(',', '').replace('.', '').upper() for w in topic.split() if len(w) <= 8][:2]
        fillers = ["SHOCKING", "HIDDEN", "SECRET", "DARK", "FORBIDDEN"]
        while len(words) < 3:
            words.append(fillers[len(words) % len(fillers)])
        return words[:3]
