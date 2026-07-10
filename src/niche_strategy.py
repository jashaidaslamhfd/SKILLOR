"""
Niche Strategy Module for SKILLOR Pipeline
OPTIMIZED FOR: HIGH RETENTION + PSYCHOLOGICAL PACING
"""

import logging
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ============================================
# 1. EXPANDED DARK TOPICS (100+ topics)
# ============================================
DARK_TOPICS = [
    # Brain / Mind / Neuroscience (25+)
    "Your Heart Has Its Own Brain",
    "This Happens Inside Your Brain When You Sleep",
    "Why You Get Goosebumps",
    "Your Brain Eats Itself While You Sleep",
    "The Part of Your Brain That Never Sleeps",
    "Why Your Brain Lies to You Every Day",
    "This Is What Deja Vu Actually Is",
    "Your Brain Can Rewire Itself Overnight",
    "The Reason You Talk to Yourself in Your Head",
    "Why Nightmares Exist At All",
    "Your Brain Deletes Memories on Purpose",
    "The Real Reason You Freeze Under Pressure",
    "Why Some People Never Forget a Face",
    "Your Brain Has a Hidden Backup System",
    "The Chemical That Makes You Fall in Love",
    "Why Your Brain Processes Fear Faster Than Logic",
    "The Part of Your Brain That Never Stops Growing",
    "Why You Can't Remember Being a Baby",
    "Your Brain Has Its Own Immune System",
    "The Reason You Get Brain Freeze",
    "Why Your Brain Shrinks When You're Depressed",
    "The Secret Language of Your Brain Waves",
    "Why Your Brain Makes You See Ghosts",
    "The Reason Your Brain Forgets Names",
    "Your Brain Creates Reality, Not Just Perceives It",
    
    # Heart / Blood / Circulatory (20+)
    "Your Body Has 100,000 km of Veins",
    "Why Your Heart Skips a Beat",
    "Your Blood Has a Secret Weapon",
    "Your Heart Beats 100,000 Times a Day Without Asking",
    "The Sound Your Heart Makes That You've Never Heard",
    "Why Your Face Turns Red When You're Angry",
    "The Reason Cold Hands Mean a Warm Heart",
    "Your Blood Changes Color Inside Your Body",
    "Your Heart Can Predict Your Death",
    "The Secret Behind Your Heartbeat",
    "Why Your Blood Is Actually Blue Inside",
    "Your Heart Has Its Own Electrical System",
    "The Reason Your Pulse Changes When You Lie",
    "Your Blood Vessels Could Circle the Earth",
    "Why Your Heart Breaks When You're Sad",
    "The Hidden Power of Your Blood Type",
    "Why Your Heart Beats Faster in the Morning",
    "The Reason Your Blood Clots When You Cut Yourself",
    "Your Heart Has a Memory of Its Own",
    "Why Your Blood Pressure Rises When You're Stressed",
    
    # Lungs / Breathing (15+)
    "Your Lungs Can Drown You From Inside",
    "Why You Yawn When You See Someone Else Yawn",
    "The Real Reason You Can't Tickle Yourself",
    "Why Holding Your Breath Feels Like Panic",
    "Your Lungs Have Their Own Cleaning System",
    "The Reason You Sneeze When You Look at Light",
    "Your Breathing Changes When You Think",
    "Why Your Lungs Never Fully Empty",
    "The Secret Power of Deep Breathing",
    "Why You Breathe Differently at Night",
    "The Reason Your Lungs Hurt in Cold Weather",
    "Your Lungs Can Heal Themselves",
    "Why Asthma Attacks Happen at Night",
    "The Hidden Connection Between Breath and Anxiety",
    "Why Your Breathing Slows When You Sleep",
    
    # Bones / Muscles (15+)
    "The Bone That Breaks Most in Fights",
    "Your Bones Are Being Replaced Right Now",
    "Why Cracking Your Knuckles Makes That Sound",
    "The Strongest Muscle in Your Body Isn't What You Think",
    "Why You Lose Height During the Day",
    "Your Bones Are Stronger Than Steel",
    "The Muscle That Never Tires",
    "Why Your Jaw Is the Strongest Muscle",
    "Your Skeleton Regenerates Every 10 Years",
    "The Bone That's Actually Fused at Birth",
    "Why Your Muscles Get Sore After Exercise",
    "The Secret to Building Muscle Faster",
    "Why Your Bones Weaken With Age",
    "The Strongest Bone in Your Body",
    "Why You Can't Move When You Sleep",
    
    # Digestive / Organs (15+)
    "Your Stomach Can Digest Itself",
    "The Organ You Can Live Without",
    "Your Gut Has Its Own Nervous System",
    "Why Your Stomach Growls Even When You're Not Hungry",
    "The Organ That Regrows Itself Completely",
    "Why You Can't Breathe and Swallow at the Same Time",
    "Your Liver Can Regrow in 30 Days",
    "The Reason You Get Heartburn",
    "Your Gut Has More Neurons Than Your Spinal Cord",
    "The Organ That Decides Your Mood",
    "Why Your Digestion Slows at Night",
    "The Secret to a Healthy Gut",
    "Why Your Stomach Hurts When You're Nervous",
    "The Organ That Controls Your Appetite",
    "Why You Get Food Cravings",
    
    # Skin / Senses (15+)
    "Your Skin Replaces Itself Every Month",
    "Why Your Eyes Never Actually Stop Moving",
    "The Reason Your Ears Never Stop Growing",
    "Why You Can't See Your Own Blind Spot",
    "Your Fingerprints Started Forming Before You Were Born",
    "Your Skin Has Its Own Immune System",
    "Why Your Hair Changes Color With Age",
    "The Reason You Get Goosebumps When Cold",
    "Your Eyes Have a Blind Spot You Never Notice",
    "Why Your Sense of Smell Changes at Night",
    "The Secret of Your Skin's Microbiome",
    "Why Your Skin Changes With Stress",
    "The Reason You Get Dark Circles Under Your Eyes",
    "Why Your Fingers Prune in Water",
    "The Hidden Power of Your Sense of Touch",
    
    # Mystery / Dark Facts (20+)
    "The Sound Only Your Body Can Hear",
    "Why Fear Has a Physical Smell",
    "The Moment Your Body Knows You're Lying",
    "Why Your Body Remembers Trauma Before Your Mind Does",
    "The Reflex You Can't Control No Matter What",
    "Why Some People Feel Pain Differently Than Others",
    "The Signal Your Body Sends Before You Even Notice It's Sick",
    "Why Your Body Temperature Drops Right Before You Wake Up",
    "Your Body Has a Hidden Backup Organ",
    "The Reason You Get Chills When You're Scared",
    "Why Your Body Twitches When You Sleep",
    "The Secret Death Signal Your Body Sends",
    "Why Your Body Smells Different When You're Anxious",
    "The Hidden Language of Your Body Language",
    "Why Your Body Freezes When You're in Danger",
    "The Reason Your Heart Pounds in a Crowd",
    "Why Your Body Can Heal Itself Without You Knowing",
    "The Hidden Intelligence of Your Immune System",
    "Why Your Body Yearns for Nature",
    "The Secret Rhythms of Your Body Clock",
]

