"""Settings — Synced with all fixed modules"""

import os
from dataclasses import dataclass
from typing import List, Dict
from datetime import time


@dataclass
class VideoConfig:
    # FIX: Duration target 40-55s (sync with audio_generator.py + content_generator.py)
    DURATION_MIN: int = 40
    DURATION_MAX: int = 55
    TARGET_DURATION: int = 47  # NEW: Middle of range for optimal pacing

    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 23  # FIX: 18 → 23 (faster encoding, still high quality)
    PRESET: str = "medium"  # FIX: "slow" → "medium" (faster, good enough for Shorts)

    # FIX: Segment durations (sync with content_generator.py)
    HOOK_DURATION: float = 6.0
    SHOCK_DURATION: float = 3.5  # NEW: Visual shock moment
    SUSPENSE_DURATION: float = 4.5
    STORY_DURATION: float = 30.0
    CTR_DURATION: float = 4.0
    PAUSE_DURATION: float = 0.4

    # FIX: Cuts = 2.5-5s (sync with video_assembler.py smooth cuts)
    FAST_CUT_INTERVAL: float = 2.5  # FIX: 0.8 → 2.5 (smooth, not choppy)
    CUT_MIN_DURATION: float = 2.0  # NEW: Minimum cut length
    CUT_MAX_DURATION: float = 5.0  # NEW: Maximum cut length

    ZOOM_INTENSITY: float = 1.25
    SHAKE_INTENSITY: int = 3

    # NEW: Keyframe settings for smooth playback
    KEYFRAME_INTERVAL: int = 30  # 1 second at 30fps
    SCENE_CHANGE_THRESHOLD: int = 0  # Disable scene change detection


@dataclass
class AudioConfig:
    # Voice: deep, mysterious, cinematic for USA/UK audience
    VOICE: str = "en-US-GuyNeural"
    RATE: str = "-5%"  # FIX: -12% → -5% (base rate, audio_generator.py dynamic override)
    PITCH: str = "-3Hz"
    VOLUME: str = "+10%"

    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"

    # Background audio
    BG_MUSIC_VOLUME: float = 0.06
    FAN_NOISE_VOLUME: float = 0.018
    SFX_VOLUME: float = 0.25

    # FIX: WPM = 130 (sync with audio_generator.py target)
    # 130 WPM = ~2.17 words/sec → 100 words = 46s, 115 words = 53s
    WORDS_PER_MINUTE: int = 130

    # NEW: Dynamic rate range (audio_generator.py uses this)
    RATE_MIN: int = -15  # Fastest (for long scripts)
    RATE_MAX: int = 10   # Slowest (for short scripts)

    # NEW: Target duration enforcement
    TARGET_DURATION_MIN: float = 40.0
    TARGET_DURATION_MAX: float = 55.0


@dataclass
class CaptionConfig:
    """CapCut-style — USA/UK Shorts standard — Red/White alternating words"""
    FONT_SIZE: int = 90  # FIX: 95 → 90 (consistent with video_assembler.py)
    FONT_NAME: str = "Arial"
    BOLD: int = 1

    PRIMARY_COLOR: str = "&H00FFFFFF"    # White (even words)
    SECONDARY_COLOR: str = "&H000000FF"  # Red (odd words, BGR format)
    OUTLINE_COLOR: str = "&H00000000"    # Black outline
    OUTLINE_WIDTH: int = 6
    SHADOW: int = 2

    # FIX: ALIGNMENT 2 = bottom-center (safe from YouTube UI)
    # MARGIN_V = 1400 = lower 40% of 1920 height (safe zone)
    ALIGNMENT: int = 2  # FIX: 5 → 2 (bottom-center, not middle)
    MARGIN_V: int = 1400  # FIX: 0 → 1400 (safe zone)

    HIGHLIGHT_COLOR: str = "&H000000FF"  # Red emphasis

    # NEW: Karaoke settings
    MAX_WORDS_PER_LINE: int = 3  # FIX: 2 → 3 (optimal readability)
    ALTERNATE_COLORS: bool = True
    ACTIVE_WORD_SCALE: float = 1.15  # NEW: 115% size for active word
    SAFE_ZONE_TOP: int = 0
    SAFE_ZONE_BOTTOM: int = 350  # YouTube subscribe button area


@dataclass
class SEOConfig:
    # FIX: Title 40-60 chars (Shorts sweet spot)
    TITLE_MAX_LENGTH: int = 50  # FIX: 40 → 50 (slightly more flexible)
    TITLE_MIN_LENGTH: int = 10

    DESCRIPTION_LENGTH: int = 125  # 100-150 words target
    TAGS_COUNT: int = 12  # 10-14 range

    # FIX: Category 22 = People & Blogs (better RPM for mystery niche)
    # 27 = Education, 28 = Science & Tech
    CATEGORY_ID: str = "22"  # FIX: "27" → "22"

    MADE_FOR_KIDS: bool = False
    LICENSE: str = "youtube"
    PRIVACY_STATUS: str = "public"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_AUDIO_LANGUAGE: str = "en"

    # NEW: Shorts-specific
    HASHTAGS_REQUIRED: List[str] = None  # Set in __post_init__

    def __post_init__(self):
        self.HASHTAGS_REQUIRED = ["#Shorts", "#shorts", "#psychology", "#science"]


