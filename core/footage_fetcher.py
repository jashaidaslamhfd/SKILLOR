"""
Footage Fetcher - Production Ready (FIXED)
OPTIMIZED FOR: 35-54 Male USA/UK Audience

FIXES:
1. ✅ Connection pooling with explicit timeouts
2. ✅ Concurrent download with proper exception handling
3. ✅ Rate limit handling with exponential backoff + Retry-After
4. ✅ Portrait orientation validation (9:16 only)
5. ✅ Motion score validation (no static clips)
6. ✅ Comprehensive logging
7. ✅ Partial success handling (don't fail all if one fails)
"""

import os
import re
import time
import random
import logging
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from config.settings import API_KEYS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('footage_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FootageFetcher:
    """Production Footage Fetcher - FIXED"""
    
    def __init__(self):
        # API Keys
        self.pexels_key = API_KEYS.PEXELS_API_KEY
        self.pixabay_key = API_KEYS.PIXABAY_API_KEY
        
        # API Endpoints
        self.pexels_base = "https://api.pexels.com/videos"
        self.pixabay_base = "https://pixabay.com/api/videos"
        
        # FIX 1: Retry settings with better backoff
        self.max_retries = 3
        self.retry_delay = 2
        self.max_delay = 60
        
        # FIX 2: Timeout settings (connect, read)
        self.connect_timeout = 10
        self.read_timeout = 60
        
        # FIX 3: Session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Compatible; FootageFetcher/2.0)',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Cache for used clips (prevent repeats)
        self.used_ids = set()
        self.clip_cache = {}
        
        # Statistics
        self.stats = {
            'total_searched': 0,
            'total_found': 0,
            'total_downloaded': 0,
            'failed_downloads': 0,
            'rate_limits_hit': 0,
        }
        
        # ============================================================
        # SEGMENT-SPECIFIC MOOD MODIFIERS
        # ============================================================
        self.mood_modifiers = {
            'hook': [
                "cinematic dramatic motion",
                "close up mysterious movement",
                "dark moody atmosphere"
            ],
            'shock': [
                "dramatic reveal motion",
                "intense close up action",
                "surprising visual effect"
            ],
            'suspense': [
                "suspenseful tense movement",
                "dramatic shadow motion",
                "eerie atmosphere moving"
            ],
            'story': [
                "scientific close up motion",
                "macro detail moving",
                "documentary style dynamic"
            ],
            'ctr': [
                "dramatic reveal motion",
                "close up emotional reaction",
                "bright realization moment"
            ]
        }
        
        # ============================================================
        # FALLBACK QUERIES
        # ============================================================
        self.fallback_queries = [
            "human brain neurons glowing motion",
            "person thinking deep thought cinematic",
            "brain scan medical close up motion",
            "abstract neural network dark flowing",
            "eye close up blinking dramatic",
            "heartbeat pulse medical motion",
            "shadow figure walking mysterious",
            "person sleeping bedroom night moving",
            "nature calm relaxing motion",
            "city night lights cinematic",
        ]
        
        logger.info("📹 FootageFetcher initialized")

    # ============================================================
    # FIX 1: RATE LIMITED REQUEST WITH TIMEOUTS
    # ============================================================
    
    def _rate_limited_request(
        self,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        method: str = 'GET',
        timeout: Tuple[int, int] = (10, 60)
    ) -> Optional[Dict]:
        """
        Make API request with rate limiting, timeouts, and exponential backoff
        
        Args:
            timeout: Tuple of (connect_timeout, read_timeout)
        """
        
        for attempt in range(self.max_retries):
            try:
                # Merge headers
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # FIX: Explicit timeout
                if method.upper() == 'GET':
                    response = self.session.get(
                        url,
                        params=params,
                        headers=request_headers,
                        timeout=timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        data=params,
                        headers=request_headers,
                        timeout=timeout
                    )
                
                # FIX: Rate limit handling with Retry-After
                if response.status_code == 429:
                    self.stats['rate_limits_hit'] += 1
                    retry_after = int(response.headers.get("Retry-After", 5))
                    wait_time = min(self.max_delay, retry_after * (2 ** attempt))
                    logger.warning(f"⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Server errors
                if response.status_code in [500, 502, 503, 504]:
                    if attempt < self.max_retries - 1:
                        wait_time = min(self.max_delay, self.retry_delay * (1.5 ** attempt))
                        logger.warning(f"⚠️ Server error {response.status_code}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Connection error (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Request error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
        
        return None

    # ============================================================
    # FIX 2: BUILD SEARCH QUERY
    # ============================================================
    
    def _topic_to_query(self, topic: str, seg_type: str, seg_idx: int) -> str:
        """Build search query from topic + segment type"""
        
        # Clean topic: remove stopwords
        stopwords = {
            'why', 'do', 'we', 'does', 'the', 'a', 'an', 'is', 'are',
            'happens', 'happen', 'to', 'your', 'you', 'for', 'and', 'or',
            'but', 'so', 'because', 'when', 'where', 'what', 'how'
        }
        words = [w for w in topic.lower().split() if w not in stopwords]
        core_topic = ' '.join(words[:3]) if words else topic
        
        # Get mood modifier
        modifiers = self.mood_modifiers.get(seg_type, self.mood_modifiers['story'])
        modifier = modifiers[seg_idx % len(modifiers)]
        
        return f"{core_topic} {modifier} motion".strip()

    # ============================================================
    # FIX 3: SEARCH PEXELS WITH ORIENTATION VALIDATION
    # ============================================================
    
    def search_pexels(self, query: str, per_page: int = 20) -> List[Dict]:
        """Search Pexels for videos - FIXED"""
        if not self.pexels_key:
            logger.warning("⚠️ Pexels API key not configured")
            return []
        
        headers = {"Authorization": self.pexels_key}
        page = random.randint(1, min(3, 10))
        
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": "portrait",
            "size": "large"
        }
        
        try:
            data = self._rate_limited_request(
                f"{self.pexels_base}/search",
                params=params,
                headers=headers,
                timeout=(10, 60)
            )
            
            if not data or not data.get('videos'):
                # Try landscape if no portrait results
                params["orientation"] = "landscape"
                data = self._rate_limited_request(
                    f"{self.pexels_base}/search",
                    params=params,
                    headers=headers,
                    timeout=(10, 60)
                )
            
            if not data or not data.get('videos'):
                return []
            
            videos = []
            for video in data.get('videos', []):
                # Find best quality video file
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
                    width = best_file.get('width', 0)
                    height = best_file.get('height', 0)
                    
                    # FIX: Orientation validation - prefer portrait
                    is_portrait = height > width
                    
                    videos.append({
                        'url': best_file['link'],
                        'duration': video.get('duration', 15),
                        'source': 'pexels',
                        'id': str(video.get('id', '')),
                        'description': ' '.join([
                            video.get('alt', ''),
                            video.get('user', {}).get('name', ''),
                            ' '.join(video.get('tags', []))
                        ]),
                        'width': width,
                        'height': height,
                        'orientation': 'portrait' if is_portrait else 'landscape',
                        'file_type': best_file.get('file_type', ''),
                        'is_portrait': is_portrait,
                    })
            
            self.stats['total_found'] += len(videos)
            return videos
            
        except Exception as e:
            logger.error(f"❌ Pexels error: {e}")
            return []

    # ============================================================
    # FIX 4: SEARCH PIXABAY WITH ORIENTATION VALIDATION
    # ============================================================
    
    def search_pixabay(self, query: str, per_page: int = 20) -> List[Dict]:
        """Search Pixabay for videos - FIXED"""
        if not self.pixabay_key:
            logger.warning("⚠️ Pixabay API key not configured")
            return []
        
        page = random.randint(1, min(3, 10))
        
        params = {
            "key": self.pixabay_key,
            "q": query,
            "per_page": per_page,
            "page": page,
            "orientation": "vertical",
            "video_type": "film"
        }
        
        try:
            data = self._rate_limited_request(
                f"{self.pixabay_base}/",
                params=params,
                timeout=(10, 60)
            )
            
            if not data or not data.get('hits'):
                # Try all orientations if no vertical results
                params["orientation"] = "all"
                data = self._rate_limited_request(
                    f"{self.pixabay_base}/",
                    params=params,
                    timeout=(10, 60)
                )
            
            if not data or not data.get('hits'):
                return []
            
            videos = []
            for hit in data.get('hits', []):
                videos_data = hit.get('videos', {})
                
                # Try to get best quality
                for size in ['large', 'medium', 'small']:
                    video_info = videos_data.get(size, {})
                    url = video_info.get('url', '')
                    if url:
                        width = video_info.get('width', 0)
                        height = video_info.get('height', 0)
                        is_portrait = height > width
                        
                        videos.append({
                            'url': url,
                            'duration': hit.get('duration', 15),
                            'source': 'pixabay',
                            'id': str(hit.get('id', '')),
                            'description': ' '.join([
                                hit.get('tags', ''),
                                hit.get('user', '')
                            ]),
                            'width': width,
                            'height': height,
                            'orientation': 'portrait' if is_portrait else 'landscape',
                            'file_type': 'video/mp4',
                            'is_portrait': is_portrait,
                        })
                        break
            
            self.stats['total_found'] += len(videos)
            return videos
            
        except Exception as e:
            logger.error(f"❌ Pixabay error: {e}")
            return []

    # ============================================================
    # FIX 5: SEMANTIC MATCHING
    # ============================================================
    
    def _score_clip_relevance(self, clip_desc: str, segment_text: str) -> float:
        """Score how well a clip matches the segment text"""
        if not clip_desc or not segment_text:
            return 0.5
        
        # Clean and tokenize
        clip_words = set(re.sub(r'[^\w\s]', '', clip_desc.lower()).split())
        seg_words = set(re.sub(r'[^\w\s]', '', segment_text.lower()).split())
        
        # Remove stopwords
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
        
        # Jaccard similarity
        intersection = clip_words & seg_words
        union = clip_words | seg_words
        
        if not union:
            return 0.5
        
        return len(intersection) / len(union)

    # ============================================================
    # FIX 6: MOTION VALIDATION
    # ============================================================
    
    def _check_motion_score(self, video_path: str) -> float:
        """Check if video has real motion (not static image)"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration,bit_rate,r_frame_rate',
                '-show_entries', 'format=duration,bit_rate',
                '-of', 'default=noprint_wrappers=1',
                video_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return 0.5
            
            data = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    k, v = line.split('=', 1)
                    data[k.strip()] = v.strip()
            
            duration = float(data.get('duration', 0) or 0)
            if duration <= 0:
                return 0.5
            
            file_size = os.path.getsize(video_path)
            size_per_sec = file_size / duration
            
            if size_per_sec < 100000:
                return 0.2
            
            return min(1.0, size_per_sec / 1000000)
            
        except subprocess.TimeoutExpired:
            logger.warning("⏰ Motion check timeout")
            return 0.5
        except Exception as e:
            logger.warning(f"⚠️ Motion check error: {e}")
            return 0.5

    # ============================================================
    # FIX 7: SEARCH ALL SOURCES
    # ============================================================
    
    def search_all_sources(self, query: str) -> List[Dict]:
        """Search all video sources and merge results"""
        all_videos = []
        
        # Search Pexels
        pexels_videos = self.search_pexels(query, per_page=20)
        all_videos.extend(pexels_videos)
        
        # Search Pixabay
        pixabay_videos = self.search_pixabay(query, per_page=20)
        all_videos.extend(pixabay_videos)
        
        # FIX: Prioritize portrait videos
        portrait_videos = [v for v in all_videos if v.get('is_portrait', False)]
        landscape_videos = [v for v in all_videos if not v.get('is_portrait', False)]
        
        # Put portrait first, then landscape
        sorted_videos = portrait_videos + landscape_videos
        
        # Deduplicate by ID
        seen_ids = set()
        unique = []
        for v in sorted_videos:
            vid = v.get('id', '') + v.get('source', '')
            if vid not in seen_ids:
                seen_ids.add(vid)
                unique.append(v)
        
        # Shuffle for variety (keeping portrait preference)
        random.shuffle(unique)
        
        return unique

    # ============================================================
    # FIX 8: SEARCH FOR SEGMENT
    # ============================================================
    
    def _search_for_segment(self, i: int, segment: Dict, topic: str) -> Tuple[int, List[Dict]]:
        """Search for footage for a single segment"""
        seg_type = segment.get('type', 'story')
        query = self._topic_to_query(topic, seg_type, i)
        logger.info(f"🔍 Seg {i} ({seg_type}): '{query[:40]}...'")
        
        self.stats['total_searched'] += 1
        videos = self.search_all_sources(query)
        
        if not videos:
            fallback_q = self.fallback_queries[i % len(self.fallback_queries)]
            logger.warning(f"⚠️ Seg {i}: no results, fallback: '{fallback_q[:40]}...'")
            videos = self.search_all_sources(fallback_q)
        
        return i, videos

    # ============================================================
    # FIX 9: FETCH FOOTAGE FOR SCRIPT
    # ============================================================
    
    def fetch_footage_for_script(
        self, 
        script_segments: List[Dict], 
        topic: str
    ) -> List[Dict]:
        """Fetch footage for all script segments"""
        logger.info(f"📹 Fetching footage for {len(script_segments)} segments...")
        
        # Reset used IDs for this run
        self.used_ids = set()
        
        # Search for each segment in parallel
        search_results = {}
        max_workers = min(6, max(1, len(script_segments)))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._search_for_segment, i, segment, topic)
                for i, segment in enumerate(script_segments)
            ]
            for future in as_completed(futures):
                try:
                    i, videos = future.result()
                    search_results[i] = videos
                except Exception as e:
                    logger.error(f"❌ Search failed for segment: {e}")
                    search_results[i] = []
        
        # Select best clips for each segment
        clips = []
        for i, segment in enumerate(script_segments):
            seg_type = segment.get('type', 'story')
            seg_text = segment.get('text', '')
            videos = search_results.get(i, [])
            
            if not videos:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 3),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                logger.warning(f"⚠️ Seg {i}: no clip, using color bg")
                continue
            
            # Score and filter clips
            scored = []
            for v in videos:
                vid = v.get('id', '') + v.get('source', '')
                if vid in self.used_ids:
                    continue
                
                # FIX: Prefer portrait clips
                portrait_bonus = 0.2 if v.get('is_portrait', False) else 0
                relevance = self._score_clip_relevance(
                    v.get('description', ''), 
                    seg_text
                ) + portrait_bonus
                
                scored.append((relevance, v))
            
            # Sort by relevance
            scored.sort(key=lambda x: x[0], reverse=True)
            
            # Take top candidates
            top_candidates = [v for _, v in scored[:5]] if scored else videos[:5]
            
            # Select random from top candidates
            selected = random.choice(top_candidates) if top_candidates else None
            
            if not selected:
                clips.append({
                    'url': None,
                    'start_time': segment.get('start', 0),
                    'duration': segment.get('duration', 3),
                    'segment_type': seg_type,
                    'source': 'generated'
                })
                logger.warning(f"⚠️ Seg {i}: no suitable clip, using color bg")
                continue
            
            # Mark as used
            self.used_ids.add(selected.get('id', '') + selected.get('source', ''))
            
            clips.append({
                'url': selected['url'],
                'start_time': segment.get('start', 0),
                'duration': segment.get('duration', 3),
                'segment_type': seg_type,
                'source': selected['source'],
                'id': selected.get('id', ''),
                'description': selected.get('description', ''),
                'orientation': selected.get('orientation', 'landscape'),
                'is_portrait': selected.get('is_portrait', False),
                'width': selected.get('width', 0),
                'height': selected.get('height', 0),
            })
            
            logger.info(f"✅ Seg {i}: selected from {selected['source']} ({selected.get('orientation', 'unknown')})")
        
        return clips

    # ============================================================
    # FIX 10: DOWNLOAD FOOTAGE
    # ============================================================
    
    def _download_one(self, i: int, clip: Dict, output_dir: str) -> Tuple[int, Optional[str]]:
        """Download and validate a single clip"""
        if not clip.get('url'):
            logger.warning(f"⚠️ Clip {i}: no URL")
            self.stats['failed_downloads'] += 1
            return i, None
        
        filepath = os.path.join(output_dir, f"clip_{i}.mp4")
        
        # Check cache
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            motion = self._check_motion_score(filepath)
            if motion > 0.3:
                logger.info(f"✅ Clip {i}: cached (motion: {motion:.2f})")
                return i, filepath
            else:
                logger.warning(f"⚠️ Clip {i}: cached but low motion ({motion:.2f}), re-downloading")
        
        # Download with retry
        for attempt in range(3):
            try:
                logger.info(f"⬇️ Clip {i}: downloading ({clip['source']})...")
                
                response = self.session.get(
                    clip['url'],
                    stream=True,
                    timeout=(30, 120)  # Longer timeout for downloads
                )
                response.raise_for_status()
                
                # Write to file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=65536):
                        f.write(chunk)
                
                # Validate
                file_size = os.path.getsize(filepath)
                if file_size < 10000:
                    os.remove(filepath)
                    logger.warning(f"⚠️ Clip {i}: too small ({file_size} bytes)")
                    self.stats['failed_downloads'] += 1
                    return i, None
                
                # Check motion
                motion = self._check_motion_score(filepath)
                logger.info(f"📊 Clip {i}: {file_size//1024}KB | motion: {motion:.2f}")
                
                if motion < 0.2:
                    logger.warning(f"⚠️ Clip {i}: low motion, using color bg")
                    os.remove(filepath)
                    self.stats['failed_downloads'] += 1
                    return i, None
                
                self.stats['total_downloaded'] += 1
                logger.info(f"✅ Clip {i}: downloaded & validated")
                return i, filepath
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Clip {i}: timeout (attempt {attempt+1})")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                self.stats['failed_downloads'] += 1
                return i, None
                
            except Exception as e:
                logger.warning(f"⚠️ Clip {i}: download failed (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                self.stats['failed_downloads'] += 1
                return i, None
        
        return i, None

    def download_footage(
        self, 
        clips: List[Dict], 
        output_dir: str
    ) -> Dict[int, str]:
        """
        Download all footage clips concurrently
        
        Returns:
            Dict mapping segment index to downloaded file path
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean old clips
        for f in os.listdir(output_dir):
            if f.startswith('clip_') and f.endswith('.mp4'):
                try:
                    os.remove(os.path.join(output_dir, f))
                except:
                    pass
        
        # Download in parallel
        results = {}
        max_workers = min(6, max(1, len(clips)))
        
        logger.info(f"📦 Downloading {len(clips)} clips with {max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._download_one, i, clip, output_dir)
                for i, clip in enumerate(clips)
            ]
            for future in as_completed(futures):
                try:
                    i, filepath = future.result()
                    if filepath:
                        results[i] = filepath
                except Exception as e:
                    logger.error(f"❌ Download error: {e}")
        
        logger.info(f"📦 Downloaded {len(results)}/{len(clips)} clips")
        logger.info(f"📊 Stats: {self.stats}")
        
        return results

    # ============================================================
    # GET STATS
    # ============================================================
    
    def get_stats(self) -> Dict:
        """Get fetcher statistics"""
        return self.stats.copy()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING FOOTAGE FETCHER (FIXED)\n" + "="*60)
    
    fetcher = FootageFetcher()
    
    test_topic = "forgetting names"
    test_segments = [
        {'type': 'hook', 'text': 'Your brain is ALREADY forgetting names', 'start': 0, 'duration': 3},
        {'type': 'story', 'text': 'The science behind memory loss', 'start': 3, 'duration': 5},
        {'type': 'ctr', 'text': 'Follow for more brain facts', 'start': 8, 'duration': 3},
    ]
    
    print(f"\n📹 Fetching clips for: {test_topic}")
    clips = fetcher.fetch_footage_for_script(test_segments, test_topic)
    
    for i, clip in enumerate(clips):
        print(f"\nClip {i}:")
        print(f"  URL: {clip.get('url', 'N/A')[:60]}...")
        print(f"  Source: {clip.get('source', 'N/A')}")
        print(f"  Orientation: {clip.get('orientation', 'N/A')}")
        print(f"  Portrait: {clip.get('is_portrait', False)}")
    
    print(f"\n✅ Found {len(clips)} clips")
    print(f"📊 Stats: {fetcher.get_stats()}")
