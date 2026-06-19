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
        # FIX: Two styles — White and Red — so words alternate color, centered, bold
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
                # FIX: Alternate White/Red per word — even index=White, odd index=Red
                style = "White" if idx % 2 == 0 else "Red"
                lines.append(f"Dialogue: 0,{self._seconds_to_ass(wt['start'])},{self._seconds_to_ass(wt['end'])},{style},,0,0,0,,{word.upper()}")
        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,, ")
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    📝 ASS: {len(lines)} words | size:{font_size}px")

    # ─── Fast Cuts from Footage ───────────────────────────────────
    def _fast_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int) -> str:
        """
        TikTok/Reels style fast cuts:
        - Every 1.5–2.5s clip changes
        - Each cut: random start point from source footage
        - Each cut: random zoom (1.05–1.30x) + random direction
        - Portrait scale enforced after every zoom
        """
        # Get source clip duration
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
            cut_len = min(random.uniform(0.8, 1.5), total_dur - current)  # FIX: faster cuts (was 1.5-2.5)
            if cut_len < 0.4:
                break

            cut_path = os.path.join(temp_dir, f"fastcut_{seg_idx}_{cut_idx}.mp4")

            # Random start in source clip
            max_start = max(0.0, src_dur - cut_len - 0.5)
            ss = random.uniform(0, max_start)

            # Random zoom + direction — each cut looks different
            z = random.uniform(1.15, 1.35)  # FIX: stronger zoom (was 1.05-1.30)
            dirs_x = [f"iw/2-(iw/zoom/2)", "0", f"iw-(iw/zoom)"]
            dirs_y = [f"ih/2-(ih/zoom/2)", "0", f"ih-(ih/zoom)"]
            dx = random.choice(dirs_x)
            dy = random.choice(dirs_y)

            vf = (
                # Step 1: Scale footage to portrait
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},setsar=1,"
                # Step 2: Zoom in random direction
                f"zoompan=z='min(zoom+0.01,{z})':d=1:x='{dx}':y='{dy}',"
                # Step 3: Force portrait back (zoompan resets resolution)
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

        # Concat cuts into one segment
        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")
        cut_list = os.path.join(temp_dir, f"cuts_{seg_idx}.txt")
        with open(cut_list, 'w') as f:
            for c in cuts:
                f.write(f"file '{c}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur), "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an",
            out_path
        ], capture_output=True)

        if os.path.exists(out_path):
            print(f"    ✅ Seg {seg_idx}: {len(cuts)} fast cuts | footage")
            return out_path
        return None

    def _color_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        """Dark color bg with pulsing zoom — for when no footage"""
        colors = {"hook": "0x050510", "suspense": "0x100005", "story": "0x050010", "ctr": "0x100500", "pause": "0x000000"}
        color = colors.get(seg_type, "0x050510")

        z = random.uniform(1.08, 1.25)
        vf = (
            f"format=yuv420p,"
            f"zoompan=z='if(lte(zoom,1.0),{z},max(1.0,zoom-0.012))':d=1,"
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

    # ─── Main Create ──────────────────────────────────────────────
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        total_audio = audio_data.get('total_duration', 0)
        print(f"\n  🎬 VideoAssembler | Audio: {total_audio:.1f}s | Words: {len(word_timings)}")

        # Sync segment durations to audio
        if total_audio > 0 and script_segments:
            non_pause_dur = sum(s.get('duration', 0) for s in script_segments if not s.get('is_pause'))
            pause_dur = sum(s.get('duration', 0) for s in script_segments if s.get('is_pause'))
            speech_audio = total_audio - pause_dur
            if non_pause_dur > 0:
                ratio = speech_audio / non_pause_dur
                for s in script_segments:
                    if not s.get('is_pause'):
                        s['duration'] = round(s['duration'] * ratio, 3)
                print(f"  🔧 Duration ratio: {ratio:.2f}")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        footage_dir = os.path.join("output", "footage")

        # Build video segments
        print(f"  🎬 Building {len(script_segments)} segments...")
        segment_files = []
        footage_idx = 0

        for i, seg in enumerate(script_segments):
            duration = seg.get('duration', 2.0)
            seg_type = seg.get('type', 'story')
            is_pause = seg.get('is_pause', False)

            if is_pause:
                # Black frame for pause duration
                black = self._color_bg_segment('pause', duration, temp_dir, i)
                if black:
                    segment_files.append(black)
                continue

            # Try footage first
            clip_file = os.path.join(footage_dir, f"clip_{footage_idx}.mp4")
            has_footage = os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000

            if has_footage:
                out = self._fast_cut_segment(clip_file, duration, temp_dir, i)
                if out:
                    segment_files.append(out)
                    footage_idx += 1
                    continue

            # Fallback color bg
            out = self._color_bg_segment(seg_type, duration, temp_dir, i)
            if out:
                segment_files.append(out)
            footage_idx += 1

        if not segment_files:
            raise Exception("No segments created!")

        # Concat segments
        print(f"  🔗 Concat {len(segment_files)} segments...")
        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{sf}'\n")

        video_raw = os.path.join(temp_dir, "video_raw.mp4")
        audio_path = audio_data.get("final_audio", "")

        if audio_path and not os.path.exists(audio_path):
            audio_dir = os.path.join("output", "audio")
            if os.path.exists(audio_dir):
                mp3s = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
                if mp3s:
                    audio_path = os.path.join(audio_dir, max(mp3s, key=lambda x: os.path.getsize(os.path.join(audio_dir, x))))

        has_audio = audio_path and os.path.exists(audio_path)

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        ]
        if has_audio:
            concat_cmd += ["-i", audio_path,
                          "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                          "-r", str(self.fps), "-c:a", "aac", "-b:a", "192k",
                          "-ar", "44100", "-ac", "2", "-shortest", "-movflags", "+faststart"]
        else:
            concat_cmd += ["-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                          "-r", str(self.fps), "-movflags", "+faststart"]
        concat_cmd.append(video_raw)

        r = subprocess.run(concat_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ❌ Concat error: {r.stderr[-200:]}")
        if not os.path.exists(video_raw):
            raise Exception("Video concat failed")

        # Burn captions
        print(f"  📝 Burning captions...")
        ass_path = os.path.join(temp_dir, "subs.ass")
        self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE)
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        r = subprocess.run([
            "ffmpeg", "-y", "-i", video_raw,
            "-vf", f"ass={safe_ass}",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
            "-r", str(self.fps), "-c:a", "copy", "-movflags", "+faststart",
            output_path
        ], capture_output=True, text=True)

        if r.returncode != 0 or not os.path.exists(output_path):
            print(f"    ⚠️ Captions failed, saving without")
            shutil.copy(video_raw, output_path)

        if os.path.exists(output_path):
            size = os.path.getsize(output_path) / (1024*1024)
            probe = subprocess.run([
                "ffprobe", "-v", "error",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1", output_path
            ], capture_output=True, text=True)
            info = dict(l.split('=',1) for l in probe.stdout.splitlines() if '=' in l)
            dur = float(info.get('duration', 0))
            print(f"\n  ✅ FINAL: {output_path}")
            print(f"  📐 {info.get('width')}x{info.get('height')} @ {info.get('r_frame_rate')}fps")
            print(f"  ⏱️  {dur:.1f}s {'✅' if 40<=dur<=55 else '⚠️'} | {size:.1f}MB")
        else:
            raise Exception("Final video not created")

        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_path
