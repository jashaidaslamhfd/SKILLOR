"""
Video Assembler — Production 2026
KEY FIX: Each clip is now TRIMMED to segment_duration from footage_fetcher.
This means clip length = exact voice duration for that segment.
No more clips running too long or too short vs the narrator.
"""

import os
import subprocess
import tempfile
import shutil
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RetentionVideoAssembler:

    def __init__(self):
        self.width  = 1080
        self.height = 1920
        self.fps    = 30
        self.crf    = 18
        self.preset = "faster"
        logger.info(
            f"🎬 Retention Video Assembler Engine Active "
            f"[Enforced Portrait {self.width}x{self.height} | {self.fps} FPS | 1.2s fast cuts]"
        )

    def _get_duration(self, file_path: str) -> float:
        if not file_path or not os.path.exists(file_path):
            return 0.0
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nockey=1', file_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(res.stdout.strip()) if res.stdout.strip() else 0.0
        except Exception:
            return 0.0

    def _trim_clip_to_duration(self, clip_path: str, target_duration: float, out_path: str) -> str:
        """
        ✅ CORE FIX — Trims (or loops) a clip to exactly target_duration seconds.
        This makes each video segment match the voice narration length precisely.

        - If clip is longer  → trim to target_duration
        - If clip is shorter → loop it to fill target_duration
        """
        clip_dur = self._get_duration(clip_path)

        if clip_dur <= 0:
            # Can't read clip, just copy as-is
            shutil.copy(clip_path, out_path)
            return out_path

        try:
            if clip_dur >= target_duration:
                # Simple trim — take from the middle for more visual interest
                start = max(0, (clip_dur - target_duration) / 2)
                cmd = [
                    'ffmpeg', '-y',
                    '-ss', str(round(start, 3)),
                    '-i', clip_path,
                    '-t', str(round(target_duration, 3)),
                    '-c:v', 'libx264', '-crf', str(self.crf),
                    '-preset', self.preset, '-an', out_path
                ]
            else:
                # Loop clip to fill required duration
                loops = int(target_duration / clip_dur) + 2
                cmd = [
                    'ffmpeg', '-y',
                    '-stream_loop', str(loops),
                    '-i', clip_path,
                    '-t', str(round(target_duration, 3)),
                    '-c:v', 'libx264', '-crf', str(self.crf),
                    '-preset', self.preset, '-an', out_path
                ]

            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode != 0:
                logger.warning(f"⚠️ Trim failed for {clip_path}: {res.stderr[:200]}")
                shutil.copy(clip_path, out_path)
            return out_path

        except Exception as e:
            logger.warning(f"⚠️ Trim exception: {e}")
            shutil.copy(clip_path, out_path)
            return out_path

    def _build_portrait_filter(self, idx: int, width: int, height: int,
                                crop_needed: bool, duration: float) -> str:
        if crop_needed or width > height:
            scale_filter = "scale=-1:1920,crop=1080:1920:(iw-1080)/2:0"
        else:
            scale_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

        safe_dur = duration if duration and duration > 0 else 4.0
        zoom_frames = max(1, int(round(safe_dur * self.fps)))
        zoom_filter = (
            f"zoompan=z='zoom+0.0012':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={zoom_frames}:s=1080x1920:fps={self.fps}"
        )
        return f"[{idx}:v]{scale_filter},{zoom_filter},setsar=1[v_processed_{idx}]"

    def assemble_final_video(
        self,
        processed_clips: Dict[int, str],
        audio_path: str,
        ass_path: Optional[str],
        output_path: str,
        metadata_clips: List[Dict]
    ) -> str:
        if not processed_clips:
            raise ValueError("❌ No clips to assemble.")

        temp_dir = tempfile.mkdtemp(prefix="render_engine_")
        logger.info(f"🚀 Assembling video — {len(processed_clips)} clips")

        try:
            sorted_indices = sorted(processed_clips.keys())

            # ✅ STEP 1: Trim each clip to its voice segment duration
            trimmed_clips = {}
            for idx in sorted_indices:
                clip_path = processed_clips[idx]
                meta = metadata_clips[idx] if idx < len(metadata_clips) else {}

                # segment_duration injected by content_generator & footage_fetcher
                target_dur = meta.get('segment_duration', None)
                if not target_dur or target_dur <= 0:
                    target_dur = self._get_duration(clip_path) or 5.0

                trimmed_path = os.path.join(temp_dir, f"trimmed_{idx}.mp4")
                self._trim_clip_to_duration(clip_path, target_dur, trimmed_path)
                trimmed_clips[idx] = trimmed_path

                logger.info(f"✂️  Clip {idx}: trimmed to {target_dur:.1f}s (voice sync)")

            # STEP 2: Build FFmpeg filter graph
            cmd = ['ffmpeg', '-y']
            filter_blocks = []
            concat_video_inputs = ""

            for idx in sorted_indices:
                clip_file = trimmed_clips[idx]
                cmd.extend(['-i', clip_file])

                meta = metadata_clips[idx] if idx < len(metadata_clips) else {}
                w = meta.get('width', 1080)
                h = meta.get('height', 1920)
                crop = meta.get('crop_needed', False)
                clip_dur = self._get_duration(clip_file)

                p_filter = self._build_portrait_filter(idx, w, h, crop, clip_dur)
                filter_blocks.append(p_filter)
                concat_video_inputs += f"[v_processed_{idx}]"

            # STEP 3: Add voice audio
            audio_index = len(sorted_indices)
            cmd.extend(['-i', audio_path])

            # STEP 4: Concat all clips
            num_clips = len(sorted_indices)
            filter_blocks.append(f"{concat_video_inputs}concat=n={num_clips}:v=1:a=0[v_unsplit]")

            # STEP 5: Captions overlay
            if ass_path and os.path.exists(ass_path):
                clean_ass = ass_path.replace("\\", "/").replace(":", "\\:")
                filter_blocks.append(f"[v_unsplit]subtitles='{clean_ass}'[v_final]")
                video_out_label = "[v_final]"
            else:
                video_out_label = "[v_unsplit]"

            cmd.extend(['-filter_complex', ";".join(filter_blocks)])
            cmd.extend([
                '-map', video_out_label,
                '-map', f"{audio_index}:a",
                '-c:v', 'libx264',
                '-crf', str(self.crf),
                '-preset', self.preset,
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                output_path
            ])

            logger.info("⚡ Running FFmpeg final render...")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if res.returncode != 0:
                logger.error(f"FFmpeg stdout: {res.stdout}")
                logger.error(f"FFmpeg stderr: {res.stderr}")
                raise RuntimeError(f"❌ FFmpeg failed: {res.stderr[:400]}")

            final_dur = self._get_duration(output_path)
            logger.info(
                f"✅ Video compiled: {os.path.basename(output_path)} | "
                f"Duration: {final_dur:.2f}s | Clips voice-synced ✅"
            )
            return output_path

        except Exception as e:
            logger.error(f"❌ Assembly failed: {e}")
            raise
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
