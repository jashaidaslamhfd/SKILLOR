import os
import random
import hashlib
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from image_providers import PROVIDER_REGISTRY, available_providers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# N-LAYER FALLBACK CHAIN — provider list ab image_providers.py mein shared
# registry se aati hai (dono ye file aur scripts/generate_fallback_images.py
# usi registry se providers uthate hain, taake nayi API add karne par dono
# jagah automatically mil jaye, alag-alag jagah copy-paste na karna pade).
#
# Order (env keys available hone par):
#   1. Pollinations.ai  - "flux" model      (free, no key)
#   2. Pollinations.ai  - "turbo" model     (free, no key, different seed/model)
#   3. Hugging Face Inference API           (needs HF_API_KEY env var)
#   4. Google Gemini image generation       (needs GEMINI_API_KEY env var)
#   5. DeepAI                               (needs DEEPAI_API_KEY env var)
#   6. Craiyon                              (free, no key)
#   ... (aur providers image_providers.py mein add karte hi yahan bhi try honge)
#   LAST: Local fallback pool (assets/fallback_images/*, random non-repeating)
#                                             - guaranteed final fallback
# ---------------------------------------------------------------------------

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


def _try_registry_provider(provider: dict, index: int, prompt: str, seed: int, scene_text: str) -> str:
    """Runs one provider from image_providers.PROVIDER_REGISTRY and saves
    the result to output/scene_{index}.{ext}. Raises on failure/rate-limit
    (image_providers functions already raise RuntimeError/RateLimitError)."""
    image_bytes, ext = provider["generate"](prompt, seed, scene_text)
    return _save_bytes(image_bytes, index, ext=ext)


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

    # Registry se sirf wo providers uthao jinke required env keys mojood hain
    # (no-key providers jaise Pollinations/Craiyon hamesha include hote hain).
    layers = [
        (p["name"], lambda p=p: _try_registry_provider(p, index, prompt, seed, scene_text))
        for p in available_providers()
    ]
    layers.append(("Placeholder", lambda: _layer5_placeholder(index, used_fallbacks)))

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

    logger.error(f"Scene {index}: ALL layers failed (tried {len(layers)}).")
    return {"index": index, "path": None, "success": False, "source": None}


def generate_images(scenes, max_workers=2):
    """
    Registry-driven fallback chain, executed per scene:
    every available provider from image_providers.PROVIDER_REGISTRY (in order)
    -> local fallback pool (assets/fallback_images/*) as guaranteed last resort.
    Returns a list of image paths (same order as `scenes`), skipping only
    scenes where literally every layer failed (which should be near-impossible
    as long as assets/placeholder.png or assets/fallback_images/ has content).
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
