"""
Audio Generator - Production Ready
FULLY OPTIMIZED FOR: 35-54 Male USA/UK Audience

FEATURES:
1. Natural, soulful TTS voice (en-US-GuyNeural)
2. 120 WPM - calm adult conversation pace
3. Topic-matched gentle background music
4. Natural breathing pauses with fade
5. Room presence (subtle ambient)
6. 42-55 second duration control
7. Automatic rate adjustment
8. FFmpeg concat with error recovery
"""

import os
import asyncio
import subprocess
import shutil
import re
from typing import Dict, List, Optional, Tuple

from config.settings import AUDIO_CONFIG


class AudioGenerator:
    """
    Production Audio Generator with Natural Voice
    
    USAGE:
        audio_gen = AudioGenerator()
        audio_data = await audio_gen.generate_with_effects(
            script_segments=segments,
            output_dir="output/audio",
            topic="forgetting names"
        )
    """
    
    def __init__(self):
        # Voice: en-US-GuyNeural - Deep, calm, authoritative male voice
        self.voice = getattr(AUDIO_CONFIG, 'VOICE', 'en-US-GuyNeural')
        
        # Speech pacing: 120 WPM = calm adult conversation
        self.target_wpm = getattr(AUDIO_CONFIG, 'WORDS_PER_MINUTE', 120)
        self.base_rate = getattr(AUDIO_CONFIG, 'RATE_MIN', -6)
        self.pitch = getattr(AUDIO_CONFIG, 'PITCH', '+0Hz')
        self.volume = getattr(AUDIO_CONFIG, 'VOLUME', '+0%')
        
        # Audio quality
        self.sample_rate = 44100
        self.channels = 2
        self.audio_bitrate = "192k"
        
        # Duration targets
        self.duration_min = 42
        self.duration_max = 55
        self.target_duration = 48
        
        # Background music (very subtle)
        self.bg_volume = 0.03
        self.fan_volume = 0.008
        self.speed_factor = 1.05
        
        print(f"🎙️ AudioGenerator initialized with voice: {self.voice}")

    # ============================================================
    # TTS RATE CALCULATION
    # ============================================================
    
    def _calculate_tts_rate(self, word_count: int) -> str:
        """Calculate dynamic TTS rate based on word count"""
        rate_min = getattr(AUDIO_CONFIG, 'RATE_MIN', -8)
        rate_max = getattr(AUDIO_CONFIG, 'RATE_MAX', 8)
        
        # Calculate expected duration
        expected_duration = word_count / (self.target_wpm / 60)
        
        # Determine rate based on duration
        if expected_duration > self.duration_max + 2:
            rate = rate_min
        elif expected_duration > self.duration_max:
            rate = round(rate_min * 0.66)
        elif expected_duration > self.target_duration:
            rate = round(rate_min * 0.33)
        elif expected_duration > self.duration_min:
            rate = 0
        elif expected_duration > self.duration_min - 2:
            rate = round(rate_max * 0.5)
        else:
            rate = rate_max
        
        # Clamp to valid range
        rate = max(rate_min, min(rate_max, rate))
        prefix = "+" if rate >= 0 else ""
        rate_str = f"{prefix}{rate}%"
        
        print(f"    🎙️ Words: {word_count} | Expected: {expected_duration:.1f}s | Rate: {rate_str}")
        return rate_str

    # ============================================================
    # NATURAL BREATH PAUSE
    # ============================================================
    
    def _make_breath_pause(self, duration: float, output_path: str) -> None:
        """
        Create a natural breath pause
        - Gentle pink noise with fade in/out
        - Lowpass filtered for softness
        - Swells and fades like a real breath
        """
        fade = min(0.4, duration / 2.5)
        
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=pink:amplitude=0.015:duration={duration}',
            '-af', 
            f'lowpass=f=700,'  # Soft, not harsh
            f'afade=t=in:st=0:d={fade},'  # Fade in
            f'afade=t=out:st={max(0, duration - fade)}:d={fade}',  # Fade out
            '-ar', str(self.sample_rate),
            '-ac', str(self.channels),
            '-b:a', self.audio_bitrate,
            '-acodec', 'libmp3lame',
            output_path
        ]
        subprocess.run(cmd, capture_output=True, timeout=10)

    # ============================================================
    # TOPIC-MATCHED MUSIC
    # ============================================================
    
    def _get_topic_music_profile(self, topic: str = "") -> dict:
        """Get music profile based on topic for 35-54 male audience"""
        topic_lower = (topic or "").lower()
        
        # Memory & Brain Fog - Soft piano/cello (most common)
        if any(w in topic_lower for w in ['memory', 'forget', 'brain fog', 'remember', 'recall']):
            return {
                'name': 'soft_piano',
                'freq': 55,
                'freq2': 85,
                'lowpass': 180,
                'amplitude': 0.028,
                'volume_factor': 0.80,
                'description': '🎹 Soft piano'
            }
        
        # Sleep/Relaxation - Deep ambient
        elif any(w in topic_lower for w in ['sleep', 'wake', 'tired', 'exhausted']):
            return {
                'name': 'ambient_deep',
                'freq': 48,
                'freq2': 70,
                'lowpass': 140,
                'amplitude': 0.022,
                'volume_factor': 0.75,
                'description': '🌙 Deep ambient'
            }
        
        # Stress/Worry - Warm strings
        elif any(w in topic_lower for w in ['stress', 'anxiety', 'worry', 'pressure']):
            return {
                'name': 'warm_strings',
                'freq': 65,
                'freq2': 95,
                'lowpass': 200,
                'amplitude': 0.032,
                'volume_factor': 0.85,
                'description': '🎻 Warm strings'
            }
        
        # Default - Gentle documentary (BBC/Discovery style)
        else:
            return {
                'name': 'gentle_doc',
                'freq': 60,
                'freq2': 90,
                'lowpass': 175,
                'amplitude': 0.030,
                'volume_factor': 0.82,
                'description': '🎬 Gentle documentary'
            }

    # ============================================================
    # MIX AUDIO WITH MUSIC AND ROOM PRESENCE
    # ============================================================
    
    def _add_bg_music_and_fan(self, speech_path: str, output_path: str, 
                              total_duration: float, topic: str = ""):
        """
        Mix speech with subtle background music and room presence
        - Voice: 1.0 (full volume)
        - Music: 0.03 (barely audible, like a quiet room)
        - Fan: 0.008 (subtle room air)
        """
        music_profile = self._get_topic_music_profile(topic)
        print(f"    🎵 {music_profile['description']}")
        
        # ============================================================
        # Room presence (subtle fan noise)
        # ============================================================
        fan_path = output_path.replace('.mp3', '_fan.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anoisesrc=r={self.sample_rate}:color=brown:amplitude=0.008:duration={total_duration}',
            '-af', f'lowpass=f=400,afade=t=in:st=0:d=0.8',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', fan_path
        ], capture_output=True, timeout=30)
        
        # ============================================================
        # Topic-matched music (two sine tones for warmth)
        # ============================================================
        music_path = output_path.replace('.mp3', '_music.mp3')
        freq1 = music_profile['freq']
        freq2 = music_profile['freq2']
        lp = music_profile['lowpass']
        amp = music_profile['amplitude']
        fade_out_start = max(0, total_duration - 1.2)
        
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'sine=frequency={freq1}:duration={total_duration}',
            '-f', 'lavfi',
            '-i', f'sine=frequency={freq2}:duration={total_duration}',
            '-filter_complex',
            f'[0:a]volume={amp}[a1];'
            f'[1:a]volume={amp * 0.5}[a2];'
            f'[a1][a2]amix=inputs=2:normalize=0[mixed];'
            f'[mixed]lowpass=f={lp},'
            f'afade=t=in:st=0:d=0.6,'  # Gentle fade in
            f'afade=t=out:st={fade_out_start}:d=1.0[out]',  # Fade out
            '-map', '[out]',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', music_path
        ], capture_output=True, timeout=30)
        
        # ============================================================
        # Final mix: Voice + Fan + Music
        # ============================================================
        bg_vol = getattr(AUDIO_CONFIG, 'BG_MUSIC_VOLUME', 0.04) * music_profile['volume_factor']
        fan_vol = getattr(AUDIO_CONFIG, 'FAN_NOISE_VOLUME', 0.008)
        
        if os.path.exists(fan_path) and os.path.exists(music_path):
            subprocess.run([
                'ffmpeg', '-y',
                '-i', speech_path,
                '-i', fan_path,
                '-i', music_path,
                '-filter_complex',
                f'[0:a]volume=1.0[speech];'
                f'[1:a]volume={fan_vol}[fan];'
                f'[2:a]volume={bg_vol}[music];'
                '[speech][fan][music]amix=inputs=3:duration=first:normalize=0[out]',
                '-map', '[out]',
                '-ar', str(self.sample_rate), '-ac', str(self.channels),
                '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame',
                output_path
            ], capture_output=True, timeout=60)
            
            # Cleanup temp files
            for f in [fan_path, music_path]:
                if os.path.exists(f):
                    os.remove(f)
            
            print(f"    ✅ Voice + music + room mix complete")
        else:
            shutil.copy(speech_path, output_path)
            print(f"    ⚠️ Music mix failed, using speech only")

    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _get_audio_duration(self, path: str) -> float:
        """Get audio duration using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0.0

    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text to remove mid-sentence punctuation that causes unnatural breaths"""
        if not text:
            return ""
        
        # Convert ... to period
        text = re.sub(r"\.{2,}", ".", text)
        
        # Remove mid-sentence commas before lowercase
        text = re.sub(r",\s+(?=[a-z])", " ", text)
        
        # Remove semicolons and dashes
        text = text.replace(";", "").replace("—", " ").replace("–", " ")
        
        # Remove parentheses content
        text = re.sub(r"\(.*?\)", "", text)
        
        # Clean multiple spaces
        text = re.sub(r"  +", " ", text).strip()
        
        # Ensure ends with period
        if text and text[-1] not in ".!?":
            text += "."
        
        return text

    def _sanitize_for_tts(self, text: str) -> str:
        """Remove symbols that TTS reads literally"""
        if not text:
            return text
        
        # Remove hashtags
        text = re.sub(r'#\w+', '', text)
        text = text.replace('#', '')
        
        # Remove markdown symbols
        text = text.replace('/', ' ')
        text = re.sub(r'[*_~`]', '', text)
        
        # Clean spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _generate_word_timings_fallback(self, audio_path: str, text: str) -> List[Dict]:
        """Generate word timings if TTS boundaries are not available"""
        actual_duration = self._get_audio_duration(audio_path)
        words = text.split()
        
        if not words or actual_duration <= 0:
            return []
        
        # Weight words by character length
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
        current = 0.0
        
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

    # ============================================================
    # TTS GENERATION
    # ============================================================
    
    async def _generate_speech(self, text: str, path: str, rate: str) -> Tuple[float, List[Dict]]:
        """Generate TTS using edge-tts"""
        import edge_tts
        
        text = self._clean_text_for_tts(text)
        boundaries = []
        last_error = None
        
        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(
                    text, 
                    voice=self.voice,
                    rate=rate, 
                    volume=self.volume, 
                    pitch=self.pitch,
                    boundary="WordBoundary"
                )
                
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
                    await asyncio.wait_for(_run(), timeout=90)
                
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    break
                    
            except asyncio.TimeoutError:
                last_error = "Timeout"
                print(f"    ⚠️ TTS timeout (attempt {attempt}/3)")
            except Exception as e:
                last_error = str(e)
                print(f"    ⚠️ TTS error (attempt {attempt}/3): {e}")
            
            if attempt < 3:
                await asyncio.sleep(2)
        else:
            raise Exception(f"❌ TTS failed after 3 attempts: {last_error}")
        
        if not os.path.exists(path) or os.path.getsize(path) < 100:
            raise Exception("❌ TTS generated empty file")
        
        # HQ encode
        hq_path = path.replace('.mp3', '_hq.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', path,
            '-ar', str(self.sample_rate), 
            '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, 
            '-acodec', 'libmp3lame', hq_path
        ], capture_output=True, timeout=30)
        
        if os.path.exists(hq_path) and os.path.getsize(hq_path) > 0:
            os.replace(hq_path, path)
        
        return self._get_audio_duration(path), boundaries

    # ============================================================
    # MAIN: GENERATE AUDIO
    # ============================================================
    
    async def generate_with_effects(self, script_segments: List[Dict], 
                                     output_dir: str, 
                                     topic: str = "") -> Dict:
        """
        Generate complete audio with natural voice, music, and effects
        
        Args:
            script_segments: List of script segments with 'text' and 'is_pause'
            output_dir: Directory to save audio files
            topic: Topic for music selection
        
        Returns:
            Dict with audio_path, total_duration, word_timings
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Calculate TTS rate
        all_words = sum(
            len(s.get('text', '').split())
            for s in script_segments
            if not s.get('is_pause') and s.get('text', '').strip()
        )
        tts_rate = self._calculate_tts_rate(all_words)
        
        segment_files = []
        all_word_timings = []
        timeline_cursor = 0.0
        
        print(f"    🎙️ Generating {len(script_segments)} segments...")
        
        for idx, seg in enumerate(script_segments):
            # Handle pause segments
            if seg.get('is_pause'):
                pause_dur = float(seg.get('duration', 0.4))
                pause_path = os.path.join(output_dir, f'pause_{idx}.mp3')
                self._make_breath_pause(pause_dur, pause_path)
                
                if os.path.exists(pause_path) and os.path.getsize(pause_path) > 100:
                    segment_files.append((pause_path, pause_dur))
                timeline_cursor += pause_dur
                continue
            
            # Handle speech segments
            text = seg.get('text', '').strip()
            if not text:
                continue
            
            text = self._sanitize_for_tts(text)
            seg_path = os.path.join(output_dir, f'seg_{idx}.mp3')
            
            try:
                actual_dur, boundaries = await self._generate_speech(text, seg_path, tts_rate)
            except Exception as e:
                print(f"    ⚠️ Segment {idx} failed: {e}")
                continue
            
            if not os.path.exists(seg_path) or actual_dur <= 0:
                continue
            
            # Shift word timings to absolute timeline
            for b in boundaries:
                all_word_timings.append({
                    'word': b['word'],
                    'start': round(timeline_cursor + b['start'], 3),
                    'end': round(timeline_cursor + b['end'], 3),
                })
            
            segment_files.append((seg_path, actual_dur))
            timeline_cursor += actual_dur
        
        # Validate segments
        if not segment_files:
            raise Exception("❌ No audio segments generated")
        
        valid_files = [(p, d) for p, d in segment_files 
                       if os.path.exists(p) and os.path.getsize(p) > 100]
        
        if not valid_files:
            raise Exception("❌ No valid audio segments")
        
        # Concatenate all segments
        concat_list = os.path.join(output_dir, 'concat.txt')
        with open(concat_list, 'w') as f:
            for path, _ in valid_files:
                f.write(f"file '{os.path.abspath(path)}'\n")
        
        raw_speech = os.path.join(output_dir, 'speech_raw.mp3')
        result = subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list,
            '-ar', str(self.sample_rate), 
            '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, 
            '-acodec', 'libmp3lame',
            raw_speech
        ], capture_output=True, text=True, timeout=120)
        
        if not os.path.exists(raw_speech) or os.path.getsize(raw_speech) < 100:
            print(f"    ❌ FFmpeg concat error: {result.stderr[:500]}")
            raise Exception("❌ Audio concatenation failed")
        
        total_duration = self._get_audio_duration(raw_speech)
        
        # Mix in background music and room presence
        final_path = os.path.join(output_dir, 'final_audio.mp3')
        self._add_bg_music_and_fan(raw_speech, final_path, total_duration, topic=topic)
        
        if not os.path.exists(final_path):
            shutil.copy(raw_speech, final_path)
        
        # Generate fallback word timings if TTS didn't provide them
        if not all_word_timings:
            print("    ⚠️ No word boundaries - using fallback")
            full_text = ' '.join(
                s.get('text', '') for s in script_segments if not s.get('is_pause')
            )
            all_word_timings = self._generate_word_timings_fallback(final_path, full_text)
        
        print(f"    ✅ Audio complete: {total_duration:.1f}s | {len(all_word_timings)} words")
        
        return {
            'audio_path': final_path,
            'total_duration': total_duration,
            'word_timings': all_word_timings,
            'word_count': all_words,
        }


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING AUDIO GENERATOR\n" + "="*60)
    
    # Test segments
    test_segments = [
        {'type': 'hook', 'text': 'Your brain is ALREADY forgetting names you just heard...', 'is_pause': False},
        {'type': 'pause', 'is_pause': True, 'duration': 0.5},
        {'type': 'shock', 'text': 'Your brain processes 70,000 thoughts daily... and forgets 90% of them.', 'is_pause': False},
        {'type': 'pause', 'is_pause': True, 'duration': 0.3},
        {'type': 'story', 'text': 'The science behind memory loss is simpler than you think. Your brain has a filter that gets too good at its job after 35.', 'is_pause': False},
    ]
    
    async def test():
        audio_gen = AudioGenerator()
        result = await audio_gen.generate_with_effects(
            script_segments=test_segments,
            output_dir="test_audio",
            topic="forgetting names"
        )
        print(f"\n✅ Result: {result['total_duration']:.1f}s")
        print(f"   Words: {result['word_count']}")
        print(f"   Timings: {len(result['word_timings'])}")
    
    asyncio.run(test())