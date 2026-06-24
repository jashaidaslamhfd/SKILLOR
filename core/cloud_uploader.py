"""
Cloud Uploader — Uploads video to Cloudinary and returns public URL
REQUIRED FOR: Instagram uploads (needs public URL)
"""

import os
from typing import Optional

from config.settings import API_KEYS


class CloudUploader:
    def __init__(self):
        self.cloud_name = API_KEYS.CLOUDINARY_CLOUD_NAME
        self.api_key = API_KEYS.CLOUDINARY_API_KEY
        self.api_secret = API_KEYS.CLOUDINARY_API_SECRET
        self._configured = False

    def is_configured(self) -> bool:
        """Check if Cloudinary credentials are set"""
        return bool(self.cloud_name and self.api_key and self.api_secret)

    def _ensure_config(self):
        """Configure Cloudinary if not already configured"""
        if self._configured:
            return
        
        if not self.is_configured():
            print("⚠️ Cloudinary credentials not set")
            return
        
        try:
            import cloudinary
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=True,
            )
            self._configured = True
            print("✅ Cloudinary configured")
        except Exception as e:
            print(f"⚠️ Cloudinary config failed: {e}")

    def upload_video(self, video_path: str, public_id: Optional[str] = None) -> Optional[str]:
        """Upload video to Cloudinary and return public URL"""
        
        if not self.is_configured():
            print("⚠️ Cloudinary credentials not set")
            return None
        
        if not os.path.exists(video_path):
            print(f"⚠️ File not found: {video_path}")
            return None

        try:
            self._ensure_config()
            import cloudinary.uploader

            print(f"  ☁️ Uploading video to Cloudinary...")
            
            result = cloudinary.uploader.upload(
                video_path,
                resource_type="video",
                public_id=public_id,
                folder="youtube_shorts",
                overwrite=True,
                format="mp4",
                quality="auto",
                transformation=[
                    {'duration': '0:0:55'},
                    {'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
            
            url = result.get("secure_url")
            if url:
                print(f"  ✅ Cloudinary URL: {url[:80]}...")
                return url
            else:
                print(f"  ⚠️ No secure_url in response")
                return None
                
        except Exception as e:
            print(f"⚠️ Cloudinary upload failed: {e}")
            return None

    def upload_thumbnail(self, thumbnail_path: str, public_id: Optional[str] = None) -> Optional[str]:
        """Upload thumbnail to Cloudinary and return public URL"""
        
        if not self.is_configured():
            print("⚠️ Cloudinary credentials not set")
            return None
        
        if not os.path.exists(thumbnail_path):
            print(f"⚠️ Thumbnail not found: {thumbnail_path}")
            return None

        try:
            self._ensure_config()
            import cloudinary.uploader

            print(f"  🖼️ Uploading thumbnail to Cloudinary...")
            
            result = cloudinary.uploader.upload(
                thumbnail_path,
                resource_type="image",
                public_id=public_id,
                folder="youtube_shorts_thumbnails",
                overwrite=True,
                format="jpg",
                quality="auto"
            )
            
            url = result.get("secure_url")
            if url:
                print(f"  ✅ Thumbnail URL: {url[:60]}...")
                return url
            return None
                
        except Exception as e:
            print(f"⚠️ Cloudinary thumbnail upload failed: {e}")
            return None
