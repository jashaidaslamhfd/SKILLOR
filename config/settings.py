"""Settings — Audience-Matched: USA/UK Males 35-54, Calm Credible Tone"""

import os
from dataclasses import dataclass
from typing import List, Dict
from datetime import time


@dataclass
class VideoConfig:
    # Duration: 45-55s sweet spot for 35-54 audience
    # This age group needs slightly more time to process info vs teens
    DURATION_MIN: int = 42
    DURATION_MAX: int = 55
    TARGET_DURATION: int = 48

    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 23
    PRESET: str = "medium"

    # Segment durations — AUDIENCE MATCHED
    # 35-54 males need slightly longer hook to process (not teen 1-second reaction)
    HOOK_DURATION: float = 5.0      # Slightly shorter — statement lands fast
    SHOCK_DURATION: float = 3.0     # Quick surprising fact
    SUSPENSE_DURATION: float = 5.0  # Give them time to think
    STORY_DURATION: float = 32.0    # Main content — this audience wants substance
    CTR_DURATION: float = 4.0
    PAUSE_DURATION: float = 0.5     # Slightly longer pauses = more natural/human feel

    # Cut intervals — CALM not choppy
    # 35-54 males hate rapid cuts — feels like teen content, they swipe
    # 3.5-6s cuts = documentary feel = credible = they stay
    FAST_CUT_INTERVAL: float = 3.5  # UPDATED: 2.5 → 3.5 (calmer, less teen)
    CUT_MIN_DURATION: float = 3.0   # UPDATED: 2.0 → 3.0
    CUT_MAX_DURATION: float = 6.0   # UPDATED: 5.0 → 6.0

    # Effects — subtle for this audience
    # Heavy zoom/shake = teen TikTok feel = this audience swipes
    ZOOM_INTENSITY: float = 1.12    # UPDATED: 1.25 → 1.12 (subtle, credible)
    SHAKE_INTENSITY: int = 1        # UPDATED: 3 → 1 (almost no shake)

    KEYFRAME_INTERVAL: int = 30
    SCENE_CHANGE_THRESHOLD: int = 0


@dataclass
class AudioConfig:
    # ═══════════════════════════════════════════════════════
    # VOICE — Matched to 35-54 Male USA/UK Audience
    # ═══════════════════════════════════════════════════════
    # These men trust a calm, deep, credible male voice.
    # They do NOT respond to energetic/hype voices — sounds like an ad.
    #
    # BEST VOICE FOR THIS AUDIENCE: en-US-GuyNeural
    # — Deep, calm, mature American male
    # — Sounds like a trusted friend explaining something
    # — NOT young/energetic like Brian
    # — Exactly what a 40-year-old man trusts
    #
    # ALTERNATIVES if you want to test:
    #   "en-US-AndrewMultilingualNeural" — slightly warmer, also good
    #   "en-GB-RyanNeural"               — British accent, good for UK audience
    #   "en-US-ChristopherNeural"        — deep authoritative, slightly formal
    #
    VOICE: str = "en-US-GuyNeural"  # AUDIENCE MATCH: Deep calm male = 35-54 trust signal

    # Rate: -5% = noticeably slower than default
    # This audience is NOT in a rush. Slow = thoughtful = credible.
    # Fast rate = sounds like AI trying to fit words in = they notice = swipe
    RATE: str = "-5%"   # UPDATED: -3% → -5% (calmer pace for mature audience)

    PITCH: str = "+0Hz"  # No pitch shift — natural is always better
    VOLUME: str = "+0%"  # Clean, no compression

    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    AUDIO_BITRATE: str = "192k"

    # Background audio — VERY subtle for this audience
    # 35-54 males are more likely to notice intrusive background music
    # and find it annoying (unlike teens who expect it)
    # Music should be BARELY noticeable — like a quiet room, not a music video
    BG_MUSIC_VOLUME: float = 0.03   # UPDATED: 0.04 → 0.03 (nearly invisible)
    FAN_NOISE_VOLUME: float = 0.010  # UPDATED: 0.012 → 0.010 (just room presence)
    SFX_VOLUME: float = 0.15        # UPDATED: 0.20 → 0.15 (subtle transitions)

    # WPM: 120 = calm adult conversation pace
    # 130+ WPM = starts sounding like AI reading fast
    # 120 WPM = how a person actually tells a story
    WORDS_PER_MINUTE: int = 120     # UPDATED: 130 → 120

    # Rate range: tight range = consistent calm tone
    # Wide range causes jarring speed changes = unnatural = robotic feel
    RATE_MIN: int = -6   # UPDATED: -5 → -6 (calmer floor)
    RATE_MAX: int = 2    # UPDATED: 5 → 2 (never speeds up much = always calm)

    TARGET_DURATION_MIN: float = 42.0
    TARGET_DURATION_MAX: float = 55.0