# ============================================
# 2. HOOK FORMULAS (25+ with CLIFFHANGER ENDINGS)
# ============================================
HOOK_FORMULAS = [
    "This happens to your body every night... and you have no idea.",
    "Doctors don't want you to know this about {topic}...",
    "Your body is lying to you about {topic}. Here's the truth.",
    "Nobody told you this is happening inside you right now.",
    "This is the part of {topic} your biology teacher skipped.",
    "You've done this a million times and never asked why.",
    "Something in your body is happening without your permission.",
    "This sounds fake, but {topic} is 100% real.",
    "Scientists only figured this out about {topic} recently.",
    "Your body has been hiding this from you your whole life.",
    "This is why {topic} feels so unsettling once you know it.",
    "Most people go their entire life never knowing this about {topic}.",
    "If this happened to you, your body did something incredible.",
    "There's a reason no one talks about {topic}.",
    "This is the creepiest thing your own body does.",
    "What if I told you {topic} is completely different than you think?",
    "The truth about {topic} that nobody wants to admit.",
    "This one fact about {topic} will change how you see yourself.",
    "You won't believe what {topic} actually means for your body.",
    "This is what happens inside when {topic} occurs.",
    "The hidden secret of {topic} that's been right in front of you.",
    "Why {topic} is the most misunderstood thing about your body.",
    "Every time {topic} happens, your body is trying to tell you something.",
    "The science behind {topic} is stranger than fiction.",
    "This is the real reason {topic} happens in your body.",
]

