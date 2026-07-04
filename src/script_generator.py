import os
import json
import time
import logging
from groq import Groq, BadRequestError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MIN_SCENES = 6
MAX_SCENES = 8
MIN_WORDS = 110
MAX_WORDS = 150


def _default_prompt(topic: str) -> str:
    """Fallback generic prompt (used only if no niche-specific prompt is passed in)."""
    return f"""
    You are a viral YouTube Shorts scriptwriter for a USA audience.
    Topic: "{topic}".
    Write a 40-55 second, high-retention, fast-paced script in ENGLISH ONLY.
    Use a strong hook in the first 3 seconds.
    Split the script into {MIN_SCENES}-{MAX_SCENES} scenes. Each scene needs:
      - "visual": 5-8 word description for image generation
      - "caption": the EXACT spoken text for that scene (captions concatenated
        in order must reconstruct the full voiceover word-for-word)
    Total spoken word count must be between {MIN_WORDS}-{MAX_WORDS} words.
    Output ONLY valid JSON:
    {{"title": "...", "hook": "...", "scenes": [{{"visual": "...", "caption": "..."}}], "cta": "..."}}
    """


def _normalize_scenes(script_data: dict) -> dict:
    """Ensure scenes is a list of {"visual","caption"} dicts and derive a
    top-level 'voiceover' field (join of all captions) for quality_checker /
    anti_spam / uploader description use."""
    scenes = script_data.get('scenes', [])
    normalized = []
    for s in scenes:
        if isinstance(s, dict):
            visual = s.get('visual') or s.get('description') or s.get('scene') or ''
            caption = s.get('caption') or s.get('text') or ''
        else:
            # Backward-compat: old format was a plain string (used as both)
            visual = str(s)
            caption = str(s)
        if visual and caption:
            normalized.append({"visual": visual.strip(), "caption": caption.strip()})

    script_data['scenes'] = normalized
    script_data['voiceover'] = ' '.join(s['caption'] for s in normalized)
    return script_data


def generate_script(topic: str, custom_prompt: str = None, max_retries: int = 3) -> dict:
    """
    Groq API se USA audience ke liye English script banata hai.
    Agar custom_prompt diya gaya hai (niche_strategy se), wahi use hota hai -
    warna generic fallback prompt. Retries max_retries tak agar invalid JSON
    ya validation fail ho.
    """
    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY missing hai. GitHub Secrets check karo.")

    prompt = custom_prompt or _default_prompt(topic)
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Script generation attempt {attempt}/{max_retries}")

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                response_format={"type": "json_object"},
                reasoning_effort="low",
                max_tokens=1800,
                timeout=30,
            )
            content = chat_completion.choices[0].message.content
            script_data = json.loads(content)

            if not all(k in script_data for k in ("title", "hook", "scenes")):
                raise ValueError("Response mein title/hook/scenes missing hai")

            if not isinstance(script_data['scenes'], list) or len(script_data['scenes']) < MIN_SCENES:
                raise ValueError(f"Scenes must be a list with at least {MIN_SCENES} items")

            script_data = _normalize_scenes(script_data)

            word_count = len(script_data['voiceover'].split())
            if word_count < MIN_WORDS - 20 or word_count > MAX_WORDS + 30:
                # Too far outside target -> better to regenerate than to
                # rely purely on post-hoc speed scaling in video_editor.
                raise ValueError(
                    f"Voiceover word count {word_count} too far from target "
                    f"{MIN_WORDS}-{MAX_WORDS} range - regenerating"
                )

            logger.info(f"Script generation successful ✅ ({word_count} words, {len(script_data['scenes'])} scenes)")
            return script_data

        except (BadRequestError, json.JSONDecodeError, ValueError) as e:
            last_error = e
            logger.error(f"Script generation attempt {attempt}/{max_retries} fail hui: {e}")
            if attempt < max_retries:
                time.sleep(3 * attempt)
            continue
        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error in script generation: {e}")
            if attempt < max_retries:
                time.sleep(3 * attempt)
            continue

    raise RuntimeError(f"Script generation {max_retries} attempts ke baad bhi fail hui: {last_error}")
