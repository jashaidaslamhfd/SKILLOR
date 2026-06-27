"""AI Prompts for Groq — 2026 Viral Formula
   NICHE: Body + Brain Science (Mystery Crispy Style)
   AUDIENCE: All Ages (13-65+) | USA/UK/Global English
   FORMAT: YouTube Shorts (40-55 seconds)
   GOAL: Make viewer UNABLE to swipe away
   STRUCTURE: Hook → Shock → Suspense → Problem → Solution → Loopback → CTR
"""

from typing import List, Dict, Optional
import random

# ═══════════════════════════════════════════════════════════
# AUDIENCE PROFILE — All Ages, Global English
# ═══════════════════════════════════════════════════════════
AUDIENCE_PROFILE = """
AUDIENCE:
- Age: ALL AGES (13-65+) — teens, young adults, middle age, seniors
- Gender: All genders
- Location: USA, UK, Canada, Australia, Global English
- Device: 85%+ Mobile
- Behavior: Scroll during breaks, before bed, commuting
- Universal Pain Points:
  * "Why does my body do that?"
  * "I thought I was the only one"
  * "Nobody ever explained this to me"
- What Works: Relatable, surprising, "OMG that happens to ME"
- What Fails: Age-specific, gender-specific, medical jargon, horror tone
"""

# ═══════════════════════════════════════════════════════════
# NEGATIVE CONSTRAINTS
# ═══════════════════════════════════════════════════════════
NEGATIVE_CONSTRAINTS = """
--- ⛔ NEGATIVE CONSTRAINTS (FORBIDDEN) ---
1. NO age-specific language ("after 35", "after 40", "men over 50")
2. NO gender-specific language ("men", "women") — use "you/your" only
3. NO "shocking", "terrifying", "horrifying", "crazy", "insane"
4. NO "scientists say", "studies show", "research proves"
5. NO medical fear-mongering or doom tone
6. NO parenting or children topics
7. If ANY of these appear, the script is REJECTED
"""

# ═══════════════════════════════════════════════════════════
# 2026 HOOK PSYCHOLOGY
# ═══════════════════════════════════════════════════════════
HOOK_PSYCHOLOGY_2026 = """
MODERN HOOK RULES (2026):

OLD hooks = SWIPE:
- "Did you know" → passive, weak
- "Scientists discovered" → too formal
- "Shocking truth" → overused, nobody believes it
- Questions → weaker than statements

WHAT WORKS IN 2026:
1. Universal experience: "Your body does this every single day..."
2. Curiosity gap: "...and nobody ever explains why"
3. Urgency: "ALREADY", "RIGHT NOW", "THIS SECOND"
4. Personal: always "you/your" — never "people" or "humans"
5. Relatable mystery: something they've experienced but never understood

FORMULA: [Universal experience] + [Happening RIGHT NOW] + [Curiosity gap]
Example: "Your body is doing something RIGHT NOW... and you have no idea why"
"""

# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR — All Age, All Gender
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for 2026.

GOAL: Create titles that make ANYONE think "wait... this is about ME"
AUDIENCE: All ages (13-65+), all genders, global English speakers

OLD TITLES (AVOID — will cause swipe):
❌ "Did you know..."
❌ "Scientists discovered..."
❌ "Shocking truth..."
❌ "Mind-blowing fact..."
❌ Any question format
❌ Age-specific ("after 40", "for men over 35")

WINNING TITLE TYPES:

🟢 Type 1 — "Your body/brain" hooks:
✅ "Your body does this every single day..."
✅ "Your brain is ALREADY doing this right now"
✅ "Your body has been hiding this from you"
✅ "Your brain does this while you sleep"

🟢 Type 2 — "Why" hooks (universal):
✅ "Why your body does [X]"
✅ "Why you feel [X] for no reason"
✅ "Why your brain can't stop [X]"
✅ "Why [X] happens to everyone"

🟢 Type 3 — Mystery hooks:
✅ "Nobody explains why [X] happens"
✅ "The real reason your body [X]"
✅ "What nobody tells you about [X]"
✅ "The hidden reason behind [X]"

🟢 Type 4 — Relatable experience hooks:
✅ "That feeling when your body [X]... explained"
✅ "Why you always [X] and never knew why"
✅ "This happens to your body every day"

🟢 Type 5 — Science made simple:
✅ "The science of [X] explained simply"
✅ "[X] explained in 45 seconds"
✅ "What [X] actually does to your body"

