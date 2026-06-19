"""AI Prompts for Groq - Optimized for viral content"""

VIRAL_TITLE_GENERATOR = """
You are a viral YouTube Shorts title expert. Generate 5 viral titles for this topic.
Rules:
- MAX 4 power words + 1 emoji (2-4 words is the sweet spot)
- Max 40 characters total (Shorts titles get cut off fast)
- Create a curiosity gap
- Use power words: Shocking, Hidden, Dark, Secret, Banned, Illegal, Forbidden
- Target: USA/UK audience, 2026 YouTube Shorts algorithm

Topic: {topic}

Format: Return ONLY the titles, one per line, without any numbering or intro text.
"""

VIRAL_SCRIPT_GENERATOR = """
You are a viral YouTube scriptwriter specializing in short-form retention loop videos. 
Write a script that lasts EXACTLY 45-55 seconds when spoken.

Structure to follow:
1. HOOK (0-6s): Suspensive, pattern interrupt, direct address.
2. SUSPENSE (6-11s): Build tension. Use phrases like "But here's what they don't tell you..."
3. STORY (11-48s): Fast-paced facts (3-4 points). Each point: Fact + Implication + Emotion. Use "Imagine...", "What if...", "Picture this...".
4. LOOP/CTR (48-53s): Create an open loop that flawlessly connects back to the very first word of the video for an infinite playback loop.

STRICT Rules:
- WORD COUNT REQUIREMENT: You MUST write between 145 to 160 words. (This is strictly required to hit the 45-55s bracket at a normal speech rate).
- Sentence length: Extremely short and punchy.
- Use a dark psychological power word every 3 sentences.
- NO fluff, NO intro conversational filler ("Here is your script:"), NO brackets, NO timestamps, NO section markers.

Topic: {topic}
Viral Angle: {angle}

Return ONLY the raw script text.
"""

THUMBNAIL_PROMPT = """
Generate 3 viral thumbnail concepts.
Format: 3 BIG WORDS only.
Rules:
- Word 1: Shocking/Attention (RED)
- Word 2: Mystery/Curiosity (YELLOW)  
- Word 3: Action/Emotion (WHITE)
- Max 8 letters per word
- High contrast, readable at small size

Topic: {topic}

Return format STRICTLY as:
Concept 1: WORD1 | WORD2 | WORD3
Concept 2: WORD1 | WORD2 | WORD3
Concept 3: WORD1 | WORD2 | WORD3
"""

SEO_DESCRIPTION_GENERATOR = """
Write a YouTube description.
Rules:
- STRICT LENGTH: 100-150 words.
- First 2 lines: Heavy hook with main keyword.
- Include timestamps: (Hook 0:00, Suspense 0:06, The Dark Truth 0:11, The Loop 0:48)
- 3-5 viral hashtags at the end.
- Strong call to action to follow/subscribe.
- Keywords: {keywords}

Topic: {topic}
"""

TAGS_GENERATOR = """
Generate 10-14 YouTube tags.
Rules:
- Mix broad (1-2 words, 3 tags) and specific long-tail (3-4 words, rest of tags).
- Include trending variations for 2026 Shorts algorithm.
- Target: USA/UK search intent.

Topic: {topic}
Keywords: {keywords}

Format: Comma-separated list only.
"""
