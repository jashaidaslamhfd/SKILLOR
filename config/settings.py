"""
Settings — Body + Brain Science (USA Audience 2026)
TARGET: USA | All Ages | YouTube Shorts + Facebook Reels + Instagram Reels

FIXES APPLIED:
1. ✅ Thumbnail resolution: 1280x720 (YouTube standard)
2. ✅ HASHTAGS_REQUIRED: Single #Shorts (no duplicates)
3. ✅ USA posting times: UTC converted from ET
4. ✅ Hook duration: 3.5s (fast hook = lower swipe rate)
5. ✅ Fast cuts: 1.4s (retention booster)
6. ✅ Audio: Voice starts at 0.0s (no delay)
7. ✅ USA geo-targeting enabled
8. ✅ SEO: Dynamic, not hardcoded
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time


# ============================================================
# VIDEO CONFIG — YouTube Shorts 2026 Optimized
# ============================================================
@dataclass
class VideoConfig:
    # YouTube Shorts duration: 42-55 seconds (2026 sweet spot)
    DURATION_MIN: int = 42
    DURATION_MAX: int = 55
    TARGET_DURATION: int = 48

    # Resolution
    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 23
    PRESET: str = "medium"

    # ═══════════════════════════════════════════════════════════
    # FIX: Hook duration REDUCED to 3.5s (fast hook = lower swipe)
    # 70% viewers decide in 1.5s — hook must hit HARD and FAST
    # ═══════════════════════════════════════════════════════════
    HOOK_DURATION: float = 3.5      # FAST hook (was 5.0)
    SHOCK_DURATION: float = 2.5
    SUSPENSE_DURATION: float = 4.0
    STORY_DURATION: float = 32.0
    CTR_DURATION: float = 4.0
    PAUSE_DURATION: float = 0.3     # Minimal pauses (retention killer)

    # ═══════════════════════════════════════════════════════════
    # FIX: Fast cuts = 1.4s (2026 Shorts standard)
    # Faster cuts = higher retention for under-30 audience
    # ═══════════════════════════════════════════════════════════
    FAST_CUT_INTERVAL: float = 1.4   # Was 2.5
    CUT_MIN_DURATION: float = 1.2    # Was 2.0
    CUT_MAX_DURATION: float = 3.0    # Was 6.0

    # Visual effects (subtle — not distracting)
    ZOOM_INTENSITY: float = 1.12
    SHAKE_INTENSITY: int = 0         # Disabled for clean look

    KEYFRAME_INTERVAL: int = 30
    SCENE_CHANGE_THRESHOLD: int = 0


# ============================================================
# AUDIO CONFIG — Voice starts at 0.0s (NO DELAY)
# ============================================================
@dataclass
class AudioConfig:
    # Voice: Groq Orpheus 'troy' (deep male USA voice)
    VOICE: str = "troy"
    MODEL: str = "canopylabs/orpheus-v1-english"

    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"

    # Background audio (VERY subtle)
    BG_MUSIC_VOLUME: float = 0.02    # Almost silent
    FAN_NOISE_VOLUME: float = 0.005
    SFX_VOLUME: float = 0.10

    # Word timing reference
    WORDS_PER_MINUTE: int = 130      # Slightly faster for retention

    TARGET_DURATION_MIN: float = 42.0
    TARGET_DURATION_MAX: float = 55.0


# ============================================================
# CAPTION CONFIG — Clean, Readable, USA English
# ============================================================
@dataclass
class CaptionConfig:
    # Large, bold font for mobile
    FONT_SIZE: int = 92              # Slightly bigger
    FONT_NAME: str = "Arial"
    BOLD: int = 1

    # ASS color codes (BGR format)
    PRIMARY_COLOR: str = "&H00FFFFFF"    # White
    SECONDARY_COLOR: str = "&H0000FFFF"  # Yellow (highlight)
    OUTLINE_COLOR: str = "&H00000000"    # Black
    OUTLINE_WIDTH: int = 8
    SHADOW: int = 4

    # Bottom-center alignment (safe zone for YouTube UI)
    ALIGNMENT: int = 2
    MARGIN_V: int = 350              # Safe from bottom bar
    MARGIN_L: int = 80

    HIGHLIGHT_COLOR: str = "&H0000FFFF"
    MAX_WORDS_PER_LINE: int = 3
    ALTERNATE_COLORS: bool = True
    ACTIVE_WORD_SCALE: float = 1.10
    SAFE_ZONE_TOP: int = 0
    SAFE_ZONE_BOTTOM: int = 350


# ============================================================
# SEO CONFIG — 2026 YouTube Algorithm (SPAM-FREE)
# ============================================================
@dataclass
class SEOConfig:
    # Title limits (YouTube Shorts)
    TITLE_MAX_LENGTH: int = 55
    TITLE_MIN_LENGTH: int = 20

    # Description: 100-150 words (not too long)
    DESCRIPTION_LENGTH: int = 130

    # Tags: 10-14 max (quality over quantity)
    TAGS_COUNT: int = 12

    # Category: 27 = Education (best for brain/body niche)
    CATEGORY_ID: str = "27"

    # YouTube Shorts settings
    MADE_FOR_KIDS: bool = False
    LICENSE: str = "youtube"
    PRIVACY_STATUS: str = "public"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_AUDIO_LANGUAGE: str = "en-US"  # USA English

    # ═══════════════════════════════════════════════════════════
    # FIX: ONLY #Shorts — rest are generated dynamically
    # Duplicate hashtags = SPAM SIGNAL for YouTube 2026
    # ═══════════════════════════════════════════════════════════
    HASHTAGS_REQUIRED: List[str] = field(default_factory=lambda: ["#Shorts"])

    # USA geo-targeting hints for YouTube algorithm
    GEO_TARGET: Dict = field(default_factory=lambda: {
        'country': 'US',
        'language': 'en',
        'region': 'America/New_York'
    })


# ============================================================
# THUMBNAIL CONFIG — 1280x720 (YouTube Standard)
# ============================================================
@dataclass
class ThumbnailConfig:
    # ═══════════════════════════════════════════════════════════
    # FIX: YouTube displays ALL thumbnails as 1280x720 LANDSCAPE
    # Even for Shorts! Portrait (1080x1920) gets CROPPED.
    # ═══════════════════════════════════════════════════════════
    RESOLUTION: tuple = (1280, 720)      # YouTube standard
    STYLE: str = "credible"

    WORD_COUNT: int = 3
    FONT_SIZE_MAIN: int = 130
    FONT_SIZE_SUB: int = 52

    # Colors: Dark background + Gold/White text (high CTR)
    BG_COLORS: List[str] = field(default_factory=lambda: [
        "#050A1A", "#0A0F1E", "#080D18", "#060B15", "#0D1220"
    ])
    TEXT_COLORS: List[str] = field(default_factory=lambda: [
        "#FFD700", "#FFFFFF", "#4FC3F7", "#E8E8E8", "#FFF9C4"
    ])
    ACCENT_COLORS: List[str] = field(default_factory=lambda: [
        "#4A90D9", "#FFD700", "#FFFFFF"
    ])

    DROP_SHADOW: bool = True
    OUTLINE_WIDTH: int = 7
    GLOW_EFFECT: bool = False

    BORDER_COLOR: str = "#4A90D9"
    BORDER_WIDTH: int = 12
    EMOJI_ENABLED: bool = True


# ============================================================
# PLATFORM CONFIG — USA Peak Times (ET → UTC converted)
# ============================================================
@dataclass
class PlatformConfig:
    TARGET_AUDIENCE: str = "USA"
    TIMEZONE: str = "America/New_York"

    DAILY_SHORTS_COUNT: int = 3
    UPLOAD_DELAY_SECONDS: int = 120

    # Instagram API
    INSTAGRAM_API_VERSION: str = "v19.0"
    INSTAGRAM_MAX_RETRIES: int = 3
    INSTAGRAM_RETRY_DELAY: int = 5
    INSTAGRAM_MAX_DELAY: int = 60
    INSTAGRAM_MAX_POLL: int = 30
    INSTAGRAM_POLL_INTERVAL: int = 3
    INSTAGRAM_BATCH_SIZE: int = 3

    # Facebook API
    FACEBOOK_API_VERSION: str = "v19.0"
    FACEBOOK_MAX_RETRIES: int = 3
    FACEBOOK_RETRY_DELAY: int = 5
    FACEBOOK_MAX_DELAY: int = 60
    FACEBOOK_MAX_POLL: int = 60
    FACEBOOK_POLL_INTERVAL: int = 5
    FACEBOOK_BATCH_SIZE: int = 3

    # ═══════════════════════════════════════════════════════════
    # FIX: USA Eastern Time posting times converted to UTC
    # 7AM ET = 12:00 UTC | 12PM ET = 16:00 UTC | 7PM ET = 23:00 UTC
    # ═══════════════════════════════════════════════════════════
    YOUTUBE_POST_TIMES: List[time] = field(default_factory=lambda: [
        time(12, 0),   # 7AM ET - Morning scroll
        time(16, 0),   # 12PM ET - Lunch break
        time(23, 0),   # 7PM ET - After dinner peak
    ])
    FACEBOOK_POST_TIMES: List[time] = field(default_factory=lambda: [
        time(12, 30),  # 7:30AM ET
        time(19, 0),   # 2PM ET
    ])
    INSTAGRAM_POST_TIMES: List[time] = field(default_factory=lambda: [
        time(12, 0),   # 7AM ET
        time(19, 0),   # 2PM ET
    ])


# ============================================================
# NICHE CONFIG — USA Audience Topics (All Ages)
# ============================================================
@dataclass
class NicheConfig:
    # USA-specific trending topics (high search volume)
    TOPICS: List[str] = field(default_factory=lambda: [
        # ── BRAIN & MEMORY ──
        "why you forget names right after hearing them",
        "why you walk into a room and forget why",
        "why a song gets stuck in your head",
        "why you feel deja vu",
        "why your brain replays embarrassing memories",
        "why you cannot remember a word on the tip of your tongue",
        "why you forget dreams within seconds",
        "why your brain blanks out under pressure",

        # ── BODY MYSTERIES ──
        "why your body jerks before you fall asleep",
        "why you get goosebumps from music",
        "why you yawn when someone else yawns",
        "why your stomach growls when you are not hungry",
        "why you get brain freeze",
        "why your eye twitches randomly",
        "why you sneeze when you look at bright light",
        "why your heart skips a beat",
        "why you get dizzy when you stand up fast",
        "why your ears ring in silence",
        "why you get hiccups",
        "why you get random chills",

        # ── USA-SPECIFIC ──
        "why Americans feel tired all the time",
        "why you crave sugar even when full",
        "why your phone makes your neck hurt",
        "why your eyes feel tired from screen time",
        "why you wake up at 3am and cannot sleep",
        "why you feel sluggish after sitting all day",
        "why coffee wakes you up but crashes later",
        "why you feel anxious for no reason",
    ])

    SUB_NICHES: List[str] = field(default_factory=lambda: [
        "brain science explained",
        "body mysteries",
        "why does my body do that",
        "USA health facts",
        "brain facts",
    ])

    KEYWORDS: List[str] = field(default_factory=lambda: [
        "brain science", "body facts", "why does my body",
        "brain mysteries", "health facts USA", "explained simply",
        "why your body", "how your brain works",
        "science shorts", "body explained",
    ])


# ============================================================
# API KEYS — Lazy Evaluation (FIXED)
# ============================================================
class APIKeys:
    """API keys with lazy evaluation — .env loaded before import"""

    def __init__(self):
        self._env_keys = {
            'GROQ_API_KEY': 'GROQ_API_KEY',
            'PEXELS_API_KEY': 'PEXELS_API_KEY',
            'PIXABAY_API_KEY': 'PIXABAY_API_KEY',
            'YOUTUBE_API_KEY': 'YOUTUBE_API_KEY',
            'YOUTUBE_CLIENT_SECRETS': 'YOUTUBE_CLIENT_SECRETS',
            'REFRESH_TOKEN': 'REFRESH_TOKEN',
            'GOOGLE_CLIENT_ID': 'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET': 'GOOGLE_CLIENT_SECRET',
            'FACEBOOK_ACCESS_TOKEN': 'FACEBOOK_ACCESS_TOKEN',
            'FACEBOOK_PAGE_ID': 'FACEBOOK_PAGE_ID',
            'INSTAGRAM_ACCESS_TOKEN': 'INSTAGRAM_ACCESS_TOKEN',
            'INSTAGRAM_USER_ID': 'INSTAGRAM_USER_ID',
            'CLOUDINARY_CLOUD_NAME': 'CLOUDINARY_CLOUD_NAME',
            'CLOUDINARY_API_KEY': 'CLOUDINARY_API_KEY',
            'CLOUDINARY_API_SECRET': 'CLOUDINARY_API_SECRET',
        }

    @property
    def GROQ_API_KEY(self) -> str:
        return os.getenv("GROQ_API_KEY", "")

    @property
    def PEXELS_API_KEY(self) -> str:
        return os.getenv("PEXELS_API_KEY", "")

    @property
    def PIXABAY_API_KEY(self) -> str:
        return os.getenv("PIXABAY_API_KEY", "")

    @property
    def YOUTUBE_API_KEY(self) -> str:
        return os.getenv("YOUTUBE_API_KEY", "")

    @property
    def YOUTUBE_CLIENT_SECRETS(self) -> str:
        return os.getenv("YOUTUBE_CLIENT_SECRETS", "")

    @property
    def REFRESH_TOKEN(self) -> str:
        return os.getenv("REFRESH_TOKEN", "")

    @property
    def GOOGLE_CLIENT_ID(self) -> str:
        return os.getenv("GOOGLE_CLIENT_ID", "")

    @property
    def GOOGLE_CLIENT_SECRET(self) -> str:
        return os.getenv("GOOGLE_CLIENT_SECRET", "")

    @property
    def FACEBOOK_ACCESS_TOKEN(self) -> str:
        return os.getenv("FACEBOOK_ACCESS_TOKEN", "")

    @property
    def FACEBOOK_PAGE_ID(self) -> str:
        return os.getenv("FACEBOOK_PAGE_ID", "")

    @property
    def INSTAGRAM_ACCESS_TOKEN(self) -> str:
        return os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

    @property
    def INSTAGRAM_USER_ID(self) -> str:
        return os.getenv("INSTAGRAM_USER_ID", "")

    @property
    def CLOUDINARY_CLOUD_NAME(self) -> str:
        return os.getenv("CLOUDINARY_CLOUD_NAME", "")

    @property
    def CLOUDINARY_API_KEY(self) -> str:
        return os.getenv("CLOUDINARY_API_KEY", "")

    @property
    def CLOUDINARY_API_SECRET(self) -> str:
        return os.getenv("CLOUDINARY_API_SECRET", "")

    def validate(self) -> Dict[str, bool]:
        """Check which APIs are configured"""
        return {
            'groq': bool(self.GROQ_API_KEY),
            'pexels': bool(self.PEXELS_API_KEY),
            'pixabay': bool(self.PIXABAY_API_KEY),
            'youtube': bool(self.YOUTUBE_API_KEY and self.REFRESH_TOKEN and self.GOOGLE_CLIENT_ID),
            'facebook': bool(self.FACEBOOK_ACCESS_TOKEN and self.FACEBOOK_PAGE_ID),
            'instagram': bool(self.INSTAGRAM_ACCESS_TOKEN and self.INSTAGRAM_USER_ID),
            'cloudinary': bool(self.CLOUDINARY_CLOUD_NAME and self.CLOUDINARY_API_KEY),
        }

    def missing_keys(self) -> List[str]:
        """Return list of missing API keys"""
        return [k for k, v in self.validate().items() if not v]


# ============================================================
# HEALTH CHECK — FIXED
# ============================================================
def health_check() -> Dict:
    """Check all configurations"""
    result = {
        'status': 'ok',
        'warnings': [],
        'errors': []
    }

    # Check Video Config
    if VideoConfig.DURATION_MIN > VideoConfig.DURATION_MAX:
        result['errors'].append("VideoConfig: DURATION_MIN > DURATION_MAX")

    # Check Thumbnail Resolution
    if ThumbnailConfig.RESOLUTION != (1280, 720):
        result['warnings'].append(
            f"ThumbnailConfig: RESOLUTION={ThumbnailConfig.RESOLUTION} "
            "(recommended 1280x720 for YouTube)"
        )

    # Check Caption Config
    if CaptionConfig.MARGIN_V < 300:
        result['warnings'].append(
            f"CaptionConfig: MARGIN_V={CaptionConfig.MARGIN_V} (recommended 350+)"
        )

    # Check API Keys
    try:
        missing = API_KEYS.missing_keys()
        if missing:
            result['warnings'].append(f"APIKeys: Missing: {', '.join(missing)}")
            result['status'] = 'degraded'
    except Exception:
        result['errors'].append("APIKeys: Not initialized")

    return result


# ============================================================
# INSTANCES
# ============================================================
VIDEO_CONFIG = VideoConfig()
AUDIO_CONFIG = AudioConfig()
CAPTION_CONFIG = CaptionConfig()
SEO_CONFIG = SEOConfig()
THUMBNAIL_CONFIG = ThumbnailConfig()
PLATFORM_CONFIG = PlatformConfig()
NICHE_CONFIG = NicheConfig()
API_KEYS = APIKeys()


# ============================================================
# STATUS DISPLAY
# ============================================================
def display_status():
    """Display configuration status"""
    print("=" * 60)
    print("📊 CONFIGURATION STATUS (USA 2026)")
    print("=" * 60)

    print("\n🎯 NICHE:")
    print(f"    Topics: {len(NICHE_CONFIG.TOPICS)}")
    print(f"    Keywords: {len(NICHE_CONFIG.KEYWORDS)}")
    print(f"    Sub-niches: {len(NICHE_CONFIG.SUB_NICHES)}")

    print("\n🎬 VIDEO:")
    print(f"    Duration: {VIDEO_CONFIG.DURATION_MIN}-{VIDEO_CONFIG.DURATION_MAX}s")
    print(f"    Fast Cut: {VIDEO_CONFIG.FAST_CUT_INTERVAL}s")
    print(f"    Hook Duration: {VIDEO_CONFIG.HOOK_DURATION}s")
    print(f"    Resolution: {VIDEO_CONFIG.RESOLUTION}")

    print("\n🎙️ AUDIO:")
    print(f"    Voice: {AUDIO_CONFIG.VOICE}")
    print(f"    WPM: {AUDIO_CONFIG.WORDS_PER_MINUTE}")

    print("\n📝 CAPTIONS:")
    print(f"    Font Size: {CAPTION_CONFIG.FONT_SIZE}px")
    print(f"    Margin V: {CAPTION_CONFIG.MARGIN_V}")

    print("\n🖼️ THUMBNAIL:")
    print(f"    Resolution: {THUMBNAIL_CONFIG.RESOLUTION} (YouTube standard)")

    print("\n🔑 API KEYS:")
    api_status = API_KEYS.validate()
    for key, value in api_status.items():
        status = "✅" if value else "❌"
        print(f"    {status} {key}")

    print("\n🔍 HEALTH CHECK:")
    health = health_check()
    print(f"    Status: {health['status']}")
    if health['warnings']:
        for w in health['warnings']:
            print(f"    ⚠️ {w}")
    if health['errors']:
        for e in health['errors']:
            print(f"    ❌ {e}")

    print("\n" + "=" * 60)


# ============================================================
# RUN STATUS
# ============================================================
if __name__ == "__main__":
    display_status()
