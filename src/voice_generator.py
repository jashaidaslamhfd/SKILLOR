import os
import numpy as np
import soundfile as sf
import logging
from typing import Optional

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

def generate_voice(
    text: str, 
    voice: str = "am_michael", 
    output_path: str = "output/voice.wav"
) -> str:
    """
    Generate voice from text using Kokoro TTS with error handling.
    """
    if not tts:
        raise RuntimeError("Kokoro TTS model not loaded. Check Kokoro installation.")
    
    if not text or len(text.strip()) == 0:
        raise ValueError("Text cannot be empty")
    
    try:
        logger.info(f"Generating Voice with: {voice}...")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Generate audio with timeout handling
        generator = tts(text, voice=voice, speed=1.0)

        audio_chunks = []
        chunk_count = 0
        
        for gs, ps, audio in generator:
            if audio is not None:
                audio_chunks.append(audio)
                chunk_count += 1

        if not audio_chunks:
            raise RuntimeError("Kokoro ne koi audio generate nahi kiya - text check karo")

        logger.info(f"Generated {chunk_count} audio chunks")
        
        # Concatenate chunks safely
        full_audio = np.concatenate(audio_chunks)
        
        # Validate audio
        if len(full_audio) == 0:
            raise RuntimeError("Generated audio is empty")
        
        if np.isnan(full_audio).any():
            logger.warning("Audio contains NaN values, replacing with zeros")
            full_audio = np.nan_to_num(full_audio, 0.0)
        
        # Normalize audio to prevent clipping
        max_val = np.abs(full_audio).max()
        if max_val > 1.0:
            logger.warning(f"Audio peak {max_val} exceeds 1.0, normalizing...")
            full_audio = full_audio / max_val * 0.95
        
        # Save audio
        sf.write(output_path, full_audio, SAMPLE_RATE)
        logger.info(f"Voice Saved: {output_path} ({len(audio_chunks)} chunks, {len(full_audio)} samples)")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise RuntimeError(f"Voice generation error: {e}")
