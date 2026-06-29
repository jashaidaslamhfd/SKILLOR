"""
Content Generator - FIXED VERSION (Production Safe)
Fixes:
- HookEngine API key injection bug
- Safe fallback mode
- No hard crash on missing env
"""

import os
import logging

from core.hook_engine import HookEngine

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates viral content safely with dependency injection fix"""

    def __init__(self, config=None):
        """
        FIX: API key is now safely injected OR loaded from env
        Prevents crash: HookEngine needs API key
        """

        self.config = config or {}

        # ===============================
        # FIX 1: SAFE API KEY LOADING
        # ===============================
        self.hook_api_key = (
            self.config.get("hook_api_key")
            or os.getenv("HOOK_ENGINE_API_KEY")
            or os.getenv("GROQ_API_KEY")  # fallback (optional)
        )

        # ===============================
        # FIX 2: SAFE HOOK ENGINE INIT
        # ===============================
        try:
            if not self.hook_api_key:
                logger.warning(
                    "⚠️ HookEngine running in FALLBACK MODE (no API key found)"
                )

            self.hook_engine = HookEngine(
                api_key=self.hook_api_key,
                use_cache=False
            )

            logger.info("✅ HookEngine initialized successfully")

        except Exception as e:
            logger.error(f"❌ HookEngine init failed: {e}")

            # ===============================
            # FIX 3: FAILSAFE MODE (NO CRASH)
            # ===============================
            self.hook_engine = None

    # ============================================================
    # HOOK GENERATION
    # ============================================================

    def generate_hook(self, topic: str) -> str:
        """Generate hook safely even if API fails"""

        try:
            if self.hook_engine:
                return self.hook_engine.generate(topic)

        except Exception as e:
            logger.warning(f"HookEngine failed, using fallback: {e}")

        # ===============================
        # FALLBACK HOOK SYSTEM
        # ===============================
        return self._fallback_hook(topic)

    def _fallback_hook(self, topic: str) -> str:
        """Local fallback hooks (NO API REQUIRED)"""

        fallback_hooks = [
            f"Your baby’s brain does this with {topic}…",
            f"Nobody tells you this about {topic}",
            f"This is happening in your baby right now",
            f"Your baby is secretly doing this every day",
            f"Why your baby reacts to {topic} like this",
        ]

        import random
        return random.choice(fallback_hooks)

    # ============================================================
    # OPTIONAL EXTENSIONS (safe)
    # ============================================================

    def generate_title(self, topic: str) -> str:
        """Safe title generator fallback"""

        return f"Your baby’s brain and {topic} 🧠"

    def generate_script(self, topic: str) -> str:
        """Basic safe script fallback"""

        return f"""
Hook: Your baby is experiencing {topic} right now...

Insight: This is part of natural brain development.

Explanation: Babies respond to {topic} in unique ways as their brain grows.

CTA: Follow for more baby brain science facts.
"""
