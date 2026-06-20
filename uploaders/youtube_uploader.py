import os
import time
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from config.settings import SEO_CONFIG

class YouTubeUploader:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'

    def get_authenticated_service(self):
        refresh_token = os.getenv("REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not all([refresh_token, client_id, client_secret]):
            raise Exception("❌ Missing YouTube OAuth credentials in GitHub Secrets.")

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        return build(self.api_service_name, self.api_version, credentials=credentials)

    def upload_video(self, video_path: str, thumbnail_path: str, title: str, description: str, tags: List[str], privacy_status: str = 'public') -> Dict:
        # --- FIX: Absolute Path Validation ---
        abs_video_path = os.path.abspath(video_path)
        abs_thumbnail_path = os.path.abspath(thumbnail_path)

        if not os.path.exists(abs_video_path):
            raise FileNotFoundError(f"❌ Video file not found at: {abs_video_path}")
        if not os.path.exists(abs_thumbnail_path):
            raise FileNotFoundError(f"❌ Thumbnail not found at: {abs_thumbnail_path}")

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

        # Use absolute paths here
        media = MediaFileUpload(abs_video_path, mimetype='video/mp4', resumable=True)

        request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

        print(f"🚀 Uploading: {abs_video_path}")
        response = None
        max_retries = 8
        retry_count = 0
        start_time = time.time()
        max_total_seconds = 600

        while response is None:
            if time.time() - start_time > max_total_seconds:
                raise Exception("❌ Upload timed out.")
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Progress: {int(status.progress() * 100)}%")
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries: raise Exception(f"Failed after retries: {e}")
                time.sleep(min(2 ** retry_count, 30))

        video_id = response['id']
        self.upload_thumbnail(youtube, video_id, abs_thumbnail_path)
        return {'video_id': video_id, 'url': f'https://youtube.com/watch?v={video_id}'}

    def upload_thumbnail(self, youtube, video_id: str, thumbnail_path: str):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            ).execute()
            print("✅ Thumbnail uploaded successfully!")
        except Exception as e:
            print(f"⚠️ Thumbnail error: {e}")
