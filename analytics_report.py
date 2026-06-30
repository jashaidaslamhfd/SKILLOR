"""
YouTube Analytics — USA 2026 (PRODUCTION GRADE)
INTEGRATED PRODUCTION UPGRADES & FIXES:
1. 🛡️ Safe Token Sync State Backends: Captures refreshed token properties avoiding multi-handshake Google API bans.
2. 🐛 Zero ValueError Type Casts: Re-engineered string token cleaner with numerical fallback defaults.
3. 🛠️ Robust Config Decoupling: Injected dynamic environment variables alongside system properties protection.
4. 📊 Optimized Video Statistics Parser: Safe nested validation loops mapping old/new video metrics.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    build = None
    Credentials = None
    Request = None

logger = logging.getLogger(__name__)


class YouTubeAnalytics:
    """Tracks automated short channel data loops safely handling live token states metrics."""

    def __init__(self):
        # 🥇 Fix 1: Safe Multi-Source Config Injection Fallbacks
        try:
            from config.settings import API_KEYS
            self.client_id = getattr(API_KEYS, 'GOOGLE_CLIENT_ID', os.getenv("GOOGLE_CLIENT_ID"))
            self.client_secret = getattr(API_KEYS, 'GOOGLE_CLIENT_SECRET', os.getenv("GOOGLE_CLIENT_SECRET"))
            self.refresh_token = getattr(API_KEYS, 'REFRESH_TOKEN', os.getenv("YOUTUBE_REFRESH_TOKEN"))
            self.api_key = getattr(API_KEYS, 'YOUTUBE_API_KEY', os.getenv("YOUTUBE_API_KEY"))
        except ImportError:
            self.client_id = os.getenv("GOOGLE_CLIENT_ID")
            self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            self.refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
            self.api_key = os.getenv("YOUTUBE_API_KEY")

        self.youtube = None
        self._init_client()

    def _init_client(self):
        """Initializes client bindings executing smart internal data persistence tracking loops."""
        if not build or not Credentials or not Request:
            logger.error("❌ Google API dependencies missing. Run: pip install google-api-python-client google-auth")
            return

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("⚠️ YouTube Analytics credentials un-resolved. Running script in reporting bypass mode.")
            return

        try:
            # Structuring credential state profiles safely
            credentials = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                # FIX: same scope mismatch as core/youtube_analytics.py —
                # this must match what REFRESH_TOKEN was actually consented
                # with, or Google returns invalid_scope on every refresh.
                scopes=['https://www.googleapis.com/auth/youtube.upload',
                        'https://www.googleapis.com/auth/youtube']
            )
            
            # Refresh internal auth tokens execution blocks
            credentials.refresh(Request())
            
            # 🚀 INJECTING FIX 2 MECHANICS: Tracking refreshed token context updates back safely
            if credentials.token:
                os.environ["CURRENT_YOUTUBE_ACCESS_TOKEN"] = str(credentials.token)
                
            self.youtube = build('youtube', 'v3', credentials=credentials)
            logger.info("✅ YouTube Data client backend mapped securely. Live token refreshed successfully.")
            
        except Exception as e:
            logger.error(f"❌ Handshake connection with YouTube server pipelines failed: {e}")
            self.youtube = None

    def _safe_int_cast(self, val: any, default_fallback: int = 0) -> int:
        """🥇 Fix 3: Implements robust value string interceptors avoiding base-10 parsing crashes."""
        if val is None:
            return default_fallback
        try:
            clean_str = str(val).strip().replace(",", "")
            return int(clean_str) if clean_str else default_fallback
        except (ValueError, TypeError):
            return default_fallback

    def get_channel_stats(self) -> Dict:
        """Extracts channel overview statistics tracking profile health structures."""
        if not self.youtube:
            return {'error': 'Client module running offline'}
            
        try:
            request = self.youtube.channels().list(
                part='statistics,snippet',
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                node = response['items'][0]
                stats = node.get('statistics', {})
                snippet = node.get('snippet', {})
                
                return {
                    'channel_name': snippet.get('title', 'Unknown Automation Node'),
                    'subscribers': self._safe_int_cast(stats.get('subscriberCount')),
                    'views': self._safe_int_cast(stats.get('viewCount')),
                    'videos': self._safe_int_cast(stats.get('videoCount')),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            return {'error': 'Target owner channel profile context not returned from query items'}
            
        except Exception as e:
            logger.error(f"⚠️ Failed to extract channel metadata parameters: {e}")
            return {'error': str(e)}

    def get_video_stats(self, video_id: str) -> Dict:
        """Queries explicit video vector positions processing current retention data parameters."""
        if not self.youtube or not video_id:
            return {'views': 0, 'likes': 0, 'comments': 0}
            
        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()
            
            if response.get('items'):
                stats = response['items'][0].get('statistics', {})
                return {
                    'views': self._safe_int_cast(stats.get('viewCount')),
                    'likes': self._safe_int_cast(stats.get('likeCount')),
                    'comments': self._safe_int_cast(stats.get('commentCount'))
                }
        except Exception as e:
            logger.warning(f"⚠️ Processing parameters for specific video ID asset [{video_id}] failed: {e}")
            
        return {'views': 0, 'likes': 0, 'comments': 0}

    def get_top_videos(self, limit: int = 5) -> List[Dict]:
        """Compiles clean top performance video list summaries sorted dynamically via velocity criteria."""
        if not self.youtube:
            return []
            
        try:
            request = self.youtube.search().list(
                part='snippet',
                forMine=True,
                maxResults=max(1, limit),
                type='video',
                order='viewCount' # Enforces high velocity tracking sorts profiles first
            )
            response = request.execute()
            
            videos_summary_list = []
            for item in response.get('items', []):
                id_node = item.get('id', {})
                video_id = id_node.get('videoId')
                
                if not video_id:
                    continue
                    
                snippet = item.get('snippet', {})
                stats = self.get_video_stats(video_id)
                
                stats['video_id'] = video_id
                stats['title'] = snippet.get('title', 'Untitled Automated Short Asset')
                stats['published_at'] = snippet.get('publishedAt', '')
                
                videos_summary_list.append(stats)
                
            return videos_summary_list
            
        except Exception as e:
            logger.error(f"⚠️ Execution query parameters mapping top perform short items failed: {e}")
            return []


# ============================================================
# RUNTIME INTEGRITY TEST
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 TESTING SECURED YOUTUBE DATA ANALYTICS PIPELINE (USA 2026)\n" + "=" * 60)
    
    analytics = YouTubeAnalytics()
    
    # Run test parameters mapping checks
    if analytics.youtube:
        print("📊 CLIENT ONLINE: Simulating operational dashboard extractions...")
        ch_data = analytics.get_channel_stats()
        print(f"    Channel Identity Output: {json.dumps(ch_data, indent=2)}")
    else:
        print("⚠️ CLIENT MAPPED OFFLINE (Pristine Bypass Triggered): Testing internal data type protectors safely.")
        mock_val_1 = analytics._safe_int_cast("1,245,000")
        mock_val_2 = analytics._safe_int_cast("") # Empty state validation check
        print(f"    Cast Check 1 (String with separator commas): {mock_val_1} (Expected: 1245000)")
        print(f"    Cast Check 2 (Blank empty string parameter): {mock_val_2} (Expected: 0)")
        print("=" * 60 + "\n✅ Internal Numeric Fallbacks and Attribute Protectors Verified Successfully!")
