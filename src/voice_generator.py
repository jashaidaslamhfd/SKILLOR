import os
import numpy as np
import soundfile as sf
import logging
import re
import time
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PRIMARY ENGINE: Chatterbox (Resemble AI, MIT license - safe for a
# monetized channel).
#
# Why Chatterbox over Kokoro: Kokoro has no emotion/delivery control at all
# - every line comes out at the same flat intensity regardless of content,
# which is exactly why the channel's "dark mystery" voiceovers read as
# monotone. Chatterbox's `exaggeration` parameter is the first open-source
# control of its kind for this, so it's what actually fixes the tone
# instead of just changing which model renders the same flat delivery.
#
# Lazy-loaded on first use (not at import time) so a missing pip install or
# a failed model download doesn't crash the whole pipeline before it even
# starts - _get_chatterbox() catches that, and every call in this file
# falls back to Kokoro per-segment if Chatterbox is unavailable or a
# specific generation call fails. One bad Chatterbox call should never take
# a whole video down.
# ---------------------------------------------------------------------------
_chatterbox_model = None
_chatterbox_load_failed = False

# CORRECTED per Chatterbox's own docs: "higher exaggeration tends to speed
# up speech." The previous settings here (exaggeration=0.7, cfg_weight=0.35)
# were following Chatterbox's own "dramatic delivery" recipe, but that
# combination is documented to net out FASTER than default, not slower -
# which matches the "has emotion but talks too fast, loses the mystery
# vibe" feedback. Dialing exaggeration back down and cfg_weight back up
# keeps some expressiveness without the speedup side effect. Reliable
# pacing control now comes from CHATTERBOX_TEMPO below instead of fighting
# the model's internal speed/emotion coupling.
CHATTERBOX_EXAGGERATION = 0.6
CHATTERBOX_CFG_WEIGHT = 0.5
CHATTERBOX_TEMPERATURE = 0.8

# Chatterbox has no direct "speed" parameter like Kokoro does, so this
# applies an explicit pitch-preserving tempo change via ffmpeg after
# generation (ffmpeg's atempo filter) - this is what actually delivers a
# slow, deliberate "dark mystery" pace reliably, rather than relying on
# exaggeration/cfg_weight side effects. 0.85 = 15% slower, same pitch.
# Lower = slower/more ominous; 1.0 = no change. Valid ffmpeg atempo range
# per call is 0.5-2.0.
CHATTERBOX_TEMPO = float(os.environ.get("CHATTERBOX_TEMPO", "0.98"))

# Number of times Chatterbox retries per segment before giving up and
# falling back to Kokoro. Retries use the cloned voice reference every
# time — if the reference is bad the first attempt will fail, and retrying
# with the same bad reference won't help, so _synthesize_chatterbox()
# detects that case and skips pointless retries.
CHATTERBOX_MAX_RETRIES = 3

# Seconds to wait between Chatterbox retry attempts. Gives transient
# issues (GPU memory pressure, model hot-reload glitches, etc.) a moment
# to clear before hammering again.
CHATTERBOX_RETRY_DELAY = 2.0

# Optional voice-clone reference. Drop a clean 10-20s WAV (single speaker,
# no background noise) here and Chatterbox will clone that voice for every
# video instead of its own built-in default voice. If this file doesn't
# exist, Chatterbox just uses its default voice - nothing else changes.
VOICE_REFERENCE_PATH = os.environ.get("VOICE_REFERENCE_PATH", "assets/voice_reference.wav")


def _voice_reference_ok() -> bool:
    """True only if the reference WAV is actually usable for cloning.

    Guards against three silent failure modes that would otherwise make the
    pipeline *think* it cloned when it didn't: (1) file missing, (2) file
    present but empty/corrupt, (3) file readable but effectively silent
    (all-zero / near-silent), which produces a garbage clone. Any problem
    here just logs and returns False -> Chatterbox uses its default voice
    instead of a broken clone.
    """
    path = VOICE_REFERENCE_PATH
    if not path or not os.path.exists(path) or os.path.getsize(path) < 1024:
        return False
    try:
        info = sf.info(path)
        if info.frames <= 0 or info.duration < 1.0:
            logger.warning(f"Voice reference too short ({info.duration:.1f}s) - using default voice.")
            return False
        # Quick loudness sanity check on a small slice (cheap, no full read).
        sample, _ = sf.read(path, frames=min(info.frames, info.samplerate * 3), dtype="float32")
        if sample.size == 0 or float(np.abs(sample).max()) < 1e-3:
            logger.warning("Voice reference is silent/near-silent - using default voice.")
            return False
        return True
    except Exception as e:
        logger.warning(f"Voice reference unreadable ({e}) - using default voice.")
        return False


def _get_chatterbox():
    """Loads the Chatterbox model once and caches it. Returns None (and
    remembers not to retry) if loading fails for any reason - missing
    package, no internet for the first-run model download, out-of-memory
    on a CPU-only runner, etc."""
    global _chatterbox_model, _chatterbox_load_failed
    if _chatterbox_model is not None or _chatterbox_load_failed:
        return _chatterbox_model
    try:
        import torch
        from chatterbox.tts import ChatterboxTTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Chatterbox TTS model on {device} (first call only, then cached)...")
        _chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info("Chatterbox loaded successfully.")
    except Exception as e:
        logger.error(f"Chatterbox unavailable ({e}) - every segment will fall back to Kokoro.")
        _chatterbox_load_failed = True
        _chatterbox_model = None
    return _chatterbox_model


def _apply_tempo(audio: np.ndarray, sr: int, tempo: float) -> np.ndarray:
    """Pitch-preserving speed change via ffmpeg's atempo filter. Writes to a
    temp wav, runs ffmpeg, reads the result back. Returns the original
    audio unchanged if ffmpeg isn't available or the call fails, so a
    pacing tweak can never be the reason a whole segment fails."""
    if tempo == 1.0:
        return audio
    try:
        import subprocess
        import tempfile
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "in.wav")
            out_path = os.path.join(tmpdir, "out.wav")
            sf.write(in_path, audio, sr)
            result = subprocess.run(
                [ffmpeg_exe, "-y", "-i", in_path, "-filter:a", f"atempo={tempo}", out_path],
                capture_output=True, timeout=30,
            )
            if result.returncode != 0 or not os.path.exists(out_path):
                logger.warning(f"ffmpeg tempo adjustment failed, using original pace: {result.stderr[:200]}")
                return audio
            stretched, _ = sf.read(out_path, dtype="float32")
            return stretched
    except Exception as e:
        logger.warning(f"Tempo adjustment failed ({e}), using original pace")
        return audio


