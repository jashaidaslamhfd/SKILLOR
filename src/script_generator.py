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
    2. High Pacing: Short, punchy SENTENCES - this does not mean a short script.
       Use several punchy sentences per scene so the total word count still hits
       the target given in the user prompt; a script that undershoots the word
       count is treated as a failed output, so never sacrifice length for brevity.
    3. Loopable Outros: The end should naturally lead back to the start.
    4. Retention: Remove filler/fluff words, but keep every scene's content full -
       "no fluff" means no wasted words, not fewer words overall.
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
    messages = [
        {"role": "system", "content": _get_system_prompt()},
        {"role": "user", "content": prompt}
    ]

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Generating optimized script (Attempt {attempt}/{max_retries})")

            completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2500
            )

            raw_reply = completion.choices[0].message.content
            script_data = json.loads(raw_reply)
            script_data = _normalize_scenes(script_data)

            # Validation
            word_count = len(script_data['voiceover'].split())
            if not (MIN_WORDS - 10 <= word_count <= MAX_WORDS + 10):
                # Give the model a corrective nudge instead of rerolling blind:
                # tell it exactly how far off it was and ask it to rewrite the
                # SAME script at the right length rather than starting over.
                direction = "shorter" if word_count > MAX_WORDS + 10 else "longer"
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({"role": "user", "content": (
                    f"That script's voiceover was {word_count} words, but it must be "
                    f"{MIN_WORDS}-{MAX_WORDS} words total. It needs to be {direction}. "
                    f"Rewrite the full script (same topic, hook, and structure) with "
                    f"every scene's caption adjusted so the total lands in "
                    f"{MIN_WORDS}-{MAX_WORDS} words. Return ONLY the corrected JSON, "
                    f"same shape as before."
                )})
                raise ValueError(f"Word count {word_count} is out of target range.")

            logger.info(f"Script successful: {word_count} words, {len(script_data['scenes'])} scenes.")
            return script_data

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError("Script generation failed after multiple attempts.")
