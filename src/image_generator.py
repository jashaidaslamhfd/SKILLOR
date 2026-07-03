import os
import google.generativeai as genai

# API key configure karein
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def generate_images(scenes):
    paths = []
    # Imagen 3 model ka istemal
    model = genai.GenerativeModel('imagen-3.0-generate-001')

    print(f"Generating {len(scenes)} images via Gemini...")

    for i, scene in enumerate(scenes):
        try:
            # Prompt ko mazeed behtar banaya taake YouTube par reused content na aaye
            prompt = f"Cinematic, highly detailed, photorealistic, 8k, {scene}, vertical aspect ratio 9:16"
            
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1
            )
            
            # Result save karein
            for image in result.generated_images:
                path = f"scene_{i}.png"
                with open(path, "wb") as f:
                    f.write(image.image.image_bytes)
                paths.append(path)
                print(f"Scene {i+1} saved successfully.")
                
        except Exception as e:
            print(f"Gemini Error on scene {i}: {e}")
            # Fallback: Agar error aaye toh koi purani image copy kar lein
            # taake script crash na ho (optional)
            continue
            
    return paths
