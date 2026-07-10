"""
Voice Generator Module for SKILLOR Pipeline
OPTIMIZED FOR: Dark Mystery Tone + Emotional Delivery + High Retention
PRIMARY: Chatterbox (Expressive TTS) | FALLBACK: Kokoro (Reliable TTS)

UPDATES:
1. Soft-limiter (tanh compression) for radio-quality audio
2. Segment padding for seamless flow
3. Dynamic exaggeration based on scene metadata
4. Voice cloning support
"""

import os
import numpy as np
import soundfile as sf
import logging
import re
import time
from typing import List, Dict, Optional, Tuple

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONSTANTS
# ============================================
TARGET_RMS = 0.11
SILENCE_PAD_SEC = 0.25  # Padding between segments for smooth flow
KOKORO_SAMPLE_RATE = 24000
DEFAULT_VOICE = "am_adam"
DEFAULT_SPEED = 0.95

# Soft-limiter constants
SOFT_LIMITER_THRESHOLD = 0.95
SOFT_LIMITER_GAIN = 1.2  # Slight boost before limiting

# ============================================
# 1. CHATTERBOX TTS (Primary Engine)
# ============================================
# Chatterbox: Resemble AI (MIT license) - expressive TTS with emotion control
# Parameters tuned for dark/mystery body-science tone:
# - exaggeration=0.7: Dramatic/tense delivery (0.5 is neutral)
# - cfg_weight=0.35: Slows down pacing for ominous read
# - temperature=0.8: Natural variation in delivery

CHATTERBOX_EXAGGERATION_BASE = 0.7
CHATTERBOX_CFG_WEIGHT = 0.35
CHATTERBOX_TEMPERATURE = 0.8
VOICE_REFERENCE_PATH = "assets/voice_reference.wav"

_chatterbox_model = None
_chatterbox_load_failed = False


def _get_chatterbox():
    """
    Lazy-loads Chatterbox TTS model on first use.
    Returns None if loading fails - every segment falls back to Kokoro.
    """
    global _chatterbox_model, _chatterbox_load_failed
    
    if _chatterbox_model is not None or _chatterbox_load_failed:
        return _chatterbox_model
    
    try:
        import torch
        from chatterbox.tts import ChatterboxTTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Chatterbox TTS model on {device} (first call only, then cached)...")
        
        _chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info("✅ Chatterbox loaded successfully.")
        
    except ImportError:
        logger.warning("Chatterbox not installed - falling back to Kokoro only")
        _chatterbox_load_failed = True
        _chatterbox_model = None
        
    except Exception as e:
        logger.error(f"Chatterbox unavailable ({e}) - falling back to Kokoro")
        _chatterbox_load_failed = True
        _chatterbox_model = None
    
    return _chatterbox_model


def _get_dynamic_exaggeration(text: str, scene_index: int, total_scenes: int) -> float:
    """
    Dynamic exaggeration based on scene position and content.
    
    - Hook scenes (first 2): Higher exaggeration for impact
    - Climax scenes (middle): Moderate exaggeration
    - Resolution scenes (last 2): Lower exaggeration for calm
    - Content keywords: Adjust based on emotional intensity
    """
    base = CHATTERBOX_EXAGGERATION_BASE
    
    # Position-based adjustment
    if scene_index < 2:  # Hook scenes
        base += 0.15
    elif scene_index > total_scenes - 3:  # Resolution scenes
        base -= 0.1
    
    # Content-based adjustment
    intense_keywords = ['secret', 'truth', 'shock', 'dark', 'hidden', 'never', 'always']
    if any(keyword in text.lower() for keyword in intense_keywords):
        base += 0.1
    
    calm_keywords = ['relax', 'calm', 'peace', 'heal', 'rest']
    if any(keyword in text.lower() for keyword in calm_keywords):
        base -= 0.1
    
    # Clamp to safe range
    return max(0.3, min(1.2, base))


