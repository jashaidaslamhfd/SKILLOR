from kokoro_onnx import Kokoro
import soundfile as sf
import os

# Model 1 baar download hoga. Phir cache se chalega
MODEL_PATH = "kokoro-v0.19.onnx"
VOICES_PATH = "voices-v0.19.bin"

def generate_voice(text, voice="am_adam", out_path="voice.wav"): # am_adam = US Male. Best for Baby Niche
    print("Loading Kokoro ONNX...")
    kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
    
    samples, sample_rate = kokoro.create(
        text, 
        voice=voice, 
        speed=1.0, # 1.0 = Normal. 1.2 = Fast
        lang="en-us"
    )
    sf.write(out_path, samples, sample_rate)
    print(f"Voice Done: {out_path}")
    return out_path
