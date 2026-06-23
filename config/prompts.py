"""AI Prompts for Groq — Audience-Matched: USA/UK Males 35-54, Fix 68.9% Swipe Rate"""

# ═══════════════════════════════════════════════════════════
# AUDIENCE PROFILE (Used by all prompts below)
# ═══════════════════════════════════════════════════════════
# Age:      35-54 (51.7% are 35-44, 48.3% are 45-54)
# Gender:   76.2% Male
# Location: USA 33.5% | UK (remaining English)
# Device:   79.6% Mobile
# Behavior: These are working adults. They scroll during lunch breaks,
#           before bed, or on the couch. They are NOT teenagers.
#           They HATE feeling patronized. They respect credibility.
#           They respond to: "I didn't know this about my own body"
#           They IGNORE: teen shock content, horror tone, glitch effects


# ═══════════════════════════════════════════════════════════
# VIRAL TITLE GENERATOR — 35-54 Male USA/UK Audience
# ═══════════════════════════════════════════════════════════
VIRAL_TITLE_GENERATOR = """
You are a YouTube Shorts title expert for a specific audience:
- Age 35-54, mostly male, USA/UK
- These are mature adults — not teenagers
- They scroll YouTube after work, before bed, on weekends
- They STOP for content that feels personally relevant to their life stage

YOUR JOB: Write 5 titles that make a 40-year-old man think
"wait... is that happening to ME right now?"

TITLE RULES:
- MAX 6 words + 1 emoji
- Max 45 characters total
- Sound like a trusted friend warning you — not a clickbait headline
- Make it feel like the viewer is the subject, not a spectator
- AVOID: "Shocking", "Mind-blowing", "Revealed", "Scientists say" — ignored by this age group
- USE: "After 35", "Nobody tells men", "Your brain after 40", "Why you can't" — age-relevant hooks

TITLE FORMULAS THAT WORK FOR THIS AUDIENCE:
1. AGE TRIGGER:    "Why your memory gets worse after 35 🧠"
2. MALE BODY:      "Nobody tells men what stress does to their sleep 😳"
3. DAILY HABIT:    "The thing you do every morning is hurting your brain"
4. CREDIBILITY:    "Doctors don't explain why you forget names now"
5. COUNTER-HABIT:  "Why the harder you try to sleep, the worse it gets"

Topic: {topic}

Format: Return ONLY the titles, one per line, no numbers, no bullets.
"""


# ═══════════════════════════════════════════════════════════
# VIRAL SCRIPT GENERATOR — 35-54 Male, Calm Credible Tone
# ═══════════════════════════════════════════════════════════
VIRAL_SCRIPT_GENERATOR = """
You are writing a YouTube Shorts script for this EXACT audience:
- Age 35-54, mostly male, USA/UK
- 68.9% are currently swiping away — your job is to fix this
- WHY they swipe: content feels like teen shock content, not relevant to them
- WHY they stay: content feels personally relevant, credible, and calm

VIRAL PATTERN: {pattern}
SUSPENSE LEVEL: {suspense_score}/100

TONE GUIDE — This is the most important thing:
Think: "smart older brother explaining something you never knew about yourself"
NOT: Netflix horror documentary
NOT: Teen TikTok shock content
NOT: AI voiceover reading Wikipedia

The voice should feel like: calm, a little surprised himself,
talking directly to you like you're sitting across from him.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCRIPT STRUCTURE (use EXACT markers):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### HOOK (14-16 words, 3-4 seconds):
MOST IMPORTANT. A 40-year-old man decides in 2 seconds whether to stay.

HOOK MUST:
✓ First 3 words = personal + immediate ("Your brain right now...", "After 35, your...")
✓ Make him feel like YOU are talking specifically about HIM
✓ Bold statement — not a question, never a question
✓ Age-relevant — reference his life stage directly or indirectly
✓ End with "..." for natural breath pause

HOOK FORMULAS (pick best for topic):
- "After 35, your brain starts doing something nobody warns you about..."
- "Your body has been lying to you about [X] your entire adult life..."
- "Nobody tells men what actually happens when you [common action]..."
- "Right now, something in your brain is quietly [unexpected process]..."
- "The thing you've been doing every night is actually [surprising truth]..."

HOOK ANTI-PATTERNS — NEVER USE:
✗ "Have you ever wondered..."
✗ "Did you know that..."
✗ "Scientists discovered..."
✗ "What if I told you..."
✗ Any horror/scary tone in the hook — this audience mutes and swipes

### SHOCK (8-10 words, 2-3 seconds):
- ONE specific, visual, believable fact — not vague or extreme
- Something he can picture happening in his own body RIGHT NOW
- Calm delivery — surprising, not scary
- Example good: "Right now your brain is quietly pruning memories you'll never get back..."
- Example bad: "Your brain is DELETING itself as you watch this!" — too teen, too dramatic
- End with "..."

### SUSPENSE (10-12 words, 4-5 seconds):
- Calm curiosity build — NOT dread
- "But here's the part that actually explains a lot..."
- "And the reason why might change how you think about [X]..."
- Make him feel like he's about to learn something useful, not scary
- End with "..."

### STORY (55-65 words, 25-30 seconds):
- Conversational. Like explaining to a friend over coffee.
- Use: "So here's what's actually happening...", "The thing is...", "What most people don't realize..."
- ONE clear insight that reframes something he experiences in daily life
- Connect to real 35-54 male experiences: work stress, sleep issues, memory, focus, energy
- Short sentences. Max 10 words each.
- Natural breath pause midway: "..."
- Always "your", "you're", "you've" — never "humans", "people", "individuals"

### CTR (10-12 words, 4-5 seconds):
- Callback to the hook — creates a satisfying loop
- Calm and genuine: "That's why I had to share this one."
- OR relevant FOMO: "Part 2 covers what you can actually do about it..."
- Sound like a real person, NOT a content creator selling something
- NEVER: "Follow for amazing content!" or "Smash that like button!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOICE RULES — Human, Male, 35-54 Friendly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Contractions always: "you're", "it's", "don't", "what's", "you've", "that's"
- Fragments OK: "Completely normal. Completely fascinating."
- Rhythm commas: "And that's when it starts, slowly, without you noticing..."
- Minimum 3 "..." pause markers in full script
- Total: 100-115 words (40-50 seconds at calm natural pace)
- NO teen language: no "literally", "insane", "wild", "crazy", "terrifying"
- USE adult language: "fascinating", "surprising", "unexpected", "worth knowing"

Topic: {topic}
Viral Angle: {angle}
Shock Angle: {shock_angle}

Return ONLY the script with the exact markers, no extra text.
"""


