"""
Content Generator - Production 2026
FIX (duration): the script used to be 4 hardcoded, mostly-static segments
totaling ~12-22s of voice no matter what topic was locked, so it could
never reach the channel's 35-55s target and barely referenced the actual
topic beyond one string substitution. This version asks Groq for a
topic-specific set of body segments and keeps adding/trimming segments
until the estimated spoken duration lands inside TARGET_DURATION range,
falling back to a rotating (still topic-aware) template bank if Groq is
unavailable or returns something unusable.
FIX: segment_duration added to each segment so clips match voice exactly.
"""

import os
import re
import json
import random
import logging
from typing import List, Dict, Optional

try:
    from core.hook_engine import HookEngine
except ImportError:
    class HookEngine:
        def __init__(self, api_key=None, use_cache=False): pass
        def generate(self, topic): raise RuntimeError("HookEngine unlinked.")

try:
    from config.settings import VIDEO_CONFIG
    TARGET_DURATION_MIN = float(getattr(VIDEO_CONFIG, 'DURATION_MIN', 35))
    TARGET_DURATION_MAX = float(getattr(VIDEO_CONFIG, 'DURATION_MAX', 55))
except ImportError:
    TARGET_DURATION_MIN = 35.0
    TARGET_DURATION_MAX = 55.0

logger = logging.getLogger(__name__)


def estimate_spoken_duration(text: str, wpm: float = 155.0) -> float:
    """Estimate how long Kokoro TTS will take to speak this text at speed=1.0"""
    word_count = len(text.split())
    raw_secs = (word_count / wpm) * 60.0
    return round(max(1.5, raw_secs + 0.25), 2)


# ============================================================
# FALLBACK BODY TEMPLATE BANK (used when Groq is unavailable/fails)
# Grouped by category so we can pull a fresh mix per topic instead of
# always returning the same two fixed strings.
# ============================================================
_FALLBACK_BODY_BANK: Dict[str, List[str]] = {
    "insight": [
        "This developmental shift activates neural pathways, sparking massive cognitive growth bursts in {topic_lower}.",
        "Every time this happens, your baby's brain fires thousands of new connections in seconds.",
        "Scientists say this exact moment shapes how your baby's brain wires itself for life.",
    ],
    "explanation": [
        "When experiencing {topic_lower}, their brain builds thousands of microscopic synapse connections every single second.",
        "This response starts in the brainstem, then spreads to regions controlling memory and emotion.",
        "Researchers tracked this pattern across thousands of babies and found it predicts later development.",
    ],
    "mechanism": [
        "The prefrontal cortex is still forming, so {topic_lower} triggers a much bigger reaction than in adults.",
        "Myelin is still coating these neural pathways, which is exactly why this response looks so intense.",
        "Hormones like cortisol and oxytocin spike together here, shaping how safe your baby feels.",
    ],
    "practical_tip": [
        "Pediatric researchers recommend staying calm and present, since babies mirror the emotional state around them.",
        "Experts suggest gentle, consistent responses here to help these neural pathways strengthen properly over time.",
        "Tracking small patterns like this can help parents spot healthy development milestones early.",
    ],
}

_VISUAL_PROMPTS = {
    "hook": "close up cinematic cute baby smiling curious slow motion high quality",
    "insight": "abstract glowing brain synapses firing neon macro depth of field cinematic",
    "explanation": "mother father tenderly holding newborn baby emotional bonding warm soft studio lighting",
    "mechanism": "macro shot baby brain development science visualization cinematic slow motion",
    "practical_tip": "parent gently soothing baby calm warm lighting close up cinematic",
    "cta": "minimalist clean motion graphic subscribe animation overlay",
}

