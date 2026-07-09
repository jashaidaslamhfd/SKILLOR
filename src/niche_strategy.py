# src/niche_strategy.py
import random

DARK_TOPICS = [
    "Your Heart Has Its Own Brain",
    "Your Body Has 100,000 km of Veins",
    "Why Your Heart Skips a Beat",
    "This Happens Inside Your Brain When You Sleep",
    "Your Lungs Can Drown You From Inside",
    "The Bone That Breaks Most in Fights",
    "Your Blood Has a Secret Weapon",
    "Why You Get Goosebumps",
    "Your Stomach Can Digest Itself",
    "The Organ You Can Live Without",
]

HOOK_FORMULAS = [
    "This happens to your body every night... and you have no idea.",
    "Doctors don't want you to know this about {topic}...",
    "Your body is lying to you about {topic}. Here's the truth.",
]

PAIN_POINTS = [
    "Worried something is wrong with your body",
    "Can't sleep because your mind won't shut off",
    "Feel anxious about random body symptoms",
]

CTAS = [
    "Follow for more dark body secrets",
    "Share this if it blew your mind",
    "Comment: Did this happen to you?",
]

CATEGORY_TAGS = {
    "Brain": [
        "neuroscience", "brainfacts", "psychologyfacts", "mindblown",
        "brainscience", "humanbrain", "nerveoussystem", "mentalhacks"
    ],
    "Body": [
        "humanbody", "bodyfacts", "anatomy", "bodyparts", "humanfacts",
        "bodyawareness", "bodymystery", "yourbiody"
    ],
    "Mystery": [
        "mysteryscience", "weirdfacts", "creepyfacts", "unknownfacts",
        "darkscience", "bodysecrets", "themoreyouknow", "mindblowing"
    ],
    "Health": [
        "healthfacts", "bodyhacks", "sciencefacts", "healthscience",
        "medicalmystery", "humanhealth", "wellness"
    ],
}
# Strong base tags — YouTube search-optimized for dark/mystery science niche
BASE_TAGS = [
    "darkfacts", "facts", "shorts", "youtubeshorts", "science",
    "didyouknow", "mindblowing", "funfacts", "scaryfacts", "viral"
]
# Kept in sync with script_generator.py's MIN_WORDS/MAX_WORDS - these two
# used to disagree (110-150 here vs an effective 120-180 there), so any
# script that hit *this* file's own target could still fail validation.
TARGET_WORD_RANGE = (130, 160)


def _make_seo_title(title: str, topic: str) -> str:
    """Enhances the AI-generated title with CTR-boosting patterns common in
    dark-facts shorts without being clickbaity enough to get flagged.
    Keeps it under 70 chars (YouTube truncates beyond that in search)."""
    # If the title already has a strong hook pattern leave it alone
    power_words = ["secret", "nobody", "never", "actually", "dark", "scary",
                   "real", "hidden", "warning", "shock", "fact", "truth"]
    if any(pw in title.lower() for pw in power_words):
        return title[:55]

    # Prefix with a hook emoji + badge that performs well in dark-science niche
    enhanced = f"🫀 {title}"
    if len(enhanced) <= 55:
        return enhanced
    return title[:55]


def get_random_topic() -> str:
    return random.choice(DARK_TOPICS)


def get_topic_category(topic: str) -> str:
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ['brain', 'mind', 'sleep', 'nerve', 'psych']):
        return "Brain"
    elif any(word in topic_lower for word in ['heart', 'blood', 'lung', 'kidney', 'bone', 'organ']):
        return "Body"
    elif any(word in topic_lower for word in ['scary', 'secret', 'kill', 'dark', 'mystery', 'hidden']):
        return "Mystery"
    else:
        return "Body"


