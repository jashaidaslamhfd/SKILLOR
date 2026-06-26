"""AI Prompts for Groq — 2026 Modern Hooks
   NICHE: Mystery Crispy Body Science for Men 35+
   AUDIENCE: USA/UK Males 35-54
   FORMAT: YouTube Shorts (40-55 seconds)
   GOAL: Make viewer UNABLE to swipe away
   STRUCTURE: Hook → Suspense → Problem → Solution → Loopback → CTR
"""

from typing import List, Dict, Optional
import random

# ═══════════════════════════════════════════════════════════
# AUDIENCE PROFILE (Unchanged - Critical for targeting)
# ═══════════════════════════════════════════════════════════
AUDIENCE_PROFILE = """
AUDIENCE:
- Age: 35-54 (51.7% are 35-44, 48.3% are 45-54)
- Gender: 76.2% Male
- Location: USA 33.5% | UK (remaining English)
- Device: 79.6% Mobile
- Behavior: Working adults, scroll during lunch, before bed, on couch
- Pain Point: Experiencing memory loss and brain fog
- Search Terms: "why do i forget", "brain fog", "memory loss"
- Emotional State: Worried, alone, confused
- What Works: "I thought I was the only one"
- What Fails: Broad science, teen shock, horror tone
"""

# ═══════════════════════════════════════════════════════════
# NEGATIVE CONSTRAINTS (CRITICAL - Do Not Remove)
# ═══════════════════════════════════════════════════════════
NEGATIVE_CONSTRAINTS = """
--- ⛔ NEGATIVE CONSTRAINTS (These are FORBIDDEN) ---
1. ABSOLUTELY NO mention of sleep, insomnia, or waking up
2. ABSOLUTELY NO mention of stress, cortisol, or anxiety
3. ABSOLUTELY NO mention of testosterone or men's health (other than memory)
4. ABSOLUTELY NO mention of parenting, children, or babies
5. DO NOT use "shocking", "terrifying", "horrifying", "crazy", "insane"
6. DO NOT use "scientists say", "studies show", "research proves"
7. If ANY of these appear, the script is REJECTED
"""

# ═══════════════════════════════════════════════════════════
# 2026 HOOK PSYCHOLOGY — What Works NOW
# ═══════════════════════════════════════════════════════════
HOOK_PSYCHOLOGY_2026 = """
MODERN HOOK RULES (2026):

CRITICAL: Old hooks don't work anymore.
- "Did you know" → SWIPE (weak, passive)
- "Scientists discovered" → SWIPE (too formal)
- "Shocking truth" → SWIPE (overused)
- Questions → SWIPE (statements are stronger)

WHAT WORKS IN 2026:
1. Direct statements: "Your brain is ALREADY forgetting..."
2. Personal address: "This is why YOU forget names..."
3. Experience validation: "The reason you forget is SIMPLER than you think..."
4. Urgency words: "ALREADY", "RIGHT NOW", "BEEN"
5. Confirmation: "You're not broken... your brain is just CHANGING"

FORMULA: [Urgency/Possession] + [Action happening to viewer] + [Curiosity gap]
Example: "Your brain is ALREADY forgetting names you just heard..."
         ^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^
         Urgency       Action on viewer            Curiosity gap
"""


# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR — 2026 Modern (25+ Templates)
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for 2026.

GOAL: Create titles that make a 40-year-old man think "this is about ME"

OLD HOOKS (AVOID AT ALL COSTS):
❌ "Did you know..."
❌ "Scientists discovered..."
❌ "Shocking truth..."
❌ "Mind-blowing fact..."
❌ Any question

NEW HOOKS (CHOOSE 5 DIFFERENT ONES):
🟢 Type 1 - "Your brain" hooks:
✅ "Your brain is ALREADY [doing X]"
✅ "Your brain is quietly [doing X]"
✅ "Your brain is changing with [X]"
✅ "Your brain has been [doing X] for years"
✅ "Your brain starts [doing X] after 35"

🟢 Type 2 - "Why" hooks:
✅ "Why [X] happens to you"
✅ "Why your [X] gets worse"
✅ "Why [X] is more common than you think"
✅ "Why you can't stop [X]"
✅ "Why ignoring [X] is dangerous"

🟢 Type 3 - "Truth/Secret" hooks:
✅ "The hidden truth about [X]"
✅ "The surprising truth about [X]"
✅ "The real reason behind [X]"
✅ "What nobody explains about [X]"
✅ "What your brain does with [X]"

🟢 Type 4 - "What/How" hooks:
✅ "What [X] actually means for you"
✅ "How [X] affects your brain"
✅ "How to stop [X]"
✅ "What happens when [X] occurs"
✅ "What [X] does to your memory"

🟢 Type 5 - "Stop/Warning" hooks:
✅ "Stop [X] now - Here's why"
✅ "Warning: [X] is destroying your memory"
✅ "The danger of [X] after 35"
✅ "Why ignoring [X] is a mistake"
✅ "The simple truth about [X]"

🟢 Type 6 - "Science/Explained" hooks:
✅ "The science behind [X] explained"
✅ "[X] explained in 60 seconds"
✅ "The brain science of [X]"
✅ "What science says about [X]"

