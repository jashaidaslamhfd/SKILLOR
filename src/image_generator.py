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
# ---------------------------------------------------------------------------

POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
GEMINI_IMAGE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"

REQUEST_TIMEOUT = 30

FALLBACK_DIR = "assets/fallback_images"
LEGACY_PLACEHOLDER = "assets/placeholder.png"
_FALLBACK_POOL_CACHE = None
_fallback_lock = threading.Lock()

def _load_fallback_pool():
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
    url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={seed}&model={model}&nologo=true"
    last_status = None
    for attempt in range(3):
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200 and len(response.content) > 2000:
            return _save_bytes(response.content, index)
        last_status = response.status_code
        if response.status_code == 429:
            time.sleep(2 + attempt * 3)
            continue
        break
    raise RuntimeError(f"Pollinations({model}) bad response: {last_status}")

def _layer1_pollinations_flux(index, prompt, seed):
    return _pollinations_request(prompt, seed, "flux", index)

def _layer2_pollinations_turbo(index, prompt, seed):
    new_seed = random.randint(10000, 99999)
    return _pollinations_request(prompt, new_seed, "turbo", index)

def _layer3_huggingface(index, scene_text):
    hf_key = os.environ.get("HF_API_KEY")
    if not hf_key:
        raise RuntimeError("HF_API_KEY not set - skipping Hugging Face layer")

    headers = {"Authorization": f"Bearer {hf_key}"}
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": scene_text}, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200 and response.headers.get("content-type", "").startswith("image"):
        return _save_bytes(response.content, index)
    raise RuntimeError(f"Hugging Face bad response: {response.status_code} {response.text[:150]}")

def _layer4_gemini(index, scene_text):
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
        try:
            import base64
            result = response.json().get("result", {})
            b64 = result.get("image")
            if b64:
                return _save_bytes(base64.b64decode(b64), index, ext="png")
        except Exception:
            pass
    raise RuntimeError(f"Cloudflare AI bad response: {response.status_code} {response.text[:150]}")

def _layer_modelslab(index, scene_text):
    api_key = os.environ.get("MODELSLAB_API_KEY")
    if not api_key:
        raise RuntimeError("MODELSLAB_API_KEY not set - skipping ModelsLab layer")

    payload = {
        "key": api_key,
        "prompt": scene_text,
        "negative_prompt": "blurry, low quality, watermark",
        "width": "1024",
        "height": "1024",
        "samples": "1",
        "safety_checker": "no",
    }
    response = requests.post("https://modelslab.com/api/v6/images/text2img", json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"ModelsLab bad response: {response.status_code} {response.text[:150]}")

    data = response.json()
    if data.get("status") not in ("success", "processing"):
        raise RuntimeError(f"ModelsLab error: {data.get('message', data)}")
    images = data.get("output") or data.get("images") or []
    if not images:
        raise RuntimeError("ModelsLab: no image URL returned (may need to poll fetch_result)")

    img_resp = requests.get(images[0], timeout=60)
    if img_resp.status_code != 200 or len(img_resp.content) < 2000:
        raise RuntimeError("ModelsLab: failed to download generated image")
    return _save_bytes(img_resp.content, index)

def _layer_replicate(index, scene_text):
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        raise RuntimeError("REPLICATE_API_TOKEN not set - skipping Replicate layer")

    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    response = requests.post(
        "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
        headers=headers,
        json={"input": {"prompt": scene_text}},
        timeout=30,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Replicate bad response: {response.status_code} {response.text[:150]}")

    prediction = response.json()
    get_url = prediction.get("urls", {}).get("get")
    if not get_url:
        raise RuntimeError("Replicate: no polling URL in response")

    for _ in range(20):  # poll up to ~20s
        time.sleep(1)
        poll = requests.get(get_url, headers=headers, timeout=15).json()
        status = poll.get("status")
        if status == "succeeded":
            output = poll.get("output")
            img_url = output[0] if isinstance(output, list) else output
            if not img_url:
                raise RuntimeError("Replicate: succeeded but no output URL")
            img_resp = requests.get(img_url, timeout=30)
            return _save_bytes(img_resp.content, index)
        if status == "failed":
            raise RuntimeError(f"Replicate: prediction failed - {poll.get('error')}")
    raise RuntimeError("Replicate: timed out waiting for prediction")

def _layer5_local_pool(index, used_fallbacks: set):
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

    with _fallback_lock:
        for url in img_urls:
            if url in used_fallbacks:
                continue
            used_fallbacks.add(url)
            break
        else:
            url = img_urls[0]
    img_resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if img_resp.status_code != 200 or len(img_resp.content) < 2000:
        raise RuntimeError(f"{source}: failed to download chosen image")
    return _save_bytes(img_resp.content, index)

def _layer6_pexels_live(index, scene_text, used_fallbacks: set):
    return _stock_photo_request(index, scene_text, "pexels", used_fallbacks)

def _layer7_pixabay_live(index, scene_text, used_fallbacks: set):
    return _stock_photo_request(index, scene_text, "pixabay", used_fallbacks)

def _layer8_guaranteed_fallback(index, used_fallbacks: set):
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
    if isinstance(scene, dict):
        return scene.get('visual') or scene.get('description') or scene.get('scene') or scene.get('caption') or ''
    return str(scene)

def _generate_one(index, scene, used_hashes: set, used_fallbacks: set):
    scene_text = _scene_text(scene)
    prompt = scene_text.replace(' ', '_')
    seed = random.randint(1000, 9999)

    # DeepAI aur OpenRouter hata diye gaye — dono ka free tier khatam ho chuka hai
    # (DeepAI ab sirf Pro members ke liye, OpenRouter ko paid credits chahiye),
    # isliye ye har run mein sirf time waste kar rahe the bina kabhi succeed hue.
    layers = [
        ("Pollinations-flux", lambda: _layer1_pollinations_flux(index, prompt, seed)),
        ("Pollinations-turbo", lambda: _layer2_pollinations_turbo(index, prompt, seed)),
        ("HuggingFace", lambda: _layer3_huggingface(index, scene_text)),
        ("Cloudflare-AI", lambda: _layer_cloudflare(index, scene_text)),
        ("Gemini", lambda: _layer4_gemini(index, scene_text)),
        ("ModelsLab", lambda: _layer_modelslab(index, scene_text)),
        ("Replicate", lambda: _layer_replicate(index, scene_text)),
        ("Pexels-live", lambda: _layer6_pexels_live(index, scene_text, used_fallbacks)),
        ("Pixabay-live", lambda: _layer7_pixabay_live(index, scene_text, used_fallbacks)),
        ("LocalPool", lambda: _layer5_local_pool(index, used_fallbacks)),
        ("GuaranteedFallback", lambda: _layer8_guaranteed_fallback(index, used_fallbacks)),
    ]

    for name, fn in layers:
        try:
            path = fn()
            try:
                with open(path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash in used_hashes:
                    logger.warning(f"Scene {index}: image from '{name}' is byte-identical to an earlier scene's image (reused-content risk).")
                used_hashes.add(file_hash)
            except Exception:
                pass

            logger.info(f"Scene {index}: image generated via {name} -> {path}")
            return {"index": index, "path": path, "source": name}
        except Exception as e:
            logger.error(f"Scene {index}: {name} failed: {e}")
            continue

    raise RuntimeError(f"Scene {index}: All generation layers failed.")
