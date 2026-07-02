import os
from moviepy.editor import *
from moviepy.video.fx.all import *

def create_viral_captions(captions_data, video_duration):
    """MrBeast style captions - 3 words max, big, yellow"""
    clips = []

    for cap in captions_data:
        txt = cap['text'].upper()
        # 3 words per line max
        words = txt.split()
        lines = [' '.join(words[i:i+3]) for i in range(0, len(words), 3)]

        for i, line in enumerate(lines):
            start = cap['start'] + i * 0.4
            end = min(cap['end'], start + 0.4)

            # MrBeast style: Bold, Yellow, Black outline, Pop animation
            txt_clip = TextClip(
                line,
                fontsize=110,
                color='yellow',
                font='Impact',
                stroke_color='black',
                stroke_width=8,
                method='caption',
                size=(900, None)
            )
            txt_clip = txt_clip.set_position(('center', 0.75), relative=True)
            txt_clip = txt_clip.set_start(start).set_end(end)

            # Pop in animation - 0.1s
            txt_clip = txt_clip.resize(lambda t: 1 + 0.3 * (t < 0.1))
            clips.append(txt_clip)

    return clips

def assemble_video(footage_path, audio_path, captions_data, hook_data, script_data):
    """
    Swap Rate Fix: First 1 second me 4 things honge
    1. Zoom in 1.3x 2. Shake 3. Whoosh SFX 4. Red flash
    """
    print("[Assembler] Starting viral assembly...")

    # 1. Load assets
    video = VideoFileClip(footage_path)
    audio = AudioFileClip(audio_path)

    # 2. Duration match
    duration = min(video.duration, audio.duration, 29.0)
    video = video.subclip(0, duration)
    audio = audio.subclip(0, duration)

    # 3. SWAP RATE KILLER: First 1 second effects
    def apply_hook_effects(get_frame, t):
        frame = get_frame(t)
        if t < 1.0: # First 1 second
            # Zoom 1.0 -> 1.3x
            zoom = 1 + 0.3 * t
            h, w = frame.shape[:2]
            new_h, new_w = int(h/zoom), int(w/zoom)
            y1 = (h - new_h) // 2
            x1 = (w - new_w) // 2
            frame = frame[y1:y1+new_h, x1:x1+new_w]
            frame = cv2.resize(frame, (w, h))

            # Shake effect
            if 0.2 < t < 0.8:
                dx = random.randint(-10, 10)
                dy = random.randint(-10, 10)
                M = np.float32([[1, 0, dx], [0, 1, dy]])
                frame = cv2.warpAffine(frame, M, (w, h))

            # Red flash at 0.1s
            if 0.08 < t < 0.15:
                frame = frame * 0.3 + np.array([0, 0, 255]) * 0.7
        return frame

    import cv2
    import numpy as np
    video = video.fl(apply_hook_effects)

    # 4. Add Whoosh SFX at 0.1s - Pattern interrupt
    try:
        whoosh = AudioFileClip("assets/whoosh.mp3").subclip(0, 0.5).volumex(0.6)
        audio = CompositeAudioClip([audio, whoosh.set_start(0.1)])
    except:
        print("[Assembler] Whoosh SFX not found, skipping")

    # 5. Viral captions
    caption_clips = create_viral_captions(captions_data, duration)

    # 6. Hook text overlay 0-1s - Big red
    hook_clip = TextClip(
        hook_data['hook'].upper(),
        fontsize=120,
        color='red',
        font='Impact',
        stroke_color='white',
        stroke_width=5
    ).set_position('center').set_duration(1.0)

    # 7. Final composite
    final = CompositeVideoClip([video, hook_clip] + caption_clips)
    final = final.set_audio(audio)

    # 8. Export - YouTube Shorts settings
    output_path = "temp/final_short.mp4"
    final.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        threads=4,
        logger=None,
        preset='ultrafast' # Fast render
    )

    # Cleanup
    video.close()
    audio.close()
    final.close()

    print(f"[Assembler] ✅ Final video: {output_path}")
    return output_path
