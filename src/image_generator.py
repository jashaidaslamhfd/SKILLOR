import os
import time
import json
import random
import shutil
import hashlib
import requests
import logging
import urllib.parse
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GEMINI HATA DIYA GAYA HAI — free tier quota 0 hai is model ke liye,
# isliye ye kabhi kaam nahi karta tha (har call 429 RESOURCE_EXHAUSTED deta
# tha). Agar future mein billing enable karo to wapas add kar sakte ho.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PRIORITY 1: Pollinations.ai — free, no API key, unlimited (fair-use only).
# Seed + style randomization taake same/similar prompt bhi hamesha NAYI
# image de, warna server-side caching ki wajah se reused content ka risk
# hota hai.
# ---------------------------------------------------------------------------
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
POLLINATIONS_TIMEOUT = 60
STYLE_VARIANTS = [
    "cinematic 3D render",
    "digital painting, concept art",
    "cinematic photo, dramatic lighting",
    "3D pixar-style render",
    "moody cinematic still",
    "hyperrealistic 3D illustration",
]

# ---------------------------------------------------------------------------
# PRIORITY 2: AI Horde (stablehorde.net) — genuinely free, community-GPU
# Stable Diffusion cluster. Anonymous key "0000000000" kaam karti hai
# (rate-limited but free), signup optional for higher priority.
# ---------------------------------------------------------------------------
AI_HORDE_KEY = os.environ.get("AI_HORDE_KEY", "0000000000")  # anonymous by default
AI_HORDE_SUBMIT_URL = "https://stablehorde.net/api/v2/generate/async"
AI_HORDE_STATUS_URL = "https://stablehorde.net/api/v2/generate/status/{id}"
AI_HORDE_TIMEOUT = 180
AI_HORDE_POLL_INTERVAL = 6

# ---------------------------------------------------------------------------
# PRIORITY 3 (fallback): Hugging Face FLUX.1-schnell — rakha hai kyunki
# monthly credits agle billing cycle refresh ho sakte hain. Abhi 402 aa raha
# hai to ye jaldi skip ho jayega (fail-fast flag neeche).
# ---------------------------------------------------------------------------
HF_API_KEY = os.environ.get("HF_API_KEY")
HF_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HF_TIMEOUT = 60
HF_MAX_RETRIES = 1  # sirf 1 try — agar fail ho (402/quota) to turant skip, retry pe time waste mat karo

# PRIORITY 4 (last resort): local placeholder image
PLACEHOLDER = "assets/placeholder.png"

# History file to avoid reused/duplicate images across videos
IMAGE_HISTORY_FILE = "output/image_history.json"
HASH_SIMILARITY_THRESHOLD = 6  # lower = stricter (perceptual hash hamming distance)


def _build_prompt(scene: str) -> str:
    style = random.choice(STYLE_VARIANTS)
    return (
        f"{style}, {scene}, high quality, vertical 9:16 shorts frame, "
        f"vibrant colors, detailed"
    )


def _try_pollinations(prompt: str, path: str, retries: int = 2) -> bool:
    """Free, no API key, effectively unlimited. Seed randomized every call."""
    encoded_prompt = urllib.parse.quote(prompt)
    seed = random.randint(1, 999_999)

    for attempt in range(1, retries + 1):
        url = (
            f"{POLLINATIONS_URL}/{encoded_prompt}"
            f"?width=1080&height=1920&nologo=true&seed={seed}&model=flux"
        )
        try:
            logger.info(f"Pollinations attempt {attempt}/{retries} (seed={seed})")
            response = requests.get(url, timeout=POLLINATIONS_TIMEOUT)

            if response.status_code == 200 and response.content:
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Pollinations image saved to {path}")
                return True

            logger.warning(f"Pollinations returned {response.status_code}, attempt {attempt}/{retries}")
            seed = random.randint(1, 999_999)  # naya seed agle attempt ke liye
            if attempt < retries:
                time.sleep(3 * attempt)

        except requests.Timeout:
            logger.error(f"Pollinations timeout (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(3 * attempt)
        except Exception as e:
            logger.error(f"Pollinations exception: {e} (attempt {attempt}/{retries})")
            if attempt < retries:
                time.sleep(3 * attempt)

    return False


def _try_ai_horde(prompt: str, path: str) -> bool:
    """Free community-GPU Stable Diffusion. Slower (queue-based) but real, diverse images."""
    try:
        headers = {"apikey": AI_HORDE_KEY, "Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "params": {
                "width": 576,   # AI Horde requires multiples of 64; upscale later if needed
                "height": 1024,
                "steps": 20,
                "sampler_name": "k_euler",
                "cfg_scale": 7,
                "seed": str(random.randint(1, 999_999)),
            },
            "nsfw": False,
            "models": ["stable_diffusion"],
        }

        logger.info("Submitting job to AI Horde...")
        submit = requests.post(AI_HORDE_SUBMIT_URL, headers=headers, json=payload, timeout=30)
        if submit.status_code not in (200, 202):
            logger.warning(f"AI Horde submit failed: {submit.status_code} - {submit.text[:150]}")
            return False

        job_id = submit.json().get("id")
        if not job_id:
            logger.warning("AI Horde: no job id returned")
            return False

        elapsed = 0
        while elapsed < AI_HORDE_TIMEOUT:
            time.sleep(AI_HORDE_POLL_INTERVAL)
            elapsed += AI_HORDE_POLL_INTERVAL
            status = requests.get(AI_HORDE_STATUS_URL.format(id=job_id), timeout=30)
            data = status.json()

            if data.get("done"):
                generations = data.get("generations", [])
                if not generations:
                    logger.warning("AI Horde: job done but no generations returned")
                    return False
                img_url = generations[0]["img"]
                img_resp = requests.get(img_url, timeout=60)
                if img_resp.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(img_resp.content)
                    logger.info(f"AI Horde image saved to {path}")
                    return True
                return False

            if data.get("faulted"):
                logger.warning("AI Horde: job faulted")
                return False

        logger.warning("AI Horde: timed out waiting for job")
        return False

    except Exception as e:
        logger.error(f"AI Horde exception: {e}")
        return False


