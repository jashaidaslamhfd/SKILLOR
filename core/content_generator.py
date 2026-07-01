"""
Content Generator - Production 2026
FIX: segment_duration added to each segment so clips match voice exactly.
"""

import os
import re
import random
import logging
from typing import List, Dict, Optional

try:
    from core.hook_engine import HookEngine
except ImportError:
    class HookEngine:
        def __init__(self, api_key=None, use_cache=False): pass
        def generate(self, topic): raise RuntimeError("HookEngine unlinked.")

logger = logging.getLogger(__name__)


def estimate_spoken_duration(text: str, wpm: float = 155.0) -> float:
    """Estimate how long Kokoro TTS will take to speak this text at speed=1.0"""
    word_count = len(text.split())
    raw_secs = (word_count / wpm) * 60.0
    return round(max(1.5, raw_secs + 0.25), 2)


class ContentGenerator:

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.hook_api_key = (
            self.config.get("hook_api_key")
            or os.getenv("HOOK_ENGINE_API_KEY")
            or os.getenv("GROQ_API_KEY")
        )
        try:
            self.hook_engine = HookEngine(api_key=self.hook_api_key, use_cache=True)
            logger.info("✅ HookEngine initialized successfully")
        except Exception as e:
            logger.error(f"❌ HookEngine init failed: {e}")
            self.hook_engine = None

    def generate_hook(self, topic: str) -> str:
        try:
            if self.hook_engine:
                raw = self.hook_engine.generate(topic)
                if raw and len(raw.strip()) > 5:
                    return raw.strip()
        except Exception as e:
            logger.warning(f"HookEngine failed, using local backup matrix: {e}")
        return self._fallback_hook(topic)

    def _fallback_hook(self, topic: str) -> str:
        clean = topic.lower().replace("infant ", "").replace("baby ", "").strip()
        hooks = [
            f"Your baby's brain does this during {clean}...",
            f"Nobody tells you this vital truth about {clean}.",
            f"This is secretly altering your baby's brain right now.",
            f"Why your newborn reacts to {clean} exactly like this...",
            f"The hidden neuroscience behind infant {clean} exposed."
        ]
        return random.choice(hooks)

    def generate_title(self, topic: str) -> str:
        return f"The Science of {topic.title()} 🧠"

    def generate_script(self, topic: str) -> List[Dict]:
        hook_text = self.generate_hook(topic)
        clean_topic = topic.lower()

        raw_segments = [
            {
                "segment_id": 1,
                "type": "hook",
                "text": hook_text,
                "visual_prompt": "close up cinematic cute baby smiling curious slow motion high quality",
                "is_pause": False
            },
            {
                "segment_id": 2,
                "type": "insight",
                "text": "This developmental shift activates neural pathways, sparking massive cognitive growth bursts.",
                "visual_prompt": "abstract glowing brain synapses firing neon macro depth of field cinematic",
                "is_pause": False
            },
            {
                "segment_id": 3,
                "type": "explanation",
                "text": f"When experiencing {clean_topic}, their brain builds thousands of microscopic synapse connections every single second.",
                "visual_prompt": "mother father tenderly holding newborn baby emotional bonding warm soft studio lighting",
                "is_pause": False
            },
            {
                "segment_id": 4,
                "type": "cta",
                "text": "Subscribe to unlock more baby brain science secrets.",
                "visual_prompt": "minimalist clean motion graphic subscribe animation overlay",
                "is_pause": False
            }
        ]

        # ✅ Inject segment_duration so footage + assembler trim clips to voice length
        segments = []
        total = 0
        for seg in raw_segments:
            dur = estimate_spoken_duration(seg["text"])
            total += dur
            segments.append({**seg, "segment_duration": dur})
            logger.info(f"📐 [{seg['type'].upper()}] {len(seg['text'].split())} words → {dur:.1f}s clip")

        logger.info(
            f"📋 Generated {len(segments)} segments | "
            f"Total estimated voice: {total:.1f}s"
        )
        return segments