def _synthesize_chatterbox(text: str, scene_index: int = 0, total_scenes: int = 1) -> Tuple[np.ndarray, int]:
    """
    Synthesize audio using Chatterbox with dynamic exaggeration.
    Returns (audio: np.ndarray float32, sample_rate: int)
    """
    model = _get_chatterbox()
    if model is None:
        raise RuntimeError("Chatterbox model not loaded")

    # Get dynamic exaggeration
    exaggeration = _get_dynamic_exaggeration(text, scene_index, total_scenes)
    
    kwargs = {
        "exaggeration": exaggeration,
        "cfg_weight": CHATTERBOX_CFG_WEIGHT,
        "temperature": CHATTERBOX_TEMPERATURE,
    }
    
    # Use voice reference if available
    if os.path.exists(VOICE_REFERENCE_PATH):
        kwargs["audio_prompt_path"] = VOICE_REFERENCE_PATH
        logger.debug(f"Using voice reference: {VOICE_REFERENCE_PATH}")

    # Generate audio
    wav = model.generate(text, **kwargs)
    audio = wav.squeeze().detach().cpu().numpy().astype(np.float32)

    # Clean up
    if np.isnan(audio).any():
        audio = np.nan_to_num(audio, 0.0)
    
    return audio, model.sr


# ============================================
# 2. KOKORO TTS (Fallback Engine)
# ============================================
_kokoro_tts = None

try:
    from kokoro import KPipeline
    logger.info("Loading Kokoro TTS model (fallback engine)...")
    _kokoro_tts = KPipeline(lang_code='a')  # 'a' = American English
    logger.info("✅ Kokoro loaded successfully.")
except ImportError:
    logger.warning("Kokoro not installed - will use silence fallback")
    _kokoro_tts = None
except Exception as e:
    logger.error(f"Kokoro loading failed: {e}")
    _kokoro_tts = None


def _synthesize_kokoro(text: str, voice: str = "am_adam", speed: float = 0.95) -> Tuple[np.ndarray, int]:
    """
    Synthesize audio using Kokoro (fallback).
    Returns (audio: np.ndarray float32, sample_rate: int)
    """
    if not _kokoro_tts:
        raise RuntimeError("Kokoro TTS model not loaded. Check Kokoro installation.")

    generator = _kokoro_tts(text, voice=voice, speed=speed)
    chunks = []
    
    for gs, ps, audio in generator:
        if audio is not None:
            chunks.append(audio)

    if not chunks:
        raise RuntimeError(f"Kokoro generated no audio for: {text[:50]}...")

    full_audio = np.concatenate(chunks)
    
    # Clean up
    if np.isnan(full_audio).any():
        full_audio = np.nan_to_num(full_audio, 0.0)

    return full_audio, KOKORO_SAMPLE_RATE


# ============================================
# 3. AUDIO PROCESSING UTILITIES (OPTIMIZED)
# ============================================

def _apply_soft_limiter(audio: np.ndarray, threshold: float = SOFT_LIMITER_THRESHOLD) -> np.ndarray:
    """
    Applies soft-clipping using tanh compression.
    Produces "radio-quality" audio with smoother peaks.
    """
    if audio.size == 0:
        return audio
    
    # Apply tanh soft-clipping for smoother peaks
    # tanh(x * 1.5) / 1.5 creates a soft compression curve
    compressed = np.tanh(audio * SOFT_LIMITER_GAIN) / SOFT_LIMITER_GAIN
    
    # Ensure we don't exceed the threshold
    peak = np.abs(compressed).max()
    if peak > threshold:
        compressed = compressed / peak * threshold
    
    return compressed.astype(np.float32)


