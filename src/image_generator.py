import os
import requests
import google.generativeai as genai

# Setup
HF_API_KEY = os.environ.get("HF_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_with_huggingface(prompt):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
    if response.status_code == 200 and len(response.content) > 1000:
        return response.content
    return None

def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel('imagen-3.0-generate-001')
        result = model.generate_images(prompt=prompt, number_of_images=1)
        for image in result.generated_images:
            return image.image.image_bytes
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def generate_images(scenes):
    paths = []
    print(f"Generating {len(scenes)} images with Fallback logic...")

    for i, scene in enumerate(scenes):
        prompt = f"Cinematic 3D render, {scene}, high quality, photorealistic, 9:16 vertical"
        img_bytes = None
        
        # 1. Pehle HuggingFace Try Karo
        img_bytes = generate_with_huggingface(prompt)
        
        # 2. Agar HF fail ho, toh Gemini Try Karo
        if not img_bytes:
            print(f"HuggingFace fail, using Gemini fallback for scene {i+1}...")
            img_bytes = generate_with_gemini(prompt)
            
        # 3. Agar dono fail ho jayein (Rare), toh script handle kare
        if img_bytes:
            path = f"scene_{i}.png"
            with open(path, "wb") as f:
                f.write(img_bytes)
            paths.append(path)
            print(f"Image {i+1} saved.")
        else:
            print(f"CRITICAL: Scene {i+1} generate nahi ho saka.")

    return paths
