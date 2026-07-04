import os
import time
import shutil
import requests
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PRIORITY 1: Google Gemini (Nano Banana - gemini-2.5-flash-image)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-image"

# ---------------------------------------------------------------------------
# PRIORITY 2 (fallback): Hugging Face FLUX.1-schnell
# NOTE: Hugging Face ne purana "api-inference.huggingface.co" endpoint band
# kar diya hai (410 Gone / DNS resolve fail). Naya endpoint router.huggingface.co
# ke through jata hai.
# ---------------------------------------------------------------------------
HF_API_KEY = os.environ.get("HF_API_KEY")
HF_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HF_TIMEOUT = 120  # Increased timeout for image generation
HF_MAX_RETRIES = 3

# PRIORITY 3 (fallback): Pollinations.ai — free, no API key, effectively
# unlimited (fair-use rate limit only). Used when Gemini + Hugging Face
# both fail (quota/credits exhausted), so we still get a real AI image
# instead of repeating the same placeholder for every scene.
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
POLLINATIONS_TIMEOUT = 60

# PRIORITY 4 (last resort): local placeholder image, taake image count
# hamesha scene count ke barabar rahe (index/caption misalignment na ho)
PLACEHOLDER = "assets/placeholder.png"


def _try_gemini(prompt: str, path: str) -> bool:
    """Try generating image with Google Gemini API."""
    if not GEMINI_API_KEY:
        logger.debug("Gemini API key not configured")
        return False
    try:
        from google import genai
        from google.genai import types

        logger.info("Attempting Gemini image generation...")
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
            ),
        )
        for part in response.parts:
            if part.inline_data is not None:
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                logger.info(f"Gemini image saved to {path}")
                return True
        logger.warning("Gemini ne image return nahi ki (empty response, shayad safety filter)")
        return False
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return False


