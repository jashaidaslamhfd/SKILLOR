"""AI Prompts for Groq — 2026 Viral Formula (USA Audience)
   NICHE: Body + Brain Science (Mystery Crispy Style)
   TARGET: USA PRIMARY | All Ages (13-65+) | English
   FORMAT: YouTube Shorts (42-55 seconds)
   GOAL: 0% Swipe Rate | 70%+ Retention | Viral Titles
   STRUCTURE: Hook (1.5s) → Shock → Suspense → Story → CTR
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
- "Why do I feel tired all the time?"
- "Why can't I focus anymore?"
- "Why does my body do weird things?"
- "I thought I was the only one"
- "Nobody ever explained this to me"

WHAT WORKS IN USA:
- Relatable, surprising, "OMG that happens to ME"
- Direct, confident, no fluff
- American English ONLY (color, favor, organize)
- Fast-paced, no slow build-ups
- Clear value proposition in first 3 seconds

WHAT FAILS IN USA:
- Age-specific content ("after 35", "over 40")
- Gender-specific content ("men", "women")
- Medical jargon or horror tone
- British spelling (colour, favour, organise)
- Slow introductions
- Questions (weaker than statements)
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
6. NO parenting or children topics
7. NO British spelling — use American English ONLY:
   color (not colour), favor (not favour), organize (not organise)
   recognize (not recognise), behavior (not behaviour)
   program (not programme), center (not centre)
   fiber (not fibre), defense (not defence)
8. If ANY of these appear, the script is REJECTED
"""

# ═══════════════════════════════════════════════════════════
# 2026 HOOK PSYCHOLOGY — USA SWIPE RATE KILLER
# ═══════════════════════════════════════════════════════════
HOOK_PSYCHOLOGY_2026 = """
MODERN HOOK RULES (2026) — USA AUDIENCE:

CRITICAL: 70% of USA viewers decide to stay or swipe in the FIRST 1.5 SECONDS.
The hook MUST deliver an irresistible pattern interrupt in the FIRST 3 WORDS.

OLD hooks = INSTANT SWIPE (USA audience specifically):
- "Did you know" → passive, boring, sounds like school
- "Scientists discovered" → too formal, sounds like homework
- "Shocking truth" → overused, nobody believes it
- Questions → weaker than statements for USA audience
- Slow build-ups → USA viewers swipe faster than any other market

WHAT WORKS IN USA 2026 — SWIPE STOPPERS:

1. FIRST 3 WORDS must be a PATTERN INTERRUPT:
   - "Your body RIGHT NOW..." (urgency + personal)
   - "Nobody explains why..." (exclusion + curiosity)
   - "This happens EVERY..." (frequency + universality)
   - "You've felt this..." (recognition + validation)

2. Universal experience: "Your body does this every single day..."

3. Curiosity gap WITHIN FIRST 5 WORDS: "...and nobody ever explains why"

4. Urgency words in FIRST LINE: "ALREADY", "RIGHT NOW", "THIS SECOND", "EVERY DAY"

5. Personal: ALWAYS "you/your" — never "people" or "humans"

6. Relatable mystery: something they've experienced but never understood

7. THE 1-SECOND RULE: The VERY FIRST WORD must create recognition.
   If the viewer doesn't think "that's me" within 1 second, they swipe.
   Start with: "Your", "You've", "This", "Nobody", "Every"
   NEVER start with: "The", "A", "An", "When", "If", "Have"

8. THE 3-SECOND COMMITMENT: By second 3, the viewer must feel:
   - "This is about ME" (personal recognition)
   - "I didn't know this" (curiosity gap opened)
   - "I need to hear the answer" (investment created)

FORMULA: [Pattern Interrupt] + [Happening RIGHT NOW] + [Curiosity gap]
Example: "Your body is doing something RIGHT NOW... and you have no idea why"

ANTI-PATTERN: "There's an interesting fact about your body..." → SWIPE (too slow)
"""

# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR — USA SEO 2026
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for USA audience in 2026.

GOAL: Create titles that make USA viewers think "wait... this is about ME"
AUDIENCE: USA primary (13-65+), all genders

OLD TITLES (AVOID — will cause swipe in USA):
❌ "Did you know..."
❌ "Scientists discovered..."
❌ "Shocking truth..."
❌ "Mind-blowing fact..."
❌ Any question format
❌ Age-specific ("after 40", "for men over 35")
❌ British spelling (colour, favour, organise)

WINNING TITLE TYPES FOR USA:

🟢 Type 1 — "Your body/brain" hooks:
✅ "Your body does this every single day..."
✅ "Your brain is ALREADY doing this right now"
✅ "Your body has been hiding this from you"
✅ "Your brain does this while you sleep"

🟢 Type 2 — "Why" hooks (universal USA curiosity):
✅ "Why your body does [X]"
✅ "Why you feel [X] for no reason"
✅ "Why your brain can't stop [X]"
✅ "Why [X] happens to everyone"

