import requests, os
API = os.environ.get("LEONARDO_API_KEY")

def generate_images(scenes):
    paths = []
    for i, scene in enumerate(scenes):
        payload = {"prompt": f"3D render, scientific, baby brain, {scene}, 9:16, white background", "modelId": "leonardo-diffusion-xl"}
        r = requests.post("https://cloud.leonardo.ai/api/rest/v1/generations", json=payload, headers={"Authorization": f"Bearer {API}"})
        img_url = r.json()['generations'][0]['generated_images'][0]['url']
        path = f"scene_{i}.png"
        open(path, 'wb').write(requests.get(img_url).content)
        paths.append(path)
        time.sleep(2) # Rate limit safe
    return paths
