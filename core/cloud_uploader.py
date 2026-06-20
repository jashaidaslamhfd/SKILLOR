"""Cloud Uploader — uploads the rendered video to Cloudinary and returns a
public URL.

WHY THIS FILE EXISTS:
Instagram's Graph API (media creation endpoint) only accepts a publicly
reachable `video_url` — it cannot accept a raw file upload like Facebook's
API can. cloudinary was already listed in requirements.txt and its API keys
were already wired into settings.py / the GitHub Actions workflow secrets,
but nothing in the codebase ever actually called Cloudinary — main.py just
handed Instagram a local file path, which Instagram's servers can never
reach. That's why Instagram uploads always failed. This module is the
missing piece that closes that gap.
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
        return bool(self.cloud_name and self.api_key and self.api_secret)

    def _ensure_config(self):
        if self._configured:
            return
        import cloudinary
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )
        self._configured = True

    def upload_video(self, video_path: str, public_id: Optional[str] = None) -> Optional[str]:
        """Uploads a local video file to Cloudinary and returns its public
        HTTPS URL, or None if upload failed / credentials aren't set."""
        if not self.is_configured():
            print("⚠️ Cloudinary credentials not set — cannot get a public URL for Instagram")
            return None
        if not os.path.exists(video_path):
            print(f"⚠️ Cloud upload skipped — file not found: {video_path}")
            return None

        try:
            self._ensure_config()
            import cloudinary.uploader

            print(f"    ☁️ Uploading {os.path.basename(video_path)} to Cloudinary...")
            result = cloudinary.uploader.upload(
                video_path,
                resource_type="video",
                public_id=public_id,
                overwrite=True,
                folder="skillor_shorts",
            )
            url = result.get("secure_url")
            if url:
                print(f"    ✅ Cloudinary URL: {url}")
            return url
        except Exception as e:
            print(f"⚠️ Cloudinary upload failed: {e}")
            return None
