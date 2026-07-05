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
    "Brain": ["neuroscience", "brainfacts", "psychologyfacts"],
    "Body": ["humanbody", "bodyfacts", "anatomy"],
    "Mystery": ["darkfacts", "mysteryscience", "weirdfacts"],
    "Health": ["healthfacts", "bodyhacks", "sciencefacts"],
}
BASE_TAGS = ["facts", "shorts", "science", "darkfacts"]
TARGET_WORD_RANGE = (110, 150)

def get_random_topic() -> str:
    return random.choice(DARK_TOPICS)

def get_topic_category(topic: str) -> str:
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ['brain', 'mind', 'sleep']):
        return "Brain"
    elif any(word in topic_lower for word in ['heart', 'blood', 'lung', 'kidney', 'bone']):
        return "Body"
    elif any(word in topic_lower for word in ['scary', 'secret', 'kill']):
        return "Mystery"
    else:
        return "Body"

def get_script_prompt_for_niche(topic: str, hook_preference: str = None) -> str:
    if not hook_preference:
        hook_preference = HOOK_FORMULAS[hash(topic) % len(HOOK_FORMULAS)]
    pain_point = PAIN_POINTS[hash(topic) % len(PAIN_POINTS)]
    cta = CTAS[hash(topic) % len(CTAS)]
    min_w, max_w = TARGET_WORD_RANGE
    prompt = f"""
You are an expert mystery science communicator creating DARK MYSTERY YouTube Shorts for USA adults 18+.
Topic: {topic}
Target spoken length: {min_w}-{max_w} words total (~40-55 seconds)
SCRIPT REQUIREMENTS: 1. DARK HOOK: "{hook_preference}" 2. RELATE 3. SCIENCE 4. RELIEF 5. CTA: "{cta}"
TONE: Dark, mysterious, factual. PAIN POINT: {pain_point}
Return ONLY valid JSON with keys: hook, scenes[], cta, description
"""
    return prompt

def get_seo_tags(topic: str, category: str = "Body") -> list:
    tags = BASE_TAGS.copy()
    tags.extend(CATEGORY_TAGS.get(category, []))
    tags.extend(topic.lower().split()[:3])
    return list(dict.fromkeys(tags))
