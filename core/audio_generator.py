"""
Audio Generator â€” FIXED v3
Fixes:
  1. Sine tones REMOVED â€” replaced with brown noise music bed (no more tik-tik)
  2. audio_path key confirmed correct
  3. edge-tts timeout 120s + proper retry
  4. Humanizer EQ for warm natural voice
"""

import os
import asyncio
import subprocess
import shutil
import re
import random
from typing import Dict, List, Tuple

from config.settings import AUDIO_CONFIG


class AudioGenerator:

    def __init__(self):
        self.voice        = getattr(AUDIO_CONFIG, 'VOICE',           'en-US-GuyNeural')
        self.target_wpm   = getattr(AUDIO_CONFIG, 'WORDS_PER_MINUTE', 120)
        self.pitch        = getattr(AUDIO_CONFIG, 'PITCH',            '+0Hz')
        self.volume       = getattr(AUDIO_CONFIG, 'VOLUME',           '+0%')
        self.sample_rate  = 44100
        self.channels     = 2
        self.audio_bitrate = "192k"
        self.duration_min  = 42
        self.duration_max  = 55
        self.target_duration = 48
        print(f"ðŸŽ™ï¸ AudioGenerator v3 | voice: {self.voice}")

    # â”€â”€ TTS rate â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _calculate_tts_rate(self, word_count: int) -> str:
        rate_min = getattr(AUDIO_CONFIG, 'RATE_MIN', -8)
        rate_max = getattr(AUDIO_CONFIG, 'RATE_MAX',  8)
        expected = word_count / (self.target_wpm / 60)
        if   expected > self.duration_max + 2: rate = rate_min
        elif expected > self.duration_max:     rate = round(rate_min * 0.66)
        elif expected > self.target_duration:  rate = round(rate_min * 0.33)
        elif expected > self.duration_min:     rate = 0
        elif expected > self.duration_min - 2: rate = round(rate_max * 0.5)
        else:                                  rate = rate_max
        rate = max(rate_min, min(rate_max, rate))
        prefix = "+" if rate >= 0 else ""
        print(f"    ðŸŽ™ï¸ Words:{word_count} Expected:{expected:.1f}s Rate:{prefix}{rate}%")
        return f"{prefix}{rate}%"

    # â”€â”€ Breath pause â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _make_breath_pause(self, duration: float, output_path: str):
        fade = min(0.4, duration / 2.5)
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=pink:amplitude=0.012:duration={duration}',
            '-af', f'lowpass=f=600,afade=t=in:st=0:d={fade},afade=t=out:st={max(0,duration-fade)}:d={fade}',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
        ], capture_output=True, timeout=10)

    # â”€â”€ Music bed â€” NO SINE TONES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _add_bg_music_and_fan(self, speech_path: str, output_path: str, total_duration: float, topic: str = ""):
        """
        Brown-noise music bed â€” completely replaces sine tones.
        Brown noise filtered through EQ sounds like a warm music bed.
        Zero ticking, zero buzzing.
        """
        topic_lower = topic.lower()

        # Pick EQ profile based on topic
        if any(w in topic_lower for w in ['memory', 'forget', 'brain', 'remember']):
            lp, hp, amp = 220, 60, 0.032
        elif any(w in topic_lower for w in ['sleep', 'tired', 'exhausted']):
            lp, hp, amp = 160, 40, 0.026
        elif any(w in topic_lower for w in ['stress', 'anxiety', 'worry']):
            lp, hp, amp = 250, 70, 0.038
        else:
            lp, hp, amp = 200, 55, 0.030

        fade_out = max(0, total_duration - 1.5)

        # Room presence
        fan_path = output_path.replace('.mp3', '_fan.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.005:duration={total_duration}',
            '-af', f'lowpass=f=300,afade=t=in:st=0:d=1.0,afade=t=out:st={max(0,total_duration-1.0)}:d=1.0',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', fan_path
        ], capture_output=True, timeout=30)

        # Warm music bed (brown noise shaped â€” NO sine waves)
        music_path = output_path.replace('.mp3', '_music.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude={amp}:duration={total_duration}',
            '-af', (
                f'highpass=f={hp},'
                f'lowpass=f={lp},'
                f'equalizer=f=120:t=o:w=60:g=3,'
                f'equalizer=f=800:t=o:w=400:g=-4,'
                f'aecho=0.7:0.5:30:0.15,'
                f'afade=t=in:st=0:d=1.2,'
                f'afade=t=out:st={fade_out}:d=1.5'
            ),
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', music_path
        ], capture_output=True, timeout=30)

        # 3-way mix: Voice + Fan + Music
        if os.path.exists(fan_path) and os.path.exists(music_path):
            result = subprocess.run([
                'ffmpeg', '-y',
                '-i', speech_path, '-i', fan_path, '-i', music_path,
                '-filter_complex',
                '[0:a]volume=1.0[speech];'
                '[1:a]volume=0.005[fan];'
                '[2:a]volume=0.022[music];'
                '[speech][fan][music]amix=inputs=3:duration=first:normalize=0[out]',
                '-map', '[out]',
                '-ar', str(self.sample_rate), '-ac', str(self.channels),
                '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', output_path
            ], capture_output=True, timeout=60)

            for f in [fan_path, music_path]:
                if os.path.exists(f):
                    os.remove(f)

            if result.returncode == 0 and os.path.exists(output_path):
                print("    âœ… Voice + music bed mixed")
                return

        shutil.copy(speech_path, output_path)
        print("    âš ï¸ Mix failed â€” speech only")

    # â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _get_audio_duration(self, path: str) -> float:
        try:
            r = subprocess.run([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return float(r.stdout.strip())
        except Exception:
            pass
        return 0.0

    def _clean_text_for_tts(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r",\s+(?=[a-z])", " ", text)
        text = text.replace(";","").replace("â€”"," ").replace("â€“"," ")
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"  +", " ", text).strip()
        if text and text[-1] not in ".!?": text += "."
        return text

    def _sanitize_for_tts(self, text: str) -> str:
        if not text: return text
        text = re.sub(r'#\w+', '', text)
        text = text.replace('#','').replace('/',' ')
        text = re.sub(r'[*_~`]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _generate_word_timings_fallback(self, audio_path: str, text: str) -> List[Dict]:
        dur = self._get_audio_duration(audio_path)
        words = text.split()
        if not words or dur <= 0: return []
        weights = [1.0 + (0.10 if len(w.strip('.,!?;:\"\' ')) > 8 else 0.05 if len(w.strip('.,!?;:\"\' ')) > 5 else 0) for w in words]
        scale = dur / sum(weights)
        timings, cur = [], 0.0
        for word, weight in zip(words, weights):
            clean = word.strip('.,!?;:\"()[]{}"\'')
            d = weight * scale
            timings.append({'word': clean, 'start': round(cur, 3), 'end': round(cur + d, 3), 'duration': round(d, 3)})
            cur += d
        return timings

    # â”€â”€ TTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def _generate_speech(self, text: str, path: str, rate: str) -> Tuple[float, List[Dict]]:
        import edge_tts
        text = self._clean_text_for_tts(text)
        boundaries = []
        last_error = None

        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(text, voice=self.voice, rate=rate, volume=self.volume, pitch=self.pitch)
                with open(path, "wb") as f:
                    async def _run():
                        async for chunk in comm.stream():
                            if chunk["type"] == "audio":
                                f.write(chunk["data"])
                            elif chunk["type"] == "WordBoundary":
                                boundaries.append({
                                    "word":  chunk["text"],
                                    "start": chunk["offset"] / 10_000_000,
                                    "end":   (chunk["offset"] + chunk["duration"]) / 10_000_000,
                                })
                    await asyncio.wait_for(_run(), timeout=120)
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    break
            except asyncio.TimeoutError:
                last_error = "Timeout"
                print(f"    âš ï¸ TTS timeout attempt {attempt}/3")
            except Exception as e:
                last_error = str(e)
                print(f"    âš ï¸ TTS error attempt {attempt}/3: {e}")
            if attempt < 3:
                await asyncio.sleep(3)
        else:
            raise Exception(f"TTS failed: {last_error}")

        if not os.path.exists(path) or os.path.getsize(path) < 100:
            raise Exception("TTS empty file")

        # HQ encode
        hq = path.replace('.mp3', '_hq.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', path,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', hq
        ], capture_output=True, timeout=30)
        if os.path.exists(hq) and os.path.getsize(hq) > 0:
            os.replace(hq, path)

        # Humanizer
        tempo = round(random.uniform(0.986, 1.014), 4)
        human = path.replace('.mp3', '_human.mp3')
        r = subprocess.run([
            'ffmpeg', '-y', '-i', path,
            '-af', (
                f'atempo={tempo},'
                'equalizer=f=120:t=o:w=80:g=3.0,'
                'equalizer=f=250:t=o:w=100:g=1.5,'
                'equalizer=f=7000:t=o:w=2000:g=-3.0,'
                'equalizer=f=10000:t=o:w=3000:g=-1.5,'
                'aecho=0.8:0.6:35:0.20,'
                'acompressor=threshold=0.45:ratio=2.5:attack=6:release=100:makeup=1.15,'
                'loudnorm=I=-14:TP=-1.5:LRA=8'
            ),
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', human
        ], capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.exists(human) and os.path.getsize(human) > 0:
            os.replace(human, path)

        return self._get_audio_duration(path), boundaries

    # â”€â”€ MAIN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def generate_with_effects(self, script_segments: List[Dict],
                                    output_dir: str, topic: str = "") -> Dict:
        os.makedirs(output_dir, exist_ok=True)

        all_words = sum(
            len(s.get('text', '').split())
            for s in script_segments
            if not s.get('is_pause') and s.get('text', '').strip()
        )
        tts_rate = self._calculate_tts_rate(all_words)

        segment_files, all_word_timings, cursor = [], [], 0.0
        print(f"    ðŸŽ™ï¸ Generating {len(script_segments)} segments...")

        for idx, seg in enumerate(script_segments):
            if seg.get('is_pause'):
                dur = float(seg.get('duration', 0.4))
                p = os.path.join(output_dir, f'pause_{idx}.mp3')
                self._make_breath_pause(dur, p)
                if os.path.exists(p) and os.path.getsize(p) > 100:
                    segment_files.append((p, dur))
                cursor += dur
                continue

            text = seg.get('text', '').strip()
            if not text: continue
            text = self._sanitize_for_tts(text)
            seg_path = os.path.join(output_dir, f'seg_{idx}.mp3')

            try:
                actual_dur, boundaries = await self._generate_speech(text, seg_path, tts_rate)
            except Exception as e:
                print(f"    âš ï¸ Segment {idx} failed: {e}")
                continue

            if not os.path.exists(seg_path) or actual_dur <= 0: continue

            for b in boundaries:
                all_word_timings.append({
                    'word': b['word'],
                    'start': round(cursor + b['start'], 3),
                    'end':   round(cursor + b['end'], 3),
                })
            segment_files.append((seg_path, actual_dur))
            cursor += actual_dur

        if not segment_files:
            raise Exception("No audio segments generated")

        valid = [(p, d) for p, d in segment_files if os.path.exists(p) and os.path.getsize(p) > 100]
        if not valid:
            raise Exception("No valid audio segments")

        concat_list = os.path.join(output_dir, 'concat.txt')
        with open(concat_list, 'w') as f:
            for path, _ in valid:
                f.write(f"file '{os.path.abspath(path)}'\n")

        raw_speech = os.path.join(output_dir, 'speech_raw.mp3')
        r = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', raw_speech
        ], capture_output=True, text=True, timeout=120)

        if not os.path.exists(raw_speech) or os.path.getsize(raw_speech) < 100:
            raise Exception(f"Concat failed: {r.stderr[:300]}")

        total_duration = self._get_audio_duration(raw_speech)
        final_path = os.path.join(output_dir, 'final_audio.mp3')
        self._add_bg_music_and_fan(raw_speech, final_path, total_duration, topic=topic)

        if not os.path.exists(final_path):
            shutil.copy(raw_speech, final_path)

        if not all_word_timings:
            full_text = ' '.join(s.get('text','') for s in script_segments if not s.get('is_pause'))
            all_word_timings = self._generate_word_timings_fallback(final_path, full_text)

        print(f"    âœ… Audio: {total_duration:.1f}s | {len(all_word_timings)} word timings")

        return {
            'audio_path':     final_path,
            'final_audio':    final_path,
            'total_duration': total_duration,
            'word_timings':   all_word_timings,
            'word_count':     all_words,
    }
