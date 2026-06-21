import os
import time
import json
import random
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config.settings import SEO_CONFIG


class YouTubeUploader:
    def __init__(self):
        # FIX: invalid_scope errors happen when you request MORE scopes
        # during token refresh than were originally granted when the
        # REFRESH_TOKEN was created. A refresh token is locked to the
        # scopes consented to at authorization time — adding extra scopes
        # later (even broader ones) makes Google reject the refresh
        # entirely. 'youtube.upload' alone covers both video upload and
        # thumbnail upload, so we only request that.
        self.scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
        ]
        self.api_service_name = 'youtube'
        self.api_version = 'v3'

    def get_authenticated_service(self):
        refresh_token = os.getenv("REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not all([refresh_token, client_id, client_secret]):
            raise Exception("❌ Missing YouTube OAuth credentials in GitHub Secrets.\n"
                          "Required: REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET")

        # FIX: Create credentials with auto-refresh capability
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=self.scopes
        )

        # FIX: Force refresh token to get valid access token
        try:
            credentials.refresh(Request())
            print(f"  🔑 Token refreshed, expires: {credentials.expiry}")
        except Exception as e:
            raise Exception(f"❌ Token refresh failed: {str(e)}\n"
                          "Check: REFRESH_TOKEN valid? Not expired? Re-authorize if needed.")

        return build(self.api_service_name, self.api_version, credentials=credentials)

    def upload_video(self, video_path: str, thumbnail_path: str, title: str,
                     description: str, tags: List[str],
                     privacy_status: str = 'public') -> Dict:
        # ═══════════════════════════════════════════════════════════
        # FIX: Pre-upload validations
        # ═══════════════════════════════════════════════════════════
        abs_video_path = os.path.abspath(video_path)
        abs_thumbnail_path = os.path.abspath(thumbnail_path)

        if not os.path.exists(abs_video_path):
            raise FileNotFoundError(f"❌ Video file not found: {abs_video_path}")
        if not os.path.exists(abs_thumbnail_path):
            raise FileNotFoundError(f"❌ Thumbnail not found: {abs_thumbnail_path}")

        # FIX: File size validation (YouTube limit: 256GB, but practical: 2GB)
        file_size = os.path.getsize(abs_video_path)
        if file_size > 256 * 1024 * 1024 * 1024:
            raise ValueError(f"❌ File too large: {file_size / (1024**3):.2f}GB (max 256GB)")
        if file_size < 1024:
            raise ValueError(f"❌ File too small: {file_size} bytes (likely corrupt)")

        print(f"  📁 Video: {file_size / (1024**2):.1f}MB | {abs_video_path}")

        # FIX: Validate #Shorts in title or description (critical for Shorts indexing)
        title_lower = title.lower()
        desc_lower = description.lower()
        if '#shorts' not in title_lower and '#shorts' not in desc_lower:
            print(f"  ⚠️ WARNING: #Shorts missing in title/description! Adding to description...")
            description = f"{description}\n\n#Shorts #shorts"
            print(f"  ✅ Added #Shorts to description")

        # FIX: Validate title length
        if len(title) > 100:
            print(f"  ⚠️ Title too long ({len(title)} chars), truncating to 100...")
            title = title[:97] + "..."
        if len(title) < 5:
            raise ValueError(f"❌ Title too short: '{title}' (min 5 chars)")

        # FIX: Validate description
        if len(description) > 5000:
            description = description[:4997] + "..."

        # FIX: Validate tags (max 500 chars total, max 30 tags)
        tags = [t for t in tags if t.strip()]
        tags = tags[:30]  # Max 30 tags
        total_tag_len = sum(len(t) for t in tags)
        if total_tag_len > 500:
            # Truncate tags to fit
            trimmed = []
            current_len = 0
            for t in tags:
                if current_len + len(t) + 1 <= 500:
                    trimmed.append(t)
                    current_len += len(t) + 1
                else:
                    break
            tags = trimmed
            print(f"  ⚠️ Tags trimmed to fit 500 char limit")

        # FIX: Get fresh service (ensures valid token)
        youtube = self.get_authenticated_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': str(getattr(SEO_CONFIG, 'CATEGORY_ID', '22')),  # 22 = People & Blogs
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': getattr(SEO_CONFIG, 'MADE_FOR_KIDS', False),
                'publishAt': None,  # Can be set for scheduled uploads
            }
        }

        # FIX: Chunked upload with explicit chunk size for large files
        chunk_size = 5 * 1024 * 1024  # 5MB chunks (good balance)
        media = MediaFileUpload(
            abs_video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=chunk_size
        )

        request = youtube.videos().insert(
            part='snippet,status,contentDetails',
            body=body,
            media_body=media,
            notifySubscribers=True
        )

        print(f"🚀 Uploading: {os.path.basename(abs_video_path)}")
        response = None
        max_retries = 10
        retry_count = 0
        start_time = time.time()
        max_total_seconds = 900  # 15 min timeout

        last_progress = 0

        while response is None:
            if time.time() - start_time > max_total_seconds:
                raise Exception(f"❌ Upload timed out after {max_total_seconds}s")

            try:
                status, response = request.next_chunk()

                if status:
                    progress = int(status.progress() * 100)
                    if progress > last_progress:
                        print(f"  📤 Progress: {progress}%")
                        last_progress = progress

            except Exception as e:
                error_str = str(e)
                retry_count += 1

                # FIX: Parse Google API error details
                error_details = self._parse_google_error(e)

                print(f"  ⚠️ Upload error (attempt {retry_count}/{max_retries}): {error_details}")

                # FIX: Don't retry on permanent errors
                if error_details.get('code') in [400, 401, 403, 404]:
                    raise Exception(f"❌ Permanent error, not retrying: {error_details}")

                if retry_count >= max_retries:
                    raise Exception(f"❌ Failed after {max_retries} retries: {error_details}")

                # FIX: Exponential backoff with jitter
                wait = min(2 ** retry_count + random.uniform(0, 5), 60)
                print(f"  ⏳ Retrying in {wait:.1f}s...")
                time.sleep(wait)

                # FIX: Refresh token on auth errors
                if error_details.get('code') == 401:
                    print(f"  🔑 Refreshing token...")
                    youtube = self.get_authenticated_service()

        video_id = response.get('id')
        if not video_id:
            raise Exception(f"❌ Upload succeeded but no video ID returned: {response}")

        print(f"  ✅ Video uploaded: https://youtube.com/shorts/{video_id}")

        # FIX: Upload thumbnail with retry
        thumbnail_result = self.upload_thumbnail_with_retry(
            youtube, video_id, abs_thumbnail_path
        )

        return {
            'video_id': video_id,
            'url': f'https://youtube.com/shorts/{video_id}',
            'thumbnail_uploaded': thumbnail_result
        }

    def _parse_google_error(self, error) -> Dict:
        """FIX: Extract detailed error info from Google API exceptions"""
        try:
            if hasattr(error, 'resp') and hasattr(error.resp, 'status'):
                status = error.resp.status
                try:
                    body = json.loads(error.content.decode('utf-8'))
                    error_info = body.get('error', {})
                    return {
                        'code': status,
                        'message': error_info.get('message', str(error)),
                        'errors': error_info.get('errors', []),
                        'reason': error_info.get('errors', [{}])[0].get('reason', 'unknown')
                    }
                except:
                    return {'code': status, 'message': str(error), 'reason': 'unknown'}
            return {'code': 0, 'message': str(error), 'reason': 'unknown'}
        except:
            return {'code': 0, 'message': str(error), 'reason': 'unknown'}

    def upload_thumbnail_with_retry(self, youtube, video_id: str,
                                     thumbnail_path: str, max_retries: int = 3) -> bool:
        """FIX: Thumbnail upload with separate retry logic"""
        for attempt in range(max_retries):
            try:
                # FIX: Refresh credentials before thumbnail upload
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
                print(f"  ⚠️ Thumbnail error (attempt {attempt+1}/{max_retries}): {error_details.get('message', str(e))}")

                if error_details.get('code') in [400, 401, 403, 404]:
                    print(f"  ❌ Permanent thumbnail error, skipping...")
                    return False

                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"  ⏳ Retrying thumbnail in {wait}s...")
                    time.sleep(wait)

        print(f"  ❌ Thumbnail upload failed after {max_retries} attempts")
        return False

    # Keep old method for backward compatibility
    def upload_thumbnail(self, youtube, video_id: str, thumbnail_path: str):
        self.upload_thumbnail_with_retry(youtube, video_id, thumbnail_path)
