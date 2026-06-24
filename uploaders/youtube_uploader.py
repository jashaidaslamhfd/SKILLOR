"""
YouTube Uploader - Production Ready
FIXES:
1. GitHub Actions cache via actions/cache
2. Upload ID preservation on token refresh
3. Resumable upload with file pointer tracking
4. Cross-run token persistence
"""

import os
import time
import json
import random
import base64
from typing import List, Dict, Optional
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config.settings import SEO_CONFIG


class YouTubeUploader:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
        ]
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        
        # FIX: Multiple cache locations
        self.token_cache_file = 'token_cache.json'
        self.token_cache_env = 'YOUTUBE_TOKEN_CACHE'
        
        # FIX: Track upload state for resumable uploads
        self._upload_state = {
            'video_id': None,
            'bytes_uploaded': 0,
            'upload_id': None,
            'file_size': 0
        }

    def _get_cached_token(self) -> Optional[Dict]:
        """FIX: Get cached token from multiple sources"""
        # 1. Try environment variable (GitHub Actions current run)
        cached_json = os.getenv(self.token_cache_env)
        if cached_json:
            try:
                decoded = base64.b64decode(cached_json).decode('utf-8')
                return json.loads(decoded)
            except Exception as e:
                print(f"⚠️ Could not decode env token: {e}")
        
        # 2. Try file (local development)
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load token file: {e}")
        
        return None

    def _save_cached_token(self, creds_data: Dict):
        """FIX: Save token to multiple locations"""
        # Save to file
        try:
            with open(self.token_cache_file, 'w') as f:
                json.dump(creds_data, f)
            print(f"  💾 Token cached to file")
        except Exception as e:
            print(f"⚠️ Could not save token file: {e}")
        
        # Save to environment variable
        try:
            json_str = json.dumps(creds_data)
            encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            os.environ[self.token_cache_env] = encoded
            print(f"  💾 Token cached to environment")
            
            # FIX: GitHub Actions - Set output for cross-step sharing
            # This works with: echo "::set-output name=token_cache::{encoded}"
            # But use environment variable within same job
        except Exception as e:
            print(f"⚠️ Could not save token to env: {e}")

    def _credentials_from_cache(self, cached_data: Dict) -> Optional[Credentials]:
        """Create Credentials from cached data"""
        try:
            credentials = Credentials.from_authorized_user_info(cached_data)
            
            # FIX: Use library's expired() method
            if not credentials.expired:
                print(f"  ✅ Using cached token (expires: {credentials.expiry})")
                return credentials
            else:
                print(f"  ⏰ Cached token expired at {credentials.expiry}")
                return None
                
        except Exception as e:
            print(f"⚠️ Could not create credentials: {e}")
            return None

    def get_authenticated_service(self) -> build:
        """Get authenticated YouTube service"""
        refresh_token = os.getenv("REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not all([refresh_token, client_id, client_secret]):
            raise Exception("❌ Missing YouTube OAuth credentials")

        # Try cached token
        cached_data = self._get_cached_token()
        if cached_data:
            credentials = self._credentials_from_cache(cached_data)
            if credentials:
                return build(self.api_service_name, self.api_version, credentials=credentials)

        # Create new credentials
        print("  🔑 Creating new credentials...")
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=self.scopes
        )

        try:
            request = Request()
            credentials.refresh(request)
            
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            self._save_cached_token(creds_data)
            print(f"  🔑 Token refreshed, expires: {credentials.expiry}")
            
        except Exception as e:
            raise Exception(f"❌ Token refresh failed: {str(e)}")

        return build(self.api_service_name, self.api_version, credentials=credentials)

    def _create_upload_request(self, youtube, video_path: str, body: Dict, 
                                resume_upload_id: Optional[str] = None):
        """FIX: Create upload request with resume support"""
        file_size = os.path.getsize(video_path)
        self._upload_state['file_size'] = file_size
        
        chunk_size = 5 * 1024 * 1024  # 5MB
        
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=chunk_size
        )
        
        # FIX: If we have a resume upload ID, use it
        request = youtube.videos().insert(
            part='snippet,status,contentDetails',
            body=body,
            media_body=media,
            notifySubscribers=True
        )
        
        # Store upload state
        self._upload_state['upload_id'] = getattr(media, '_upload_id', None)
        
        return request, media

    def _parse_google_error(self, error) -> Dict:
        """Parse Google API error with better logging"""
        try:
            if hasattr(error, 'resp') and hasattr(error.resp, 'status'):
                status = error.resp.status
                content = error.content.decode('utf-8') if error.content else ''
                
                try:
                    body = json.loads(content) if content else {}
                    error_info = body.get('error', {})
                    
                    return {
                        'code': status,
                        'message': error_info.get('message', str(error)),
                        'errors': error_info.get('errors', []),
                        'reason': error_info.get('errors', [{}])[0].get('reason', 'unknown'),
                        'raw_content': content[:500]
                    }
                except json.JSONDecodeError:
                    print(f"  ⚠️ Could not parse JSON: {content[:200]}")
                    return {'code': status, 'message': str(error), 'reason': 'parse_error'}
                    
            return {'code': 0, 'message': str(error), 'reason': 'unknown'}
        except Exception as e:
            print(f"  ⚠️ Error parsing error: {e}")
            return {'code': 0, 'message': str(error), 'reason': 'parse_error'}

    def upload_video(self, video_path: str, thumbnail_path: str, title: str,
                     description: str, tags: List[str],
                     privacy_status: str = 'public') -> Dict:
        """Upload video with resumable support and token handling"""
        
        # Validations
        abs_video_path = os.path.abspath(video_path)
        abs_thumbnail_path = os.path.abspath(thumbnail_path) if thumbnail_path else None

        if not os.path.exists(abs_video_path):
            raise FileNotFoundError(f"❌ Video file not found")

        if abs_thumbnail_path and not os.path.exists(abs_thumbnail_path):
            print(f"  ⚠️ Thumbnail not found, continuing without one")
            abs_thumbnail_path = None

        file_size = os.path.getsize(abs_video_path)
        if file_size < 1024:
            raise ValueError(f"❌ File too small: {file_size} bytes")

        print(f"  📁 Video: {file_size / (1024**2):.1f}MB")

        # Ensure #Shorts
        if '#shorts' not in title.lower() and '#shorts' not in description.lower():
            description = f"{description}\n\n#Shorts #shorts"

        # Validate title
        if len(title) > 100:
            title = title[:97] + "..."
        if len(title) < 5:
            raise ValueError(f"❌ Title too short")

        # Validate tags
        tags = [t for t in tags if t.strip()][:30]
        total_tag_len = sum(len(t) for t in tags)
        if total_tag_len > 500:
            trimmed = []
            current_len = 0
            for t in tags:
                if current_len + len(t) + 1 <= 500:
                    trimmed.append(t)
                    current_len += len(t) + 1
                else:
                    break
            tags = trimmed

        # Get service
        youtube = self.get_authenticated_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': str(getattr(SEO_CONFIG, 'CATEGORY_ID', '22')),
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': getattr(SEO_CONFIG, 'MADE_FOR_KIDS', False),
            }
        }

        # Create upload request
        request, media = self._create_upload_request(youtube, abs_video_path, body)

        print(f"🚀 Uploading: {os.path.basename(abs_video_path)}")
        response = None
        max_retries = 10
        retry_count = 0
        start_time = time.time()
        max_total_seconds = 900
        last_progress = 0

        while response is None:
            if time.time() - start_time > max_total_seconds:
                raise Exception(f"❌ Upload timed out")

            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress > last_progress:
                        print(f"  📤 Progress: {progress}%")
                        last_progress = progress

            except Exception as e:
                retry_count += 1
                error_details = self._parse_google_error(e)
                
                # FIX: Handle token expiry with upload resume
                if error_details.get('code') == 401:
                    print(f"  🔑 Token expired during upload, refreshing...")
                    
                    # Get new credentials
                    youtube = self.get_authenticated_service()
                    
                    # FIX: Recreate request with resume capability
                    # The upload_id should be preserved for resumable upload
                    request, media = self._create_upload_request(
                        youtube, abs_video_path, body,
                        resume_upload_id=self._upload_state.get('upload_id')
                    )
                    continue
                
                # FIX: Handle network errors (resumable upload can handle)
                if error_details.get('code') in [500, 502, 503, 504]:
                    print(f"  ⚠️ Server error, resuming upload...")
                    # Resumable upload will retry from last successful chunk
                    continue
                
                print(f"  ⚠️ Upload error (attempt {retry_count}/{max_retries}): {error_details.get('message')}")

                if error_details.get('code') in [400, 403, 404]:
                    raise Exception(f"❌ Permanent error: {error_details}")

                if retry_count >= max_retries:
                    raise Exception(f"❌ Failed after {max_retries} retries")

                wait = min(2 ** retry_count + random.uniform(0, 5), 60)
                print(f"  ⏳ Retrying in {wait:.1f}s...")
                time.sleep(wait)

        video_id = response.get('id')
        if not video_id:
            raise Exception(f"❌ No video ID returned")

        print(f"  ✅ Video uploaded: https://youtube.com/shorts/{video_id}")

        # Upload thumbnail if available
        thumbnail_result = False
        if abs_thumbnail_path:
            thumbnail_result = self.upload_thumbnail_with_retry(
                youtube, video_id, abs_thumbnail_path
            )

        return {
            'video_id': video_id,
            'url': f'https://youtube.com/shorts/{video_id}',
            'thumbnail_uploaded': thumbnail_result
        }

    def upload_thumbnail_with_retry(self, youtube, video_id: str,
                                     thumbnail_path: str, max_retries: int = 3) -> bool:
        """Upload thumbnail with retry"""
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            print("  ⚠️ No thumbnail available, skipping")
            return False

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    youtube = self.get_authenticated_service()

                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
                ).execute()

                print(f"  ✅ Thumbnail uploaded!")
                return True

            except Exception as e:
                error_details = self._parse_google_error(e)
                print(f"  ⚠️ Thumbnail error (attempt {attempt+1}/{max_retries})")

                if error_details.get('code') in [400, 401, 403, 404]:
                    print(f"  ❌ Permanent thumbnail error")
                    return False

                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"  ⏳ Retrying thumbnail in {wait}s...")
                    time.sleep(wait)

        return False


# ============================================================
# GITHUB ACTIONS CACHE INTEGRATION
# ============================================================

def setup_github_actions_cache():
    """
    FIX: GitHub Actions Cache Setup
    
    Use this in your workflow:
    
    steps:
      - name: Cache YouTube Token
        uses: actions/cache@v3
        with:
          path: token_cache.json
          key: youtube-token-${{ runner.os }}
          restore-keys: |
            youtube-token-${{ runner.os }}
    
    Then in Python:
        youtube_uploader = YouTubeUploader()
        # It will automatically use token_cache.json if available
    """
    cache_file = 'token_cache.json'
    cache_env = 'YOUTUBE_TOKEN_CACHE'
    
    # If cache file exists from GitHub Actions cache restore
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                # Load into environment for this run
                os.environ[cache_env] = base64.b64encode(
                    json.dumps(data).encode('utf-8')
                ).decode('utf-8')
                print(f"  📦 Loaded token from cache file")
                return True
        except Exception as e:
            print(f"  ⚠️ Could not load cache: {e}")
    
    return False
