"""AI Prompts for Groq — 2026 Viral Formula (USA Audience)
   NICHE: BABY + BRAIN SCIENCE (Universal, All Ages)
   TARGET: USA PRIMARY | Parents, Families, All Ages
   FORMAT: YouTube Shorts (42-55 seconds)
   GOAL: 0% Swipe Rate | 70%+ Retention | Viral Titles
   STRUCTURE: Hook (1.5s) → Shock → Suspense → Story → CTR
   
   FIXED: All required variables exported (VIRAL_TITLE_GENERATOR, VIRAL_SCRIPT_GENERATOR, SHOCK_MOMENT_GENERATOR)
"""

from typing import List, Dict, Optional
import random

# ═══════════════════════════════════════════════════════════
# AUDIENCE PROFILE — USA PRIMARY
# ═══════════════════════════════════════════════════════════
AUDIENCE_PROFILE = """
AUDIENCE:
- PRIMARY: USA (75%+ target)
- SECONDARY: UK, Canada, Australia
- Age: ALL AGES (13-65+)
- Gender: All genders
- Device: 90%+ Mobile (YouTube Shorts)
- Behavior: Scroll during breaks, before bed, commuting

USA-SPECIFIC PAIN POINTS:
- "Why does my baby do this?"
- "Am I a good parent?"
- "Is my baby developing normally?"
- "What should I do as a parent?"
- "I want to understand my child better"

WHAT WORKS IN USA:
- Relatable parenting moments
- "OMG that happens to MY baby"
- Direct, confident, no fluff
- American English ONLY
- Fast-paced, emotional
- Clear value proposition in first 3 seconds
"""

# ═══════════════════════════════════════════════════════════
# NEGATIVE CONSTRAINTS — ABSOLUTELY FORBIDDEN
# ═══════════════════════════════════════════════════════════
NEGATIVE_CONSTRAINTS = """
--- ⛔ NEGATIVE CONSTRAINTS (FORBIDDEN) ---
1. NO age-specific language ("after 35", "after 40", "men over 50")
2. NO gender-specific language ("men", "women") — use "you/your" only
3. NO "shocking", "terrifying", "horrifying", "crazy", "insane"
4. NO "scientists say", "studies show", "research proves"
5. NO medical fear-mongering or doom tone
6. NO British spelling — use American English ONLY:
   color (not colour), favor (not favour), organize (not organise)
   recognize (not recognise), behavior (not behaviour)
"""

# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR — USA SEO 2026
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for USA audience in 2026.

GOAL: Create titles that make USA parents think "wait... this is about MY baby"
AUDIENCE: Parents, expecting parents, families

WINNING TITLE TYPES FOR USA PARENTS:

🟢 Type 1 — "Your baby" hooks:
✅ "Your baby's brain does this every single day..."
✅ "Your baby is ALREADY doing this right now"
✅ "Your baby's brain has been hiding this from you"
✅ "Your baby does this while they sleep"

🟢 Type 2 — "Why" hooks:
✅ "Why your baby does [X]"
✅ "Why your baby feels [X]"
✅ "Why your baby's brain can't stop [X]"
✅ "Why [X] happens to every baby"

🟢 Type 3 — "Nobody tells you" hooks:
✅ "Nobody explains why your baby [X]"
✅ "The real reason your baby [X]"
✅ "What nobody tells you about [X]"
✅ "The hidden reason behind [X]"

TITLE RULES:
- 5-8 words MAX + 1 emoji at the end
- NO age or gender references
- MUST be a statement (not question)
- MUST create curiosity gap
- MUST use American English spelling

TOPIC: {topic}

Return EXACTLY 5 titles, one per line. No numbers, no bullets.
"""

# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — USA 2026
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for USA audience in 2026.

AUDIENCE: USA parents and families.
TONE: Like a brilliant friend explaining baby science — casual, clear, a little mind-blowing.
GOAL: Make them feel "OMG I never knew this about my baby"

STRUCTURE: Hook → Shock → Suspense → Story → CTR
TARGET: 40-55 seconds spoken at natural pace

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### HOOK (8-10 words, 1.5-2.5 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Swipe-stopper hooks (pick style based on topic):
✅ "Your baby's brain is growing RIGHT NOW at 100,000 new neurons..."
✅ "Nobody ever explains why your baby does this..."
✅ "This happens to your baby's brain every single day..."
✅ "Your baby's brain has been keeping a secret from you..."
✅ "You've seen this in your baby... here's why..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SHOCK (8-10 words, 2-3 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
One surprising fact about baby brain development.
Examples:
- "Your baby's brain doubles in size in the first year..."
- "By age 3, your child's brain has 100 trillion connections..."
- "Your baby can recognize your voice from birth..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SUSPENSE (8-10 words, 3-4 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"But here's what nobody explains..."
"And this is where it gets interesting..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### STORY (50-60 words, 22-28 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM then SOLUTION — like explaining to a curious parent.
- Short sentences. Max 10 words each.
- Universal experiences any parent can relate to
- Always "you/your" — never "parents", "people"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### CTR (12-15 words, 5-6 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY: Like + Comment + Follow ask
Examples:
"Comment BABY if your little one does this too! Follow for more."
"Double tap if you love your baby! Tag a new parent! Follow."
"Like if this blew your mind! Comment YES! Follow."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES:
- Use "you/your" throughout
- American English ONLY
- Total: 40-55 seconds

Topic: {topic}
Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with exact markers. No extra text.
"""