# ============================================
# 3. TRANSITION HOOKS (For Scene-to-Scene Retention)
# ============================================
TRANSITION_HOOKS = [
    "but that's only half the story...",
    "and you won't believe why...",
    "here's where it gets really strange...",
    "but wait... there's more...",
    "and this is the part nobody tells you...",
    "but here's the shocking part...",
    "and that's when things get dark...",
    "but your body has a secret...",
    "and this changes everything...",
    "but the real reason will surprise you...",
    "and it gets even weirder...",
    "but here's the twist...",
]

# ============================================
# 4. PAIN POINTS (15+)
# ============================================
PAIN_POINTS = [
    "Worried something is wrong with your body",
    "Can't sleep because your mind won't shut off",
    "Feel anxious about random body symptoms",
    "Notice something about their body and can't explain it",
    "Feel like their body is a mystery even to themselves",
    "Get scared by symptoms they don't understand",
    "Wonder if what's happening to them is normal",
    "Feel disconnected from how their own body works",
    "Google symptoms late at night and spiral",
    "Feel like no one explains this stuff clearly",
    "Worry about aging and what it means for their body",
    "Feel helpless when their body doesn't cooperate",
    "Want to understand why their body reacts differently than others",
    "Feel ashamed of body functions they can't control",
    "Question whether their body is working properly",
]

# ============================================
# 5. CTAS (15+)
# ============================================
CTAS = [
    "Follow for more dark body secrets",
    "Share this if it blew your mind",
    "Comment: Did this happen to you?",
    "Save this before you forget it",
    "Follow if your body just did this to you",
    "Tag someone who needs to see this",
    "Comment 'same' if this happens to you too",
    "Share this with someone who overthinks everything",
    "Follow for the next dark body fact",
    "Send this to the friend who's always cold/tired/anxious",
    "Drop a ❤️ if you learned something new",
    "Comment '🤯' if this shocked you",
    "Save this for when you need to impress someone with facts",
    "Share to make someone think twice about their body",
    "Follow to unlock more body mysteries",
]

# ============================================
# 6. CATEGORY TAGS (SEO)
# ============================================
CATEGORY_TAGS = {
    "Brain": [
        "neuroscience", "brainfacts", "psychologyfacts", "mindblown",
        "brainscience", "humanbrain", "nervoussystem", "mentalhacks",
        "brainhealth", "neuroplasticity", "cognition", "memory",
    ],
    "Body": [
        "humanbody", "bodyfacts", "anatomy", "bodyparts", "humanfacts",
        "bodyawareness", "bodymystery", "yourbody", "physiology",
        "humananatomy", "bodyscience", "healthfacts",
    ],
    "Mystery": [
        "mysteryscience", "weirdfacts", "creepyfacts", "unknownfacts",
        "darkscience", "bodysecrets", "themoreyouknow", "mindblowing",
        "scaryfacts", "unexplained", "paranormal",
    ],
    "Health": [
        "healthfacts", "bodyhacks", "sciencefacts", "healthscience",
        "medicalmystery", "humanhealth", "wellness", "healthtips",
        "wellnessjourney", "healthyliving",
    ],
}

# ============================================
# 7. BASE TAGS
# ============================================
BASE_TAGS = [
    "darkfacts", "facts", "shorts", "youtubeshorts", "science",
    "didyouknow", "mindblowing", "funfacts", "scaryfacts", "viral",
    "mystery", "unknown", "creepy", "interesting", "education",
]

# ============================================
# 8. CONSTANTS
# ============================================
TARGET_WORD_RANGE = (130, 170)
MAX_TAGS = 15
MAX_TITLE_LENGTH = 55
SCENES_PER_SCRIPT = 9  # Optimized for 3-5 second scenes

