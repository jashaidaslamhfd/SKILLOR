import os
import re
import json
import logging
from typing import Dict, List
# src/niche_strategy.py

PAIN_POINTS = {
    "Sleep": ["Baby not sleeping through the night", "Waking up every hour", "Parents feeling exhausted"],
    "Brain": ["Is my baby hitting milestones?", "Why does baby cry at night?", "Brain development signs"],
    "Body": ["Is my baby eating enough?", "Growth spurts explained", "Safe tummy time tips"]
}

def get_script_prompt_for_niche(topic):
    # Ab yahan PAIN_POINTS ka use safely ho jayega
    # ... baki code wahi rehne dein

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Brain & Body Science for Babies/Children Topics
BRAIN_SCIENCE_TOPICS = [
    "Why Babies Need to Crawl Before Walking",
    "The 3 Sleep Stages Every Baby Parent Must Know",
    "Brain Development Milestones: 0-6 Months",
    "Right Brain vs Left Brain: How Parents Can Help",
    "The Science Behind Baby Babbling",
    "Motor Skill Development Timeline",
    "How Touch Develops Baby's Brain",
    "Language Development: What Parents Miss",
    "Sensory Development in First Year",
    "Why Babies Cry: The Neuroscience",
    "Attachment Theory: Science Explained",
    "Brain Growth Nutrition for Babies",
    "The 4 Month Sleep Regression Explained",
    "How Play Develops Your Baby's Brain",
    "Emotional Intelligence in Toddlers",
    "Why Babies Love Repetition: Brain Science",
    "Object Permanence Development Explained",
    "Mirror Neurons and Baby Learning",
    "Bilingual Brain Development in Babies",
    "How Music Helps Baby Brain Development",
]

HOOK_FORMULAS = [
    "Most parents don't know this about {topic}...",
    "Science shows that babies who {action} develop {benefit}...",
    "Here's what pediatricians wish all parents knew about {topic}...",
    "This {topic} mistake is happening in 95% of households...",
    "Your baby's brain needs this {topic}... and here's why...",
    "One simple {topic} change can boost your baby's development by {percent}%...",
    "Brain scientists discovered something shocking about {topic}...",
    "If your baby {symptom}, this is what's really happening...",
    "The {topic} myth that's hurting your baby's development...",
    "Your baby's future depends on understanding {topic}...",
]

PAIN_POINTS = [
    "Worried about baby's development",
    "Don't know if baby is hitting milestones",
    "Confused about baby sleep",
    "Wondering if baby needs intervention",
    "Unsure about nutrition for brain",
    "Baby seems behind peers",
    "Worried about language delay",
    "Baby won't eat certain foods",
    "Sleep schedule is chaotic",
    "Baby seems less social than others",
]

# CTAs - deliberately parent-directed (adult audience), never addressed to the
# child watching. Important for YouTube "Made for Kids" self-classification:
# a video ABOUT children that speaks TO parents is treated differently than
# content that speaks/plays directly to children.
CTAS = [
    "Save this video - you'll need it for reference",
    "Share this with someone raising a baby",
    "Comment: Did your baby do this?",
    "Follow for more research-backed parenting tips",
    "Tag a parent who needs to see this",
    "Send this to your pediatrician",
    "Save and share with your partner",
    "Which milestone surprised you the most?",
    "Does your baby do this? Comment below",
    "This changed how I parent - share if it helps you too",
]

# Words that trigger a mandatory disclaimer / soften pass before publishing
MEDICAL_TRIGGERS = ['disorder', 'disease', 'autism', 'adhd', 'delay', 'disability', 'diagnos']
FEAR_WORDS = ['dangerous', 'toxic', 'poison', 'kill', 'harm', 'damage', 'permanently']

# Target pacing for Shorts/Reels retention: short scripts hold attention
# better and match the 40-55s target duration used across the pipeline.
TARGET_WORD_RANGE = (110, 150)   # ~2.5-2.8 wps -> ~40-55s spoken
TARGET_SCENE_COUNT = (6, 8)      # fast cuts every ~6-8s