def _try_huggingface(prompt: str, path: str, retries: int = HF_MAX_RETRIES) -> bool:
    if not HF_API_KEY:
        return False

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"HF attempt {attempt}/{retries}")
            response = requests.post(HF_URL, headers=headers, json=payload, timeout=HF_TIMEOUT)

            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Hugging Face image saved to {path}")
                return True

            # 402 = credits depleted, 429 = rate limited — dono ka matlab
            # is run mein dobara try karna faltu hai, turant fail mark karo
            if response.status_code in (402, 429):
                logger.warning(f"HF unavailable this run (HTTP {response.status_code}) - skipping further HF attempts")
                return False

            logger.error(f"HF Error: {response.status_code} - {response.text[:150]}")
            return False

        except Exception as e:
            logger.error(f"HF exception: {e}")
            return False

    return False


def _phash(path: str):
    """Lightweight perceptual hash (no extra dependency needed beyond Pillow)."""
    try:
        from PIL import Image
        img = Image.open(path).convert("L").resize((9, 8), Image.LANCZOS)
        pixels = list(img.getdata())
        diff = []
        for row in range(8):
            for col in range(8):
                diff.append(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
        # pack bits into hex string
        bits = "".join("1" if b else "0" for b in diff)
        return hex(int(bits, 2))
    except Exception as e:
        logger.debug(f"phash failed: {e}")
        return None


def _hamming(h1: str, h2: str) -> int:
    try:
        b1, b2 = bin(int(h1, 16))[2:].zfill(64), bin(int(h2, 16))[2:].zfill(64)
        return sum(c1 != c2 for c1, c2 in zip(b1, b2))
    except Exception:
        return 999


def _load_image_history() -> list:
    if os.path.exists(IMAGE_HISTORY_FILE):
        try:
            with open(IMAGE_HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_image_history(hashes: list):
    os.makedirs(os.path.dirname(IMAGE_HISTORY_FILE) or ".", exist_ok=True)
    history = _load_image_history()
    history.extend(hashes)
    history = history[-500:]  # keep last 500 image hashes only
    with open(IMAGE_HISTORY_FILE, "w") as f:
        json.dump(history, f)


def _is_duplicate(path: str, known_hashes: list) -> bool:
    h = _phash(path)
    if not h:
        return False
    for known in known_hashes:
        if _hamming(h, known) <= HASH_SIMILARITY_THRESHOLD:
            return True
    return False


def _generate_one(i: int, scene: str, known_hashes: list) -> dict:
    """Generate a single scene image, trying fallbacks in order, retrying
    once with a new prompt/seed if the result is a near-duplicate of a
    previously used image."""
    path = f"scene_{i}.png"

    for retry in range(2):  # up to 2 tries if duplicate detected
        prompt = _build_prompt(scene)
        success = False
        source = None

        success = _try_pollinations(prompt, path)
        source = "Pollinations.ai"

        if not success:
            success = _try_ai_horde(prompt, path)
            source = "AI Horde"

        if not success:
            success = _try_huggingface(prompt, path)
            source = "Hugging Face"

        if success:
            if _is_duplicate(path, known_hashes):
                logger.warning(f"Scene {i+1}: near-duplicate detected from [{source}], retrying with new prompt/seed...")
                continue  # try again with different style/seed
            logger.info(f"Scene {i+1} generated ✅ [{source}]")
            return {"index": i, "path": path, "success": True}

    # Last resort: placeholder
    if os.path.exists(PLACEHOLDER):
        shutil.copy(PLACEHOLDER, path)
        logger.warning(f"Scene {i+1}: all sources failed/duplicate — used placeholder")
        return {"index": i, "path": path, "success": True}

    logger.error(f"Scene {i+1}: failed and no placeholder available")
    return {"index": i, "path": path, "success": False}


def generate_images(scenes: List[str], max_workers: int = 4) -> List[str]:
    """
    Har scene ke liye (parallel):
      1. Pollinations.ai (free, unlimited, seed+style randomized)
      2. AI Horde (free community GPU, real diversity)
      3. Hugging Face (fallback, agar credits available hon)
      4. Placeholder (last resort)

    Duplicate-check: har naye image ka perceptual hash purane history se
    compare hota hai; match milne par prompt/seed badal ke dobara try hota
    hai — taake same/similar image repeat na ho.

    Return list HAMESHA len(scenes) ke barabar hogi.
    """
    known_hashes = _load_image_history()
    results = [None] * len(scenes)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_generate_one, i, scene, known_hashes): i
            for i, scene in enumerate(scenes)
        }
        for future in as_completed(futures):
            r = future.result()
            results[r["index"]] = r

    paths = [r["path"] for r in results if r]
    new_hashes = [h for h in (_phash(r["path"]) for r in results if r and r["success"]) if h]
    _save_image_history(new_hashes)

    if not any(r["success"] for r in results if r):
        raise RuntimeError(
            "Koi bhi image nahi bani (Pollinations, AI Horde, Hugging Face, placeholder sab fail) — "
            "pipeline rok rahe hain. Internet/network access aur assets/placeholder.png check karo."
        )

    return paths