# ═══════════════════════════════════════════════════════════
# SHOCK MOMENT GENERATOR — USA 2026
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising fact for video editing emphasis.

Audience: USA parents — anyone with a baby.
Feel: "whoa I never knew that" NOT "oh god that's terrifying"

Rules:
- 8-10 words maximum
- About: {topic}
- Tone: calm but surprising
- NO age or gender references
- American English spelling ONLY

{NEGATIVE_CONSTRAINTS}

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the fact text, no markers, no extra words.
"""

# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION — USA 2026
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description for USA audience in 2026.

RULES:
- STRICT LENGTH: 100-150 words
- FIRST LINE: Hook with main keyword + "#Shorts"
- Include timestamps: Hook 0:00, Key fact 0:08, Main insight 0:15, Takeaway 0:40
- 3-5 hashtags: include #Shorts, plus 2-3 topic-relevant hashtags
- CTA: "Follow for more baby science"
- Keywords: {keywords}
- American English ONLY

Topic: {topic}
"""

# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — USA SEO 2026
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags for USA audience in 2026.

Rules:
- EXACTLY 3 broad tags (1-2 words)
- EXACTLY 7-9 specific tags (3-4 words)
- EXACTLY 1 #Shorts tag
- Include: "youtube shorts", "baby brain", "parenting tips"
- NO age-specific terms

Topic: {topic}
Keywords: {keywords}

Return format: One tag per line, no numbers.
"""

# ═══════════════════════════════════════════════════════════
# BABY HOOKS (Fallback)
# ═══════════════════════════════════════════════════════════
BABY_HOOKS = [
    "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
    "The first 1000 days decide your child's entire future brain power...",
    "What your baby's brain is secretly doing while they sleep will AMAZE you...",
    "Your newborn's brain has already started THIS incredible process...",
    "The one thing that builds your baby's brain faster than ANYTHING else...",
    "Your baby's brain has MORE connections than stars in the galaxy...",
    "This simple activity TRIPLES your baby's brain growth...",
    "Your baby's brain is ALREADY processing language before they speak...",
    "The surprising reason your baby cries — it's brain development...",
    "Your child's brain is doing THIS every single night without fail...",
    "Nobody tells you what your baby's brain is doing RIGHT NOW...",
    "The science behind your baby's first smile is BRAIN GROWTH...",
    "Your toddler's brain is wired for THIS — and it's AMAZING...",
    "Your baby's brain is built through play — here's HOW...",
    "The first year of brain development changes EVERYTHING...",
]

# ═══════════════════════════════════════════════════════════
# BABY CTAS (Forced Engagement)
# ═══════════════════════════════════════════════════════════
BABY_CTAS = [
    "👍 DOUBLE TAP if your baby does this!",
    "❤️ Like if you're AMAZED by your baby's brain!",
    "👇 Comment 'BABY' if your little one does this too!",
    "💬 What does YOUR baby do that amazes you? Comment below!",
    "💬 Tag a NEW PARENT who needs to see this!",
    "📌 SAVE this — every parent needs to know this!",
    "🗣️ SHARE this with every new mom you know!",
    "👍 Like AND Comment 'BRAIN' if you love baby science!",
]

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with kwargs"""
    if '{NEGATIVE_CONSTRAINTS}' in template:
        kwargs.setdefault('NEGATIVE_CONSTRAINTS', NEGATIVE_CONSTRAINTS)
    return template.format(**kwargs)

def get_baby_hook() -> str:
    """Get a random baby hook"""
    return random.choice(BABY_HOOKS)

def get_baby_cta() -> str:
    """Get a random baby CTA"""
    return random.choice(BABY_CTAS)


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 TESTING PROMPTS (USA 2026 - BABY NICHE)\n" + "=" * 60)
    
    print("\n✅ All variables loaded:")
    print(f"   VIRAL_TITLE_GENERATOR: {len(VIRAL_TITLE_GENERATOR)} chars")
    print(f"   VIRAL_SCRIPT_GENERATOR: {len(VIRAL_SCRIPT_GENERATOR)} chars")
    print(f"   SHOCK_MOMENT_GENERATOR: {len(SHOCK_MOMENT_GENERATOR)} chars")
    print(f"   BABY_HOOKS: {len(BABY_HOOKS)} hooks")
    print(f"   BABY_CTAS: {len(BABY_CTAS)} CTAs")
    
    print("\n🎯 Testing format_prompt:")
    formatted = format_prompt(VIRAL_TITLE_GENERATOR, topic="baby brain development")
    print(f"   {formatted[:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ All prompts loaded successfully!")
