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
# FALLBACK CHAIN (in order):
#
#   1. Pollinations.ai  - "flux" model      (free, no key)
#   2. Pollinations.ai  - "turbo" model     (free, no key, different seed/model)
#   3. Hugging Face Inference API           (needs HF_API_KEY env var)
#   4. Cloudflare Workers AI                (needs CLOUDFLARE_ACCOUNT_ID +
#                                             CLOUDFLARE_API_TOKEN env vars)
#   5. DeepAI                               (needs DEEPAI_API_KEY env var -
#                                             only useful if your DeepAI plan
#                                             fits your needs)
#   6. OpenRouter                           (needs OPENROUTER_API_KEY env var
#                                             - only used when a $0-cost image
#                                             model is currently available)
#   7. Google Gemini image generation       (needs GEMINI_API_KEY env var -
#                                             kept from before, not on the
#                                             requested list but left in)
#   8. Pexels  - LIVE search                (needs PEXELS_API_KEY)
#   9. Pixabay - LIVE search                (needs PIXABAY_API_KEY, second try)
#  10. Local fallback pool                  (assets/fallback_images/*, random
#                                             non-repeating - now the LAST
#                                             thing tried before the final
#                                             guaranteed fallback, per your
#                                             request)
#  11. Guaranteed last resort               (reuse a local pool image, or the
#                                             legacy assets/placeholder.png -
#                                             never fails)
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
    """Layer 4: Google Gemini image generation (only runs if GEMINI_API_KEY is set).
    Not on your requested list, but left in since it's already working -
    remove it from the `layers` list in _generate_one if you don't want it."""
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


def _layer_cloudflare(index, scene_text):
    """Cloudflare Workers AI (needs CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN
    env vars). Uses the free FLUX.1-schnell model hosted on Workers AI -
    Cloudflare gives a daily free allocation of Workers AI usage."""
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID/CLOUDFLARE_API_TOKEN not set - skipping Cloudflare AI layer")

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers, json={"prompt": scene_text}, timeout=REQUEST_TIMEOUT)

    if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
        return _save_bytes(response.content, index)

    if response.status_code == 200:
        # Some Workers AI models return JSON with base64 instead of raw bytes.
        try:
            import base64
            result = response.json().get("result", {})
            b64 = result.get("image")
            if b64:
                return _save_bytes(base64.b64decode(b64), index, ext="png")
        except Exception:
            pass

    raise RuntimeError(f"Cloudflare AI bad response: {response.status_code} {response.text[:150]}")


def _layer_deepai(index, scene_text):
    """DeepAI text2img (needs DEEPAI_API_KEY env var). Only useful if your
    DeepAI plan/quota fits your needs - if the key isn't set, this layer is
    skipped automatically."""
    key = os.environ.get("DEEPAI_API_KEY")
    if not key:
        raise RuntimeError("DEEPAI_API_KEY not set - skipping DeepAI layer")

    response = requests.post(
        "https://api.deepai.org/api/text2img",
        data={"text": scene_text},
        headers={"api-key": key},
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code != 200:
        raise RuntimeError(f"DeepAI bad response: {response.status_code} {response.text[:150]}")

    img_url = response.json().get("output_url")
    if not img_url:
        raise RuntimeError("DeepAI response missing output_url")

    img_resp = requests.get(img_url, timeout=REQUEST_TIMEOUT)
    if img_resp.status_code != 200 or len(img_resp.content) < 2000:
        raise RuntimeError("DeepAI: failed to download generated image")
    return _save_bytes(img_resp.content, index)


_OPENROUTER_FREE_MODEL_CACHE = {"checked": False, "model": None}


def _get_free_openrouter_image_model(api_key):
    """Looks up whether OpenRouter currently has any $0-cost image-output
    model available, and caches the result for the rest of this run (model
    availability won't change mid-pipeline, no need to re-check every scene)."""
    if _OPENROUTER_FREE_MODEL_CACHE["checked"]:
        return _OPENROUTER_FREE_MODEL_CACHE["model"]

    model = None
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"output_modalities": "image"},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 200:
            for m in resp.json().get("data", []):
                pricing = m.get("pricing", {})
                # Free models report $0 pricing across the board.
                prices = [pricing.get(k) for k in ("prompt", "completion", "image") if k in pricing]
                if prices and all(float(p) == 0 for p in prices):
                    model = m.get("id")
                    break
    except Exception as e:
        logger.warning(f"OpenRouter free-model lookup failed: {e}")

    _OPENROUTER_FREE_MODEL_CACHE["checked"] = True
    _OPENROUTER_FREE_MODEL_CACHE["model"] = model
    return model


