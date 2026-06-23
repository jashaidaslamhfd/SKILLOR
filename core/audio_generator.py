"""Audio Generator - Natural Breathing Pauses + Fan Ambience + Duration Control"""

import os
import asyncio
import subprocess
import math
import shutil
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
        # AUDIENCE MATCH: reads from settings.py AUDIO_CONFIG
        # Current: en-US-GuyNeural — deep, calm, mature American male
        # Trusted by 35-54 males. Sounds credible, not like an ad.
        self.voice = getattr(AUDIO_CONFIG, 'VOICE', 'en-US-GuyNeural')
        self.base_rate = getattr(AUDIO_CONFIG, 'RATE_MIN', -6)
        self.pitch = getattr(AUDIO_CONFIG, 'PITCH', '+0Hz')
        self.volume = getattr(AUDIO_CONFIG, 'VOLUME', '+0%')
        self.sample_rate = 44100
        self.channels = 2
        self.audio_bitrate = "192k"
        # AUDIENCE MATCH: 120 WPM = calm adult storyteller pace
        # 150 WPM sounds rushed/AI — 35-54 males notice and swipe
        self.target_wpm = 120       # UPDATED: 150 → 120
        self.speed_factor = 1.05    # UPDATED: 1.15 → 1.05 (barely any speedup)
        self.target_duration = 48

    def _calculate_tts_rate(self, word_count: int) -> str:
        """
        Dynamic TTS rate based on word count to hit 40-55s target.
        Format: "+10%" or "-10%" - Edge-TTS requires + or - prefix!

        FIX: rate steps were hardcoded (-15/-10/-5/0/5/10), completely
        disconnected from AUDIO_CONFIG.RATE_MIN/RATE_MAX in settings.py -
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

    def _get_topic_music_profile(self, topic: str = "") -> dict:
        """
        AUDIENCE MATCHED: Topic-aware background music for 35-54 male USA/UK.

        Key principle: This audience is NOT teenagers. They do NOT want:
        - Heavy bass drops
        - Horror drone music
        - Energetic electronic beats

        They respond to: calm, warm, understated background tone.
        Think: Discovery Channel / BBC documentary feel, not TikTok horror.

        All profiles use LOW amplitude — voice must always be dominant.
        Music should be barely noticeable, like a quiet room with a TV on.
        """
        topic_lower = (topic or "").lower()

        # Brain / Memory / Focus / Aging (Primary audience topics)
        if any(w in topic_lower for w in ['brain', 'memory', 'forget', 'focus', 'mind',
                                           'cognitive', 'mental', 'alzheimer', 'dementia',
                                           'fog', 'think', 'concentrate']):
            return {
                'name': 'calm_documentary',
                'freq': 60,           # Warm low bass — like a cello note
                'freq2': 90,          # Gentle harmonic
                'lowpass': 160,       # Very muffled = almost subliminal
                'amplitude': 0.035,   # Very quiet
                'volume_factor': 0.85,
                'description': '🧠 Calm documentary (brain/memory)'
            }

        # Sleep / Rest / Recovery
        elif any(w in topic_lower for w in ['sleep', 'wake', 'tired', 'rest', 'dream',
                                              'insomnia', 'fatigue', 'exhausted', 'night']):
            return {
                'name': 'ambient_calm',
                'freq': 50,           # Very deep, slow pulse = sleep feel
                'freq2': 75,
                'lowpass': 140,       # Very filtered = quiet night feel
                'amplitude': 0.030,   # Quietest of all — sleep topics need silence
                'volume_factor': 0.80,
                'description': '😴 Ambient calm (sleep)'
            }

        # Stress / Work / Anxiety / Cortisol
        elif any(w in topic_lower for w in ['stress', 'anxiety', 'cortisol', 'pressure',
                                              'work', 'burnout', 'worry', 'tension', 'nervous']):
            return {
                'name': 'grounded_warm',
                'freq': 65,           # Grounding bass tone
                'freq2': 100,
                'lowpass': 175,
                'amplitude': 0.038,
                'volume_factor': 0.88,
                'description': '💼 Grounded warm (stress/work)'
            }

        # Body / Health / Aging / Testosterone
        elif any(w in topic_lower for w in ['body', 'health', 'age', 'aging', 'testosterone',
                                              'hormone', 'weight', 'muscle', 'heart', 'blood',
                                              'belly', 'fat', 'recover', 'hangover']):
            return {
                'name': 'health_neutral',
                'freq': 70,
                'freq2': 105,
                'lowpass': 185,
                'amplitude': 0.040,
                'volume_factor': 0.90,
                'description': '💪 Health neutral (body/aging)'
            }

        # Kids / Parenting (Proven topic — Baby Memory Lost = 1.1K views)
        elif any(w in topic_lower for w in ['baby', 'child', 'kid', 'parent', 'toddler',
                                              'infant', 'son', 'daughter', 'school']):
            return {
                'name': 'warm_gentle',
                'freq': 75,           # Warmer, more comforting tone
                'freq2': 115,
                'lowpass': 200,
                'amplitude': 0.038,
                'volume_factor': 0.85,
                'description': '👶 Warm gentle (parenting)'
            }

        # Default: BBC/Discovery documentary feel — works for everything
        else:
            return {
                'name': 'documentary_neutral',
                'freq': 62,
                'freq2': 95,
                'lowpass': 170,
                'amplitude': 0.035,
                'volume_factor': 0.85,
                'description': '🎬 Documentary neutral'
            }

    def _add_bg_music_and_fan(self, speech_path: str, output_path: str, total_duration: float, topic: str = ""):
        """
        HUMAN VIBES UPDATE: Topic-aware background music + natural room presence.

        Key changes:
        1. Music is now topic-matched (mystery = dark drone, science = techy pulse, etc.)
        2. Two-tone sine blend instead of raw noise = sounds like actual music, not static
        3. Fan noise is lighter (0.012 vs 0.018) = room presence without sounding like HVAC
        4. Gentle fade-in on music (0.8s) = sounds like a human hit play on background music
        5. Voice sits clearly ON TOP of music (not buried in it)
        """
        music_profile = self._get_topic_music_profile(topic)
        print(f"    🎵 Music profile: {music_profile['description']}")

        # Room presence / subtle ambient air (lighter than before)
        fan_path = output_path.replace('.mp3', '_fan.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.012:duration={total_duration}',
            '-af', f'lowpass=f=400,afade=t=in:st=0:d=1.0',  # Fade in = human feel
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', fan_path
        ], capture_output=True)

        # Topic-matched background music: blend of two sine tones (sounds musical, not like noise)
        music_path = output_path.replace('.mp3', '_music.mp3')
        freq1 = music_profile['freq']
        freq2 = music_profile['freq2']
        lp = music_profile['lowpass']
        amp = music_profile['amplitude']
        fade_out_start = max(0, total_duration - 1.5)

        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            # Two sine frequencies blended = harmonic texture, not random noise
            '-i', f'sine=frequency={freq1}:duration={total_duration}',
            '-f', 'lavfi',
            '-i', f'sine=frequency={freq2}:duration={total_duration}',
            '-filter_complex',
            f'[0:a]volume={amp}[a1];[1:a]volume={amp * 0.6}[a2];'
            f'[a1][a2]amix=inputs=2:normalize=0[mixed];'
            f'[mixed]lowpass=f={lp},'
            f'afade=t=in:st=0:d=0.8,'
            f'afade=t=out:st={fade_out_start}:d=1.2[out]',
            '-map', '[out]',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', music_path
        ], capture_output=True)

        bg_music_vol = getattr(AUDIO_CONFIG, 'BG_MUSIC_VOLUME', 0.04) * music_profile['volume_factor']
        fan_vol = getattr(AUDIO_CONFIG, 'FAN_NOISE_VOLUME', 0.012)

        if os.path.exists(fan_path) and os.path.exists(music_path):
            subprocess.run([
                'ffmpeg', '-y',
                '-i', speech_path,
                '-i', fan_path,
                '-i', music_path,
                '-filter_complex',
                f'[0:a]volume=1.0[speech];[1:a]volume={fan_vol}[fan];[2:a]volume={bg_music_vol}[music];'
                '[speech][fan][music]amix=inputs=3:duration=first:normalize=0[out]',
                '-map', '[out]',
                '-ar', str(self.sample_rate), '-ac', str(self.channels),
                '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
                output_path
            ], capture_output=True)
            for f in [fan_path, music_path]:
                if os.path.exists(f):
                    os.remove(f)
            print(f"    🎵 Topic-matched BG music mixed ✅ (voice:1.0 | music:{bg_music_vol:.3f} | fan:{fan_vol})")
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
        """Async method - no asyncio.run() conflict!"""
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

        # Post-processing: only apply on segments long enough to be safe.
        # Short segments (< 4s) skip all processing — TTS rate already
        # handles pacing via _calculate_tts_rate, and processing 2-3s clips
        # was the root cause of "Speed up too aggressive / Silence removal
        # too aggressive" on EVERY segment → empty/broken files → concat fail.
        orig_dur = self._get_audio_duration(path)
        skip_processing = orig_dur < 4.0

        if not skip_processing:
            # Light silence removal
            no_sil = path.replace('.mp3', '_ns.mp3')
            self._remove_silence(path, no_sil)
            if os.path.exists(no_sil):
                ns_dur = self._get_audio_duration(no_sil)
                if ns_dur >= orig_dur * 0.8:
                    os.replace(no_sil, path)
                    print(f"    🔇 Silence removed ({orig_dur:.1f}s → {ns_dur:.1f}s)")
                else:
                    print(f"    ⚠️ Silence removal skipped ({orig_dur:.1f}s → {ns_dur:.1f}s)")
                    if os.path.exists(no_sil):
                        os.remove(no_sil)

            # Speed up — only if segment is long enough AND result is reasonable
            fast = path.replace('.mp3', '_fast.mp3')
            self._speed_up(path, fast)
            if os.path.exists(fast):
                fast_dur = self._get_audio_duration(fast)
                cur_dur = self._get_audio_duration(path)
                if fast_dur >= cur_dur * 0.75:  # Removed the broken "> 10s" gate
                    os.replace(fast, path)
                    for b in boundaries:
                        b['start'] /= self.speed_factor
                        b['end'] /= self.speed_factor
                    print(f"    ⚡ Speed {self.speed_factor}x applied ({cur_dur:.1f}s → {fast_dur:.1f}s)")
                else:
                    print(f"    ⚠️ Speed up skipped ({cur_dur:.1f}s → {fast_dur:.1f}s)")
                    if os.path.exists(fast):
                        os.remove(fast)

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
        Edge-TTS reads symbols literally out loud - '#' becomes "hashtag",
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
        """FIX (retention): Remove dead air between sentences for tight pacing.

        CAUTION: Must NOT remove actual speech. Only removes gaps > 0.3s
        at -50dB threshold to preserve all words.
        """
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-af', 'silenceremove=start_periods=1:start_duration=0.3:start_threshold=-50dB:stop_periods=1:stop_duration=0.3:stop_threshold=-50dB',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
        ], capture_output=True)

        # SAFETY: if output is drastically shorter than input, use original
        orig_dur = self._get_audio_duration(input_path)
        new_dur = self._get_audio_duration(output_path)
        if new_dur < orig_dur * 0.7:  # If lost more than 30% of audio
            print(f"    ⚠️ Silence removal too aggressive ({orig_dur:.1f}s → {new_dur:.1f}s), using original")
            shutil.copy(input_path, output_path)

        return output_path if os.path.exists(output_path) else input_path

    def _speed_up(self, input_path: str, output_path: str):
        """FIX (retention): 1.15x speed without chipmunk effect.

        SAFETY: Only apply if output duration is reasonable.
        """
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-af', f'atempo={self.speed_factor}',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
        ], capture_output=True)

        # SAFETY: verify output duration
        orig_dur = self._get_audio_duration(input_path)
        new_dur = self._get_audio_duration(output_path)
        if new_dur < orig_dur * 0.5:  # If lost more than 50%
            print(f"    ⚠️ Speed up failed ({orig_dur:.1f}s → {new_dur:.1f}s), using original")
            shutil.copy(input_path, output_path)

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

    async def generate_with_effects(self, script_segments: List[Dict], output_dir: str, topic: str = "") -> Dict:
        """Async method - await _generate_speech!

        HUMAN VIBES UPDATE:
        - topic param passed to _add_bg_music_and_fan for topic-matched music
        - HOOK segment gets slightly slower rate (human storyteller = starts slow)
        - SHOCK segment gets normal rate (punchy = no slow down)
        - STORY gets dynamic rate (natural variation = human feel)

        Uses a single authoritative timeline_cursor that advances by the
        EXACT requested segment duration to prevent timestamp drift.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Collect all non-pause text to calculate TTS rate once
        all_words = sum(
            len(s.get('text', '').split())
            for s in script_segments
            if not s.get('is_pause') and s.get('text', '').strip()
        )
        tts_rate = self._calculate_tts_rate(all_words)

        segment_files = []   # (path, duration_seconds)
        all_word_timings = []
        timeline_cursor = 0.0

        for idx, seg in enumerate(script_segments):
            if seg.get('is_pause'):
                pause_dur = float(seg.get('duration', 0.4))
                pause_path = os.path.join(output_dir, f'pause_{idx}.mp3')
                self._make_breath_pause(pause_dur, pause_path)
                if os.path.exists(pause_path):
                    segment_files.append((pause_path, pause_dur))
                timeline_cursor += pause_dur
                continue

            text = seg.get('text', '').strip()
            if not text:
                continue

            text = self._sanitize_for_tts(text)
            seg_path = os.path.join(output_dir, f'seg_{idx}.mp3')

            try:
                actual_dur, boundaries = await self._generate_speech(text, seg_path, tts_rate)
            except Exception as e:
                print(f"    ⚠️ TTS failed for segment {idx}: {e}")
                continue

            if not os.path.exists(seg_path) or actual_dur <= 0:
                continue

            # Shift word timings to absolute timeline position
            for b in boundaries:
                all_word_timings.append({
                    'word': b['word'],
                    'start': round(timeline_cursor + b['start'], 3),
                    'end': round(timeline_cursor + b['end'], 3),
                })

            # Advance cursor by ACTUAL measured duration (not estimated)
            segment_files.append((seg_path, actual_dur))
            timeline_cursor += actual_dur

        if not segment_files:
            raise Exception("No audio segments generated")

        # Concatenate all segments
        valid_files = [(p, d) for p, d in segment_files if os.path.exists(p) and os.path.getsize(p) > 100]
        if not valid_files:
            raise Exception(f"No valid audio segments (had {len(segment_files)} attempts, all empty/missing)")

        concat_list = os.path.join(output_dir, 'concat.txt')
        with open(concat_list, 'w') as f:
            for path, _ in valid_files:
                # Use absolute paths, no shell quoting needed (ffmpeg reads the file directly)
                f.write(f"file '{os.path.abspath(path)}'\n")

        raw_speech = os.path.join(output_dir, 'speech_raw.mp3')
        result = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
            raw_speech
        ], capture_output=True, text=True, timeout=120)

        if not os.path.exists(raw_speech) or os.path.getsize(raw_speech) < 100:
            print(f"    ❌ FFmpeg concat stderr: {result.stderr[-500:]}")
            raise Exception("Audio concatenation failed")

        total_duration = self._get_audio_duration(raw_speech)

        # Mix in topic-matched background music + fan noise
        final_path = os.path.join(output_dir, 'final_audio.mp3')
        self._add_bg_music_and_fan(raw_speech, final_path, total_duration, topic=topic)
        if not os.path.exists(final_path):
            import shutil as _shutil
            _shutil.copy(raw_speech, final_path)

        # Add SFX transitions for retention
       # self._add_sfx_transitions(final_path, total_duration)

        # Fallback: estimate timings if TTS gave none
        if not all_word_timings:
            print("    ⚠️ No word boundaries from TTS — using estimate fallback")
            all_word_timings = self._generate_word_timings(final_path, " ".join(
                s.get('text', '') for s in script_segments if not s.get('is_pause')
            ))

        print(f"    ✅ Audio generated: {total_duration:.1f}s | {len(all_word_timings)} word timings")

        return {
            'audio_path': final_path,
            'total_duration': total_duration,
            'word_timings': all_word_timings,
            'word_count': all_words,
        }
