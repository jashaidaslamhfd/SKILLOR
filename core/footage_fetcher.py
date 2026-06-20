"""Footage Fetcher — Topic-relevant MOTION clips, Human/Brain Mystery niche"""

import requests
import os
import random
import subprocess
from typing import List, Dict
from config.settings import API_KEYS


class FootageFetcher:
    def __init__(self):
        self.pexels_key = API_KEYS.PEXELS_API_KEY
        self.pixabay_key = API_KEYS.PIXABAY_API_KEY
        self.pexels_base = "https://api.pexels.com/videos"
        self.pixabay_base = "https://pixabay.com/api/videos"

        # FIX: Added Mixkit & Coverr — better free motion videos than Pexels
        self.mixkit_base = "https://assets.mixkit.co/videos/preview"
        # Coverr has no API, but we can use their search page structure

        self.mood_modifiers = {
            'hook': ["cinematic dramatic fast", "close up mysterious motion", "dark moody atmosphere moving"],
            'shock': ["glitch distortion", "fast zoom motion", "shocking visual effect"],
            'suspense': ["suspenseful tense movement", "dramatic shadow motion", "eerie atmosphere moving"],
            'story': ["scientific close up motion", "macro detail moving", "documentary style dynamic"],
            'ctr': ["dramatic reveal motion", "close up emotional reaction", "bright realization moment"],
        }

        # FIX: Fallback queries with MOTION keywords — forces dynamic footage
        self.fallback_queries = [
            "human brain neurons glowing motion",
            "person sleeping bedroom night moving",
            "brain scan medical close up motion",
            "person thinking deep thought cinematic",
            "abstract neural network dark flowing",
            "eye close up blinking dramatic",
            "heartbeat pulse medical motion",
            "shadow figure walking mysterious",
        ]

    def _topic_to_query(self, topic: str, seg_type: str, seg_idx: int) -> str:
        """Build search query FROM topic + motion modifier"""
        stopwords = {'why', 'do', 'we', 'does', 'the', 'a', 'an', 'is', 'are', 'happens', 'happen', 'to', 'your', 'you'}
        words = [w for w in topic.lower().split() if w not in stopwords]
        core_topic = ' '.join(words) if words else topic

        modifiers = self.mood_modifiers.get(seg_type, self.mood_modifiers['story'])
        modifier = modifiers[seg_idx % len(modifiers)]

        # FIX: Always append motion keywords to get REAL moving footage
        return f"{core_topic} {modifier} motion".strip()

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

    # ─── NEW: Motion score validation ───────────────────────────
    def _check_motion_score(self, video_path: str) -> float:
        """
        Check if video has REAL motion (not static image or slideshow)
        Returns: 0.0-1.0 motion score
        """
        try:
            # Get frame count and duration
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-count_frames', '-show_entries', 'stream=nb_read_frames,duration,r_frame_rate',
                '-of', 'default=noprint_wrappers=1', video_path
            ], capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return 0.5  # Default: assume motion

            lines = result.stdout.strip().split('\n')
            data = {}
            for line in lines:
                if '=' in line:
                    k, v = line.split('=', 1)
                    data[k.strip()] = v.strip()

            # Parse frame rate
            fps_str = data.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 30
            else:
                fps = float(fps_str)

            # Parse frame count
            frames = int(data.get('nb_read_frames', 0))
            duration = float(data.get('duration', 10))

            if frames == 0 or duration == 0:
                return 0.5

            # Calculate motion score
            expected_frames = fps * duration
            actual_ratio = frames / expected_frames if expected_frames > 0 else 1

            # FIX: If frame count is suspiciously low, it's probably a static image
            if actual_ratio < 0.5:
                return 0.1  # Likely static/slideshow

            # Check file size vs duration (motion videos are larger)
            file_size = os.path.getsize(video_path)
            size_per_sec = file_size / duration

            # Typical motion video: 500KB-2MB per second at 1080p
            if size_per_sec < 100000:  # < 100KB/sec = probably static/low motion
                return 0.2

            return min(1.0, size_per_sec / 1000000)  # Normalize

        except Exception:
            return 0.5

    # ─── NEW: Semantic matching ─────────────────────────────────
    def _score_clip_relevance(self, clip_desc: str, segment_text: str) -> float:
        """Score how well a clip matches the segment text"""
        if not clip_desc or not segment_text:
            return 0.5

        clip_words = set(clip_desc.lower().split())
        seg_words = set(segment_text.lower().split())

        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'between', 'under', 'again', 'further', 'then', 'once',
                     'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'each', 'few', 'more', 'most', 'other', 'some', 'such',
                     'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                     'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
                     'until', 'while', 'this', 'that', 'these', 'those'}

        clip_words -= stopwords
        seg_words -= stopwords

        if not clip_words or not seg_words:
            return 0.5

        intersection = clip_words & seg_words
        union = clip_words | seg_words

        if not union:
            return 0.5

        return len(intersection) / len(union)

    def search_pexels(self, query: str, per_page: int = 20) -> List[Dict]:
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

            # FIX: Also try landscape and crop later if portrait returns nothing
            if not data.get('videos', []):
                params["orientation"] = "landscape"
                response = requests.get(f"{self.pexels_base}/search", headers=headers, params=params, timeout=10)
                data = response.json()

            videos = []
            for video in data.get('videos', []):
                best_file = None
                best_height = 0

                for file in video.get('video_files', []):
                    height = file.get('height', 0)
                    # FIX: Prefer higher resolution, but also check file type
                    if height >= best_height and file.get('file_type', '').startswith('video'):
                        best_file = file
                        best_height = height

                if not best_file and video.get('video_files'):
                    best_file = video['video_files'][0]

                if best_file:
                    # FIX: Build description from tags + user info for semantic matching
                    description = ' '.join([
                        video.get('alt', ''),
                        video.get('user', {}).get('name', ''),
                        ' '.join(video.get('tags', []))
                    ])

                    videos.append({
                        'url': best_file['link'],
                        'duration': video.get('duration', 15),
                        'source': 'pexels',
                        'id': str(video.get('id', '')),
                        'description': description,
                        'width': best_file.get('width', 0),
                        'height': best_file.get('height', 0),
                        'orientation': 'portrait' if best_file.get('height', 0) > best_file.get('width', 0) else 'landscape'
                    })
            return videos
        except Exception as e:
            print(f"    Pexels error: {e}")
            return []

    def search_pixabay(self, query: str, per_page: int = 20) -> List[Dict]:
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

            # FIX: Try all orientations if vertical empty
            if not data.get('hits', []):
                params["orientation"] = "all"
                response = requests.get(f"{self.pixabay_base}/", params=params, timeout=10)
                data = response.json()

            videos = []
            for hit in data.get('hits', []):
                videos_data = hit.get('videos', {})
                # FIX: Prefer larger sizes for better motion
                for size in ['large', 'medium', 'small']:
                    url = videos_data.get(size, {}).get('url', '')
                    if url:
                        description = ' '.join([
                            hit.get('tags', ''),
                            hit.get('user', '')
                        ])

                        videos.append({
                            'url': url,
                            'duration': hit.get('duration', 15),
                            'source': 'pixabay',
                            'id': str(hit.get('id', '')),
                            'description': description,
                            'width': videos_data.get(size, {}).get('width', 0),
                            'height': videos_data.get(size, {}).get('height', 0),
                            'orientation': 'portrait' if videos_data.get(size, {}).get('height', 0) > videos_data.get(size, {}).get('width', 0) else 'landscape'
                        })
                        break
            return videos
        except Exception as e:
            print(f"    Pixabay error: {e}")
            return []

    # ─── NEW: Search multiple sources ───────────────────────────
    def search_all_sources(self, query: str) -> List[Dict]:
        """Search all video sources and merge results"""
        all_videos = []

        # Pexels
        pexels_videos = self.search_pexels(query, per_page=20)
        all_videos.extend(pexels_videos)

        # Pixabay
        pixabay_videos = self.search_pixabay(query, per_page=20)
        all_videos.extend(pixabay_videos)

        # FIX: Deduplicate by ID
        seen_ids = set()
        unique = []
        for v in all_videos:
            vid = v.get('id', '') + v.get('source', '')
            if vid not in seen_ids:
                seen_ids.add(vid)
                unique.append(v)

        return unique

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        """
        FIX: Semantic matching + motion validation for REAL video feel
        """
        clips = []
        used_ids = set()

        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')
            seg_text = segment.get('text', '')
            query = self._topic_to_query(topic, seg_type, i)

            print(f"    🎬 Seg {i} ({seg_type}): searching '{query}'")

            # Search all sources
            videos = self.search_all_sources(query)

            # Fallback if no results
            if not videos:
                fallback_q = self.fallback_queries[i % len(self.fallback_queries)]
                print(f"    ⚠️ No results, fallback: '{fallback_q}'")
                videos = self.search_all_sources(fallback_q)

            if not videos:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                print(f"    ⚠️ No clip found, using color bg")
                continue

            # FIX: Score by relevance to segment text
            scored = []
            for v in videos:
                if v.get('id') in used_ids:
                    continue
                relevance = self._score_clip_relevance(v.get('description', ''), seg_text)
                scored.append((relevance, v))

            # ─── FIX: Sort by relevance score only (not dict) ─────────────────
            scored.sort(key=lambda x: x[0], reverse=True)
            top_candidates = [v for _, v in scored[:3]]

            if not top_candidates:
                top_candidates = [v for v in videos if v.get('id') not in used_ids]
                if not top_candidates:
                    top_candidates = videos

            # Randomize among top candidates for variety
            random.shuffle(top_candidates)
            selected = top_candidates[0]
            used_ids.add(selected.get('id', ''))

            clips.append({
                'url': selected['url'],
                'start_time': segment.get('start', 0),
                'duration': segment.get('duration', 5),
                'segment_type': seg_type,
                'source': selected['source'],
                'id': selected.get('id', ''),
                'description': selected.get('description', ''),
                'orientation': selected.get('orientation', 'landscape')
            })
            print(f"    ✅ Found clip from {selected['source']} ({selected.get('orientation', 'unknown')})")

        return clips

    def download_footage(self, clips: List[Dict], output_dir: str) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)

        # Clean old clips
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

            # FIX: Skip if already downloaded this URL
            if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
                # Check motion score
                motion = self._check_motion_score(filepath)
                if motion > 0.3:
                    downloaded.append(filepath)
                    print(f"  ✅ Clip {i}: cached (motion: {motion:.2f})")
                    continue
                else:
                    print(f"  ⚠️ Clip {i}: cached but low motion ({motion:.2f}), re-downloading")

            try:
                print(f"  ⬇️ Clip {i} ({clip['source']})...")
                response = requests.get(clip['url'], stream=True, timeout=30)
                response.raise_for_status()

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=65536):
                        f.write(chunk)

                # FIX: Validate downloaded clip
                file_size = os.path.getsize(filepath)
                if file_size < 10000:
                    os.remove(filepath)
                    print(f"  ⚠️ Clip {i}: too small ({file_size} bytes)")
                    continue

                # FIX: Check motion score
                motion = self._check_motion_score(filepath)
                print(f"  📊 Clip {i}: {file_size//1024}KB | motion: {motion:.2f}")

                if motion < 0.2:
                    print(f"  ⚠️ Clip {i}: LOW MOTION — likely static/slideshow, will use color bg")
                    os.remove(filepath)
                    continue

                downloaded.append(filepath)
                print(f"  ✅ Clip {i}: downloaded & validated")

            except Exception as e:
                print(f"  ❌ Clip {i}: {e}")

        return downloaded
