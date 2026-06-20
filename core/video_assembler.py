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

    # ─── Crossfade helper (smooth transitions instead of jump cuts) ──
    def _xfade_concat(self, cuts: List[str], cut_lens: List[float], out_path: str,
                       seg_idx: int, transition: float = 0.35) -> bool:
        """Dissolve consecutive cuts into each other with xfade instead of a
        hard concat cut. Hard cuts every ~1s, each at a different random
        zoom/crop, is what produced the 'photos flipping' look the viewer
        sees instead of real moving footage. A short crossfade between each
        cut reads as a smooth camera/scene transition instead."""
        n = len(cuts)
        if n == 0:
            return False
        if n == 1:
            shutil.copy(cuts[0], out_path)
            return True

        inputs = []
        for c in cuts:
            inputs += ['-i', c]

        filter_parts = []
        prev_label = '0:v'
        running_offset = cut_lens[0]
        for i in range(1, n):
            t = max(0.08, min(transition, cut_lens[i - 1] * 0.4, cut_lens[i] * 0.4))
            offset = max(0.0, running_offset - t)
            out_label = f"s{seg_idx}x{i}"
            filter_parts.append(
                f"[{prev_label}][{i}:v]xfade=transition=fade:duration={t:.3f}:offset={offset:.3f}[{out_label}]"
            )
            prev_label = out_label
            running_offset += cut_lens[i] - t

        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", ";".join(filter_parts),
            "-map", f"[{prev_label}]",
            "-c:v", "libx264", "-crf", str(self.crf), "-preset", "fast",
            "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an",
            out_path
        ]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000

    def _normalize_duration(self, video_path: str, target_dur: float, temp_dir: str, seg_idx: int) -> str:
        """Crossfading consumes a bit of runtime at each transition (two cuts
        overlap), which leaves the segment slightly shorter than total_dur.
        Pad with a held last frame (or trim) so every segment lands exactly
        on its target length and stays in sync with the narration."""
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ], capture_output=True, text=True)
            actual = float(probe.stdout.strip())
        except Exception:
            return video_path

        diff = target_dur - actual
        if abs(diff) < 0.05:
            return video_path

        fixed_path = os.path.join(temp_dir, f"norm_{seg_idx}.mp4")
        if diff > 0:
            cmd = ["ffmpeg", "-y", "-i", video_path,
                   "-vf", f"tpad=stop_mode=clone:stop_duration={diff:.3f}",
                   "-c:v", "libx264", "-crf", str(self.crf), "-preset", "fast",
                   "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an", fixed_path]
        else:
            cmd = ["ffmpeg", "-y", "-i", video_path, "-t", str(target_dur),
                   "-c:v", "libx264", "-crf", str(self.crf), "-preset", "fast",
                   "-r", str(self.fps), "-pix_fmt", "yuv420p", "-an", fixed_path]
        r = subprocess.run(cmd, capture_output=True)
        return fixed_path if (r.returncode == 0 and os.path.exists(fixed_path)) else video_path

    # ─── Fast Cuts from Footage ───────────────────────────────────
    def _fast_cut_segment(self, clip_file: str, total_dur: float, temp_dir: str, seg_idx: int) -> str:
        """
        Smooth retention-style cuts:
        - Every ~1.8-3.0s clip changes (was 0.8-1.5s — too fast, read as
          photos flipping instead of footage playing)
        - Each cut: random start point from source footage
        - Each cut: gentle zoom (1.06-1.18x) + random direction
        - Crossfade dissolve between cuts instead of a hard jump cut
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
        cut_lens = []
        current = 0.0
        cut_idx = 0

        # FIX: cuts were 0.8-1.5s with a hard concat between them — visually
        # indistinguishable from a slideshow flipping through photos. 1.8-3.0s
        # cuts give each shot enough time to read as footage, not a flash card.
        while current < total_dur:
            cut_len = min(random.uniform(1.8, 3.0), total_dur - current)
            if cut_len < 0.5:
                break

            cut_path = os.path.join(temp_dir, f"fastcut_{seg_idx}_{cut_idx}.mp4")

            # Random start in source clip
            max_start = max(0.0, src_dur - cut_len - 0.5)
            ss = random.uniform(0, max_start)

            # FIX: gentle zoom (was 1.15-1.35 — too aggressive, made every cut
            # feel like a sudden snap-zoom rather than a smooth push-in)
            z = random.uniform(1.06, 1.18)
            dirs_x = [f"iw/2-(iw/zoom/2)", "0", f"iw-(iw/zoom)"]
            dirs_y = [f"ih/2-(ih/zoom/2)", "0", f"ih-(ih/zoom)"]
            dx = random.choice(dirs_x)
            dy = random.choice(dirs_y)

            # zoompan needs d = total number of output frames for this cut, and a
            # per-frame zoom increment small enough to reach `z` exactly
            # over that many frames — that's what makes the zoom glide
            # continuously instead of snapping.
            total_frames = max(1, int(round(cut_len * self.fps)))
            zoom_step = (z - 1.0) / total_frames

            vf = (
                # Step 0: normalize source fps to match output fps BEFORE
                # zoompan — zoompan's frame stepping is driven by the *input*
                # frame rate, so this has to happen first or the zoom still
                # steps on the source's original cadence.
                f"fps={self.fps},"
                # Step 1: Scale footage to portrait
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,"
                f"crop={self.width}:{self.height},setsar=1,"
                # Step 2: Zoom in random direction — smooth over full clip length
                f"zoompan=z='min(zoom+{zoom_step:.6f},{z})':d={total_frames}:x='{dx}':y='{dy}':s={self.width}x{self.height}:fps={self.fps},"
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
                cut_lens.append(cut_len)

            current += cut_len
            cut_idx += 1

        if not cuts:
            return None

        out_path = os.path.join(temp_dir, f"seg_footage_{seg_idx}.mp4")

        # FIX: try smooth crossfade-dissolve first (this is what actually
        # kills the "photo click" feel). Fall back to the old hard concat
        # only if xfade fails for some reason, so a video still gets made.
        if self._xfade_concat(cuts, cut_lens, out_path, seg_idx):
            print(f"    ✅ Seg {seg_idx}: {len(cuts)} cuts | crossfade-smoothed footage")
        else:
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
            print(f"    ⚠️ Seg {seg_idx}: crossfade failed, used hard concat fallback")

        if not os.path.exists(out_path):
            return None

        out_path = self._normalize_duration(out_path, total_dur, temp_dir, seg_idx)
        return out_path

    def _color_bg_segment(self, seg_type: str, duration: float, temp_dir: str, idx: int) -> str:
        """Dark color bg with pulsing zoom — for when no footage"""
        colors = {"hook": "0x050510", "suspense": "0x100005", "story": "0x050010", "ctr": "0x100500", "pause": "0x000000"}
        color = colors.get(seg_type, "0x050510")

        z = random.uniform(1.08, 1.25)
        # FIX: d=1 caused a stop-motion "photo click" pulse instead of a
        # smooth zoom — same fix as the footage cuts above.
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

    # ─── Main Create ──────────────────────────────────────────────
    def create_video(self, script_segments: List[Dict], audio_data: Dict,
                     footage_clips: List[Dict], word_timings: List[Dict],
                     output_path: str) -> str:

        total_audio = audio_data.get('total_duration', 0)
        print(f"\n  🎬 VideoAssembler | Audio: {total_audio:.1f}s | Words: {len(word_timings)}")

        # FIX: segment durations now derived from REAL word_timings
        # (actual edge-tts timestamps) instead of scaling an estimated
        # duration by a global ratio. The ratio approach kept segments
        # roughly proportional but not actually aligned to where each
        # segment's words are spoken — this is why footage cuts visually
        # drifted out of sync with the audio over the course of a video.
        if word_timings and script_segments:
            wt_idx = 0
            for s in script_segments:
                if s.get('is_pause'):
                    continue
                seg_word_count = len(s.get('text', '').split())
                seg_words = word_timings[wt_idx:wt_idx + seg_word_count]
                wt_idx += seg_word_count
                if seg_words:
                    new_dur = round(max(0.2, seg_words[-1]['end'] - seg_words[0]['start']), 3)
                    # FIX: sanity-check the realigned duration against the
                    # original estimate. If word_timings slicing drifted
                    # (e.g. due to a word-count mismatch upstream), it could
                    # produce a wildly-too-short duration, which silently
                    # collapsed total video length to ~31-35s instead of
                    # the target 40-55s. Only trust the realigned value if
                    # it's reasonably close to what was originally expected
                    # for this segment's word count.
                    original_dur = s.get('duration', new_dur)
                    if original_dur > 0 and new_dur < original_dur * 0.5:
                        print(f"  ⚠️ Segment duration realignment looked wrong ({new_dur}s vs expected ~{original_dur}s) — keeping original estimate")
                    else:
                        s['duration'] = new_dur
            print(f"  🔧 Segment durations re-aligned to real word timestamps")
        elif total_audio > 0 and script_segments:
            # Fallback: old ratio-based estimate, only used if word_timings is empty
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
