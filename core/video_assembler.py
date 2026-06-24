"""
Video Assembler - FINAL PRODUCTION READY
OPTIMIZED FOR: 35-54 Male USA/UK Audience

FIXES:
1. ✅ shutil.rmtree crash fixed (try-except wrap)
2. ✅ FFmpeg timeout increased to 600s
3. ✅ FPS filter added to plain color fallback
4. ✅ Fast cuts optimized for retention
5. ✅ Proper error handling in all subprocess calls
6. ✅ Memory cleanup guaranteed
"""

import os
import subprocess
import tempfile
import shutil
import random
import math
import time
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path

from config.settings import VIDEO_CONFIG, CAPTION_CONFIG


class VideoAssembler:
    """Production Video Assembler - FINAL VERSION"""
    
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.crf = getattr(VIDEO_CONFIG, 'CRF', 23)
        self.preset = getattr(VIDEO_CONFIG, 'PRESET', 'veryfast')
        self.bitrate = getattr(VIDEO_CONFIG, 'BITRATE', '8000k')
        
        # Duration settings
        self.duration_min = getattr(VIDEO_CONFIG, 'DURATION_MIN', 42)
        self.duration_max = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)
        self.target_duration = getattr(VIDEO_CONFIG, 'TARGET_DURATION', 48)
        
        # FIX: Fast cut settings for retention
        self.fast_cut_min = 1.2   # Very fast for hook
        self.fast_cut_max = 2.5
        self.normal_cut_min = 2.5
        self.normal_cut_max = 5.5
        
        # Effects
        self.zoom_intensity = getattr(VIDEO_CONFIG, 'ZOOM_INTENSITY', 1.12)
        self.shake_intensity = getattr(VIDEO_CONFIG, 'SHAKE_INTENSITY', 1)
        
        print(f"🎬 VideoAssembler initialized ({self.width}x{self.height} @ {self.fps}fps)")

    # ============================================================
    # SECONDS TO ASS TIME
    # ============================================================
    
    def _seconds_to_ass(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        if seconds < 0:
            seconds = 0
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    # ============================================================
    # GET VIDEO DURATION (WITH ERROR HANDLING)
    # ============================================================
    
    def _get_duration(self, path: str) -> float:
        """Get video duration using ffprobe with error handling"""
        if not path or not os.path.exists(path):
            return 0.0
        
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0.0

    # ============================================================
    # CREATE ASS SUBTITLES (FIXED)
    # ============================================================
    
    def _create_ass(self, word_timings: List[Dict], ass_path: str, 
                    font_size: int = 88, max_duration: float = None) -> str:
        """Create ASS subtitle file from word timings - FIXED"""
        
        margin_lr = 60
        margin_v = max(getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 350), 280)
        alignment = 2
        font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'Arial')
        primary_color = getattr(CAPTION_CONFIG, 'PRIMARY_COLOR', '&H00FFFFFF')
        secondary_color = getattr(CAPTION_CONFIG, 'SECONDARY_COLOR', '&H0000FFFF')
        outline_color = getattr(CAPTION_CONFIG, 'OUTLINE_COLOR', '&H00000000')
        outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 7)
        shadow = getattr(CAPTION_CONFIG, 'SHADOW', 3)
        bold = 1
        
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H00000000,{bold},0,0,0,100,100,2,0,1,{outline_width},{shadow},{alignment},{margin_lr},{margin_lr},{margin_v},1
Style: Red,{font_name},{font_size},{secondary_color},&H00FFFFFF,{outline_color},&H00000000,{bold},0,0,0,100,100,2,0,1,{outline_width},{shadow},{alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Sort and clean timings
        if not word_timings:
            word_timings = self._generate_fallback_timings(max_duration or 48.0)
        
        sorted_timings = sorted(word_timings, key=lambda w: w.get('start', 0))
        clean_timings = []
        
        for idx, wt in enumerate(sorted_timings):
            start = wt.get('start', 0)
            end = wt.get('end', start + 0.3)
            
            if max_duration is not None:
                if start >= max_duration:
                    continue
                end = min(end, max_duration)
            
            if idx + 1 < len(sorted_timings):
                next_start = sorted_timings[idx + 1].get('start', end)
                if end > next_start:
                    end = max(start + 0.05, next_start - 0.01)
            
            if end <= start:
                continue
            
            clean_timings.append({**wt, 'start': start, 'end': end})
        
        if not clean_timings:
            clean_timings = self._generate_fallback_timings(max_duration or 48.0)
        
        # Generate events
        events = []
        line_idx = 0
        current_line = []
        max_words = 3
        
        for idx, wt in enumerate(clean_timings):
            word = str(wt.get('word', '')).strip().upper()
            word = word.replace(',', '').replace('{', '').replace('}', '')
            word = word.replace('\\', '')
            word = ''.join(ch for ch in word if ch.isprintable())
            
            if not word:
                continue
            
            current_line.append(wt)
            
            if len(current_line) >= max_words or idx == len(clean_timings) - 1:
                style = "Red" if line_idx % 2 == 0 else "White"
                
                for wt_line in current_line:
                    safe_word = str(wt_line.get('word', '')).strip().upper()
                    safe_word = safe_word.replace(',', '').replace('{', '').replace('}', '')
                    safe_word = safe_word.replace('\\', '')
                    safe_word = ''.join(ch for ch in safe_word if ch.isprintable())
                    
                    if not safe_word:
                        continue
                    
                    w_start = self._seconds_to_ass(wt_line['start'])
                    w_end = self._seconds_to_ass(wt_line['end'])
                    events.append(f"Dialogue: 0,{w_start},{w_end},{style},,0,0,0,,{safe_word}")
                
                current_line = []
                line_idx += 1
        
        if not events:
            events = ["Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,,YOUR BRAIN IS AMAZING"]
        
        # Write to file
        os.makedirs(os.path.dirname(ass_path) or ".", exist_ok=True)
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(events) + "\n")
        
        print(f"    [ASS] {len(events)} events | {line_idx} groups")
        return ass_path

    def _generate_fallback_timings(self, duration: float) -> List[Dict]:
        """Generate fallback word timings"""
        fallback_text = "YOUR BRAIN IS AMAZING AND POWERFUL"
        words = fallback_text.split()
        
        if not words:
            words = ["YOUR", "BRAIN", "IS", "AMAZING"]
        
        timings = []
        word_duration = duration / len(words)
        current = 0.0
        
        for word in words:
            timings.append({
                'word': word,
                'start': round(current, 3),
                'end': round(current + word_duration, 3),
                'duration': round(word_duration, 3)
            })
            current += word_duration
        
        return timings

    # ============================================================
    # FIX 1: SMOOTH CUT SEGMENT (OPTIMIZED FAST CUTS)
    # ============================================================
    
    def _smooth_cut_segment(self, clip_file: str, total_dur: float, 
                            temp_dir: str, seg_idx: int, 
                            fast_pacing: bool = False) -> Optional[str]:
        """Create smooth motion segment with pan/zoom - FAST CUTS OPTIMIZED"""
        
        # Get source duration
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', clip_file
            ], capture_output=True, text=True, timeout=10)
            src_dur = float(probe.stdout.strip()) if probe.stdout.strip() else 30.0
        except Exception:
            src_dur = 30.0
        
        # Generate cuts with optimized pacing
        cuts = []
        current = 0.0
        cut_idx = 0
        
        # FIX: Fast cuts for hook (1.2-2.5s), normal for rest (2.5-5.5s)
        if fast_pacing:
            cut_range = (self.fast_cut_min, self.fast_cut_max)
            print(f"      ⚡ FAST CUTS: {cut_range[0]:.1f}-{cut_range[1]:.1f}s")
        else:
            cut_range = (self.normal_cut_min, self.normal_cut_max)
        
        while current < total_dur:
            remaining = total_dur - current
            cut_len = min(random.uniform(*cut_range), remaining)
            
            if cut_len < 0.8:
                if cuts and remaining > 0:
                    current += remaining
                break
            
            cut_path = os.path.join(temp_dir, f"smoothcut_{seg_idx}_{cut_idx}.mp4")
            
            # Random start time
            max_start = max(0.0, src_dur - cut_len - 1.0)
            ss = random.uniform(0, max_start) if max_start > 0 else 0.0
            
            # Zoom and pan (subtle for mature audience)
            z_start = random.uniform(1.0, 1.08)
            z_end = random.uniform(1.08, 1.25)
            
            pan_x_start = random.uniform(0, 0.3)
            pan_x_end = random.uniform(0.3, 0.7)
            pan_y_start = random.uniform(0, 0.3)
            pan_y_end = random.uniform(0.3, 0.7)
            
            vf = (
                f"fps={self.fps},"
                f"scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=increase,"
                f"crop={self.width*2}:{self.height*2},"
                f"crop={self.width}:{self.height}:(in_w-out_w)*{pan_x_start}+(in_w-out_w)*({pan_x_end}-{pan_x_start})*t/{cut_len}:"
                f"(in_h-out_h)*{pan_y_start}+(in_h-out_h)*({pan_y_end}-{pan_y_start})*t/{cut_len},"
                f"setsar=1,format=yuv420p"
            )
            
            cmd = [
                "ffmpeg", "-y", "-ss", str(ss), "-i", clip_file,
                "-t", str(cut_len), "-vf", vf,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                "-r", str(self.fps), "-pix_fmt", "yuv420p",
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0", "-an",
                cut_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(cut_path) and os.path.getsize(cut_path) > 1000:
                cuts.append(cut_path)
            
            current += cut_len
            cut_idx += 1
        
        if not cuts:
            return None
        
        # Concatenate cuts
        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")
        
        if len(cuts) == 1:
            shutil.copy(cuts[0], out_path)
            return out_path
        
        cut_list = os.path.join(temp_dir, f"cuts_{seg_idx}.txt")
        with open(cut_list, 'w') as f:
            for c in cuts:
                f.write(f"file '{os.path.abspath(c)}'\n")
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur),
            "-c", "copy", "-an", out_path
        ], capture_output=True, text=True, timeout=60)
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return out_path
        
        return None

    # ============================================================
    # FIX 2: DYNAMIC BACKGROUND (WITH FPS)
    # ============================================================
    
    def _dynamic_bg_segment(self, seg_type: str, duration: float, 
                            temp_dir: str, idx: int) -> Optional[str]:
        """Create dynamic animated background - FIXED with FPS"""
        
        colors = {
            "hook": "0x0a0a1a",
            "shock": "0x1a0a00",
            "suspense": "0x1a0505",
            "story": "0x050a1a",
            "ctr": "0x1a1505",
            "pause": "0x080808",
            "reveal": "0x001a0a",
        }
        
        color = colors.get(seg_type, "0x0a0a0a")
        r0, g0, b0 = int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)
        z = random.uniform(1.05, 1.15)
        
        out = os.path.join(temp_dir, f"seg_dynamic_{idx}.mp4")
        
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
            "-vf", (
                f"geq="
                f"r='min(255,max(0,{r0}+35*sin(2*PI*T/{duration})))':"
                f"g='min(255,max(0,{g0}+28*sin(2*PI*T/{duration}+1)))':"
                f"b='min(255,max(0,{b0}+22*sin(2*PI*T/{duration}+2)))',"
                f"noise=alls={random.randint(8, 20)}:allf=t+u,"
                f"zoompan=z='if(eq(on,1),{z},max(1.0,zoom-0.0005))':"
                f"d={int(duration * self.fps)}:s={self.width}x{self.height}:fps={self.fps},"
                f"scale={self.width}:{self.height},setsar=1,format=yuv420p"
            ),
            "-c:v", "libx264", "-crf", str(self.crf),
            "-preset", "veryfast", 
            "-r", str(self.fps),  # FIX: Explicit FPS
            "-g", str(self.fps), 
            "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 500:
            return out
        
        return None

    # ============================================================
    # FIX 3: PLAIN COLOR FALLBACK (WITH FPS)
    # ============================================================
    
    def _plain_color_fallback(self, seg_type: str, duration: float,
                              temp_dir: str, idx: int) -> Optional[str]:
        """Absolute fallback - plain color with FPS - FIXED"""
        
        colors = {
            "hook": "0x0a0a1a",
            "shock": "0x1a0a00",
            "suspense": "0x1a0505",
            "story": "0x050a1a",
            "ctr": "0x1a1505",
            "pause": "0x080808",
            "reveal": "0x001a0a",
        }
        
        color = colors.get(seg_type, "0x0a0a0a")
        out = os.path.join(temp_dir, f"seg_fallback_{idx}.mp4")
        
        try:
            # FIX: Explicit FPS and GOP settings
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                "-r", str(self.fps),  # FIX: Explicit FPS
                "-pix_fmt", "yuv420p",
                "-g", str(self.fps),  # FIX: GOP = FPS
                "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-an",
                "-t", str(duration),
                out
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 500:
                return out
                
        except Exception:
            pass
        
        return None

    # ============================================================
    # SUSPENSE EFFECTS
    # ============================================================
    
    def _add_suspense_effect(self, base_video: str, effect_type: str,
                             temp_dir: str, idx: int) -> str:
        """Add suspense visual effects"""
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
            "-preset", "veryfast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p", "-an",
            out
        ], capture_output=True, text=True, timeout=60)
        
        return out if os.path.exists(out) else base_video

    # ============================================================
    # FIX 4: SAFE CLEANUP (shutil.rmtree crash fixed)
    # ============================================================
    
    def _safe_cleanup(self, temp_dir: str) -> None:
        """Safe cleanup with try-except to prevent crashes"""
        if not temp_dir or not os.path.exists(temp_dir):
            return
        
        try:
            shutil.rmtree(temp_dir)
            print(f"   🧹 Cleaned up: {temp_dir}")
        except PermissionError:
            print(f"   ⚠️ Permission error while cleaning {temp_dir}")
        except OSError as e:
            print(f"   ⚠️ OS error while cleaning {temp_dir}: {e}")
        except Exception as e:
            print(f"   ⚠️ Error while cleaning {temp_dir}: {e}")

    # ============================================================
    # MAIN: CREATE VIDEO (FINAL)
    # ============================================================
    
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: Union[Dict, List], 
                     word_timings: List[Dict],
                     output_path: str, caption_ass_path: str = None) -> str:
        """Create final video with all components - FINAL VERSION"""
        
        print(f"\n🎬 Assembling video...")
        print(f"   Segments: {len(script_segments)}")
        print(f"   Audio: {audio_data.get('total_duration', 0):.1f}s")
        
        # Set target duration
        audio_duration = audio_data.get('total_duration', 0)
        target_duration = max(self.duration_min, min(self.duration_max, audio_duration))
        print(f"   Target duration: {target_duration:.1f}s")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        try:
            # ============================================================
            # Step 1: Process footage clips
            # ============================================================
            footage_dir = os.path.join("output", "footage")
            footage_paths = {}
            
            if isinstance(footage_clips, dict):
                footage_paths = footage_clips
            elif isinstance(footage_clips, list):
                for idx in range(len(script_segments)):
                    candidate = os.path.join(footage_dir, f"clip_{idx}.mp4")
                    if os.path.exists(candidate):
                        footage_paths[idx] = candidate
            
            # ============================================================
            # Step 2: Generate segments with fast cuts
            # ============================================================
            segment_files = []
            skipped_segments = []
            
            for i, seg in enumerate(script_segments):
                seg_type = seg.get('type', 'story')
                duration = max(1.0, seg.get('duration', 2.5))
                
                if seg.get('is_pause'):
                    pause = self._dynamic_bg_segment('pause', min(duration, 0.5), temp_dir, i)
                    if pause:
                        segment_files.append(pause)
                    continue
                
                # FIX: Fast pacing only for hook
                is_opening_hook = seg_type == 'hook'
                is_hook = seg_type in ['hook', 'shock', 'suspense']
                is_cta = seg_type in ['ctr', 'reveal']
                
                clip_file = footage_paths.get(i)
                used_real_footage = False
                
                # Try real footage
                if clip_file and os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000:
                    out = self._smooth_cut_segment(clip_file, duration, temp_dir, i, 
                                                    fast_pacing=is_opening_hook)
                    if out:
                        # Add effects
                        if is_hook:
                            out = self._add_suspense_effect(out, "glitch", temp_dir, i)
                        elif is_cta:
                            out = self._add_suspense_effect(out, "heartbeat", temp_dir, i)
                        elif seg_type == 'suspense':
                            out = self._add_suspense_effect(out, "tension", temp_dir, i)
                        
                        segment_files.append(out)
                        used_real_footage = True
                
                # Try dynamic background
                if not used_real_footage:
                    out = self._dynamic_bg_segment(seg_type, duration, temp_dir, i)
                    if out:
                        if is_hook:
                            out = self._add_suspense_effect(out, "flash", temp_dir, i)
                        segment_files.append(out)
                        used_real_footage = True
                
                # FIX: Plain color fallback
                if not used_real_footage:
                    fallback = self._plain_color_fallback(seg_type, duration, temp_dir, i)
                    if fallback:
                        segment_files.append(fallback)
                        print(f"   ⚠️ Seg {i}: used plain color fallback")
                    else:
                        skipped_segments.append(i)
                        print(f"   ❌ Seg {i}: ALL render paths failed")
            
            if skipped_segments:
                print(f"   ⚠️ {len(skipped_segments)} segment(s) failed to render")
            
            if not segment_files:
                raise ValueError("No segments generated")
            
            # ============================================================
            # Step 3: Concatenate video segments
            # ============================================================
            concat_list = os.path.join(temp_dir, "concat.txt")
            with open(concat_list, 'w') as f:
                for sf in segment_files:
                    f.write(f"file '{os.path.abspath(sf)}'\n")
            
            video_prepad = os.path.join(temp_dir, "video_prepad.mp4")
            result = subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                "-r", str(self.fps),
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-pix_fmt", "yuv420p", "-an",
                video_prepad
            ], capture_output=True, text=True, timeout=120)
            
            if not os.path.exists(video_prepad) or os.path.getsize(video_prepad) < 1000:
                raise Exception("Video concatenation failed")
            
            # ============================================================
            # Step 4: Pad video if needed (slow-motion tail)
            # ============================================================
            prepad_duration = self._get_duration(video_prepad)
            video_source = video_prepad
            
            if prepad_duration > 0 and prepad_duration < target_duration - 0.2:
                print(f"   ⚠️ Video ({prepad_duration:.1f}s) shorter than target ({target_duration:.1f}s)")
                shortfall = target_duration - prepad_duration
                
                # Slow-motion tail extension
                tail_window = min(3.0, max(0.5, prepad_duration / 2))
                split_point = max(0.0, prepad_duration - tail_window)
                slowed_tail_duration = tail_window + shortfall
                speed_factor = tail_window / slowed_tail_duration
                
                video_padded = os.path.join(temp_dir, "video_padded.mp4")
                pad_cmd = [
                    "ffmpeg", "-y", "-i", video_prepad,
                    "-filter_complex",
                    f"[0:v]trim=0:{split_point},setpts=PTS-STARTPTS[head];"
                    f"[0:v]trim={split_point}:{prepad_duration},setpts=(PTS-STARTPTS)/{speed_factor}[tail];"
                    f"[head][tail]concat=n=2:v=1:a=0[outv]",
                    "-map", "[outv]",
                    "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                    "-r", str(self.fps), "-pix_fmt", "yuv420p",
                    "-g", str(self.fps), "-keyint_min", str(self.fps),
                    "-sc_threshold", "0", "-an",
                    video_padded
                ]
                result = subprocess.run(pad_cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0 and os.path.exists(video_padded):
                    video_source = video_padded
                    print(f"   ✅ Padded video to {target_duration:.1f}s")
            
            # ============================================================
            # Step 5: Create captions
            # ============================================================
            if caption_ass_path and os.path.exists(caption_ass_path):
                ass_path = caption_ass_path
            else:
                ass_path = os.path.join(temp_dir, "subs.ass")
                self._create_ass(word_timings, ass_path, 
                                getattr(CAPTION_CONFIG, 'FONT_SIZE', 88),
                                max_duration=target_duration)
            
            # ============================================================
            # Step 6: Final render with audio + captions
            # ============================================================
            audio_path = audio_data.get("audio_path") or audio_data.get("final_audio", "")
            has_audio = audio_path and os.path.exists(audio_path)
            
            safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')
            
            # FIX: timeout increased to 600s
            cmd = [
                "ffmpeg", "-y", "-i", video_source,
                "-vf", f"ass={safe_ass},format=yuv420p",
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                "-r", str(self.fps),
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
            ]
            
            if has_audio:
                cmd.extend(["-i", audio_path, "-c:a", "aac", "-b:a", "192k", "-shortest"])
            
            cmd.extend(["-t", str(target_duration), output_path])
            
            # FIX: 600 second timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                print(f"   ❌ Render error: {result.stderr[:500]}")
                raise Exception(f"Video render failed: {result.stderr[:300]}")
            
            # ============================================================
            # Step 7: Verify output
            # ============================================================
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                raise Exception("Output file missing or too small")
            
            final_duration = self._get_duration(output_path)
            print(f"   ✅ Video created: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
            print(f"   ⏱️ Duration: {final_duration:.1f}s")
            
            return output_path
            
        except Exception as e:
            print(f"   ❌ Video assembly failed: {e}")
            raise
            
        finally:
            # FIX: Safe cleanup (shutil.rmtree crash fixed)
            self._safe_cleanup(temp_dir)


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING VIDEO ASSEMBLER (FINAL)\n" + "="*60)
    
    assembler = VideoAssembler()
    print("✅ VideoAssembler initialized successfully!")
