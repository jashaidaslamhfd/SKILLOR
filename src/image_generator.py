import requests, os, time

API = os.environ.get("HF_API_KEY") # GitHub Secret wala naam
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API}"}

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.content # Direct image bytes mil jati hain

def generate_images(scenes):
    paths = []
    print(f"Generating {len(scenes)} AI Images from HuggingFace...")
    
    for i, scene in enumerate(scenes):
        # PROMPT = Anti-Spam + Unique. Pexels jesa kuch nahi.
        # Niche-specific hardcoding hata di, ab har topic ke liye generic/cinematic prompt banega.
        prompt = f"cinematic 3D render, {scene}, 9:16 vertical, ultra detailed, 8k, photorealistic, no watermark, no text"
        
        try:
            image_bytes = query({"inputs": prompt})
            
            # Agar model loading ho raha ho to 20 sec wait karega
            if b"loading" in image_bytes:
                print("Model loading... 20 sec wait")
                time.sleep(20)
                image_bytes = query({"inputs": prompt})

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