def get_script_prompt_for_niche(topic: str, hook_preference: str = None) -> str:
    """
    Domain-specific script prompt for parenting/brain-science content.
    Scenes are now returned as {"visual": ..., "caption": ...} pairs so that
    the caption shown on-screen is the EXACT spoken line for that scene
    (not an image description) - required for accurate captions and for
    per-scene TTS generation used to keep voice/caption/clip in sync.
    """
    if not hook_preference:
        hook_preference = HOOK_FORMULAS[0]

    pain_point = PAIN_POINTS[hash(topic) % len(PAIN_POINTS)]
    cta = CTAS[hash(topic) % len(CTAS)]
    min_w, max_w = TARGET_WORD_RANGE
    min_s, max_s = TARGET_SCENE_COUNT

    prompt = f"""
    You are an expert parenting educator specializing in baby brain and body science,
    writing for a YouTube Shorts / Facebook Reels audience of PARENTS (not children).

    Topic: {topic}
    Target Audience: USA parents (concerned about child development) - the video
    speaks TO the parent watching, never to a child.
    Target spoken length: {min_w}-{max_w} words total (~40-55 seconds at natural pace).

    SCRIPT REQUIREMENTS:
    1. Start with this hook: "{hook_preference}"
    2. Address this parent pain point: {pain_point}
    3. Give a scientific explanation (cite brain science/pediatric research in plain terms)
    4. Offer 1-2 actionable tips parents can implement TODAY
    5. End with this CTA, addressed to the parent: "{cta}"

    SAFETY / MONETIZATION GUIDELINES (must follow):
    - Do not use fear-mongering language (e.g. "dangerous", "toxic", "your baby will suffer").
    - If mentioning any developmental disorder, delay, or diagnosis, include a brief
      disclaimer to consult a pediatrician - do not present it as a diagnosis.
    - No clickbait medical claims presented as fact; use "research suggests" framing.
    - Keep tone reassuring and empowering, not guilt-inducing.
    - Content must be clearly FOR the parent audience, not designed to be watched
      or interacted with by children themselves.

    SCENE / CAPTION REQUIREMENTS:
    - Produce {min_s}-{max_s} scenes.
    - Each scene must have:
        "visual": a 5-8 word description of the image to generate for that scene
        "caption": the EXACT segment of the voiceover spoken during that scene
          (captions across all scenes, concatenated in order, must reconstruct
          the full voiceover word-for-word)

    FORMAT (JSON ONLY, no markdown, no preamble):
    {{
        "title": "Engaging 5-6 word title",
        "hook": "First 3 seconds - attention grabber",
        "scenes": [
            {{"visual": "...", "caption": "..."}},
            {{"visual": "...", "caption": "..."}}
        ],
        "cta": "{cta}",
        "key_message": "One-line takeaway",
        "sources": ["Research or source reference"]
    }}
    """
    return prompt


def get_random_topic() -> str:
    return BRAIN_SCIENCE_TOPICS[hash(os.urandom(8)) % len(BRAIN_SCIENCE_TOPICS)]


def get_topic_category(topic: str) -> str:
    categories = {
        "Sleep": ["sleep", "regression", "tired"],
        "Development": ["milestone", "development", "motor", "crawl", "walk"],
        "Brain": ["brain", "cognitive", "learning"],
        "Communication": ["language", "babbling", "talk", "speech"],
        "Nutrition": ["nutrition", "eat", "food", "brain growth"],
        "Emotion": ["emotional", "attachment", "cry"],
        "Sensory": ["sensory", "touch", "sound"],
        "Play": ["play", "learn", "activity"],
    }
    topic_lower = topic.lower()
    for category, keywords in categories.items():
        if any(kw in topic_lower for kw in keywords):
            return category
    return "General"


def validate_script_for_medical_accuracy(script_data: Dict) -> Dict:
    """
    Validate script for medical accuracy, fear-mongering, and COPPA-adjacent
    concerns. This is now actually CALLED from main.py's pipeline (previously
    it was defined but never invoked).
    """
    issues = []
    warnings = []

    full_text = script_data.get('voiceover', '')
    if not full_text and script_data.get('scenes'):
        full_text = ' '.join(
            s.get('caption', '') if isinstance(s, dict) else str(s)
            for s in script_data['scenes']
        )
    script_text = (full_text + ' ' + script_data.get('title', '')).lower()

    if any(trigger in script_text for trigger in MEDICAL_TRIGGERS):
        if 'consult' not in script_text and 'doctor' not in script_text and 'pediatrician' not in script_text:
            issues.append("Medical/diagnostic term used without a doctor-consultation disclaimer")

    if any(word in script_text for word in FEAR_WORDS):
        warnings.append("Fear-inducing language detected - may hurt watch-time and violate tone guidelines")

    word_count = len(full_text.split())
    if word_count < TARGET_WORD_RANGE[0]:
        warnings.append(f"Script shorter than target ({word_count} words) - risks video under 40s")
    elif word_count > TARGET_WORD_RANGE[1] + 20:
        warnings.append(f"Script longer than target ({word_count} words) - risks video over 55s")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "recommendation": "Approved" if len(issues) == 0 else "Needs revision - add disclaimer"
    }


def auto_add_disclaimer(script_data: Dict) -> Dict:
    """
    If a medical trigger word is present without a disclaimer, append a short
    disclaimer as a final scene rather than rejecting the whole script outright.
    """
    disclaimer_caption = "This is general information, not medical advice - always check with your pediatrician."
    scenes = script_data.get('scenes', [])
    scenes.append({
        "visual": "a warm illustration of a parent and pediatrician talking",
        "caption": disclaimer_caption
    })
    script_data['scenes'] = scenes
    script_data['voiceover'] = script_data.get('voiceover', '') + ' ' + disclaimer_caption
    return script_data
