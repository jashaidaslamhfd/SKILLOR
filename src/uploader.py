import json
import os
import logging
import time
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5

# ---------------------------------------------------------------------------
# IMPORTANT: YouTube video uploads require OAuth 2.0 USER credentials, not a
# service-account key. A service account cannot upload to a personal/brand
# YouTube channel without domain-wide delegation (which YouTube doesn't
# support for this use case), and google.oauth2.credentials.Credentials()
# does not accept service-account fields at all - this was the reason
# YouTube upload was always failing.
#
# YT_CLIENT_SECRET must now be a JSON blob shaped like:
# {
#   "token": "<any placeholder, refreshed automatically>",
#   "refresh_token": "...",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "client_id": "...",
#   "client_secret": "...",
#   "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
# }
# Get refresh_token once via the OAuth consent flow (Google Cloud Console ->
# OAuth 2.0 Client ID -> local run of the standard installed-app flow).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# YOUTUBE "MADE FOR KIDS" (COPPA) - READ BEFORE CHANGING
# This channel's content is ABOUT babies/children but is SPOKEN TO parents,
# which is why MADE_FOR_KIDS defaults to False below. This is a legal
# self-declaration under COPPA, not just a checkbox - YouTube considers
# audience, characters, subject matter, and more when auto-detecting the
# actual status regardless of what you declare. Do not flip this default
# without manually re-reading YouTube's "Made for Kids" guidance and
# confirming the content genuinely targets adults.
# ---------------------------------------------------------------------------
MADE_FOR_KIDS = os.environ.get("YT_MADE_FOR_KIDS", "false").lower() == "true"


def upload_all(video_path, thumb_path, script_data):
    """Upload video to YouTube and Facebook with comprehensive error handling."""

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if not script_data or 'title' not in script_data:
        raise ValueError("Invalid script data - missing title")

    title = script_data.get('title', 'Untitled')
    voiceover = script_data.get('voiceover', '')
    cta = script_data.get('cta', '')
    desc = f"{voiceover[:180]}...\n\n{cta}\n\n#shorts #parentingtips #babybrain"

    logger.info(f"Starting upload process for: {title}")
    logger.info(f"selfDeclaredMadeForKids = {MADE_FOR_KIDS} (verify this is correct for your content!)")

    # ============================================================================
    # 1. YOUTUBE UPLOAD
    # ============================================================================
    youtube_success = False
    yt_video_id = None

    try:
        yt_key_raw = os.environ.get("YT_CLIENT_SECRET")
        if not yt_key_raw:
            logger.error("YT_CLIENT_SECRET missing - YouTube upload skipped")
        else:
            try:
                yt_key = json.loads(yt_key_raw)
            except json.JSONDecodeError:
                logger.error("Invalid YT_CLIENT_SECRET JSON format")
                raise ValueError("YT_CLIENT_SECRET is not valid JSON")

            required_fields = {"refresh_token", "token_uri", "client_id", "client_secret"}
            missing = required_fields - yt_key.keys()
            if missing:
                raise ValueError(
                    f"YT_CLIENT_SECRET missing OAuth fields: {missing}. "
                    "This must be OAuth user credentials, not a service-account key."
                )

            creds = google.oauth2.credentials.Credentials(
                token=yt_key.get("token"),
                refresh_token=yt_key["refresh_token"],
                token_uri=yt_key["token_uri"],
                client_id=yt_key["client_id"],
                client_secret=yt_key["client_secret"],
                scopes=yt_key.get("scopes", ["https://www.googleapis.com/auth/youtube.upload"]),
            )

            yt = build('youtube', 'v3', credentials=creds)

            body = {
                'snippet': {
                    'title': title[:100],
                    'description': desc[:5000],
                    'categoryId': '22',
                    'tags': ['parenting', 'babydevelopment', 'shorts', 'brainscience'],
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': MADE_FOR_KIDS,
                }
            }

            logger.info("Uploading to YouTube...")

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    req = yt.videos().insert(
                        part="snippet,status",
                        body=body,
                        media_body=MediaFileUpload(video_path, chunksize=1024 * 1024, resumable=True)
                    )
                    res = req.execute()
                    yt_video_id = res.get('id')
                    logger.info(f"YouTube upload successful: https://youtu.be/{yt_video_id}")
                    youtube_success = True

                    if thumb_path and os.path.exists(thumb_path):
                        try:
                            yt.thumbnails().set(
                                videoId=yt_video_id,
                                media_body=MediaFileUpload(thumb_path)
                            ).execute()
                            logger.info("Thumbnail uploaded successfully")
                        except Exception as thumb_error:
                            logger.warning(f"Thumbnail upload failed: {thumb_error}")

                    break

                except HttpError as e:
                    if e.resp.status in [429, 500, 502, 503]:
                        logger.warning(f"YouTube API error {e.resp.status} (attempt {attempt}/{MAX_RETRIES})")
                        if attempt < MAX_RETRIES:
                            time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))
                        continue
                    else:
                        logger.error(f"YouTube upload failed: {e}")
                        raise

            if not youtube_success:
                logger.error("YouTube upload failed after retries")

    except Exception as e:
        logger.error(f"YouTube upload process failed: {e}")

    # ============================================================================
    # 2. FACEBOOK REELS UPLOAD
    # ============================================================================
    facebook_success = False

    try:
        fb_token = os.environ.get("FB_ACCESS_TOKEN")
        fb_page = os.environ.get("FB_PAGE_ID")

        if not fb_token or not fb_page:
            logger.warning("FB_ACCESS_TOKEN or FB_PAGE_ID missing - Facebook upload skipped")
        else:
            fb_url = f"https://graph.facebook.com/v19.0/{fb_page}/videos"

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    with open(video_path, 'rb') as video_file:
                        files = {'source': video_file}
                        data = {
                            'description': title[:63],
                            'access_token': fb_token,
                        }
                        logger.info(f"Posting to Facebook (attempt {attempt}/{MAX_RETRIES})...")
                        r = requests.post(fb_url, files=files, data=data, timeout=300)

                    fb_result = r.json()

                    if r.status_code == 200 and "error" not in fb_result:
                        logger.info(f"Facebook Upload Successful: {fb_result}")
                        facebook_success = True
                        break
                    else:
                        error_msg = fb_result.get('error', {}).get('message', str(fb_result))
                        logger.warning(f"Facebook error (attempt {attempt}/{MAX_RETRIES}): {error_msg}")
                        if "temporarily_blocked" in error_msg or "rate" in error_msg.lower():
                            if attempt < MAX_RETRIES:
                                time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))
                                continue
                        else:
                            logger.error(f"Facebook Upload FAILED: {error_msg}")
                            break

                except requests.Timeout:
                    logger.warning(f"Facebook upload timeout (attempt {attempt}/{MAX_RETRIES})")
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))
                    continue
                except Exception as e:
                    logger.error(f"Facebook upload exception (attempt {attempt}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))
                    continue

    except Exception as e:
        logger.error(f"Facebook upload process failed: {e}")

    logger.info(f"YouTube Upload: {'SUCCESS' if youtube_success else 'FAILED/SKIPPED'}")
    if yt_video_id:
        logger.info(f"  URL: https://youtu.be/{yt_video_id}")
    logger.info(f"Facebook Upload: {'SUCCESS' if facebook_success else 'FAILED/SKIPPED'}")

    if not (youtube_success or facebook_success):
        raise RuntimeError("Both YouTube and Facebook uploads failed")

    return {
        "youtube_success": youtube_success,
        "youtube_video_id": yt_video_id,
        "facebook_success": facebook_success
    }
