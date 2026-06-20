"""Audio Generator — Natural Breathing Pauses + Fan Ambience"""

import os
import asyncio
import subprocess
from typing import Dict, List


class AudioGenerator:
    def __init__(self):
        # FIX: Dark psychology voice for USA/UK audience
        self.voice = "en-US-GuyNeural"   # Deep, intense, cinematic
        self.rate = "-12%"                # Slower = more dramatic
        self.pitch = "-3Hz"              # Lower = darker feel
        self.volume = "+10%"
        self.sample_rate = 44100
        self.channels = 2
        self.audio_bitrate = "192k"

    def _get_audio_duration(self, path: str) -> float:
        try:
            r = subprocess.run([
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return float(r.stdout.strip())
        except:
            pass
        return 0.0

    def _make_breath_pause(self, duration: float, output_path: str):
        """
        Real breathing pause:
        - Brown noise (fan/room ambience) — so YouTube doesn't flag silence as robotic
        - Amplitude 0.018 = subtle room tone (FIX: was 0.012, too low)
        - Feels like narrator took a breath, not a dead cut
        """
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.018:duration={duration}',
            '-ar', str(self.sample_rate),
            '-ac', str(self.channels),
            '-b:a', self.audio_bitrate,
            '-acodec', 'libmp3lame',
            output_path
        ]
        subprocess.run(cmd, capture_output=True)

    def _add_bg_music_and_fan(self, speech_path: str, output_path: str, total_duration: float):
        """
        FIX: Mix speech with:
        1. Continuous fan/room noise (brown noise at 0.018) — natural room feel
        2. Dark ambient background music simulation (low-freq brown noise at 0.06)
        Both layers underneath the voice — USA/UK dark psychology channel standard
        """
        # Fan noise layer (continuous throughout whole video)
        fan_path = output_path.replace('.mp3', '_fan.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.018:duration={total_duration}',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', fan_path
        ], capture_output=True)

        # Dark ambient music layer (low rumble - cinematic dark feel)
        music_path = output_path.replace('.mp3', '_music.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            # Low-frequency pink noise = cinematic ambient/drone sound
            '-i', f'anoisesrc=r={self.sample_rate}:color=pink:amplitude=0.06:duration={total_duration}',
            '-af', 'lowpass=f=200,volume=0.6',  # Cut high freqs = music-like rumble
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', music_path
        ], capture_output=True)

        # Mix: Speech (100%) + Fan (18%) + Music (6%)
        if os.path.exists(fan_path) and os.path.exists(music_path):
            subprocess.run([
                'ffmpeg', '-y',
                '-i', speech_path,
                '-i', fan_path,
                '-i', music_path,
                '-filter_complex',
                '[0:a]volume=1.0[speech];[1:a]volume=0.18[fan];[2:a]volume=0.06[music];'
                '[speech][fan][music]amix=inputs=3:duration=first:normalize=0[out]',
                '-map', '[out]',
                '-ar', str(self.sample_rate), '-ac', str(self.channels),
                '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
                output_path
            ], capture_output=True)
            # Cleanup temp files
            for f in [fan_path, music_path]:
                if os.path.exists(f):
                    os.remove(f)
            print(f"    🎵 BG music + fan noise mixed ✅")
        else:
            import shutil
            shutil.copy(speech_path, output_path)
            print(f"    ⚠️ BG mix failed, using speech only")

    def _generate_word_timings(self, audio_path: str, text: str, time_offset: float = 0.0) -> List[Dict]:
        actual_duration = self._get_audio_duration(audio_path)
        words = text.split()
        if not words or actual_duration <= 0:
            return []

        weights = []
        for word in words:
            base = 1.0
            char_len = len(word.strip('.,!?;:\"\' '))
            if char_len > 8:
                base += 0.1
            elif char_len > 5:
                base += 0.05
            weights.append(base)

        scale = actual_duration / sum(weights)
        timings = []
        current = time_offset
        for word, weight in zip(words, weights):
            clean = word.strip('.,!?;:\"()[]{}"\'')
            dur = weight * scale
            timings.append({
                'word': clean,
                'start': round(current, 3),
                'end': round(current + dur, 3),
                'duration': round(dur, 3)
            })
            current += dur
        return timings

    async def _async_tts(self, text: str, path: str, capture_boundaries: bool = False) -> list:
        import edge_tts
        comm = edge_tts.Communicate(
            text, voice=self.voice,
            rate=self.rate, volume=self.volume, pitch=self.pitch
        )
        boundaries = []
        if capture_boundaries:
            # FIX: edge-tts emits real WordBoundary events with exact
            # offsets — using these instead of estimating from character
            # length is what fixes captions drifting ahead of/behind the
            # actual spoken audio ("captions faster than audio").
            with open(path, "wb") as f:
                async def _run():
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            boundaries.append({
                                "word": chunk["text"],
                                "start": chunk["offset"] / 10_000_000,  # 100ns units -> seconds
                                "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                            })
                await asyncio.wait_for(_run(), timeout=60)
        else:
            await asyncio.wait_for(comm.save(path), timeout=60)
        return boundaries

    def _generate_speech(self, text: str, path: str) -> tuple:
        # FIX: retry up to 3 times with timeout, instead of hanging forever
        # on a single bad attempt. Now also returns real word-boundary
        # timestamps captured directly from edge-tts.
        last_error = None
        boundaries = []
        for attempt in range(1, 4):
            try:
                try:
                    boundaries = asyncio.run(self._async_tts(text, path, capture_boundaries=True))
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    boundaries = loop.run_until_complete(self._async_tts(text, path, capture_boundaries=True))
                    loop.close()
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    break
            except (asyncio.TimeoutError, Exception) as e:
                last_error = e
                print(f"    ⚠️ TTS attempt {attempt}/3 failed: {e}")
                if attempt < 3:
                    import time as _time
                    _time.sleep(3)
        else:
            raise Exception(f"❌ TTS failed after 3 attempts: {last_error}")

        if not os.path.exists(path):
            return 0.0, []

        # Upsample to 44.1kHz stereo 192k
        hq = path.replace('.mp3', '_hq.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', path,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', hq
        ], capture_output=True, timeout=60)
        if os.path.exists(hq):
            os.replace(hq, path)

        return self._get_audio_duration(path), boundaries

    def generate_with_effects(self, script_segments: List[Dict], output_dir: str) -> Dict:
        os.makedirs(output_dir, exist_ok=True)

        print(f"    🎙️ Voice: {self.voice} | Rate: {self.rate} | Pitch: {self.pitch}")

        # Step 1: Generate ONE continuous speech for all non-pause segments
        # This eliminates inter-segment robotic gaps
        speech_segs = [s for s in script_segments if not s.get('is_pause') and s.get('text', '').strip()]
        full_text = ' '.join(s['text'] for s in speech_segs)
        print(f"    📝 Full speech: {len(full_text.split())} words")

        speech_path = os.path.join(output_dir, "speech_full.mp3")
        # FIX: now captures real per-word timestamps from edge-tts
        # (WordBoundary events) instead of estimating them afterward from
        # character length. This is what fixes captions running ahead of
        # or behind the actual spoken audio.
        speech_dur, word_boundaries = self._generate_speech(full_text, speech_path)
        print(f"    🎙️ Speech duration: {speech_dur:.1f}s | {len(word_boundaries)} real word timestamps")

        words = full_text.split()
        # Fallback wps only used if edge-tts didn't return boundaries for some reason
        wps = speech_dur / len(words) if words else 0.3
        # FIX: this check was too loose (allowed off-by-2), which let
        # mismatched boundary counts (e.g. from contractions like "don't"
        # being split into 2 WordBoundary events by edge-tts) through.
        # That misalignment caused per-segment slicing further down to
        # grab the WRONG audio range — silently shrinking total video
        # duration to ~31-35s instead of the target 40-55s. Now we require
        # an EXACT count match, and fall back to the estimated-wps method
        # (still better than wrong slicing) whenever counts disagree.
        use_real_boundaries = len(word_boundaries) == len(words)
        if not use_real_boundaries:
            print(f"    ⚠️ Word boundary count mismatch ({len(word_boundaries)} boundaries vs {len(words)} words) — using estimated timing instead")

        # Step 2: Slice speech + insert breath pauses
        audio_files = []
        all_timings = []
        current_time = 0.0
        word_offset = 0.0  # seconds into speech_full
        boundary_idx = 0

        for i, seg in enumerate(script_segments):

            if seg.get('is_pause'):
                pause_dur = float(seg.get('duration', 0.5))
                pause_path = os.path.join(output_dir, f"pause_{i}.mp3")
                self._make_breath_pause(pause_dur, pause_path)
                if os.path.exists(pause_path):
                    audio_files.append(pause_path)
                    current_time += pause_dur
                    print(f"      ⏸️  Breath pause {i}: {pause_dur}s")
            else:
                seg_text = seg.get('text', '').strip()
                if not seg_text:
                    continue

                seg_word_count = len(seg_text.split())

                if use_real_boundaries:
                    # Use actual edge-tts timestamps for this segment's words
                    seg_boundaries = word_boundaries[boundary_idx:boundary_idx + seg_word_count]
                    boundary_idx += seg_word_count
                    if seg_boundaries:
                        seg_start = seg_boundaries[0]['start']
                        seg_end = seg_boundaries[-1]['end']
                        seg_dur = max(0.1, seg_end - seg_start)
                    else:
                        seg_dur = seg_word_count * wps
                        seg_start = word_offset
                else:
                    seg_dur = seg_word_count * wps
                    seg_start = word_offset

                chunk_path = os.path.join(output_dir, f"chunk_{i}.mp3")

                # Trim exact slice from full speech
                subprocess.run([
                    'ffmpeg', '-y', '-i', speech_path,
                    '-ss', str(seg_start),
                    '-t', str(seg_dur),
                    '-ar', str(self.sample_rate),
                    '-ac', str(self.channels),
                    '-b:a', self.audio_bitrate,
                    '-acodec', 'libmp3lame',
                    chunk_path
                ], capture_output=True)

                if os.path.exists(chunk_path):
                    actual_dur = self._get_audio_duration(chunk_path)
                    audio_files.append(chunk_path)

                    if use_real_boundaries and seg_boundaries:
                        # Re-anchor each word's timestamp to current_time
                        # (position in the final assembled track, which
                        # includes breath pauses inserted between segments)
                        shift = current_time - seg_start
                        for wb in seg_boundaries:
                            all_timings.append({
                                'word': wb['word'].strip('.,!?;:"()[]{}\'').strip(),
                                'start': round(wb['start'] + shift, 3),
                                'end': round(wb['end'] + shift, 3),
                                'duration': round(wb['end'] - wb['start'], 3)
                            })
                    else:
                        timings = self._generate_word_timings(chunk_path, seg_text, current_time)
                        all_timings.extend(timings)

                    current_time += actual_dur
                    word_offset += seg_dur

        # Step 3: Concatenate all chunks + pauses
        final_path = os.path.join(os.path.abspath(output_dir), "final_audio.mp3")

        if not audio_files:
            raise Exception("No audio files generated")

        list_file = os.path.join(output_dir, "final_list.txt")
        with open(list_file, 'w') as f:
            for af in audio_files:
                f.write(f"file '{os.path.abspath(af)}'\n")

        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
            final_path
        ], capture_output=True)

        raw_dur = self._get_audio_duration(final_path)

        # FIX: Mix in background music + fan noise for natural USA/UK feel
        mixed_path = os.path.join(os.path.abspath(output_dir), "final_audio_mixed.mp3")
        self._add_bg_music_and_fan(final_path, mixed_path, raw_dur)
        if os.path.exists(mixed_path) and os.path.getsize(mixed_path) > 1000:
            final_path = mixed_path

        total_dur = self._get_audio_duration(final_path)
        print(f"    ✅ Final: {total_dur:.1f}s | {len(all_timings)} words")
        print(f"    🎯 {'✅ IN RANGE' if 40 <= total_dur <= 55 else '⚠️ ' + str(round(total_dur,1)) + 's out of range'}")

        return {
            'final_audio': final_path,
            'segments': audio_files,
            'word_timings': all_timings,
            'total_duration': total_dur
    }
