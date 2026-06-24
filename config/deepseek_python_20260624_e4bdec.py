"""AI Prompts for Groq — 2026 Modern Hooks
   NICHE: Memory & Brain Fog Science for Men 35+
   AUDIENCE: USA/UK Males 35-54
   FORMAT: YouTube Shorts (45-55 seconds)
   GOAL: Make viewer UNABLE to swipe away
"""

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
# VIRAL TITLE GENERATOR — 2026 Modern
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

NEW HOOKS (USE THESE):
✅ "Your brain is ALREADY [doing X]"
✅ "Nobody tells you what [X] actually does"
✅ "This is why YOU [experience X]"
✅ "The truth about [X] is SURPRISING"
✅ "You're not [X]... your brain is just [doing Y]"

TITLE RULES:
- 6 words MAX + 1 emoji
- MUST create urgency
- MUST be personal ("you/your")
- MUST be a statement (not question)
- MUST have curiosity gap
- MUST be about memory or brain fog

TOPIC: {topic}

Return ONLY 5 titles, one per line. No numbers. No bullets.
"""


# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — 2026 Modern with Storytelling
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for 2026.

AUDIENCE: Men 35-54 experiencing memory loss and brain fog.
TONE: "A doctor who also experiences memory loss" - Calm, relatable, credible.
GOAL: Make them feel understood, then explain the science simply.

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
✅ "Nobody tells you what actually happens to memory..."
✅ "This is why YOU forget names right after hearing them..."
✅ "The reason you forget is SIMPLER than you think..."
✅ "Your brain isn't broken... it's just CHANGING..."

RULES FOR 2026 HOOK:
✓ Must start with: "Your", "Nobody", "This is why", "The reason", "You're not"
✓ Must use urgency words: "ALREADY", "RIGHT NOW", "BEEN"
✓ Must be personal: "you/your"
✓ Must be a statement (NOT question)
✓ Must be 8-10 words

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### SHOCK (8-10 words, 2-3 seconds):
- One specific, surprising fact about memory or brain fog
- Must confirm they were right to stay
- Calm delivery — surprising, not scary
- End with "..."

Examples:
- "Your brain processes 70,000 thoughts daily... and forgets 90% of them"
- "The memories you think are permanent... are being rewritten right now"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### SUSPENSE (10-12 words, 4-5 seconds):
- Calm curiosity build
- "But here's what's REALLY happening..."
- "And the reason might explain a lot about your own life..."
- End with "..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### STORY (55-65 words, 25-30 seconds):
- Conversational. Like explaining to a friend over coffee.
- Connect to daily experiences (forgetting names, walking into rooms)
- Short sentences. Max 10 words each.
- Natural breath pause midway: "..."
- Always "you", "your", "you've" — never "people" or "individuals"

Example: "Your brain has something called a memory filter. And after 35... it gets TOO good at filtering. Which means your brain is deleting things it shouldn't. And that's why you walk into a room... and forget why you're there."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### CTR (10-12 words, 4-5 seconds):
- Callback to the hook — creates a satisfying loop
- Warm invitation, NOT urgency/FOMO pressure
- "Follow for more on why your brain works this way."
- "Part 2 explains what actually helps memory after 40."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES:
- EVERYTHING MUST BE ABOUT MEMORY OR BRAIN FOG
- Hook MUST be 8-10 words (NOT more)
- Use "you/your" throughout
- NO "shocking", "terrifying", "crazy"
- NO sleep topics, NO stress topics, NO parenting topics
- Place "..." only where a real person would naturally pause to breathe

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
# MODERN HOOK TEMPLATES (2026) — Ready to Use
# ═══════════════════════════════════════════════════════════
MODERN_HOOK_TEMPLATES = [
    # Type 1: "Already" hooks (urgency)
    "Your brain is ALREADY forgetting {topic} right now...",
    "Your memory has BEEN changing with {topic} for years...",
    "Your brain is QUIETLY deleting {topic} as you read this...",
    
    # Type 2: "Nobody tells you" hooks (insider info)
    "Nobody tells you what {topic} actually does to your brain...",
    "Nobody explains why {topic} happens to you every day...",
    "Nobody warns you about what your brain does with {topic}...",
    
    # Type 3: "This is why" hooks (personal)
    "This is why YOU keep experiencing {topic}...",
    "This is what YOUR brain does when {topic} happens...",
    "This is why YOUR memory gets worse with {topic}...",
    
    # Type 4: "The reason" hooks (curiosity)
    "The reason you keep experiencing {topic} is SIMPLER than you think...",
    "The truth about {topic} is SURPRISING...",
    "The science behind {topic} is FASCINATING...",
    
    # Type 5: "You're not broken" hooks (relief)
    "Your brain isn't broken... it's just CHANGING with {topic}...",
    "You're not losing your mind... you're just EXPERIENCING {topic}...",
    "You're not getting dementia... your brain is just DOING {topic}...",
]


# ═══════════════════════════════════════════════════════════
# HELPER: Format Prompt with Topic
# ═══════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    """
    Format prompt with given variables
    Automatically includes NEGATIVE_CONSTRAINTS if present in template
    """
    # Ensure negative constraints are always included
    if '{NEGATIVE_CONSTRAINTS}' in template:
        kwargs.setdefault('NEGATIVE_CONSTRAINTS', NEGATIVE_CONSTRAINTS)
    
    return template.format(**kwargs)


def generate_modern_hooks(topic: str, count: int = 5) -> List[str]:
    """Generate modern 2026 hooks for a topic"""
    import random
    
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
    print("\n🎯 MODERN HOOKS:")
    hooks = generate_modern_hooks("forgetting names", 5)
    for i, hook in enumerate(hooks, 1):
        print(f"   {i}. {hook}")
    
    print("\n" + "="*60)
    print("✅ All prompts loaded successfully!")