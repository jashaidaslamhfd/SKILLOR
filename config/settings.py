import os
from dataclasses import dataclass
from typing import List
from datetime import time

@dataclass
class VideoConfig:
    DURATION_MIN = 40
    DURATION_MAX = 55
    RESOLUTION = (1080, 1920)
    FPS = 30
    BITRATE = "8000k"
    CRF = 18
    PRESET = "slow"
    HOOK_DURATION = 6.0
    SUSPENSE_DURATION = 4.0
    STORY_DURATION = 32.0
    CTR_DURATION = 3.0
    FAST_CUT_INTERVAL = 0.8    # FIX: 1.5 → 0.8 (TikTok/Reels speed for USA/UK viral)
    ZOOM_INTENSITY = 1.25      # FIX: 1.15 → 1.25 (more aggressive zoom = attention)
    SHAKE_INTENSITY = 3

@dataclass
class AudioConfig:
    # Dark psychology voice - deep, mysterious, cinematic feel for USA/UK audience
    VOICE: str = "en-US-GuyNeural"          # FIX: Christopher → Guy (deeper, more intense)
    RATE: str = "-12%"                       # FIX: -3% → -12% (slower = more dramatic)
    PITCH: str = "-3Hz"                      # FIX: +0Hz → -3Hz (deeper voice = dark feel)
    VOLUME: str = "+10%"
    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"
    BG_MUSIC_VOLUME: float = 0.06           # FIX: 0.08 → 0.06 (subtle, not distracting)
    FAN_NOISE_VOLUME: float = 0.018         # FIX: NEW - continuous fan/room tone
    SFX_VOLUME: float = 0.25
    WORDS_PER_MINUTE: int = 120             # FIX: 130 → 120 (slower = clearer for USA/UK)

@dataclass
class CaptionConfig:
    """CapCut-style — USA/UK Shorts standard — Red/White alternating words"""
    FONT_SIZE: int = 95            # FIX: 90 → 95 (slightly bigger = more readable on mobile)
    FONT_NAME: str = "Arial"
    BOLD: int = 1
    PRIMARY_COLOR: str = "&H00FFFFFF"    # White (even-indexed words)
    SECONDARY_COLOR: str = "&H000000FF"  # FIX: NEW - Red (odd-indexed words, BGR format)
    OUTLINE_COLOR: str = "&H00000000"    # Black outline
    OUTLINE_WIDTH: int = 6               # FIX: 5 → 6 (thicker outline = more readable)
    SHADOW: int = 2
    # FIX: ALIGNMENT 5 = middle-center (screen center, not top)
    ALIGNMENT: int = 5                   # FIX: 8 (top) → 5 (middle = screen center)
    MARGIN_V: int = 0                    # FIX: 300 → 0 (true center)
    HIGHLIGHT_COLOR: str = "&H000000FF"  # Red for emphasis

@dataclass
class SEOConfig:
    TITLE_MAX_LENGTH = 40          # FIX: 60 → 40 (Shorts: short titles win)
    DESCRIPTION_LENGTH = 125       # FIX: 300 → 125 (100-150 words target)
    TAGS_COUNT = 12                # FIX: 15 → 12 (10-14 range, quality over quantity)
    CATEGORY_ID = "27"             # FIX: "28" (Science) → "27" (Education) — better for dark psych
    MADE_FOR_KIDS = False
    LICENSE = "youtube"
    PRIVACY_STATUS = "public"
    DEFAULT_LANGUAGE = "en"
    DEFAULT_AUDIO_LANGUAGE = "en"

@dataclass
class ThumbnailConfig:
    RESOLUTION = (1280, 720)
    STYLE = "suspense"
    WORD_COUNT = 3
    FONT_SIZE_MAIN = 120
    FONT_SIZE_SUB = 40
    BG_COLORS = ["#0a0a0a", "#1a0000", "#00051a", "#1a0a00"]
    TEXT_COLORS = ["#ff3333", "#ff6600", "#ffff00", "#ffffff"]
    ACCENT_COLORS = ["#ff0000", "#ff4500", "#ffd700"]
    DROP_SHADOW = True
    OUTLINE_WIDTH = 8
    GLOW_EFFECT = True

@dataclass
class PlatformConfig:
    TARGET_AUDIENCE = "US,UK,CA,AU"
    TIMEZONE = "America/New_York"
    DAILY_SHORTS_COUNT = 3  # FIX: was missing, caused AttributeError — "3 Shorts/day" target
    YOUTUBE_POST_TIMES = [time(9, 0), time(17, 0)]
    FACEBOOK_POST_TIMES = [time(10, 0), time(18, 0)]
    INSTAGRAM_POST_TIMES = [time(11, 0), time(19, 0)]

@dataclass
class NicheConfig:
    # USA/UK viral dark psychology + mind-body science topics
    TOPICS = [
        # Sleep & Brain
        "why your body jerks when falling asleep",
        "what happens to your brain when you die",
        "sleep paralysis science explained",
        "why deja vu happens to your brain",
        "how your brain creates false memories",
        # Dark Psychology
        "dark psychology manipulation tactics",
        "how governments use psychology to control you",
        "social media addiction brain science",
        "why you cant stop doomscrolling",
        "how corporations exploit your psychology",
        # Body Mysteries
        "how blood is actually made in your body",
        "why humans are afraid of the dark",
        "what your body does the moment you die",
        "why some people never feel fear",
        "the science of gut feeling intuition",
        # Mind Control
        "subliminal messaging in advertising",
        "how cult leaders control peoples minds",
        "the psychology of mass hysteria",
        "why people believe conspiracy theories",
        "how your environment controls your thoughts",
        # Shocking Science
        "banned psychological experiments",
        "the stanford prison experiment truth",
        "milgram obedience experiment dark truth",
        "what happens to your brain on no sleep",
        "the science of near death experiences",
    ]
    SUB_NICHES = [
        "dating psychology", "workplace manipulation",
        "criminal psychology", "ancient mysteries",
        "neuroscience secrets", "behavioral economics"
    ]
    KEYWORDS = [
        "psychology", "brain", "mind", "dark psychology",
        "science", "mystery", "secret", "shocking",
        "manipulation", "control", "behavior", "neuroscience"
    ]

class APIKeys:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS")
    REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")              # FIX: was missing, caused AttributeError
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")        # FIX: was missing, caused AttributeError
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  # FIX: was missing, caused AttributeError
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")  # FIX: was missing, caused AttributeError
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")  # FIX: was missing, caused AttributeError
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

VIDEO_CONFIG = VideoConfig()
AUDIO_CONFIG = AudioConfig()
CAPTION_CONFIG = CaptionConfig()
SEO_CONFIG = SEOConfig()
THUMBNAIL_CONFIG = ThumbnailConfig()
PLATFORM_CONFIG = PlatformConfig()
NICHE_CONFIG = NicheConfig()
API_KEYS = APIKeys()
