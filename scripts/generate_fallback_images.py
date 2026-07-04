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

Uses Pollinations.ai - same free, no-API-key service already used as
Layer 1/2 in image_generator.py - so no new signup/key needed at all.

Run from the repo root:
    python scripts/generate_fallback_images.py

Resumable: if you stop it and re-run, it keeps whatever was already
generated (checks how many files already exist) and continues from there.
"""

import os
import time
import random
import requests

OUTPUT_DIR = "assets/fallback_images"
TARGET_COUNT = 500
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
REQUEST_TIMEOUT = 30

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
    return f"{subject} {setting}, {style}".replace(" ", "_")


def already_have():
    if not os.path.isdir(OUTPUT_DIR):
        return 0
    return len([f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))])


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    count = already_have()
    print(f"Starting with {count} images already in {OUTPUT_DIR}")

    models = ["flux", "turbo"]  # alternate for extra variety
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 20

    while count < TARGET_COUNT:
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            print(f"\nStopping: {MAX_CONSECUTIVE_FAILURES} bad responses in a row - "
                  f"check your internet connection or Pollinations.ai status, then re-run "
                  f"(it will resume from {count}/{TARGET_COUNT}).")
            break

        prompt = build_prompt()
        seed = random.randint(1, 999999)
        model = models[count % 2]
        url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={seed}&model={model}&nologo=true"

        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            print(f"  ! request failed: {e} - retrying in 5s")
            consecutive_failures += 1
            time.sleep(5)
            continue

        if resp.status_code == 200 and len(resp.content) > 2000:
            fname = f"fallback_{count:04d}_{seed}.jpg"
            dest = os.path.join(OUTPUT_DIR, fname)
            with open(dest, "wb") as f:
                f.write(resp.content)
            count += 1
            consecutive_failures = 0
            print(f"  [{count}/{TARGET_COUNT}] saved {fname}  (prompt: {prompt})")
        elif resp.status_code == 429:
            print("Rate limited - waiting 30s...")
            time.sleep(30)
            continue
        else:
            print(f"  ! bad response {resp.status_code}, retrying with new prompt/seed")
            consecutive_failures += 1

        time.sleep(1)  # be polite to the free service, avoid hammering it

    print(f"\nDone. Total unique AI-generated fallback images: {count}")


if __name__ == "__main__":
    main()
