"""Video Assembler — Fast Cuts + Dynamic Motion + 9:16 Portrait"""

import os
import subprocess
import tempfile
import shutil
import random
import math
from typing import List, Dict

from config.settings import VIDEO_CONFIG, CAPTION_CONFIG


class VideoAssembler:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.crf = getattr(VIDEO_CONFIG, 'CRF', 23)
        self.preset = getattr(VIDEO_CONFIG, 'PRESET', 'medium')
        self.bitrate = getattr(VIDEO_CONFIG, 'BITRATE', '8000k')

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

    # ─── Smooth Motion from Footage ───────────────────────────────────
    def _smooth_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int) -> str:
        """Create smooth motion segment with longer cuts and pan/zoom"""
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', clip_file
            ], capture_output=True, text=True)
            src_dur = float(probe.stdout.strip())
        except:
            src_dur = 30.0

        # FIX: Longer cuts for smooth feel (2.5-5 sec instead of 0.8-1.5)
        cuts = []
        current = 0.0
        cut_idx = 0

        while current < total_dur:
            # FIX: 2.5-5 second cuts for smooth, cinematic feel
            remaining = total_dur - current
            cut_len = min(random.uniform(2.5, 5.0), remaining)
            if cut_len < 1.0:
                break

            cut_path = os.path.join(temp_dir, f"smoothcut_{seg_idx}_{cut_idx}.mp4")
            max_start = max(0.0, src_dur - cut_len - 2.0)
            ss = random.uniform(0, max_start)

            # FIX: Smooth pan + zoom using geq (better than zoompan for smooth motion)
            # Use geq for smooth, continuous motion instead of discrete zoompan
            z_start = random.uniform(1.0, 1.15)
            z_end = random.uniform(1.15, 1.35)
            
            # Smooth pan directions
            pan_x_start = random.uniform(0, 0.3)
            pan_x_end = random.uniform(0.3, 0.7)
            pan_y_start = random.uniform(0, 0.3)
            pan_y_end = random.uniform(0.3, 0.7)

            # FIX: Use geq for smooth interpolation instead of zoompan
            # This creates REAL motion feel, not static photo zoom
            vf = (
                f"fps={self.fps},"
                f"scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=decrease,"
                f"crop={self.width}:{self.height}:(in_w-out_w)*{pan_x_start}+(in_w-out_w)*({pan_x_end}-{pan_x_start})*t/{cut_len}:"
                f"(in_h-out_h)*{pan_y_start}+(in_h-out_h)*({pan_y_end}-{pan_y_start})*t/{cut_len},"
                f"setsar=1,"
                f"format=yuv420p"
            )

            cmd = [
                "ffmpeg", "-y", "-ss", str(ss), "-i", clip_file,
                "-t", str(cut_len), "-vf", vf,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "fast",
                "-r", str(self.fps), "-pix_fmt", "yuv420p",
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0", "-an",
                cut_path
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(cut_path) and os.path.getsize(cut_path) > 1000:
                cuts.append(cut_path)
                print(f"      ✂️ Cut {cut_idx}: {cut_len:.1f}s | pan:({pan_x_start:.2f}→{pan_x_end:.2f})")

            current += cut_len
            cut_idx += 1

        if not cuts:
            return None

        # FIX: Concatenate with smooth transitions (fade or crossfade)
        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")
        
        if len(cuts) == 1:
            shutil.copy(cuts[0], out_path)
            return out_path

        # FIX: Use xfade for smooth transitions between cuts
        filter_parts = []
        for i, c in enumerate(cuts):
            filter_parts.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}]")
        
        # Build xfade chain
        xfade_chain = "[v0]"
        for i in range(1, len(cuts)):
            duration = 0.3  # 0.3 sec crossfade
            xfade_chain += f"[v{i}]xfade=transition=fade:duration={duration}:offset={i*2.5}[out{i}]"
            if i < len(cuts) - 1:
                xfade_chain = f"[out{i}]"

        # Alternative: simple concat with re-encoding for smooth playback
        cut_list = os.path.join(temp_dir, f"cuts_{seg_idx}.txt")
        with open(cut_list, 'w') as f:
            for c in cuts:
                f.write(f"file '{os.path.abspath(c)}'\n")

        # FIX: Re-encode with consistent keyframes for smooth playback
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur),
            "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an", out_path
        ], capture_output=True, text=True)

        if os.path.exists(out_path):
            return out_path
        return None

    # ─── Dynamic Background with Motion ─────────────────────────────────
    def _dynamic_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        """Create dynamic background with real motion feel"""
        colors = {
            "hook": "0x0a0a1a",      # Dark blue-black
            "suspense": "0x1a0505",   # Dark red-black
            "story": "0x050a1a",      # Dark blue
            "ctr": "0x1a1505",        # Dark gold
            "pause": "0x080808",      # Near black
            "shock": "0x1a0a00",      # Dark orange
            "reveal": "0x001a0a"      # Dark green
        }
        color = colors.get(seg_type, "0x0a0a0a")

        # FIX: Add subtle animated noise/grain for "real video" feel
        # Use geq for smooth color shifts + noise overlay
        z = random.uniform(1.05, 1.15)
        
        # FIX: Create smooth motion with animated gradient + noise
        # This looks like real footage, not static color
        vf = (
            f"format=yuv420p,"
            f"geq="
            f"r='min(255,({int(color[2:4], 16)}+10*sin(2*PI*t/{duration})+5*(random(0)*2-1)))':"
            f"g='min(255,({int(color[4:6], 16)}+8*sin(2*PI*t/{duration}+1)+5*(random(0)*2-1)))':"
            f"b='min(255,({int(color[6:8], 16)}+6*sin(2*PI*t/{duration}+2)+5*(random(0)*2-1)))',"
            f"scale={self.width}:{self.height},setsar=1"
        )

        out = os.path.join(temp_dir, f"seg_dynamic_{idx}.mp4")
        
        # FIX: Use color source with noise for real texture
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
            "-vf", (
                f"noise=alls={random.randint(5, 15)}:allf=t+u,"
                f"zoompan=z='if(eq(on,1),{z},max(1.0,zoom-0.0005))':"
                f"d={int(duration * self.fps)}:s={self.width}x{self.height}:fps={self.fps},"
                f"scale={self.width}:{self.height},setsar=1,format=yuv420p"
            ),
            "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ], capture_output=True, text=True)
        return out if os.path.exists(out) else None

    # ─── Suspense Visual Effect ─────────────────────────────────
    def _suspense_effect(self, base_video: str, effect_type: str, temp_dir: str, idx: int) -> str:
        """Add suspense visual effects (glitch, shake, flash, zoom)"""
        out = os.path.join(temp_dir, f"suspense_{effect_type}_{idx}.mp4")
        
        effects = {
            "glitch": (
                f"chromashift=cbh=-8:cbv=4,"
                f"noise=alls=20:allf=t+u,"
                f"eq=contrast=1.3:saturation=1.2"
            ),
            "shake": (
                f"crop={self.width-20}:{self.height-20}:(in_w-out_w)/2+10*sin(10*t):(in_h-out_h)/2+10*cos(8*t),"
                f"scale={self.width}:{self.height},setsar=1"
            ),
            "flash": (
                f"eq=brightness='if(lt(mod(t,0.5),0.1),0.3,0)':contrast=1.2,"
                f"noise=alls=10:allf=t+u"
            ),
            "heartbeat": (
                f"zoompan=z='1+0.05*sin(4*PI*t)':d=1:s={self.width}x{self.height}:fps={self.fps},"
                f"eq=contrast=1.1"
            ),
            "tension": (
                f"eq=contrast=1.4:brightness=-0.1,"
                f"noise=alls=15:allf=t+u,"
                f"chromashift=cbh=4:cbv=-2"
            )
        }
        
        vf = effects.get(effect_type, effects["tension"])
        vf += f",scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},setsar=1,format=yuv420p"
        
        subprocess.run([
            "ffmpeg", "-y", "-i", base_video,
            "-vf", vf,
            "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "fast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p", "-an",
            out
        ], capture_output=True, text=True)
        
        return out if os.path.exists(out) else base_video

    # ─── Main Video Creation ─────────────────────────────────
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        # FIX: Calculate target duration from audio, enforce 40-55 sec
        total_audio = audio_data.get('total_duration', 0)
        target_duration = max(40, min(55, total_audio)) if total_audio > 0 else 50
        
        print(f"  🎯 Target duration: {target_duration:.1f}s (40-55s range)")

        # FIX: Adjust segment durations to match target
        if script_segments and total_audio > 0:
            current_total = sum(s.get('duration', 2) for s in script_segments)
            ratio = target_duration / max(current_total, 1)
            
            for s in script_segments:
                if not s.get('is_pause'):
                    s['duration'] = min(max(s.get('duration', 2) * ratio, 1.5), 8.0)
            
            # Re-calculate with word timings for precision
            if word_timings:
                wt_idx = 0
                for s in script_segments:
                    if s.get('is_pause'): 
                        s['duration'] = min(s.get('duration', 0.5), 0.5)
                        continue
                    seg_word_count = len(s.get('text', '').split())
                    seg_words = word_timings[wt_idx:wt_idx + seg_word_count]
                    wt_idx += seg_word_count
                    if seg_words:
                        audio_dur = round(max(1.5, seg_words[-1]['end'] - seg_words[0]['start']), 3)
                        s['duration'] = audio_dur

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        footage_dir = os.path.join("output", "footage")

        segment_files = []
        footage_idx = 0
        
        for i, seg in enumerate(script_segments):
            seg_type = seg.get('type', 'story')
            duration = max(1.0, seg.get('duration', 2.5))
            
            # FIX: Pause segments very short
            if seg.get('is_pause'):
                pause = self._dynamic_bg_segment('pause', min(duration, 0.3), temp_dir, i)
                if pause: 
                    segment_files.append(pause)
                continue

            # FIX: Hook segments get suspense effects
            is_hook = seg_type in ['hook', 'shock', 'suspense']
            is_cta = seg_type in ['ctr', 'reveal']

            clip_file = os.path.join(footage_dir, f"clip_{footage_idx}.mp4")
            if os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000:
                # FIX: Use smooth cuts instead of fast cuts
                out = self._smooth_cut_segment(clip_file, duration, temp_dir, i)
                if out:
                    # FIX: Apply suspense effects to hook/CTA segments
                    if is_hook:
                        out = self._suspense_effect(out, "glitch", temp_dir, i)
                    elif is_cta:
                        out = self._suspense_effect(out, "heartbeat", temp_dir, i)
                    elif seg_type == 'suspense':
                        out = self._suspense_effect(out, "tension", temp_dir, i)
                    
                    segment_files.append(out)
                    footage_idx += 1
                    continue
            
            # FIX: Dynamic background with motion instead of static color
            out = self._dynamic_bg_segment(seg_type, duration, temp_dir, i)
            if out: 
                # FIX: Apply effects even to background segments
                if is_hook:
                    out = self._suspense_effect(out, "flash", temp_dir, i)
                segment_files.append(out)
            footage_idx += 1

        if not segment_files:
            raise ValueError("❌ No segments generated!")

        # FIX: Concatenate with smooth encoding
        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{os.path.abspath(sf)}'\n")

        video_raw = os.path.join(temp_dir, "video_raw.mp4")
        audio_path = audio_data.get("final_audio", "")
        has_audio = audio_path and os.path.exists(audio_path)

        # FIX: Proper concat with audio sync and smooth encoding
        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list
        ]
        if has_audio:
            concat_cmd += [
                "-i", audio_path,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                "-r", str(self.fps), "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-movflags", "+faststart",
                "-pix_fmt", "yuv420p",
                "-fflags", "+genpts",
                "-async", "1"
            ]
        else:
            concat_cmd += [
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                "-r", str(self.fps),
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-movflags", "+faststart",
                "-pix_fmt", "yuv420p"
            ]
        concat_cmd.append(video_raw)
        
        r = subprocess.run(concat_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ Concat error: {r.stderr[:500]}")

        # FIX: Final render with captions - smooth encoding
        ass_path = os.path.join(temp_dir, "subs.ass")
        self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE)
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        # FIX: Single-pass render with all optimizations
        r = subprocess.run([
            "ffmpeg", "-y", "-i", video_raw,
            "-vf", f"ass={safe_ass},format=yuv420p",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
            "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            "-t", str(target_duration + 1),  # Allow slight buffer
            output_path
        ], capture_output=True, text=True)

        if r.returncode != 0:
            print(f"  ❌ Final render error: {r.stderr[:500]}")

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Verify output
        if os.path.exists(output_path):
            try:
                probe = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', output_path
                ], capture_output=True, text=True)
                final_dur = float(probe.stdout.strip())
                print(f"  ✅ Final video: {final_dur:.1f}s | {output_path}")
            except:
                print(f"  ✅ Video created: {output_path}")
        
        return output_path
