"""Footage Fetcher — Varied clips per video, Dark Psychology queries"""

import requests
import os
import random
import hashlib
from typing import List, Dict
from config.settings import API_KEYS


class FootageFetcher:
    def __init__(self):
        self.pexels_key = API_KEYS.PEXELS_API_KEY
        self.pixabay_key = API_KEYS.PIXABAY_API_KEY
        self.pexels_base = "https://api.pexels.com/videos"
        self.pixabay_base = "https://pixabay.com/api/videos"

        # FIX 3: Dark psychology themed clip pools
        # Multiple query variations taake har video mein different clips aayein
        self.dark_queries = {
            'hook': [
                "dark shadow person walking alone night",
                "mysterious eye close up dramatic",
                "brain scan glowing neural activity",
                "silhouette man dark room thinking",
                "hypnotic spiral motion abstract dark",
                "crowd manipulation psychology",
            ],
            'suspense': [
                "shadow figure suspense thriller",
                "clock ticking countdown dark",
                "storm dark clouds dramatic sky",
                "locked door secret hallway",
                "dark forest fog mystery",
                "surveillance camera watching people",
            ],
            'story': [
                "human brain neurons firing close up",
                "psychology experiment lab",
                "crowd people mind control influence",
                "person thinking alone deep thought",
                "data visualization network connections",
                "ancient manuscript secret symbols",
                "scientist researcher laboratory dark",
            ],
            'ctr': [
                "person shocked surprised revelation",
                "light bulb idea moment dramatic",
                "unlock door reveal secret",
                "dramatic close up human eye",
                "explosion of knowledge concept",
            ]
        }

    def _get_used_clips_log(self, output_dir: str) -> set:
        """Track which clip URLs were used before — avoid repeats"""
        log_path = os.path.join(output_dir, ".used_clips.txt")
        used = set()
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                used = set(line.strip() for line in f if line.strip())
        return used

    def _save_used_clip(self, output_dir: str, url: str):
        log_path = os.path.join(output_dir, ".used_clips.txt")
        # Keep only last 200 entries
        existing = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                existing = [l.strip() for l in f if l.strip()]
        existing.append(url)
        existing = existing[-200:]
        with open(log_path, 'w') as f:
            f.write('\n'.join(existing))

    def search_pexels(self, query: str, per_page: int = 15) -> List[Dict]:
        if not self.pexels_key:
            return []
        headers = {"Authorization": self.pexels_key}
        # FIX 3: Random page offset — different results each run
        page = random.randint(1, 3)
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "portrait",
            "size": "large"
        }
        try:
            response = requests.get(f"{self.pexels_base}/search", headers=headers, params=params, timeout=10)
            data = response.json()
            videos = []
            for video in data.get('videos', []):
                best_file = None
                for file in video.get('video_files', []):
                    if file.get('height', 0) >= 1280:
                        best_file = file
                        break
                if not best_file and video.get('video_files'):
                    best_file = video['video_files'][0]
                if best_file:
                    videos.append({
                        'url': best_file['link'],
                        'duration': video.get('duration', 15),
                        'source': 'pexels',
                        'id': str(video.get('id', ''))
                    })
            return videos
        except Exception as e:
            print(f"    Pexels error: {e}")
            return []

    def search_pixabay(self, query: str, per_page: int = 15) -> List[Dict]:
        if not self.pixabay_key:
            return []
        page = random.randint(1, 3)
        params = {
            "key": self.pixabay_key,
            "q": query,
            "per_page": per_page,
            "page": page,
            "orientation": "vertical",
            "video_type": "film"
        }
        try:
            response = requests.get(f"{self.pixabay_base}/", params=params, timeout=10)
            data = response.json()
            videos = []
            for hit in data.get('hits', []):
                url = hit.get('videos', {}).get('large', {}).get('url', '')
                if url:
                    videos.append({
                        'url': url,
                        'duration': hit.get('duration', 15),
                        'source': 'pixabay',
                        'id': str(hit.get('id', ''))
                    })
            return videos
        except Exception as e:
            print(f"    Pixabay error: {e}")
            return []

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        """
        FIX 3: Each segment gets a DIFFERENT clip query + random page
        so clips vary every video run.
        """
        clips = []
        used_ids = set()  # Within this video, no duplicate clips

        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')

            # FIX 3: Pick a random query from the pool for this seg type
            query_pool = self.dark_queries.get(seg_type, self.dark_queries['story'])
            # Use segment index to rotate through pool (not pure random — ensures variety)
            query = query_pool[i % len(query_pool)]

            print(f"    🎬 Seg {i} ({seg_type}): searching '{query}'")

            # Try Pexels first, then Pixabay
            videos = self.search_pexels(query, per_page=15)
            if not videos:
                videos = self.search_pixabay(query, per_page=15)

            # FIX 3: Filter out clips already used in this video
            fresh = [v for v in videos if v.get('id') not in used_ids]
            if not fresh:
                fresh = videos  # Fallback if all used

            if fresh:
                # FIX 3: Shuffle and pick — different each time
                random.shuffle(fresh)
                video = fresh[0]
                used_ids.add(video.get('id', ''))

                clips.append({
                    'url': video['url'],
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': video['source'],
                    'id': video.get('id', '')
                })
                print(f"    ✅ Found clip from {video['source']}")
            else:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                print(f"    ⚠️ No clip found, using color bg")

        return clips

    def download_footage(self, clips: List[Dict], output_dir: str) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)

        # FIX 3: Clear old clips before downloading new ones
        # Taake purane clips reuse na hon
        for f in os.listdir(output_dir):
            if f.startswith('clip_') and f.endswith('.mp4'):
                try:
                    os.remove(os.path.join(output_dir, f))
                except:
                    pass

        downloaded = []
        for i, clip in enumerate(clips):
            if not clip.get('url'):
                print(f"  ⚠️ Clip {i}: no URL, using color bg")
                continue

            filepath = os.path.join(output_dir, f"clip_{i}.mp4")
            try:
                print(f"  ⬇️ Clip {i} ({clip['source']})...")
                response = requests.get(clip['url'], stream=True, timeout=30)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=65536):
                        f.write(chunk)

                if os.path.getsize(filepath) > 10000:
                    downloaded.append(filepath)
                    print(f"  ✅ Clip {i}: {os.path.getsize(filepath)//1024}KB")
                else:
                    os.remove(filepath)
                    print(f"  ⚠️ Clip {i}: too small")
            except Exception as e:
                print(f"  ❌ Clip {i}: {e}")

        return downloaded