TITLE RULES:
- 5-8 words MAX + 1 emoji at the end
- NO age or gender references ("after 35", "men", "women")
- MUST be a statement (not question)
- MUST create curiosity gap
- MUST feel universal — any age should think "this is me"
- NO repeating words in the same title
- NO incomplete sentences or cut-off words
- Each title must be COMPLETE and make sense on its own

TOPIC: {topic}

IMPORTANT:
- Return EXACTLY 5 titles
- One title per line
- No numbers, no bullets, no dashes
- No explanations or headers
- Just the 5 titles, nothing else
"""

# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — All Age, Mystery Crispy Style
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for 2026.

AUDIENCE: ALL AGES (13 to 65+) — anyone who has a body and a brain.
TONE: Like a brilliant friend explaining something over text — casual, clear, a little mind-blowing.
GOAL: Make them feel "OMG I never knew this" then hook them to follow.

STRUCTURE: Hook → Shock → Suspense → Problem → Solution → Loopback → CTR
TARGET: 40-55 seconds spoken at natural pace

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### HOOK (8-10 words, 2-3 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The viewer decides in 1-2 seconds. Make it universal.

FORBIDDEN hooks:
❌ "Have you ever wondered..."
❌ "Did you know..."
❌ "Scientists have discovered..."
❌ "After age 35..."

WINNING hooks (pick style based on topic):
✅ "Your body is doing something RIGHT NOW you don't know about..."
✅ "Nobody ever explains why your brain does this..."
✅ "This happens to your body every single day..."
✅ "Your brain has been keeping a secret from you..."
✅ "You've felt this your whole life... here's why..."

RULES:
✓ Start with "Your", "Nobody", "This", "You've", "Every"
✓ Universal — any age, any gender should nod their head
✓ Statement NOT question
✓ 8-10 words only
✓ End with "..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SHOCK (8-10 words, 2-3 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
One surprising fact that confirms they were right to stay.
Calm tone — "whoa" not "terrifying".
End with "..."

Examples:
- "Your gut has more neurons than your entire spinal cord..."
- "Your heart sends more signals to your brain than your brain sends back..."
- "Your body replaces 96% of its atoms every single year..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SUSPENSE (8-10 words, 3-4 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build tension — this is the PROBLEM setup.
"But here's what nobody explains..."
"And this is where it gets interesting..."
End with "..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### STORY (50-60 words, 22-28 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM then SOLUTION — like explaining to a curious friend.
- Short sentences. Max 10 words each.
- Universal experiences anyone can relate to
- Natural pause midway: "..."
- Always "you/your" — never "people", "humans", "individuals"
- End with LOOPBACK — callback to hook for satisfying close

Example: "Your brain has a built-in filter. And it runs 24 hours a day. Its job is to decide what matters... and delete the rest. The problem is it doesn't always get it right. But here's the good part — once you understand the pattern, you can start to work with it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### CTR (10-12 words, 4-5 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Callback to hook — satisfying loop close.
Warm, not pushy. MUST include Follow, Subscribe, or Like.

Examples:
"Follow for more body science nobody teaches you."
"Subscribe — your body has more secrets like this."
"Like if this blew your mind... Follow for Part 2."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES:
- ANY topic: brain, body, gut, heart, skin, energy, memory, nerves
- NO age references ("after 35", "over 40")
- NO gender references ("men", "women")
- NO "shocking", "terrifying", "crazy", "insane"
- NO medical doom tone
- Use "you/your" throughout
- Place "..." only at natural breath pauses
- TOTAL: 40-55 seconds spoken at natural pace

Topic: {topic}
Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with exact markers. No extra text. No explanations.
"""

# ═══════════════════════════════════════════════════════════
# SHOCK MOMENT GENERATOR
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising fact for video editing emphasis.

Audience: ALL AGES — universal, anyone with a body/brain.
Feel: "whoa I never knew that" NOT "oh god that's terrifying"

Rules:
- 8-10 words maximum
- About: {topic}
- Tone: calm but surprising — "quietly", "actually", "without you realizing"
- NO age or gender references
- Avoid: "terrifying", "horrifying", "deadly", "destroying"
- Use: "fascinating", "surprising", "unexpected", "worth knowing"

