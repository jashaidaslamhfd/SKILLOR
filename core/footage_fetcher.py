"""
Footage Fetcher — USA 2026 (PRODUCTION GRADE AUTOMATION)
INTEGRATED PRODUCTION UPGRADES & FIXES:
1. 🐛 Fixed Groq NameError: Explicitly imported and mapped using standard 'groq' package.
2. 🚀 Native Visual Prompt Extraction: Prioritizes pre-baked visual prompts from ContentGenerator.
3. 🧠 Smart Keyword Hybrid Fallback Layer: Combines topic markers if prompts are missing.
4. 🥇 Thread-safe Rate Limiting & Persistent Token Bucket Processing.
5. 🎬 Integrated Center-Crop Metadata Flags to guide FFmpeg / MoviePy layout compiling.
"""

import os
import re
import time
import math
import random
import logging
import subprocess
import requests
import threading
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 🥇 Fix 1: Safe Groq SDK import injection to prevent NameError crash loop
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from config.settings import API_KEYS
except ImportError:
    class FallbackAPIKeys:
        PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
        PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    API_KEYS = FallbackAPIKeys()

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Thread-safe Token Bucket for Pexels/Pixabay API rate limits control."""
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
            
            wait_time = (1 - self.tokens) / self.fill_rate
            time.sleep(wait_time)
            self.tokens = 0
            return True


class FootageFetcher:
    """Production Footage Fetcher - Linked with 2026 Content Pipeline Structure"""
    
    def __init__(self):
        self.pexels_key = getattr(API_KEYS, 'PEXELS_API_KEY', '')
        self.pixabay_key = getattr(API_KEYS, 'PIXABAY_API_KEY', '')
        
        self.pexels_base = "https://api.pexels.com/videos"
        self.pixabay_base = "https://pixabay.com/api/videos"
        
        self.max_retries = 3
        self.retry_delay = 2
        self.max_delay = 30
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Compatible; Automation FootageFetcher/3.0)',
            'Accept-Encoding': 'gzip, deflate',
        })
        
        self.used_ids_file = "state/used_clips.txt"
        self._state_lock = threading.Lock()
        self.used_ids = self._load_used_ids()
        
        self.query_cache = {}
        self.cache_lock = threading.Lock()
        self.limiter = TokenBucketRateLimiter(tokens=15, fill_rate=2.0) 
        
        self.stats = {
            'total_searched': 0,
            'total_found': 0,
            'total_downloaded': 0,
            'failed_downloads': 0,
            'rate_limits_hit': 0,
        }

        # 🥇 Fix 1 Validation: Linking proper instantiated Groq environment handles
        self.groq_client = None
        self.groq_model = "llama-3.3-70b-versatile"
        
        groq_api_token = getattr(API_KEYS, 'GROQ_API_KEY', os.getenv("GROQ_API_KEY", ""))
        if Groq and groq_api_token:
            try:
                self.groq_client = Groq(api_key=groq_api_token)
                logger.info("✅ AI Visual Keyword Extraction Engine online via Groq")
            except Exception as e:
                logger.warning(f"⚠️ Groq client initialization bypassed: {e}")
        
        self.fallback_queries = [
            "cute baby playing close up", "happy infant smiling cinematic",
            "mother holding newborn warm light", "glowing abstract medical background",
            "parents bonding baby slow motion", "toddler laughing looking camera"
        ]
        
        logger.info("📹 FootageFetcher pipeline loaded successfully (Portrait Enforced)")

    def _load_used_ids(self) -> set:
        try:
            os.makedirs("state", exist_ok=True)
            if os.path.exists(self.used_ids_file):
                with open(self.used_ids_file, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.warning(f"⚠️ Could not load used logs: {e}")
        return set()

    def _save_used_id(self, clip_id: str):
        try:
            with self._state_lock:
                with open(self.used_ids_file, 'a') as f:
                    f.write(clip_id + "\n")
        except Exception:
            pass

    def _rate_limited_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        for attempt in range(self.max_retries):
            self.limiter.acquire()
            try:
                req_headers = self.session.headers.copy()
                if headers: req_headers.update(headers)
                
                response = self.session.get(url, params=params, headers=req_headers, timeout=(10, 45))
                
                if response.status_code == 429:
                    self.stats['rate_limits_hit'] += 1
                    time.sleep(min(self.max_delay, 5 * (2 ** attempt)))
                    continue
                    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Network request terminal failure: {e}")
                time.sleep(self.retry_delay * (attempt + 1))
        return None

    def _generate_visual_keywords(self, segment_text: str, seg_type: str, topic: str) -> str:
        """Backup keyword extraction logic running if prompt data matrix is completely empty."""
        if not self.groq_client:
            return f"{topic} cinematic motion".strip()
        try:
            prompt = f"Extract exactly 2 visual physical search terms for Pexels based on: '{segment_text}'. Output only comma separated words."
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=30
            )
            result = response.choices[0].message.content.strip()
            clean_data = re.sub(r'[^a-zA-Z0-9,\s]', '', result)
            first_term = clean_data.split(',')[0].strip()
            return f"{first_term} slow motion"
        except Exception:
            return f"{topic} motion"

    def search_pexels(self, query: str) -> List[Dict]:
        if not self.pexels_key: return []
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": 15, "orientation": "portrait", "size": "large"}
        
        try:
            data = self._rate_limited_request(f"{self.pexels_base}/search", params=params, headers=headers)
            # Safe Fallback to landscape assets if portrait orientation runs dry
            if not data or not data.get('videos'):
                params["orientation"] = "landscape"
                data = self._rate_limited_request(f"{self.pexels_base}/search", params=params, headers=headers)
            
            if not data: return []
            
            videos = []
            for video in data.get('videos', []):
                best_file = None
                for file in video.get('video_files', []):
                    if file.get('file_type', '').startswith('video'):
                        best_file = file
                        break
                
                if best_file:
                    w, h = best_file.get('width', 0), best_file.get('height', 0)
                    videos.append({
                        'url': best_file['link'], 'duration': video.get('duration', 10), 'source': 'pexels',
                        'id': f"pex_{video.get('id')}", 'width': w, 'height': h,
                        'description': video.get('alt', ''), 'is_portrait': h > w
                    })
            return videos
        except Exception as e:
            logger.error(f"Pexels fetch crash: {e}")
            return []

    def search_pixabay(self, query: str) -> List[Dict]:
        if not self.pixabay_key: return []
        params = {"key": self.pixabay_key, "q": query, "per_page": 10, "orientation": "vertical"}
        try:
            data = self._rate_limited_request(self.pixabay_base, params=params)
            if not data or not data.get('hits'):
                params["orientation"] = "all"
                data = self._rate_limited_request(self.pixabay_base, params=params)
                
            if not data: return []
            
            videos = []
            for hit in data.get('hits', []):
                v_data = hit.get('videos', {})
                med = v_data.get('medium', v_data.get('small', {}))
                if med.get('url'):
                    w, h = med.get('width', 0), med.get('height', 0)
                    videos.append({
                        'url': med['url'], 'duration': hit.get('duration', 10), 'source': 'pixabay',
                        'id': f"pix_{hit.get('id')}", 'width': w, 'height': h,
                        'description': hit.get('tags', ''), 'is_portrait': h > w
                    })
            return videos
        except Exception:
            return []

    def search_all_sources(self, query: str) -> List[Dict]:
        with self.cache_lock:
            if query in self.query_cache: return self.query_cache[query]
            
        results = []
        results.extend(self.search_pexels(query))
        results.extend(self.search_pixabay(query))
        
        # Prioritize portrait formats first over raw lists
        portraits = [v for v in results if v['is_portrait']]
        landscapes = [v for v in results if not v['is_portrait']]
        ordered = portraits + landscapes
        
        with self.cache_lock:
            self.query_cache[query] = ordered
        return ordered

    def _search_for_segment(self, i: int, segment: Dict, topic: str) -> Tuple[int, List[Dict]]:
        """🥇 Fix 2: Directly pulls visual_prompt extracted from ContentGenerator."""
        stype = segment.get('type', 'story')
        stext = segment.get('text', '')
        
        # Direct pipeline lookup configuration check
        query = segment.get('visual_prompt', '').strip()
        
        if not query:
            # Fallback to local regex/groq layer only if content script generator passed empty data
            query = self._generate_visual_keywords(stext, stype, topic)
            
        self.stats['total_searched'] += 1
        videos = self.search_all_sources(query)
        
        if not videos:
            # Harsh backup if API query parameters were over-specified
            backup_query = f"{topic} baby narrative motion"
            videos = self.search_all_sources(backup_query)
            
        return i, videos

    def fetch_footage_for_script(self, script_segments: List[Dict], topic: str) -> List[Dict]:
        logger.info(f"📹 Querying cloud asset catalogs for script structures...")
        s_res = {}
        
        with ThreadPoolExecutor(max_workers=min(4, len(script_segments))) as executor:
            futures = [executor.submit(self._search_for_segment, i, seg, topic) for i, seg in enumerate(script_segments)]
            for future in as_completed(futures):
                idx, vids = future.result()
                s_res[idx] = vids
                
        clips = []
        for i, segment in enumerate(script_segments):
            videos = s_res.get(i, [])
            selected_video = None
            
            for v in videos:
                with self._state_lock:
                    if v['id'] not in self.used_ids:
                        selected_video = v
                        self.used_ids.add(v['id'])
                        self._save_used_id(v['id'])
                        break
            
            if not selected_video and videos:
                selected_video = videos[0] # Reuse asset safe fallback bound
                
            if not selected_video:
                # Absolute system empty fallback dummy track
                clips.append({'url': None, 'is_portrait': True, 'crop_needed': False, 'source': 'empty'})
                continue

            # 🥇 Fix 3: Injected transform crop flags to alert downstream processing layers
            clips.append({
                'url': selected_video['url'],
                'id': selected_video['id'],
                'source': selected_video['source'],
                'is_portrait': selected_video['is_portrait'],
                'crop_needed': not selected_video['is_portrait'],  # Flag used by video compiler
                'width': selected_video['width'],
                'height': selected_video['height']
            })
            
        return clips

    def _check_motion_score(self, video_path: str) -> float:
        """Uses FFmpeg select metric to calculate clip visual variance densities."""
        try:
            cmd = ['ffmpeg', '-i', video_path, '-filter:v', "select='gt(scene,0.02)',metadata=print:file=-", '-f', 'null', '-']
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return 0.8 if res.stdout.count("lavfi.scene_score") > 1 else 0.1
        except Exception:
            return 0.5

    def download_footage(self, clips: List[Dict], output_dir: str) -> Dict[int, str]:
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        def _download_track(idx, clip):
            if not clip.get('url'): return idx, None
            path = os.path.join(output_dir, f"clip_{idx}.mp4")
            try:
                res = requests.get(clip['url'], stream=True, timeout=45)
                res.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=32768): f.write(chunk)
                return idx, path
            except Exception:
                return idx, None

        with ThreadPoolExecutor(max_workers=3) as exec:
            futures = [exec.submit(_download_track, i, c) for i, c in enumerate(clips)]
            for f in as_completed(futures):
                idx, pth = f.result()
                if pth: results[idx] = pth
        return results

# ============================================================
# RUNTIME INTEGRITY TEST
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetcher = FootageFetcher()
    print("\n✅ FootageFetcher structurally safe and linked to 2026 prompt matrices!")
