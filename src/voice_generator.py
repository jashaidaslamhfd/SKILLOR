import os
import numpy as np
import soundfile as sf
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from kokoro import KPipeline
    logger.info("Loading Kokoro TTS Model...")
    tts = KPipeline(lang_code='a')  # 'a' = American English
except ImportError as e:
    logger.error(f"Failed to import Kokoro: {e}")
    tts = None

SAMPLE_RATE = 24000  # Kokoro hamesha 24kHz audio deta hai
SILENCE_PAD_SEC = 0.15  # chhota sa gap har scene ke beech, taake voice cramped na lage


def _synthesize(text: str, voice: str, speed: float) -> np.ndarray:
    if not tts:
        raise RuntimeError("Kokoro TTS model not loaded. Check Kokoro installation.")
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    generator = tts(text, voice=voice, speed=speed)
    chunks = []
    for gs, ps, audio in generator:
        if audio is not None:
            chunks.append(audio)

    if not chunks:
        raise RuntimeError(f"Kokoro ne audio generate nahi kiya for: {text[:50]}...")

    full_audio = np.concatenate(chunks)
    if np.isnan(full_audio).any():
        full_audio = np.nan_to_num(full_audio, 0.0)

    max_val = np.abs(full_audio).max()
    if max_val > 1.0:
        full_audio = full_audio / max_val * 0.95

    return full_audio


def generate_voice(text: str, voice: str = "am_michael", output_path: str = "output/voice.wav", speed: float = 1.0) -> str:
    """Original single-file API - kept for backward compatibility (thumbnail/
    description generation, or any place still expecting one full voiceover file)."""
    try:
        logger.info(f"Generating full voiceover with: {voice}...")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        audio = _synthesize(text, voice, speed)
        sf.write(output_path, audio, SAMPLE_RATE)
        logger.info(f"Voice saved: {output_path} ({len(audio)} samples, {len(audio)/SAMPLE_RATE:.2f}s)")
        return output_path
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise RuntimeError(f"Voice generation error: {e}")


def generate_voice_segments(
    scenes: List[dict],
    voice: str = "am_michael",
    output_dir: str = "output/segments",
    speed: float = 1.0,
) -> List[Dict]:
    """
    Generates ONE audio file PER SCENE caption. This is what makes voice +
    caption + clip line up exactly: each image/Ken-Burns clip is shown for
    precisely the duration of the audio that speaks its own caption - no
    guessing, no even-splitting of total duration.

    Returns: [{"path": "...", "duration": float, "caption": str}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    segments = []

    for i, scene in enumerate(scenes):
        caption = scene.get('caption', '').strip() if isinstance(scene, dict) else str(scene)
        if not caption:
            caption = " "

        try:
            audio = _synthesize(caption, voice, speed)
        except Exception as e:
            logger.error(f"Segment {i+1} TTS failed: {e} - inserting short silence instead")
            audio = np.zeros(int(SAMPLE_RATE * 1.5), dtype=np.float32)

        path = os.path.join(output_dir, f"seg_{i}.wav")
        sf.write(path, audio, SAMPLE_RATE)
        duration = len(audio) / SAMPLE_RATE

        segments.append({"path": path, "duration": duration, "caption": caption})
        logger.info(f"Segment {i+1}/{len(scenes)}: {duration:.2f}s - \"{caption[:50]}...\"")

    total = sum(s['duration'] for s in segments)
    logger.info(f"Total voiceover duration across {len(segments)} segments: {total:.2f}s")
    return segments
