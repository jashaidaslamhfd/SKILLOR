import os
import soundfile as sf
from kokoro import Kokoro

# Model 1 baar load hoga = Fast
print("Loading Kokoro TTS Model...")
tts = Kokoro.from_pretrained("hexgrad/Kokoro-82M")

def generate_voice(text: str, voice: str = "am_michael", output_path: str = "output/voice.wav") -> str:
    """
    Kokoro TTS se English voice banata hai. USA Voice = am_michael
    """
    print(f"Generating Voice with: {voice}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Kokoro se audio generate
    audio, sample_rate = tts.create(text, voice=voice, speed=1.0)

    #.wav me save
    sf.write(output_path, audio, sample_rate)

    print(f"Voice Saved: {output_path}")
    return output_path