{NEGATIVE_CONSTRAINTS}

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the fact text, no markers, no extra words.
"""

# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION — All Age, Global English
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description for a global English audience, all ages.

Rules:
- STRICT LENGTH: 100-150 words
- FIRST LINE: Hook with main keyword + "#Shorts"
- First 2 lines visible before "...more" — make them count
- Include timestamps: Hook 0:00, Key fact 0:08, Main insight 0:15, Takeaway 0:40
- 3-5 hashtags: include #Shorts, #BodyScience, #BrainFacts
- CTA: "Follow for more science nobody teaches you"
- Keywords: {keywords}
- Natural placement, NO keyword stuffing
- Tone: curious, credible — like a science newsletter anyone would read

Topic: {topic}
"""

# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — All Age, Global Search
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags for a global English audience, all ages.

Universal search behavior:
- People search: "why does my body", "what happens when", "why do I feel"
- They trust: "body science", "brain facts", "explained simply"
- Universal terms beat age-specific ones

Rules:
- EXACTLY 3 broad tags (1-2 words): high volume, universal
- EXACTLY 7-9 specific tags (3-4 words): long-tail, experience-based
- EXACTLY 1 trending tag: 2026 format
- EXACTLY 1 #Shorts tag: always include
- Order: Highest search volume first
- Include: "youtube shorts", "body facts", "brain science", "explained"
- NO age-specific terms ("after 40", "over 35")

Topic: {topic}
Keywords: {keywords}

Return format: One tag per line, no numbers, no bullets.
"""

# ═══════════════════════════════════════════════════════════
# MODERN HOOK TEMPLATES — Universal, All Age
# ═══════════════════════════════════════════════════════════
MODERN_HOOK_TEMPLATES = [
    # Universal experience hooks
    "Your body is doing something RIGHT NOW you don't know about...",
    "This happens to your body every single day without warning...",
    "Your body has been hiding something from you your whole life...",
    "Every single day your body does {topic}... and nobody explains why...",

    # Nobody tells you hooks
    "Nobody ever explains why your body does {topic}...",
    "Nobody warns you what {topic} actually does to your brain...",
    "Nobody mentions what really happens when {topic} occurs...",
    "Nobody teaches you what your body does with {topic}...",

    # This is why hooks
    "This is why you keep experiencing {topic}...",
    "This is what your brain actually does during {topic}...",
    "This explains why {topic} happens to you...",
    "This is the real reason behind {topic}...",

    # Curiosity gap hooks
    "The reason {topic} happens is SIMPLER than you think...",
    "The truth about {topic} is genuinely surprising...",
    "The science behind {topic} will change how you see your body...",
    "The real reason behind {topic} is unexpected...",

    # Relief hooks
    "Your body isn't broken... it's just doing {topic}...",
    "You're not alone — your brain does {topic} to everyone...",
    "You've felt {topic} your whole life... here's why...",

    # Direct science hooks
    "What actually happens in your body during {topic}...",
    "Here's what {topic} actually does to your brain...",
    "What {topic} does to your body is fascinating...",
    "What science found about {topic} is unexpected...",
]


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    if '{NEGATIVE_CONSTRAINTS}' in template:
        kwargs.setdefault('NEGATIVE_CONSTRAINTS', NEGATIVE_CONSTRAINTS)
    return template.format(**kwargs)


def generate_modern_hooks(topic: str, count: int = 5) -> List[str]:
    hooks = []
    templates = random.sample(MODERN_HOOK_TEMPLATES, min(count, len(MODERN_HOOK_TEMPLATES)))
    for template in templates:
        hook = template.format(topic=topic)
        hooks.append(hook)
    return hooks


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 TESTING PROMPTS\n" + "="*60)

    print("\n📝 TITLE PROMPT:")
    title_prompt = format_prompt(VIRAL_TITLE_GENERATOR, topic="why your body jerks before sleep")
    print(title_prompt[:500] + "...")

    print("\n🎬 SCRIPT PROMPT:")
    script_prompt = format_prompt(
        VIRAL_SCRIPT_GENERATOR,
        topic="why your body jerks before sleep",
        angle="Universal body mystery everyone experiences",
        shock_angle="Your brain literally thinks you are falling"
    )
    print(script_prompt[:500] + "...")

    print("\n🎯 MODERN HOOKS:")
    hooks = generate_modern_hooks("why your body jerks before sleep", 5)
    for i, hook in enumerate(hooks, 1):
        print(f"   {i}. {hook}")

    print("\n" + "="*60)
    print("✅ All prompts loaded successfully!")