def _normalize_loudness(
    audio: np.ndarray, 
    target_rms: float = TARGET_RMS,
    apply_soft_limit: bool = True
) -> np.ndarray:
    """
    Normalizes audio to consistent perceived loudness (RMS).
    Applies soft-limiter for radio-quality audio.
    
    Args:
        audio: Input audio array
        target_rms: Target RMS level
        apply_soft_limit: Whether to apply soft-limiter
    
    Returns:
        Normalized audio array
    """
    if audio.size == 0:
        return audio
    
    # Calculate RMS
    rms = float(np.sqrt(np.mean(np.square(audio))))
    
    if rms < 1e-6:
        # Near silence - return as-is
        return audio
    
    # Apply gain to reach target RMS
    gain = target_rms / rms
    normalized = audio * gain
    
    # Apply soft-limiter for radio-quality audio
    if apply_soft_limit:
        normalized = _apply_soft_limiter(normalized)
    
    # Hard peak ceiling (safety net)
    peak = np.abs(normalized).max()
    if peak > 0.95:
        normalized = normalized / peak * 0.95
    
    return normalized.astype(np.float32)


def _add_padding(audio: np.ndarray, sr: int, padding_sec: float = SILENCE_PAD_SEC) -> np.ndarray:
    """
    Adds silence padding at start and end for seamless flow.
    """
    if padding_sec <= 0:
        return audio
    
    pad_samples = int(sr * padding_sec)
    padding = np.zeros(pad_samples, dtype=np.float32)
    
    return np.concatenate([padding, audio, padding])


def add_mystery_pauses(text: str) -> str:
    """
    Adds suspenseful pauses for retention.
    Uses punctuation (ellipsis, commas) instead of SSML tags.
    """
    # "you too?" -> trailing pause via ellipsis
    text = re.sub(r'you too\?', 'you too?..', text, flags=re.IGNORECASE)
    
    # ".." -> stretch into a longer natural pause
    text = re.sub(r'(?<!\.)\.\.(?!\.)', '...', text)
    
    # "right now." -> comma-separated beat before continuing
    text = re.sub(r'right now\.', 'right now...', text, flags=re.IGNORECASE)
    
    # Add pauses after cliffhangers
    text = re.sub(r'(\?!)', '?!..', text)
    text = re.sub(r'(!)', '!..', text)
    
    return text


def _synthesize(
    text: str, 
    voice: str = "am_adam", 
    speed: float = 0.95,
    scene_index: int = 0,
    total_scenes: int = 1
) -> Tuple[np.ndarray, int, str]:
    """
    Synthesize audio with Chatterbox (primary) and Kokoro (fallback).
    Returns: (audio, sample_rate, engine_used)
    """
    if not text or not text.strip():
        logger.warning("Empty text received - generating silence")
        audio = np.zeros(int(KOKORO_SAMPLE_RATE * 1.0), dtype=np.float32)
        return audio, KOKORO_SAMPLE_RATE, "silence"

    # Add suspenseful pauses
    text_with_pauses = add_mystery_pauses(text)

    # Try Chatterbox first
    try:
        audio, sr = _synthesize_chatterbox(text_with_pauses, scene_index, total_scenes)
        audio = _normalize_loudness(audio)
        return audio, sr, "chatterbox"
    except Exception as e:
        logger.warning(f"Chatterbox failed ({e}) - falling back to Kokoro")

    # Try Kokoro as fallback
    try:
        audio, sr = _synthesize_kokoro(text_with_pauses, voice, speed)
        audio = _normalize_loudness(audio)
        return audio, sr, "kokoro"
    except Exception as e:
        logger.error(f"Kokoro also failed ({e}) - generating silence")

    # Ultimate fallback: silence
    audio = np.zeros(int(KOKORO_SAMPLE_RATE * 1.5), dtype=np.float32)
    return audio, KOKORO_SAMPLE_RATE, "silence"


# ============================================
# 4. MAIN GENERATION FUNCTIONS
# ============================================

