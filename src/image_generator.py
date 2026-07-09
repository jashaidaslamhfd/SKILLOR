import os
import time
import random
import hashlib
import threading
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FALLBACK CHAIN (in order) - simplified to 3 layers only:
#   1) Playwright  - search the topic, open the top result, screenshot it
#   2) Pexels      - live stock photo API
#   3) Pixabay     - live stock photo API
# All the old AI-image-generator layers (Pollinations, HuggingFace, Gemini,
# Cloudflare AI, ModelsLab, Replicate) and the local fallback pool have been
# removed on purpose - just these 3 layers now.
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 30
_fallback_lock = threading.Lock()

def _save_bytes(content: bytes, index: int, ext: str = "jpg") -> str:
    os.makedirs("output", exist_ok=True)
    path = f"output/scene_{index}.{ext}"
    with open(path, "wb") as f:
        f.write(content)
    return path

def _layer1_playwright_screenshot(index, scene_text):
    """Video script ke scene text se relevant website dhoondo (search engine
    ke pehle result se), us page ko khol kar screenshot le lo - wahi screenshot
    is scene ka visual clip ban jata hai."""
    from playwright.sync_api import sync_playwright

    query = (scene_text or "mystery science").strip()[:100]
    screenshot_bytes = None

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.set_default_timeout(20000)

            # DuckDuckGo ka HTML-only endpoint - no JS needed, easy to scrape,
            # aur bina API key ke kaam karta hai.
            page.goto(f"https://html.duckduckgo.com/html/?q={query}", wait_until="domcontentloaded")
            link = page.query_selector("a.result__a")
            if not link:
                raise RuntimeError("Playwright: search result nahi mila")
            target_url = link.get_attribute("href")
            if not target_url:
                raise RuntimeError("Playwright: search result ka href empty tha")

            page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1500)  # cookie banners/lazy images settle hone dein
            screenshot_bytes = page.screenshot(type="png")
        finally:
            browser.close()

    if not screenshot_bytes or len(screenshot_bytes) < 2000:
        raise RuntimeError("Playwright: screenshot khaali/chota tha")
    return _save_bytes(screenshot_bytes, index, ext="png")

def _stock_photo_request(index, scene_text, source: str, used_fallbacks: set):
    query = (scene_text or "mystery science").strip()[:80]
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

def _layer2_pexels_live(index, scene_text, used_fallbacks: set):
    return _stock_photo_request(index, scene_text, "pexels", used_fallbacks)

def _layer3_pixabay_live(index, scene_text, used_fallbacks: set):
    return _stock_photo_request(index, scene_text, "pixabay", used_fallbacks)

def _scene_text(scene) -> str:
    if isinstance(scene, dict):
        return scene.get('visual') or scene.get('description') or scene.get('scene') or scene.get('caption') or ''
    return str(scene)

def _generate_one(index, scene, used_hashes: set, used_fallbacks: set):
    scene_text = _scene_text(scene)

    layers = [
        ("Playwright-screenshot", lambda: _layer1_playwright_screenshot(index, scene_text)),
        ("Pexels-live", lambda: _layer2_pexels_live(index, scene_text, used_fallbacks)),
        ("Pixabay-live", lambda: _layer3_pixabay_live(index, scene_text, used_fallbacks)),
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
