from moviepy.editor import *
import whisperx, os

def build_video(image_paths, audio_path, scenes):
    """
    Images + audio (Kokoro se pehle hi bana hua) ko combine karke
    Ken Burns zoom effect wali 9:16 video banata hai (captions ke bina).
    """
    audio = AudioFileClip(audio_path)
    clip_duration = audio.duration / len(image_paths)

    clips = []
    for img_path in image_paths:
        img = ImageClip(img_path).set_duration(clip_duration).resize(height=1920)
        img = img.resize(lambda t: 1 + 0.3 * t / clip_duration)  # 100% to 130% Zoom = Ken Burns
        img = img.set_position('center')
        clips.append(img)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    os.makedirs("output", exist_ok=True)
    out_path = "output/video_no_captions.mp4"
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", preset="medium")
    return out_path


def add_captions(video_path, audio_path):
    """
    WhisperX se word-level timing nikal kar video par bold word-by-word captions add karta hai.
    """
    model = whisperx.load_model("tiny", device="cpu", compute_type="int8")
    result = model.transcribe(audio_path)
    words = [w for seg in result["segments"] for w in seg.get("words", [])]

    video = VideoFileClip(video_path)
    caption_clips = []
    for w in words:
        # Kabhi kabhi whisperx kisi word ka timing nahi deta, usko skip karo
        if w.get("start") is None or w.get("end") is None:
            continue
        txt = TextClip(w['word'], fontsize=70, color='white', stroke_color='black',
                        stroke_width=2, font="Arial-Bold")
        txt = txt.set_position(('center', 0.8), relative=True).set_start(w['start']).set_duration(w['end'] - w['start'])
        caption_clips.append(txt)

    final = CompositeVideoClip([video] + caption_clips)
    out_path = "output/final_short.mp4"
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", preset="medium")
    return out_path


def generate_thumbnail(image_path, title, out_path="output/thumb.jpg"):
    """
    Pehli AI image par title text daal kar 9:16 thumbnail banata hai.
    """
    img = ImageClip(image_path).resize(height=1920)
    title_txt = TextClip(title, fontsize=100, color='yellow', stroke_color='black',
                          stroke_width=3, font="Arial-Bold").set_position('center')
    thumb = CompositeVideoClip([img, title_txt])
    thumb.save_frame(out_path, t=0.1)
    return out_path
