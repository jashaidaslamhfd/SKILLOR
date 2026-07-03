import os
import requests
import google.generativeai as genai

# API Keys
HF_API_KEY = os.environ.get("HF_API_KEY")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_with_huggingface(prompt):
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        if response.status_code == 200 and len(response.content) > 1000:
            return response.content
    except: pass
    return None

def generate_with_gemini(prompt):
    # Gemini 1.5 Flash text model hai, image generation ke liye 'imagen' use hota hai
    # Agar error aaye to hum None return kar rahe hain taake crash na ho
    print("Gemini image generation feature is currently unstable/unavailable for this account.")
    return None

def generate_images(scenes):
    paths = []
    print(f"Generating {len(scenes)} images...")

    for i, scene in enumerate(scenes):
        prompt = f"Cinematic 3D render, {scene}, high quality, photorealistic, 9:16 vertical"
        
        # Pehle HF try karo
        img_bytes = generate_with_huggingface(prompt)
        
        if img_bytes:
            path = f"scene_{i}.png"
            with open(path, "wb") as f:
                f.write(img_bytes)
            paths.append(path)
        else:
            print(f"Scene {i+1} generate nahi ho saka.")
            
    return paths
