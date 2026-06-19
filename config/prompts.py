"""AI Prompts for Groq - Optimized for viral content"""

VIRAL_TITLE_GENERATOR = """
You are a viral YouTube Shorts title expert. Generate 5 viral titles for this topic.
Rules:
- MAX 4 power words + 1 emoji (4 words is the ceiling, not a target — 2-4 words is fine)
- Max 40 characters total (Shorts titles get cut off fast)
- Create a curiosity gap
- Use power words: Shocking, Hidden, Dark, Secret, Banned, Illegal, Forbidden
- Target: USA/UK audience, 2026 YouTube Shorts algorithm
- Niche: Crispy mysterious science & human behavior

Topic: {topic}

Format: Return ONLY the titles, one per line.
"""

VIRAL_SCRIPT_GENERATOR = """
You are a viral YouTube scriptwriter. Write a 45-second script.
Structure:
1. HOOK (0-6s): Suspensive, pattern interrupt, direct address
2. SUSPENSE (6-10s): Build tension, "But here's what they don't tell you..."
3. STORY (10-42s): 
   - Fast-paced facts
   - 3-4 key points
   - Each point: Fact + Implication + Emotion
   - Use "Imagine...", "What if...", "Picture this..."
4. LOOP/CTR (42-45s): "Part 2 reveals the dark side..." or "Comment if you experienced this"

Rules:
- Word count: 110-130 words (for 45s at 150 WPM)
- Sentence length: Short, punchy
- Use power words every 3 sentences
- End with open loop
- NO fluff, NO filler
- Natural speech patterns (contractions, pauses)

Topic: {topic}
Viral Angle: {angle}

Return ONLY the script text, no markers.
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
- Create curiosity gap

Topic: {topic}

Return format:
Concept 1: WORD1 | WORD2 | WORD3
Concept 2: WORD1 | WORD2 | WORD3
Concept 3: WORD1 | WORD2 | WORD3
"""

SEO_DESCRIPTION_GENERATOR = """
Write a YouTube description.
Rules:
- STRICT LENGTH: 100-150 words, not less, not more
- First 2 lines: Hook with main keyword (this shows before "...more")
- Include timestamps (Hook 0:00, Story 0:06, Reveal 0:40)
- 3-5 hashtags at the end
- Strong call to action (subscribe/follow/comment)
- Keywords: {keywords}
- Natural keyword placement, no keyword stuffing
- Add 1-2 related video suggestion lines

Topic: {topic}
"""

TAGS_GENERATOR = """
Generate 10-14 YouTube tags (not more than 14, not less than 10).
Rules:
- Mix broad (1-2 words, 3 tags) and specific long-tail (3-4 words, rest of tags)
- Include trending variations for 2026 Shorts algorithm
- Target: USA/UK search behavior
- Order: Most important/highest-search-volume first

Topic: {topic}
Keywords: {keywords}
"""
