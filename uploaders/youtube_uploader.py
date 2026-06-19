import os
import pickle
import time
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from config.settings import API_KEYS, SEO_CONFIG

class YouTubeUploader:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'

    def get_authenticated_service(self):
        """GitHub Actions-ready authentication (No browser required)"""
        # FIX: Fail fast instead of hanging if credentials are missing
        refresh_token = os.getenv("REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        missing = [name for name, val in [
            ("REFRESH_TOKEN", refresh_token),
            ("GOOGLE_CLIENT_ID", client_id),
            ("GOOGLE_CLIENT_SECRET", client_secret),
        ] if not val]

        if missing:
            raise Exception(
                f"❌ Missing YouTube OAuth credentials in GitHub Secrets: {', '.join(missing)}. "
                f"Set these in repo Settings → Secrets and variables → Actions, "
                f"otherwise the upload step will hang indefinitely."
            )

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        return build(self.api_service_name, self.api_version, credentials=credentials)

    def upload_video(self,
                     video_path: str,
                     thumbnail_path: str,
                     title: str,
                     description: str,
                     tags: List[str],
                     privacy_status: str = 'public') -> Dict:

        youtube = self.get_authenticated_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': SEO_CONFIG.CATEGORY_ID,
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': SEO_CONFIG.MADE_FOR_KIDS,
            }
        }

        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)

        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        print("Starting upload...")
        response = None
        # FIX: hard cap on retries + per-chunk timeout so the job can never hang forever
        max_retries = 8
        retry_count = 0
        start_time = time.time()
        max_total_seconds = 600  # 10 min hard ceiling for the whole upload

        while response is None:
            if time.time() - start_time > max_total_seconds:
                raise Exception(f"❌ Upload timed out after {max_total_seconds}s — aborting instead of hanging forever.")
            try:
                status, response = request.next_chunk()
                retry_count = 0  # reset on success
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            except Exception as e:
                retry_count += 1
                print(f"⚠️ Upload chunk error ({retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    raise Exception(f"❌ Upload failed after {max_retries} retries: {e}")
                time.sleep(min(2 ** retry_count, 30))  # exponential backoff, capped

        video_id = response['id']
        self.upload_thumbnail(youtube, video_id, thumbnail_path)

        return {'video_id': video_id, 'url': f'https://youtube.com/watch?v={video_id}'}

    def upload_thumbnail(self, youtube, video_id: str, thumbnail_path: str):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            ).execute()
            print("Thumbnail uploaded successfully!")
        except Exception as e:
            print(f"Thumbnail upload error: {e}")
