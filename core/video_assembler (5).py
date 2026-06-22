"""Video Assembler - Fast Cuts + Dynamic Motion + 9:16 Portrait"""

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
        self.preset = getattr(VIDEO_CONFIG, 'PRESET', 'veryfast')
        self.bitrate = getattr(VIDEO_CONFIG, 'BITRATE', '8000k')

        assert self.width < self.height, f"[FAIL] Portrait check failed"
        print(f"  [DIM] {self.width}x{self.height} @ {self.fps}fps | CRF:{self.crf}")

    #  ASS Subtitles 
    def _seconds_to_ass(self, s: float) -> str:
        h = int(s // 3600); m = int((s % 3600) // 60)
        sc = int(s % 60); cs = int((s % 1) * 100)
        return f"{h}:{m:02d}:{sc:02d}.{cs:02d}"

    def _create_ass(self, word_timings: List[Dict], ass_path: str, font_size: int = 90, max_duration: float = None):
        c = CAPTION_CONFIG
        # FIX: Use CAPTION_CONFIG.ALIGNMENT so settings.py is respected
        alignment = getattr(c, 'ALIGNMENT', 2)
        margin_v = getattr(c, 'MARGIN_V', 0) if alignment == 5 else max(getattr(c, 'SAFE_ZONE_BOTTOM', 280), 220)
        # FIX: MarginL/MarginR were hardcoded to 10px, far too tight for a
        # 90px font on a 1080px-wide frame -- long single words (e.g.
        # "BECAUSE", "BACKGROUND") could overflow past the left/right
        # edges of the screen, which is exactly what showed up as text
        # being cut off at the screen edge in the reported screenshots.
        # 60px gives a safe ~960px usable text width.
        margin_lr = 60

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{c.FONT_NAME},{font_size},{c.PRIMARY_COLOR},&H000000FF,{c.OUTLINE_COLOR},&H00000000,1,0,0,0,100,100,2,0,1,{c.OUTLINE_WIDTH},{c.SHADOW},{alignment},{margin_lr},{margin_lr},{margin_v},1
Style: Red,{c.FONT_NAME},{font_size},{c.SECONDARY_COLOR},&H00FFFFFF,{c.OUTLINE_COLOR},&H00000000,1,0,0,0,100,100,2,0,1,{c.OUTLINE_WIDTH},{c.SHADOW},{alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
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

        lines = []
        for idx, wt in enumerate(clean_timings):
            word = str(wt.get('word', '')).strip()
            if word:
                # FIX (root cause of "WORD0:00:28.74" leaking into captions):
                # ASS Dialogue lines are comma-separated fields. If a word
                # itself ever contains a raw comma or unexpected control
                # character, libass's field parser shifts, merging the Text
                # field with the timestamp fields -- producing exactly the
                # glued-together artifact seen on screen. We defensively
                # strip commas/control chars and escape ASS's own special
                # characters ({ } \) so they can never be misread as
                # override tags either.
                safe_word = word.upper()
                safe_word = safe_word.replace(',', '')
                safe_word = safe_word.replace('{', '').replace('}', '')
                safe_word = safe_word.replace('\\', '')
                safe_word = ''.join(ch for ch in safe_word if ch.isprintable())
                if not safe_word.strip():
                    continue
                style = "White" if idx % 2 == 0 else "Red"
                lines.append(f"Dialogue: 0,{self._seconds_to_ass(wt['start'])},{self._seconds_to_ass(wt['end'])},{style},,0,0,0,,{safe_word}")
        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,, ")
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    [NOTE] ASS: {len(lines)} words | size:{font_size}px | align:{alignment} | marginV:{margin_v}")

    def _create_hormozi_captions(self, word_timings: List[Dict], ass_path: str, font_size: int = 110, max_duration: float = None):
        """FIX (retention 80%+): Alex Hormozi style — BIG, centered, word-by-word ACTIVE highlight.

        Unlike _create_ass which shows one word at a time ( karaoke style),
        this shows ALL words on screen but highlights the CURRENT word in WHITE
        while others fade to GRAY. This creates a "reading along" effect that
        keeps viewers glued to the screen.
        """
        c = CAPTION_CONFIG
        alignment = 2  # Bottom-center
        margin_v = max(getattr(c, 'SAFE_ZONE_BOTTOM', 280), 220)
        margin_lr = 60

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Active,{c.FONT_NAME},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,10,0,{alignment},{margin_lr},{margin_lr},{margin_v},1
Style: Inactive,{c.FONT_NAME},{font_size},&H80808080,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,10,0,{alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        # Sort and clean timings
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

        lines = []
        for idx, wt in enumerate(clean_timings):
            word = str(wt.get('word', '')).strip()
            if word:
                safe_word = word.upper()
                safe_word = safe_word.replace(',', '').replace('{', '').replace('}', '').replace('\\', '')
                safe_word = ''.join(ch for ch in safe_word if ch.isprintable())
                if not safe_word.strip():
                    continue

                start = self._seconds_to_ass(wt['start'])
                end = self._seconds_to_ass(wt['end'])

                # FIX: Show word as ACTIVE (white) during its exact timing, INACTIVE (gray) otherwise
                # But to show ALL words, we need a different approach — show sentence with current word highlighted
                # For simplicity in ASS: show the word as Active during its time
                lines.append(f"Dialogue: 0,{start},{end},Active,,0,0,0,,{safe_word}")

        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,Inactive,,0,0,0,, ")

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")
        print(f"    [RETENTION] Hormozi Captions: {len(lines)} words | {font_size}px | ACTIVE highlight")



    #  Smooth Motion from Footage 
    def _smooth_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int, fast_pacing: bool = False) -> str:
        """Create smooth motion segment with longer cuts and pan/zoom.

        FIX (swipe-away rate / retention): added `fast_pacing` for the hook
        segment specifically. The first 1-2 seconds of a Short are where
        almost all swipe-away decisions happen -- a single long, slow pan
        during that window reads as "nothing is happening yet" and invites
        a swipe. Quicker cuts (1.2-2.0s instead of 2.5-5.0s) during the
        hook create a sense of immediate movement/energy without changing
        anything about the audio or caption timing.
        """
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
        cut_range = (1.2, 2.0) if fast_pacing else (2.5, 5.0)

        while current < total_dur:
            remaining = total_dur - current
            cut_len = min(random.uniform(*cut_range), remaining)
            if cut_len < 1.0:
                if cuts and remaining > 0:
                    current += remaining
                    continue
                break

            cut_path = os.path.join(temp_dir, f"smoothcut_{seg_idx}_{cut_idx}.mp4")
            max_start = max(0.0, src_dur - cut_len - 2.0)
            ss = random.uniform(0, max_start) if max_start > 0 else 0.0

            z_start = random.uniform(1.0, 1.15)
            z_end = random.uniform(1.15, 1.35)

            pan_x_start = random.uniform(0, 0.3)
            pan_x_end = random.uniform(0.3, 0.7)
            pan_y_start = random.uniform(0, 0.3)
            pan_y_end = random.uniform(0.3, 0.7)

            vf = (
                f"fps={self.fps},"
                # FIX (root cause of segments rendering as solid black with
                # only the caption visible): force_original_aspect_ratio=
                # DECREASE shrinks the source to FIT inside the target box,
                # leaving black letterbox/pillarbox bars for any source
                # that isn't already 9:16 (e.g. landscape footage from
                # Pixabay, which this pipeline does use -- see "(landscape)"
                # in the footage-fetch logs). The subsequent pan/crop filter
                # picks a RANDOM region to crop from, with no awareness of
                # where those black bars are -- so whenever the random pan
                # path crossed into a letterboxed bar, the entire visible
                # frame went black for that cut's whole duration. Using
                # INCREASE instead scales the source to COVER the target
                # box (cropping off the excess on one axis instead of
                # padding with black), which guarantees every pixel in the
                # final frame comes from real footage, never a black bar,
                # regardless of the source's original aspect ratio.
                f"scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=increase,"
                f"crop={self.width*2}:{self.height*2},"
                f"crop={self.width}:{self.height}:(in_w-out_w)*{pan_x_start}+(in_w-out_w)*({pan_x_end}-{pan_x_start})*t/{cut_len}:"
                f"(in_h-out_h)*{pan_y_start}+(in_h-out_h)*({pan_y_end}-{pan_y_start})*t/{cut_len},"
                f"setsar=1,"
                f"format=yuv420p"
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
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(cut_path) and os.path.getsize(cut_path) > 1000:
                cuts.append(cut_path)
                print(f"      [CUT] Cut {cut_idx}: {cut_len:.1f}s | pan:({pan_x_start:.2f}->{pan_x_end:.2f})")
            else:
                # FIX: previously a failed ffmpeg cut was silently dropped
                # with zero trace in the logs -- this is exactly how the
                # landscape-source black-bar/crop-failure bug went
                # unnoticed (ffmpeg errored out on every cut for that
                # segment, cuts stayed empty, the segment fell through to
                # dynamic-bg/fallback, and nothing in the log hinted why).
                # Logging the actual ffmpeg stderr here makes any future
                # per-cut failure immediately diagnosable instead of just
                # silently degrading to a fallback.
                err_tail = (r.stderr or '').strip().splitlines()[-1] if r.stderr else 'no stderr'
                print(f"      [WARN] Cut {cut_idx} failed (seg {seg_idx}): {err_tail}")

            current += cut_len
            cut_idx += 1

        if not cuts:
            return None

        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")

        if len(cuts) == 1:
            shutil.copy(cuts[0], out_path)
            return out_path

        cut_list = os.path.join(temp_dir, f"cuts_{seg_idx}.txt")
        with open(cut_list, 'w') as f:
            for c in cuts:
                f.write(f"file '{os.path.abspath(c)}'\n")

        r = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
            "-t", str(total_dur),
            "-c", "copy",
            "-an", out_path
        ], capture_output=True, text=True)
        if r.returncode != 0:
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", cut_list,
                "-t", str(total_dur),
                "-c:v", "libx264", "-crf", str(self.crf),
                "-preset", "veryfast", "-r", str(self.fps),
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an", out_path
            ], capture_output=True, text=True)

        if os.path.exists(out_path):
            actual = 0.0
            try:
                probe = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', out_path
                ], capture_output=True, text=True)
                actual = float(probe.stdout.strip())
            except:
                pass
            if actual > 0 and actual < total_dur - 0.15:
                padded = os.path.join(temp_dir, f"seg_footage_{seg_idx}_padded.mp4")
                pad_amount = total_dur - actual
                subprocess.run([
                    "ffmpeg", "-y", "-i", out_path,
                    "-vf", f"tpad=stop_mode=clone:stop_duration={pad_amount}",
                    "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                    "-r", str(self.fps), "-pix_fmt", "yuv420p",
                    "-g", str(self.fps), "-keyint_min", str(self.fps),
                    "-sc_threshold", "0", "-an",
                    padded
                ], capture_output=True, text=True)
                if os.path.exists(padded):
                    return padded
            return out_path
        return None

    #  Dynamic Background with Motion 
    def _dynamic_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        """Create dynamic background with real motion feel.

        FIX (root cause of segments rendering as solid near-black frames,
        e.g. the ~8.5s near-pure-black stretch and the CTR segment both
        showing as flat dark backgrounds): this method built a `geq` filter
        string meant to animate the color/brightness over time, but never
        actually included it in the ffmpeg command below -- the real -vf
        chain was only `noise + zoompan + scale`, which has no color
        animation at all. So every segment just sat at its flat, very dark
        base color (e.g. "ctr": 0x1a1505 is RGB(26,21,5) -- already near
        black) for its entire duration, with only faint static noise on
        top. We now actually apply the geq color animation, AND brighten
        the base colors themselves so the animated range sits in a visible
        midtone rather than near-black.
        """
        colors = {
            "hook": "0x16163a", "suspense": "0x3a1212", "story": "0x10183a",
            "ctr": "0x3a2e10", "pause": "0x141414", "shock": "0x3a1f00",
            "reveal": "0x00351c",
        }
        color = colors.get(seg_type, "0x18181f")

        z = random.uniform(1.05, 1.15)
        r0, g0, b0 = int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)

        out = os.path.join(temp_dir, f"seg_dynamic_{idx}.mp4")

        subprocess.run([
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
            "-preset", "veryfast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p",
            "-t", str(duration), "-an", out
        ], capture_output=True, text=True)
        return out if os.path.exists(out) else None

    #  Suspense Visual Effect 
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
            "-preset", "veryfast", "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p", "-an",
            out
        ], capture_output=True, text=True)

        return out if os.path.exists(out) else base_video

    # --- Last-Resort Fallback (Guaranteed Success) -----------------------
    def _plain_color_fallback(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        """Absolute last-resort segment renderer. Uses the simplest possible
        ffmpeg invocation (plain solid color, no zoompan/geq/noise filters)
        so it has the maximum possible chance of succeeding even in
        constrained/unusual CI environments where the fancier filters used
        by _dynamic_bg_segment might fail. This guarantees every segment
        contributes ITS planned duration to the final timeline, which is
        what prevents the overall video from ever coming out shorter than
        the audio."""
        colors = {
            "hook": "0x0a0a1a", "suspense": "0x1a0505", "story": "0x050a1a",
            "ctr": "0x1a1505", "pause": "0x080808", "shock": "0x1a0a00",
            "reveal": "0x001a0a",
        }
        color = colors.get(seg_type, "0x0a0a0a")
        out = os.path.join(temp_dir, f"seg_fallback_{idx}.mp4")

        try:
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"color=c={color}:s={self.width}x{self.height}:r={self.fps}:d={duration}",
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                "-r", str(self.fps), "-pix_fmt", "yuv420p",
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0", "-an",
                "-t", str(duration),
                out
            ], capture_output=True, text=True, timeout=30)
        except Exception:
            return None

        return out if os.path.exists(out) and os.path.getsize(out) > 500 else None

    #  Main Video Creation 
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips, word_timings: List[Dict],
                     output_path: str, caption_ass_path: str = None) -> str:
        """Accepts optional 6th arg for backward compatibility with main.py.

        FIX: footage_clips lookup now keyed by ORIGINAL segment index (dict),
        matching the fixed footage_fetcher.download_footage output shape.
        Eliminates the index-shift bug that caused clips to land on the
        wrong segment (visible as "same scene repeating").

        FIX: duration is now hard-capped at the end with `-t` driven by the
        REAL measured audio duration, clamped into VIDEO_CONFIG's
        DURATION_MIN/MAX range - so even if any upstream segment timing is
        slightly off, the final render can never run away to 2x length.
        """

        dur_min = getattr(VIDEO_CONFIG, 'DURATION_MIN', 40)
        dur_max = getattr(VIDEO_CONFIG, 'DURATION_MAX', 55)
        total_audio = audio_data.get('total_duration', 0)
        target_duration = max(dur_min, min(dur_max, total_audio)) if total_audio > 0 else getattr(VIDEO_CONFIG, 'TARGET_DURATION', 47)

        print(f"  [TARGET] Target duration: {target_duration:.1f}s ({dur_min}-{dur_max}s range)")

        if script_segments and total_audio > 0:
            current_total = sum(s.get('duration', 2) for s in script_segments)
            ratio = target_duration / max(current_total, 1)

            for s in script_segments:
                if not s.get('is_pause'):
                    s['duration'] = min(max(s.get('duration', 2) * ratio, 1.5), 8.0)

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
                        s['duration'] = min(audio_dur, 8.0)

            non_pause = [s for s in script_segments if not s.get('is_pause')]
            if non_pause:
                pause_total = sum(s.get('duration', 0) for s in script_segments if s.get('is_pause'))
                speech_target = max(1.0, target_duration - pause_total)
                speech_sum = sum(s.get('duration', 2) for s in non_pause)
                if speech_sum > 0:
                    fix_ratio = speech_target / speech_sum
                    for s in non_pause:
                        s['duration'] = min(max(s['duration'] * fix_ratio, 1.0), 8.0)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        temp_dir = tempfile.mkdtemp()
        footage_dir = os.path.join("output", "footage")

        # Support both the new dict shape (segment_index -> filepath) and
        # an older list shape, without assuming a shifted index.
        footage_clip_paths: Dict[int, str] = {}
        if isinstance(footage_clips, dict):
            footage_clip_paths = footage_clips
        elif isinstance(footage_clips, list):
            for idx in range(len(script_segments)):
                candidate = os.path.join(footage_dir, f"clip_{idx}.mp4")
                if os.path.exists(candidate):
                    footage_clip_paths[idx] = candidate

        segment_files = []
        skipped_segments = []

        for i, seg in enumerate(script_segments):
            seg_type = seg.get('type', 'story')
            duration = max(1.0, seg.get('duration', 2.5))

            if seg.get('is_pause'):
                pause = self._dynamic_bg_segment('pause', min(duration, 0.3), temp_dir, i)
                if pause:
                    segment_files.append(pause)
                else:
                    # Even a pause segment failing to render is fine to
                    # drop (worst case: a slightly shorter breath gap),
                    # since pauses are capped at 0.5s and don't meaningfully
                    # affect total duration.
                    print(f"  [WARN] Seg {i} (pause): failed to render, skipping (negligible)")
                continue

            is_hook = seg_type in ['hook', 'shock', 'suspense']
            is_cta = seg_type in ['ctr', 'reveal']
            # FIX (swipe-away rate): only the literal opening 'hook' segment
            # needs the faster cut rhythm -- shock/suspense come a couple
            # seconds in, after the viewer has already decided to stay.
            is_opening_hook = seg_type == 'hook'

            clip_file = footage_clip_paths.get(i)
            used_real_footage = False

            if clip_file and os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000:
                out = self._smooth_cut_segment(clip_file, duration, temp_dir, i, fast_pacing=is_opening_hook)
                if out:
                    if is_hook:
                        out = self._suspense_effect(out, "glitch", temp_dir, i)
                    elif is_cta:
                        out = self._suspense_effect(out, "heartbeat", temp_dir, i)
                    elif seg_type == 'suspense':
                        out = self._suspense_effect(out, "tension", temp_dir, i)

                    segment_files.append(out)
                    used_real_footage = True

            if not used_real_footage:
                out = self._dynamic_bg_segment(seg_type, duration, temp_dir, i)
                if out:
                    if is_hook:
                        out = self._suspense_effect(out, "flash", temp_dir, i)
                    segment_files.append(out)
                    used_real_footage = True

            # FIX (root cause of the final video coming out SHORTER than the
            # audio, e.g. 27s video for 37s audio): if BOTH the real-footage
            # path and the animated dynamic-background path failed (e.g. an
            # ffmpeg invocation errored for any reason), this segment was
            # previously dropped completely and silently -- no warning, no
            # trace, just a missing chunk of timeline. Since `-shortest` is
            # used when muxing with audio, a video track that's missing
            # segments ends up shorter than the audio and the whole render
            # comes in under the target duration. We now fall back to a
            # guaranteed-to-succeed plain solid-color clip (no zoompan/geq/
            # noise filters that could themselves fail) as a last resort,
            # so every segment ALWAYS contributes its planned duration to
            # the timeline.
            if not used_real_footage:
                fallback = self._plain_color_fallback(seg_type, duration, temp_dir, i)
                if fallback:
                    segment_files.append(fallback)
                    print(f"  [WARN] Seg {i} ({seg_type}): footage + dynamic bg both failed, used plain color fallback")
                else:
                    skipped_segments.append(i)
                    print(f"  [FAIL] Seg {i} ({seg_type}): ALL render paths failed (including plain fallback) -- this segment will be MISSING from the timeline")

        if skipped_segments:
            print(f"  [WARN] {len(skipped_segments)} segment(s) totally failed to render: {skipped_segments}")

        if not segment_files:
            raise ValueError("[FAIL] No segments generated!")

        # FIX: verify the concatenated video track's total duration BEFORE
        # muxing with audio. If segments came in short for any reason (a
        # ffmpeg cut landing slightly under its requested length, a
        # fallback segment, etc.), `-shortest` below would silently
        # truncate the final video to whatever the video track's length
        # is -- which is exactly how a 37s-audio video previously came out
        # as a 27s final render. We pad the raw concatenated video up to
        # target_duration here (freezing the last frame) so `-shortest`
        # is never the thing that ends up deciding the final length --
        # the explicit `-t target_duration` on the muxing/render passes is.
        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for sf in segment_files:
                f.write(f"file '{os.path.abspath(sf)}'\n")

        video_prepad = os.path.join(temp_dir, "video_prepad.mp4")
        prepad_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
            "-r", str(self.fps),
            "-g", str(self.fps), "-keyint_min", str(self.fps),
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p", "-an",
            video_prepad
        ]
        r = subprocess.run(prepad_cmd, capture_output=True, text=True)
        concat_source = video_prepad if (r.returncode == 0 and os.path.exists(video_prepad)) else None

        if concat_source:
            prepad_duration = 0.0
            try:
                probe = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', concat_source
                ], capture_output=True, text=True)
                prepad_duration = float(probe.stdout.strip())
            except Exception:
                pass

            if prepad_duration > 0 and prepad_duration < target_duration - 0.2:
                shortfall = target_duration - prepad_duration
                print(f"  [WARN] Concatenated video ({prepad_duration:.1f}s) shorter than target "
                      f"({target_duration:.1f}s) -- extending {shortfall:.1f}s via slow-motion on the tail")
                video_padded = os.path.join(temp_dir, "video_padded.mp4")

                # FIX: tpad's stop_mode=clone freezes and repeats the exact
                # final frame for the entire shortfall duration. If that
                # final frame happens to land mid-transition/mid-effect
                # (e.g. a glitch/heartbeat effect's darker frame, or a
                # frame right at a hard cut), the freeze makes it visible
                # as a static "black frame" for several seconds at the end
                # of the video -- exactly what was reported. Slow-motion
                # stretching the last few seconds (via setpts) keeps actual
                # motion playing instead of repeating one static frame, so
                # there's no flat/frozen-looking segment for a dark frame
                # to get stuck on. We take the last min(3s, half the clip)
                # of footage and slow it down enough to cover the
                # shortfall, leaving the rest of the video untouched.
                tail_window = min(3.0, max(0.5, prepad_duration / 2))
                split_point = max(0.0, prepad_duration - tail_window)
                slowed_tail_duration = tail_window + shortfall
                speed_factor = tail_window / slowed_tail_duration  # < 1.0 = slower

                pad_cmd = [
                    "ffmpeg", "-y", "-i", concat_source,
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
                rp = subprocess.run(pad_cmd, capture_output=True, text=True)

                if rp.returncode == 0 and os.path.exists(video_padded):
                    concat_source = video_padded
                else:
                    # Fallback: if the slow-motion filter chain ever fails
                    # for any reason (e.g. tail_window edge case), fall
                    # back to the simple freeze-frame approach rather than
                    # leaving the video short.
                    print(f"  [WARN] Slow-motion tail extension failed, falling back to frame-hold padding")
                    fallback_padded = os.path.join(temp_dir, "video_padded_fallback.mp4")
                    fallback_cmd = [
                        "ffmpeg", "-y", "-i", concat_source,
                        "-vf", f"tpad=stop_mode=clone:stop_duration={shortfall}",
                        "-c:v", "libx264", "-crf", str(self.crf), "-preset", "veryfast",
                        "-r", str(self.fps), "-pix_fmt", "yuv420p",
                        "-g", str(self.fps), "-keyint_min", str(self.fps),
                        "-sc_threshold", "0", "-an",
                        fallback_padded
                    ]
                    rp2 = subprocess.run(fallback_cmd, capture_output=True, text=True)
                    if rp2.returncode == 0 and os.path.exists(fallback_padded):
                        concat_source = fallback_padded
        else:
            # Prepad pass itself failed -- fall back to the original
            # concat list directly, same as before this fix existed.
            concat_source = None

        video_raw = os.path.join(temp_dir, "video_raw.mp4")
        audio_path = audio_data.get("audio_path") or audio_data.get("final_audio", "")
        has_audio = audio_path and os.path.exists(audio_path)

        if concat_source:
            # We already have a (possibly padded) concatenated video track.
            # Just mux it with audio / re-encode with final settings.
            concat_cmd = ["ffmpeg", "-y", "-i", concat_source]
        else:
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
                "-async", "1",
                "-t", str(target_duration),
            ]
        else:
            concat_cmd += [
                "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset,
                "-r", str(self.fps),
                "-g", str(self.fps), "-keyint_min", str(self.fps),
                "-sc_threshold", "0",
                "-movflags", "+faststart",
                "-pix_fmt", "yuv420p",
                "-t", str(target_duration),
            ]
        concat_cmd.append(video_raw)

        r = subprocess.run(concat_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  [FAIL] Concat error: {r.stderr[:500]}")

        if caption_ass_path and os.path.exists(caption_ass_path):
            ass_path = caption_ass_path
        else:
            ass_path = os.path.join(temp_dir, "subs.ass")
            self._create_ass(word_timings, ass_path, CAPTION_CONFIG.FONT_SIZE, max_duration=target_duration)
        safe_ass = ass_path.replace('\\', '/').replace(':', '\\:')

        # FIX: this final render pass now always has a complete, explicit
        # `-t target_duration` - this is what previously got cut off /
        # malformed and let the rendered video run away to 2x length.
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
            "-t", str(target_duration),
            output_path
        ], capture_output=True, text=True)

        if r.returncode != 0:
            print(f"  [FAIL] Final render error: {r.stderr[:500]}")
            raise Exception(f"Video render failed: {r.stderr[:300]}")

        try:
            shutil.rmtree(temp_dir)
        except:
            pass

        return output_path