def _layer_openrouter(index, scene_text):
    """OpenRouter (needs OPENROUTER_API_KEY env var) - only used WHEN a free
    ($0-cost) image-output model is currently available on OpenRouter, per
    your instruction. If none is available right now, this layer is skipped
    (raises) rather than spending money automatically."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set - skipping OpenRouter layer")

    model = _get_free_openrouter_image_model(key)
    if not model:
        raise RuntimeError("OpenRouter: no free image-output model currently available")

    response = requests.post(
        "https://openrouter.ai/api/v1/images",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "prompt": scene_text},
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter bad response: {response.status_code} {response.text[:150]}")

    data = response.json()
    images = data.get("data") or data.get("images") or []
    if not images:
        raise RuntimeError("OpenRouter: response contained no images")

    first = images[0]
    b64 = first.get("b64_json") or first.get("image") if isinstance(first, dict) else None
    if not b64:
        raise RuntimeError("OpenRouter: response image had no usable base64 data")

    import base64
    return _save_bytes(base64.b64decode(b64), index, ext="png")


def _layer5_local_pool(index, used_fallbacks: set):
    """Local fallback pool (assets/fallback_images/*, thread-safe, random
    non-repeating). Now tried near the END of the chain (after all AI
    layers AND live Pexels/Pixabay), per your preference - it's only used
    once everything else has failed. If every image in the pool has
    already been used elsewhere in this same run, this layer raises
    instead of silently reusing one, so the final guaranteed-fallback
    layer handles the (rare) full-exhaustion case."""
    pool = _load_fallback_pool()
    if not pool:
        raise RuntimeError(f"'{FALLBACK_DIR}' is empty/missing - no local pool to use")

    with _fallback_lock:
        available = [p for p in pool if p not in used_fallbacks]
        if not available:
            raise RuntimeError("Local fallback pool exhausted for this run (all images already used)")
        choice = random.choice(available)
        used_fallbacks.add(choice)
    return choice


def _stock_photo_request(index, scene_text, source: str, used_fallbacks: set):
    """Shared helper for live Pexels/Pixabay lookups - only reached if the
    local pool (layer 5) has nothing fresh left to offer."""
    query = (scene_text or "baby parenting").strip()[:80]

    if source == "pexels":
        key = os.environ.get("PEXELS_API_KEY")
        if not key:
            raise RuntimeError("PEXELS_API_KEY not set - skipping live Pexels layer")
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": key},
            params={"query": query, "per_page": 15, "orientation": "portrait"},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Pexels bad response: {resp.status_code}")
        photos = resp.json().get("photos", [])
        if not photos:
            raise RuntimeError(f"Pexels: no results for '{query}'")
        img_urls = [p["src"]["large"] for p in photos]

    elif source == "pixabay":
        key = os.environ.get("PIXABAY_API_KEY")
        if not key:
            raise RuntimeError("PIXABAY_API_KEY not set - skipping live Pixabay layer")
        resp = requests.get(
            "https://pixabay.com/api/",
            params={"key": key, "q": query, "image_type": "photo",
                    "orientation": "vertical", "per_page": 15, "safesearch": "true"},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Pixabay bad response: {resp.status_code}")
        hits = resp.json().get("hits", [])
        if not hits:
            raise RuntimeError(f"Pixabay: no results for '{query}'")
        img_urls = [h.get("largeImageURL") or h.get("webformatURL") for h in hits]

    else:
        raise ValueError(f"Unknown stock source: {source}")

    # Try a few candidates in case one URL happens to already have been used
    # (e.g. same photo turns up for two different scene queries in this run).
    with _fallback_lock:
        for url in img_urls:
            if url in used_fallbacks:
                continue
            used_fallbacks.add(url)
            break
        else:
            url = img_urls[0]  # all seen before - still better than a static placeholder repeat

    img_resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if img_resp.status_code != 200 or len(img_resp.content) < 2000:
        raise RuntimeError(f"{source}: failed to download chosen image")
    return _save_bytes(img_resp.content, index)


def _layer6_pexels_live(index, scene_text, used_fallbacks: set):
    """Layer 6: live Pexels search, scoped to this scene's own description
    for relevance - only reached once the local pool is exhausted."""
    return _stock_photo_request(index, scene_text, "pexels", used_fallbacks)


def _layer7_pixabay_live(index, scene_text, used_fallbacks: set):
    """Layer 7: live Pixabay search - same role as layer 6, second try."""
    return _stock_photo_request(index, scene_text, "pixabay", used_fallbacks)


def _layer8_guaranteed_fallback(index, used_fallbacks: set):
    """Layer 8: absolute last resort - never raises. Reuses a local pool
    image (even if already used this run) or the legacy static placeholder.
    Only reached if layers 1-7 ALL failed (no internet, no API keys, empty
    pool - a very unlikely combination)."""
    pool = _load_fallback_pool()
    if pool:
        with _fallback_lock:
            choice = random.choice(pool)
            used_fallbacks.add(choice)
        logger.warning("All other layers failed - reusing a local fallback image (last resort).")
        return choice

    if os.path.exists(LEGACY_PLACEHOLDER):
        logger.warning("All other layers failed - using the static legacy placeholder (last resort).")
        return LEGACY_PLACEHOLDER

    raise RuntimeError("No fallback available anywhere: pool empty, no legacy placeholder, all live layers failed")


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
        ("Cloudflare-AI", lambda: _layer_cloudflare(index, scene_text)),
        ("DeepAI", lambda: _layer_deepai(index, scene_text)),
        ("OpenRouter", lambda: _layer_openrouter(index, scene_text)),
        ("Gemini", lambda: _layer4_gemini(index, scene_text)),
        ("Pexels-live", lambda: _layer6_pexels_live(index, scene_text, used_fallbacks)),
        ("Pixabay-live", lambda: _layer7_pixabay_live(index, scene_text, used_fallbacks)),
        ("LocalPool", lambda: _layer5_local_pool(index, used_fallbacks)),
        ("GuaranteedFallback", lambda: _layer8_guaranteed_fallback(index, used_fallbacks)),
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
            return {"ind
