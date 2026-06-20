"""AI Prompts for Groq — Optimized for viral content + segment types + visual effects"""

# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a viral YouTube Shorts title expert. Generate 5 viral titles for this topic.
Rules:
- MAX 4 power words + 1 emoji (2-4 words ideal)
- Max 40 characters total (Shorts titles get cut off fast)
- Create a curiosity gap
- Use power words: Shocking, Hidden, Secret, Mystery, Unexplained, Truth, Dark, Revealed
- Target: USA/UK audience, 2026 YouTube Shorts algorithm
- Niche: Human body/brain mystery — Netflix-documentary curiosity, NOT manipulation tactics

Topic: {topic}

Format: Return ONLY the titles, one per line.
"""

# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — WITH SEGMENT TYPES + SHOCK MOMENT
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a viral YouTube Shorts scriptwriter. Write a 100-120 word script.
Style: Netflix mystery-documentary tone about the human body/brain — dark
curiosity and suspense, NOT manipulation/dark-psychology advice. Treat the
topic like a mystery being unraveled.

VIRAL PATTERN: {pattern}
SUSPENSE LEVEL: {suspense_score}/100 (higher = more shocking language)

Structure (MUST use these exact markers):

### HOOK (18-22 words, 6-8 seconds):
Pattern: {pattern}
- Direct "you/your" address
- Pattern interrupt — NO "have you ever wondered"
- End with "..." for visual suspense effect
- Create immediate curiosity gap

### SHOCK (8-10 words, 3-4 seconds):
- ONE visual shock moment — something that makes eyes widen
- Use words like "terrifying", "bizarre", "impossible", "wrong"
- This triggers GLITCH/SHAKE visual effect in video
- End with "..."

### SUSPENSE (10-12 words, 4-5 seconds):
- Build tension: "But here's what's really happening..."
- Dark, moody language
- Tease the twist before revealing it
- End with "..."

### STORY (55-65 words, 25-30 seconds):
- Fast-paced facts about body/brain
- ONE UNEXPECTED TWIST — recontextualizes everything
- Vivid, unsettling imagery: "your body is literally...", "your brain secretly..."
- Use "Imagine...", "What if...", "Picture this..."
- Natural mid-story pause: "..." (for breath timing)
- Connect facts with "and", "but", "because", "which means"

### CTR (10-12 words, 4-5 seconds):
- Loop back to hook's exact question
- "Part 2 reveals more..." OR "Follow if this surprised you"
- Create FOMO — viewer feels they'll miss the full story

RULES:
- Total: 100-120 words (for 40-55s at 130-150 WPM)
- Short, punchy sentences
- Contractions: "you're", "it's", "don't" (natural speech)
- NO fluff, NO filler words
- Every word must earn its place
- Use "..." for pause markers (TTS uses these for breath timing)

Topic: {topic}
Viral Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with markers, no extra text.
"""

# ═══════════════════════════════════════════════════════════
# THUMBNAIL PROMPT — WITH EMOJI + VISUAL ELEMENTS
# ═══════════════════════════════════════════════════════════
THUMBNAIL_PROMPT = """
Generate 3 viral thumbnail concepts for YouTube Shorts.
Format: 3 BIG WORDS + 1 relevant emoji.

Rules:
- Word 1: Shocking/Attention (RED) — 3-8 letters
- Word 2: Mystery/Curiosity (YELLOW/ORANGE) — 3-8 letters  
- Word 3: Action/Emotion (WHITE) — 3-8 letters
- Emoji: Relevant to topic, positioned near Word 2
- Max 8 letters per word
- High contrast, readable at 50x50px (Shorts shelf size)
- Create curiosity gap — viewer MUST click to understand

VIRAL PATTERN: {pattern}

Topic: {topic}

Return format:
Concept 1: WORD1 | WORD2 | WORD3 | EMOJI
Concept 2: WORD1 | WORD2 | WORD3 | EMOJI
Concept 3: WORD1 | WORD2 | WORD3 | EMOJI
"""

# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION — WITH SHORTS OPTIMIZATION
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description.
Rules:
- STRICT LENGTH: 100-150 words
- FIRST LINE: Must include "#Shorts" and main keyword
- First 2 lines: Hook with main keyword (shows before "...more")
- Include timestamps: Hook 0:00, Shock 0:06, Story 0:10, Reveal 0:40
- 3-5 hashtags at the end (including #Shorts)
- Strong CTA: "Follow for daily mind-blowing science"
- Keywords: {keywords}
- Natural placement, NO keyword stuffing
- Add 1-2 related video suggestion lines
- Mention "Part 2" to create FOMO

Topic: {topic}
"""

# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — WITH 2026 SHORTS ALGORITHM
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags.
Rules:
- EXACTLY 3 broad tags (1-2 words): high search volume
- EXACTLY 7-9 specific tags (3-4 words): long-tail, niche
- EXACTLY 1 trending tag: 2026 viral format
- EXACTLY 1 #Shorts tag: "#Shorts" always included
- Order: Highest search volume first
- Target: USA/UK search behavior
- Include: "youtube shorts", "viral shorts", "trending 2026"

Topic: {topic}
Keywords: {keywords}

Return format: One tag per line, no numbers/bullets.
"""

# ═══════════════════════════════════════════════════════════
# NEW: SHOCK MOMENT GENERATOR — For visual effect timing
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE visual shock moment description for video editing.
This will trigger a GLITCH/SHAKE effect in the video.

Rules:
- 8-10 words maximum
- Must be about: {topic}
- Language: visceral, visual, immediate
- Words that suggest motion: "suddenly", "flashes", "twitches", "freezes"
- Must create an "eyes widen" moment

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the shock text, no markers.
"""

# ═══════════════════════════════════════════════════════════
# NEW: SEGMENT TYPE CLASSIFIER — For video_assembler.py
# ═══════════════════════════════════════════════════════════
SEGMENT_TYPE_PROMPT = """
Classify each sentence of this script into segment types for video editing.

Types:
- HOOK: Opening curiosity grab (0-6s)
- SHOCK: Visual shock moment (6-10s) — triggers glitch effect
- SUSPENSE: Tension building (10-15s)
- STORY: Main content (15-40s)
- CTR: Call to action (40-45s)
- PAUSE: Breath/break moment

Script:
{script}

Return format:
HOOK: [text]
SHOCK: [text]
SUSPENSE: [text]
STORY: [text]
CTR: [text]
"""

# ═══════════════════════════════════════════════════════════
# NEW: WORD BOUNDARY HINTS — For audio_generator.py TTS timing
# ═══════════════════════════════════════════════════════════
WORD_TIMING_PROMPT = """
Add pause markers to this script for precise TTS timing.
Use "..." for 0.5s breath pauses at natural speech breaks.

Rules:
- HOOK end: "..." (suspense)
- SHOCK end: "..." (impact)
- STORY middle: "..." (breath)
- Before CTR: "..." (transition)

Script:
{script}

Return: Same script with "..." added at correct positions.
"""