# ============================================
# 9. MEDICAL RED FLAGS
# ============================================
_MEDICAL_ADVICE_RED_FLAGS = [
    "cure", "diagnose", "you have", "stop taking", "don't need a doctor",
    "instead of medication", "guaranteed to heal", "definitely means you have",
    "you should", "you must", "never go to the doctor", "ignore your doctor",
    "this is the only cure", "better than medicine", "replace your medication",
]

# ============================================
# 10. RETENTION-OPTIMIZED PROMPT GENERATION
# ============================================

def get_script_prompt_for_niche(
    topic: str, 
    hook_preference: Optional[str] = None
) -> str:
    """
    Generates a RETENTION-OPTIMIZED prompt for script generation.
    Focuses on: Psychological Pacing, Visual Stimulation, and Cliffhangers.
    
    Args:
        topic: Topic string
        hook_preference: Specific hook to use (optional)
    
    Returns:
        Prompt string for AI
    """
    # Select hook
    if not hook_preference:
        hook_preference = random.choice(HOOK_FORMULAS)
        if "{topic}" in hook_preference:
            hook_preference = hook_preference.format(topic=topic)
    
    # Select pain point and CTA
    pain_point = random.choice(PAIN_POINTS)
    cta = random.choice(CTAS)
    
    # Word count and scene configuration
    min_w, max_w = TARGET_WORD_RANGE
    num_scenes = SCENES_PER_SCRIPT
    per_scene_lo = min_w // num_scenes
    per_scene_hi = max_w // num_scenes
    
    # Select random transitions for cliffhangers
    transitions = random.sample(TRANSITION_HOOKS, min(5, len(TRANSITION_HOOKS)))
    
    # Build RETENTION-OPTIMIZED prompt
    prompt = f"""
You are an expert mystery science communicator creating HIGH-RETENTION YouTube Shorts for USA adults 18+.

TOPIC: {topic}

🎯 RETENTION STRATEGY (CRITICAL):
- Every scene must end with a CLIFFHANGER that makes the viewer WANT to see the next scene
- Use "YOU" language throughout (e.g., "Your brain", "You feel") - make it PERSONAL
- Each scene MUST be 3-5 seconds of spoken content (short, punchy, intense)
- Build CURIOSITY > REVEAL > CLIFFHANGER pattern in every scene

SCRIPT STRUCTURE:
1. DARK HOOK: "{hook_preference}"
2. RELATE the information to the viewer's daily life
3. SCIENCE behind the phenomenon (simplified, intriguing)
4. REVELATION that shocks or surprises
5. CLIFFHANGER transition to next scene
6. CTA: "{cta}"
7. DISCLAIMER: Educational/entertainment only, not medical advice

TONE: Dark, mysterious, factual, engaging, personal
PAIN POINT: {pain_point}
SUGGESTED CLIFFHANGER TRANSITIONS (use similar style between scenes): {', '.join(transitions)}

📝 SCENE REQUIREMENTS:

WORD COUNT (HARD REQUIREMENT):
- Total voiceover MUST be {min_w}-{max_w} words
- Split into exactly {num_scenes} scenes
- Each scene caption: {per_scene_lo}-{per_scene_hi} words
- Each scene = 3-5 seconds of speech

CAPTION QUALITY FOR RETENTION:
- Start each scene with a MICRO-HOOK (e.g., "But here's the twist...")
- End each scene with a CLIFFHANGER (e.g., "...and that's when it gets weird")
- Use short, punchy sentences (5-10 words max per sentence)
- Build tension with every sentence
- NO filler words - every word must add value
- Connect each scene to the viewer's personal experience

🎨 VISUAL DESCRIPTION (CRITICAL FOR RETENTION):
- "visual": Describe an image that is VISUALLY STIMULATING
- Use words like: cinematic, high-contrast, macro-lens, motion blur, dark, moody
- Each visual should be UNIQUE and DYNAMIC (no static images)
- Consider: dramatic lighting, close-ups, abstract representations, metaphors

SCENE FORMAT:
For each scene, provide:
- "visual": 5-8 words describing a CINEMATIC image (e.g., "Macro shot of a beating heart, dark background")
- "caption": The EXACT spoken text (punchy, cliffhanger-driven, personal)

OUTPUT FORMAT:
Return ONLY valid JSON, no other text:

{{
  "title": "Short catchy title (under 55 chars)",
  "hook": "{hook_preference}",
  "scenes": [
    {{"visual": "...", "caption": "..."}},
    ...
  ],
  "cta": "{cta}",
  "description": "1-2 sentence video description"
}}

⚡ RETENTION CHECKLIST (BEFORE FINALIZING):
✓ Every scene ends with a cliffhanger
✓ "YOU" language used throughout
✓ Each scene is 3-5 seconds of speech
✓ Visual descriptions are CINEMATIC and UNIQUE
✓ Total word count: {min_w}-{max_w}
✓ Exactly {num_scenes} scenes
✓ No medical advice
✓ Dark, mysterious, scientific tone

REMEMBER: The viewer should feel COMPELLED to watch the next scene. Make it ADDICTIVE.
"""
    return prompt