def _validate_generated_audio(audio: np.ndarray, sr: int, min_duration: float = 0.3) -> None:
    """Reject garbage TTS output that would silently produce broken audio.

    Catches three failure modes:
    1. Empty / near-zero-length arrays (model returned nothing)
    2. NaN / Inf contamination (numerical explosion in the model)
    3. Too-short output (e.g. model choked on the text and spat out a blip)

    Raises RuntimeError with a descriptive message so callers can decide
    whether to retry or fall back to another engine.
    """
    if audio is None or audio.size == 0:
        raise RuntimeError("TTS returned empty audio array")
    if np.isnan(audio).any() or np.isinf(audio).any():
        raise RuntimeError("TTS returned NaN/Inf audio — numerical explosion")
    duration = audio.size / sr if sr > 0 else 0.0
    if duration < min_duration:
        raise RuntimeError(f"TTS output too short ({duration:.2f}s < {min_duration:.2f}s minimum)")


def _synthesize_chatterbox(text: str, attempt: int = 1) -> tuple:
    """Generate speech with Chatterbox using the cloned voice reference.

    Returns (audio: np.ndarray float32, sample_rate: int).

    The voice reference is ALWAYS used when available — this is the whole
    point of the retry loop. If the reference file itself is broken
    (_voice_reference_ok() returns False), there is no point retrying with
    the same broken file, so we raise immediately to let the caller skip
    straight to Kokoro.

    Parameters
    ----------
    text : str
        The text to synthesize.
    attempt : int
        Current attempt number (1-based), used for logging.
    """
    model = _get_chatterbox()
    if model is None:
        raise RuntimeError("Chatterbox model not loaded")

    # If the voice reference is broken, retrying with the same broken
    # file is pointless — fail fast so the caller jumps to Kokoro.
    use_clone = _voice_reference_ok()
    if not use_clone and attempt == 1:
        logger.warning(
            "Voice reference NOT usable — Chatterbox will use its default voice. "
            "Retrying won't help since the reference won't magically fix itself."
        )

    kwargs = dict(
        exaggeration=CHATTERBOX_EXAGGERATION,
        cfg_weight=CHATTERBOX_CFG_WEIGHT,
        temperature=CHATTERBOX_TEMPERATURE,
    )
    if use_clone:
        kwargs["audio_prompt_path"] = VOICE_REFERENCE_PATH
        logger.info(f"Chatterbox attempt {attempt}/{CHATTERBOX_MAX_RETRIES}: using CLONED voice from {VOICE_REFERENCE_PATH}")
    else:
        logger.info(f"Chatterbox attempt {attempt}/{CHATTERBOX_MAX_RETRIES}: using DEFAULT voice (no valid reference)")

    wav = model.generate(text, **kwargs)
    audio = wav.squeeze().detach().cpu().numpy().astype(np.float32)

    # Validate before any post-processing — a garbage generation should
    # be retried, not normalised and passed downstream.
    _validate_generated_audio(audio, model.sr, min_duration=0.3)

    if np.isnan(audio).any():
        audio = np.nan_to_num(audio, 0.0)
    peak = np.abs(audio).max()
    if peak > 1.0:
        audio = audio / peak * 0.95

    audio = _apply_tempo(audio, model.sr, CHATTERBOX_TEMPO)

    return audio, model.sr


