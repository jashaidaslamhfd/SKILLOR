import json, os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

def upload_all(video_path, thumb_path, script_data):
    title = script_data['title']
    desc = f"{script_data['voiceover'][:200]}...\n\n#babypsychology #parenting #shorts"

    # 1. YOUTUBE UPLOAD
    yt_key_raw = os.environ.get("YT_CLIENT_SECRET")
    if not yt_key_raw:
        raise ValueError("YT_CLIENT_SECRET missing hai. GitHub Secrets check karo.")

    yt_key = json.loads(yt_key_raw)
    creds = google.oauth2.credentials.Credentials(**yt_key)
    yt = build('youtube', 'v3', credentials=creds)
    body = {
        'snippet': {'title': title, 'description': desc, 'categoryId': '22'},
        'status': {'privacyStatus': 'public'}
    }
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video_path))
    res = req.execute()
    vid_id = res['id']

    if thumb_path and os.path.exists(thumb_path):
        yt.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(thumb_path)).execute()

    print(f"YouTube Uploaded: https://youtu.be/{vid_id}")

    # 2. FACEBOOK REELS UPLOAD
    fb_token = os.environ.get("FB_ACCESS_TOKEN")
    fb_page = os.environ.get("FB_PAGE_ID")

    if not fb_token or not fb_page:
        print("FB_ACCESS_TOKEN / FB_PAGE_ID missing hai, Facebook upload skip kar diya.")
        return

    with open(video_path, 'rb') as video_file:
        files = {'source': video_file}
        data = {'description': title, 'access_token': fb_token}
        r = requests.post(f"https://graph.facebook.com/v19.0/{fb_page}/videos", files=files, data=data)

    fb_result = r.json()
    # Pehle ye response check kiye bina hi "Uploaded" print kar deta tha,
    # is se FB upload fail hone par bhi pipeline "success" dikhata tha.
    if r.status_code != 200 or "error" in fb_result:
        print(f"Facebook Upload FAILED: {fb_result}")
    else:
        print(f"Facebook Uploaded: {fb_result}")

    # 3. INSTA REELS: FB ke through hi hota hai
    # Iske liye pehle FB pe upload phir IG container banana parta hai.
    # Filhal YT+FB priority hai, IG baad me add karna.
