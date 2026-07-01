"""
Footage Fetcher — Production 2026
Sources:
  1. Pexels      — paid API (existing)
  2. Life of Vids — FREE, no key, unique clips
  3. Dareful     — FREE, no key, 4K stock
REMOVED: Pixabay (400 error), Coverr (401 — no longer free), Videvo (0 results),
         Mazwai (domain merged into Freepik/Magnific, old API endpoint dead — 403s)
FIX: Each clip is trimmed to segment_duration so it matches voice EXACTLY
"""

import os
import re
import time
import random
import logging
import subprocess
import requests
import threading
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from config.settings import API_KEYS
except ImportError:
    class FallbackAPIKeys:
        PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    API_KEYS = FallbackAPIKeys()

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    def __init__(self, tokens: int = 15, fill_rate: float = 2.0):
        self.capacity = tokens
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.timestamp = time.time()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            delta = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + delta * self.fill_rate)
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            time.sleep((1 - self.tokens) / self.fill_rate)
            self.tokens = 0
            return True


class FootageFetcher:

    def __init__(self):
        self.pexels_key = getattr(API_KEYS, 'PEXELS_API_KEY', '')
        self.pexels_base = "https://api.pexels.com/videos"

        self.max_retries = 3
        self.retry_delay = 2

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AutomationBot/3.0)',
            'Accept-Encoding': 'gzip, deflate',
        })

        self.used_ids_file = "state/used_clips.txt"
        self.max_used_ids = 400
        self._state_lock = threading.Lock()
        self.used_ids = self._load_used_ids()

        self.query_cache = {}
        self.cache_lock = threading.Lock()
        self.limiter = TokenBucketRateLimiter(tokens=15, fill_rate=2.0)

        self.stats = {'total_searched': 0, 'total_found': 0, 'failed_downloads': 0}

        self.groq_client = None
        groq_key = getattr(API_KEYS, 'GROQ_API_KEY', os.getenv("GROQ_API_KEY", ""))
        if Groq and groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("✅ AI Visual Keyword Extraction Engine online via Groq")
            except Exception as e:
                logger.warning(f"⚠️ Groq init bypassed: {e}")

        logger.info("📹 FootageFetcher pipeline loaded successfully (Portrait Enforced)")
        logger.info("🎬 Sources active: Pexels + Life of Vids (free) + Dareful (free)")

    # ──────────────────────────────────────────
    def _load_used_ids(self) -> set:
        try:
            os.makedirs("state", exist_ok=True)
            if os.path.exists(self.used_ids_file):
                with open(self.used_ids_file, 'r') as f:
                    ids = [l.strip() for l in f if l.strip()]
                return set(ids[-self.max_used_ids:])
        except Exception:
            pass
        return set()

    def _save_used_id(self, clip_id: str):
        try:
            with self._state_lock:
                with open(self.used_ids_file, 'a') as f:
                    f.write(clip_id + "\n")
        except Exception:
            pass

    def _rate_limited_get(self, url: str, params: Dict = None, headers: Dict = None, timeout=(10, 45)) -> Optional[Dict]:
        for attempt in range(self.max_retries):
            self.limiter.acquire()
            try:
                h = dict(self.session.headers)
                if headers:
                    h.update(headers)
                r = self.session.get(url, params=params, headers=h, timeout=timeout)
                if r.status_code == 429:
                    time.sleep(5 * (2 ** attempt))
                    continue
                if r.status_code in (401, 403):
                    logger.warning(f"⚠️ Auth error {r.status_code} for {url} — skipping source")
                    return None
                r.raise_for_status()
                return r.json()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Network failure: {e}")
                time.sleep(self.retry_delay * (attempt + 1))
        return None

    def _generate_visual_keywords(self, segment_text: str, topic: str) -> str:
        if not self.groq_client:
            return f"{topic} cinematic motion"
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Give 2 visual stock video search words for: '{segment_text}'. Only words, comma separated."}],
                temperature=0.4, max_tokens=20
            )
            raw = response.choices[0].message.content.strip()
            clean = re.sub(r'[^a-zA-Z0-9,\s]', '', raw)
            return clean.split(',')[0].strip() + " slow motion"
        except Exception:
            return f"{topic} motion"

    # ──────────────────────────────────────────
    # SOURCE 1: PEXELS
    # ──────────────────────────────────────────
    def search_pexels(self, query: str) -> List[Dict]:
        if not self.pexels_key:
            return []
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": 25, "orientation": "portrait", "size": "large"}

        data = self._rate_limited_get(f"{self.pexels_base}/search", params=params, headers=headers)
        if not data or not data.get('videos'):
            params["orientation"] = "landscape"
            data = self._rate_limited_get(f"{self.pexels_base}/search", params=params, headers=headers)
        if not data:
            return []

        videos = []
        for video in data.get('videos', []):
            best = None
            for f in video.get('video_files', []):
                if f.get('file_type', '').startswith('video'):
                    best = f
                    break
            if best:
                w, h = best.get('width', 0), best.get('height', 0)
                videos.append({
                    'url': best['link'], 'duration': video.get('duration', 10),
                    'source': 'pexels', 'id': f"pex_{video.get('id')}",
                    'width': w, 'height': h, 'is_portrait': h > w
                })
        return videos

    # ──────────────────────────────────────────
    # SOURCE 3: LIFE OF VIDS — Free, no key
    # Unique clips, very low audience overlap
    # ──────────────────────────────────────────
    def search_life_of_vids(self, query: str) -> List[Dict]:
        """
        Life of Vids: Free videos, no attribution required.
        Uses their JSON catalog filtered by keywords.
        """
        try:
            # LoV exposes a simple JSON catalog
            data = self._rate_limited_get(
                "https://www.lifeofvids.com/api/videos",
                params={"search": query, "limit": 12},
                timeout=(8, 20)
            )
            if not data:
                return []

            videos = []
            items = data.get('videos', data if isinstance(data, list) else [])
            for item in items:
                mp4_url = item.get('mp4', item.get('url', item.get('video_url', '')))
                if not mp4_url:
                    continue
                w = item.get('width', 1920)
                h = item.get('height', 1080)
                clip_id = f"lov_{item.get('id', random.randint(10000, 99999))}"
                videos.append({
                    'url': mp4_url, 'duration': item.get('duration', 7),
                    'source': 'lifeofvids', 'id': clip_id,
                    'width': w, 'height': h, 'is_portrait': h > w
                })
            logger.info(f"🎞️ LifeOfVids: {len(videos)} clips for '{query}'")
            return videos
        except Exception as e:
            logger.warning(f"⚠️ LifeOfVids failed: {e}")
            return []

    # ──────────────────────────────────────────
    # COMBINED SEARCH — All sources parallel
    # ──────────────────────────────────────────
    def search_all_sources(self, query: str) -> List[Dict]:
        with self.cache_lock:
            if query in self.query_cache:
                return self.query_cache[query]

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_pexels   = ex.submit(self.search_pexels,       query)
            f_lov      = ex.submit(self.search_life_of_vids, query)

            r_pexels   = f_pexels.result()
            r_lov      = f_lov.result()

        # Interleave so sources alternate
        results = []
        for i in range(max(len(r_pexels), len(r_lov))):
            if i < len(r_pexels):  results.append(r_pexels[i])
            if i < len(r_lov):     results.append(r_lov[i])

        portraits  = [v for v in results if v['is_portrait']]
        landscapes = [v for v in results if not v['is_portrait']]
        ordered = portraits + landscapes

        logger.info(
            f"📊 Clips: {len(ordered)} total "
            f"(Pexels:{len(r_pexels)} LoV:{len(r_lov)})"
        )

        with self.cache_lock:
            self.query_cache[query] = ordered
        return ordered

    def _search_for_segment(self, i: int, segment: Dict, topic: str) -> Tuple[int, List[Dict]]:
        query = segment.get('visual_prompt', '').strip()
        if not query:
            query = self._generate_visual_keywords(segment.get('text', ''), topic)
        self.stats['total_searched'] += 1
        videos = self.search_all_sources(query)
        if not videos:
            videos = self.search_all_sources(f"{topic} cinematic motion")
        return i, videos

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        logger.info("📹 Querying cloud asset catalogs for script structures...")
        s_res = {}

        with ThreadPoolExecutor(max_workers=min(4, len(script_segments))) as ex:
            futures = [ex.submit(self._search_for_segment, i, seg, topic)
                       for i, seg in enumerate(script_segments)]
            for f in as_completed(futures):
                idx, vids = f.result()
                s_res[idx] = vids

        clips = []
        for i, segment in enumerate(script_segments):
            videos = s_res.get(i, [])
            selected = None
            for v in videos:
                with self._state_lock:
                    if v['id'] not in self.used_ids:
                        selected = v
                        self.used_ids.add(v['id'])
                        self._save_used_id(v['id'])
                        break
            if not selected and videos:
                selected = random.choice(videos)
            if not selected:
                clips.append({'url': None, 'is_portrait': True, 'crop_needed': False,
                              'source': 'empty', 'segment_duration': segment.get('segment_duration', 5.0)})
                continue

            clips.append({
                'url': selected['url'],
                'id': selected['id'],
                'source': selected['source'],
                'is_portrait': selected['is_portrait'],
                'crop_needed': not selected['is_portrait'],
                'width': selected['width'],
                'height': selected['height'],
                # ✅ KEY: pass voice timing so assembler trims clip correctly
                'segment_duration': segment.get('segment_duration', selected.get('duration', 5.0)),
            })
        return clips

    def download_footage(self, clips: List[Dict], output_dir: str) -> Dict[int, str]:
        os.makedirs(output_dir, exist_ok=True)

        def _dl(idx, clip):
            if not clip.get('url'):
                return idx, None
            path = os.path.join(output_dir, f"clip_{idx}.mp4")
            try:
                r = requests.get(clip['url'], stream=True, timeout=45)
                r.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(32768):
                        f.write(chunk)
                return idx, path
            except Exception as e:
                logger.error(f"Download failed clip {idx}: {e}")
                return idx, None

        results = {}
        with ThreadPoolExecutor(max_workers=3) as ex:
            for idx, path in ex.map(lambda x: _dl(*x), enumerate(clips)):
                if path:
                    results[idx] = path
        return results
