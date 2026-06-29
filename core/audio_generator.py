"""
Audio Generator - GROQ TTS (USA 2026) - PRODUCTION GRADE
INTEGRATED PRODUCTION UPGRADES & FIXES:
1. 🛡️ API Key & Startup Validation
2. 🚀 Memory Efficient Chunk Processing & Sentence Breaker (< 300 words)
3. 🔁 Exponential Backoff Retry Strategy (2s, 4s, 8s, 16s) with Timeout Execution
4. 🔤 Advanced Emoji & Unsafe Symbol Sanitization
5. 🔊 Professional Audio Processing (Loudnorm Normalization, Silence Trim, Concatenation)
6. 🔎 Strict FFmpeg & MP3 Existence/Corruption Validation (Retaining WAV until validated)
7. 📝 Structural Logging via standard logger
8. 🧩 Deterministic Word Timings & Dynamic Voice Assignment (Configurable voice parameter)
9. 💾 Hash-Based Request Caching to prevent duplicate generation calls
"""

import os
import asyncio
import re
import logging
import subprocess
import hashlib
import json
from typing import Dict, List, Optional

from groq import Groq
from config.settings import API_KEYS

logger = logging.getLogger(__name__)

class AudioGenerator:
    """Production Audio Generator — Groq TTS (Reliable, Resilient, Scalable)"""
    
    def __init__(self, voice: str = "daniel"):
        # 1. API Key Check
        if not API_KEYS or not getattr(API_KEYS, 'GROQ_API_KEY', None):
            raise ValueError("❌ CRITICAL ERROR: GROQ_API_KEY is empty or missing from config.settings")
            
        self.client = Groq(api_key=API_KEYS.GROQ_API_KEY)
        self.model = "canopylabs/orpheus-v1-english"
        
        # 16. Voice Flexibility Configurable Parameter
        self.voice = voice 
        
        self.sample_rate = 44100
        self.channels = 1
        self.audio_bitrate = "192k"
        self.chunk_word_limit = 350
        self.cache_dir = ".tts_cache"
        
        logger.info(f"🎙️ Initialized AudioGenerator (Groq TTS | Voice: {self.voice} [Warm/Conversational])")

    async def _get_audio_duration_async(self, path: str) -> float:
        """Get audio duration safely using ffprobe"""
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
        except Exception as e:
            logger.warning(f"⚠️ ffprobe duration read issue: {e}")
        return 0.0

    def _sanitize_text(self, text: str) -> str:
        """
        11. Extended Text Sanitization.
        Clean text for TTS, scrubbing emojis, symbols, and irregular spacing,
        preventing unexpected TTS engine crashes/robotic output.
        """
        if not text:
            return ""
        
        # Remove emojis, special unicode characters,™ ® ©, hidden control characters
        emoji_pattern = re.compile(
            "["
            "\U00010000-\U0010ffff"  # All emojis and wide unicode
"]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)
        
        # Remove specific symbols, trademark chars, and hashtags
        text = re.sub(r'[😀😂🔥💯™®©😀-🙏\U0001F000-\U0001FAAF]', '', text)
        text = re.sub(r'#\w+', '', text)
        text = text.replace('#', '').replace('/', ' ').replace('\\', ' ')
        text = re.sub(r'[*_~`\-—–]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _break_into_chunks(self, text: str) -> List[str]:
        """
        2 & 12. Very Long Script Management and Sentence Breakers.
        Splits scripts at punctuation boundaries into chunks under 350 words.
        """
        words = text.split()
        if len(words) <= self.chunk_word_limit:
            return [text]

        chunks = []
        current_chunk = []
        current_word_count = 0
        
        # Regex breaking cleanly at sentence-ending punctuation
        sentences = re.split(r'(?<=[.?!])\s+', text)
        
        for sentence in sentences:
            sentence_words = sentence.split()
            if current_word_count + len(sentence_words) > self.chunk_word_limit:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                # If a single sentence is massive (> limit), chop it strictly
                if len(sentence_words) > self.chunk_word_limit:
                    for i in range(0, len(sentence_words), self.chunk_word_limit):
                        sub_sentence = " ".join(sentence_words[i:i + self.chunk_word_limit])
                        chunks.append(sub_sentence)
                    continue
            
            current_chunk.extend(sentence_words)
            current_word_count += len(sentence_words)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def _call_groq_api_with_retry(self, text_chunk: str, output_wav_path: str):
        """
        3, 4 & 17. Exponential Backoff & Timeout Engine (2s, 4s, 8s, 16s).
        Handles specific API, connection, timeout, and IO failures.
        """
        max_retries = 4
        base_delay = 2.0
        
        for attempt in range(1, max_retries + 1):
            try:
                def call_groq():
                    response = self.client.audio.speech.create(
                        model=self.model,
                        voice=self.voice,
                        input=text_chunk,
                        response_format="wav"
                    )
                    response.write_to_file(output_wav_path)

                # 4. Asynchronous timeout protection
                await asyncio.wait_for(asyncio.to_thread(call_groq), timeout=45.0)
                
                if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 1000:
                    logger.info(f"      ✅ Chunk voice generated: {os.path.getsize(output_wav_path) / 1024:.0f} KB")
                    return
                    
            except asyncio.TimeoutError:
                logger.error(f"   ⏱️ Groq TTS connection hung/timed out on attempt {attempt}/{max_retries}")
            except Exception as e:
                logger.warning(f"   ⚠️ Groq API issue on attempt {attempt}/{max_retries}: {e}")
                
            if attempt < max_retries:
                sleep_duration = base_delay * (2 ** (attempt - 1)) # 2s, 4s, 8s, 16s
                logger.info(f"      ⏳ Backing off for {sleep_duration}s before retry...")
                await asyncio.sleep(sleep_duration)
            else:
                raise RuntimeError(f"❌ Groq TTS failed after {max_retries} retry attempts.")

    async def _process_chunk_conversion(self, wav_path: str, mp3_path: str) -> bool:
        """
        6, 13 & 14. FFmpeg Validation, Normalization, Silence Trim.
        Applies volume normalization, silence removal, and converts WAV chunks to MP3 chunks.
        """
        # 14. Apply silence removal (start/end) and loudness normalization (13)
        cmd = [
            'ffmpeg', '-y', '-i', wav_path,
            '-af', 'silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:stop_periods=1:stop_duration=0.1:stop_threshold=-45dB,loudnorm=I=-16:TP=-1.5:Lra=11',
            '-ar', str(self.sample_rate), '-ac', str(self.channels),
            '-b:a', self.audio_bitrate, '-acodec', 'libmp3lame', mp3_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=45)
            
            # 6. Verify ffmpeg returncode
            if process.returncode != 0:
                logger.error(f"❌ FFmpeg conversion failure: {stderr.decode()[-200:]}")
                return False
                
            # 7. MP3 Existence/Corruption verification check
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 100:
                return True
                
        except Exception as e:
            logger.error(f"❌ Exception in FFmpeg execution: {e}")
            
        return False

    async def _merge_and_validate_chunks(self, chunk_mp3_paths: List[str], final_mp3_output: str) -> float:
        """Merges converted MP3 chunks and builds final file with FFmpeg structural verification."""
        if len(chunk_mp3_paths) == 1:
            os.replace(chunk_mp3_paths[0], final_mp3_output)
        else:
            # Create merge manifest list
            manifest_path = os.path.join(os.path.dirname(final_mp3_output), "concat_chunks.txt")
            with open(manifest_path, 'w') as f:
                for path in chunk_mp3_paths:
                    f.write(f"file '{os.path.abspath(path)}'\n")
                    
            cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', manifest_path, '-c', 'copy', final_mp3_output]
            try:
                process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await asyncio.wait_for(process.communicate(), timeout=30)
            except Exception as e:
                logger.error(f"❌ Chunk MP3 merge exception: {e}")
                return 0.0
            finally:
                if os.path.exists(manifest_path):
                    os.remove(manifest_path)
                    
        # 7. Validate final MP3 existence and structural length integrity
        duration = await self._get_audio_duration_async(final_mp3_output)
        if duration <= 0 or not os.path.exists(final_mp3_output) or os.path.getsize(final_mp3_output) < 200:
            raise RuntimeError("❌ Final MP3 file validation failed. Zero size or file corrupt.")
            
        return duration

    def _get_cache_hash(self, text: str) -> str:
        """15. Generates MD5 Hash key of script chunks for low-cost duplicate prevention caching."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    async def generate_with_effects(self, script_segments: List[Dict],
                                    output_dir: str, topic: str = "") -> Dict:
        """Orchestrates multi-chunk Groq generation using memory-scalable chunking."""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 2 & 18. Scalable Extract and Streamline Text Processing Memory
        text_parts = []
        for s in script_segments:
            if not s.get('is_pause') and s.get('text', '').strip():
                text_parts.append(s.get('text', '').strip())
                
        full_text = " ".join(text_parts)
        clean_text = self._sanitize_text(full_text)
        
        if len(clean_text.split()) <= 1:
            raise ValueError("❌ No valid, readable script text found to synthesize")
            
        logger.info(f"    🎙️ Requesting voice generation chunks (Voice: {self.voice})")
        
        # 2. Chunking Process Iteration
        chunks = self._break_into_chunks(clean_text)
        chunk_mp3_paths = []
        
        for idx, chunk in enumerate(chunks):
            # 15. Cache Checking implementation step
            chunk_hash = self._get_cache_hash(chunk)
            cached_mp3 = os.path.join(self.cache_dir, f"{chunk_hash}.mp3")
            
            if os.path.exists(cached_mp3) and os.path.getsize(cached_mp3) > 500:
                logger.info(f"⏭️ Cache hit found for text chunk {idx+1}/{len(chunks)}")
                chunk_mp3_paths.append(cached_mp3)
                continue
                
            temp_wav = os.path.join(output_dir, f"chunk_{idx}_raw.wav")
            temp_mp3 = os.path.join(output_dir, f"chunk_{idx}_temp.mp3")
            
            # API Generation with exponential backoff and timeout
            await self._call_groq_api_with_retry(chunk, temp_wav)
            
            # FFmpeg conversion and validation
            conversion_success = await self._process_chunk_conversion(temp_wav, temp_mp3)
            if not conversion_success:
                raise RuntimeError(f"❌ Failed processing audio file converter pipeline for chunk {idx}")
                
            # 10. Validated - Safe to cache and delete source WAV
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                    except Exception:
                    pass
                
            # Save to persistent cache system
            shutil_copy_path = os.path.join(output_dir, f"chunk_{idx}.mp3")
            os.replace(temp_mp3, shutil_copy_path)
            
            # Cache locally
            try:
                with open(shutil_copy_path, 'rb') as f_src, open(cached_mp3, 'wb') as f_dst:
                    f_dst.write(f_src.read())
            except Exception: 
                pass
                
            chunk_mp3_paths.append(shutil_copy_path)

        final_path_mp3 = os.path.join(output_dir, 'final_audio.mp3')
        total_duration = await self._merge_and_validate_chunks(chunk_mp3_paths, final_path_mp3)
        
        # 1, 8 & 9. Deterministic Word Timings Engine
        # Whisper/forced-alignment fallback, dividing duration evenly and removing random deviation
        word_timings = self._enforce_strict_word_timings(final_path_mp3, clean_text, total_duration)
        
        logger.info(f"    ✅ Audio Build Success: {total_duration:.1f}s | Words: {len(word_timings)}")
        
        return {
            'audio_path': final_path_mp3,
            'final_audio': final_path_mp3,
            'total_duration': total_duration,
            'word_timings': word_timings,
            'word_count': len(clean_text.split()),
            'voice_used': self.voice,
        }

    def _enforce_strict_word_timings(self, audio_path: str, text: str, total_duration: float) -> List[Dict]:
        """
        1, 9 & 8. Deterministic Word Timing Generator.
        Replaces fake random intervals with reproducible word blocks calculated strictly from duration.
        """
        words = text.split()
        if not words or total_duration <= 0:
            return []
            
        word_duration = total_duration / len(words)
        timings = []
        current = 0.0
        
        for i, word in enumerate(words):
            clean = word.strip('.,!?;:\'"()[]{}')
            
            # 9. Fixed deterministic calculation without random variables
            # Guarantees builds are identical and repeatable across runs
            duration = word_duration
            
            # CRITICAL: Lock first frame starting at exact 0.0s for hook retention
            if i == 0:
                current = 0.0
                
            timings.append({
                'word': clean,
                'start': round(current, 3),
                'end': round(current + duration, 3),
                'duration': round(duration, 3)
            })
            current += duration
            
        # Lock final word to absolute track end
        if timings:
            timings[-1]['end'] = round(total_duration, 3)
            timings[-1]['duration'] = round(timings[-1]['end'] - timings[-1]['start'], 3)
            
        return timings
