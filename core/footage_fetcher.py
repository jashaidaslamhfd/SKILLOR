"""Footage Fetcher — Semantic Query Mapping + Cross-Run De-duplication"""

import requests
import os
import random
from typing import List, Dict
from config.settings import API_KEYS


class FootageFetcher:
    def __init__(self):
        self.pexels_key = API_KEYS.PEXELS_API_KEY
        self.pixabay_key = API_KEYS.PIXABAY_API_KEY
        self.pexels_base = "https://api.pexels.com/videos"
        self.pixabay_base = "https://pixabay.com/api/videos"

        # Dark psychology themed clip pools — Expanded variant seeds
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
        """Track which clip IDs were used before across workflows"""
        log_path = os.path.join(output_dir, ".used_clips.txt")
        used = set()
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                used = set(line.strip() for line in f if line.strip())
        return used

    def _save_used_clip(self, output_dir: str, clip_id: str):
        log_path = os.path.join(output_dir, ".used_clips.txt")
        existing = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                existing = [l.strip() for l in f if l.strip()]
        if clip_id not in existing:
            existing.append(clip_id)
        # Keep only the last 300 entries to prevent tracking overflow bloating
        existing = existing[-300:]
        with open(log_path, 'w') as f:
            f.write('\n'.join(existing))

    def search_pexels(self, query: str, per_page: int = 15) -> List[Dict]:
        if not self.pexels_key:
            return []
        headers = {"Authorization": self.pexels_key}
        page = random.randint(1, 4)
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "portrait",
            "size": "large"
        }
        try:
            response = requests.get(f"{self.pexels_base}/search", headers=headers, params=params, timeout=12)
            if response.status_code != 200:
                return []
            data = response.json()
            videos = []
            for video in data.get('videos', []):
                best_file = None
                # Filter out landscape formats or fetch HD definitions cleanly
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
                        'id': f"pexels_{video.get('id', '')}"
                    })
            return videos
        except Exception as e:
            print(f"    ⚠️ Pexels retrieval bypass: {e}")
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
            response = requests.get(f"{self.pixabay_base}/", params=params, timeout=12)
            if response.status_code != 200:
                return []
            data = response.json()
            videos = []
            for hit in data.get('hits', []):
                url = hit.get('videos', {}).get('large', {}).get('url', '')
                if not url:
                    url = hit.get('videos', {}).get('medium', {}).get('url', '')
                if url:
                    videos.append({
                        'url': url,
                        'duration': hit.get('duration', 15),
                        'source': 'pixabay',
                        'id': f"pixabay_{hit.get('id', '')}"
                    })
            return videos
        except Exception as e:
            print(f"    ⚠️ Pixabay retrieval bypass: {e}")
            return []

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        """Maps out structural variations checking persistence logs to maintain variety"""
        clips = []
        used_within_video = set()
        
        # Ensure context output directory mapping safely mirrors setup bounds
        base_output_dir = "output"
        cross_run_used = self._get_used_clips_log(base_output_dir)

        # Inject topic keywords directly into search variations matrix safely
        topic_keywords = [w.lower() for w in topic.split() if len(w) > 3]

        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')
            query_pool = self.dark_queries.get(seg_type, self.dark_queries['story'])
            
            # Form dynamic semantic combinations based on raw trending contextual queries
            base_query = query_pool[i % len(query_pool)]
            if topic_keywords and random.random() > 0.4:
                query = f"{random.choice(topic_keywords)} {base_query}"
                if len(query) > 50: 
                    query = base_query
            else:
                query = base_query

            print(f"    🎬 Segment {i} ({seg_type}): Resolving engine query -> '{query}'")

            videos = self.search_pexels(query, per_page=15)
            if not videos:
                videos = self.search_pixabay(query, per_page=15)

            # De-duplication filtration check (Current compilation run vs History records)
            fresh = [v for v in videos if v['id'] not in used_within_video and v['id'] not in cross_run_used]
            if not fresh:
                fresh = [v for v in videos if v['id'] not in used_within_video]
            if not fresh:
                fresh = videos  # Ultimate structural fallback

            if fresh:
                random.shuffle(fresh)
                selected_video = fresh[0]
                
                used_within_video.add(selected_video['id'])
                self._save_used_clip(base_output_dir, selected_video['id'])

                clips.append({
                    'url': selected_video['url'],
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': selected_video['source'],
                    'id': selected_video['id']
                })
                print(f"      ✅ Selected Asset ID: {selected_video['id']} [{selected_video['source']}]")
            else:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': 'fallback'
                })
                print(f"      ⚠️ Zero inventory found for query framework. Enforcing backend color fallback.")

        return clips

    def download_footage(self, clips: List[Dict], output_dir: str) -> List[str]:
        """Downloads assets while preserving strict indexed structural indices for assembler alignment"""
        os.makedirs(output_dir, exist_ok=True)

        # Clean deployment directory layout bounds
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                if f.startswith('clip_') and f.endswith('.mp4'):
                    try:
                        os.remove(os.path.join(output_dir, f))
                    except:
                        pass

        downloaded_paths = []
        
        # FIX: Loop mapping tracks actual output indexes instead of raw compress array appends
        for i, clip in enumerate(clips):
            if not clip.get('url'):
                print(f"    ⚠️ Asset Index {i}: Flagged as Null URL stream. Initializing dynamic generator canvas pipeline context.")
                continue

            target_filename = f"clip_{i}.mp4"
            filepath = os.path.join(output_dir, target_filename)
            
            try:
                print(f"    📥 Fetching Stream Asset [{i}] -> Source: {clip['source']}...")
                response = requests.get(clip['url'], stream=True, timeout=35)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=131072): # Balanced buffer chunks for pipeline
                        if chunk:
                            f.write(chunk)

                if os.path.exists(filepath) and os.path.getsize(filepath) > 15000:
                    downloaded_paths.append(filepath)
                    print(f"      💎 Asset {i} successfully stored -> {os.path.getsize(filepath) // 1024} KB")
                else:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    print(f"      ⚠️ Corrupt tracking payload signature on Asset {i}. Cleaned from local space boundaries.")
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                print(f"      ❌ Network processing timeout on tracking target asset {i}: {e}")

        return downloaded_paths
