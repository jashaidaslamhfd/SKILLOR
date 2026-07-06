import os
import json
import logging
import time
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import requests
from niche_strategy import _make_seo_title

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 5

# ---------------------------------------------------------------------------
# IMPORTANT: YouTube video uploads require OAuth 2.0 USER credentials, not a
# service-account key. Credentials are read from THREE separate secrets/env
# vars: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REFRESH_TOKEN.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# YOUTUBE "MADE FOR KIDS" (COPPA)
# This channel's content is dark/mystery body-science facts aimed at adults
# (18+), so MADE_FOR_KIDS defaults to False. If your niche or audience
# changes again, re-verify this setting - COPPA fines are no joke.
# ---------------------------------------------------------------------------
MADE_FOR_KIDS = os.environ.get("YT_MADE_FOR_KIDS", "false").lower() == "true"


def _build_youtube_description(script_data: dict, tags: list) -> str:
    """CTR-optimized YouTube description:
    - First 2 lines visible before 'Show more' — hook viewer immediately
    - Keywords appear early (good for YouTube search ranking)
    - Clean hashtag section at end (max 3 work best for YT Shorts reach)"""
    title = script_data.get('title', '')
    hook = script_data.get('hook', '')
    cta = script_data.get('cta', 'Follow for more dark body secrets.')
    description = script_data.get('description', '')

    # YouTube shows only first ~125 chars before "Show more" in Shorts
    # Put the most engaging line first so it doubles as the preview text
    first_line = hook[:120] if hook else title

    # Top 3 tags as hashtags (YouTube Shorts surfaces videos via hashtags)
    yt_hashtags = ' '.join(f"#{t}" for t in tags[:3])

    return (
        f"{first_line}\n\n"
        f"{description}\n\n"
        f"👇 {cta}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔬 Dark body science | USA adults\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{yt_hashtags}"
    )[:5000]


def _build_facebook_description(script_data: dict, tags: list) -> str:
    """Facebook Reels description:
    - Facebook's own guidelines warn that MORE THAN 5 hashtags can
      suppress reach — so we use MAX 3 (sweet spot for Reels).
    - Hook in first line (shows before 'See more' truncation).
    - Clean CTA drives the follow/share action."""
    hook = script_data.get('hook', '')
    cta = script_data.get('cta', 'Follow for more dark body secrets.')
    description = script_data.get('description', '')

    # Strict 3-hashtag limit for Facebook — avoids the >5 hashtag warning
    fb_hashtags = ' '.join(f"#{t}" for t in tags[:3])

    return (
        f"{hook}\n\n"
        f"{description}\n\n"
        f"{cta}\n\n"
        f"{fb_hashtags}"
    )[:2200]


def _already_uploaded_to_facebook(script_data: dict) -> bool:
    """Checks output/video_history.json to see if this exact video title
    was already successfully posted to Facebook — prevents the same video
    being uploaded 3x on retries/re-runs of the same pipeline execution."""
    history_file = "output/video_history.json"
    if not os.path.exists(history_file):
        return False
    try:
        with open(history_file) as f:
            history = json.load(f)
        title = script_data.get('title', '')
        return any(
            v.get('title') == title and v.get('facebook_success')
            for v in history
        )
    except Exception:
        return False


def _upload_youtube(video_path, thumb_path, script_data, tags):
    """Returns (success: bool, video_id: str|None)."""
    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("REFRESH_TOKEN")

    missing = [
        name for name, val in {
            "GOOGLE_CLIENT_ID": google_client_id,
            "GOOGLE_CLIENT_SECRET": google_client_secret,
            "REFRESH_TOKEN": refresh_token,
        }.items() if not val
    ]
    if missing:
        logger.error(f"YouTube upload skipped - missing secrets: {missing}")
        return False, None

    title = script_data.get('title', 'Untitled')
    enhanced_title = _make_seo_title(title, script_data.get('topic', title))
    desc = _build_youtube_description(script_data, tags)

    creds = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=google_client_id,
        client_secret=google_client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    yt = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': enhanced_title[:100],
            'description': desc[:5000],
            'categoryId': '22',
            # FIX: was a fixed hardcoded list on every single video - now
            # topic/category-aware tags from niche_strategy.generate_seo_tags,
            # which also helps SEO reach and avoids duplicate-metadata spam risk.
            'tags': tags,
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en',
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': MADE_FOR_KIDS,
        }
    }

    logger.info("Uploading to YouTube...")
    yt_video_id = None
    youtube_success = False

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
                break
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            break

    return youtube_success, yt_video_id


