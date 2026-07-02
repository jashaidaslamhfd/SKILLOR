import os
import requests
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

os.makedirs("temp/footage", exist_ok=True)

def fetch_from_pexels(query, per_page=15):
    """Pexels se high quality vertical videos"""
    try:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "portrait", # Shorts ke liye
            "size": "medium"
        }
        res = requests.get(url, headers=headers, params=params, timeout=10)
        videos = res.json().get("videos", [])

        valid_urls = []
        for v in videos:
            # 1080x1920 ya 720x1280 wala dhundo
            for file in v["video_files"]:
                if file["height"] >= 1280 and file["width"] <= file["height"]:
                    valid_urls.append(file["link"])
                    break
        return valid_urls
    except Exception as e:
        print(f"[Footage] Pexels error: {e}")
        return []

def fetch_from_pixabay(query):
    """Fallback - Pixabay free hai"""
    try:
        url = "https://pixabay.com/api/videos/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": query,
            "video_type": "film",
            "per_page": 15
        }
        res = requests.get(url, params=params, timeout=10)
        hits = res.json().get("hits", [])
        return [v["videos"]["medium"]["url"] for v in hits if v["videos"].get("medium")]
    except Exception as e:
        print(f"[Footage] Pixabay error: {e}")
        return []

def download_clip(url, idx):
    """Single clip download with retry"""
    path = f"temp/footage/clip_{idx}.mp4"
    for attempt in range(2):
        try:
            r = requests.get(url, stream=True, timeout=15)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            # Check if valid
            clip = VideoFileClip(path)
            if clip.duration > 1:
                clip.close()
                return path
            clip.close()
        except:
            continue
    return None

def fetch_stock_footage(niche, search_terms, duration_needed=30):
    """
    Swap Rate Fix: Har 0.8-1.2 sec ka clip dega
    Total 30 sec ke liye 25-35 clips download karega
    """
    print(f"[Footage] Searching: {search_terms}")

    all_urls = []

    # 1. Har search term ke liye footage lao
    for term in search_terms[:3]: # 3 terms max
        urls = fetch_from_pexels(term)
        if not urls:
            urls = fetch_from_pixabay(term) # Fallback
        all_urls.extend(urls[:5]) # Har term se 5 clips

    if not all_urls:
        # Last fallback: niche based generic
        fallback_terms = {
            'mystery': 'dark fog night',
            'science': 'space technology abstract',
            'human_behaviour': 'people city lifestyle'
        }
        all_urls = fetch_from_pexels(fallback_terms.get(niche, 'abstract'))
        if not all_urls:
            raise Exception("No footage found anywhere")

    # 2. Random shuffle + download 30-35 clips
    random.shuffle(all_urls)
    clips = []
    total_duration = 0
    target_clips = 35 # Swap rate fix: zyada cuts

    for idx, url in enumerate(all_urls[:target_clips]):
        path = download_clip(url, idx)
        if not path:
            continue

        try:
            clip = VideoFileClip(path)
            # BUG FIX: Har clip ko 0.8-1.2 sec kaat do
            clip_duration = min(clip.duration, random.uniform(0.8, 1.2))
            clip = clip.subclip(0, clip_duration)

            # Vertical crop agar needed
            if clip.w > clip.h:
                clip = clip.crop(x_center=clip.w/2, width=clip.h*9/16)

            clips.append(clip)
            total_duration += clip_duration
            print(f"[Footage] Clip {len(clips)}: {clip_duration:.1f}s")

            if total_duration >= duration_needed:
                break

        except Exception as e:
            print(f"[Footage] Clip error: {e}")
            continue

    if not clips:
        raise Exception("All clips failed to process")

    # 3. Fast cuts ke saath jod do
    print(f"[Footage] ✅ Total: {len(clips)} clips, {total_duration:.1f}s")
    final = concatenate_videoclips(clips, method="compose")

    output_path = "temp/footage/final_footage.mp4"
    final.write_videofile(output_path, fps=30, logger=None, threads=4)
    final.close()

    # Cleanup
    for clip in clips:
        clip.close()

    return output_path
