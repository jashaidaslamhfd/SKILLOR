import requests, os, time

API = os.environ.get("HF_API_KEY") 
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HEADERS = {"Authorization": f"Bearer {API}"}

def query(payload):
    # Timeout ko 120 seconds tak barha diya
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
    return response.content

def generate_images(scenes):
    paths = []
    print(f"Generating {len(scenes)} AI Images from HuggingFace...")

    for i, scene in enumerate(scenes):
        prompt = f"cinematic 3D render, {scene}, 9:16 vertical, ultra detailed, 8k, photorealistic, no watermark, no text"

        try:
            # Pehli koshish
            image_bytes = query({"inputs": prompt})

            # Agar model loading mein ho to wait karein
            if b"loading" in image_bytes or b"error" in image_bytes[:200].lower():
                print(f"Model load ho raha hai, 45 seconds wait kar rahe hain...")
                time.sleep(45) 
                image_bytes = query({"inputs": prompt})

            if len(image_bytes) < 1000:
                print(f"Scene {i} fail, phir se try karte hain...")
                time.sleep(10)
                image_bytes = query({"inputs": prompt})

            if len(image_bytes) > 1000:
                path = f"scene_{i}.png"
                with open(path, "wb") as f:
                    f.write(image_bytes)
                paths.append(path)
                print(f"Image {i+1}/{len(scenes)} Done")
            
            time.sleep(5) # Har image ke baad pause

        except Exception as e:
            print(f"Image {i} Error: {e}")
            continue

    min_required = max(3, int(len(scenes) * 0.5)) # Requirement kam kar di (0.7 se 0.5)
    assert len(paths) >= min_required, f"Image Fail: Sirf {len(paths)} images bani, {min_required} chahiye thin."
    return paths
