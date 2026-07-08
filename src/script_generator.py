import os
import json
import time
import logging
from groq import Groq, BadRequestError

# 2026 Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2026 Standards: High retention needs more scenes to maintain engagement
MIN_SCENES = 8
MAX_SCENES = 12
MIN_WORDS = 130
MAX_WORDS = 170

def _get_system_prompt() -> str:
    return """You are a top-tier Social Media Strategist for 2026. 
    Your expertise is creating viral scripts for YouTube Shorts/Facebook Reels.
    Focus on:
    1. Pattern Interrupt Hooks: Start with something shocking or counter-intuitive.
    2. High Pacing: Short, punchy sentences.
    3. Loopable Outros: The end should naturally lead back to the start.
    4. Retention: Remove all fluff; every word must add value.
    5. Output: STRICT JSON format only."""

def _default_prompt(topic: str) -> str:
    return f"""
    Create a 45-second viral script for the topic: "{topic}".
    The script must be high-energy and engaging for a USA audience.
    
    Format Requirements:
    - Return ONLY a JSON object.
    - 'title': Catchy, click-worthy title.
    - 'hook': The first 3 seconds (The most important part).
    - 'scenes': A list of {MIN_SCENES}-{MAX_SCENES} objects, each with 'visual' (detailed description for AI image generation) and 'caption' (spoken text).
    - 'cta': A non-intrusive, natural call-to-action that fits the end.
    
    The total word count must be between {MIN_WORDS} and {MAX_WORDS} words.
    """

def _normalize_scenes(script_data: dict) -> dict:
    normalized = []
    for s in script_data.get('scenes', []):
        visual = s.get('visual') or s.get('description') or ''
        caption = s.get('caption') or s.get('text') or ''
        if visual and caption:
            normalized.append({"visual": visual.strip(), "caption": caption.strip()})
    
    script_data['scenes'] = normalized
    script_data['voiceover'] = ' '.join(s['caption'] for s in normalized)
    return script_data

def generate_script(topic: str, custom_prompt: str = None, max_retries: int = 3) -> dict:
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is missing.")

    prompt = custom_prompt or _default_prompt(topic)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Generating optimized script (Attempt {attempt}/{max_retries})")
            
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": _get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2500
            )
            
            script_data = json.loads(completion.choices[0].message.content)
            script_data = _normalize_scenes(script_data)
            
            # Validation
            word_count = len(script_data['voiceover'].split())
            if not (MIN_WORDS - 10 <= word_count <= MAX_WORDS + 10):
                raise ValueError(f"Word count {word_count} is out of target range.")
            
            logger.info(f"Script successful: {word_count} words, {len(script_data['scenes'])} scenes.")
            return script_data

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError("Script generation failed after multiple attempts.")
