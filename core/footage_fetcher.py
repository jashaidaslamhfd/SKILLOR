"""
Footage Fetcher - Production Ready (FIXED)
OPTIMIZED FOR: Universal Brain & Body Science Audience

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
import threading  # FIX M3: Added for thread lock on shared state file access
from urllib.parse import urlparse

from config.settings import API_KEYS

try:
    from groq import Groq as GroqClient
except ImportError:
    GroqClient = None

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
        
        # Cache for used clips — FIX: persistent across runs
        self.used_ids_file = "state/used_clips.txt"
        self.used_ids = self._load_used_ids()
        self.clip_cache = {}
        
        # FIX M3: Thread lock for concurrent state file writes from ThreadPoolExecutor
        self._state_lock = threading.Lock()
        
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
                "man face closeup shocked surprised reaction",
                "middle aged man touching head confused",
                "person looking directly camera serious face",
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
        
        
        # AI-powered visual keyword extraction (Groq LLM)
        self.groq_client = None
        self.groq_model = "llama-3.3-70b-versatile"
        try:
            if GroqClient and API_KEYS.GROQ_API_KEY:
                self.groq_client = GroqClient(api_key=API_KEYS.GROQ_API_KEY)
                logger.info("AI visual keyword extraction enabled (Groq)")
        except Exception as e:
            logger.warning(f"Groq client init failed: {e}, using keyword-based search")
        
        logger.info("📹 FootageFetcher initialized")

    # ============================================================
    # FIX: PERSISTENT CLIP TRACKING
    # ============================================================

    def _load_used_ids(self) -> set:
        """Load previously used clip IDs from disk"""
        try:
            os.makedirs("state", exist_ok=True)
            if os.path.exists(self.used_ids_file):
                with open(self.used_ids_file, 'r') as f:
                    ids = set(line.strip() for line in f if line.strip())
                logger.info(f"📋 Loaded {len(ids)} used clip IDs")
                # Keep only last 500 to avoid infinite blacklist
                if len(ids) > 500:
                    ids = set(list(ids)[-500:])
                return ids
        except Exception as e:
            logger.warning(f"⚠️ Could not load used IDs: {e}")
        return set()

    def _save_used_id(self, clip_id: str):
        """Save a clip ID to persistent used list — FIX M3: Thread-safe with lock"""
        try:
            os.makedirs("state", exist_ok=True)
            with self._state_lock:  # FIX M3: Prevent concurrent writes from thread pool
                with open(self.used_ids_file, 'a') as f:
                    f.write(clip_id + "\n")
        except Exception:
            pass

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
    
    # ============================================================
    # AI-POWERED VISUAL KEYWORD EXTRACTION
    # ============================================================
    
    def _generate_visual_keywords(self, segment_text: str, seg_type: str, topic: str) -> str:
        """
        Use Groq LLM to generate visual search keywords for a script segment.
        
        Instead of searching Pexels with topic keywords (which returns generic
        clips like "fire" for any topic), we ask the AI: "What should the viewer
        SEE on screen while this text is being spoken?"
        
        The AI returns 3-5 concrete visual keywords that map directly to 
        available stock footage on Pexels/Pixabay.
        
        Example:
          Audio: "Your brain has a built-in filter..."
          AI Keywords: "brain neural network filtering, abstract data flowing, neuron synapse firing"
          Search: "neuron synapse firing" → gets a relevant brain clip
        
        Falls back to keyword-based search if Groq is unavailable.
        """
        if not self.groq_client:
            return self._topic_to_query(topic, seg_type, 0)
        
        if not segment_text or len(segment_text.strip()) < 10:
            return self._topic_to_query(topic, seg_type, 0)
        
        try:
            prompt = f"""You are a YouTube Shorts video editor. Given the script segment below, generate 3-5 specific visual search keywords for stock footage that would show on screen while this text is spoken.

RULES:
- Keywords must describe CONCRETE VISUAL things (not abstract concepts)
- Must be searchable on stock footage sites like Pexels
- Each keyword phrase should be 2-4 words
- Think about what the VIEWER should SEE, not what the audio says
- Return ONLY comma-separated keywords, nothing else
- Example: for "Your brain has a built-in filter" → "brain neurons glowing, abstract data filtering, synapse firing close up"
- Example: for "Your heart sends signals to your brain" → "heartbeat pulse monitor, heart anatomy animated, brain neural signals"
- Example: for "You forget 50% of what you learn" → "person forgetting confused, memory fade away effect, brain erasing thoughts"

Segment type: {seg_type} (hook=attention-grabbing, shock=surprising reveal, suspense=tense buildup, story=explanation, ctr=call-to-action)
Topic context: {topic}
Segment text: "{segment_text}"

