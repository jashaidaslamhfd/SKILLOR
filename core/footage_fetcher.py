"""
Footage Fetcher — Production 2026
Sources:
  1. Pexels      — paid API
  2. Dareful     — FREE, 4K stock
REMOVED: Mazwai, Life of Vids, Pixabay, Coverr, Videvo
"""

import os
import re
import time
import logging
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class FootageFetcher:
    def __init__(self):
        self.pexels_key = getattr(API_KEYS, 'PEXELS_API_KEY', '')
        self.pexels_base = "https://api.pexels.com/videos"
        self.max_retries = 3
        
        # Dareful Configuration
        self.dareful_url = "https://www.dareful.com/api/v1/videos" 
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.used_ids_file = "state/used_clips.txt"
        self.used_ids = self._load_used_ids()
        self._state_lock = threading.Lock()
        
        logger.info("🎬 Pipeline Updated: Sources set to Pexels + Dareful (Unique Clips)")

    def search_dareful(self, query: str) -> List[Dict]:
        """
        Fetches 4K stock footage from Dareful with error safety.
        """
        try:
            # Dareful endpoint call
            response = self.session.get(self.dareful_url, params={"search": query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            # Safety check: ensuring data format exists before iterating
            items = data.get('videos', []) if isinstance(data, dict) else []
            
            for item in items:
                videos.append({
                    'url': item.get('download_url'),
                    'duration': item.get('duration', 10),
                    'source': 'dareful',
                    'id': f"dar_{item.get('id', random.randint(1000, 9999))}",
                    'width': 3840, 'height': 2160,
                    'is_portrait': False
                })
            return videos
        except Exception as e:
            logger.error(f"❌ Dareful source failed: {e}")
            return []

    def search_all_sources(self, query: str) -> List[Dict]:
        # Threading for speed, only 2 sources now to prevent bottleneck
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_pexels = ex.submit(self.search_pexels, query)
            f_dareful = ex.submit(self.search_dareful, query)
            
            # Combine results safely
            results = f_pexels.result() + f_dareful.result()
            
        # Prioritize portrait clips for Shorts/Reels
        ordered = sorted(results, key=lambda x: x['is_portrait'], reverse=True)
        return ordered

    # (Baki functions like _load_used_ids, fetch_footage_for_script, download_footage wese hi rahen ge)