_CTA_VARIANTS = [
    "Subscribe to unlock more baby brain science secrets.",
    "Follow for more science-backed baby development insights every week.",
    "Save this video, your future self will thank you.",
]


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

        # Reuse the same Groq client HookEngine already set up (avoids a
        # second client + a second key lookup for the body-script call).
        self.groq_client = getattr(self.hook_engine, "client", None)

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

    # ──────────────────────────────────────────
    # AI-GENERATED, TOPIC-SPECIFIC BODY SEGMENTS
    # ──────────────────────────────────────────
    def _ai_generate_body_segments(self, topic: str, target_words: int) -> List[Dict]:
        """Ask Groq for topic-specific body segments (not the hook/cta) sized
        to roughly target_words total. Returns [] on any failure so the
        caller can fall back to the template bank."""
        if not self.groq_client:
            return []
        try:
            prompt = (
                f"Write a short-form video script BODY (not the opening hook, not the "
                f"call-to-action) for a baby brain science / parenting channel. "
                f"Topic: \"{topic}\".\n"
                f"Return ONLY a JSON array of 3 to 5 objects, each with keys "
                f"\"type\" (one of: insight, explanation, mechanism, practical_tip) "
                f"and \"text\" (a single spoken sentence, 12-22 words, factual, "
                f"specific to this exact topic, no hashtags, no emojis). "
                f"Total words across all objects should be close to {target_words}. "
                f"Return ONLY the JSON array, nothing else."
            )
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=500,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.MULTILINE).strip()
            data = json.loads(raw)
            if not isinstance(data, list):
                return []

            segments = []
            for item in data:
                text = str(item.get("text", "")).strip()
                seg_type = str(item.get("type", "insight")).strip().lower()
                if seg_type not in _VISUAL_PROMPTS:
                    seg_type = "insight"
                if len(text.split()) < 4:
                    continue
                segments.append({
                    "type": seg_type,
                    "text": text,
                    "visual_prompt": _VISUAL_PROMPTS.get(seg_type, _VISUAL_PROMPTS["insight"]),
                })
            return segments
        except Exception as e:
            logger.warning(f"⚠️ AI body-script generation failed, using template fallback: {e}")
            return []

    def _fallback_body_segments(self, topic: str, target_words: int) -> List[Dict]:
        """Topic-aware fallback: pulls a fresh mix from each category and
        keeps adding until we're close to target_words, instead of always
        returning the same two fixed strings."""
        clean_topic = topic.lower()
        categories = list(_FALLBACK_BODY_BANK.keys())
        random.shuffle(categories)

        segments = []
        word_count = 0
        for cat in categories:
            choice = random.choice(_FALLBACK_BODY_BANK[cat])
            text = choice.format(topic_lower=clean_topic)
            segments.append({
                "type": cat,
                "text": text,
                "visual_prompt": _VISUAL_PROMPTS.get(cat, _VISUAL_PROMPTS["insight"]),
            })
            word_count += len(text.split())
            if word_count >= target_words:
                break

        # If still short (small bank / high target), cycle through again
        # picking different entries than what's already used where possible.
        attempts = 0
        while word_count < target_words and attempts < 6:
            cat = random.choice(categories)
            pool = [t for t in _FALLBACK_BODY_BANK[cat]
                    if t.format(topic_lower=clean_topic) not in [s["text"] for s in segments]]
            if not pool:
                attempts += 1
                continue
            text = random.choice(pool).format(topic_lower=clean_topic)
            segments.append({
                "type": cat,
                "text": text,
                "visual_prompt": _VISUAL_PROMPTS.get(cat, _VISUAL_PROMPTS["insight"]),
            })
            word_count += len(text.split())
            attempts += 1

        return segments

    def generate_script(self, topic: str) -> List[Dict]:
        hook_text = self.generate_hook(topic)
        cta_text = random.choice(_CTA_VARIANTS)

        # Words needed (at ~155 wpm) to land in the middle of the target
        # duration range, minus what the hook + cta already cover.
        mid_target_secs = (TARGET_DURATION_MIN + TARGET_DURATION_MAX) / 2.0
        hook_cta_secs = estimate_spoken_duration(hook_text) + estimate_spoken_duration(cta_text)
        remaining_secs = max(10.0, mid_target_secs - hook_cta_secs)
        target_body_words = int(remaining_secs * (155.0 / 60.0))

        body_segments = self._ai_generate_body_segments(topic, target_body_words)
        if not body_segments:
            body_segments = self._fallback_body_segments(topic, target_body_words)

        raw_segments = (
            [{"type": "hook", "text": hook_text, "visual_prompt": _VISUAL_PROMPTS["hook"]}]
            + body_segments
            + [{"type": "cta", "text": cta_text, "visual_prompt": _VISUAL_PROMPTS["cta"]}]
        )

        # Inject segment_duration so footage + assembler trim clips to voice length
        segments = []
        total = 0.0
        for i, seg in enumerate(raw_segments, start=1):
            dur = estimate_spoken_duration(seg["text"])
            total += dur
            segments.append({**seg, "segment_id": i, "segment_duration": dur, "is_pause": False})
            logger.info(f"📐 [{seg['type'].upper()}] {len(seg['text'].split())} words -> {dur:.1f}s clip")

        # Safety net: if we're still short of the minimum (e.g. AI + fallback
        # both returned thin content), pad with extra fallback segments
        # rather than shipping an under-length video.
        guard = 0
        while total < TARGET_DURATION_MIN and guard < 5:
            extra = self._fallback_body_segments(topic, int((TARGET_DURATION_MIN - total) * (155.0 / 60.0)))
            if not extra:
                break
            insert_at = len(segments) - 1  # keep CTA last
            for seg in extra:
                dur = estimate_spoken_duration(seg["text"])
                if total >= TARGET_DURATION_MAX:
                    break
                total += dur
                segments.insert(insert_at, {**seg, "segment_id": insert_at + 1,
                                             "segment_duration": dur, "is_pause": False})
                insert_at += 1
            guard += 1

        # Re-number segment_ids cleanly after any insertions
        for i, seg in enumerate(segments, start=1):
            seg["segment_id"] = i

        logger.info(
            f"📋 Generated {len(segments)} segments | "
            f"Total estimated voice: {total:.1f}s (target {TARGET_DURATION_MIN:.0f}-{TARGET_DURATION_MAX:.0f}s)"
        )
        return segments