@dataclass
class ThumbnailConfig:
    # FIX: 9:16 for Shorts shelf (was 1280x720 landscape!)
    RESOLUTION: tuple = (1080, 1920)  # FIX: (1280, 720) → (1080, 1920)
    STYLE: str = "suspense"

    WORD_COUNT: int = 3
    FONT_SIZE_MAIN: int = 140  # FIX: 120 → 140 (bigger for mobile)
    FONT_SIZE_SUB: int = 50

    # Color psychology: dark backgrounds + high contrast text
    BG_COLORS: List[str] = None
    TEXT_COLORS: List[str] = None
    ACCENT_COLORS: List[str] = None

    DROP_SHADOW: bool = True
    OUTLINE_WIDTH: int = 8
    GLOW_EFFECT: bool = True

    # NEW: Visual elements
    BORDER_COLOR: str = "#FF6B35"  # Orange = curiosity
    BORDER_WIDTH: int = 14
    EMOJI_ENABLED: bool = True

    def __post_init__(self):
        self.BG_COLORS = ["#0A0A1A", "#1A0505", "#0F1A0A", "#1A1005", "#050A1A"]
        self.TEXT_COLORS = ["#FF6B35", "#00D4FF", "#FFD700", "#FF3366", "#39FF14"]
        self.ACCENT_COLORS = ["#FF0000", "#FF4500", "#FFD700"]


@dataclass
class PlatformConfig:
    TARGET_AUDIENCE: str = "US,UK,CA,AU"
    TIMEZONE: str = "America/New_York"

    # FIX: 3 Shorts/day with delay (rate limit protection)
    DAILY_SHORTS_COUNT: int = 3
    UPLOAD_DELAY_SECONDS: int = 120  # NEW: 2 min between uploads

    # Posting times (peak traffic)
    YOUTUBE_POST_TIMES: List[time] = None
    FACEBOOK_POST_TIMES: List[time] = None
    INSTAGRAM_POST_TIMES: List[time] = None

    def __post_init__(self):
        self.YOUTUBE_POST_TIMES = [time(9, 0), time(14, 0), time(17, 0)]  # FIX: Added 2PM
        self.FACEBOOK_POST_TIMES = [time(10, 0), time(18, 0)]
        self.INSTAGRAM_POST_TIMES = [time(11, 0), time(19, 0)]


@dataclass
class NicheConfig:
    # USA/UK viral dark psychology + mind-body science topics
    TOPICS: List[str] = None

    SUB_NICHES: List[str] = None
    KEYWORDS: List[str] = None

    def __post_init__(self):
        self.TOPICS = [
            # Sleep & Brain (High suspense)
            "why your body jerks when falling asleep",
            "what happens to your brain when you die",
            "sleep paralysis science explained",
            "why deja vu happens to your brain",
            "how your brain creates false memories",
            "why we forget dreams instantly",
            "what lucid dreaming does to your brain",
            "why sleep paralysis feels so real",

            # Dark Psychology (High engagement)
            "dark psychology manipulation tactics",
            "how governments use psychology to control you",
            "social media addiction brain science",
            "why you cant stop doomscrolling",
            "how corporations exploit your psychology",
            "why people believe conspiracy theories",
            "the psychology of mass hysteria",

            # Body Mysteries (Visual shock potential)
            "how blood is actually made in your body",
            "why humans are afraid of the dark",
            "what your body does the moment you die",
            "why some people never feel fear",
            "the science of gut feeling intuition",
            "why we get goosebumps for no reason",
            "what adrenaline does to your body visually",

            # Mind Control (Controversial = viral)
            "subliminal messaging in advertising",
            "how cult leaders control peoples minds",
            "the psychology of brainwashing",
            "why people join cults explained",
            "how your environment controls your thoughts",

            # Shocking Science (High shareability)
            "banned psychological experiments",
            "the stanford prison experiment truth",
            "milgram obedience experiment dark truth",
            "what happens to your brain on no sleep",
            "the science of near death experiences",
            "why time feels slower in danger",
            "how your brain tricks your eyes",
        ]

        self.SUB_NICHES = [
            "dating psychology", "workplace manipulation",
            "criminal psychology", "ancient mysteries",
            "neuroscience secrets", "behavioral economics",
            "sleep science", "memory hacking",
        ]

        self.KEYWORDS = [
            "psychology", "brain", "mind", "dark psychology",
            "science", "mystery", "secret", "shocking",
            "manipulation", "control", "behavior", "neuroscience",
            "sleep", "dream", "memory", "fear", "adrenaline",
        ]


class APIKeys:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_CLIENT_SECRETS: str = os.getenv("YOUTUBE_CLIENT_SECRETS", "")
    REFRESH_TOKEN: str = os.getenv("REFRESH_TOKEN", "")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_USER_ID: str = os.getenv("INSTAGRAM_USER_ID", "")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")

    # NEW: Validation method
    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            'groq': bool(cls.GROQ_API_KEY),
            'youtube': bool(cls.YOUTUBE_API_KEY and cls.REFRESH_TOKEN),
            'pexels': bool(cls.PEXELS_API_KEY),
            'pixabay': bool(cls.PIXABAY_API_KEY),
        }


# ═══════════════════════════════════════════════════════════
# INSTANCES
# ═══════════════════════════════════════════════════════════

VIDEO_CONFIG = VideoConfig()
AUDIO_CONFIG = AudioConfig()
CAPTION_CONFIG = CaptionConfig()
SEO_CONFIG = SEOConfig()
THUMBNAIL_CONFIG = ThumbnailConfig()
PLATFORM_CONFIG = PlatformConfig()
NICHE_CONFIG = NicheConfig()
API_KEYS = APIKeys()

# NEW: Validation check on import
_key_status = API_KEYS.validate()
print(f"  🔑 API Status: {sum(_key_status.values())}/{len(_key_status)} configured")
if not _key_status['youtube']:
    print("  ⚠️ WARNING: YouTube credentials missing — upload will fail!")
if not _key_status['groq']:
    print("  ⚠️ WARNING: Groq API missing — content generation will fail!")
