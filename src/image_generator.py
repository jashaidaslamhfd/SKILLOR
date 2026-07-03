import requests, os, time

API = os.environ.get("HF_API_KEY") # GitHub Secret wala naam
# HuggingFace ne api-inference.huggingface.co retire kar diya hai (July 2025).
# Naya endpoint router.huggingface.co hai, aur model bhi FLUX.1-schnell mein
# switch kiya hai kyunki SDXL jaise heavy models ab CPU-focused free tier
# (hf-inference) par unreliable/slow ho sakte hain.
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HEADERS = {"Authorization": f"Bearer {API}"}

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    return response.content # Direct image bytes mil jati hain

def generate_images(scenes):
    paths = []
    print(f"Generating {len(scenes)} AI Images from HuggingFace...")

    for i, scene in enumerate(scenes):
        # PROMPT = Anti-Spam + Unique. Pexels jesa kuch nahi.
        prompt = f"cinematic 3D render, {scene}, 9:16 vertical, ultra detailed, 8k, photorealistic, no watermark, no text"

        try:
            image_bytes = query({"inputs": prompt})

            # Agar model loading ho raha ho to 20 sec wait karega
            if b"loading" in image_bytes or b"error" in image_bytes[:200].lower():
                print(f"Scene {i} response abnormal lagi, 20 sec wait karke retry...")
                time.sleep(20)
                image_bytes = query({"inputs": prompt})

            # Sanity check: agar bytes bohot chhote hain to woh image nahi, error JSON hai
            if len(image_bytes) < 1000:
                raise ValueError(f"Response valid image nahi lagti: {image_bytes[:200]}")

            path = f"scene_{i}.png"
            with open(path, "wb") as f:
                f.write(image_bytes)
            paths.append(path)
            print(f"Image {i+1}/{len(scenes)} Done")
            time.sleep(3) # Rate limit se bachne ke liye. Zaroori hai.

        except Exception as e:
            print(f"Image {i} Fail: {e}")
            # Fail hua to bot rukega nahi. Khali jagah skip.
            continue

    assert len(paths) >= 8, "Image Fail: Kam se kam 8 images chahiye Anti-Spam ke liye"
    return paths
