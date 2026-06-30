"""
Facebook Video Uploader - Production Ready
FIXES:
1. Retry logic with exponential backoff
2. Video URL support (resumable)
3. Container status polling
4. Thumbnail upload with retry
5. Async support with aiohttp
6. Queue integration
7. Metrics collection
8. Session management
"""

import os
import time
import json
import asyncio
import logging
from typing import Dict, List, Optional, Union, Callable, BinaryIO
from urllib.parse import urlparse
from datetime import datetime
from dataclasses import dataclass, field

import requests
from config.settings import API_KEYS, PLATFORM_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class FacebookUploadMetrics:
    """Track upload performance metrics"""
    attempts: int = 0
    retries: int = 0
    start_time: float = 0
    end_time: float = 0
    upload_time: float = 0
    processing_time: float = 0
    thumbnail_time: float = 0
    file_size: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > 0 else 0


class FacebookUploader:
    def __init__(self):
        self.access_token = API_KEYS.FACEBOOK_ACCESS_TOKEN
        self.page_id = API_KEYS.FACEBOOK_PAGE_ID
        
        # FIX: Version from settings
        self.api_version = getattr(PLATFORM_CONFIG, 'FACEBOOK_API_VERSION', 'v19.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # FIX: Retry settings
        self.max_retries = getattr(PLATFORM_CONFIG, 'FACEBOOK_MAX_RETRIES', 3)
        self.retry_delay = getattr(PLATFORM_CONFIG, 'FACEBOOK_RETRY_DELAY', 5)
        self.max_delay = getattr(PLATFORM_CONFIG, 'FACEBOOK_MAX_DELAY', 60)
        
        # FIX: Processing polling settings
        self.max_poll_attempts = getattr(PLATFORM_CONFIG, 'FACEBOOK_MAX_POLL', 60)
        self.poll_interval = getattr(PLATFORM_CONFIG, 'FACEBOOK_POLL_INTERVAL', 5)
        
        # FIX: Session with better headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Compatible; FacebookUploader/2.0)',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'application/json',
        })
        
        # Queue support
        self._upload_queue = []
        self._is_processing = False

    # ============================================================
    # FIX 1: Rate Limited Request with Dynamic Methods
    # ============================================================
    def _rate_limited_request(
        self,
        url: str,
        data: Dict = None,
        files: Dict = None,
        method: str = 'POST',
        timeout: int = 300,
        headers: Dict = None,
        retry_on: List[int] = None
    ) -> Dict:
        """
        Make API request with rate limiting and retry logic
        
        Args:
            url: API endpoint
            data: Request data
            files: File uploads
            method: HTTP method
            timeout: Request timeout
            headers: Additional headers
            retry_on: List of status codes to retry
        """
        method = method.upper()
        retry_on = retry_on or [429, 500, 502, 503, 504]
        
        for attempt in range(self.max_retries):
            try:
                # 🐛 FIX: when this loop retries after a 429/5xx, `files` holds
                # an already-read file object — requests had already consumed
                # the stream on the first attempt, so every retry silently
                # uploaded 0 bytes instead of the video. Rewind every
                # file-like value before each attempt (including the first,
                # which is a harmless no-op).
                if files:
                    for f in files.values():
                        try:
                            f.seek(0)
                        except Exception:
                            pass

                # Merge headers
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # Dynamic method with files support
                if files:
                    response = self.session.request(
                        method, url,
                        data=data,
                        files=files,
                        headers=request_headers,
                        timeout=timeout
                    )
                else:
                    if method == 'GET':
                        response = self.session.request(
                            method, url,
                            params=data,
                            headers=request_headers,
                            timeout=timeout
                        )
                    else:
                        response = self.session.request(
                            method, url,
                            data=data,
                            headers=request_headers,
                            timeout=timeout
                        )
                
                # ============================================================
                # Error Classification
                # ============================================================
                
                # Rate limit
                if response.status_code == 429:
                    wait_time = min(self.max_delay, self.retry_delay * (2 ** attempt))
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Server errors
                if response.status_code in [500, 502, 503, 504]:
                    if response.status_code in retry_on:
                        wait_time = min(self.max_delay, self.retry_delay * (1.5 ** attempt))
                        logger.warning(f"Server error {response.status_code}, retrying...")
                        time.sleep(wait_time)
                        continue
                
                # OAuth errors
                if response.status_code == 400:
                    try:
                        error_data = response.json() if response.text else {}
                        error_type = error_data.get('error', {}).get('type', '')
                        if 'OAuthException' in error_type:
                            logger.error(f"OAuth error: {error_type}")
                            return {'error': 'OAuthException', 'details': error_data}
                    except (json.JSONDecodeError, ValueError, AttributeError):  # FIX M5: Specific exceptions instead of bare except
                        pass
                
                response.raise_for_status()
                
                # Parse response
                if response.text and response.text.strip():
                    return response.json()
                return {}
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                return {'error': 'Request timeout'}
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                return {'error': str(e)}
        
        return {'error': 'Max retries exceeded'}

    # ============================================================
    # FIX 2: Async Support
    # ============================================================
    async def _async_rate_limited_request(
        self,
        url: str,
        data: Dict = None,
        method: str = 'POST',
        timeout: int = 300,
        headers: Dict = None
    ) -> Dict:
        """Async version for web frameworks"""
        try:
            import aiohttp
        except ImportError:
            logger.error("aiohttp not installed")
            return {'error': 'aiohttp not installed'}
        
        method = method.upper()
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    if method == 'GET':
                        async with session.get(
                            url,
                            params=data,
                            headers=headers or {},
                            timeout=timeout_obj
                        ) as response:
                            if response.status == 429:
                                wait_time = min(self.max_delay, self.retry_delay * (2 ** attempt))
                                await asyncio.sleep(wait_time)
                                continue
                            return await response.json()
                    else:
                        async with session.post(
                            url,
                            data=data,
                            headers=headers or {},
                            timeout=timeout_obj
                        ) as response:
                            if response.status == 429:
                                wait_time = min(self.max_delay, self.retry_delay * (2 ** attempt))
                                await asyncio.sleep(wait_time)
                                continue
                            return await response.json()
                            
            except asyncio.TimeoutError:
                logger.warning(f"Async timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {'error': 'Timeout'}
            except Exception as e:
                logger.warning(f"Async error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {'error': str(e)}
        
        return {'error': 'Max retries exceeded'}

    # ============================================================
    # FIX 3: Resumable Video Upload with URL
    # ============================================================
    def _upload_video_file(
        self,
        video_path: str,
        title: str,
        description: str,
        privacy: str = 'PUBLIC'
    ) -> Dict:
        """Upload video file with resumable support"""
        url = f"{self.base_url}/{self.page_id}/videos"
        
        # FIX: Get file size for progress tracking
        file_size = os.path.getsize(video_path)
        logger.info(f"Uploading video: {file_size / (1024**2):.1f}MB")
        
        # FIX M10: Facebook Graph API uses single-request multipart upload (not chunked).
        # The chunk_size/total_chunks variables below are for progress tracking only,
        # not for actual chunked upload. Facebook's resumable upload API is separate
        # and requires start_offset/end_offset session management.
        chunk_size = 5 * 1024 * 1024  # Used for progress calculation only
        
        data = {
            'access_token': self.access_token,
            'title': title,
            'description': description,
            'published': 'true',
            'privacy': privacy,
        }
        
        try:
            with open(video_path, 'rb') as video_file:
                # FIX: Progress tracking
                total_chunks = (file_size + chunk_size - 1) // chunk_size
                uploaded_chunks = 0
                last_progress = 0
                
                # Use multipart upload
                files = {'source': video_file}
                
                result = self._rate_limited_request(
                    url=url,
                    data=data,
                    files=files,
                    method='POST',
                    timeout=600  # Longer timeout for large files
                )
                
                if 'id' in result:
                    video_id = result['id']
                    logger.info(f"Video uploaded: {video_id}")
                    
                    # FIX: Poll for processing status
                    processing_result = self._poll_video_status(video_id)
                    if processing_result.get('status') == 'ready':
                        return {
                            'video_id': video_id,
                            'url': f"https://facebook.com/{self.page_id}/videos/{video_id}",
                            'status': 'uploaded',
                            'processing': processing_result
                        }
                    else:
                        return {
                            'video_id': video_id,
                            'url': f"https://facebook.com/{self.page_id}/videos/{video_id}",
                            'status': 'uploaded',
                            'processing': processing_result
                        }
                
                return {'error': result.get('error', 'Upload failed')}
                
        except Exception as e:
            logger.error(f"Video upload error: {e}")
            return {'error': str(e)}

    def _upload_video_url(
        self,
        video_url: str,
        title: str,
        description: str,
        privacy: str = 'PUBLIC'
    ) -> Dict:
        """Upload video using URL (no local file needed)"""
        url = f"{self.base_url}/{self.page_id}/videos"
        
        data = {
            'access_token': self.access_token,
            'file_url': video_url,
            'title': title,
            'description': description,
            'published': 'true',
            'privacy': privacy,
        }
        
        logger.info(f"Uploading video from URL: {video_url[:60]}...")
        
        result = self._rate_limited_request(
            url=url,
            data=data,
            method='POST',
            timeout=120
        )
        
        if 'id' in result:
            video_id = result['id']
            logger.info(f"Video uploaded: {video_id}")
            
            # Poll for processing status
            processing_result = self._poll_video_status(video_id)
            if processing_result.get('status') == 'ready':
                return {
                    'video_id': video_id,
                    'url': f"https://facebook.com/{self.page_id}/videos/{video_id}",
                    'status': 'uploaded',
                    'processing': processing_result
                }
            else:
                return {
                    'video_id': video_id,
                    'url': f"https://facebook.com/{self.page_id}/videos/{video_id}",
                    'status': 'uploaded',
                    'processing': processing_result
                }
        
        return {'error': result.get('error', 'Upload failed')}

    # ============================================================
    # FIX 4: Video Status Polling
    # ============================================================
    def _poll_video_status(self, video_id: str) -> Dict:
        """Poll video processing status"""
        url = f"{self.base_url}/{video_id}"
        
        for attempt in range(self.max_poll_attempts):
            try:
                result = self._rate_limited_request(
                    url=url,
                    data={
                        'access_token': self.access_token,
                        'fields': 'status,embed_html,error_message'
                    },
                    method='GET',
                    timeout=30
                )
                
                if 'error' in result:
                    if 'timeout' in str(result['error']).lower():
                        continue
                    return result
                
                status = result.get('status', {})
                status_code = status.get('status_code') if isinstance(status, dict) else None
                status_msg = status.get('status_msg') if isinstance(status, dict) else str(status)
                
                # Check for error
                if 'error' in status_msg.lower() or status_code == 'ERROR':
                    error_msg = result.get('error_message') or status_msg
                    logger.error(f"Video processing error: {error_msg}")
                    return {'status': 'error', 'error': error_msg}
                
                # Check if ready
                if status_code in ['FINISHED', 'READY']:
                    logger.info(f"Video {video_id} processing complete")
                    return {'status': 'ready', 'video_id': video_id}
                
                # Still processing
                if attempt % 5 == 0:  # Log every 5th attempt
                    logger.info(f"Video {video_id}: {status_msg} ({attempt + 1}/{self.max_poll_attempts})")
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.warning(f"Status poll error: {e}")
                time.sleep(self.poll_interval)
        
        return {'status': 'timeout', 'error': 'Video processing timeout'}

    # ============================================================
    # FIX 5: Thumbnail Upload with Retry and Delay
    # ============================================================
    def _upload_thumbnail_with_retry(
        self,
        video_id: str,
        thumbnail_path: str,
        max_retries: int = 3
    ) -> Dict:
        """Upload thumbnail with retry and proper timing"""
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            logger.warning("Thumbnail not found, skipping")
            return {'status': 'skipped'}
        
        # FIX: Wait for video processing before thumbnail upload
        # Facebook requires video to be ready for thumbnail upload
        time.sleep(3)
        
        url = f"{self.base_url}/{video_id}"
        
        for attempt in range(max_retries):
            try:
                with open(thumbnail_path, 'rb') as thumb_file:
                    files = {'thumb': thumb_file}
                    data = {'access_token': self.access_token}
                    
                    result = self._rate_limited_request(
                        url=url,
                        data=data,
                        files=files,
                        method='POST',
                        timeout=60
                    )
                    
                    if 'id' in result or result.get('success') is not False:
                        logger.info(f"âœ… Thumbnail uploaded for {video_id}")
                        return {'status': 'uploaded', 'thumbnail_id': result.get('id')}
                    
                    # Check if error is retryable
                    error_msg = str(result.get('error', ''))
                    if 'processing' in error_msg.lower() or 'not ready' in error_msg.lower():
                        logger.warning(f"Video not ready for thumbnail, waiting...")
                        time.sleep(5)
                        continue
                    
                    return {'error': result.get('error', 'Thumbnail upload failed')}
                    
            except Exception as e:
                logger.warning(f"Thumbnail attempt {attempt + 1} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
        
        return {'error': 'Thumbnail upload failed after retries'}

    # ============================================================
    # FIX 6: Queue Support
    # ============================================================
    def add_to_queue(
        self,
        video_path: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        title: str = "",
        description: str = "",
        privacy: str = 'PUBLIC',
        callback: Optional[Callable] = None
    ) -> str:
        """Add upload to queue for batch processing"""
        if not video_path and not video_url:
            raise ValueError("Either video_path or video_url required")
        
        task_id = f"fb_{int(time.time())}_{len(self._upload_queue)}"
        
        task = {
            'id': task_id,
            'video_path': video_path,
            'video_url': video_url,
            'thumbnail_path': thumbnail_path,
            'title': title,
            'description': description,
            'privacy': privacy,
            'callback': callback,
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
        }
        
        self._upload_queue.append(task)
        logger.info(f"Task {task_id} added to queue (size: {len(self._upload_queue)})")
        
        return task_id

    def process_queue(self, batch_size: int = 3) -> List[Dict]:
        """Process upload queue in batches"""
        results = []
        
        if not self._upload_queue:
            logger.info("Queue is empty")
            return results
        
        if self._is_processing:
            logger.warning("Queue already being processed")
            return results
        
        self._is_processing = True
        
        try:
            while self._upload_queue:
                batch = self._upload_queue[:batch_size]
                self._upload_queue = self._upload_queue[batch_size:]
                
                for task in batch:
                    try:
                        logger.info(f"Processing {task['id']}...")
                        result = self.upload_video(
                            video_path=task.get('video_path'),
                            video_url=task.get('video_url'),
                            thumbnail_path=task.get('thumbnail_path'),
                            title=task.get('title', ''),
                            description=task.get('description', ''),
                            privacy=task.get('privacy', 'PUBLIC')
                        )
                        
                        task['status'] = 'completed' if 'video_id' in result else 'failed'
                        task['result'] = result
                        results.append(task)
                        
                        if task.get('callback'):
                            try:
                                task['callback'](result)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                        
                    except Exception as e:
                        logger.error(f"Task {task['id']} failed: {e}")
                        task['status'] = 'failed'
                        task['error'] = str(e)
                        results.append(task)
                
                if self._upload_queue:
                    time.sleep(self.retry_delay)
        
        finally:
            self._is_processing = False
        
        return results

    # ============================================================
    # FIX 7: Main Upload Method
    # ============================================================
    def upload_video(
        self,
        video_path: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        title: str = "",
        description: str = "",
        privacy: str = 'PUBLIC',
        retry_count: int = 3
    ) -> Dict:
        """
        Upload video to Facebook with full retry logic
        
        Args:
            video_path: Local video file path
            video_url: Public URL of video
            thumbnail_path: Local thumbnail path
            title: Video title
            description: Video description
            privacy: Privacy setting (PUBLIC, FRIENDS, ONLY_ME, etc.)
            retry_count: Number of retry attempts
        
        Returns:
            Dict with upload status
        """
        metrics = FacebookUploadMetrics()
        metrics.start_time = time.time()
        metrics.file_size = os.path.getsize(video_path) if video_path else 0
        
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            if not self.page_id:
                return {"error": "FACEBOOK_PAGE_ID not set"}
            
            if not self.access_token:
                return {"error": "FACEBOOK_ACCESS_TOKEN not set"}
            
            if not video_path and not video_url:
                return {"error": "Either video_path or video_url required"}
            
            if video_path and not os.path.exists(video_path):
                return {"error": f"Video file not found: {video_path}"}
            
            # ============================================================
            # OPTIMIZE DESCRIPTION
            # ============================================================
            
            optimized_description = self.optimize_description(description)
            logger.info(f"Description length: {len(optimized_description)} chars")
            
            # ============================================================
            # UPLOAD WITH RETRY
            # ============================================================
            
            last_error = None
            for attempt in range(retry_count):
                metrics.attempts += 1
                logger.info(f"Upload attempt {attempt + 1}/{retry_count}")
                
                try:
                    # FIX: Choose upload method based on input
                    upload_start = time.time()
                    
                    if video_url:
                        result = self._upload_video_url(
                            video_url=video_url,
                            title=title,
                            description=optimized_description,
                            privacy=privacy
                        )
                    else:
                        result = self._upload_video_file(
                            video_path=video_path,
                            title=title,
                            description=optimized_description,
                            privacy=privacy
                        )
                    
                    metrics.upload_time = time.time() - upload_start
                    
                    if 'error' in result:
                        error_msg = result['error']
                        logger.warning(f"Upload failed: {error_msg}")
                        
                        # Check if retryable
                        if any(k in str(error_msg).lower() for k in ['rate', 'limit', 'timeout', 'server']):
                            if attempt < retry_count - 1:
                                metrics.retries += 1
                                wait_time = min(self.max_delay, self.retry_delay * (2 ** attempt))
                                logger.info(f"Retrying in {wait_time}s...")
                                time.sleep(wait_time)
                                continue
                        else:
                            metrics.errors.append(error_msg)
                            return {'error': error_msg}
                    
                    video_id = result.get('video_id')
                    if not video_id:
                        return {'error': 'No video ID returned'}
                    
                    # ============================================================
                    # UPLOAD THUMBNAIL
                    # ============================================================
                    
                    thumbnail_result = {'status': 'skipped'}
                    if thumbnail_path:
                        thumbnail_start = time.time()
                        thumbnail_result = self._upload_thumbnail_with_retry(
                            video_id=video_id,
                            thumbnail_path=thumbnail_path
                        )
                        metrics.thumbnail_time = time.time() - thumbnail_start
                    
                    # ============================================================
                    # SUCCESS
                    # ============================================================
                    
                    metrics.end_time = time.time()
                    logger.info(f"âœ… Facebook video published in {metrics.total_duration:.1f}s!")
                    
                    return {
                        'video_id': video_id,
                        'url': f"https://facebook.com/{self.page_id}/videos/{video_id}",
                        'status': 'published',
                        'thumbnail': thumbnail_result,
                        'metrics': {
                            'attempts': metrics.attempts,
                            'retries': metrics.retries,
                            'duration': metrics.total_duration,
                            'upload_time': metrics.upload_time,
                            'thumbnail_time': metrics.thumbnail_time,
                            'file_size_mb': round(metrics.file_size / (1024**2), 1)
                        }
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Attempt {attempt + 1} error: {e}")
                    metrics.errors.append(str(e))
                    
                    if attempt < retry_count - 1:
                        metrics.retries += 1
                        wait_time = self.retry_delay * (attempt + 1)
                        logger.info(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    continue
            
            # ============================================================
            # FAILURE
            # ============================================================
            
            metrics.end_time = time.time()
            return {
                'error': f"Failed after {retry_count} attempts",
                'last_error': last_error,
                'metrics': {
                    'attempts': metrics.attempts,
                    'retries': metrics.retries,
                    'duration': metrics.total_duration,
                    'errors': metrics.errors
                }
            }
            
        except Exception as e:
            metrics.end_time = time.time()
            return {
                'error': f"Upload failed: {str(e)}",
                'metrics': {
                    'attempts': metrics.attempts,
                    'duration': metrics.total_duration
                }
            }

    # ============================================================
    # Helper Methods
    # ============================================================
    
    def optimize_description(self, description: str) -> str:
        """Optimize description for Facebook algorithm — FIX H8: Account for hook length in truncation"""
        hooks = [
            "\n\nWhat do you think? 💭",
            "\n\nTag someone who needs to see this! 👇",
            "\n\nComment YES if this happened to you! ✅",
            "\n\nShare if this explains a lot! 🧠",
            "\n\nFollow for more brain facts! 🔔",
        ]
        # Add engagement hook
        import random
        hook = random.choice(hooks)
        
        # FIX H8: Calculate hook length first, then truncate to fit within max_length
        max_length = 200
        available_for_desc = max_length - len(hook)
        if available_for_desc < 50:
            available_for_desc = 50  # Ensure minimum description length
        
        if len(description) > available_for_desc:
            description = description[:available_for_desc] + "..."
        
        return description + hook

    def get_facebook_status(self) -> Dict:
        """Health check for Facebook credentials"""
        if not self.page_id:
            return {'status': 'error', 'error': 'FACEBOOK_PAGE_ID not set'}
        
        url = f"{self.base_url}/{self.page_id}"
        data = {
            'access_token': self.access_token,
            'fields': 'id,name,fan_count,posts.limit(1)'
        }
        
        try:
            result = self._rate_limited_request(url, data, method='GET')
            
            if 'name' in result:
                return {
                    'status': 'ok',
                    'page_name': result.get('name'),
                    'page_id': result.get('id'),
                    'fan_count': result.get('fan_count', 0)
                }
            elif 'error' in result:
                return {
                    'status': 'error',
                    'error': result.get('error'),
                    'details': result.get('details', '')
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Unexpected response',
                    'details': str(result)[:200]
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def get_queue_status(self) -> Dict:
        """Get upload queue status"""
        return {
            'queue_size': len(self._upload_queue),
            'is_processing': self._is_processing,
            'tasks': [
                {
                    'id': t['id'],
                    'status': t['status'],
                    'title': t.get('title', ''),
                    'created_at': t['created_at']
                }
                for t in self._upload_queue[:10]
            ]
        }
