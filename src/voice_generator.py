import os
import numpy as np
import soundfile as sf
from kokoro import KPipeline

print("Loading Kokoro TTS Model...")
tts = KPipeline(lang_code='a') # 'a' = American English

SAMPLE_RATE = 24000  # Kokoro hamesha 24kHz audio deta hai, generator se nahi milta

def generate_voice(text: str, voice: str = "am_michael", output_path: str = "output/voice.wav") -> str:
    print(f"Generating Voice with: {voice}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    generator = tts(text, voice=voice, speed=1.0)

    audio_chunks = []
    for gs, ps, audio in generator:
        audio_chunks.append(audio)

    if not audio_chunks:
        raise RuntimeError("Kokoro ne koi audio generate nahi kiya - text check karo")

    full_audio = np.concatenate(audio_chunks)
    sf.write(output_path, full_audio, SAMPLE_RATE)
    print(f"Voice Saved: {output_path} ({len(audio_chunks)} chunks combine kiye)")
    return output_path
