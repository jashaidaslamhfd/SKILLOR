"""Video Assembler — Fast Cuts + Aggressive Zoom + 9:16 Portrait"""

import os
import subprocess
import tempfile
import shutil
import random
from typing import List, Dict

from config.settings import VIDEO_CONFIG, CAPTION_CONFIG


class VideoAssembler:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.crf = VIDEO_CONFIG.CRF       # 18
        self.preset = VIDEO_CONFIG.PRESET  # slow
        self.bitrate = VIDEO_CONFIG.BITRATE

        assert self.width < self.height, f"❌ Portrait check failed"
        print(f"  📐 {self.width}x{self.height} @ {self.fps}fps | CRF:{self.crf}")

    # ─── ASS Subtitles ────────────────────────────────────────────
    def _seconds_to_ass(self, s: float) -> str:
        h = int(s // 3600); m = int((s % 3600) // 60)
        sc = int(s % 60); cs = int((s % 1) * 100)
        return f"{h}:{m:02d}:{sc:02d}.{cs:02d}"

    def _create_ass(self, word_timings: List[Dict], ass_path: str, font_size: int = 90):
        c = CAPTION_CONFIG
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{c.FONT_NAME},{font_size},{c.PRIMARY_COLOR},&H000000FF,{c.OUTLINE_COLOR},&H00000000,1,0,0,0,100,100,2,0,1,{c.OUTLINE_WIDTH},{c.SHADOW},{c.ALIGNMENT},10,10,{c.MARGIN_V},1
Style: Red,{c.FONT_NAME},{font_size},{c.SECONDARY_COLOR},&H00FFFFFF,{c.OUTLINE_COLOR},&H00000000,1,0,0,0,100,100,2,0,1,{c.OUTLINE_WIDTH},{c.SHADOW},{c.ALIGNMENT},10,10,{c.MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = []
        for idx, wt in enumerate(word_timings):
            word = str(wt.get('word', '')).strip()
            if word:
                style = "White" if idx % 2 == 0 else "Red"
                lines.append(f"Dialogue: 0,{self._seconds_to_ass(wt['start'])},{self._seconds_to_ass(wt['end'])},{style},,0,0,0,,{word.upper()}")
        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,, ")
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    📝 ASS: {len(lines)} words | size:{font_size}px")

    # ─── Fast Cuts from Footage ───────────────────────────────────
    def _fast_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int) -> str:
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', clip_file
            ], capture_output=True, text=True)
            src_dur = float(probe.stdout.strip())
        except:
            src_dur = 30.0

        cuts = []
        current = 0.0
        cut_idx = 0

        while current < total_dur:
            cut_len = min(random.uniform(0.8, 1.5), total_dur - current)
            if cut_len < 0.4:
                break

            cut_path = os.path.join(temp_dir, f"fastcut_{seg_idx}_{cut_idx}.mp4")
            max_start = max(0.0, src_dur - cut_len - 0.5)
            ss = random.uniform(0, max_start)

            z = random.uniform(1.15, 1.35)
            dirs_x = [f"iw/2-(iw/zoom/2)", "0", f"iw-(iw/zoom)"]
            dirs_y = [f"ih/2-(ih/zoom/2)", "0", f"ih-(ih/zoom)"]
            dx = random.choice(dirs_x)
            dy = random.choice(dirs_y)

            total_frames = max(1, int(round(cut_len * self.fps)))
            zoom_step = (z - 1.0) / total_frames

            vf = (
                f"fps={self.fps},"
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},setsar=1,"
                f"zoompan=z='min(zoom+{zoom_step:.6f},{z})':d={total_frames}:x='{dx}':y='{dy}':s={self.width}x{self.height}:fps={self.fps},"
                f"scale={self.width}:{self.height},setsar=1"
            )

            cmd = [
                "ffmpeg", "-y", "-ss", str(ss), "-i", clip_file,
                "-t", str(cut_len), "-vf", vf,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "fast",
                "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an",
                cut_path
            ]
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode == 0 and os.path.exists(cut_path) and os.path.getsize(cut_path) > 1000:
                cuts.append(cut_path)

            current += cut_len
            cut_idx += 1

        if not cuts:
            return None

        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")
        cut_list = os.path.join(temp_dir, f"cuts_{seg_idx}.txt")
        with open(cut_list, 'w') as f:
            for c in cuts:
                f.write(f"file '{os.path.abspath(c)}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur), "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an",
            out_path
        ], capture_output=True)

        if os.path.exists(out_path):
            return out_path
        return None

    def _color_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        colors = {"hook": "0x050510", "suspense": "0x100005", "story": "0x050010", "ctr": "0x100500", "pause": "0x0a0a0c"}
        color = colors.get(seg_type, "0x050510")

        z = random.uniform(1.08, 1.25)
        total_frames = max(1, int(round(duration * self.fps)))
        zoom_step = (z - 1.0) / total_frames
        vf = (
            f"format=yuv420p,"
            f"zoompan=z='if(lte(zoom,1.0),{z},max(1.0,zoom-{zoom_step:.6f}))':d={total_frames}:s={self.width}x{self.height}:fps={self.fps},"
            f"scale={self.width}:{self.height},setsar=1"
        )
        out = os.path.join(temp_dir, f"seg_color_{idx}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
            "-vf", vf, "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps), "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ], capture_output=True)
        return out if os.path.exists(out) else None

    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        total_audio = audio_data.get('total_duration', 0)
        if word_timings and script_segments:
            wt_idx = 0
            for s in script_segments:
                if s.get('is_pause'): continue
                seg_word_count = len(s.get('text', '').split())
                seg_words = word_timings[wt_idx:wt_idx + seg_word_count]
                wt_idx += seg_word_count
                if seg_words:
                    new_dur = round(max(0.2, seg_words[-1]['end'] - seg_words[0]['start']), 3)
                    original_dur = s.get('duration', new_dur)
                    if not (original_dur > 0 and new_dur < original_dur * 0.5):
                        s['duration'] = new_dur
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        footage_dir = os.path.join("output", "footage")

        segment_files = []
        footage_idx = 0
        for i, seg in enumerate(script_segments):
            duration = max(0.3, seg.get('duration', 2.0))
            if seg.get('is_pause'):
                black = self._color_bg_segment('pause', min(duration, 0.35), temp_dir, i)
                if black: segment_files.append(black)
                continue

            clip_file = os.path.join(footage_dir, f"clip_{footage_idx}.mp4")
            if os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000:
                out = self._fast_cut_segment(clip_file, duration, temp_dir, i)
                if out:
                    segment_files.append(out)
                    footage_idx += 1
                    continue
            
            out = self._color_bg_segment(seg.get('type', 'story'), duration, temp_dir, i)
            if out: segment_files.append(out)
            footage_idx += 1

        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{os.path.abspath(sf)}'\n")

        video_raw = os.path.join(temp_dir, "video_raw.mp4")
        audio_path = audio_data.get("final_audio", "")
        has_audio = audio_path and os.path.exists(audio_path)

        concat_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list]
        if has_audio:
            concat_cmd += ["-i", audio_path, "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                          "-r", str(self.fps), "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "-pix_fmt", "yuv420p"]
        concat_cmd.append(video_raw)
        subprocess.run(concat_cmd, capture_output=True)

        # FIX: Final Caption Burn with Padding and Shortest
        ass_path = os.path.join(temp_dir, "subs.ass")
        self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE)
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        r = subprocess.run([
            "ffmpeg", "-y", "-i", video_raw,
            "-vf", f"ass={safe_ass},pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
            "-r", str(self.fps), "-c:a", "aac", "-shortest", "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            output_path
        ], capture_output=True, text=True)

        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_path
