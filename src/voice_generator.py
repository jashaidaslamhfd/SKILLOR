import os
import numpy as np
import soundfile as sf
import logging
import re
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from kokoro import KPipeline
    logger.info("Loading Kokoro TTS Model...")
    tts = KPipeline(lang_code='a') # 'a' = American English
except ImportError as e:
    logger.error(f"Failed to import Kokoro: {e}")
    tts = None

SAMPLE_RATE = 24000
SILENCE_PAD_SEC = 0.25 # Badha diya 0.15 se 0.25. Dar ke liye pause zyada

def add_mystery_pauses(text: str) -> str:
    """Add <break> tags after dark hooks for retention"""
    # "you too?" ke baad pause
    text = re.sub(r'you too\?', 'you too? <break time="0.5s"/>', text, flags=re.IGNORECASE)
    # "..." ke baad pause
    text = re.sub(r'\.\.', '... <break time="0.3s"/>', text)
    # "right now" ke baad pause
    text = re.sub(r'right now\.', 'right now. <break time="0.4s"/>', text, flags=re.IGNORECASE)
    return text

def _synthesize(text: str, voice: str, speed: float) -> np.ndarray:
    if not tts:
        raise RuntimeError("Kokoro TTS model not loaded. Check Kokoro installation.")
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # NEW: Add mystery pauses before TTS
    text = add_mystery_pauses(text)

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

def generate_voice(text: str, voice: str = "am_adam", output_path: str = "output/voice.wav", speed: float = 0.95) -> str:
    """USA Dark Science Voice: Deep, Slow, Mysterious"""
    try:
        logger.info(f"Generating DARK voiceover with: {voice} at speed {speed}...")
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
    voice: str = "am_adam", # CHANGE 1: am_michael se am_adam
    output_dir: str = "output/segments",
    speed: float = 0.95, # CHANGE 2: 1.0 se 0.95. Thora slow
) -> List[Dict]:
    """
    Each scene gets its own audio with mystery pauses
    """
    os.makedirs(output_dir, exist_ok=True)
    segments = []

    for i, scene in enumerate(scenes):
        caption = scene.get('caption', '').strip() if isinstance(scene, dict) else str(scene)
        if not caption:
            caption = " "

        try:
            audio = _synthesize(caption, voice, speed) # Pauses auto add ho jaenge
        except Exception as e:
            logger.error(f"Segment {i+1} TTS failed: {e} - inserting short silence instead")
            audio = np.zeros(int(SAMPLE_RATE * 1.5), dtype=np.float32)

        path = os.path.join(output_dir, f"seg_{i}.wav")
        sf.write(path, audio, SAMPLE_RATE)
        duration = len(audio) / SAMPLE_RATE

        segments.append({"path": path, "duration": duration, "caption": caption})
        logger.info(f"Segment {i+1}/{len(scenes)}: {duration:.2f}s - \"{caption[:50]}...\"")

    total = sum(s['duration'] for s in segments)
    logger.info(f"Total DARK voiceover duration: {total:.2f}s")
    return segments
