"""
Settings — REFINED: Memory & Brain Fog Science for Men 35+ (GROQ SPEECH READY)
AUDIENCE: USA/UK Males 35-54
NICHE: Memory Loss & Brain Fog (Micro-Niche)
GOAL: Low Competition, High Demand

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
    DURATION_MIN: int = 35
    DURATION_MAX: int = 55
    TARGET_DURATION: int = 48

    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 23
    PRESET: str = "medium"

    # Segment durations — AUDIENCE MATCHED
    HOOK_DURATION: float = 3.5
    SHOCK_DURATION: float = 3.0
    SUSPENSE_DURATION: float = 5.0
    STORY_DURATION: float = 32.0
    CTR_DURATION: float = 4.0
    PAUSE_DURATION: float = 0.5

    # Cut intervals — CALM not choppy (35-54 hate rapid cuts)
    FAST_CUT_INTERVAL: float = 3.5
    CUT_MIN_DURATION: float = 3.0
    CUT_MAX_DURATION: float = 6.0

    # Effects — subtle for this audience
    ZOOM_INTENSITY: float = 1.12
    SHAKE_INTENSITY: int = 1

    KEYFRAME_INTERVAL: int = 30
    SCENE_CHANGE_THRESHOLD: int = 0


# ============================================================
# AUDIO CONFIG — Voice Matched to 35-54 Male Audience (GROQ)
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
# CAPTION CONFIG — Readable for 35-54 Audience on Mobile
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

    # Category 27 = Education — Credibility for 35-54 audience
    CATEGORY_ID: str = "27"

    MADE_FOR_KIDS: bool = False
    LICENSE: str = "youtube"
    PRIVACY_STATUS: str = "public"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_AUDIO_LANGUAGE: str = "en"

    HASHTAGS_REQUIRED: List[str] = field(default_factory=list)

    def __post_init__(self):
        # REFINED: Memory & Brain Fog hashtags
        self.HASHTAGS_REQUIRED = [
            "#Shorts", "#shorts",
            "#MemoryFacts", "#BrainFog", "#BrainHealth",
            "#MemoryLoss", "#MenOver35"
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
# PLATFORM CONFIG — Posting Times for 35-54 Schedule
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
        # Lunch break (12pm), after work (6:30pm), evening (9pm)
        self.YOUTUBE_POST_TIMES = [time(12, 0), time(18, 30), time(21, 0)]
        self.FACEBOOK_POST_TIMES = [time(12, 30), time(19, 0)]
        self.INSTAGRAM_POST_TIMES = [time(12, 0), time(20, 0)]


# ============================================================
# NICHE CONFIG — REFINED: Memory & Brain Fog Only
# ============================================================
@dataclass
class NicheConfig:
    # REFINED: ONLY Memory & Brain Fog topics
    TOPICS: List[str] = field(default_factory=list)
    SUB_NICHES: List[str] = field(default_factory=list)
    KEYWORDS: List[str] = field(default_factory=list)

    def __post_init__(self):
        # ============================================================
        # MEMORY TOPICS
        # ============================================================
        self.TOPICS = [
            # Name Memory
            "why you forget names after 35",
            "why you forget names right after hearing them",
            "why you can't remember names you just heard",
            
            # Room Memory
            "why you walk into a room and forget why",
            "why you forget what you were about to do",
            "why you keep losing your train of thought",
            
            # General Memory
            "why your memory gets worse after 40",
            "why short term memory gets worse with age",
            "why you forget things you just read",
            "why you forget words while speaking",
            "why your brain deletes memories while you sleep",
            "why men forget things more as they age",
            "why you forget what you were saying mid-sentence",
            
            # Brain Fog
            "what causes brain fog in adults",
            "why brain fog happens after 35",
            "why you feel mentally foggy all the time",
            "what causes brain fog and memory loss",
            "why brain fog gets worse with age",
            "why you feel spaced out and can't focus",
            "why your brain feels slow and tired",
        ]

        # ============================================================
        # SUB-NICHES
        # ============================================================
        self.SUB_NICHES = [
            "memory loss after 35",
            "men's brain health after 40",
            "brain fog in adults",
            "why men forget things",
            "memory improvement for men",
            "cognitive decline in men",
            "short term memory loss",
        ]

        # ============================================================
        # KEYWORDS — Search Terms Used by 35-54 Males
        # ============================================================
        self.KEYWORDS = [
            # Primary
            "memory", "forget", "brain fog", "remember",
            "memory loss", "brain health", "cognitive decline",
            
            # Long-tail (what they actually search)
            "why can't I remember", "memory tips for men",
            "men over 35 memory", "brain fog causes",
            "forgetting names", "short term memory",
            
            # Related
            "brain science", "men's health", "cognitive function",
            "memory improvement", "brain exercises",
        ]


# ============================================================
# API KEYS — Load from Environment
# ============================================================
class APIKeys:
    # AI & Content
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Stock Footage
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")
    
    # YouTube
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_CLIENT_SECRETS: str = os.getenv("YOUTUBE_CLIENT_SECRETS", "")
    REFRESH_TOKEN: str = os.getenv("REFRESH_TOKEN", "")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Facebook
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    
    # Instagram
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_USER_ID: str = os.getenv("INSTAGRAM_USER_ID", "")
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Check which APIs are configured"""
        return {
            'groq': bool(cls.GROQ_API_KEY),
            'pexels': bool(cls.PEXELS_API_KEY),
            'pixabay': bool(cls.PIXABAY_API_KEY),
            'youtube': bool(cls.REFRESH_TOKEN and cls.GOOGLE_CLIENT_ID),
            'facebook': bool(cls.FACEBOOK_ACCESS_TOKEN and cls.FACEBOOK_PAGE_ID),
            'instagram': bool(cls.INSTAGRAM_ACCESS_TOKEN and cls.INSTAGRAM_USER_ID),
            'cloudinary': bool(cls.CLOUDINARY_CLOUD_NAME and cls.CLOUDINARY_API_KEY),
        }

    @classmethod
    def missing_keys(cls) -> List[str]:
        """Return list of missing API keys"""
        return [k for k, v in cls.validate().items() if not v]


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
    
    # Check API Keys
    missing = APIKeys.missing_keys()
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
