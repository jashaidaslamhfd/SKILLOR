from moviepy.editor import *
import whisperx, os, torch
from PIL import Image
from omegaconf import ListConfig, DictConfig
from omegaconf.base import ContainerMetadata

# PyTorch 2.6+ security fix: allowlist omegaconf types
torch.serialization.add_safe_globals([ListConfig, DictConfig, ContainerMetadata])

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

CAPTION_FONT = "DejaVu-Sans-Bold"

def build_video(image_paths, audio_path, scenes):
    audio = AudioFileClip(audio_path)
    clip_duration = audio.duration / len(image_paths)

    clips = []
    for img_path in image_paths:
        img = ImageClip(img_path).set_duration(clip_duration).resize(height=1920)
        img = img.resize(lambda t: 1 + 0.3 * t / clip_duration)
        img = img.set_position('center')
        clips.append(img)

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    os.makedirs("output", exist_ok=True)
    out_path = "output/video_no_captions.mp4"
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", preset="medium")
    return out_path

def add_captions(video_path, audio_path):
    device = "cpu"
    compute_type = "int8"

    model = whisperx.load_model("tiny", device=device, compute_type=compute_type)
    audio_array = whisperx.load_audio(audio_path)
    result = model.transcribe(audio_array, batch_size=16)

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio_array, device, return_char_alignments=False)

    words = [w for seg in result["segments"] for w in seg.get("words", [])]

    video = VideoFileClip(video_path)
    caption_clips = []
    for w in words:
        if w.get("start") is None or w.get("end") is None:
            continue
        txt = TextClip(w['word'], fontsize=70, color='white', stroke_color='black',
                       stroke_width=2, font=CAPTION_FONT)
        txt = txt.set_position(('center', 0.8), relative=True).set_start(w['start']).set_duration(w['end'] - w['start'])
        caption_clips.append(txt)

    final = CompositeVideoClip([video] + caption_clips)
    out_path = "output/final_short.mp4"
    final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", preset="medium")
    return out_path

def generate_thumbnail(image_path, title, out_path="output/thumb.jpg"):
    img = ImageClip(image_path).resize(height=1920)
    title_txt = TextClip(title, fontsize=100, color='yellow', stroke_color='black',
                         stroke_width=3, font=CAPTION_FONT).set_position('center')
    thumb = CompositeVideoClip([img, title_txt])
    thumb.save_frame(out_path, t=0.1)
    return out_path
