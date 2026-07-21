#!/usr/bin/env python3
"""
THUMBNAIL PROMPTS — Copy-paste into Midjourney/DALL-E/Flux
Run: python scripts/thumbnail_prompts.py --topic "your topic"
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

THUMBNAIL_TEMPLATES = [
    {
        "name": "Shocked Face + Arrow",
        "prompt": "Vertical 9:16 thumbnail, close-up shocked human face {gender}, eyes wide open, mouth slightly open, pointing arrow toward {visual_element}, bold yellow text '{text}' top right, high contrast, cinematic lighting, 8k, photorealistic --ar 9:16",
        "text_max_words": 3,
    },
    {
        "name": "Curious Face + Question",
        "prompt": "Vertical 9:16 thumbnail, curious thoughtful face {gender}, hand on chin, thinking expression, floating {visual_element} hologram beside head, bold white text '{text}' with black outline, clean background, professional YouTube thumbnail style --ar 9:16",
        "text_max_words": 3,
    },
    {
        "name": "Relieved/Smiling Face",
        "prompt": "Vertical 9:16 thumbnail, relieved happy face {gender}, relaxed shoulders, subtle smile, {visual_element} glowing green checkmark overlay, bold green text '{text}', warm lighting, trustworthy vibe --ar 9:16",
        "text_max_words": 3,
    },
    {
        "name": "Before/After Split",
        "prompt": "Vertical 9:16 thumbnail, split screen down middle: LEFT side {visual_element} red/crossed out/struggling, RIGHT side {visual_element} green/checkmark/healthy, bold white text '{text}' center dividing line, high contrast, clear comparison --ar 9:16",
        "text_max_words": 3,
    },
    {
        "name": "Macro Detail + Bold Text",
        "prompt": "Vertical 9:16 thumbnail, extreme macro close-up of {visual_element}, ultra-detailed, scientific visualization style, bold large yellow text '{text}' overlay with black stroke, dark cinematic background, 8k resolution --ar 9:16",
        "text_max_words": 3,
    },
    {
        "name": "Expert Badge + Fact",
        "prompt": "Vertical 9:16 thumbnail, clean minimal design: {visual_element} centered, 'NEUROSCIENTIST REVEALS' or 'DOCTOR EXPLAINS' small text top, bold large text '{text}' bottom, professional medical/science aesthetic, blue/white color scheme --ar 9:16",
        "text_max_words": 4,
    },
]

VISUAL_ELEMENTS = {
    'brain': 'glowing human brain with neural connections',
    'sleep': 'person sleeping peacefully with brain waves visualization',
    'memory': 'neurons firing, memory formation visualization',
    'heart': 'beating human heart with blood flow animation',
    'blood': 'red blood cells flowing through vessels',
    'eye': 'human eye macro shot, iris detail, eyelid twitch',
    'twitch': 'eyelid close-up with muscle fiber animation',
    'gut': 'intestine with glowing microbiome bacteria',
    'stomach': 'stomach anatomy with acid visualization',
    'muscle': 'muscle fibers contracting, myofibrils detail',
    'bone': 'bone cross-section with osteoblasts working',
    'hormone': 'molecular structure of dopamine/serotonin/cortisol',
    'immune': 'white blood cell attacking pathogen',
    'dream': 'brain with dream cloud visualization',
    'skin': 'skin cross-section with collagen fibers',
    'breath': 'lungs expanding, oxygen molecules entering blood',
}

TEXT_OPTIONS = {
    'brain': ['BRAIN REWIRED', 'MEMORY HACK', 'NEURAL TRUTH', 'MIND BLOWN'],
    'sleep': ['SLEEP SECRET', '90 MIN RULE', 'DREAM TRUTH', 'WAKE UP BETTER'],
    'memory': ['MEMORY FIX', 'RECALL BOOST', 'FORGET LESS', 'BRAIN UPGRADE'],
    'heart': ['HEART TRUTH', 'PULSE SECRET', 'CARDIO MYTH', 'BEAT BETTER'],
    'eye': ['EYE TWITCH FIX', 'VISION TRUTH', 'BLINK SECRET', 'SEE CLEARLY'],
    'gut': ['GUT BRAIN', 'DIGEST TRUTH', 'BIOME HACK', 'BELLY FIX'],
    'muscle': ['MUSCLE MYTH', 'STRENGTH SECRET', 'GROWTH TRUTH', 'RECOVERY HACK'],
    'hormone': ['HORMONE HACK', 'MOOD FIX', 'ENERGY SECRET', 'BALANCE RESTORED'],
    'immune': ['IMMUNE BOOST', 'SICKNESS PROOF', 'DEFENSE MODE', 'HEAL FASTER'],
    'dream': ['DREAM CONTROL', 'LUCID SECRET', 'SLEEP HACK', 'NIGHT POWER'],
    'default': ['BODY HACK', 'SCIENCE TRUTH', 'DOCTORS HIDE THIS', 'YOU NEED THIS'],
}

def get_visual_element(topic: str) -> str:
    topic_lower = topic.lower()
    for key, value in VISUAL_ELEMENTS.items():
        if key in topic_lower:
            return value
    return VISUAL_ELEMENTS['brain']

def get_text_options(topic: str) -> list:
    topic_lower = topic.lower()
    for key, value in TEXT_OPTIONS.items():
        if key in topic_lower:
            return value
    return TEXT_OPTIONS['default']

def main():
    parser = argparse.ArgumentParser(description="Generate thumbnail prompts for Midjourney/DALL-E")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--gender", choices=['male', 'female', 'person'], default='person', help="Face gender")
    parser.add_argument("--output", default="output/thumbnail_prompts.txt", help="Output file")
    args = parser.parse_args()
    
    visual = get_visual_element(args.topic)
    texts = get_text_options(args.topic)
    
    print(f"\n🎨 THUMBNAIL PROMPTS FOR: {args.topic}")
    print(f"   Visual Element: {visual}")
    print(f"   Text Options: {', '.join(texts)}")
    print("=" * 60)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, 'w') as f:
        f.write(f"THUMBNAIL PROMPTS FOR: {args.topic}\n")
        f.write(f"Visual: {visual}\n")
        f.write(f"Text Options: {', '.join(texts)}\n")
        f.write("=" * 60 + "\n\n")
        
        for template in THUMBNAIL_TEMPLATES:
            text = texts[0]
            prompt = template['prompt'].format(
                gender=args.gender,
                visual_element=visual,
                text=text
            )
            
            print(f"\n📸 {template['name']}:")
            print(f"   {prompt[:100]}...")
            
            f.write(f"### {template['name']}\n")
            f.write(f"{prompt}\n\n")
    
    print(f"\n✅ Saved {len(THUMBNAIL_TEMPLATES)} prompts to {args.output}")
    print("\n💡 COPY any prompt → paste in Midjourney/DALL-E/Flux → download → use as thumbnail")

if __name__ == "__main__":
    main()