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

        self.mixkit_base = "https://assets.mixkit.co/videos/preview"

        self.mood_modifiers = {
            'hook': ["cinematic dramatic fast", "close up mysterious motion", "dark moody atmosphere moving"],
            'shock': ["glitch distortion", "fast zoom motion", "shocking visual effect"],
            'suspense': ["suspenseful tense movement", "dramatic shadow motion", "eerie atmosphere moving"],
            'story': ["scientific close up motion", "macro detail moving", "documentary style dynamic"],
            'ctr': ["dramatic reveal motion", "close up emotional reaction", "bright realization moment"],
        }

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

    # ─── Motion score validation ───────────────────────────
    def _check_motion_score(self, video_path: str) -> float:
        """
        Check if video likely has REAL motion (not static image or slideshow)
        Returns: 0.0-1.0 motion score
        """
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration,bit_rate,r_frame_rate,nb_frames',
                '-show_entries', 'format=duration,bit_rate',
                '-of', 'default=noprint_wrappers=1',
                video_path
            ], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return 0.5  # Default: assume motion

            data = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    k, v = line.split('=', 1)
                    data[k.strip()] = v.strip()

            duration = float(data.get('duration', 0) or 0)
            if duration <= 0:
                duration = 10.0

            file_size = os.path.getsize(video_path)
            size_per_sec = file_size / duration

            if size_per_sec < 100000:  # < 100KB/sec = probably static/low motion
                return 0.2

            return min(1.0, size_per_sec / 1000000)  # Normalize

        except Exception:
            return 0.5

    # ─── Semantic matching ─────────────────────────────────
    def _score_clip_relevance(self, clip_desc: str, segment_text: str) -> float:
        """Score how well a clip matches the segment text"""
        if not clip_desc or not segment_text:
            return 0.5

        clip_words = set(clip_desc.lower().split())
        seg_words = set(segment_text.lower().split())

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
                    if height >= best_height and file.get('file_type', '').startswith('video'):
                        best_file = file
                        best_height = height

                if not best_file and video.get('video_files'):
                    best_file = video['video_files'][0]

                if best_file:
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

            if not data.get('hits', []):
                params["orientation"] = "all"
                response = requests.get(f"{self.pixabay_base}/", params=params, timeout=10)
                data = response.json()

            videos = []
            for hit in data.get('hits', []):
                videos_data = hit.get('videos', {})
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

    # ─── Search multiple sources ───────────────────────────
    def search_all_sources(self, query: str) -> List[Dict]:
        """Search all video sources and merge results"""
        all_videos = []

        pexels_videos = self.search_pexels(query, per_page=20)
        all_videos.extend(pexels_videos)

        pixabay_videos = self.search_pixabay(query, per_page=20)
        all_videos.extend(pixabay_videos)

        # Deduplicate by ID
        seen_ids = set()
        unique = []
        for v in all_videos:
            vid = v.get('id', '') + v.get('source', '')
            if vid not in seen_ids:
                seen_ids.add(vid)
                unique.append(v)

        return unique

    def _search_for_segment(self, i: int, segment: Dict, topic: str) -> tuple:
        seg_type = segment.get('type', 'story')
        query = self._topic_to_query(topic, seg_type, i)
        print(f"    🎬 Seg {i} ({seg_type}): searching '{query}'")

        videos = self.search_all_sources(query)

        if not videos:
            fallback_q = self.fallback_queries[i % len(self.fallback_queries)]
            print(f"    ⚠️ Seg {i}: no results, fallback: '{fallback_q}'")
            videos = self.search_all_sources(fallback_q)

        return i, videos

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        """
        Semantic matching + motion validation for REAL video feel.
        Searches run concurrently for speed.

        FIX: `used_ids` was being checked while building candidates but a
        segment with zero unmatched candidates silently fell back to
        `videos` (the FULL unfiltered list, including already-used clips)
        — so the same clip could legitimately win twice and play back to
        back / repeat across the video. We now guarantee global uniqueness
        per fetch: if every scored candidate for a segment is already used,
        we keep searching down the list before ever reusing an id, and we
        only reuse a previously-used id as an absolute last resort when
        nothing unused exists anywhere in the results.
        """
        used_ids = set()

        from concurrent.futures import ThreadPoolExecutor
        search_results = {}
        max_workers = min(6, max(1, len(script_segments)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._search_for_segment, i, segment, topic)
                for i, segment in enumerate(script_segments)
            ]
            for future in futures:
                i, videos = future.result()
                search_results[i] = videos

        clips = []
        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')
            seg_text = segment.get('text', '')
            videos = search_results.get(i, [])

            if not videos:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                print(f"    ⚠️ No clip found for seg {i}, using color bg")
                continue

            # FIX: Only ever consider candidates NOT already used this run.
            unused_videos = [v for v in videos if v.get('id') not in used_ids]

            if not unused_videos:
                # Genuinely nothing unused left for this segment — fall back
                # to color background instead of silently repeating a clip.
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 5),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                print(f"    ⚠️ Seg {i}: all candidates already used, using color bg")
                continue

            scored = []
            for v in unused_videos:
                relevance = self._score_clip_relevance(v.get('description', ''), seg_text)
                scored.append((relevance, v))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_candidates = [v for _, v in scored[:3]] or unused_videos

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
            print(f"    ✅ Seg {i}: found clip from {selected['source']} ({selected.get('orientation', 'unknown')})")

        return clips

    def _download_one(self, i: int, clip: Dict, output_dir: str):
        """Download + validate a single clip. Returns (i, filepath_or_None)."""
        if not clip.get('url'):
            print(f"  ⚠️ Clip {i}: no URL, using color bg")
            return i, None

        filepath = os.path.join(output_dir, f"clip_{i}.mp4")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            motion = self._check_motion_score(filepath)
            if motion > 0.3:
                print(f"  ✅ Clip {i}: cached (motion: {motion:.2f})")
                return i, filepath
            else:
                print(f"  ⚠️ Clip {i}: cached but low motion ({motion:.2f}), re-downloading")

        try:
            print(f"  ⬇️ Clip {i} ({clip['source']})...")
            response = requests.get(clip['url'], stream=True, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=65536):
                    f.write(chunk)

            file_size = os.path.getsize(filepath)
            if file_size < 10000:
                os.remove(filepath)
                print(f"  ⚠️ Clip {i}: too small ({file_size} bytes)")
                return i, None

            motion = self._check_motion_score(filepath)
            print(f"  📊 Clip {i}: {file_size//1024}KB | motion: {motion:.2f}")

            if motion < 0.2:
                print(f"  ⚠️ Clip {i}: LOW MOTION — likely static/slideshow, will use color bg")
                os.remove(filepath)
                return i, None

            print(f"  ✅ Clip {i}: downloaded & validated")
            return i, filepath

        except Exception as e:
            print(f"  ❌ Clip {i}: {e}")
            return i, None

    def download_footage(self, clips: List[Dict], output_dir: str) -> Dict[int, str]:
        """
        FIX: Previously returned a re-indexed list (`downloaded = [results[i]
        for i in sorted(...)]`), which silently DROPPED the original segment
        index whenever any segment had no clip (failed download / no URL).
        Example: if segment 2 had no clip, the old list became
        [seg0_clip, seg1_clip, seg3_clip, seg4_clip, ...] — i.e. seg3's clip
        physically lands at list position 2. Since the video assembler reads
        clips back as `clip_{footage_idx}.mp4` and increments footage_idx
        sequentially regardless of gaps, this caused later segments to load
        the WRONG (already-used) clip file from disk — the visible
        "same scene repeats" bug. We now return a dict keyed by the ORIGINAL
        segment index, so gaps stay gaps instead of shifting everything
        after them.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Clean old clips
        for f in os.listdir(output_dir):
            if f.startswith('clip_') and f.endswith('.mp4'):
                try:
                    os.remove(os.path.join(output_dir, f))
                except:
                    pass

        from concurrent.futures import ThreadPoolExecutor

        results = {}
        max_workers = min(6, max(1, len(clips)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._download_one, i, clip, output_dir)
                       for i, clip in enumerate(clips)]
            for future in futures:
                i, filepath = future.result()
                if filepath:
                    results[i] = filepath

        # FIX: return index-keyed dict instead of a re-indexed list
        return results