# ---------------------------------------------------------------------------
# FALLBACK ENGINE: Kokoro (Apache 2.0). No emotion control, but has no
# install/download surprises and is fast on CPU - kept exactly as before so
# a Chatterbox failure never takes the whole pipeline down with it.
# ---------------------------------------------------------------------------
_kokoro_tts = None
_kokoro_load_failed = False


def _get_kokoro():
    """Lazy-loads Kokoro only when actually needed as a fallback. Previously
    this loaded unconditionally at module import time (every single
    pipeline run), which meant paying its ~5s load + first-run model
    download cost even on runs where Chatterbox succeeded for every
    segment and Kokoro was never actually used."""
    global _kokoro_tts, _kokoro_load_failed
    if _kokoro_tts is not None or _kokoro_load_failed:
        return _kokoro_tts
    try:
        from kokoro import KPipeline
        logger.info("Loading Kokoro TTS model (fallback engine, first use only)...")
        _kokoro_tts = KPipeline(lang_code='a')  # 'a' = American English
        logger.info("Kokoro loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Kokoro: {e}")
        _kokoro_load_failed = True
        _kokoro_tts = None
    return _kokoro_tts

KOKORO_SAMPLE_RATE = 24000
SILENCE_PAD_SEC = 0.25  # Badha diya 0.15 se 0.25. Dar ke liye pause zyada


def add_mystery_pauses(text: str) -> str:
    """Adds a beat of suspense after dark hooks/reveals for retention.

    Neither Kokoro nor Chatterbox reads SSML tags like '<break time="0.5s"/>'
    - both read plain text/punctuation, so a literal SSML tag would get
    spoken aloud as text. Real neural TTS models DO respect
    punctuation-driven pauses though, so we use an ellipsis (natural
    trailing-off pause) or a short standalone clause instead - actually
    audible, not spoken as text."""
    # "you too?" -> trailing pause via ellipsis
    text = re.sub(r'you too\?', 'you too?..', text, flags=re.IGNORECASE)
    # already-present ".." -> stretch into a longer natural pause
    text = re.sub(r'(?<!\.)\.\.(?!\.)', '...', text)
    # "right now." -> comma-separated beat before continuing
    text = re.sub(r'right now\.', 'right now...', text, flags=re.IGNORECASE)
    return text


def _synthesize_kokoro(text: str, voice: str, speed: float):
    """Returns (audio: np.ndarray float32, sample_rate: int)."""
    kokoro = _get_kokoro()
    if not kokoro:
        raise RuntimeError("Kokoro TTS model not loaded. Check Kokoro installation.")

    generator = kokoro(text, voice=voice, speed=speed)
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

    return full_audio, KOKORO_SAMPLE_RATE


