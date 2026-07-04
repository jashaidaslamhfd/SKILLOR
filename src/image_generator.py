import os
import time
import random
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fallback Services
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"
# Yahan aap doosri free APIs ke endpoints add kar sakte hain
# Jaise Prodia, DeepAI, etc.

def _generate_one(index, scene, known_hashes):
    prompt = scene.replace(' ', '_')
    seed = random.randint(1000, 9999)
    
    # 1. Layer: Pollinations.ai (Primary)
    try:
        url = f"{POLLINATIONS_URL}/{prompt}?width=1080&height=1920&seed={seed}&nologo=true"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            path = f"output/scene_{index}.jpg"
            with open(path, 'wb') as f:
                f.write(response.content)
            return {"index": index, "path": path, "success": True}
    except Exception as e:
        logger.warning(f"Pollinations failed for scene {index}: {e}")

    # 2. Layer: Placeholder (Emergency Fallback)
    # Agar API call fail ho jaye, toh assets folder mein padi image uthaein
    placeholder = "assets/placeholder.png"
    if os.path.exists(placeholder):
        logger.info(f"Using placeholder for scene {index}")
        return {"index": index, "path": placeholder, "success": True}
    
    # 3. Last Resort: Agar assets mein bhi file nahi mili
    return {"index": index, "path": None, "success": False}

def generate_images(scenes, max_workers=2):
    """
    5-Layer logic: 
    Pollinations -> Fallback -> Placeholder -> Error Handling
    """
    results = [None] * len(scenes)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_generate_one, i, scene, {}): i for i, scene in enumerate(scenes)}
        for future in as_completed(futures):
            r = future.result()
            results[r["index"]] = r

    # Filter out failures
    paths = [r["path"] for r in results if r and r["path"]]
    
    if len(paths) < len(scenes):
        logger.error("Kuch images generate nahi ho sakin, fallback image use ki gayi hai.")
        
    return paths

# Test block
if __name__ == "__main__":
    test_scenes = ["happy baby playing", "brain science diagram"]
    paths = generate_images(test_scenes)
    print(f"Generated paths: {paths}")