def get_script_prompt_for_niche(topic: str, hook_preference: str = None) -> str:
    if not hook_preference:
        hook_preference = HOOK_FORMULAS[hash(topic) % len(HOOK_FORMULAS)]
    pain_point = PAIN_POINTS[hash(topic) % len(PAIN_POINTS)]
    cta = CTAS[hash(topic) % len(CTAS)]
    min_w, max_w = TARGET_WORD_RANGE
    num_scenes = 7
    per_scene_lo = min_w // num_scenes
    per_scene_hi = max_w // num_scenes
    prompt = f"""
You are an expert mystery science communicator creating DARK MYSTERY YouTube Shorts for USA adults 18+.
Topic: {topic}
SCRIPT REQUIREMENTS: 1. DARK HOOK: "{hook_preference}" 2. RELATE 3. SCIENCE 4. RELIEF 5. CTA: "{cta}"
TONE: Dark, mysterious, factual. PAIN POINT: {pain_point}

WORD COUNT IS A HARD REQUIREMENT - read this carefully:
- The full voiceover (all captions combined) MUST total {min_w}-{max_w} words. Not less.
- "Punchy" and "high pacing" means short SENTENCES, not short SCRIPTS - use several
  punchy sentences per scene rather than one clipped fragment. A scene like
  "Your heart is lying." is too short; a scene like "Your heart is lying to you
  right now, and it has been since the day you were born." is the right density.
- Split the script into exactly {num_scenes} scenes. Each scene's "caption" should be
  roughly {per_scene_lo}-{per_scene_hi} words on its own - if a caption is much shorter
  than that, add another punchy sentence to it before moving to the next scene.
- Before you finalize your answer, mentally count the total words across all
  captions and confirm it falls in the {min_w}-{max_w} range. If it's short, expand
  scenes with more concrete detail/science rather than padding with filler.

Each scene needs:
  - "visual": 5-8 word description for image generation (what should be shown on screen)
  - "caption": the EXACT spoken text for that scene (captions concatenated in
    order must reconstruct the full voiceover word-for-word, total {min_w}-{max_w} words)

Return ONLY valid JSON, no other text, in exactly this shape:
{{"title": "short catchy video title", "hook": "{hook_preference}", "scenes": [{{"visual": "...", "caption": "..."}}], "cta": "{cta}", "description": "1-2 sentence video description"}}
"""
    return prompt


def get_seo_tags(topic: str, category: str = "Body") -> list:
    """Returns YouTube-optimized tag list (max 15 tags, mix of broad + niche)."""
    tags = BASE_TAGS.copy()
    tags.extend(CATEGORY_TAGS.get(category, []))
    # Add topic-specific keyword tags (each word separately for broader reach)
    topic_words = [w for w in topic.lower().split() if len(w) > 3]
    tags.extend(topic_words[:4])
    # Deduplicate and cap at 15 (more tags beyond ~15 don't help YouTube SEO)
    seen, result = set(), []
    for t in tags:
        clean = t.strip().lower().replace(' ', '')
        if clean and clean not in seen:
            seen.add(clean)
            result.append(t)
        if len(result) >= 15:
            break
    return result


def generate_seo_tags(topic: str, category: str = "Body", title: str = "") -> list:
    return get_seo_tags(topic, category)


_MEDICAL_ADVICE_RED_FLAGS = [
    "cure", "diagnose", "you have", "stop taking", "don't need a doctor",
    "instead of medication", "guaranteed to heal", "definitely means you have",
]


def validate_script_for_medical_accuracy(script_data: dict) -> dict:
    """This channel presents body/brain 'facts' to a general audience, so
    scripts must not read as an actual medical diagnosis or instruction to
    ignore professional care. Flags a short list of red-flag phrases;
    if any are found, auto_add_disclaimer() below adds a disclaimer."""
    voiceover = script_data.get('voiceover', '') or ' '.join(
        s.get('caption', '') for s in script_data.get('scenes', []) if isinstance(s, dict)
    )
    lowered = voiceover.lower()
    flags = [phrase for phrase in _MEDICAL_ADVICE_RED_FLAGS if phrase in lowered]
    return {"valid": len(flags) == 0, "flags": flags}


def auto_add_disclaimer(script_data: dict) -> dict:
    """Appends a short educational-only disclaimer to the CTA/description so
    a flagged script doesn't read as medical advice."""
    disclaimer = "This video is for educational/entertainment purposes only and is not medical advice. Consult a doctor for any health concerns."
    script_data['cta'] = (script_data.get('cta', '') + " " + disclaimer).strip()
    script_data['disclaimer_added'] = True
    return script_data
