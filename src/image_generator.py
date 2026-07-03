import os
import time
import shutil
import requests

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

# PRIORITY 3 (last resort): local placeholder image, taake image count
# hamesha scene count ke barabar rahe (index/caption misalignment na ho)
PLACEHOLDER = "assets/placeholder.png"


def _try_gemini(prompt: str, path: str) -> bool:
    if not GEMINI_API_KEY:
        return False
    try:
        from google import genai
        from google.genai import types

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
                return True
        print("Gemini ne image return nahi ki (empty response, shayad safety filter)")
        return False
    except Exception as e:
        print(f"Gemini error: {e}")
        return False


def _try_huggingface(prompt: str, path: str, retries: int = 2) -> bool:
    if not HF_API_KEY:
        return False
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                HF_URL, headers=headers, json={"inputs": prompt}, timeout=60
            )
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                return True
            elif response.status_code == 503:
                wait = 10 * attempt
                print(f"HF model load ho raha hai, {wait}s wait kar rahe hain (attempt {attempt}/{retries})")
                time.sleep(wait)
                continue
            else:
                print(f"HF Error: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            print(f"HF exception: {e}")
            time.sleep(3)
    return False


def generate_images(scenes):
    """
    Har scene ke liye:
      1. Pehle Google Gemini (Nano Banana) try hota hai — first priority
      2. Fail ho to Hugging Face FLUX.1-schnell fallback
      3. Dono fail ho to local placeholder image copy hoti hai

    Return list HAMESHA len(scenes) ke barabar hogi, taake video_editor.py
    mein caption <-> image index kabhi bhi misalign na ho.
    """
    paths = []

    for i, scene in enumerate(scenes):
        prompt = (
            f"Cinematic 3D render, {scene}, high quality, photorealistic, "
            f"vertical 9:16 shorts frame, dramatic lighting"
        )
        path = f"scene_{i}.png"
        success = _try_gemini(prompt, path)
        source = "Gemini"

        if not success:
            success = _try_huggingface(prompt, path)
            source = "Hugging Face (fallback)"

        if not success:
            source = "Placeholder (dono APIs fail)"
            if os.path.exists(PLACEHOLDER):
                shutil.copy(PLACEHOLDER, path)
                success = True
            else:
                print(f"WARNING: Scene {i+1} skip ho rahi hai — placeholder image bhi missing hai ({PLACEHOLDER})")

        if success:
            paths.append(path)
            print(f"Scene {i+1}/{len(scenes)} ban gayi ✅ [{source}]")

        time.sleep(1)  # rate limit se bachne ke liye

    return paths
