import os
import time
import random
import hashlib
import threading
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 5-LAYER FALLBACK CHAIN (was only 2 layers before - Pollinations + placeholder.
# Layers 3 & 4 were only mentioned in a comment and never actually written.)
#
#   1. Pollinations.ai  - "flux" model      (free, no key)
#   2. Pollinations.ai  - "turbo" model     (free, no key, different seed/model
#                                             so it isn't just retrying the
#                                             exact same failing request)
#   3. Hugging Face Inference API           (needs HF_API_KEY env var)
#   4. Google Gemini image generation       (needs GEMINI_API_KEY env var)
#   5. Local fallback pool (assets/fallback_images/*, random non-repeating)
#                                             - guaranteed final fallback
# ---------------------------------------------------------------------------

POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
GEMINI_IMAGE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"

REQUEST_TIMEOUT = 30

# ---------------------------------------------------------------------------
# Fallback image pool: instead of ONE static placeholder.png, keep a large
# folder of stock images (e.g. ~500). Every time layer 5 has to be used, a
# random image is picked that hasn't already been used elsewhere in this
# same run - this drastically cuts down "identical reused image" risk vs a
# single static file, without needing scenes to be categorized/tagged.
# ---------------------------------------------------------------------------
FALLBACK_DIR = "assets/fallback_images"
LEGACY_PLACEHOLDER = "assets/placeholder.png"
_FALLBACK_POOL_CACHE = None
_fallback_lock = threading.Lock()


def _load_fallback_pool():
    """Scans FALLBACK_DIR once and caches the list of image paths."""
    global _FALLBACK_POOL_CACHE
    if _FALLBACK_POOL_CACHE is not None:
        return _FALLBACK_POOL_CACHE

    valid_ext = (".jpg", ".jpeg", ".png", ".webp")
    pool = []
    if os.path.isdir(FALLBACK_DIR):
        for fname in os.listdir(FALLBACK_DIR):
            if fname.lower().endswith(valid_ext):
                pool.append(os.path.join(FALLBACK_DIR, fname))

    _FALLBACK_POOL_CACHE = pool
    return pool


def _save_bytes(content: bytes, index: int, ext: str = "jpg") -> str:
    os.makedirs("output", exist_ok=True)
    path = f"output/scene_{index}.{ext}"
    with open(path, "wb") as f:
        f.write(content)
    return path


def _pollinations_request(prompt, seed, model, index):
    """Shared helper: request an image from Pollinations, retrying briefly on
    429 (rate limit) instead of immediately giving up - this cuts down how
    often scenes fall through to the placeholder pool just because two
    threads happened to hit Pollinations at the same moment."""
    url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={seed}&model={model}&nologo=true"
    last_status = None
    for attempt in range(3):
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200 and len(response.content) > 2000:
            return _save_bytes(response.content, index)
        last_status = response.status_code
        if response.status_code == 429:
            time.sleep(2 + attempt * 3)  # 2s, 5s, 8s backoff
            continue
        break  # non-429 failure - no point retrying the same request
    raise RuntimeError(f"Pollinations({model}) bad response: {last_status}")


def _layer1_pollinations_flux(index, prompt, seed):
    """Layer 1: Pollinations.ai, flux model (primary, free, no key)."""
    return _pollinations_request(prompt, seed, "flux", index)


def _layer2_pollinations_turbo(index, prompt, seed):
    """Layer 2: Pollinations.ai, turbo model + a fresh seed - a genuinely
    different request, not a duplicate retry of layer 1."""
    new_seed = random.randint(10000, 99999)
    return _pollinations_request(prompt, new_seed, "turbo", index)


def _layer3_huggingface(index, scene_text):
    """Layer 3: Hugging Face Inference API (only runs if HF_API_KEY is set)."""
    hf_key = os.environ.get("HF_API_KEY")
    if not hf_key:
        raise RuntimeError("HF_API_KEY not set - skipping Hugging Face layer")

    headers = {"Authorization": f"Bearer {hf_key}"}
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": scene_text}, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
        return _save_bytes(response.content, index)
    raise RuntimeError(f"Hugging Face bad response: {response.status_code} {response.text[:150]}")


def _layer4_gemini(index, scene_text):
    """Layer 4: Google Gemini image generation (only runs if GEMINI_API_KEY is set)."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY not set - skipping Gemini layer")

    import base64
    payload = {
        "contents": [{"parts": [{"text": f"Generate a photorealistic vertical image: {scene_text}"}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    url = f"{GEMINI_IMAGE_URL}?key={gemini_key}"
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini bad response: {response.status_code} {response.text[:150]}")

    data = response.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            image_bytes = base64.b64decode(inline["data"])
            return _save_bytes(image_bytes, index, ext="png")
    raise RuntimeError("Gemini response contained no image data")


def _layer5_placeholder(index, used_fallbacks: set):
    """Layer 5: guaranteed last resort. Picks a random, not-yet-used image
    from the assets/fallback_images/ pool (thread-safe). Falls back to the
    old single assets/placeholder.png if that pool doesn't exist/is empty."""
    pool = _load_fallback_pool()

    if pool:
        with _fallback_lock:
            available = [p for p in pool if p not in used_fallbacks]
            if not available:
                # Pool exhausted (more scenes than unique images) - allow
                # repeats rather than failing the scene entirely.
                logger.warning("Fallback pool exhausted for this run - reusing an already-used fallback image.")
                available = pool
            choice = random.choice(available)
            used_fallbacks.add(choice)
        return choice

    # Legacy behavior if no pool folder is set up yet.
    if os.path.exists(LEGACY_PLACEHOLDER):
        return LEGACY_PLACEHOLDER
    raise RuntimeError(f"No fallback available: '{FALLBACK_DIR}' is empty/missing and '{LEGACY_PLACEHOLDER}' also missing")


def _scene_text(scene) -> str:
    """Scenes may be a plain string (old format) or a dict like
    {"visual": "...", "caption": "..."} (current script_generator format).
    Always resolve to the descriptive text used for image prompts."""
    if isinstance(scene, dict):
        return scene.get('visual') or scene.get('description') or scene.get('scene') or scene.get('caption') or ''
    return str(scene)


def _generate_one(index, scene, used_hashes: set, used_fallbacks: set):
    scene_text = _scene_text(scene)
    prompt = scene_text.replace(' ', '_')
    seed = random.randint(1000, 9999)

    layers = [
        ("Pollinations-flux", lambda: _layer1_pollinations_flux(index, prompt, seed)),
        ("Pollinations-turbo", lambda: _layer2_pollinations_turbo(index, prompt, seed)),
        ("HuggingFace", lambda: _layer3_huggingface(index, scene_text)),
        ("Gemini", lambda: _layer4_gemini(index, scene_text)),
        ("Placeholder", lambda: _layer5_placeholder(index, used_fallbacks)),
    ]

    for name, fn in layers:
        try:
            path = fn()
            # Duplicate-content awareness: warn (not block) if the exact same
            # file bytes have already been used for another scene in this
            # video - helps flag "reused content" risk early.
            try:
                with open(path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash in used_hashes:
                    logger.warning(f"Scene {index}: image from '{name}' is byte-identical to an earlier scene's image (reused-content risk).")
                used_hashes.add(file_hash)
            except Exception:
                pass

            logger.info(f"Scene {index}: image generated via {name} -> {path}")
            return {"index": index, "path": path, "success": True, "source": name}
        except Exception as e:
            logger.warning(f"Scene {index}: layer '{name}' failed: {e}")
            continue

    logger.error(f"Scene {index}: ALL 5 layers failed.")
    return {"index": index, "path": None, "success": False, "source": None}


def generate_images(scenes, max_workers=2):
    """
    5-Layer fallback chain, executed per scene:
    Pollinations(flux) -> Pollinations(turbo) -> Hugging Face -> Gemini -> Placeholder
    Returns a list of image paths (same order as `scenes`), skipping only
    scenes where literally every layer failed (which should be near-impossible
    as long as assets/placeholder.png exists).
    """
    results = [None] * len(scenes)
    used_hashes = set()
    used_fallbacks = set()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_generate_one, i, scene, used_hashes, used_fallbacks): i for i, scene in enumerate(scenes)}
        for future in as_completed(futures):
            r = future.result()
            results[r["index"]] = r

    paths = [r["path"] for r in results if r and r["path"]]

    if len(paths) < len(scenes):
        failed = [r["index"] for r in results if r and not r["path"]]
        logger.error(f"{len(scenes) - len(paths)} scene(s) failed ALL 5 layers: {failed}")

    return paths


# Test block
if __name__ == "__main__":
    test_scenes = ["happy baby playing", "brain science diagram"]
    paths = generate_images(test_scenes)
    print(f"Generated paths: {paths}")
