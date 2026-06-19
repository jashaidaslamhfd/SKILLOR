"""Facebook Uploader with Algorithm Optimization"""

import random
import requests
from typing import Dict

from config.settings import API_KEYS


class FacebookUploader:
    def __init__(self):
        self.access_token = API_KEYS.FACEBOOK_ACCESS_TOKEN
        # FIX: FACEBOOK_PAGE_ID now exists on API_KEYS (was AttributeError before)
        self.page_id = API_KEYS.FACEBOOK_PAGE_ID
        self.base_url = "https://graph.facebook.com/v19.0"  # FIX: bumped to v19.0 (v18.0 deprecated)

    def upload_video(
        self,
        video_path: str,
        thumbnail_path: str,
        title: str,
        description: str,
    ) -> Dict:
        # FIX: fail gracefully instead of crashing the whole pipeline
        if not self.page_id:
            print("⚠️ FACEBOOK_PAGE_ID not set — skipping Facebook upload")
            return {"error": "FACEBOOK_PAGE_ID not set in environment"}
        if not self.access_token:
            print("⚠️ FACEBOOK_ACCESS_TOKEN not set — skipping Facebook upload")
            return {"error": "FACEBOOK_ACCESS_TOKEN not set in environment"}

        url = f"{self.base_url}/{self.page_id}/videos"

        data = {
            "access_token": self.access_token,
            "description": self.optimize_description(description),
            "title": title,
            "published": "true",
        }

        try:
            with open(video_path, "rb") as video_file:
                files = {"file": video_file}
                response = requests.post(url, data=data, files=files, timeout=300)
        except Exception as e:
            print(f"⚠️ Facebook upload request failed: {e}")
            return {"error": str(e)}

        result = response.json()

        if "id" in result:
            video_id = result["id"]
            self.update_thumbnail(video_id, thumbnail_path)
            return {
                "video_id": video_id,
                "url": f"https://facebook.com/watch?v={video_id}",
                "status": "uploaded",
            }

        return {"error": result.get("error", "Unknown error")}

    def update_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail"""
        url = f"{self.base_url}/{video_id}"
        try:
            with open(thumbnail_path, "rb") as f:
                requests.post(
                    url,
                    data={"access_token": self.access_token},
                    files={"thumb": f},
                    timeout=60,
                )
        except Exception as e:
            print(f"Thumbnail upload warning: {e}")

    def optimize_description(self, description: str) -> str:
        hooks = [
            "\n\nWhat do you think? 🤔",
            "\n\nTag someone who needs to see this! 👇",
            "\n\nComment 'YES' if you agree! 💯",
            "\n\nShare if this blew your mind! 🤯",
        ]
        return description[:200] + random.choice(hooks)
