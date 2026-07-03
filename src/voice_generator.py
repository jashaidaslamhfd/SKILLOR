import os
import soundfile as sf
from kokoro.pipeline import KPipeline # Yahi change hai

print("Loading Kokoro TTS Model...")
tts = KPipeline(lang_code='a') # 'a' = American English

def generate_voice(text: str, voice: str = "am_michael", output_path: str = "output/voice.wav") -> str:
    print(f"Generating Voice with: {voice}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    generator = tts(text, voice=voice, speed=1.0)
    audio, sample_rate = next(generator) # Generator se audio nikalte hain

    sf.write(output_path, audio, sample_rate)
    print(f"Voice Saved: {output_path}")
    return output_path
