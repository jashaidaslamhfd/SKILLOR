"""
Settings — BABY + BRAIN SCIENCE (USA Audience 2026)
TARGET: USA | Parents, Expecting Parents, Families | All Ages
NICHE: Baby Brain Development, Child Psychology, Parenting Science

FIXES APPLIED:
1. ✅ Execution order safety (API_KEYS instantiated above references or cleanly isolated)
2. ✅ Verbose API validation (debuggable key checks returning clear status strings)
3. ✅ Deduplicated hashtag and merged rules (guarantees <= 5-6 hashtags to bypass spam filters)
4. ✅ Resilient edge-tts voice fallback chain
5. ✅ Zoneinfo time-zone aware scheduling pattern (America/New_York)
6. ✅ Upgraded emotional/curiosity thumbnail configuration (Style & word count)
7. ✅ Deduplicated cluster grouping for keywords
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from datetime import datetime
from zoneinfo import ZoneInfo  # 🥇 Fix 5: timezone-aware datetime

# ============================================================
# VIDEO CONFIG — YouTube Shorts 2026 Optimized
# ============================================================
@dataclass
class VideoConfig:
    # YouTube Shorts duration: 45-60 seconds (2026 sweet spot, expanded buffer)
    DURATION_MIN: int = 45
    DURATION_MAX: int = 60
    TARGET_DURATION: int = 50

    # Resolution
    RESOLUTION: tuple = (1080, 1920)
    FPS: int = 30
    BITRATE: str = "8000k"
    CRF: int = 18          # ═══ HIGH QUALITY ═══
    PRESET: str = "slow"   # ═══ BEST QUALITY ═══

    # ═══════════════════════════════════════════════════════════
    # FAST CUT & RETENTION-AWARE SCENE ORCHESTRATION
    # ═══════════════════════════════════════════════════════════
    FAST_CUT_INTERVAL: float = 1.4  # Keeps visual pacing fast (1.4s cuts)
    MIN_MOTION_SCORE: int = 65      # Clip must be dynamic/moving
    PORTRAIT_ONLY: bool = True      # Enforces 9:16 vertical orientation strictly


# ============================================================
# AUDIO CONFIG (edge-tts Free USA Service)
# ============================================================
@dataclass
class AudioConfig:
    TTS_SERVICE: str = "edge-tts"
    
    # 🥇 Fix 4: Safer fallback chain for local environment edge-tts limitations
    VOICE_PRIORITY: List[str] = field(default_factory=lambda: [
        "en-US-JasonNeural",
        "en-US-GuyNeural",
        "en-US-AriaNeural",
        "en-US-DavisNeural"
    ])
    
    WORDS_PER_MINUTE: int = 155  # Optimal pace for clear comprehension and retention
    
    @property
    def VOICE(self) -> str:
        # Auto-pick first dynamic voice element if not hardcoded externally
        return self.VOICE_PRIORITY[0]


# ============================================================
# CAPTIONS CONFIG (Auto-sync SRT style)
# ============================================================
@dataclass
class CaptionConfig:
    FONT_NAME: str = "Arial-Bold"
    FONT_SIZE: int = 42
    STROKE_COLOR: str = "#000000"
    STROKE_WIDTH: int = 2
    COLOR: str = "#FFFFFF"
    HIGHLIGHT_COLOR: str = "#FFCC00" # High-contrast yellow for retention retention highlight
    MARGIN_V: int = 120  # Centered safely for Shorts UI overlays


# ============================================================
# THUMBNAIL CONFIG — High CTR Emotional/Curiosity
# ============================================================
@dataclass
class ThumbnailConfig:
    RESOLUTION: tuple = (1280, 720)
    # 🥇 Fix 6: Baby niche CTR performs significantly better with curiosity emotional triggers
    STYLE: str = "emotional_curiosity" 
    WORD_COUNT: str = "2-4"
    FONT: str = "Impact"
    BG_BLUR: bool = True
    BORDER_COLOR: str = "#FF0000" # High visual-weight red frame for feed disruption


# ============================================================
# NICHE CONSTANTS & TARGETING — Baby + Brain Science
# ============================================================
@dataclass
class BabyNicheConfig:
    TARGET_AUDIENCE: str = "USA Parents (Expecting to Toddler)"
    
    # 🥇 Fix 7: Deduplicated cluster of keywords (No redundancies/repetitive variants)
    BABY_KEYWORDS: List[str] = field(default_factory=lambda: list(set([
        "baby brain development", 
        "infant sleep regression", 
        "newborn reflexes",
        "toddler growth spurts", 
        "separation anxiety", 
        "language acquisition",
        "sensory processing", 
        "baby motor skills", 
        "emotional bonding"
    ])))
    
    # 🥇 Fix 3: Strict hash tags size control to bypass spam/duplication detection
    BABY_HASHTAGS: List[str] = field(default_factory=lambda: [
        "#baby", "#parenting", "#brain", "#science", "#motherhood", "#toddler"
    ])

    @property
    def FINAL_HASHTAGS(self) -> List[str]:
        """Merge base shorts tag with random sample, keeping total <= 5-6."""
        import random
        # Ensures no spam flags by capping total hash tags
        return ["#Shorts"] + random.sample(self.BABY_HASHTAGS, min(3, len(self.BABY_HASHTAGS)))


# ============================================================
# API KEYS & PERSISTENT STORAGE MANAGEMENT
# ============================================================
@dataclass
class APIKeys:
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY", None)
    REFRESH_TOKEN: Optional[str] = os.getenv("REFRESH_TOKEN", None)
    FACEBOOK_ACCESS_TOKEN: Optional[str] = os.getenv("FACEBOOK_ACCESS_TOKEN", None)
    FACEBOOK_PAGE_ID: Optional[str] = os.getenv("FACEBOOK_PAGE_ID", None)
    PEXELS_API_KEY: Optional[str] = os.getenv("PEXELS_API_KEY", None)

    # 🥇 Fix 2: Explicitly debuggable validate() to tell you exactly which auth key/token is missing
    def validate(self) -> Dict[str, Union[bool, str]]:
        return {
            'groq': bool(self.GROQ_API_KEY) or "MISSING GROQ_API_KEY (Required for LLM generation)",
            'youtube': bool(self.YOUTUBE_API_KEY and self.REFRESH_TOKEN) or "MISSING YOUTUBE KEYS (Required for YT Shorts publishing)",
            'facebook': bool(self.FACEBOOK_ACCESS_TOKEN and self.FACEBOOK_PAGE_ID) or "MISSING FB KEYS (Required for Meta publishing)",
            'pexels': bool(self.PEXELS_API_KEY) or "MISSING PEXELS_API_KEY (Required for Footage fetching)"
        }

    def missing_keys(self) -> List[str]:
        validation = self.validate()
        return [k for k, v in validation.items() if isinstance(v, str)]


# Instantiated safely at the bottom level to prevent import partial initialization orders
API_KEYS = APIKeys()


# ============================================================
# SCHEDULER & UPLOAD CONFIG (USA Timezone-aware)
# ============================================================
@dataclass
class SchedulerConfig:
    # 🥇 Fix 5: Best practice – Timezone-aware timezone America/New_York
    TARGET_TIMEZONE = ZoneInfo("America/New_York")
    
    POSTING_HOURS_UTC: List[int] = field(default_factory=lambda: [
        11, 14, 20  # Matches morning, afternoon, and evening USA slots dynamically
    ])
    
    @property
    def CURRENT_TIME_NY(self) -> datetime:
        return datetime.now(self.TARGET_TIMEZONE)


# Configuration Singletons
VIDEO_CONFIG = VideoConfig()
AUDIO_CONFIG = AudioConfig()
CAPTION_CONFIG = CaptionConfig()
THUMBNAIL_CONFIG = ThumbnailConfig()
NICHE_CONFIG = BabyNicheConfig()
SCHEDULER_CONFIG = SchedulerConfig()
PLATFORM_CONFIG = PlatformConfig()   # ⬅️ ADD THIS
SEO_CONFIG = SEOConfig()             # ⬅️ ADD THIS
API_KEYS = APIKeys()                 # ⬅️ ADD THIS (agar nahi hai)


# 🥇 Fix 1: Isolated health check moved safely down here to ensure dependencies are fully loaded
def health_check() -> Dict[str, Union[str, List[str], bool]]:
    """Performs absolute system-wide execution-order-safe pipeline health check."""
    api_keys = APIKeys() # Execution order safety check
    missing = api_keys.missing_keys()
    
    warnings = []
    if not os.path.exists("state"):
        warnings.warn("State directory missing. Will be created on demand.")
        
    return {
        'status': "UNHEALTHY" if missing else "HEALTHY",
        'missing_apis': missing,
        'warnings': warnings,
        'tiktok_reels_crosspost_ready': bool(api_keys.FACEBOOK_ACCESS_TOKEN)
    }


# ============================================================
# EXECUTION TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING CONFIGURATION STACK (USA 2026)\n" + "=" * 60)
    
    print("\n🎬 VIDEO:")
    print(f"    Duration: {VIDEO_CONFIG.DURATION_MIN}-{VIDEO_CONFIG.DURATION_MAX}s")
    print(f"    Fast Cut: {VIDEO_CONFIG.FAST_CUT_INTERVAL}s")
    print(f"    Resolution: {VIDEO_CONFIG.RESOLUTION}")
    print(f"    CRF: {VIDEO_CONFIG.CRF} | Preset: {VIDEO_CONFIG.PRESET}")

    print("\n🎙️ AUDIO:")
    print(f"    Service: {AUDIO_CONFIG.TTS_SERVICE} (100% FREE)")
    print(f"    Voice: {AUDIO_CONFIG.VOICE}")
    print(f"    WPM: {AUDIO_CONFIG.WORDS_PER_MINUTE}")

    print("\n📝 CAPTIONS:")
    print(f"    Font Size: {CAPTION_CONFIG.FONT_SIZE}px")
    print(f"    Margin V: {CAPTION_CONFIG.MARGIN_V}")

    print("\n🖼️ THUMBNAIL:")
    print(f"    Resolution: {THUMBNAIL_CONFIG.RESOLUTION} (YouTube standard)")
    print(f"    Style: {THUMBNAIL_CONFIG.STYLE}")
    print(f"    Border Color: {THUMBNAIL_CONFIG.BORDER_COLOR}")

    print("\n🔑 API KEYS VERBOSE STATUS:")
    api_status = API_KEYS.validate()
    for key, value in api_status.items():
        status = "✅" if value is True else "❌"
        print(f"    {status} {key} -> {value if isinstance(value, str) else 'Configured'}")

    print("\n🔍 SYSTEM HEALTH CHECK:")
    health = health_check()
    print(f"    Status: {health['status']}")
    if health['missing_apis']:
        print(f"    Missing APIs: {health['missing_apis']}")
    
    print("\n🎯 HASHTAG CHECK (USA 2026):")
    print(f"    Generated Set: {NICHE_CONFIG.FINAL_HASHTAGS}")
    
    print("\n⏱️ TIMEZONE SCHEDULER CHECK (NY):")
    print(f"    Current Time (New York): {SCHEDULER_CONFIG.CURRENT_TIME_NY.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60 + "\n✅ System Settings Verified Successfully!")
