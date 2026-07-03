import os
import json
import logging
from typing import Dict, List

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

# Hook formulas specific to parenting content
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

# Problem-Solution framework for parents
PAINT_POINTS = [
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

# CTAs optimized for parent engagement
CTAS = [
    "Save this video - you'll need it for reference",
    "Share this with someone raising a baby",
    "Comment: Did your baby do this?",
    "Subscribe for science-backed parenting tips",
    "Tag a parent who needs to see this",
    "Send this to your pediatrician",
    "Save and share with your partner",
    "Which milestone surprise you the most?",
    "Does your baby do this? Comment below",
    "This changed how I parent - share if it helps you too",
]

def get_script_prompt_for_niche(topic: str, hook_preference: str = None) -> str:
    """
    Generate domain-specific script prompt for parenting/brain science content.
    
    Args:
        topic: The specific topic about baby/child development
        hook_preference: Optional specific hook formula
    
    Returns:
        Specialized prompt for script generation
    """
    
    if not hook_preference:
        hook_preference = HOOK_FORMULAS[0]  # Default: "Most parents don't know..."
    
    # Select a pain point
    pain_point = PAIN_POINTS[hash(topic) % len(PAIN_POINTS)]
    
    # Select a CTA
    cta = CTAS[hash(topic) % len(CTAS)]
    
    prompt = f"""
    You are an expert parenting educator specializing in baby brain and body science.
    
    Topic: {topic}
    Target Audience: USA Parents (concerned about child development)
    Duration: 50-60 seconds
    
    SCRIPT REQUIREMENTS:
    1. Start with this hook: \"{hook_preference}\"
    2. Address this parent pain: {pain_point}
    3. Provide scientific explanation (cite brain science/pediatric research)
    4. Offer 1-2 actionable tips parents can implement TODAY
    5. End with this CTA: \"{cta}\"
    
    GUIDELINES:
    - Use simple, engaging language (but not condescending)
    - Include 1-2 specific percentages or timelines (from research)
    - Make parents feel empowered, not guilty
    - Create urgency without fear-mongering
    - Include specific age ranges where applicable
    - Keep educational tone but conversational style
    - Make it shareable between parents
    
    FORMAT (JSON ONLY):
    {{
        "title": "Engaging 5-6 word title",
        "hook": "First 3 seconds - attention grabber",
        "voiceover": "Full 50-60 second script",
        "scenes": ["Scene 1 description (5-7 words)", "Scene 2", ...]
        "key_message": "One-line takeaway",
        "sources": ["Research or source reference"],
        "target_engagement": "Why parents will share this"
    }}
    
    Make it VIRAL for parents concerned about their child's development.
    """
    
    return prompt


def get_random_topic() -> str:
    """Get a random topic from the brain science database."""
    return BRAIN_SCIENCE_TOPICS[hash(os.urandom(8)) % len(BRAIN_SCIENCE_TOPICS)]


def get_topic_category(topic: str) -> str:
    """Categorize the topic for better organization."""
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
    Validate script for medical accuracy and appropriateness.
    
    Returns:
        Dict with validation results and suggestions
    """
    issues = []
    warnings = []
    
    # Check for required medical disclaimers
    script_text = (script_data.get('voiceover', '') + ' ' + 
                   script_data.get('title', '')).lower()
    
    medical_triggers = ['disorder', 'disease', 'autism', 'adhd', 'delay', 'disability']
    if any(trigger in script_text for trigger in medical_triggers):
        if 'consult' not in script_text and 'doctor' not in script_text:
            issues.append("⚠️ Medical claim without doctor consultation disclaimer")
    
    # Check for fear-mongering
    fear_words = ['dangerous', 'toxic', 'poison', 'kill', 'harm', 'damage']
    if any(word in script_text for word in fear_words):
        warnings.append("⚠️ Strong language detected - may trigger parent anxiety")
    
    # Check for specificity
    if len(script_data.get('voiceover', '').split()) < 100:
        warnings.append("⚠️ Script might be too short for full explanation")
    
    # Check for sources mentioned
    if 'research' not in script_text and 'study' not in script_text:
        warnings.append("⚠️ Consider adding research sources for credibility")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "recommendation": "Approved" if len(issues) == 0 else "Needs revision"
    }


if __name__ == "__main__":
    # Test
    topic = get_random_topic()
    logger.info(f"Random topic: {topic}")
    logger.info(f"Category: {get_topic_category(topic)}")
    
    prompt = get_script_prompt_for_niche(topic)
    logger.info(f"\nGenerated prompt:\n{prompt[:200]}...")