🟢 Type 3 — Mystery hooks (USA loves insider knowledge):
✅ "Nobody explains why [X] happens"
✅ "The real reason your body [X]"
✅ "What nobody tells you about [X]"
✅ "The hidden reason behind [X]"

🟢 Type 4 — Relatable USA experience hooks:
✅ "That feeling when your body [X]... explained"
✅ "Why you always [X] and never knew why"
✅ "This happens to your body every day"

🟢 Type 5 — Science made simple (USA education style):
✅ "The science of [X] explained simply"
✅ "[X] explained in 45 seconds"
✅ "What [X] actually does to your body"

TITLE RULES:
- 5-8 words MAX + 1 emoji at the end
- NO age or gender references ("after 35", "men", "women")
- MUST be a statement (not question)
- MUST create curiosity gap
- MUST feel universal — any age should think "this is me"
- MUST use American English spelling
- NO repeating words in the same title
- NO incomplete sentences or cut-off words
- Each title must be COMPLETE and make sense on its own
- Title MUST be 15-55 characters (YouTube Shorts sweet spot)

TOPIC: {topic}

IMPORTANT:
- Return EXACTLY 5 titles
- One title per line
- No numbers, no bullets, no dashes
- No explanations or headers
- Just the 5 titles, nothing else
"""

# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — USA 2026
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are a YouTube Shorts script writer for USA audience in 2026.

AUDIENCE: USA PRIMARY — anyone who has a body and a brain.
TONE: Like a brilliant friend explaining something over text — casual, clear, a little mind-blowing.
GOAL: Make them feel "OMG I never knew this" then hook them to follow.

STRUCTURE: Hook → Shock → Suspense → Problem → Solution → Loopback → CTR
TARGET: 40-55 seconds spoken at natural pace

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### HOOK (8-10 words, 1.5-2.5 seconds) — THE SWIPE DECISION MOMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
70% of USA viewers decide in 1.5 seconds. This is the MOST IMPORTANT part.
THE FIRST 3 WORDS ARE EVERYTHING. They must create INSTANT recognition.
If the viewer doesn't think "that's me" in 1 second, they swipe away forever.

FORBIDDEN hooks (these cause INSTANT swipe in USA):
❌ "Have you ever wondered..." (slow, passive)
❌ "Did you know..." (boring, sounds like school)
❌ "Scientists have discovered..." (formal, impersonal)
❌ "After age 35..." (age-specific, alienates younger viewers)
❌ "There's something..." (weak opener, no urgency)
❌ Any question format (USA viewers prefer statements)
❌ Any hook longer than 10 words (viewer already swiped)
❌ Any hook starting with "The", "A", "An", "When", "If", "Have"

SWIPE-STOPPER hooks (pick style based on topic):
✅ "Your body is doing something RIGHT NOW you don't know about..."
✅ "Nobody ever explains why your brain does this..."
✅ "This happens to your body every single day..."
✅ "Your brain has been keeping a secret from you..."
✅ "You've felt this your whole life... here's why..."
✅ "Every single person experiences this... nobody explains it..."
✅ "Your body does this without you realizing..."

RULES:
✓ Start with "Your", "Nobody", "This", "You've", "Every" — FIRST WORD = recognition
✓ NEVER start with "The", "A", "An", "When", "If", "Have" — too slow for USA
✓ Universal — any age, any gender should nod their head
✓ Statement NOT question — statements create certainty
✓ 8-10 words only — every extra word = more swipes
✓ End with "..." — creates open loop that demands closure
✓ Must contain at least ONE urgency word: "RIGHT NOW", "EVERY DAY", "ALREADY"
✓ The viewer must feel "that's me" within the FIRST 3 WORDS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### SHOCK (8-10 words, 2-3 seconds):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
One surprising fact that confirms they were right to stay.
Calm, confident tone — "whoa" not "terrifying".
End with "..."

Examples (USA-friendly):
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
- Universal USA experiences anyone can relate to
- Natural pause midway: "..."
- Always "you/your" — never "people", "humans", "individuals"
- End with LOOPBACK — callback to hook for satisfying close

Example: "Your brain has a built-in filter. And it runs 24 hours a day. Its job is to decide what matters... and delete the rest. The problem is it doesn't always get it right. But here's the good part — once you understand the pattern, you can start to work with it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### CTR (12-15 words, 5-6 seconds) — ENGAGEMENT HOOK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Callback to hook — satisfying loop close + ENGAGEMENT TRIGGER.

MANDATORY STRUCTURE: Loopback + Like/Comment CTA + Follow
The CTR MUST explicitly ask for a like or comment. This is NON-NEGOTIABLE.
Without a direct ask, USA viewers watch and scroll — zero engagement.

REQUIRED FORMULA: [Loopback phrase] + [Direct Like/Comment ask] + [Follow]

Examples (USA-tested):
"Your body just told you something. Like if you felt it. Follow for more."
"That's why it keeps happening. Comment 'me' if this is you. Follow."
"Your brain knew before you did. Smash like if this blew your mind. Follow."
"Same thing that made you curious? Like this. Subscribe for Part 2."
"Now you know the secret. Drop a like if your body did this. Follow."

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
- AMERICAN ENGLISH ONLY: Use "color" not "colour", "favor" not "favour", 
  "organize" not "organise", "recognize" not "recognise", 
  "behavior" not "behaviour", "program" not "programme", 
  "center" not "centre", "fiber" not "fibre", "defense" not "defence"
- Target audience is USA — use USA cultural references

Topic: {topic}
Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with exact markers. No extra text. No explanations.
"""

