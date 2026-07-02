import json, os, google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

def upload_all(video_path, thumb_path, script_data):
    title = script_data['title']
    desc = f"{script_data['voiceover'][:200]}...\n\n#babypsychology #parenting #shorts"

    # 1. YOUTUBE UPLOAD
    yt_key = json.loads(os.environ.get("YOUTUBE_JSON_KEY"))
    creds = google.oauth2.credentials.Credentials(token=None, **yt_key)
    yt = build('youtube', 'v3', credentials=creds)
    body = {'snippet':{'title':title, 'description':desc, 'categoryId':'22'}, 'status':{'privacyStatus':'public'}}
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video_path))
    res = req.execute()
    vid_id = res['id']
    yt.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(thumb_path)).execute()
    print(f"YouTube Uploaded: https://youtu.be/{vid_id}")

    # 2. FACEBOOK REELS UPLOAD
    fb_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
    fb_page = os.environ.get("FACEBOOK_PAGE_ID")
    files = {'source': open(video_path, 'rb')}
    data = {'description': title, 'access_token': fb_token}
    r = requests.post(f"https://graph.facebook.com/v19.0/{fb_page}/videos", files=files, data=data)
    print(f"Facebook Uploaded: {r.json()}")

    # 3. INSTA REELS: FB ke through hi hota hai
    ig_user = os.environ.get("INSTAGRAM_USER_ID")
    # Iske liye pehle FB pe upload phir IG container banana parta hai. Code lamba hai.
    # Filhal FB kaam kar raha hai to Insta baad me add kar dena. Priority YT+FB.
