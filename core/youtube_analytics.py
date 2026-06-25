"""
YouTube Analytics - Fetch Real Video Performance Data
Requires: YouTube Data API v3 with analytics scope
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from config.settings import API_KEYS


class YouTubeAnalytics:
    """Fetch YouTube video performance data"""
    
    def __init__(self):
        self.api_key = API_KEYS.YOUTUBE_API_KEY
        self.client_id = API_KEYS.GOOGLE_CLIENT_ID
        self.client_secret = API_KEYS.GOOGLE_CLIENT_SECRET
        self.refresh_token = API_KEYS.REFRESH_TOKEN
        self._init_client()
    
    def _init_client(self):
        """Initialize YouTube API client"""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            print("⚠️ YouTube Analytics not configured")
            return
        
        try:
            credentials = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=['https://www.googleapis.com/auth/youtube.readonly']
            )
            credentials.refresh(Request())
            self.youtube = build('youtube', 'v3', credentials=credentials)
            print("✅ YouTube Analytics initialized")
        except Exception as e:
            print(f"⚠️ YouTube Analytics init failed: {e}")
            self.youtube = None
    
    def get_video_stats(self, video_id: str) -> Dict:
        """Get stats for a specific video"""
        if not self.youtube:
            return {'error': 'YouTube Analytics not configured'}
        
        try:
            request = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if response.get('items'):
                item = response['items'][0]
                stats = item.get('statistics', {})
                return {
                    'video_id': video_id,
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'shares': int(stats.get('shareCount', 0)),
                    'duration': item.get('contentDetails', {}).get('duration', ''),
                }
            return {'error': 'Video not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_channel_stats(self) -> Dict:
        """Get channel-level statistics"""
        if not self.youtube:
            return {'error': 'YouTube Analytics not configured'}
        
        try:
            request = self.youtube.channels().list(
                part='statistics',
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                stats = response['items'][0].get('statistics', {})
                return {
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'views': int(stats.get('viewCount', 0)),
                    'videos': int(stats.get('videoCount', 0)),
                }
            return {'error': 'Channel not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_top_videos(self, limit: int = 10) -> List[Dict]:
        """Get top performing videos"""
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                forMine=True,
                maxResults=limit,
                order='viewCount',
                type='video'
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                stats = self.get_video_stats(video_id)
                stats['title'] = item['snippet']['title']
                videos.append(stats)
            
            return videos
            
        except Exception as e:
            print(f"⚠️ Could not fetch top videos: {e}")
            return []