def get_random_transition_hook() -> str:
    """Get a random transition hook for scene endings"""
    return random.choice(TRANSITION_HOOKS)


def get_transition_hooks(count: int = 3) -> List[str]:
    """Get multiple transition hooks"""
    return random.sample(TRANSITION_HOOKS, min(count, len(TRANSITION_HOOKS)))

# ============================================
# 11. CORE FUNCTIONS
# ============================================

def get_random_topic(exclude: Optional[List[str]] = None) -> str:
    """
    Picks a topic for the next video.
    
    Priority:
    1. Live trend-research topics (60% chance when available)
    2. Static DARK_TOPICS pool (fallback)
    3. Skips recently used topics from exclude list
    
    Args:
        exclude: List of topics to exclude (recently used)
    
    Returns:
        Selected topic string
    """
    exclude_set = {t.strip().lower() for t in (exclude or []) if t}
    logger.debug(f"Excluding {len(exclude_set)} recent topics")

    # Try to get trending topics
    trending = []
    try:
        from trend_research import fetch_trending_topics
        trending = fetch_trending_topics()
        logger.debug(f"Fetched {len(trending)} trending topics")
    except ImportError:
        logger.debug("Trend research module not available")
    except Exception as e:
        logger.warning(f"Trend research failed: {e}")

    # Filter trending topics
    trend_candidates = [
        t for t in trending 
        if t.strip().lower() not in exclude_set
    ]
    
    # 60% chance to use trending if available
    if trend_candidates and random.random() < 0.6:
        chosen = random.choice(trend_candidates)
        logger.info(f"Selected trending topic: {chosen}")
        return chosen

    # Fallback to static pool
    static_candidates = [
        t for t in DARK_TOPICS 
        if t.strip().lower() not in exclude_set
    ]
    
    if static_candidates:
        chosen = random.choice(static_candidates)
        logger.info(f"Selected static topic: {chosen}")
        return chosen
    
    # If everything is excluded, allow a repeat
    logger.warning("All topics recently used - allowing repeat from static pool")
    return random.choice(DARK_TOPICS)


def get_topic_category(topic: str) -> str:
    """
    Categorizes a topic into Brain, Body, Mystery, or Health.
    
    Args:
        topic: Topic string
    
    Returns:
        Category name
    """
    topic_lower = topic.lower()
    
    brain_keywords = ['brain', 'mind', 'sleep', 'nerve', 'psych', 'memory', 'thought', 'conscious']
    body_keywords = ['heart', 'blood', 'lung', 'kidney', 'bone', 'organ', 'muscle', 'vein', 'artery']
    mystery_keywords = ['scary', 'secret', 'dark', 'mystery', 'hidden', 'unknown', 'creepy', 'weird']
    
    if any(word in topic_lower for word in brain_keywords):
        return "Brain"
    elif any(word in topic_lower for word in mystery_keywords):
        return "Mystery"
    elif any(word in topic_lower for word in body_keywords):
        return "Body"
    else:
        return "Body"  # Default