# ═══════════════════════════════════════════════════════════
# SHOCK MOMENT GENERATOR — USA 2026
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising fact for video editing emphasis.

Audience: USA — universal, anyone with a body/brain.
Feel: "whoa I never knew that" NOT "oh god that's terrifying"

Rules:
- 8-10 words maximum
- About: {topic}
- Tone: calm but surprising — "quietly", "actually", "without you realizing"
- NO age or gender references
- Avoid: "terrifying", "horrifying", "deadly", "destroying"
- Use: "fascinating", "surprising", "unexpected", "worth knowing"
- American English spelling ONLY

{NEGATIVE_CONSTRAINTS}

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the fact text, no markers, no extra words.
"""

# ═══════════════════════════════════════════════════════════
# SEO DESCRIPTION — USA 2026 (YouTube Algorithm)
# ═══════════════════════════════════════════════════════════
SEO_DESCRIPTION_GENERATOR = """
Write a YouTube Shorts description for USA audience in 2026.

RULES:
- STRICT LENGTH: 100-150 words
- FIRST LINE: Hook with main keyword + "#Shorts"
- First 2 lines visible before "...more" — make them count
- Include timestamps: Hook 0:00, Key fact 0:08, Main insight 0:15, Takeaway 0:40
- 3-5 hashtags: include #Shorts, plus 2-3 topic-relevant hashtags
- CTA: "Follow for more science nobody teaches you"
- Keywords: {keywords}
- Natural placement, NO keyword stuffing
- Tone: curious, credible — like a science newsletter
- American English ONLY
- USA targeting: mention "USA" or "Americans" naturally if relevant

Topic: {topic}
"""

# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — USA SEO 2026
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags for USA audience in 2026.

USA search behavior:
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
- Include USA-specific: "usa health", "american"
- NO age-specific terms ("after 40", "over 35")

Topic: {topic}
Keywords: {keywords}

Return format: One tag per line, no numbers, no bullets.
"""

# ═══════════════════════════════════════════════════════════
# MODERN HOOK TEMPLATES — USA Tested 2026
# ═══════════════════════════════════════════════════════════
MODERN_HOOK_TEMPLATES = [
    # Universal experience hooks (USA approved)
    "Your body is doing something RIGHT NOW you don't know about...",
    "This happens to your body every single day without warning...",
    "Your body has been hiding something from you your whole life...",
    "Every single day your body does {topic}... and nobody explains why...",

    # Nobody tells you hooks (USA loves insider info)
    "Nobody ever explains why your body does {topic}...",
    "Nobody warns you what {topic} actually does to your brain...",
    "Nobody mentions what really happens when {topic} occurs...",
    "Nobody teaches you what your body does with {topic}...",

    # This is why hooks (USA curiosity)
    "This is why you keep experiencing {topic}...",
    "This is what your brain actually does during {topic}...",
    "This explains why {topic} happens to you...",
    "This is the real reason behind {topic}...",

    # Curiosity gap hooks (USA loves secrets)
    "The reason {topic} happens is SIMPLER than you think...",
    "The truth about {topic} is genuinely surprising...",
    "The science behind {topic} will change how you see your body...",
    "The real reason behind {topic} is unexpected...",

    # Relief hooks (USA relatable)
    "Your body isn't broken... it's just doing {topic}...",
    "You're not alone — your brain does {topic} to everyone...",
    "You've felt {topic} your whole life... here's why...",

    # Direct science hooks (USA education style)
    "What actually happens in your body during {topic}...",
    "Here's what {topic} actually does to your brain...",
    "What {topic} does to your body is fascinating...",
    "What science found about {topic} is unexpected...",
]

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with kwargs"""
    if '{NEGATIVE_CONSTRAINTS}' in template:
        kwargs.setdefault('NEGATIVE_CONSTRAINTS', NEGATIVE_CONSTRAINTS)
    return template.format(**kwargs)


def generate_modern_hooks(topic: str, count: int = 5) -> List[str]:
    """Generate modern hooks for a topic"""
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
    print("🚀 TESTING PROMPTS (USA 2026)\n" + "=" * 60)

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

    print("\n" + "=" * 60)
    print("✅ All prompts loaded successfully!")
