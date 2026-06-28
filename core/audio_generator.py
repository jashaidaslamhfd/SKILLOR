"""
Audio Generator - GROQ TTS (USA 2026) - GITHUB ACTIONS FIX
USES: Groq Orpheus TTS (Reliable, no 403 errors)
VOICE: daniel (Warm, Conversational, Trustworthy - PERFECT for Baby Science)
"""

import os
import asyncio
import re
import logging
import subprocess
import random
from typing import Dict, List

from groq import Groq
from config.settings import API_KEYS

logger = logging.getLogger(__name__)


class AudioGenerator:
    """Production Audio Generator — Groq TTS (Reliable)"""
    
    def __init__(self):
        self.client = Groq(api_key=API_KEYS.GROQ_API_KEY)
        self.model = "canopylabs/orpheus-v1-english"
        
        # ═══════════════════════════════════════════════════════════
        # VOICE: daniel (Male, Warm, Conversational)
        # Perfect for baby science, parenting, educational content
        # Gives Netflix documentary vibe - trustworthy and engaging
        # ═══════════════════════════════════════════════════════════
        self.voice = "daniel"  # ⭐ BEST for baby/parenting content
        
        self.sample_rate = 44100
        self.channels = 2
        self.audio_bitrate = "192k"
        
        print(f"🎙️ AudioGenerator (Groq TTS | Voice: {self.voice} [Warm/Conversational - Baby Science])")

    async def _get_audio_duration_async(self, path: str) -> float:
        """Get audio duration using ffprobe"""
        if not path or not os.path.exists(path):
            return 0.0
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10)
            if stdout:
                return float(stdout.decode().strip())
        except Exception:
            pass
        return 0.0

    def _sanitize_text(self, text: str) -> str:
        """Clean text for TTS"""
        if not text:
            return ""
        # Remove hashtags and special characters
        text = re.sub(r'#\w+', '', text)
        text = text.replace('#', '').replace('/', ' ').replace('\\', ' ')
        text = re.sub(r'[*_~`\-—–]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def _generate_word_timings(self, audio_path: str, text: str) -> List[Dict]:
        """Generate word timings with perfect sync"""
        dur = await self._get_audio_duration_async(audio_path)
        words = text.split()
        
        if not words or dur <= 0:
            return []
        
        word_duration = dur / len(words)
        timings = []
        current = 0.0
        
        for i, word in enumerate(words):
            clean = word.strip('.,!?;:\'"()[]{}')
            # Add slight variation for natural feel
            duration = word_duration * random.uniform(0.9, 1.1)
            
            # ═══════════════════════════════════════════════════════════
            # CRITICAL: First word starts at 0.0s
            # 70% of viewers decide in 1.5s - no delay allowed
            # ═══════════════════════════════════════════════════════════
            if i == 0:
                current = 0.0
            
            timings.append({
                'word': clean,
                'start': round(current, 3),
                'end': round(current + duration, 3),
                'duration': round(duration, 3)
            })
            current += duration
        
        # Fix last word to end at exact duration
        if timings:
            timings[-1]['end'] = round(dur, 3)
            timings[-1]['duration'] = round(timings[-1]['end'] - timings[-1]['start'], 3)
        
        return timings

    async def generate_with_effects(self, script_segments: List[Dict],
                                    output_dir: str, topic: str = "") -> Dict:
        """Generate audio using Groq TTS with Daniel voice"""
        os.makedirs(output_dir, exist_ok=True)
        
        # ── Extract text from segments ──
        text_parts = []
        for s in script_segments:
            if not s.get('is_pause') and s.get('text', '').strip():
                text_parts.append(s.get('text', '').strip())
        
        full_text = " ".join(text_parts)
        clean_text = self._sanitize_text(full_text)
        
        if len(clean_text.split()) <= 1:
            raise ValueError("❌ No valid script text found")
        
        final_path_wav = os.path.join(output_dir, 'final_audio.wav')
        final_path_mp3 = os.path.join(output_dir, 'final_audio.mp3')
        
        print(f"    🎙️ Generating voice (Groq TTS | Voice: {self.voice} [Warm/Conversational])")
        
        # ── Generate with Groq (with retry) ──
        success = False
        for attempt in range(1, 4):
            try:
                if hasattr(asyncio, 'to_thread'):
                    def call_groq_api():
                        response = self.client.audio.speech.create(
                            model=self.model,
                            voice=self.voice,
                            input=clean_text,
                            response_format="wav"
                        )
                        response.write_to_file(final_path_wav)
                    
                    await asyncio.to_thread(call_groq_api)
                else:
                    response = self.client.audio.speech.create(
                        model=self.model,
                        voice=self.voice,
                        input=clean_text,
                        response_format="wav"
                    )
                    response.write_to_file(final_path_wav)

                if os.path.exists(final_path_wav) and os.path.getsize(final_path_wav) > 1000:
                    print(f"      ✅ Voice generated: {os.path.getsize(final_path_wav) / 1024:.0f} KB")
                    success = True
                    break

            except Exception as e:
                print(f"      ⚠️ Attempt {attempt}/3 failed: {e}")
                if attempt < 3:
                    await asyncio.sleep(6)

        if not success:
            raise RuntimeError("❌ Groq TTS failed after 3 attempts")

        # ── Convert WAV to MP3 ──
        cmd = [
            'ffmpeg', '-y', '-i', final_path_wav,
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', final_path_mp3
        ]
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(process.communicate(), timeout=30)
        except Exception as e:
            print(f"      ⚠️ MP3 conversion: {e}")

        # ── Cleanup WAV ──
        if os.path.exists(final_path_wav):
            try:
                os.remove(final_path_wav)
            except Exception:
                pass

        # ── Get duration and timings ──
        total_duration = await self._get_audio_duration_async(final_path_mp3)
        
        if total_duration <= 0:
            raise RuntimeError("Audio generation produced empty file")
        
        word_timings = await self._generate_word_timings(final_path_mp3, clean_text)
        
        print(f"    ✅ Audio: {total_duration:.1f}s | Words: {len(word_timings)}")
        print(f"    🎯 Voice: {self.voice} (Warm, Conversational - Perfect for Baby Content)")
        
        return {
            'audio_path': final_path_mp3,
            'final_audio': final_path_mp3,
            'total_duration': total_duration,
            'word_timings': word_timings,
            'word_count': len(clean_text.split()),
            'voice_used': self.voice,
        }


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("🚀 TESTING AUDIO GENERATOR (Daniel Voice)\n" + "=" * 60)
        
        gen = AudioGenerator()
        
        # Test segments
        segments = [
            {'type': 'hook', 'text': "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...", 'is_pause': False},
            {'type': 'pause', 'is_pause': True, 'duration': 0.3},
            {'type': 'shock', 'text': "The first 1000 days decide your child's entire future brain power.", 'is_pause': False},
            {'type': 'pause', 'is_pause': True, 'duration': 0.3},
            {'type': 'story', 'text': "Scientists have discovered that every single interaction you have with your baby builds their brain cells. Talking, singing, even just holding them.", 'is_pause': False},
            {'type': 'pause', 'is_pause': True, 'duration': 0.3},
            {'type': 'ctr', 'text': "Comment BABY if your little one does this too! Follow for more baby science.", 'is_pause': False},
        ]
        
        result = await gen.generate_with_effects(segments, 'test_audio', 'baby brain development')
        
        print(f"\n✅ Result:")
        print(f"   Duration: {result['total_duration']:.1f}s")
        print(f"   Words: {result['word_count']}")
        print(f"   Audio: {result['audio_path']}")
        print(f"   Voice: {result['voice_used']}")
        print(f"   Timings: {len(result['word_timings'])}")
        if result['word_timings']:
            print(f"   First word: {result['word_timings'][0]['start']:.2f}s (should be 0.0s)")
            print(f"   Last word: {result['word_timings'][-1]['end']:.2f}s")
    
    asyncio.run(test())