def generate_voice(
    text: str, 
    voice: str = "am_adam", 
    output_path: str = "output/voice.wav", 
    speed: float = 0.95,
    add_padding: bool = True
) -> str:
    """
    Generate a single voiceover file.
    Primary: Chatterbox (expressive) | Fallback: Kokoro (reliable)
    
    Args:
        text: Text to synthesize
        voice: Voice to use (Kokoro fallback only)
        output_path: Output file path
        speed: Speech speed (Kokoro fallback only)
        add_padding: Whether to add silence padding
    """
    try:
        logger.info(f"Generating voiceover (voice='{voice}', speed={speed})...")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        audio, sr, engine = _synthesize(text, voice, speed)
        
        # Add padding for smooth flow
        if add_padding:
            audio = _add_padding(audio, sr)
        
        # Final normalization after padding
        audio = _normalize_loudness(audio)
        
        sf.write(output_path, audio, sr)
        
        duration = len(audio) / sr
        logger.info(f"✅ Voice saved via {engine}: {output_path} ({duration:.2f}s)")
        return output_path
        
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise RuntimeError(f"Voice generation error: {e}")


def generate_voice_segments(
    scenes: List[Dict],
    voice: str = "am_adam",
    output_dir: str = "output/segments",
    speed: float = 0.95,
    min_duration: float = 0.6,
    add_padding: bool = True,
) -> List[Dict]:
    """
    Generate voiceover for each scene with metadata.
    
    Features:
    - Dynamic exaggeration based on scene position
    - Padding for seamless flow
    - Loudness normalization
    - Soft-limiter for radio-quality audio
    
    Args:
        scenes: List of scene dicts with 'caption' field
        voice: Voice to use (Kokoro fallback only)
        output_dir: Directory to save audio files
        speed: Speed for Kokoro fallback
        min_duration: Minimum duration for any segment
        add_padding: Whether to add silence padding
    
    Returns:
        List of segment dicts with path, duration, caption, engine
    """
    os.makedirs(output_dir, exist_ok=True)
    segments = []
    engine_counts = {}
    total_scenes = len(scenes)
    
    logger.info(f"Generating {total_scenes} voice segments...")
    
    for i, scene in enumerate(scenes):
        caption = scene.get('caption', '').strip() if isinstance(scene, dict) else str(scene)
        
        if not caption:
            logger.warning(f"Scene {i+1} has empty caption - using placeholder")
            caption = " "
        
        try:
            # Pass scene index for dynamic exaggeration
            audio, sr, engine = _synthesize(caption, voice, speed, i, total_scenes)
        except Exception as e:
            logger.error(f"Segment {i+1} TTS failed: {e}")
            audio = np.zeros(int(KOKORO_SAMPLE_RATE * 1.0), dtype=np.float32)
            sr = KOKORO_SAMPLE_RATE
            engine = "silence"
        
        # Apply padding for seamless flow
        if add_padding:
            audio = _add_padding(audio, sr)
        
        # Normalize loudness with soft-limiter
        audio = _normalize_loudness(audio, apply_soft_limit=True)
        
        # Ensure minimum duration
        duration = len(audio) / sr
        if duration < min_duration:
            pad_samples = int((min_duration - duration) * sr)
            audio = np.concatenate([audio, np.zeros(pad_samples, dtype=np.float32)])
            duration = min_duration
        
        # Save audio file
        path = os.path.join(output_dir, f"seg_{i:03d}.wav")
        sf.write(path, audio, sr)
        
        # Track engine usage
        engine_counts[engine] = engine_counts.get(engine, 0) + 1
        
        segment = {
            "path": path,
            "duration": duration,
            "caption": caption,
            "tts_engine": engine,
            "sample_rate": sr,
            "scene_index": i,
            "has_padding": add_padding
        }
        segments.append(segment)
        
        # Log progress
        logger.info(
            f"Segment {i+1}/{total_scenes} via {engine}: "
            f"{duration:.2f}s - \"{caption[:50]}{'...' if len(caption) > 50 else ''}\""
        )
    
    # Summary
    total_duration = sum(s['duration'] for s in segments)
    logger.info(
        f"✅ Generated {len(segments)} segments | "
        f"Total: {total_duration:.2f}s | Engines: {engine_counts}"
    )
    
    return segments


