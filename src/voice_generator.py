import os
import soundfile as sf
from kokoro import KPipeline

print("Loading Kokoro TTS Model...")
tts = KPipeline(lang_code='a') # 'a' = American English

SAMPLE_RATE = 24000  # Kokoro hamesha 24kHz audio deta hai, generator se nahi milta

def generate_voice(text: str, voice: str = "am_michael", output_path: str = "output/voice.wav") -> str:
    print(f"Generating Voice with: {voice}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    generator = tts(text, voice=voice, speed=1.0)
    # Kokoro generator har chunk ke liye 3 values deta hai: graphemes, phonemes, audio
    gs, ps, audio = next(generator)

    sf.write(output_path, audio, SAMPLE_RATE)
    print(f"Voice Saved: {output_path}")
    return output_path
