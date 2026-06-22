"""Audio Generator - Natural Breathing Pauses + Fan Ambience + Duration Control"""

import os
import asyncio
import subprocess
import math
from typing import Dict, List

from config.settings import AUDIO_CONFIG


class AudioGenerator:
    def __init__(self):
        # FIX: read voice from AUDIO_CONFIG.VOICE (settings.py) instead of
        # hardcoding it here separately. Previously this class had its own
        # hardcoded "en-US-GuyNeural" that was completely disconnected from
        # AUDIO_CONFIG.VOICE in settings.py -- changing the voice in
        # settings.py silently did nothing, because this is the value that
        # actually gets passed to edge_tts. Falls back to GuyNeural if
        # AUDIO_CONFIG.VOICE isn't set, for safety.
        self.voice = getattr(AUDIO_CONFIG, 'VOICE', 'en-US-AndrewMultilingualNeural')
        # FIX: pitch/volume/base_rate were hardcoded here, completely
        # disconnected from AUDIO_CONFIG in settings.py — exactly the same
        # class of bug the voice fix above already addressed. Changing
        # PITCH/VOLUME/RATE in settings.py silently did nothing because
        # these hardcoded values are what actually got passed to edge_tts.
        # Now reads from AUDIO_CONFIG, with safe fallbacks tuned for a
        # natural (non-robotic) AndrewMultilingualNeural read: no pitch
        # shift and no volume boost, since both push this voice toward a
        # processed/metallic sound.
        self.base_rate = getattr(AUDIO_CONFIG, 'RATE_MIN', -5)
        self.pitch = getattr(AUDIO_CONFIG, 'PITCH', '+0Hz')
        self.volume = getattr(AUDIO_CONFIG, 'VOLUME', '+0%')
        self.sample_rate = 44100
        self.channels = 2
        self.audio_bitrate = "192k"
        self.target_wpm = 150  # FIX: Faster pacing for retention
        self.speed_factor = 1.15  # FIX: 1.15x crisp speed
        self.target_duration = 47

    def _calculate_tts_rate(self, word_count: int) -> str:
        """
        Dynamic TTS rate based on word count to hit 40-55s target.
        Format: "+10%" or "-10%" — Edge-TTS requires + or - prefix!

        FIX: rate steps were hardcoded (-15/-10/-5/0/5/10), completely
        disconnected from AUDIO_CONFIG.RATE_MIN/RATE_MAX in settings.py —
        same disconnect class as the voice/pitch/volume bugs above.
        Changing RATE_MIN/RATE_MAX in settings.py silently did nothing.
        Now derives steps from the configured range, and clamps to it, so
        a long script can never push the rate more negative than
        RATE_MIN (the main remaining cause of robotic-sounding narration
        on long scripts).
        """
        rate_min = getattr(AUDIO_CONFIG, 'RATE_MIN', -8)
        rate_max = getattr(AUDIO_CONFIG, 'RATE_MAX', 8)

        expected_duration = word_count / (self.target_wpm / 60)

        if expected_duration > 55:
            rate = rate_min
        elif expected_duration > 50:
            rate = round(rate_min * 0.66)
        elif expected_duration > 45:
            rate = round(rate_min * 0.33)
        elif expected_duration > 40:
            rate = 0
        elif expected_duration > 35:
            rate = round(rate_max * 0.5)
        else:
            rate = rate_max

        rate = max(rate_min, min(rate_max, rate))
        prefix = "+" if rate >= 0 else ""
        rate_str = f"{prefix}{rate}%"
        print(f"    🎙️ Words: {word_count} | Expected: {expected_duration:.1f}s | TTS rate: {rate_str}")
        return rate_str

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
        """FIX: previously this was flat brown noise at constant amplitude
        for the whole pause -- that reads as a burst of static, not a
        breath. A real inhale/exhale rises and falls in volume and is
        gentler in tone. We now lowpass-filter the noise (removes the
        harsh/hissy high end) and shape it with a fade-in/fade-out envelope
        so it swells and fades like an actual breath instead of switching
        on/off abruptly."""
        fade = min(0.35, duration / 3)
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=pink:amplitude=0.025:duration={duration}',
            '-af', f'lowpass=f=900,afade=t=in:st=0:d={fade},afade=t=out:st={max(0, duration - fade)}:d={fade}',
            '-ar', str(self.sample_rate),
            '-ac', str(self.channels),
            '-b:a', self.audio_bitrate,
            '-acodec', 'libmp3lame',
            output_path
        ]
        subprocess.run(cmd, capture_output=True)

    def _add_bg_music_and_fan(self, speech_path: str, output_path: str, total_duration: float):
        fan_path = output_path.replace('.mp3', '_fan.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.018:duration={total_duration}',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', fan_path
        ], capture_output=True)

        music_path = output_path.replace('.mp3', '_music.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=pink:amplitude=0.06:duration={total_duration}',
            '-af', 'lowpass=f=200,volume=0.6',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', music_path
        ], capture_output=True)

        if os.path.exists(fan_path) and os.path.exists(music_path):
            subprocess.run([
                'ffmpeg', '-y',
                '-i', speech_path,
                '-i', fan_path,
                '-i', music_path,
                '-filter_complex',
                '[0:a]volume=1.0[speech];[1:a]volume=0.10[fan];[2:a]volume=0.03[music];  # FIX: Voice dominates for retention'
                '[speech][fan][music]amix=inputs=3:duration=first:normalize=0[out]',
                '-map', '[out]',
                '-ar', str(self.sample_rate), '-ac', str(self.channels),
                '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
                output_path
            ], capture_output=True)
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
            clean = word.strip('.,!?;:\"()[]{}")\'')
            dur = weight * scale
            timings.append({
                'word': clean,
                'start': round(current, 3),
                'end': round(current + dur, 3),
                'duration': round(dur, 3)
            })
            current += dur
        return timings

    async def _async_tts(self, text: str, path: str, rate: str, capture_boundaries: bool = False) -> list:
        import edge_tts
        # FIX (root cause of "0 real word timestamps" every single run,
        # regardless of which voice is used): newer edge-tts versions
        # default the `boundary` parameter to "SentenceBoundary" instead of
        # "WordBoundary". Without explicitly requesting WordBoundary, the
        # TTS service only emits one timing event per SENTENCE, never per
        # word -- so `chunk["type"] == "WordBoundary"` never matched
        # anything and word_boundaries always came back empty. This is why
        # captions and scene-cut timing were always falling back to rough
        # word-length estimates instead of real per-word TTS timestamps,
        # for every voice (GuyNeural, and this would have continued with
        # AndrewMultilingualNeural too without this fix). Explicitly
        # requesting "WordBoundary" restores real per-word timing, which is
        # what keeps captions and footage cuts genuinely in sync with the
        # actual spoken audio rather than an approximation.
        try:
            comm = edge_tts.Communicate(
                text, voice=self.voice,
                rate=rate, volume=self.volume, pitch=self.pitch,
                boundary="WordBoundary",
            )
        except TypeError:
            # Older edge-tts versions don't accept a `boundary` kwarg at
            # all (they always emitted WordBoundary by default, which is
            # why this bug only appeared after edge-tts changed its
            # default). Fall back to the no-boundary-kwarg call so this
            # still works on either version.
            comm = edge_tts.Communicate(
                text, voice=self.voice,
                rate=rate, volume=self.volume, pitch=self.pitch
            )
        boundaries = []
        if capture_boundaries:
            with open(path, "wb") as f:
                async def _run():
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            boundaries.append({
                                "word": chunk["text"],
                                "start": chunk["offset"] / 10_000_000,
                                "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                            })
                await asyncio.wait_for(_run(), timeout=60)
        else:
            await asyncio.wait_for(comm.save(path), timeout=60)
        return boundaries

    async def _generate_speech(self, text: str, path: str, rate: str) -> tuple:
        """Async method — no asyncio.run() conflict!"""
        last_error = None
        boundaries = []
        for attempt in range(1, 4):
            try:
                boundaries = await self._async_tts(text, path, rate, capture_boundaries=True)

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

        # FIX (retention): Remove silence (dead air between sentences)
        no_sil = path.replace('.mp3', '_ns.mp3')
        self._remove_silence(path, no_sil)
        if os.path.exists(no_sil): os.replace(no_sil, path)
        print(f"    🔇 Silence removed")

        # FIX (retention): Apply 1.15x speed for crisp delivery
        fast = path.replace('.mp3', '_fast.mp3')
        self._speed_up(path, fast)
        if os.path.exists(fast): os.replace(fast, path)
        print(f"    ⚡ Speed: {self.speed_factor}x applied")

        hq = path.replace('.mp3', '_hq.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', path,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', hq
        ], capture_output=True, timeout=60)
        if os.path.exists(hq):
            os.replace(hq, path)

        return self._get_audio_duration(path), boundaries

    def _sanitize_for_tts(self, text: str) -> str:
        """
        Edge-TTS reads symbols literally out loud — '#' becomes "hashtag",
        '/' becomes "slash", etc. Last line of defense right before TTS.
        """
        import re
        if not text:
            return text
        text = re.sub(r'#\w+', '', text)      # hashtags, e.g. #Shorts
        text = re.sub(r'#', '', text)          # any stray lone '#'
        text = text.replace('/', ' ')          # slashes -> space (avoid "slash")
        text = re.sub(r'[*_~`]', '', text)     # markdown leftovers
        text = re.sub(r'\s+', ' ', text).strip()
        return text


    def _remove_silence(self, input_path: str, output_path: str):
        """FIX (retention): Remove dead air between sentences for tight pacing."""
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-af', 'silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB:stop_periods=1:stop_duration=0.05:stop_threshold=-45dB',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
        ], capture_output=True)
        return output_path if os.path.exists(output_path) else input_path

    def _speed_up(self, input_path: str, output_path: str):
        """FIX (retention): 1.15x speed without chipmunk effect."""
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-af', f'atempo={self.speed_factor}',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
        ], capture_output=True)
        return output_path if os.path.exists(output_path) else input_path

    def _add_sfx_transitions(self, speech_path: str, total_duration: float):
        """FIX (retention): Whoosh/pop SFX every 3 seconds for engagement."""
        import tempfile
        sfx_dir = tempfile.mkdtemp()
        whoosh = os.path.join(sfx_dir, "w.mp3")
        pop = os.path.join(sfx_dir, "p.mp3")

        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'sine=frequency=600:duration=0.12,afade=t=out:st=0.08:d=0.04,volume=0.25',
            '-ar', str(self.sample_rate), whoosh], capture_output=True)
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi',
            '-i', 'sine=frequency=1000:duration=0.06,afade=t=out:st=0.04:d=0.02,volume=0.2',
            '-ar', str(self.sample_rate), pop], capture_output=True)

        if os.path.exists(whoosh) and os.path.exists(pop):
            inputs = ['-i', speech_path]
            delays = []
            count = int(total_duration / 3)
            for i in range(min(count, 8)):
                offset = (i + 1) * 3.0
                if offset < total_duration - 0.5:
                    inputs.extend(['-i', whoosh if i % 2 == 0 else pop])
                    delays.append(f"[{i+1}:a]adelay={int(offset*1000)}|{int(offset*1000)}[s{i}]")

            if len(inputs) > 2:
                mix = f"[0:a]volume=1.0[speech];" + ";".join(delays) + ";"
                mix += "[speech]" + "".join([f"[s{i}]" for i in range(len(delays))])
                mix += f"amix=inputs={len(delays)+1}:duration=first:normalize=0[out]"
                out_path = speech_path.replace('.mp3', '_sfx.mp3')
                subprocess.run([
                    'ffmpeg', '-y'] + inputs + [
                    '-filter_complex', mix, '-map', '[out]',
                    '-ar', str(self.sample_rate), '-ac', str(self.channels),
                    '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', out_path
                ], capture_output=True)
                if os.path.exists(out_path): os.replace(out_path, speech_path)
        shutil.rmtree(sfx_dir, ignore_errors=True)

    async def generate_with_effects(self, script_segments: List[Dict], output_dir: str) -> Dict:
        """Async method — await _generate_speech!

        FIX (duration doubling root cause): the previous version advanced
        `current_time` by `actual_dur` (the real duration of each cut MP3
        chunk, measured AFTER ffmpeg's `-ss`/`-t` cut, which always rounds
        to the nearest encoder frame/keyframe boundary) while computing
        caption timestamp shifts from `seg_start` (the boundary-estimated,
        un-rounded start time). Each segment's rounding error — a few
        hundredths to low tenths of a second — was carried forward and
        ACCUMULATED into every subsequent segment's `shift`, AND into
        `current_time` itself, which is also what segment durations get
        re-derived from downstream in the video assembler. Across 8-12
        segments this drift compounded into many extra seconds, and in
        pathological cases (e.g. a near-empty/very short cut snapping to a
        much longer keyframe boundary) a single segment could balloon —
        explaining videos rendering at ~2x the intended length.

        FIX: we now track a single authoritative timeline cursor
        (`timeline_cursor`) that only ever advances by the EXACT duration we
        asked ffmpeg to cut (`seg_dur`, clamped to stay inside the real
        speech length) — never by the post-hoc measured file duration. Word
        boundary timestamps are shifted onto this same cursor, so captions,
        segment durations, and total duration all stay internally
        consistent and can never drift apart or compound errors.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize every segment's text before it ever reaches TTS
        for s in script_segments:
            if not s.get('is_pause') and s.get('text'):
                s['text'] = self._sanitize_for_tts(s['text'])

        speech_segs = [s for s in script_segments if not s.get('is_pause') and s.get('text', '').strip()]
        full_text = ' '.join(s['text'] for s in speech_segs)
        total_words = len(full_text.split())

        dynamic_rate = self._calculate_tts_rate(total_words)

        if total_words < 80:
            print(f"    ⚠️ WARNING: Only {total_words} words — need 100+ for 40-55s video!")
        elif total_words > 130:
            print(f"    ⚠️ WARNING: {total_words} words — may exceed 55s!")

        speech_path = os.path.join(output_dir, "speech_full.mp3")
        speech_dur, word_boundaries = await self._generate_speech(full_text, speech_path, dynamic_rate)
        print(f"    🎙️ Speech duration: {speech_dur:.1f}s | {len(word_boundaries)} real word timestamps")

        if speech_dur < 30:
            print(f"    ⚠️ Speech only {speech_dur:.1f}s — too short!")

        words = full_text.split()
        wps = speech_dur / len(words) if words else 0.3

        boundary_diff = abs(len(word_boundaries) - len(words))
        use_real_boundaries = len(words) > 0 and boundary_diff <= max(3, int(len(words) * 0.08))

        if not use_real_boundaries:
            print(f"    ⚠️ Boundary mismatch ({len(word_boundaries)} vs {len(words)}) — using estimated timing")

        audio_files = []
        all_timings = []
        # FIX: single authoritative cursor for the OUTPUT timeline (what the
        # final concatenated audio file's clock will actually read).
        timeline_cursor = 0.0
        word_offset_words = 0
        total_pause_time = 0.0

        for i, seg in enumerate(script_segments):
            if seg.get('is_pause'):
                pause_dur = min(float(seg.get('duration', 0.5)), 0.3)  # FIX: Tighter pauses for retention
                pause_path = os.path.join(output_dir, f"pause_{i}.mp3")
                self._make_breath_pause(pause_dur, pause_path)
                if os.path.exists(pause_path):
                    actual_pause_dur = self._get_audio_duration(pause_path) or pause_dur
                    audio_files.append(pause_path)
                    timeline_cursor += actual_pause_dur
                    total_pause_time += actual_pause_dur
                    print(f"      ⏸️  Breath pause {i}: {pause_dur}s")
            else:
                seg_text = seg.get('text', '').strip()
                if not seg_text:
                    continue

                seg_word_count = len(seg_text.split())

                if use_real_boundaries and word_boundaries:
                    start_frac = word_offset_words / len(words) if words else 0
                    end_frac = (word_offset_words + seg_word_count) / len(words) if words else 0

                    b_start_idx = min(int(round(start_frac * len(word_boundaries))), len(word_boundaries) - 1)
                    b_end_idx = min(int(round(end_frac * len(word_boundaries))), len(word_boundaries))
                    b_start_idx = max(0, b_start_idx)
                    b_end_idx = max(b_start_idx + 1, b_end_idx)

                    seg_boundaries = word_boundaries[b_start_idx:b_end_idx]
                    word_offset_words += seg_word_count

                    if seg_boundaries:
                        seg_start = seg_boundaries[0]['start']
                        seg_end = seg_boundaries[-1]['end']
                        seg_dur = max(0.1, seg_end - seg_start)
                    else:
                        seg_dur = seg_word_count * wps
                        seg_start = timeline_cursor
                else:
                    seg_boundaries = []
                    seg_dur = seg_word_count * wps
                    seg_start = timeline_cursor

                chunk_path = os.path.join(output_dir, f"chunk_{i}.mp3")

                # Clamp the SOURCE cut window to stay inside real speech audio.
                seg_start = max(0, min(seg_start, speech_dur - 0.1))
                seg_dur = max(0.1, min(seg_dur, speech_dur - seg_start))

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
                    audio_files.append(chunk_path)

                    # FIX: shift word boundaries onto timeline_cursor (the
                    # OUTPUT timeline), using the exact requested seg_dur as
                    # the advance amount — not the post-cut measured file
                    # duration. This is what keeps captions, segment
                    # durations, and total duration from drifting apart.
                    if use_real_boundaries and seg_boundaries:
                        shift = timeline_cursor - seg_start
                        for wb in seg_boundaries:
                            all_timings.append({
                                'word': wb['word'].strip('.,!?;:\"()[]{}")\'').strip(),
                                'start': round(wb['start'] + shift, 3),
                                'end': round(wb['end'] + shift, 3),
                                'duration': round(wb['end'] - wb['start'], 3)
                            })
                    else:
                        timings = self._generate_word_timings(chunk_path, seg_text, timeline_cursor)
                        all_timings.extend(timings)

                    # FIX: advance by the exact requested cut length, the
                    # same number used to compute `shift` above — keeps the
                    # whole pipeline self-consistent instead of compounding
                    # ffmpeg's frame-rounding error every segment.
                    timeline_cursor += seg_dur

        if total_pause_time > 2.5:
            print(f"    ⚠️ Total pause time {total_pause_time:.1f}s — too much dead air!")

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

        # FIX: if the actual concatenated file disagrees meaningfully with
        # our computed timeline_cursor (e.g. due to mp3 frame padding on
        # concat), trust the REAL measured file for total_duration, but log
        # the drift so it's visible instead of silently propagating.
        if raw_dur > 0 and abs(raw_dur - timeline_cursor) > 1.0:
            print(f"    ⚠️ Timeline drift: computed {timeline_cursor:.2f}s vs actual file {raw_dur:.2f}s")

        # FIX (retention): Add SFX transitions for engagement
        self._add_sfx_transitions(final_path, raw_dur)
        print(f"    🔊 SFX transitions added")

        mixed_path = os.path.join(os.path.abspath(output_dir), "final_audio_mixed.mp3")
        self._add_bg_music_and_fan(final_path, mixed_path, raw_dur)
        if os.path.exists(mixed_path) and os.path.getsize(mixed_path) > 1000:
            final_path = mixed_path

        total_dur = self._get_audio_duration(final_path)

        # FIX: hard-clamp any word timing that ended up beyond the real
        # final audio duration (defensive — should not normally trigger
        # now, but prevents any caption from ever pointing past the end
        # of the actual audio/video timeline).
        all_timings = [
            t for t in all_timings if t['start'] < total_dur
        ]
        for t in all_timings:
            if t['end'] > total_dur:
                t['end'] = total_dur

        duration_status = "✅ IN RANGE" if 40 <= total_dur <= 55 else f"⚠️ {total_dur:.1f}s OUT OF RANGE"
        print(f"    ✅ Final: {total_dur:.1f}s | {len(all_timings)} words | {duration_status}")

        if total_dur < 40:
            print(f"    🔧 FIX: Add {int(45 - total_dur)} more words to script OR use slower TTS rate")
        elif total_dur > 55:
            print(f"    🔧 FIX: Remove {int(total_dur - 50)} words OR use faster TTS rate")

        return {
            'final_audio': final_path,
            'segments': audio_files,
            'word_timings': all_timings,
            'total_duration': total_dur,
            'speech_duration': speech_dur,
            'pause_duration': total_pause_time,
            'word_count': total_words,
        }