@dataclass
class CaptionConfig:
    """Captions — Readable for 35-54 audience on mobile"""
    # Slightly larger font — this age group appreciates readability
    FONT_SIZE: int = 88
    FONT_NAME: str = "Arial"
    BOLD: int = 1

    # Color scheme — UPDATED for mature audience
    # Pure white + yellow highlight = easier to read = less teen TikTok feel
    # Red/white alternating = too busy for this audience
    PRIMARY_COLOR: str = "&H00FFFFFF"    # White
    SECONDARY_COLOR: str = "&H0000FFFF"  # Yellow (BGR) — easier on eyes than red
    OUTLINE_COLOR: str = "&H00000000"    # Black outline
    OUTLINE_WIDTH: int = 7               # Slightly thicker = more readable
    SHADOW: int = 3

    ALIGNMENT: int = 5   # True center
    MARGIN_V: int = 0

    HIGHLIGHT_COLOR: str = "&H0000FFFF"  # Yellow highlight (matches secondary)

    MAX_WORDS_PER_LINE: int = 3
    ALTERNATE_COLORS: bool = True
    ACTIVE_WORD_SCALE: float = 1.10  # UPDATED: 1.15 → 1.10 (subtle, not flashy)
    SAFE_ZONE_TOP: int = 0
    SAFE_ZONE_BOTTOM: int = 350


@dataclass
class SEOConfig:
    TITLE_MAX_LENGTH: int = 55   # UPDATED: slightly longer — age-relevant titles need space
    TITLE_MIN_LENGTH: int = 20   # UPDATED: minimum meaningful title

    DESCRIPTION_LENGTH: int = 130
    TAGS_COUNT: int = 12

    # Category 27 = Education — better for 35-54 credibility seekers
    # This audience responds to educational framing, not entertainment
    CATEGORY_ID: str = "27"      # UPDATED: "22" → "27" (Education = credible)

    MADE_FOR_KIDS: bool = False
    LICENSE: str = "youtube"
    PRIVACY_STATUS: str = "public"
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_AUDIO_LANGUAGE: str = "en"

    HASHTAGS_REQUIRED: List[str] = None

    def __post_init__(self):
        # Hashtags matched to 35-54 male search behavior
        self.HASHTAGS_REQUIRED = [
            "#Shorts", "#shorts", "#BrainFacts", "#HealthFacts", "#ScienceFacts"
        ]


@dataclass
class ThumbnailConfig:
    RESOLUTION: tuple = (1080, 1920)
    STYLE: str = "credible"  # UPDATED: "suspense" → "credible"

    WORD_COUNT: int = 3
    FONT_SIZE_MAIN: int = 130   # UPDATED: 140 → 130 (slightly less aggressive)
    FONT_SIZE_SUB: int = 52

    # Color scheme — UPDATED for 35-54 male audience
    # Deep navy/dark backgrounds = credible/science feel (not horror)
    # Bright white + gold text = trustworthy, not clickbait
    BG_COLORS: List[str] = None
    TEXT_COLORS: List[str] = None
    ACCENT_COLORS: List[str] = None

    DROP_SHADOW: bool = True
    OUTLINE_WIDTH: int = 7
    GLOW_EFFECT: bool = False   # UPDATED: True → False (glow = teen style)

    BORDER_COLOR: str = "#4A90D9"  # UPDATED: orange → blue (credible/science)
    BORDER_WIDTH: int = 12
    EMOJI_ENABLED: bool = True

    def __post_init__(self):
        # Dark but not horror — science/documentary feel
        self.BG_COLORS = ["#050A1A", "#0A0F1E", "#080D18", "#060B15", "#0D1220"]
        # Gold/white/light blue = credible, not scary
        self.TEXT_COLORS = ["#FFD700", "#FFFFFF", "#4FC3F7", "#E8E8E8", "#FFF9C4"]
        self.ACCENT_COLORS = ["#4A90D9", "#FFD700", "#FFFFFF"]


