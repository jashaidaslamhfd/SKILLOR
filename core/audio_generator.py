import os
import torch
import soundfile as sf
from kokoro import KPipeline
from moviepy.editor import AudioFileClip

# Kokoro voices - Adam jaisi male voices
VOICE_IDS = {
    'mystery': 'am_adam', # Adam - deep, best for mystery
    'science': 'am_michael', # Michael - energetic, clear
    'human_behaviour': 'bm_george' # George - conversational, friendly
}

# Global pipeline - ek baar load hoga
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        print("[Audio] Loading Kokoro model... first time 1-2 min lag sakta")
        _pipeline = KPipeline(lang_code='a') # 'a' = American English
    return _pipeline

def generate_voiceover(script_text, niche='human_behaviour', output_path="temp/audio.mp3"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Script limit - Kokoro fast hai but 30s shorts ke liye
    words = script_text.split()
    if len(words) > 75:
        script_text = ' '.join(words[:75])

    # 2. Kokoro me emotion ke liye punctuation use karo
    if niche == 'mystery':
        script_text = f"...{script_text}..." # Whisper effect
    elif niche == 'science':
        script_text = f"{script_text}!" # Excited
    else:
        script_text = f"{script_text}" # Normal

    voice = VOICE_IDS.get(niche, VOICE_IDS['human_behaviour'])

    try:
        print(f"[Audio] Kokoro TTS - Voice: {voice}")
        pipeline = get_pipeline()

        # Generate - Kokoro streaming deta hai
        generator = pipeline(script_text, voice=voice, speed=1.1) # 10% fast

        # Audio combine karo
        audio_chunks = []
        for i, (gs, ps, audio) in enumerate(generator):
            audio_chunks.append(audio)

        # Save
        import numpy as np
        final_audio = np.concatenate(audio_chunks)
        sf.write(output_path, final_audio, 24000) # Kokoro ka sample rate 24kHz

        # Double check duration
        clip = AudioFileClip(output_path)
        if clip.duration > 29:
            clip = clip.fx(lambda c: c.speedx(clip.duration / 28.0))
            clip.write_audiofile(output_path, logger=None)
        clip.close()

        print(f"[Audio] ✅ Kokoro Generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"[Audio] Kokoro failed: {e}")
        # Fallback to edge-tts
        import asyncio
        import edge_tts
        communicate = edge_tts.Communicate(script_text, 'en-US-GuyNeural')
        asyncio.run(communicate.save(output_path))
        print(f"[Audio] ✅ Fallback Edge-TTS: {output_path}")
        return output_path