def _try_huggingface(prompt: str, path: str, retries: int = HF_MAX_RETRIES) -> bool:
    """Try generating image with Hugging Face API with improved error handling."""
    if not HF_API_KEY:
        logger.debug("Hugging Face API key not configured")
        return False
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"HF attempt {attempt}/{retries}")
            response = requests.post(
                HF_URL, 
                headers=headers, 
                json=payload, 
                timeout=HF_TIMEOUT
            )
            
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Hugging Face image saved to {path}")
                return True
            
            elif response.status_code == 503:
                # Model loading - retry with backoff
                wait = 15 * attempt  # Increased wait time
                logger.warning(f"HF model loading (503), waiting {wait}s before retry (attempt {attempt}/{retries})")
                time.sleep(wait)
                continue
            
            elif response.status_code == 429:
                # Rate limited - wait longer
                wait = 30 * attempt
                logger.warning(f"HF rate limited (429), waiting {wait}s before retry")
                time.sleep(wait)
                continue
            
            else:
                error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
                logger.error(f"HF Error: {response.status_code} - {error_msg}")
                if response.status_code >= 500:
                    # Server error - retry
                    if attempt < retries:
                        time.sleep(5 * attempt)
                        continue
                return False
        
        except requests.Timeout:
            logger.error(f"HF request timeout (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(5 * attempt)
                continue
        
        except requests.ConnectionError as e:
            logger.error(f"HF connection error: {e} (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(5 * attempt)
                continue
        
        except Exception as e:
            logger.error(f"HF exception: {e} (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(3 * attempt)
                continue
    
    return False


def _try_pollinations(prompt: str, path: str, retries: int = 2) -> bool:
    """
    Try generating image with Pollinations.ai — free, no API key needed.
    Practically unlimited (fair-use rate limits, no hard quota/credits).
    """
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    # width/height tuned for a 9:16 vertical Shorts frame
    url = f"{POLLINATIONS_URL}/{encoded_prompt}?width=1080&height=1920&nologo=true"

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Pollinations attempt {attempt}/{retries}")
            response = requests.get(url, timeout=POLLINATIONS_TIMEOUT)

            if response.status_code == 200 and response.content:
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Pollinations image saved to {path}")
                return True

            logger.warning(
                f"Pollinations returned {response.status_code}, "
                f"attempt {attempt}/{retries}"
            )
            if attempt < retries:
                time.sleep(3 * attempt)

        except requests.Timeout:
            logger.error(f"Pollinations request timeout (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(3 * attempt)

        except Exception as e:
            logger.error(f"Pollinations exception: {e} (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(3 * attempt)

    return False


def generate_images(scenes: List[str]) -> List[str]:
    """
    Har scene ke liye:
      1. Pehle Google Gemini (Nano Banana) try hota hai — first priority
      2. Fail ho to Hugging Face FLUX.1-schnell fallback
      3. Fail ho to Pollinations.ai (free, unlimited, no API key) fallback
      4. Sab fail ho to local placeholder image copy hoti hai

    Return list HAMESHA len(scenes) ke barabar hogi, taake video_editor.py
    mein caption <-> image index kabhi bhi misalign na ho.
    """
    paths = []

    for i, scene in enumerate(scenes):
        try:
            prompt = (
                f"Cinematic 3D render, {scene}, high quality, photorealistic, "
                f"vertical 9:16 shorts frame, dramatic lighting, vibrant colors"
            )
            path = f"scene_{i}.png"
            
            logger.info(f"Generating image {i+1}/{len(scenes)}: {scene[:50]}...")
            
            # Try Gemini first
            success = _try_gemini(prompt, path)
            source = "Gemini"

            # Fallback to Hugging Face
            if not success:
                success = _try_huggingface(prompt, path)
                source = "Hugging Face (fallback)"

            # Fallback to Pollinations.ai (free, unlimited, no key needed)
            if not success:
                success = _try_pollinations(prompt, path)
                source = "Pollinations.ai (fallback)"

            # Last resort: placeholder
            if not success:
                source = "Placeholder (dono APIs fail)"
                if os.path.exists(PLACEHOLDER):
                    try:
                        shutil.copy(PLACEHOLDER, path)
                        success = True
                        logger.info(f"Used placeholder for scene {i+1}")
                    except Exception as e:
                        logger.error(f"Failed to copy placeholder: {e}")
                else:
                    logger.warning(f"Placeholder image missing at {PLACEHOLDER}")

            if success:
                paths.append(path)
                logger.info(f"Scene {i+1}/{len(scenes)} generated ✅ [{source}]")
            else:
                logger.error(f"Failed to generate image for scene {i+1}")

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error processing scene {i+1}: {e}")
            # Try to use placeholder as fallback
            if os.path.exists(PLACEHOLDER):
                try:
                    path = f"scene_{i}.png"
                    shutil.copy(PLACEHOLDER, path)
                    paths.append(path)
                    logger.info(f"Scene {i+1} - used placeholder as fallback")
                except Exception as copy_error:
                    logger.error(f"Could not use placeholder: {copy_error}")

    if not paths:
        logger.error("No images generated at all")
        raise RuntimeError(
            "Koi bhi image nahi bani (Gemini, Hugging Face, Pollinations, placeholder sab fail) — "
            "pipeline rok rahe hain. Internet/network access ya GEMINI_API_KEY / HF_API_KEY "
            "aur assets/placeholder.png check karo."
        )

    # Ensure we have exactly len(scenes) images
    if len(paths) < len(scenes):
        logger.warning(f"Only {len(paths)}/{len(scenes)} images generated, filling with placeholder")
        while len(paths) < len(scenes):
            if os.path.exists(PLACEHOLDER):
                idx = len(paths)
                path = f"scene_{idx}.png"
                shutil.copy(PLACEHOLDER, path)
                paths.append(path)
            else:
                raise RuntimeError(f"Cannot fill missing images - placeholder not found")

    return paths
