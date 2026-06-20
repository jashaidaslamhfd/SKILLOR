"""Footage Fetcher — Topic-relevant clips per segment, Human/Brain Mystery niche"""

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

        # FIX: previously these generic queries never included the actual
        # video topic at all — "fetch_footage_for_script" received a
        # `topic` argument but silently ignored it, so a "dreams"/"sleep"
        # video could get totally unrelated footage (e.g. a Holi color
        # festival crowd) just because the segment type was "story". These
        # are now used only as a STYLE/mood modifier appended to the real
        # topic-based query, never as the query on their own.
        self.mood_modifiers = {
            'hook': ["cinematic dramatic", "close up mysterious", "dark moody atmosphere"],
            'suspense': ["suspenseful tense", "dramatic shadow", "eerie atmosphere"],
            'story': ["scientific close up", "macro detail", "documentary style"],
            'ctr': ["dramatic reveal", "close up emotional", "bright realization"],
        }

        # Only used if the topic itself yields zero usable results from
        # either provider — generic but at least on-niche (human body/brain
        # mystery), never random crowd/lifestyle stock footage.
        self.fallback_queries = [
            "human brain neurons glowing",
            "person sleeping bedroom night",
            "brain scan medical close up",
            "person thinking deep thought",
            "abstract neural network dark",
        ]

    def _topic_to_query(self, topic: str, seg_type: str, seg_idx: int) -> str:
        """
        FIX: build the actual search query FROM the topic, with a small
        mood modifier for variety per segment — instead of ignoring the
        topic and pulling from a fixed unrelated-query pool.
        """
        # Strip filler words that hurt stock-footage search relevance
        stopwords = {'why', 'do', 'we', 'does', 'the', 'a', 'an', 'is', 'are', 'happens', 'happen'}
        words = [w for w in topic.lower().split() if w not in stopwords]
        core_topic = ' '.join(words) if words else topic

        modifiers = self.mood_modifiers.get(seg_type, self.mood_modifiers['story'])
        modifier = modifiers[seg_idx % len(modifiers)]

        return f"{core_topic} {modifier}".strip()

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
        FIX: every query is now built FROM the actual topic so footage
        is relevant to what's being narrated, instead of a fixed pool of
        generic queries that ignored `topic` entirely.
        """
        clips = []
        used_ids = set()  # Within this video, no duplicate clips

        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')
            query = self._topic_to_query(topic, seg_type, i)

            print(f"    🎬 Seg {i} ({seg_type}): searching '{query}'")

            videos = self.search_pexels(query, per_page=15)
            if not videos:
                videos = self.search_pixabay(query, per_page=15)

            # FIX: if the topic-specific query returns nothing, fall back
            # to a generic but still ON-NICHE query (brain/sleep/thinking)
            # instead of leaving the segment with no footage at all.
            if not videos:
                fallback_q = self.fallback_queries[i % len(self.fallback_queries)]
                print(f"    ⚠️ No results for topic query, trying fallback: '{fallback_q}'")
                videos = self.search_pexels(fallback_q, per_page=15)
                if not videos:
                    videos = self.search_pixabay(fallback_q, per_page=15)

            fresh = [v for v in videos if v.get('id') not in used_ids]
            if not fresh:
                fresh = videos

            if fresh:
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