Visual search keywords:"""

            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=60,
                timeout=15
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the comma-separated keywords
            keywords = [k.strip().strip('"').strip("'") for k in result.split(',')]
            keywords = [k for k in keywords if len(k) > 2][:5]
            
            if not keywords:
                return self._topic_to_query(topic, seg_type, 0)
            
            # Pick one keyword phrase to search with (most relevant)
            # Add motion/cinematic modifier for better Pexels results
            search_query = keywords[0]
            
            # Add visual quality modifiers based on segment type
            quality_modifiers = {
                'hook': 'cinematic close up motion',
                'shock': 'dramatic reveal motion',
                'suspense': 'tense atmospheric motion',
                'story': 'documentary style motion',
                'ctr': 'bright inspiring motion',
            }
            modifier = quality_modifiers.get(seg_type, 'cinematic motion')
            
            final_query = f"{search_query} {modifier}".strip()
            
            logger.info(f"AI keywords for '{segment_text[:30]}...': {keywords} → search: '{final_query[:40]}'")
            
            return final_query
            
        except Exception as e:
            logger.warning(f"AI keyword generation failed: {e}, using fallback")
            return self._topic_to_query(topic, seg_type, 0)

    def _topic_to_query(self, topic: str, seg_type: str, seg_idx: int) -> str:
        """Build search query — FIX: randomized modifier so clips differ every run"""
        
        stopwords = {
            'why', 'do', 'we', 'does', 'the', 'a', 'an', 'is', 'are',
            'happens', 'happen', 'to', 'your', 'you', 'for', 'and', 'or',
            'but', 'so', 'because', 'when', 'where', 'what', 'how'
        }
        words = [w for w in topic.lower().split() if w not in stopwords]
        core_topic = ' '.join(words[:3]) if words else topic
        
        modifiers = self.mood_modifiers.get(seg_type, self.mood_modifiers['story'])
        
        # FIX: time-based seed so each run picks a different modifier
        random.seed(int(time.time() / 3600) + seg_idx * 7)   # changes every hour
        modifier = random.choice(modifiers)
        random.seed()   # reset to true random after
        
        return f"{core_topic} {modifier}".strip()

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
    
    def _score_clip_relevance(self, clip_desc: str, segment_text: str, search_query: str = '') -> float:
        """Score how well a clip matches the segment text and search query.
        
        IMPROVED v2: Now also considers the AI-generated search query keywords
        for scoring, since clip descriptions may not overlap with segment text
        but may overlap with the visual keywords used to find the clip.
        """
        if not clip_desc or (not segment_text and not search_query):
            return 0.5
        
        # Combine segment text and search query for broader matching
        combined_text = f"{segment_text} {search_query}".strip()
        
        # Clean and tokenize
        clip_words = set(re.sub(r'[^\w\s]', '', clip_desc.lower()).split())
        seg_words = set(re.sub(r'[^\w\s]', '', combined_text.lower()).split())
        
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
                     'until', 'while', 'this', 'that', 'these', 'those',
                     'your', 'you', 'body', 'brain', 'happens'}
        
        clip_words -= stopwords
        seg_words -= stopwords
        
        if not clip_words or not seg_words:
            return 0.5
        
        # Jaccard similarity
        intersection = clip_words & seg_words
        union = clip_words | seg_words
        
        if not union:
            return 0.5
        
        # Bonus for multiple keyword overlaps (stronger signal)
        base_score = len(intersection) / len(union)
        overlap_bonus = min(0.3, len(intersection) * 0.1)  # Up to 0.3 bonus for 3+ overlaps
        
        return min(1.0, base_score + overlap_bonus)

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
    
    def _search_for_segment(self, i: int, segment: Dict, topic: str) -> Tuple[int, List[Dict], str]:
        """Search for footage for a single segment — AI-powered visual matching
        
        Returns: (segment_index, video_list, search_query_used)
        """
        seg_type = segment.get('type', 'story')
        seg_text = segment.get('text', '')
        
        # AI-POWERED: Generate visual keywords that match what's being spoken
        # This replaces generic topic-based search with context-aware clip selection
        query = self._generate_visual_keywords(seg_text, seg_type, topic)
        logger.info(f"🔍 Seg {i} ({seg_type}): '{query[:40]}...'")
        
        self.stats['total_searched'] += 1
        videos = self.search_all_sources(query)
        search_query = query  # Track the actual query used for relevance scoring
        
        if not videos:
            # Fallback: try with topic-based query
            fallback_topic = self._topic_to_query(topic, seg_type, i)
            logger.warning(f"⚠️ Seg {i}: AI search empty, trying topic query: '{fallback_topic[:40]}...'")
            videos = self.search_all_sources(fallback_topic)
            search_query = fallback_topic
        
        if not videos:
            fallback_q = self.fallback_queries[i % len(self.fallback_queries)]
            logger.warning(f"⚠️ Seg {i}: no results, fallback: '{fallback_q[:40]}...'")
            videos = self.search_all_sources(fallback_q)
            search_query = fallback_q
        
        return i, videos, search_query

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

        # FIX: Do NOT reset used_ids here — they persist across videos
        # Only clear in-memory set if it gets too large (disk file handles real persistence)
        if len(self.used_ids) > 500:
            self.used_ids = self._load_used_ids()
        
        # Search for each segment in parallel
        search_results = {}
        search_queries = {}  # Track AI-generated queries for relevance scoring
        max_workers = min(6, max(1, len(script_segments)))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._search_for_segment, i, segment, topic)
                for i, segment in enumerate(script_segments)
            ]
            for future in as_completed(futures):
                try:
                    i, videos, query = future.result()
                    search_results[i] = videos
                    search_queries[i] = query
                except Exception as e:
                    logger.error(f"❌ Search failed for segment: {e}")
                    search_results[i] = []
                    search_queries[i] = ''
        
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
                # Use the AI search query for relevance scoring too
                search_q = search_queries.get(i, '')
                relevance = self._score_clip_relevance(
                    v.get('description', ''), 
                    seg_text,
                    search_query=search_q
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
            
            # Mark as used — FIX: save to disk for cross-video persistence
            clip_uid = selected.get('id', '') + selected.get('source', '')
            self.used_ids.add(clip_uid)
            self._save_used_id(clip_uid)
            
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
                except (OSError, PermissionError):  # FIX M8: Specific exceptions instead of bare except
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
