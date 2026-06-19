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
        self.bitrate = VIDEO_CONFIG.BITRATE

        assert self.width < self.height, f"❌ Portrait dimension validation check failed"
        print(f"  📐 Canvas Bounds: {self.width}x{self.height} @ {self.fps}fps | Target CRF: {self.crf}")

    # ─── ASS Subtitles Timing Fix ─────────────────────────────────
    def _seconds_to_ass(self, s: float) -> str:
        """Converts float seconds to precise ASS timestamp format with safe millisecond rounding"""
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sc = int(s % 60)
        # FIX: Rounding fractions precisely up to 2 decimal places to avoid subtitle delay lag
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
                # Alternating high contrast structural styles
                style = "White" if idx % 2 == 0 else "Red"
                start_str = self._seconds_to_ass(wt['start'])
                end_str = self._seconds_to_ass(wt['end'])
                lines.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{word.upper()}")
        
        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,, ")
            
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    📝 Subtitles Rendered: {len(lines)} word nodes successfully packed.")

    # ─── Fast Cuts from Footage ───────────────────────────────────
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
            
            dirs_x = ["(iw-ow)/2", "0", "iw-ow"]
            dirs_y = ["(ih-oh)/2", "0", "ih-oh"]
            dx = random.choice(dirs_x)
            dy = random.choice(dirs_y)

            # FIX: Scaling filter adjustments preventing system from collapsing landscape layouts into 9:16 portrait
            vf = (
                f"scale=2*iw:-1,max_vfilters=1,"
                f"crop={self.width}:{self.height},"
                f"zoompan=z='min(zoom+0.006,{zoom_factor})':d={int(cut_len*self.fps)}:x='{dx}':y='{dy}':s={self.width}x{self.height},"
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
        colors = {"hook": "0x0A0A1A", "suspense": "0x1A020A", "story": "0x0A001A", "ctr": "0x1A0A02", "pause": "0x000000"}
        color = colors.get(seg_type, "0x0A0A1A")
        
        zoom_factor = VIDEO_CONFIG.ZOOM_INTENSITY if hasattr(VIDEO_CONFIG, 'ZOOM_INTENSITY') else 1.25
        vf = (
            f"format=yuv420p,"
            f"zoompan=z='min(zoom+0.003,{zoom_factor})':d={int(duration*self.fps)}:x='(iw-ow)/2':y='(ih-oh)/2':s={self.width}x{self.height},"
            f"setsar=1"
        )
        out = os.path.join(temp_dir, f"seg_color_{idx}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
            "-vf", vf, "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "ultrafast", "-r", str(self.fps), "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ], capture_output=True)
        return out if os.path.exists(out) else None

    # ─── Main Processing Pipeline ─────────────────────────────────
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        total_audio = audio_data.get('total_duration', 0)
        print(f"\n🎬 Assembler Execution | Target Render Time: {total_audio:.2f}s")

        if total_audio > 0 and script_segments:
            non_pause_dur = sum(s.get('duration', 0) for s in script_segments if not s.get('is_pause'))
            pause_dur = sum(s.get('duration', 0) for s in script_segments if s.get('is_pause'))
            speech_audio = total_audio - pause_dur
            if non_pause_dur > 0:
                ratio = speech_audio / non_pause_dur
                for s in script_segments:
                    if not s.get('is_pause'):
                        s['duration'] = round(s['duration'] * ratio, 3)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        
        # FIX: Cross-platform directory resolver validation checking absolute maps
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in locals() else os.getcwd()
        footage_dir = os.path.join(base_dir, "output", "footage")
        if not os.path.exists(footage_dir):
            footage_dir = os.path.join(os.getcwd(), "output", "footage")

        segment_files = []
        footage_idx = 0

        for i, seg in enumerate(script_segments):
            duration = seg.get('duration', 2.0)
            seg_type = seg.get('type', 'story')
            is_pause = seg.get('is_pause', False)

            if is_pause:
                black = self._color_bg_segment('pause', duration, temp_dir, i)
                if black:
                    segment_files.append(black)
                continue

            clip_file = os.path.join(footage_dir, f"clip_{footage_idx}.mp4")
            has_footage = os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000

            if has_footage:
                out = self._fast_cut_segment(clip_file, duration, temp_dir, i)
                if out:
                    segment_files.append(out)
                    footage_idx += 1
                    continue
            else:
                print(f"⚠️ Clip missing or too small at path: {clip_file} | Generating visual fallback layer.")

            out = self._color_bg_segment(seg_type, duration, temp_dir, i)
            if out:
                segment_files.append(out)
                footage_idx += 1

        if not segment_files:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception("Processing Exception: Zero compilation assets produced.")

        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{sf}'\n")

        audio_path = audio_data.get("final_audio", "")
        if audio_path and not os.path.exists(audio_path):
            audio_dir = os.path.join(base_dir, "output", "audio")
            if os.path.exists(audio_dir):
                mp3s = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
                if mp3s:
                    audio_path = os.path.join(audio_dir, max(mp3s, key=lambda x: os.path.getsize(os.path.join(audio_dir, x))))

        has_audio = audio_path and os.path.exists(audio_path)

        ass_path = os.path.join(temp_dir, "subs.ass")
        self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE)
        
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        master_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list
        ]
        if has_audio:
            master_cmd += ["-i", audio_path]

        # Burning multi-layered elements natively inside a single composite thread pass
        master_cmd += [
            "-vf", f"ass='{safe_ass}'",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
            "-r", str(self.fps),
        ]

        if has_audio:
            master_cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", "-shortest"]
            
        master_cmd += ["-movflags", "+faststart", output_path]

        print("🚀 Compiling rendering pipes — processing audio matrix overrides & burn-in filters...")
        r = subprocess.run(master_cmd, capture_output=True, text=True)
        
        if r.returncode != 0 or not os.path.exists(output_path):
            print(f"⚠️ Master layer composition failed. Reverting to safe baseline processing pass.")
            fallback_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list]
            if has_audio:
                fallback_cmd += ["-i", audio_path, "-c:a", "aac", "-shortest"]
            fallback_cmd += ["-c:v", "libx264", "-preset", "ultrafast", output_path]
            subprocess.run(fallback_cmd, capture_output=True)

        if os.path.exists(output_path):
            size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ COMPILATION SUCCESS: {output_path} | Size: {size:.2f} MB")
        else:
            raise Exception("Fatal Pipeline Failure: Targeted deployment video artifact is dead/missing.")

        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_path