TITLE RULES:
- 6 words MAX + 1 emoji
- MUST create urgency
- MUST be personal ("you/your")
- MUST be a statement (not question)
- MUST have curiosity gap
- MUST be about memory or brain fog

TOPIC: {topic}

IMPORTANT: Return 5 COMPLETELY DIFFERENT titles. Use different types.
Return ONLY 5 titles, one per line. No numbers. No bullets.
"""


# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — 2026 Modern with Storytelling
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for 2026.

AUDIENCE: Men 35-54 experiencing unexplained body signals, memory issues, brain fog, or physical changes.
TONE: "A calm doctor who has experienced this too" — relatable, credible, never scary.
GOAL: Make them feel understood, explain the body/brain science simply, hook them to follow.

STRUCTURE: Hook → Suspense → Problem → Solution → Loopback → CTR
TARGET LENGTH: 40-55 seconds spoken at natural pace

CRITICAL: The hook must be MODERN and URGENT.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### HOOK (8-10 words, 2-3 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL: This is the most important line in the entire script.
The viewer decides to stay or swipe in 1-2 seconds.

OLD HOOKS (WILL CAUSE SWIPE):
❌ "Have you ever wondered why..."
❌ "Did you know that..."
❌ "Scientists have discovered..."
❌ "The shocking truth about..."
❌ "What if I told you..."

MODERN HOOKS (WILL STOP SCROLL):
✅ "Your brain is ALREADY forgetting names you just heard..."
✅ "Your body has been signaling this for years..."
✅ "Nobody tells you what actually happens to your body after 35..."
✅ "This is why YOU feel this... and it's not what you think..."
✅ "Your body isn't broken... it's just CHANGING..."

RULES FOR 2026 HOOK:
✓ Must start with: "Your", "Nobody", "This is why", "The reason", "You're not"
✓ Must use urgency words: "ALREADY", "RIGHT NOW", "BEEN", "QUIETLY"
✓ Must be personal: "you/your"
✓ Must be a statement (NOT question)
✓ Must be 8-10 words

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### SHOCK (8-10 words, 2-3 seconds):
- One specific, surprising fact about the topic (brain OR body)
- Must confirm they were right to stay
- Calm delivery — surprising, not scary
- End with "..."

Examples:
- "Your brain processes 70,000 thoughts daily... and forgets 90% of them"
- "Your gut has 100 million neurons... almost as many as your spine"
- "Your heart skips a beat every day... and you never notice"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### SUSPENSE (10-12 words, 4-5 seconds):
- Calm curiosity build — this is the PROBLEM setup
- "But here's what's REALLY happening in your body..."
- "And the reason might explain what you've been feeling..."
- End with "..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### STORY (50-60 words, 22-28 seconds):
- PROBLEM then SOLUTION — conversational, like a friend explaining over coffee
- Connect to daily experiences the viewer actually feels
- Short sentences. Max 10 words each.
- Natural breath pause midway: "..."
- Always "you", "your", "you've" — never "people" or "individuals"
- End the STORY with a LOOPBACK callback to the hook (satisfying close)

Example: "Your body has something called an energy regulation system. And after 35... it starts prioritizing survival over performance. Which means your body is hoarding energy it should be giving you. The good news... understanding this is the first step to working with it, not against it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### CTR (10-12 words, 4-5 seconds):
- Callback to the hook — creates a satisfying loop
- Warm invitation, NOT urgency/FOMO pressure
- ✅ MUST include ONE of: Follow, Subscribe, or Like
- Examples:
  "Follow for more on why your body works this way."
  "Subscribe — Part 2 reveals what actually fixes this."
  "Like if this happened to you... Follow for Part 2."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES:
- Topics can be about BRAIN, MEMORY, or any BODY SCIENCE mystery
- Hook MUST be 8-10 words (NOT more)
- Use "you/your" throughout
- NO "shocking", "terrifying", "crazy"
- NO parenting topics
- Place "..." only where a real person would naturally pause to breathe
- TOTAL script must read in 40-55 seconds (spoken at natural pace)

Topic: {topic}
Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with the exact markers. No extra text. No explanations.
"""


# ═══════════════════════════════════════════════════════════
# SHOCK MOMENT GENERATOR — Credible, Not Horror
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising fact moment for video editing emphasis.

Target audience: Males 35-54 experiencing memory loss.
The moment should feel: "whoa I didn't know that" NOT "oh god that's terrifying"

Rules:
- 8-10 words maximum
- Must be about memory or brain fog: {topic}
- Language: calm but surprising — "quietly", "actually", "without you realizing"
- Avoid: "terrifying", "horrifying", "deadly", "destroying"
- Use: "fascinating", "surprising", "unexpected", "worth knowing"