def get_seo_tags(topic: str, category: str = "Body") -> List[str]:
    """
    Returns YouTube-optimized tags (max 15).
    
    Args:
        topic: Topic string
        category: Category name
    
    Returns:
        List of SEO tags
    """
    tags = BASE_TAGS.copy()
    tags.extend(CATEGORY_TAGS.get(category, []))
    
    # Add topic-specific keywords
    topic_words = [
        w for w in topic.lower().split() 
        if len(w) > 3 and w not in ['your', 'this', 'that', 'what', 'when']
    ]
    tags.extend(topic_words[:4])
    
    # Add related phrases
    related_phrases = [
        "human body", "science facts", "dark science",
        "body secrets", "mysterious facts", "human anatomy"
    ]
    tags.extend(related_phrases[:3])
    
    # Deduplicate and limit
    seen = set()
    result = []
    for tag in tags:
        clean = tag.strip().lower()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(tag)
        if len(result) >= MAX_TAGS:
            break
    
    return result


def generate_seo_tags(topic: str, category: str = "Body", title: str = "") -> List[str]:
    """
    Wrapper for get_seo_tags for compatibility.
    
    Args:
        topic: Topic string
        category: Category name
        title: Video title (optional)
    
    Returns:
        List of SEO tags
    """
    return get_seo_tags(topic, category)


def validate_script_for_medical_accuracy(script_data: Dict) -> Dict:
    """
    Validates that script doesn't contain medical advice.
    
    Args:
        script_data: Script dictionary
    
    Returns:
        Dict with 'valid' boolean and 'flags' list
    """
    # Extract voiceover text
    voiceover = script_data.get('voiceover', '')
    if not voiceover:
        voiceover = ' '.join([
            s.get('caption', '') 
            for s in script_data.get('scenes', []) 
            if isinstance(s, dict)
        ])
    
    # Check for red flags
    lowered = voiceover.lower()
    flags = [
        phrase for phrase in _MEDICAL_ADVICE_RED_FLAGS 
        if phrase in lowered
    ]
    
    return {
        "valid": len(flags) == 0,
        "flags": flags,
        "has_red_flags": len(flags) > 0
    }


def auto_add_disclaimer(script_data: Dict) -> Dict:
    """
    Adds medical disclaimer to script.
    
    Args:
        script_data: Script dictionary
    
    Returns:
        Modified script dictionary
    """
    disclaimer = "This video is for educational/entertainment purposes only and is not medical advice. Consult a doctor for any health concerns."
    
    # Add to CTA
    script_data['cta'] = (
        script_data.get('cta', '') + " " + disclaimer
    ).strip()
    
    # Add to description
    if 'description' in script_data:
        script_data['description'] = (
            script_data['description'] + " " + disclaimer
        ).strip()
    
    # Add flag
    script_data['disclaimer_added'] = True
    
    logger.info("Added medical disclaimer to script")
    return script_data


def _make_seo_title(title: str, topic: str) -> str:
    """
    Enhances title for SEO while keeping under 55 chars.
    
    Args:
        title: Original title
        topic: Topic string
    
    Returns:
        SEO-optimized title
    """
    # If title already has power words, keep it
    power_words = ["secret", "nobody", "never", "actually", "dark", "scary",
                   "real", "hidden", "warning", "shock", "fact", "truth"]
    if any(pw in title.lower() for pw in power_words):
        return title[:MAX_TITLE_LENGTH]
    
    # Add hook emoji
    enhanced = f"🫀 {title}"
    if len(enhanced) <= MAX_TITLE_LENGTH:
        return enhanced
    
    return title[:MAX_TITLE_LENGTH]


# ============================================
# 12. UTILITY FUNCTIONS
# ============================================

def get_random_hook(topic: Optional[str] = None) -> str:
    """
    Get a random hook formula, optionally with topic.
    
    Args:
        topic: Topic to insert into hook (optional)
    
    Returns:
        Hook string
    """
    hook = random.choice(HOOK_FORMULAS)
    if topic and "{topic}" in hook:
        hook = hook.format(topic=topic)
    return hook


def get_random_pain_point() -> str:
    """Get a random pain point."""
    return random.choice(PAIN_POINTS)


def get_random_cta() -> str:
    """Get a random CTA."""
    return random.choice(CTAS)


