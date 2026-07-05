"""
generate_fallback_images.py
-----------------------------
One-time helper to bulk-generate ~500 UNIQUE AI images for the
assets/fallback_images/ pool (parenting / baby-health niche).

Why AI-generated instead of stock photos (Pexels/Pixabay/etc.)?
Stock photos are used by thousands of other creators, so platforms
(YouTube/Facebook/TikTok) can flag them as "reused/rescued content".
AI-generated images with random seeds are effectively one-of-a-kind,
so this risk goes away.

IMPORTANT (why this matters right now): if this pool is empty/missing,
image_generator.py's final fallback layer has nothing to pick from and
silently reuses the single static assets/placeholder.png for EVERY
scene of EVERY video whenever the live AI providers are rate-limited —
which is exactly what tanks a channel's content-quality signals. Run
this script (or the GitHub Action version of it) to populate the pool
BEFORE that happens, not after.

Uses the SAME shared provider registry as src/image_generator.py
(src/image_providers.py) — so it rotates across every provider you have
configured (Pollinations flux/turbo, Hugging Face, Gemini, DeepAI,
Craiyon, and anything else you add later), instead of getting stuck
when just one provider (usually Pollinations) is rate-limited.

Run from the repo root:
    python scripts/generate_fallback_images.py

Resumable: if you stop it and re-run, it keeps whatever was already
generated (checks how many files already exist) and continues from there.
"""

import os
import sys
import time
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from image_providers import PROVIDER_REGISTRY, available_providers, RateLimitError

OUTPUT_DIR = "assets/fallback_images"
TARGET_COUNT = 500

# Building blocks combined randomly to maximize visual variety across the
# 500 images - subject x setting x style, so no two prompts are identical.
SUBJECTS = [
    "newborn baby", "smiling toddler", "mother holding her baby",
    "father playing with his baby", "pregnant woman", "baby crawling",
    "baby sleeping peacefully", "toddler taking first steps",
    "baby being breastfed", "parents feeding a baby", "baby in a bath",
    "baby playing with toys", "happy family with a newborn",
    "baby getting a health checkup", "twin babies", "baby laughing",
    "baby reaching for a toy", "mother reading to her toddler",
    "baby held by grandparents", "child playing outdoors with parents",
]

SETTINGS = [
    "in a cozy nursery", "in a sunny living room", "in a hospital room",
    "in a garden", "on a soft blanket on the floor", "in a baby stroller",
    "at home near a window with warm light", "in a bedroom",
    "on a picnic outdoors", "in a pediatrician's office",
    "in a kitchen during feeding time", "at a park",
]

STYLES = [
    "warm natural lighting, photorealistic",
    "soft pastel tones, photorealistic",
    "candid lifestyle photography style",
    "bright and cheerful, photorealistic",
    "gentle morning light, photorealistic",
    "cinematic soft focus, photorealistic",
]


def build_prompt():
    subject = random.choice(SUBJECTS)
    setting = random.choice(SETTINGS)
    style = random.choice(STYLES)
    scene_text = f"{subject} {setting}, {style}"
    return scene_text.replace(" ", "_"), scene_text


def already_have():
    if not os.path.isdir(OUTPUT_DIR):
        return 0
    return len([f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))])


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    count = already_have()
    print(f"Starting with {count} images already in {OUTPUT_DIR}")

    providers = available_providers()
    if not providers:
        print("❌ No providers available at all (this shouldn't happen — "
              "Pollinations/Craiyon need no keys). Check your network/imports.")
        return

    print(f"Using {len(providers)} available provider(s), in rotation: "
          + ", ".join(p["name"] for p in providers))

    provider_idx = 0
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 40  # higher than before since we now rotate across many providers

    while count < TARGET_COUNT:
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            print(f"\nStopping: {MAX_CONSECUTIVE_FAILURES} bad responses in a row across "
                  f"ALL providers - check your internet connection / provider status, "
                  f"then re-run (it will resume from {count}/{TARGET_COUNT}).")
            break

        # Round-robin across every available provider, so one rate-limited
        # provider doesn't stall the whole run — the next attempt just uses
        # a different provider instead of waiting on the same one.
        provider = providers[provider_idx % len(providers)]
        provider_idx += 1

        prompt, scene_text = build_prompt()
        seed = random.randint(1, 999999)

        try:
            image_bytes, ext = provider["generate"](prompt, seed, scene_text)
        except RateLimitError as e:
            print(f"  ⚠️ {provider['name']} rate-limited: {e} — trying next provider")
            consecutive_failures += 1
            continue
        except Exception as e:
            print(f"  ❌ {provider['name']} failed: {e} — trying next provider")
            consecutive_failures += 1
            continue

        fname = f"fallback_{count:04d}_{seed}.{ext}"
        dest = os.path.join(OUTPUT_DIR, fname)
        with open(dest, "wb") as f:
            f.write(image_bytes)
        count += 1
        consecutive_failures = 0
        print(f"  [{count}/{TARGET_COUNT}] saved {fname} via {provider['name']} (prompt: {scene_text})")

        time.sleep(1)  # be polite to free services, avoid hammering them

    print(f"\nDone. Total unique AI-generated fallback images: {count}")
    if count < TARGET_COUNT:
        print(f"⚠️ Only reached {count}/{TARGET_COUNT} — re-run later when providers "
              f"have reset quotas (daily/monthly), it will resume from here.")


if __name__ == "__main__":
    main()

