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
                    {'duration': '0:1:0'},  # FIX H12: Changed from 55s to 60s cap to match YouTube Shorts max duration
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

    # ============================================================
    # FIX M11: Cleanup method for Cloudinary resources
    # ============================================================
    def cleanup_video(self, public_id: str) -> bool:
        """Delete a video from Cloudinary by public_id to free storage.
        
        Args:
            public_id: The Cloudinary public_id (without folder prefix if included in ID)
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        if not self.is_configured():
            print("⚠️ Cloudinary credentials not set, cannot cleanup")
            return False
            
        try:
            self._ensure_config()
            import cloudinary.uploader
            
            full_id = f"youtube_shorts/{public_id}" if '/' not in public_id else public_id
            result = cloudinary.uploader.destroy(
                full_id,
                resource_type="video",
                invalidate=True  # Invalidate CDN cache
            )
            
            if result.get('result') == 'ok':
                print(f"  ✅ Cloudinary video deleted: {public_id}")
                return True
            else:
                print(f"  ⚠️ Cloudinary delete result: {result.get('result', 'unknown')}")
                return False
                
        except Exception as e:
            print(f"⚠️ Cloudinary cleanup failed: {e}")
            return False

    def cleanup_old_uploads(self, max_age_days: int = 7) -> int:
        """Delete Cloudinary videos older than max_age_days to prevent storage bloat.
        
        Args:
            max_age_days: Delete resources older than this many days
            
        Returns:
            Number of resources deleted
        """
        if not self.is_configured():
            return 0
            
        try:
            self._ensure_config()
            import cloudinary.api
            from datetime import datetime, timedelta
            
            cutoff = (datetime.now() - timedelta(days=max_age_days)).strftime('%Y-%m-%d')
            deleted = 0
            
            result = cloudinary.api.resources(
                type='upload',
                prefix='youtube_shorts/',
                resource_type='video',
                max_results=500
            )
            
            for resource in result.get('resources', []):
                created_at = resource.get('created_at', '')[:10]
                if created_at < cutoff:
                    pid = resource.get('public_id', '')
                    if self.cleanup_video(pid):
                        deleted += 1
                        
            if deleted > 0:
                print(f"  ✅ Cleaned up {deleted} old Cloudinary videos (>{max_age_days}d)")
            return deleted
            
        except Exception as e:
            print(f"⚠️ Cloudinary cleanup scan failed: {e}")
            return 0
