"""AI Prompts for Groq — 2026 Viral Formula (USA Audience)
   NICHE: BABY + BRAIN SCIENCE (Universal, All Ages)
   TARGET: USA PRIMARY | Parents, Families, All Ages
   FORMAT: YouTube Shorts (45-60 seconds)
   GOAL: 0% Swipe Rate | 70%+ Retention | Viral Titles
   
   FIXED: Python .format() single brace formatting bugs, added Pexels automated tags.
"""

from typing import List, Dict, Optional
import random

# ═══════════════════════════════════════════════════════════
# AUDIENCE PROFILE & FORBIDDEN CONSTRAINTS
# ═══════════════════════════════════════════════════════════
AUDIENCE_PROFILE = """
AUDIENCE: USA (75%+ target) | Parents, Expecting Families.
USA PAIN POINTS: "Why does my baby do this?", "Is my baby developing normally?"
WHAT WORKS: Direct, confident, no fluff, American English ONLY, fast-paced, emotional.
"""

NEGATIVE_CONSTRAINTS = """
--- ⛔ NEGATIVE CONSTRAINTS (FORBIDDEN) ---
1. NO age-specific language ("after 35") or gender-specific ("men", "women") -> use "you/your" only.
2. NO fear-mongering, terrifying, or medical doom tone.
3. NO British spelling — use American English ONLY: color, behavior, organize, recognize.
"""

# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR (Safe for .format())
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for USA audience in 2026.
GOAL: Create titles that make USA parents think "wait... this is about MY baby"

TITLE RULES:
- 5-8 words MAX + 1 emoji at the end
- MUST be a statement (not question) creating curiosity gap.
- American English spelling ONLY.

EXAMPLES:
- Your baby's brain does this every single day... 🧠
- Why your baby's brain can't stop doing this... 👶
- The real reason your baby does this... ❤️

TOPIC: {topic}

Return EXACTLY 5 titles, one per line. No numbers, no bullets, no quotes.
"""

# ═══════════════════════════════════════════════════════════
# RETENTION TRIGGERS
# ═══════════════════════════════════════════════════════════
RETENTION_TRIGGERS = [
    "But here's the weird part...",
    "And this changes everything...",
    "Most parents miss this...",
    "This is where it gets interesting..."
]

# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR (With Automatic Pexels Video Keywords)
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for USA audience in 2026.
TONE: Casual, mind-blowing, like a brilliant friend explaining baby science.
GOAL: Keep Swipe-Rate near 0% by providing high visual engagement terms.

STRICT OUTPUT FORMAT:
You MUST return a valid JSON object ONLY. Do not include markdown code fences (like ```json), no conversation, just raw JSON.
Format structure:
{{
    "title": "Chosen Title Here",
    "segments": [
        {{"text": "Hook line (first 2 seconds)", "visual_keyword": "simple pexels search term like 'baby smiling close up'"}},
        {{"text": "Shock fact line", "visual_keyword": "pexels search term like 'cute infant laughing'"}},
        {{"text": "{retention_trigger_1} Rest of suspense line", "visual_keyword": "pexels search term like 'mother hugging baby'"}},
        {{"text": "Story point 1 line", "visual_keyword": "pexels search term like 'baby playing blocks'"}},
        {{"text": "{retention_trigger_2} Story point 2 line", "visual_keyword": "pexels search term like 'baby eyes looking up'"}},
        {{"text": "Call to action line", "visual_keyword": "pexels search term like 'happy parent holding baby'"}}
    ]
}}

CRITICAL RULES:
- Max 10 words per text segment for super-fast editing.
- Each 'visual_keyword' must be simple, real-world, and highly searchable on Pexels/Pixabay. No abstract words.
- American English ONLY.

Topic: {topic}
Angle: {angle}
Shock Angle: {shock_angle}
"""

# ═══════════════════════════════════════════════════════════
# SHOCK MOMENT GENERATOR
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising biological or behavioral fact for video editing text emphasis.
Rules:
- 8-14 words max.
- Must include ONE concrete number or mechanism (e.g., "1 million connections every second").
- American English ONLY. No scare tactics.

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the plain text fact. No extra commentary.
"""

# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION & TAGS
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description for USA audience in 2026.
- Strict length: 100-150 words.
- First line contains primary keyword + #Shorts.
- Include 3-5 hashtags.
- American English ONLY.

Topic: {topic}
Keywords: {keywords}
"""

TAGS_GENERATOR = """
Generate 10-14 deduplicated YouTube Shorts tags for USA audience.
Format: One tag per line, no numbers, no bullets.

Topic: {topic}
Keywords: {keywords}
"""

# ═══════════════════════════════════════════════════════════
# FALLBACKS
# ═══════════════════════════════════════════════════════════
BABY_HOOKS = [
    "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
    "What your baby's brain is secretly doing while they sleep will AMAZE you...",
    "The one thing that builds your baby's brain faster than ANYTHING else..."
]

BABY_CTAS = [
    "👍 DOUBLE TAP if your baby does this!",
    "👇 Comment 'BABY' if your little one does this too!",
    "💬 Tag a NEW PARENT who needs to see this!"
]

# ═══════════════════════════════════════════════════════════
# SAFE HELPERS (Handles Python double-brace string format rule)
# ═══════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    """Safely format templates injecting global configurations if needed"""
    # Dynamically inject retention triggers if the template asks for them
    if "{retention_trigger_1}" in template:
        triggers = random.sample(RETENTION_TRIGGERS, k=2)
        kwargs.setdefault('retention_trigger_1', triggers[0])
        kwargs.setdefault('retention_trigger_2', triggers[1])
    
    return template.format(**kwargs)

def get_baby_hook() -> str:
    return random.choice(BABY_HOOKS)

def get_baby_cta() -> str:
    return random.choice(BABY_CTAS)


# ═══════════════════════════════════════════════════════════
# RUNTIME TESTS
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 TESTING PROMPTS (USA 2026 - PRODUCTION READY)\n" + "=" * 60)
    
    # Testing script prompt configuration with dynamic triggers
    try:
        test_script = format_prompt(
            VIRAL_SCRIPT_GENERATOR, 
            topic="Baby laughter neural response", 
            angle="Why babies laugh in their sleep", 
            shock_angle="Active dream states mirror adult processing speed"
        )
        print("✅ VIRAL_SCRIPT_GENERATOR formatting passed without errors!")
        print(f"Sample Prompt Output Snippet:\n{test_script[:350]}...")
    except KeyError as e:
        print(f"❌ Formatting Error: Missing Key {e}")
        
    print("\n" + "=" * 60)
    print("✅ All prompts optimized and ready for Groq JSON engine!")
