"""
Footage Fetcher — Production 2026
Sources:
  1. Pexels      — Paid API (Portrait/Landscape)
  2. Dareful     — FREE, 4K Stock (Unique)
FIX: Type hints fixed, Mazwai/LifeOfVids removed, stability improved.
"""

import os
import re
import time
import random
import logging
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
        self.dareful_base = "https://www.dareful.com/api/v1/videos"
        
        self.max_retries = 3
        self.retry_delay = 2
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; AutomationBot/3.0)'})
        
        self.used_ids_file = "state/used_clips.txt"
        self.used_ids = self._load_used_ids()
        self._state_lock = threading.Lock()
        
        self.query_cache = {}
        self.cache_lock = threading.Lock()
        self.limiter = TokenBucketRateLimiter(tokens=15, fill_rate=2.0)
        
        logger.info("📹 FootageFetcher initialized (Pexels + Dareful)")

    def _load_used_ids(self) -> set:
        try:
            os.makedirs("state", exist_ok=True)
            if os.path.exists(self.used_ids_file):
                with open(self.used_ids_file, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
        except: pass
        return set()

    def _save_used_id(self, clip_id: str):
        with self._state_lock:
            with open(self.used_ids_file, 'a') as f:
                f.write(clip_id + "\n")

    def _rate_limited_get(self, url: str, params: Dict = None, timeout=(10, 45)) -> Optional[Dict]:
        for _ in range(self.max_retries):
            self.limiter.acquire()
            try:
                r = self.session.get(url, params=params, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except: time.sleep(self.retry_delay)
        return None

    def search_pexels(self, query: str) -> List[Dict]:
        if not self.pexels_key: return []
        data = self._rate_limited_get(f"{self.pexels_base}/search", params={"query": query, "per_page": 10, "orientation": "portrait"})
        videos = []
        if data and 'videos' in data:
            for v in data['videos']:
                files = v.get('video_files', [])
                best = next((f for f in files if f.get('file_type', '').startswith('video')), None)
                if best:
                    videos.append({'url': best['link'], 'id': f"pex_{v['id']}", 'is_portrait': True, 'source': 'pexels'})
        return videos

    def search_dareful(self, query: str) -> List[Dict]:
        data = self._rate_limited_get(self.dareful_base, params={"search": query})
        videos = []
        if data and 'videos' in data:
            for item in data['videos']:
                videos.append({
                    'url': item.get('download_url'),
                    'id': f"dar_{item.get('id', random.randint(1000, 9999))}",
                    'is_portrait': False,
                    'source': 'dareful'
                })
        return videos

    def search_all_sources(self, query: str) -> List[Dict]:
        with ThreadPoolExecutor(max_workers=2) as ex:
            f1 = ex.submit(self.search_pexels, query)
            f2 = ex.submit(self.search_dareful, query)
            results = f1.result() + f2.result()
        return sorted(results, key=lambda x: x['is_portrait'], reverse=True)

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        clips = []
        for seg in script_segments:
            query = seg.get('visual_prompt', topic)
            results = self.search_all_sources(query)
            # Logic to select unused
            selected = next((v for v in results if v['id'] not in self.used_ids), None) or (results[0] if results else None)
            if selected:
                self.used_ids.add(selected['id'])
                self._save_used_id(selected['id'])
                selected['segment_duration'] = seg.get('segment_duration', 5.0)
                clips.append(selected)
        return clips

    def download_footage(self, clips: List[Dict], output_dir: str) -> Dict[int, str]:
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        for idx, clip in enumerate(clips):
            if not clip.get('url'): continue
            path = os.path.join(output_dir, f"clip_{idx}.mp4")
            try:
                r = requests.get(clip['url'], stream=True, timeout=30)
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(32768): f.write(chunk)
                results[idx] = path
            except: continue
        return results
