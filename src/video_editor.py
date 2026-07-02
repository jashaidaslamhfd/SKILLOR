from moviepy.editor import *
from gTTS import gTTS
import whisperx, os

def make_video(script_data, image_paths):
    scenes = script_data['scenes']
    voice_text = script_data['voiceover']
    title = script_data['title']

    # 1. AI VOICE: Free gTTS. Quality ke liye ElevenLabs add kar sakte ho baad me
    tts = gTTS(voice_text, lang='en', tld='us')
    audio_path = "voice.mp3"
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)

    # 2. WORD LEVEL TIMING: Whisper se pata chalega har word kab bola
    model = whisperx.load_model("tiny", device="cpu", compute_type="int8")
    result = model.transcribe(audio_path)
    words = [w for seg in result["segments"] for w in seg["words"]]

    # 3. VIDEO BANANA: 9:16, Ken Burns, Caption Sync
    clips = []
    clip_duration = audio.duration / len(image_paths)

    for i, img_path in enumerate(image_paths):
        img = ImageClip(img_path).set_duration(clip_duration).resize(height=1920)
        img = img.resize(lambda t: 1 + 0.3 * t / clip_duration) # 100% to 130% Zoom = Ken Burns
        img = img.set_position('center')
        clips.append(img)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    # 4. CAPTION SYNC: Har word screen pe bold hoga jab bola jayega
    caption_clips = []
    for w in words:
        txt = TextClip(w['word'], fontsize=70, color='white', stroke_color='black', stroke_width=2, font="Arial-Bold")
        txt = txt.set_position(('center', 0.8), relative=True).set_start(w['start']).set_duration(w['end'] - w['start'])
        caption_clips.append(txt)

    final = CompositeVideoClip([video] + caption_clips)
    out_path = "short.mp4"
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", preset="medium")

    # 5. THUMBNAIL: 9:16 AI Image with Title Text
    thumb = image_paths[0]
    thumb_img = ImageClip(thumb).resize(height=1920)
    title_txt = TextClip(title, fontsize=100, color='yellow', stroke_color='black', stroke_width=3, font="Arial-Bold").set_position('center')
    thumbnail = CompositeVideoClip([thumb_img, title_txt]).save_frame("thumb.jpg", t=0.1)

    return out_path, "thumb.jpg"
