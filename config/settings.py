import os
from dataclasses import dataclass
from typing import List
from datetime import time

@dataclass
class VideoConfig:
    DURATION_MIN = 45          # FIX: 40 -> 45 (Aapki target range 45-55 ke mutabiq)
    DURATION_MAX = 55          # Target 45-55 seconds
    RESOLUTION = (1080, 1920)
    FPS = 30
    BITRATE = "8000k"
    CRF = 18
    PRESET = "slow"
    
    # Timestamps ratio distribution for 45-55s duration range
    HOOK_DURATION = 6.0
    SUSPENSE_DURATION = 5.0    # FIX: 4.0 -> 5.0 (Tension hold badhane ke liye)
    STORY_DURATION = 37.0      # FIX: 32.0 -> 37.0 (Video lambi karne ke liye duration yahan badhayi)
    CTR_DURATION = 4.0         # FIX: 3.0 -> 4.0 (End loop clear rakhne ke liye)
    
    FAST_CUT_INTERVAL = 0.8    # 0.8s is perfect for retention loops
    ZOOM_INTENSITY = 1.25      
    SHAKE_INTENSITY = 3

@dataclass
class AudioConfig:
    # Dark psychology voice - Deep, mysterious, cinematic feel for USA/UK audience
    VOICE: str = "en-US-GuyNeural"          
    RATE: str = "-4%"                       # FIX: -12% bohot slow aur robotic tha, -4% par smooth aur natural lagta hai
    PITCH: str = "-1Hz"                     # FIX: -3Hz deepness ko distort kar rha tha, -1Hz perfect heavy masculine voice deta hai
    VOLUME: str = "+10%"
    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"
    BG_MUSIC_VOLUME: float = 0.05           # Subtle background score
    FAN_NOISE_VOLUME: float = 0.015         # Room/ambient tone to mask silence breaks
    SFX_VOLUME: float = 0.25
    WORDS_PER_MINUTE: int = 155             # FIX: 120 -> 155 (Normal conversational speed takay robotic trailing sound na aaye)

@dataclass
class CaptionConfig:
    """CapCut-style — USA/UK Shorts standard — Red/White alternating words"""
    FONT_SIZE: int = 95            
    FONT_NAME: str = "Arial"
    BOLD: int = 1
    PRIMARY_COLOR: str = "&H00FFFFFF"    # White
    SECONDARY_COLOR: str = "&H000000FF"  # Red (BGR format)
    OUTLINE_COLOR: str = "&H00000000"    # Black outline
    OUTLINE_WIDTH: int = 6               
    SHADOW: int = 2
    ALIGNMENT: int = 5                   # Screen center middle placement
    MARGIN_V: int = 0                    # True center alignment
    HIGHLIGHT_COLOR: str = "&H000000FF"  
    # FIX: caption_generator.py reads these two fields but they were never
    # defined here, so the moment anyone instantiated CaptionGenerator() it
    # crashed with AttributeError. (video_assembler.py builds its ASS
    # subtitles directly and doesn't hit this, which is why it went unnoticed.)
    MAX_WORDS_PER_LINE: int = 2          # Short lines = faster-reading captions
    ALTERNATE_COLORS: bool = True        # Even lines red, odd lines white

@dataclass
class SEOConfig:
    TITLE_MAX_LENGTH = 40          
    DESCRIPTION_LENGTH = 125       
    TAGS_COUNT = 12                
    CATEGORY_ID = "27"             # Education (Best category for engagement algorithms in Psychology)
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
    DAILY_SHORTS_COUNT = 3  
    YOUTUBE_POST_TIMES = [time(9, 0), time(17, 0)]
    FACEBOOK_POST_TIMES = [time(10, 0), time(18, 0)]
    INSTAGRAM_POST_TIMES = [time(11, 0), time(19, 0)]

@dataclass
class NicheConfig:
    TOPICS = [
        "why your body jerks when falling asleep",
        "what happens to your brain when you die",
        "sleep paralysis science explained",
        "why deja vu happens to your brain",
        "how your brain creates false memories",
        "dark psychology manipulation tactics",
        "how governments use psychology to control you",
        "social media addiction brain science",
        "why you cant stop doomscrolling",
        "how corporations exploit your psychology",
        "how blood is actually made in your body",
        "why humans are afraid of the dark",
        "what your body does the moment you die",
        "why some people never feel fear",
        "the science of gut feeling intuition",
        "subliminal messaging in advertising",
        "how cult leaders control peoples minds",
        "the psychology of mass hysteria",
        "why people believe conspiracy theories",
        "how your environment controls your thoughts",
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
    REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")              
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")        
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")  
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")  
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