def get_category_tags(category: str) -> List[str]:
    """Get tags for a specific category."""
    return CATEGORY_TAGS.get(category, CATEGORY_TAGS["Body"])


def get_scene_count() -> int:
    """Get the optimal number of scenes for retention."""
    return SCENES_PER_SCRIPT

# ============================================
# 13. RETENTION ANALYSIS FUNCTIONS
# ============================================

def analyze_retention_potential(script_data: Dict) -> Dict:
    """
    Analyzes script for retention potential.
    
    Returns:
        Dict with retention scores and suggestions
    """
    scenes = script_data.get('scenes', [])
    score = 0
    suggestions = []
    
    # Check scene count
    if len(scenes) == SCENES_PER_SCRIPT:
        score += 20
    else:
        suggestions.append(f"Optimal scene count is {SCENES_PER_SCRIPT}, currently {len(scenes)}")
    
    # Check for cliffhangers
    cliffhanger_count = 0
    for scene in scenes:
        caption = scene.get('caption', '')
        if any(word in caption.lower() for word in ['...', 'but', 'however', 'yet', 'still']):
            cliffhanger_count += 1
    
    cliffhanger_ratio = cliffhanger_count / len(scenes) if scenes else 0
    if cliffhanger_ratio >= 0.7:
        score += 30
    else:
        suggestions.append(f"Only {cliffhanger_ratio:.0%} scenes have cliffhangers - aim for 70%+")
    
    # Check "YOU" language
    you_count = 0
    for scene in scenes:
        caption = scene.get('caption', '')
        you_count += caption.lower().count('you')
    
    if you_count >= len(scenes) * 2:
        score += 25
    else:
        suggestions.append("Use more 'YOU' language for personal connection")
    
    # Check visual quality
    visual_quality = 0
    for scene in scenes:
        visual = scene.get('visual', '')
        if any(word in visual.lower() for word in ['cinematic', 'macro', 'close', 'dark', 'dramatic']):
            visual_quality += 1
    
    if visual_quality >= len(scenes) * 0.6:
        score += 25
    else:
        suggestions.append("Make visuals more CINEMATIC and DYNAMIC")
    
    return {
        'retention_score': min(100, score),
        'suggestions': suggestions,
        'cliffhanger_ratio': cliffhanger_ratio,
        'you_count': you_count,
        'visual_quality': visual_quality / len(scenes) if scenes else 0
    }

# ============================================
# 14. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Test functionality
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("RETENTION-OPTIMIZED NICHE STRATEGY TEST")
    print("="*60)
    print()
    
    # Test topic selection
    print("1. Topic Selection:")
    for i in range(3):
        topic = get_random_topic()
        print(f"   - {topic}")
    print()
    
    # Test categorization
    test_topics = [
        "Your Brain Lies to You",
        "Your Heart Has Its Own Brain",
        "Why Fear Has a Physical Smell"
    ]
    print("2. Topic Categorization:")
    for topic in test_topics:
        category = get_topic_category(topic)
        print(f"   {topic} → {category}")
    print()
    
    # Test prompt generation
    print("3. Retention-Optimized Prompt Generation:")
    topic = "Why Your Brain Lies to You"
    prompt = get_script_prompt_for_niche(topic)
    print(f"   Generated prompt ({len(prompt)} chars)")
    print(f"   First 200 chars: {prompt[:200]}...")
    print()
    
    # Test transition hooks
    print("4. Transition Hooks:")
    transitions = get_transition_hooks(3)
    for hook in transitions:
        print(f"   - {hook}")
    print()
    
    # Test SEO tags
    print("5. SEO Tags:")
    tags = get_seo_tags("Brain Secrets", "Brain")
    print(f"   Tags: {', '.join(tags[:5])}...")
    print()
    
    # Test medical validation
    print("6. Medical Validation:")
    script = {
        "voiceover": "This can help diagnose your condition",
        "scenes": [{"caption": "Test caption"}]
    }
    result = validate_script_for_medical_accuracy(script)
    print(f"   Valid: {result['valid']}")
    print(f"   Flags: {result['flags']}")
    print()
    
    print("="*60)
    print("✅ RETENTION-OPTIMIZED MODULE READY!")
    print("="*60)
