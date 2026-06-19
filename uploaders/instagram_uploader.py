"""Instagram Reels Uploader with Algorithm Optimization"""

import os
import requests
from typing import Dict, List

from config.settings import API_KEYS


class InstagramUploader:
    def __init__(self):
        self.access_token = API_KEYS.INSTAGRAM_ACCESS_TOKEN
        # FIX: INSTAGRAM_USER_ID now exists on API_KEYS (was AttributeError before)
        self.ig_user_id = API_KEYS.INSTAGRAM_USER_ID
        self.base_url = "https://graph.facebook.com/v19.0"

    def upload_reel(
        self,
        video_path: str,
        thumbnail_path: str,
        caption: str,
        hashtags: List[str],
    ) -> Dict:
        # FIX: fail gracefully instead of crashing the whole pipeline
        if not self.ig_user_id:
            print("⚠️ INSTAGRAM_USER_ID not set — skipping Instagram upload")
            return {"error": "INSTAGRAM_USER_ID not set in environment"}
        if not self.access_token:
            print("⚠️ INSTAGRAM_ACCESS_TOKEN not set — skipping Instagram upload")
            return {"error": "INSTAGRAM_ACCESS_TOKEN not set in environment"}

        # Instagram Graph API requires a publicly accessible video URL.
        # video_path must be a Cloudinary/CDN URL in production, not a local path.
        url = f"{self.base_url}/{self.ig_user_id}/media"
        optimized_caption = self.optimize_caption(caption, hashtags)

        data = {
            "access_token": self.access_token,
            "media_type": "REELS",
            "video_url": video_path,  # must be a public URL
            "caption": optimized_caption,
            "share_to_feed": "true",
        }

        try:
            response = requests.post(url, data=data, timeout=120)
            result = response.json()
        except Exception as e:
            print(f"⚠️ Instagram upload request failed: {e}")
            return {"error": str(e)}

        if "id" in result:
            creation_id = result["id"]

            publish_url = f"{self.base_url}/{self.ig_user_id}/media_publish"
            publish_data = {
                "access_token": self.access_token,
                "creation_id": creation_id,
            }
            publish_response = requests.post(publish_url, data=publish_data, timeout=60)
            publish_result = publish_response.json()

            if "id" in publish_result:
                return {
                    "media_id": publish_result["id"],
                    "url": f"https://instagram.com/reel/{publish_result['id']}",
                    "status": "published",
                }

        return {"error": result.get("error", "Upload failed")}

    def optimize_caption(self, caption: str, hashtags: List[str]) -> str:
        top_hashtags = hashtags[:5]
        return (
            f"🤯 {caption[:100]}...\n\n"
            "Save this for later! 📌\n\n.\n.\n.\n"
            + " ".join(f"#{tag.replace(' ', '')}" for tag in top_hashtags)
            + "\n\nFollow for more 👆"
        )
