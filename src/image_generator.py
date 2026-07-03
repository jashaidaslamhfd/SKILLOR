import os
import requests
import time

# Hugging Face API
HF_API_KEY = os.environ.get("HF_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

def generate_images(scenes):
    paths = []
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    for i, scene in enumerate(scenes):
        prompt = f"Cinematic 3D render, {scene}, high quality, photorealistic, 9:16 vertical"
        
        # Hugging Face call
        try:
            response = requests.post(HF_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            
            if response.status_code == 200:
                path = f"scene_{i}.png"
                with open(path, "wb") as f:
                    f.write(response.content)
                paths.append(path)
                print(f"Scene {i+1} saved!")
            else:
                print(f"HF Error Scene {i+1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception in Scene {i+1}: {e}")
            
        time.sleep(2) # API rate limit se bachne ke liye
            
    return paths