{NEGATIVE_CONSTRAINTS}

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the fact text, no markers, no extra words.
"""


# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION — USA/UK Male 35-54 Optimized
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description optimized for USA/UK male audience aged 35-54.

Rules:
- STRICT LENGTH: 100-150 words
- FIRST LINE: Hook with main keyword + "#Shorts"
- First 2 lines visible before "...more" — make them count
- Include timestamps: Hook 0:00, Key fact 0:08, Main insight 0:15, Takeaway 0:40
- 3-5 hashtags: include #Shorts, #MemoryFacts, #BrainHealth
- CTA: "Follow for more science your doctor won't explain"
- Keywords: {keywords}
- Natural placement, NO keyword stuffing
- Tone: informative, credible — like a science newsletter, not viral bait

Topic: {topic}
"""


# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — USA/UK Male 35-54 Search Behavior
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags for USA/UK male audience aged 35-54.

This audience searches differently than teens:
- They search for PROBLEMS they experience: "why do i forget things", "memory after 40"
- They trust: "brain science", "health facts", "explained"
- They avoid: "shocking", "insane", "mind blowing"

Rules:
- EXACTLY 3 broad tags (1-2 words): high search volume, topic-relevant
- EXACTLY 7-9 specific tags (3-4 words): long-tail, age/problem-specific
- EXACTLY 1 trending tag: 2026 format
- EXACTLY 1 #Shorts tag: always include
- Order: Highest search volume first
- Include age-relevant terms where natural: "after 40", "men's health", "adult brain"
- Include: "youtube shorts", "brain facts", "health shorts"

Topic: {topic}
Keywords: {keywords}

Return format: One tag per line, no numbers, no bullets.
"""


# ═══════════════════════════════════════════════════════════
# MODERN HOOK TEMPLATES (2026) — Ready to Use (EXPANDED)
# ═══════════════════════════════════════════════════════════
MODERN_HOOK_TEMPLATES = [
    # Type 1: "Already" hooks (urgency)
    "Your brain is ALREADY forgetting {topic} right now...",
    "Your memory has BEEN changing with {topic} for years...",
    "Your brain is QUIETLY deleting {topic} as you read this...",
    "Your brain is actively {topic} right now without you knowing...",
    
    # Type 2: "Nobody tells you" hooks (insider info)
    "Nobody tells you what {topic} actually does to your brain...",
    "Nobody explains why {topic} happens to you every day...",
    "Nobody warns you about what your brain does with {topic}...",
    "Nobody mentions what {topic} really means for you...",
    
    # Type 3: "This is why" hooks (personal)
    "This is why YOU keep experiencing {topic}...",
    "This is what YOUR brain does when {topic} happens...",
    "This is why YOUR memory gets worse with {topic}...",
    "This explains why {topic} happens to you...",
    
    # Type 4: "The reason" hooks (curiosity)
    "The reason you keep experiencing {topic} is SIMPLER than you think...",
    "The truth about {topic} is SURPRISING...",
    "The science behind {topic} is FASCINATING...",
    "The real reason behind {topic} is UNEXPECTED...",
    
    # Type 5: "You're not broken" hooks (relief)
    "Your brain isn't broken... it's just CHANGING with {topic}...",
    "You're not losing your mind... you're just EXPERIENCING {topic}...",
    "You're not getting dementia... your brain is just DOING {topic}...",
    
    # Type 6: "What's happening" hooks (engagement)
    "What's happening in your brain when {topic} occurs...",
    "Here's what {topic} actually means for your memory...",
    "What {topic} does to your brain after 35...",
    "What science says about {topic} and your brain...",
]


# ═══════════════════════════════════════════════════════════
# HELPER: Format Prompt with Topic
# ═══════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    """
    Format prompt with given variables
    Automatically includes NEGATIVE_CONSTRAINTS if present in template
    """
    if '{NEGATIVE_CONSTRAINTS}' in template:
        kwargs.setdefault('NEGATIVE_CONSTRAINTS', NEGATIVE_CONSTRAINTS)
    
    return template.format(**kwargs)


def generate_modern_hooks(topic: str, count: int = 5) -> List[str]:
    """Generate modern 2026 hooks for a topic"""
    hooks = []
    templates = random.sample(MODERN_HOOK_TEMPLATES, min(count, len(MODERN_HOOK_TEMPLATES)))
    
    for template in templates:
        hook = template.format(topic=topic)
        hooks.append(hook)
    
    return hooks


# ═══════════════════════════════════════════════════════════
# TEST THE PROMPTS
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 TESTING PROMPTS\n" + "="*60)
    
    # Test title generation
    print("\n📝 TITLE PROMPT:")
    title_prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic="forgetting names")
    print(title_prompt[:500] + "...")
    
    # Test script generation
    print("\n🎬 SCRIPT PROMPT:")
    script_prompt = format_prompt(
        VIRAL_SCRIPT_GENERATOR,
        topic="forgetting names",
        angle="Why men forget names after 40",
        shock_angle="Your brain is pruning memories you'll never get back"
    )
    print(script_prompt[:500] + "...")
    
    # Test modern hooks
    print("\n🎯 MODERN HOOKS (25+ templates):")
    hooks = generate_modern_hooks("forgetting names", 5)
    for i, hook in enumerate(hooks, 1):
        print(f"   {i}. {hook}")
    
    print("\n" + "="*60)
    print("✅ All prompts loaded successfully!")