def _upload_facebook_reels(video_path, script_data, tags):
    """
    FIX: previously this posted to /{page-id}/videos as a plain video post.
    Facebook's 2026 recommendation algorithm gives materially better organic
    reach to content published through the actual Reels pipeline. This now
    uses the correct 3-phase Reels publishing flow:
      1. upload_phase=start   -> get video_id + upload_url
      2. POST binary to upload_url (rupload host)
      3. upload_phase=finish  -> attach description/hashtags and publish
    Returns success: bool.
    """
    fb_token = os.environ.get("FB_ACCESS_TOKEN")
    fb_page = os.environ.get("FB_PAGE_ID")

    if not fb_token or not fb_page:
        logger.warning("FB_ACCESS_TOKEN or FB_PAGE_ID missing - Facebook upload skipped")
        return False

    # Duplicate prevention: if this exact video title was already successfully
    # posted to Facebook in a previous run, skip it rather than uploading again.
    if _already_uploaded_to_facebook(script_data):
        logger.info(f"Facebook: '{script_data.get('title')}' already uploaded — skipping duplicate.")
        return True  # treat as success so pipeline doesn't retry/fail

    title = script_data.get('title', 'Untitled')
    # Max 3 hashtags — Facebook's own algorithm penalises Reels with >5 hashtags
    description = _build_facebook_description(script_data, tags)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # ---- Phase 1: start ----
            start_resp = requests.post(
                f"https://graph.facebook.com/v19.0/{fb_page}/video_reels",
                data={"upload_phase": "start", "access_token": fb_token},
                timeout=30,
            )
            start_data = start_resp.json()
            if "error" in start_data or "video_id" not in start_data:
                raise RuntimeError(f"Reels start phase failed: {start_data}")

            video_id = start_data["video_id"]
            upload_url = start_data["upload_url"]

            # ---- Phase 2: upload binary ----
            file_size = os.path.getsize(video_path)
            with open(video_path, "rb") as f:
                upload_resp = requests.post(
                    upload_url,
                    headers={
                        "Authorization": f"OAuth {fb_token}",
                        "offset": "0",
                        "file_size": str(file_size),
                    },
                    data=f,
                    timeout=300,
                )
            upload_data = upload_resp.json() if upload_resp.content else {}
            if upload_resp.status_code != 200 or upload_data.get("success") is False:
                raise RuntimeError(f"Reels upload phase failed: {upload_resp.status_code} {upload_data}")

            # ---- Phase 3: finish/publish ----
            finish_resp = requests.post(
                f"https://graph.facebook.com/v19.0/{fb_page}/video_reels",
                data={
                    "upload_phase": "finish",
                    "video_id": video_id,
                    "description": description,
                    "video_state": "PUBLISHED",
                    "access_token": fb_token,
                },
                timeout=60,
            )
            finish_data = finish_resp.json()
            if finish_resp.status_code == 200 and finish_data.get("success", True) and "error" not in finish_data:
                logger.info(f"Facebook Reels published successfully: video_id={video_id}")
                return True
            else:
                raise RuntimeError(f"Reels finish phase failed: {finish_data}")

        except Exception as e:
            logger.warning(f"Facebook Reels upload attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))
            continue

    logger.error("Facebook Reels upload failed after all retries")
    return False


def upload_all(video_path, thumb_path, script_data):
    """Upload video to YouTube and Facebook Reels with comprehensive error handling."""

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if not script_data or 'title' not in script_data:
        raise ValueError("Invalid script data - missing title")

    title = script_data.get('title', 'Untitled')
    # Tags come from script_data (set by main.py via niche_strategy.generate_seo_tags).
    # Fallback below only fires if that ever comes back empty - matches the
    # current dark-facts niche, not the old parenting-channel tags.
    tags = script_data.get('tags') or ['facts', 'shorts', 'science', 'darkfacts', 'bodyfacts']

    logger.info(f"Starting upload process for: {title}")
    logger.info(f"selfDeclaredMadeForKids = {MADE_FOR_KIDS} (verify this is correct for your content!)")
    logger.info(f"SEO tags for this video: {tags}")

    youtube_success, yt_video_id = _upload_youtube(video_path, thumb_path, script_data, tags)
    facebook_success = _upload_facebook_reels(video_path, script_data, tags)

    logger.info(f"YouTube Upload: {'SUCCESS' if youtube_success else 'FAILED/SKIPPED'}")
    if yt_video_id:
        logger.info(f"  URL: https://youtu.be/{yt_video_id}")
    logger.info(f"Facebook Upload: {'SUCCESS' if facebook_success else 'FAILED/SKIPPED'}")

    if not (youtube_success or facebook_success):
        raise RuntimeError("Both YouTube and Facebook uploads failed")

    return {
        "youtube_success": youtube_success,
        "youtube_video_id": yt_video_id,
        "facebook_success": facebook_success,
    }
