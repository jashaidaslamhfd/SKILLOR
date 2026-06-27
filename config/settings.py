"""
Settings — Body + Brain Science (Mystery Crispy Style)
AUDIENCE: ALL AGES (13-65+) | Global English
NICHE: Body + Brain Science Mysteries (Universal)
GOAL: Viral, High Retention, All Age Appeal

FIXES:
1. ✅ Voice Engine Upgraded: Changed from Edge-TTS to Groq 'troy' persona.
2. ✅ Health Check Fixed: Removed rigid checks for rate min/max to support Groq native scale.
3. ✅ Correct ASS color codes (BGR format)
4. ✅ Increased caption margin for safe zone
5. ✅ Proper dataclass usage
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time


# ============================================================
# VIDEO CONFIG — YouTube Shorts Optimized
# ============================================================
@dataclass
class VideoConfig:
    DURATION_MIN: int = 42  # FIX C8: Changed from 35 to align with AudioConfig.TARGET_DURATION_MIN
    DURATION_MAX: int = 55
    TARGET_DURATION: int = 48

    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 23
    PRESET: str = "medium"

    # Segment durations — optimized for all-age retention
    HOOK_DURATION: float = 5.0  # FIX: increased from 3.5 — retention data shows viewers need 5s to commit
    SHOCK_DURATION: float = 3.0
    SUSPENSE_DURATION: float = 5.0
    STORY_DURATION: float = 32.0
    CTR_DURATION: float = 4.0
    PAUSE_DURATION: float = 0.5

    # Cut intervals — steady pacing for retention
    FAST_CUT_INTERVAL: float = 2.5  # FIX: reduced from 3.5 — faster cuts keep attention in Shorts
    CUT_MIN_DURATION: float = 2.0  # FIX: reduced from 3.0 — faster pacing for retention
    CUT_MAX_DURATION: float = 6.0

    # Effects — subtle for this audience
    ZOOM_INTENSITY: float = 1.15  # FIX: increased from 1.12 — more dynamic visual movement
    SHAKE_INTENSITY: int = 1

    KEYFRAME_INTERVAL: int = 30
    SCENE_CHANGE_THRESHOLD: int = 0


# ============================================================
# AUDIO CONFIG — Voice (GROQ Orpheus Troy)
# ============================================================
@dataclass
class AudioConfig:
    # ✅ FIXED: Upgraded to Groq's Premium Deep Human Male Persona
    VOICE: str = "troy"
    MODEL: str = "canopylabs/orpheus-v1-english"

    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"

    # Background audio — VERY subtle
    BG_MUSIC_VOLUME: float = 0.03
    FAN_NOISE_VOLUME: float = 0.010
    SFX_VOLUME: float = 0.15

    # WPM reference for word count tracking
    WORDS_PER_MINUTE: int = 120

    TARGET_DURATION_MIN: float = 42.0
    TARGET_DURATION_MAX: float = 55.0


# ============================================================
# CAPTION CONFIG — Readable for all ages on Mobile
# ============================================================
@dataclass
class CaptionConfig:
    # Slightly larger font — this age group appreciates readability
    FONT_SIZE: int = 88
    FONT_NAME: str = "Arial"
    BOLD: int = 1

    # ============================================================
    # FIX: Correct ASS Color Codes (BGR Format)
    # ASS uses Blue-Green-Red (BGR) format: &HAABBGGRR
    # ============================================================
    PRIMARY_COLOR: str = "&H00FFFFFF"    # White (FIXED)
    SECONDARY_COLOR: str = "&H0000FFFF"  # Yellow (FIXED: BGR = 00 FF FF 00)
    OUTLINE_COLOR: str = "&H00000000"    # Black outline
    OUTLINE_WIDTH: int = 8               # Slightly thicker for readability
    SHADOW: int = 4                      # More shadow for depth

    # FIX: Alignment and margins for safe zone
    ALIGNMENT: int = 2                   # Bottom-center (2)
    MARGIN_V: int = 340                  # FIX: Increased safe zone for YouTube UI
    MARGIN_L: int = 80                   # FIX: Wider margin to prevent cutoff

    HIGHLIGHT_COLOR: str = "&H0000FFFF"  # Yellow highlight

    MAX_WORDS_PER_LINE: int = 3
    ALTERNATE_COLORS: bool = True
    ACTIVE_WORD_SCALE: float = 1.10
    SAFE_ZONE_TOP: int = 0
    SAFE_ZONE_BOTTOM: int = 350


# ============================================================
# SEO CONFIG — Memory & Brain Fog Keywords
# ============================================================
@dataclass
class SEOConfig:
    TITLE_MAX_LENGTH: int = 55
    TITLE_MIN_LENGTH: int = 20

    DESCRIPTION_LENGTH: int = 130
    TAGS_COUNT: int = 12

    # Category 27 = Education — Credibility for all ages
    CATEGORY_ID: str = "27"

    MADE_FOR_KIDS: bool = False
    LICENSE: str = "youtube"
    PRIVACY_STATUS: str = "public"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_AUDIO_LANGUAGE: str = "en"

    HASHTAGS_REQUIRED: List[str] = field(default_factory=list)

    def __post_init__(self):
        # FIX 2026: Removed hardcoded niche hashtags — these were identical across
        # every video, which YouTube's spam detector flags as repetitive content.
        # Hashtags are now generated dynamically per-video in the orchestrator.
        # Only keep #Shorts which is required for YouTube Shorts algorithm.
        self.HASHTAGS_REQUIRED = [
            "#Shorts", "#shorts"
        ]


# ============================================================
# THUMBNAIL CONFIG — Credible, Not Horror
# ============================================================
@dataclass
class ThumbnailConfig:
    RESOLUTION: tuple = (1080, 1920)
    STYLE: str = "credible"

    WORD_COUNT: int = 3
    FONT_SIZE_MAIN: int = 130
    FONT_SIZE_SUB: int = 52

    # Color scheme — Dark background + Gold/White text
    BG_COLORS: List[str] = field(default_factory=list)
    TEXT_COLORS: List[str] = field(default_factory=list)
    ACCENT_COLORS: List[str] = field(default_factory=list)

    DROP_SHADOW: bool = True
    OUTLINE_WIDTH: int = 7
    GLOW_EFFECT: bool = False

    BORDER_COLOR: str = "#4A90D9"
    BORDER_WIDTH: int = 12
    EMOJI_ENABLED: bool = True

    def __post_init__(self):
        # Dark but not horror — science/documentary feel
        self.BG_COLORS = [
            "#050A1A", "#0A0F1E", "#080D18", "#060B15", "#0D1220"
        ]
        # Gold/White/Light Blue = credible, not scary
        self.TEXT_COLORS = [
            "#FFD700", "#FFFFFF", "#4FC3F7", "#E8E8E8", "#FFF9C4"
        ]
        self.ACCENT_COLORS = ["#4A90D9", "#FFD700", "#FFFFFF"]


# ============================================================
# PLATFORM CONFIG — Posting Times (Peak engagement hours)
# ============================================================
@dataclass
class PlatformConfig:
    TARGET_AUDIENCE: str = "US,UK,CA,AU"
    TIMEZONE: str = "America/New_York"

    DAILY_SHORTS_COUNT: int = 3
    UPLOAD_DELAY_SECONDS: int = 120

    # Instagram API Version
    INSTAGRAM_API_VERSION: str = "v19.0"
    INSTAGRAM_MAX_RETRIES: int = 3
    INSTAGRAM_RETRY_DELAY: int = 5
    INSTAGRAM_MAX_DELAY: int = 60
    INSTAGRAM_MAX_POLL: int = 30
    INSTAGRAM_POLL_INTERVAL: int = 3
    INSTAGRAM_BATCH_SIZE: int = 3

    # Facebook API Version
    FACEBOOK_API_VERSION: str = "v19.0"
    FACEBOOK_MAX_RETRIES: int = 3
    FACEBOOK_RETRY_DELAY: int = 5
    FACEBOOK_MAX_DELAY: int = 60
    FACEBOOK_MAX_POLL: int = 60
    FACEBOOK_POLL_INTERVAL: int = 5
    FACEBOOK_BATCH_SIZE: int = 3

    # Posting times
    YOUTUBE_POST_TIMES: List[time] = field(default_factory=list)
    FACEBOOK_POST_TIMES: List[time] = field(default_factory=list)
    INSTAGRAM_POST_TIMES: List[time] = field(default_factory=list)

    def __post_init__(self):
        # FIX: Optimized for USA peak engagement (Eastern Time)
        # 7AM ET = morning scroll, 12PM ET = lunch break, 7PM ET = after dinner
        # These are the 3 highest-traffic windows for US Shorts consumption
        self.YOUTUBE_POST_TIMES = [time(7, 0), time(12, 0), time(19, 0)]
        self.FACEBOOK_POST_TIMES = [time(12, 30), time(19, 0)]
        self.INSTAGRAM_POST_TIMES = [time(7, 0), time(19, 0)]


# ============================================================
# NICHE CONFIG — Body + Brain Science (All Ages, Universal)
# ============================================================
@dataclass
class NicheConfig:
    # Universal body + brain science topics
    TOPICS: List[str] = field(default_factory=list)
    SUB_NICHES: List[str] = field(default_factory=list)
    KEYWORDS: List[str] = field(default_factory=list)

    def __post_init__(self):
        # ============================================================
        # MEMORY TOPICS
        # ============================================================
        self.TOPICS = [
            # Universal Body Mysteries
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
            "why you feel the urge to stretch",
            "why you get hiccups",
            "why you feel like you are falling when asleep",
            "why you get random chills",
            "why you sweat when nervous",
            # Universal Brain Mysteries
            "why you forget names right after hearing them",
            "why you walk into a room and forget why",
            "why a song gets stuck in your head",
            "why you cannot tickle yourself",
            "why you feel deja vu",
            "why your brain creates faces in random patterns",
            "why you feel watched when alone",
            "why you feel time moves faster as you age",
            "why music gives you chills",
            "why your brain replays embarrassing memories",
            "why you cannot remember a word on the tip of your tongue",
            "why you feel empty when everything is fine",
            "why you feel anxious for no reason",
            "why your brain is more creative at night",
            "why you feel a rush of emotion from a smell",
        ]

        # ============================================================
        # SUB-NICHES
        # ============================================================
        self.SUB_NICHES = [
            "body science mysteries",
            "brain science explained",
            "why does my body do that",
            "universal body facts",
            "how your brain works",
            "body mysteries explained",
            "nervous system facts",
            "gut brain connection",
        ]

        # ============================================================
        # KEYWORDS — Universal Search Terms (All Ages)
        # ============================================================
        self.KEYWORDS = [
            # Primary (universal)
            "body science", "brain facts", "why does my body",
            "body mysteries", "brain science", "explained simply",
            
            # Long-tail (universal search behavior)
            "why do i feel", "what happens when", "why does my brain",
            "body facts", "why your body", "how your brain works",
            
            # Related
            "science shorts", "health facts", "body explained",
            "brain explained", "did you know body", "nervous system",
        ]


# ============================================================
# API KEYS — Load from Environment
# ============================================================
class APIKeys:
    """FIX C2: API keys now use properties to evaluate os.getenv() at ACCESS time,
    not at class definition time. This ensures .env loading (load_dotenv) before
    import actually takes effect. Also FIX H14: YOUTUBE_API_KEY checked in validate()."""

    def __init__(self):
        # Store env var names — values fetched on each access via properties
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

    # --- Properties: evaluate os.getenv() at access time ---
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
        """Check which APIs are configured — FIX H14: now checks YOUTUBE_API_KEY"""
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
# HEALTH CHECK — Cleaned for Groq Native Output
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
    
    # Check Caption Config
    if CaptionConfig.MARGIN_V < 280:
        result['warnings'].append(f"CaptionConfig: MARGIN_V={CaptionConfig.MARGIN_V} (recommended 300+)")
    
    # Check API Keys — FIX: was calling class method, must use instance
    missing = API_KEYS.missing_keys()
    if missing:
        result['warnings'].append(f"APIKeys: Missing: {', '.join(missing)}")
        result['status'] = 'degraded'
    
    return result


# ============================================================
# INSTANCES — Create Config Objects
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
    print("📊 CONFIGURATION STATUS (GROQ NATIVE)")
    print("=" * 60)
    
    print("\n🎯 NICHE:")
    print(f"    Topics: {len(NICHE_CONFIG.TOPICS)}")
    print(f"    Keywords: {len(NICHE_CONFIG.KEYWORDS)}")
    print(f"    Sub-niches: {len(NICHE_CONFIG.SUB_NICHES)}")
    
    print("\n🎬 VIDEO:")
    print(f"    Duration: {VIDEO_CONFIG.DURATION_MIN}-{VIDEO_CONFIG.DURATION_MAX}s")
    print(f"    Resolution: {VIDEO_CONFIG.RESOLUTION}")
    print(f"    FPS: {VIDEO_CONFIG.FPS}")
    
    print("\n🎙️ AUDIO:")
    print(f"    Voice Engine: {AUDIO_CONFIG.MODEL}")
    print(f"    Selected Voice: {AUDIO_CONFIG.VOICE}")
    
    print("\n📝 CAPTIONS:")
    print(f"    Font Size: {CAPTION_CONFIG.FONT_SIZE}px")
    print(f"    Alignment: {CAPTION_CONFIG.ALIGNMENT}")
    print(f"    Margin V: {CAPTION_CONFIG.MARGIN_V}")
    
    print("\n🔑 API KEYS:")
    api_status = API_KEYS.validate()
    for key, value in api_status.items():
        status = "✅" if value else "❌"
        print(f"    {status} {key}")
    
    print("\n🔍 HEALTH CHECK:")
    health = health_check()
    print(f"    Status: {health['status']}")
    if health['warnings']:
        print(f"    ⚠️ Warnings: {len(health['warnings'])}")
        for warning in health['warnings']:
            print(f"       - {warning}")
    if health['errors']:
        print(f"    ❌ Errors: {len(health['errors'])}")
        for error in health['errors']:
            print(f"       - {error}")
    
    print("\n" + "=" * 60)


# ============================================================
# RUN STATUS
# ============================================================
if __name__ == "__main__":
    display_status()
