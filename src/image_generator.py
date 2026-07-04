import os
import time
import random
import hashlib
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
#   5. Local placeholder (assets/placeholder.png) - guaranteed final fallback
# ---------------------------------------------------------------------------

POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
GEMINI_IMAGE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

REQUEST_TIMEOUT = 30


def _save_bytes(content: bytes, index: int, ext: str = "jpg") -> str:
    os.makedirs("output", exist_ok=True)
    path = f"output/scene_{index}.{ext}"
    with open(path, "wb") as f:
        f.write(content)
    return path


def _layer1_pollinations_flux(index, prompt, seed):
    """Layer 1: Pollinations.ai, flux model (primary, free, no key)."""
    url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={seed}&model=flux&nologo=true"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200 and len(response.content) > 2000:
        return _save_bytes(response.content, index)
    raise RuntimeError(f"Pollinations(flux) bad response: {response.status_code}")


def _layer2_pollinations_turbo(index, prompt, seed):
    """Layer 2: Pollinations.ai, turbo model + a fresh seed - a genuinely
    different request, not a duplicate retry of layer 1."""
    new_seed = random.randint(10000, 99999)
    url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={new_seed}&model=turbo&nologo=true"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200 and len(response.content) > 2000:
        return _save_bytes(response.content, index)
    raise RuntimeError(f"Pollinations(turbo) bad response: {response.status_code}")


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


def _layer5_placeholder(index):
    """Layer 5: Local placeholder image - the guaranteed last resort."""
    placeholder = "assets/placeholder.png"
    if os.path.exists(placeholder):
        return placeholder
    raise RuntimeError("assets/placeholder.png missing - no fallback left")


def _generate_one(index, scene, used_hashes: set):
    prompt = scene.replace(' ', '_')
    seed = random.randint(1000, 9999)

    layers = [
        ("Pollinations-flux", lambda: _layer1_pollinations_flux(index, prompt, seed)),
        ("Pollinations-turbo", lambda: _layer2_pollinations_turbo(index, prompt, seed)),
        ("HuggingFace", lambda: _layer3_huggingface(index, scene)),
        ("Gemini", lambda: _layer4_gemini(index, scene)),
        ("Placeholder", lambda: _layer5_placeholder(index)),
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

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_generate_one, i, scene, used_hashes): i for i, scene in enumerate(scenes)}
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
