"""AI Prompts for Groq — BABY & CHILDREN SCIENCE (USA 2026)
   NICHE: Baby Brain Development, Child Psychology, Parenting Science
   TARGET: Parents, expecting parents, USA primary
   GOAL: 70% swap rate → 20% (emotional + educational)
"""

from typing import List, Dict, Optional
import random

# ═══════════════════════════════════════════════════════════
# BABY & CHILDREN TOPICS (50+ Viral Topics)
# ═══════════════════════════════════════════════════════════
BABY_TOPICS = [
    # ── BABY BRAIN DEVELOPMENT ──
    "How a baby's brain doubles in size in the first year",
    "Why babies cry at night — the neuroscience behind it",
    "Baby's first words: brain development milestone explained",
    "The science of baby sleep patterns and brain growth",
    "How breastfeeding builds your baby's brain",
    "Baby reflexes that disappear after 6 months — science explained",
    "Why babies smile in their sleep — brain development",
    "The neuroscience of baby-parent bonding and attachment",
    "How music affects a baby's developing brain",
    "Baby vision development — week by week guide",
    "Why babies love faces — brain development science",
    "The first 1000 days: critical window for brain development",
    "How talking to your baby builds their brain cells",
    "Baby brain development: what happens in the first 12 months",
    "Why tummy time is crucial for baby brain growth",
    "How baby brains process language before they can speak",
    "The science behind baby memory development",
    "How emotions develop in a baby's brain",
    "Why babies stare at lights — visual brain development",
    "Baby brain growth: what parents need to know",

    # ── CHILD PSYCHOLOGY ──
    "Why toddlers say 'no' to everything — psychology explained",
    "The science of tantrums: what's happening in a child's brain",
    "How play shapes a child's developing brain",
    "Why kids ask 'why' constantly — curiosity brain development",
    "The psychology of sibling rivalry and brain development",
    "How screen time affects a child's developing brain",
    "Why kids lie — the neuroscience behind childhood dishonesty",
    "The science of children's fears and brain development",
    "How sleep affects a child's brain growth",
    "Why kids have imaginary friends — psychology explained",
    "The psychology of children's eating habits",
    "How praise affects a child's developing brain",
    "The science of childhood learning and memory",
    "Why kids are more creative than adults — brain science",
    "How emotions develop in children — brain growth explained",
    "The psychology of childhood friendships",
    "Why kids get separation anxiety — brain development",
    "How bilingualism shapes a child's brain",
    "The science of childhood curiosity and brain wiring",
    "How reading to your child builds their brain",

    # ── PARENTING SCIENCE ──
    "The science of gentle parenting and brain development",
    "How your voice shapes your baby's brain",
    "The neuroscience of parent-child attachment",
    "Why skin-to-skin contact builds baby's brain",
    "How routine affects a child's developing brain",
    "The science of co-sleeping and baby brain development",
    "How stress during pregnancy affects baby's brain",
    "The science of baby-wearing and brain development",
    "How nutrition builds a baby's brain",
    "The psychology of positive parenting and brain growth",
    "How your emotional state affects your baby's brain",
    "The science of baby massage and brain development",
    "How outdoor play builds children's brains",
    "The neuroscience of family routines and brain development",
    "How pets affect a child's developing brain",
]

# ═══════════════════════════════════════════════════════════
# BABY HOOKS — Emotional + Curiosity (Swipe Stopper)
# ═══════════════════════════════════════════════════════════
BABY_HOOKS = [
    "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
    "Nobody tells you what your baby's brain is doing while they sleep...",
    "The first 1000 days decide your child's future brain power...",
    "Your newborn's brain has already started THIS incredible process...",
    "What your baby's brain is secretly doing during tummy time...",
    "The one thing that builds your baby's brain faster than anything else...",
    "Your baby's brain has more connections than stars in the galaxy...",
    "This simple activity TRIPLES your baby's brain growth...",
    "Your baby's brain is ALREADY processing language before they speak...",
    "The surprising reason your baby cries — it's brain development...",
    "Your child's brain is doing THIS every single night...",
    "The science behind your baby's first smile — it's brain growth...",
    "Your toddler's brain is wired for THIS — and it's amazing...",
    "Your baby's brain is built through play — here's how...",
    "The first year of brain development changes EVERYTHING...",
]

# ═══════════════════════════════════════════════════════════
# BABY CTAs — Engagement Driven (Like + Comment Forced)
# ═══════════════════════════════════════════════════════════
BABY_CTAS = [
    "👇 Comment 'BABY' if your little one does this too!",
    "❤️ Double tap if you love your baby's brain!",
    "📌 Save this — every parent needs to know this!",
    "🗣️ Tag a new parent who needs to see this!",
    "🔔 Follow for more baby brain science!",
    "💬 What does your baby do that amazes you? Comment below!",
    "👇 Does your baby do this? Comment YES or NO!",
    "❤️ Like if this made you appreciate your baby's brain more!",
    "🗣️ Share this with every new mom you know!",
    "🔔 Subscribe for more child brain development tips!",
    "📌 Save this for when your baby hits this milestone!",
    "👇 Comment 'MEMORY' if you want more baby science!",
]

# ═══════════════════════════════════════════════════════════
# BABY SCRIPT TEMPLATE
# ═══════════════════════════════════════════════════════════
BABY_SCRIPT_TEMPLATE = """
[Hook] {hook}

[Fact 1] Your baby's brain is creating {connections} new connections every second.

[Fact 2] By age {age}, their brain has grown to {size}% of adult size.

[Fact 3] Here's what you can do to support {activity} and build their brain.

[Emotional] Your baby is learning from you every single moment.

[CTA] {cta}
"""

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════
def get_baby_topic() -> str:
    """Get a random baby science topic"""
    return random.choice(BABY_TOPICS)

def get_baby_hook(topic: str = "") -> str:
    """Get a baby hook (with optional topic integration)"""
    hook = random.choice(BABY_HOOKS)
    if topic:
        # Integrate topic into hook
        words = topic.split()[:3]
        if words:
            hook = hook.replace("your baby", "your baby's " + " ".join(words))
    return hook

def get_baby_cta() -> str:
    """Get a baby CTA"""
    return random.choice(BABY_CTAS)

def generate_baby_script(topic: str) -> Dict:
    """Generate a complete baby science script"""
    hook = get_baby_hook(topic)
    cta = get_baby_cta()
    
    # Dynamic facts based on topic
    facts = {
        "connections": random.choice(["millions", "100,000", "1 million"]),
        "age": random.choice(["1", "2", "3", "6", "12"]),
        "size": random.choice(["80", "85", "90", "95"]),
        "activity": random.choice(["tummy time", "talking", "reading", "playing", "singing"]),
    }
    
    script = BABY_SCRIPT_TEMPLATE.format(
        hook=hook,
        connections=facts["connections"],
        age=facts["age"],
        size=facts["size"],
        activity=facts["activity"],
        cta=cta
    )
    
    return {
        "script": script,
        "hook": hook,
        "cta": cta,
        "facts": facts,
        "topic": topic,
           }