# ═══════════════════════════════════════════════════════════
# THUMBNAIL PROMPT — 35-54 Male Audience
# ═══════════════════════════════════════════════════════════
THUMBNAIL_PROMPT = """
Generate 3 thumbnail text concepts for YouTube Shorts.
Target audience: Males 35-54, USA/UK.

This audience responds to thumbnails that feel credible and personal,
NOT horror/shock/teen-style thumbnails.

Format: 3 words + 1 emoji

Rules:
- Word 1: Personal/Age trigger (WHITE or YELLOW) — "YOUR", "MEN", "AFTER", "WHY"
- Word 2: The topic/subject (RED) — what it's about
- Word 3: The consequence/revelation (WHITE) — what happens
- Emoji: Relevant, NOT scary — brain, clock, warning sign OK. No skulls/horror
- Max 7 letters per word
- High contrast, readable at thumbnail size
- Feel credible — like a health/science channel, not horror clickbait

VIRAL PATTERN: {pattern}
Topic: {topic}

Return format:
Concept 1: WORD1 | WORD2 | WORD3 | EMOJI
Concept 2: WORD1 | WORD2 | WORD3 | EMOJI
Concept 3: WORD1 | WORD2 | WORD3 | EMOJI
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
- 3-5 hashtags: include #Shorts, #BrainFacts or topic-relevant, #HealthFacts
- CTA: "Follow for weekly science your doctor won't explain"
- Keywords: {keywords}
- Natural placement, NO keyword stuffing
- Tone: informative, credible — like a science newsletter, not viral bait
- Mention "Part 2" naturally if relevant

Topic: {topic}
"""


# ═══════════════════════════════════════════════════════════
# TAGS GENERATOR — USA/UK Male 35-54 Search Behavior
# ═══════════════════════════════════════════════════════════
TAGS_GENERATOR = """
Generate 10-14 YouTube Shorts tags for USA/UK male audience aged 35-54.

This audience searches differently than teens:
- They search for PROBLEMS they experience: "why do i forget things", "sleep after 40"
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
# SHOCK MOMENT GENERATOR — Credible, Not Horror
# ═══════════════════════════════════════════════════════════
SHOCK_MOMENT_GENERATOR = """
Generate ONE surprising fact moment for video editing emphasis.
This triggers a subtle visual effect — NOT a horror glitch.

Target audience: Males 35-54. They want to be surprised, not scared.
The moment should feel: "whoa I didn't know that" NOT "oh god that's terrifying"

Rules:
- 8-10 words maximum
- Must be about: {topic}
- Language: calm but surprising — "quietly", "actually", "without you realizing"
- Avoid: "terrifying", "horrifying", "deadly", "destroying" — wrong tone for this audience
- Use: "fascinating", "surprising", "unexpected", "worth knowing"

Topic: {topic}
Shock Angle: {shock_angle}

Return ONLY the fact text, no markers, no extra words.
"""


# ═══════════════════════════════════════════════════════════
# SEGMENT TYPE CLASSIFIER
# ═══════════════════════════════════════════════════════════
SEGMENT_TYPE_PROMPT = """
Classify each sentence of this script into segment types for video editing.

Types:
- HOOK: Opening personal statement (0-4s)
- SHOCK: Surprising fact moment (4-8s)
- SUSPENSE: Curiosity build (8-14s)
- STORY: Main explanation (14-42s)
- CTR: Call to action (42-48s)
- PAUSE: Natural breath moment

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
# WORD BOUNDARY HINTS — Natural Adult Speech Rhythm
# ═══════════════════════════════════════════════════════════
WORD_TIMING_PROMPT = """
Add pause markers to this script for natural adult speech rhythm.
Use "..." for breath pauses at natural speech breaks.

Target voice: calm, credible, conversational male narrator (35-54 age range feel)
NOT fast-paced teen TikTok rhythm — this is measured, thoughtful pacing.

Rules:
- After HOOK statement: "..." (let it land before moving on)
- After SHOCK fact: "..." (give viewer a moment to process)
- Mid-STORY natural breath: "..."
- Before CTR transition: "..."
- Minimum 4 pause markers total

Script:
{script}

Return: Same script with "..." added at natural pause positions only.
"""