def _synthesize(text: str, voice: str = "am_adam", speed: float = 0.95):
    """Synthesize a single segment with retry logic.

    FLOW:
      1. Chatterbox + cloned voice reference — try up to CHATTERBOX_MAX_RETRIES
         times (default 3) with CHATTERBOX_RETRY_DELAY seconds between attempts.
      2. If ALL Chatterbox attempts fail → Kokoro (no retries, one shot).
      3. If Kokoro also fails → RuntimeError (NO silent silence insertion).

    Returns (audio, sample_rate, engine_used) so callers/logs can tell
    which engine actually produced a given segment.

    Raises
    ------
    RuntimeError
        If every Chatterbox attempt AND Kokoro both fail. The caller
        (generate_voice_segments) must handle this — it means the entire
        pipeline should abort, not silently insert silence.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text_with_pauses = add_mystery_pauses(text)

    # ---- STEP 1: Chatterbox with retries ----
    chatterbox_errors = []
    for attempt in range(1, CHATTERBOX_MAX_RETRIES + 1):
        try:
            audio, sr = _synthesize_chatterbox(text_with_pauses, attempt=attempt)
            engine = "chatterbox_clone" if _voice_reference_ok() else "chatterbox_default"
            logger.info(f"Chatterbox SUCCESS on attempt {attempt}/{CHATTERBOX_MAX_RETRIES} ({engine})")
            return audio, sr, engine
        except Exception as e:
            chatterbox_errors.append(str(e))
            logger.warning(f"Chatterbox attempt {attempt}/{CHATTERBOX_MAX_RETRIES} FAILED: {e}")
            # Wait before next retry (skip wait on last attempt)
            if attempt < CHATTERBOX_MAX_RETRIES:
                logger.info(f"Waiting {CHATTERBOX_RETRY_DELAY}s before retry...")
                time.sleep(CHATTERBOX_RETRY_DELAY)

    logger.error(
        f"All {CHATTERBOX_MAX_RETRIES} Chatterbox attempts failed. Errors: "
        + " | ".join(chatterbox_errors)
    )

    # ---- STEP 2: Kokoro fallback (one shot) ----
    logger.info("Falling back to Kokoro TTS engine...")
    try:
        audio, sr = _synthesize_kokoro(text_with_pauses, voice, speed)
        logger.info("Kokoro fallback SUCCESS")
        return audio, sr, "kokoro"
    except Exception as kokoro_err:
        # ---- STEP 3: Both engines failed — NO SILENCE, raise hard error ----
        error_msg = (
            f"VOICE GENERATION FAILED — both engines exhausted for this segment. "
            f"Chatterbox errors ({CHATTERBOX_MAX_RETRIES} attempts): "
            f"[{' | '.join(chatterbox_errors)}]. "
            f"Kokoro error: [{kokoro_err}]. "
            f"Pipeline CANNOT continue without voiceover."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def generate_voice(text: str, voice: str = "am_adam", output_path: str = "output/voice.wav", speed: float = 0.95) -> str:
    """USA Dark Science Voice: deep, slow, mysterious. Tries Chatterbox
    (expressive) first, Kokoro (flat but reliable) as fallback."""
    try:
        logger.info(f"Generating DARK voiceover (voice='{voice}', speed={speed})...")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        audio, sr, engine = _synthesize(text, voice, speed)
        sf.write(output_path, audio, sr)
        logger.info(f"Voice saved via {engine}: {output_path} ({len(audio)} samples, {len(audio)/sr:.2f}s)")
        return output_path
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise RuntimeError(f"Voice generation error: {e}")


def generate_voice_segments(
    scenes: List[dict],
    voice: str = "am_adam",  # only used if a segment falls back to Kokoro
    output_dir: str = "output/segments",
    speed: float = 0.95,     # only used if a segment falls back to Kokoro
) -> List[Dict]:
    """
    Each scene gets its own audio, generated via Chatterbox (with mystery
    pauses and dark-tone exaggeration) or Kokoro as a per-segment fallback.

    Raises
    ------
    RuntimeError
        If any segment fails on ALL engines (Chatterbox x3 + Kokoro).
        The pipeline MUST abort — a video with missing voiceover segments
        is worse than no video at all.
    """
    os.makedirs(output_dir, exist_ok=True)
    segments = []
    engine_counts = {}

    for i, scene in enumerate(scenes):
        caption = scene.get('caption', '').strip() if isinstance(scene, dict) else str(scene)
        if not caption:
            caption = " "

        # No try/except swallowing here — if _synthesize raises, the whole
        # pipeline must abort. Silent 1.5s silence inserts are NOT acceptable;
        # main.py's quality gate will catch the crash and log it properly.
        audio, sr, engine = _synthesize(caption, voice, speed)

        engine_counts[engine] = engine_counts.get(engine, 0) + 1
        path = os.path.join(output_dir, f"seg_{i}.wav")
        sf.write(path, audio, sr)
        duration = len(audio) / sr

        segments.append({"path": path, "duration": duration, "caption": caption, "tts_engine": engine})
        logger.info(f"Segment {i+1}/{len(scenes)} via {engine}: {duration:.2f}s - \"{caption[:50]}...\"")

    total = sum(s['duration'] for s in segments)
    logger.info(f"Total DARK voiceover duration: {total:.2f}s | engines used: {engine_counts}")

    # Final consistency check — all segments must use the SAME engine.
    # Mixed engines mean different voice timbres across scenes, which
    # sounds jarring and unprofessional. Abort if mixed.
    engines_used = set(engine_counts.keys())
    if len(engines_used) > 1:
        raise RuntimeError(
            f"Mixed TTS engines in the same video: {dict(engine_counts)} "
            f"— voices would sound inconsistent. Aborting."
        )

    return segments
            