@dataclass
class PlatformConfig:
    TARGET_AUDIENCE: str = "US,UK,CA,AU"
    TIMEZONE: str = "America/New_York"

    DAILY_SHORTS_COUNT: int = 3
    UPLOAD_DELAY_SECONDS: int = 120

    # Posting times — UPDATED for 35-54 male schedule
    # This audience is online: lunch break (12-1pm), after work (6-8pm), before bed (9-11pm)
    # NOT: early morning (they're getting kids to school / commuting)
    YOUTUBE_POST_TIMES: List[time] = None
    FACEBOOK_POST_TIMES: List[time] = None
    INSTAGRAM_POST_TIMES: List[time] = None

    def __post_init__(self):
        self.YOUTUBE_POST_TIMES = [time(12, 0), time(18, 30), time(21, 0)]  # Lunch + after work + evening
        self.FACEBOOK_POST_TIMES = [time(12, 30), time(19, 0)]
        self.INSTAGRAM_POST_TIMES = [time(12, 0), time(20, 0)]


@dataclass
class NicheConfig:
    # UPDATED: Topics matched to 35-54 male USA/UK interests
    # Key insight from analytics: "Baby Memory Lost" got 1.1K views
    # because 35-54 males are PARENTS — they care about memory, kids, aging
    TOPICS: List[str] = None
    SUB_NICHES: List[str] = None
    KEYWORDS: List[str] = None

    def __post_init__(self):
        self.TOPICS = [
            # Memory & Aging (HIGH RELEVANCE — this audience forgets names, keys, etc.)
            "why you forget names after 35",
            "why your memory gets worse after 40",
            "what causes brain fog in adults",
            "why you walk into a room and forget why",
            "how stress destroys your memory permanently",
            "why short term memory gets worse with age",
            "what actually causes memory loss after 40",
            "the real reason you can't focus anymore",

            # Sleep (MASSIVE pain point for 35-54 males)
            "why sleep gets worse after 35",
            "why you wake up at 3am every night",
            "what happens to your brain when you don't sleep",
            "why men sleep worse as they get older",
            "why you feel tired even after 8 hours sleep",
            "how poor sleep affects your brain after 40",
            "why you can't fall back asleep at night",

            # Stress & Work (Daily reality for this audience)
            "what chronic stress does to your brain",
            "why stress feels physical in your chest",
            "how work stress changes your personality over time",
            "why you feel mentally exhausted but can't sleep",
            "what cortisol does to your body every day",
            "why you feel anxious for no reason after 40",

            # Body Changes (Personal + age-relevant)
            "why men gain belly fat after 35",
            "what testosterone drop feels like after 40",
            "why your body recovers slower after 35",
            "why hangovers get worse with age explained",
            "what your heart does when you're stressed",
            "why your eyes get worse after 40",

            # Kids & Parenting (35-54 males are parents — Baby Memory Lost proved this)
            "what parents do that affects their kids brain",
            "why babies forget everything before age 3",
            "how stress affects children's brain development",
            "what screen time actually does to kids brains",

            # Mind & Psychology (Credible curiosity — not horror)
            "why your brain makes decisions before you do",
            "what happens in your brain when you make a decision",
            "why humans are wired to worry",
            "how your brain processes bad news differently",
            "why men struggle to ask for help science explained",
            "what loneliness does to the male brain",

            # Fascinating Science (Credible curiosity — shareable)
            "why time feels faster as you get older",
            "what your brain does while you drive on autopilot",
            "why some people never get tired",
            "how your gut affects your mood and brain",
            "why you get a gut feeling and it's actually science",
        ]

        self.SUB_NICHES = [
            "men's health after 40",
            "brain health and aging",
            "sleep science for adults",
            "stress and the male brain",
            "memory improvement",
            "parenting and child brain development",
            "work stress and burnout",
            "testosterone and aging",
        ]

        self.KEYWORDS = [
            "brain", "memory", "sleep", "stress", "after 40", "men's health",
            "aging", "focus", "cortisol", "testosterone", "brain fog",
            "science", "explained", "health facts", "neuroscience",
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

    @classmethod
    def validate(cls) -> Dict[str, bool]:
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

_key_status = API_KEYS.validate()
print(f"  🔑 API Status: {sum(_key_status.values())}/{len(_key_status)} configured")
if not _key_status['youtube']:
    print("  ⚠️ WARNING: YouTube credentials missing — upload will fail!")
if not _key_status['groq']:
    print("  ⚠️ WARNING: Groq API missing — content generation will fail!")
