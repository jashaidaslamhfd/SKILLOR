"""Video Assembler — Fast Cuts, Safe Zoompan scaling, and 9:16 Center-Locked ASS Rendering"""

import os
import subprocess
import tempfile
import shutil
import random
from typing import List, Dict

from config.settings import VIDEO_CONFIG, CAPTION_CONFIG


class VideoAssembler:
    def __init__(self):
        self.width = VIDEO_CONFIG.RESOLUTION[0] if hasattr(VIDEO_CONFIG, 'RESOLUTION') else 1080
        self.height = VIDEO_CONFIG.RESOLUTION[1] if hasattr(VIDEO_CONFIG, 'RESOLUTION') else 1920
        self.fps = VIDEO_CONFIG.FPS if hasattr(VIDEO_CONFIG, 'FPS') else 30
        self.crf = VIDEO_CONFIG.CRF       # 18
        self.preset = VIDEO_CONFIG.PRESET  # slow

        assert self.width < self.height, f"❌ Portrait dimension validation check failed"
        print(f"  📐 Canvas Bounds: {self.width}x{self.height} @ {self.fps}fps | Target CRF: {self.crf}")

    def _seconds_to_ass(self, s: float) -> str:
        """Converts float seconds to precise ASS timestamp format with safe millisecond rounding"""
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sc = int(s % 60)
        cs = int(round((s % 1) * 100))
        if cs >= 100:
            sc += 1
            cs -= 100
            if sc >= 60:
                sc -= 60
                m += 1
                if m >= 60:
                    m -= 60
                    h += 1
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
                start_str = self._seconds_to_ass(wt['start'])
                end_str = self._seconds_to_ass(wt['end'])
                lines.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{word.upper()}")
        
        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,, ")
            
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    📝 Subtitles Rendered: {len(lines)} word nodes successfully packed.")

    def _fast_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int) -> str:
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', clip_file
            ], capture_output=True, text=True, timeout=10)
            src_dur = float(probe.stdout.strip())
        except:
            src_dur = 30.0

        cuts = []
        current = 0.0
        cut_idx = 0
        interval_min = VIDEO_CONFIG.FAST_CUT_INTERVAL if hasattr(VIDEO_CONFIG, 'FAST_CUT_INTERVAL') else 0.8
        
        while current < total_dur:
            cut_len = min(random.uniform(interval_min, interval_min + 0.5), total_dur - current)
            if cut_len < 0.3:
                break

            cut_path = os.path.join(temp_dir, f"fastcut_{seg_idx}_{cut_idx}.mp4")
            max_start = max(0.0, src_dur - cut_len - 0.5)
            ss = random.uniform(0, max_start)
            zoom_factor = VIDEO_CONFIG.ZOOM_INTENSITY if hasattr(VIDEO_CONFIG, 'ZOOM_INTENSITY') else 1.25
            
            vf = (
                f"scale=2*iw:-1,crop={self.width}:{self.height},"
                f"zoompan=z='min(zoom+0.006,{zoom_factor})':d={int(cut_len*self.fps)}:x='(iw-ow)/2':y='(ih-oh)/2':s={self.width}x{self.height},"
                f"setsar=1"
            )

            cmd = [
                "ffmpeg", "-y", "-ss", str(round(ss, 2)), "-i", clip_file,
                "-t", str(round(cut_len, 2)), "-vf", vf,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "ultrafast",
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
                f.write(f"file '{c}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur), "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "ultrafast", "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an",
            out_path
        ], capture_output=True)

        return out_path if os.path.exists(out_path) else None

    def _color_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        # High contrast fallback colors so it's never pitch black
        colors = {"hook": "0x3A1A1A", "suspense": "0x1A3A1A", "story": "0x1A1A3A", "ctr": "0x3A3A1A", "pause": "0x111111"}
        color = colors.get(seg_type, "0x222222")
        
        vf = f"format=yuv420p,setsar=1"
        out = os.path.join(temp_dir, f"seg_color_{idx}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
            "-vf", vf, "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "ultrafast", "-r", str(self.fps), "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ], capture_output=True)
        return out if os.path.exists(out) else None

    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        total_audio = audio_data.get('total_duration', 0)
        print(f"\n🎬 Assembler Execution | Target Render Time: {total_audio:.2f}s")

        # FIX 1: Safe fallback for Word Timings if edge-tts drop boundaries
        if not word_timings:
            print("⚠️ Word timings empty! Generating artificial precise text maps...")
            raw_words = []
            for seg in script_segments:
                text_content = seg.get('text', '') or seg.get('script_text', '')
                if text_content:
                    raw_words.extend(text_content.split())
            if not raw_words:
                raw_words = ["DISCOVER", "THE", "SHOCKING", "TRUTH", "RIGHT", "NOW"]
            
            word_count = len(raw_words)
            time_per_word = total_audio / max(1, word_count)
            for idx, w in enumerate(raw_words):
                word_timings.append({
                    "word": w,
                    "start": round(idx * time_per_word, 3),
                    "end": round((idx + 1) * time_per_word, 3)
                })

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else os.getcwd()
        footage_dir = os.path.join(base_dir, "output", "footage")

        segment_files = []

        for i, seg in enumerate(script_segments):
            duration = seg.get('duration', 2.0)
            seg_type = seg.get('type', 'story')
            is_pause = seg.get('is_pause', False)

            if is_pause:
                black = self._color_bg_segment('pause', duration, temp_dir, i)
                if black:
                    segment_files.append(black)
                continue

            # FIX 2: Resolve clip file paths from the actual 'footage_clips' array passed by Fetcher
            clip_file = None
            if footage_clips and i < len(footage_clips):
                target = footage_clips[i]
                if isinstance(target, dict):
                    clip_file = target.get('path') or target.get('file')
                elif isinstance(target, str):
                    clip_file = target

            # Cross check Directory fallback if array mapping references are skewed
            if not clip_file or not os.path.exists(clip_file):
                if os.path.exists(footage_dir):
                    valid_mp4s = [os.path.join(footage_dir, f) for f in os.listdir(footage_dir) if f.endswith('.mp4')]
                    if valid_mp4s:
                        clip_file = valid_mp4s[i % len(valid_mp4s)]

            if clip_file and os.path.exists(clip_file) and os.path.getsize(clip_file) > 1000:
                out = self._fast_cut_segment(clip_file, duration, temp_dir, i)
                if out:
                    segment_files.append(out)
                    continue
            else:
                print(f"⚠️ Clip asset missing for segment {i} ({clip_file}) -> Rendering color fallback layer.")

            out = self._color_bg_segment(seg_type, duration, temp_dir, i)
            if out:
                segment_files.append(out)

        if not segment_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception("Processing Exception: Zero compilation assets produced.")

        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{sf}'\n")

        audio_path = audio_data.get("final_audio", "")
        has_audio = audio_path and os.path.exists(audio_path)

        ass_path = os.path.join(temp_dir, "subs.ass")
        self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE)
        
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        master_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list
        ]
        if has_audio:
            master_cmd += ["-i", audio_path]

        master_cmd += [
            "-vf", f"ass='{safe_ass}'",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", "ultrafast",
            "-r", str(self.fps),
        ]

        if has_audio:
            master_cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
            
        master_cmd += ["-movflags", "+faststart", output_path]

        print("🚀 Compiling rendering pipes — burning assets & sub layers...")
        subprocess.run(master_cmd, capture_output=True)

        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_path