def generate_batch_voices(
    texts: List[str],
    voice: str = "am_adam",
    output_dir: str = "output/voices",
    speed: float = 0.95,
) -> List[str]:
    """
    Generate voiceovers for multiple texts in batch.
    
    Args:
        texts: List of text strings
        voice: Voice to use
        output_dir: Output directory
        speed: Speech speed
    
    Returns:
        List of output file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    
    for i, text in enumerate(texts):
        path = os.path.join(output_dir, f"voice_{i:03d}.wav")
        try:
            generate_voice(text, voice, path, speed)
            paths.append(path)
        except Exception as e:
            logger.error(f"Batch voice {i} failed: {e}")
            paths.append(None)
    
    successful = sum(1 for p in paths if p)
    logger.info(f"Batch generation: {successful}/{len(texts)} successful")
    
    return paths


# ============================================
# 5. AUDIO ANALYSIS UTILITIES
# ============================================

def get_audio_duration(file_path: str) -> float:
    """Get duration of audio file in seconds."""
    try:
        info = sf.info(file_path)
        return info.duration
    except Exception as e:
        logger.error(f"Failed to get duration for {file_path}: {e}")
        return 0.0


def get_audio_info(file_path: str) -> Dict:
    """Get complete audio file info."""
    try:
        info = sf.info(file_path)
        return {
            "duration": info.duration,
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "format": info.format,
        }
    except Exception as e:
        logger.error(f"Failed to get info for {file_path}: {e}")
        return {}


def combine_audio_segments(
    segment_paths: List[str], 
    output_path: str,
    add_padding: bool = True
) -> str:
    """
    Combine multiple audio segments into one file.
    
    Args:
        segment_paths: List of audio file paths
        output_path: Output file path
        add_padding: Whether to add padding between segments
    
    Returns:
        Output file path
    """
    try:
        audio_list = []
        sample_rate = None
        
        for i, path in enumerate(segment_paths):
            if not os.path.exists(path):
                logger.warning(f"Segment not found: {path}")
                continue
            
            audio, sr = sf.read(path)
            
            if sample_rate is None:
                sample_rate = sr
            elif sr != sample_rate:
                logger.warning(f"Sample rate mismatch: {sr} != {sample_rate}")
                continue
            
            audio_list.append(audio)
            
            # Add padding between segments
            if add_padding and i < len(segment_paths) - 1:
                pad_samples = int(sr * SILENCE_PAD_SEC)
                audio_list.append(np.zeros(pad_samples, dtype=np.float32))
        
        if not audio_list:
            raise ValueError("No valid audio segments to combine")
        
        combined = np.concatenate(audio_list)
        
        # Final normalization
        combined = _normalize_loudness(combined)
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        sf.write(output_path, combined, sample_rate)
        
        logger.info(f"✅ Combined {len(segment_paths)} segments into {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to combine audio: {e}")
        raise


# ============================================
# 6. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("VOICE GENERATOR - OPTIMIZED (Soft-Limiter + Padding + Dynamic)")
    print("="*70)
    print()
    
    # Test single voice generation
    test_text = "Your heart is lying to you right now... and it has been since the day you were born."
    print(f"🧪 Testing voice generation:")
    print(f"   Text: {test_text}")
    print()
    
    try:
        output = generate_voice(test_text, "am_adam", "output/test_voice.wav")
        print(f"✅ Voice generated: {output}")
        info = get_audio_info(output)
        print(f"   Duration: {info.get('duration', 0):.2f}s")
        print(f"   Sample Rate: {info.get('sample_rate', 0)}")
        print()
        
        # Test segment generation
        print("🧪 Testing segment generation with dynamic exaggeration:")
        scenes = [
            {"caption": "This happens inside your brain every night..."},
            {"caption": "Your body has been hiding this from you your whole life."},
            {"caption": "And you won't believe why... but let me tell you the truth."},
            {"caption": "Now you know the secret that nobody talks about."}
        ]
        segments = generate_voice_segments(scenes, "am_adam", "output/test_segments")
        
        for seg in segments:
            print(f"   Scene {seg['scene_index']+1}: {seg['duration']:.2f}s ({seg['tts_engine']})")
        
        print()
        print("="*70)
        print("✅ Voice generator is ready for production!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
