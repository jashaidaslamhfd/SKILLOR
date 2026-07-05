import os
import re
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NEW NICHE: DARK BODY & BRAIN MYSTERY FOR USA ADULTS 18+
# COPPA Risk = 0% | High Retention | High CPM
# ---------------------------------------------------------------------------

# Dark Body & Brain Science Topics for USA
BRAIN_SCIENCE_TOPICS = [
    "How Many Veins Are In The Human Body And The Danger",
    "Why Your Brain Shuts Down For 2 Seconds When You Enter A Room",
    "Your Bones Are Making 2 Million Blood Cells Right Now",
    "Why You Stop Breathing 20 Times Every Night",
    "The Parasite That Controls 50% Of People In USA",
    "Your Heart Can Beat Outside Your Body For 3 Minutes",
    "Why You Get Goosebumps From Music - Brain Science",
    "The Hidden Organ Doctors Missed For 200 Years",
    "You Shed Skin Every 3 Seconds And Don't Notice",
    "Your Stomach Has A Second Brain Controlling Your Mood",
    "Why You Wake Up At 3AM - Brain Science Explained",
    "Your DNA Is Long Enough To Reach The Moon",
    "The 30 Second Brain Glitch Everyone Has",
    "Why You Blink When You Sneeze - The Real Reason",
    "Your Body Is Eating Itself Right Now And It's Normal",
]

# DARK MYSTERY HOOK FORMULAS - High Retention
HOOK_FORMULAS = [
    "There's something hiding inside you right now. Does this happen to you too?",
    "Scientists discovered this about your body... and it's terrifying.",
    "Your body is doing this without telling you. Has this happened to you?",
    "There's a {topic} inside you right now. And you don't even know it.",
    "This happens to your body every night... and you have no idea.",
    "Doctors don't want you to know this about {topic}...",
    "Your body is lying to you about {topic}. Here's the truth.",
    "If you {symptom}, your body is warning you about this...",
    "The {topic} fact that will keep you up at night...",
    "Your body is hiding a secret about {topic}. And it's scary.",
]

# ADULT PAIN POINTS - USA 18-45
PAIN_POINTS = [
    "Worried something is wrong with your body",
    "Can't sleep because your mind won't shut off",
    "Feel anxious about random body symptoms",
    "Scared you're not normal",
    "Wondering why your body does weird things",
    "Tired of not understanding your own body",
    "Think you might have ADHD or anxiety",
    "Stress is affecting your health",
    "Feel like your body is betraying you",
    "Want to know what doctors aren't telling you",
]

# CTAs - Adult focused
CTAS = [
    "Follow for more dark body secrets",
    "Share this if it blew your mind",
    "Comment: Did this happen to you?",
    "Save this before you forget",
    "Tag someone who needs to know this",
    "Which fact shocked you the most?",
    "Follow for part 2",
    "Does your body do this too? Comment",
    "This changed how I see my body",
    "Send this to someone who worries a lot",
]

# Words that trigger disclaimer
MEDICAL_TRIGGERS = ['disorder', 'disease', 'adhd', 'anxiety', 'depression', 'diagnos', 'symptom', 'condition']
FEAR_WORDS = ['dangerous', 'toxic', 'kill', 'die', 'harm', 'damage', 'burst', 'bleed']

# Target pacing for Shorts/Reels
TARGET_WORD_RANGE = (110, 150)   # ~40-55s
TARGET_SCENE_COUNT = (6, 8)

# ---------------------------------------------------------------------------
# SEO TAGS FOR USA DARK SCIENCE NICHE
# ---------------------------------------------------------------------------
CATEGORY_TAGS = {
    "Brain": ["neuroscience", "brainfacts", "psychologyfacts", "mindscience"],
    "Body": ["humanbody", "bodyfacts", "anatomy", "medicalfacts"],
    "Mystery": ["darkfacts", "mysteryscience", "weirdfacts", "scaryfacts"],
    "Health": ["healthfacts", "bodyhacks", "sciencefacts", "didyouknow"],
    "General": ["factsofinstagram", "darkpsychology", "mindblown"],
}
BASE_TAGS = ["facts", "shorts", "science", "darkfacts"]

def get_script_prompt_for_niche(topic: str, hook_preference: str = None) -> str:
    """
    Domain-specific script prompt for DARK BODY MYSTERY content.
    Format: Dark Hook > Relate > Science > Relief > CTA
    """
    if not hook_preference:
        hook_preference = HOOK_FORMULAS[hash(topic) % len(HOOK_FORMULAS)]

    pain_point = PAIN_POINTS[hash(topic) % len(PAIN_POINTS)]
    cta = CTAS[hash(topic) % len(CTAS)]
    min_w, max_w = TARGET_WORD_RANGE
    min_s, max_s = TARGET_SCENE_COUNT

    prompt = f"""
    You are an expert mystery science communicator creating DARK MYSTERY YouTube Shorts for USA adults 18+.

    Topic: {topic}
    Target Audience: USA adults who love science and mystery
    Target spoken length: {min_w}-{max_w} words total (~40-55 seconds)

    SCRIPT REQUIREMENTS - DARK MYSTERY FORMAT:
    1. DARK HOOK: Start scary. "{hook_preference}"
    2. RELATE: "Does this happen to you too?" Connect to viewer
    3. SCIENCE: Explain the science in simple,
