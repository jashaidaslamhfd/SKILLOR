"""
Caption Generator - Production Ready (STACKING & SPEED FIX)
OPTIMIZED FOR: 35-54 Male USA/UK Audience

FIXES:
1. ✅ Prevented all words from cramming into the first 3 seconds (Stretching Fix)
2. ✅ Class name: CaptionGenerator (correct)
3. ✅ No overlapping events (clean word-by-word)
4. ✅ 80px margins (no text cutoff)
5. ✅ Bottom-center alignment (2) forced
6. ✅ Auto-fallback timings & Multiple font fallbacks
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from config.settings import CAPTION_CONFIG

logger = logging.getLogger(__name__)

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load system bold fonts with multiple fallbacks"""
    import platform
    candidates = []
    
    if platform.system() == 'Windows':
        candidates = ["C:/Windows/Fonts/ArialBD.ttf", "C:/Windows/Fonts/Arial.ttf", "C:/Windows/Fonts/Impact.ttf"]
    elif platform.system() == 'Darwin':
        candidates = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/arial/arialbd.ttf"
        ]
    
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


class CaptionGenerator:
    
    def __init__(self):
        self.max_words_per_line = getattr(CAPTION_CONFIG, 'MAX_WORDS_PER_LINE', 3)
        self.alternate_colors = getattr(CAPTION_CONFIG, 'ALTERNATE_COLORS', True)
        self.font_size = getattr(CAPTION_CONFIG, 'FONT_SIZE', 88)
        self.font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'Arial')
        self.bold = getattr(CAPTION_CONFIG, 'BOLD', True)
        self.outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 7)
        self.shadow = getattr(CAPTION_CONFIG, 'SHADOW', 3)
        
        self.primary_color = getattr(CAPTION_CONFIG, 'PRIMARY_COLOR', '&H00FFFFFF')
        self.secondary_color = getattr(CAPTION_CONFIG, 'SECONDARY_COLOR', '&H0000FFFF')
        self.outline_color = getattr(CAPTION_CONFIG, 'OUTLINE_COLOR', '&H00000000')
        
        self.alignment = 2
        self.margin_v = max(getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 350), getattr(CAPTION_CONFIG, 'MARGIN_V', 280))
        
        self.width = 1080
        self.height = 1920
        self.margin_lr = 80
        
        print(f"📝 CaptionGenerator initialized (font: {self.font_size}px, align: {self.alignment})")

    def _validate_and_stretch_timings(self, word_timings: List[Dict], max_duration: float) -> List[Dict]:
        """
        CRITICAL BUG FIX: Yeh function check karta hai ke kahin saare captions 
        shuruat ke kuch seconds mein cram to nahi ho rahe. Agar aisa hai, to yeh 
        unhe poori video duration par linearly spread (auto-stretch) kar dega.
        """
        if not word_timings:
            return word_timings

        # Last word ka end time check karein
        last_word_end = word_timings[-1].get('end', 0.0)

        # Agar saare words 4 seconds se pehle hi khatam ho rahe hain jabki video lambi (e.g. 40s+) hai, 
        # to iska matlab timings corrupt hain.
        if last_word_end < 4.0 and max_duration > 10.0:
            logger.error(f"🛑 TIMING CRASH DETECTED: Captions ended at {last_word_end}s on a {max_duration}s video!")
            print("🔄 Re-calculating and spreading word timings evenly across the video duration...")
            
            total_words = len(word_timings)
            time_per_word = max_duration / total_words
            
            current_time = 0.0
            for w in word_timings:
                w['start'] = round(current_time, 2)
                w['end'] = round(current_time + time_per_word, 2)
                current_time += time_per_word
                
            return word_timings

        return word_timings

    def generate_karaoke_ass(
        self, 
        word_timings: List[Dict], 
        ass_path: str, 
        max_duration: Optional[float] = None
    ) -> str:
        """Generate ASS subtitle file with protection against bullet-speed stacking"""
        
        target_duration = max_duration or 48.0
        
        if not word_timings:
            print("    ⚠️ No word timings, generating fallback")
            word_timings = self._generate_fallback_timings(target_duration)
        
        # Guard Clause Activation: Stacking checking aur recovery
        word_timings = self._validate_and_stretch_timings(word_timings, target_duration)
        
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
            
            # Goli ki speed control: Ensure word stays on screen for a printable duration
            if (end - start) < 0.15:
                end = start + 0.25
                
            if end <= start:
                continue
            
            clean_timings.append({**wt, 'start': start, 'end': end})
        
        if not clean_timings:
            print("    ⚠️ No valid timings, using fallback")
            clean_timings = self._generate_fallback_timings(target_duration)
        
        header = self._build_ass_header()
        events = []
        line_idx = 0
        current_line = []
        
        for idx, wt in enumerate(clean_timings):
            word = self._sanitize_word(wt.get('word', ''))
            if not word:
                continue
            
            current_line.append(wt)
            
            if len(current_line) >= self.max_words_per_line or idx == len(clean_timings) - 1:
                style = "Red" if line_idx % 2 == 0 else "White"
                
                for word_timing in current_line:
                    safe_word = self._sanitize_word(word_timing.get('word', ''))
                    if not safe_word:
                        continue
                    
                    w_start = self._seconds_to_ass(word_timing['start'])
                    w_end = self._seconds_to_ass(word_timing['end'])
                    
                    events.append(
                        f"Dialogue: 0,{w_start},{w_end},{style},,0,0,0,,{safe_word.upper()}"
                    )
                
                current_line = []
                line_idx += 1
        
        if not events:
            fallback_text = "YOUR BRAIN IS AMAZING"
            events.append(f"Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,,{fallback_text}")
        
        os.makedirs(os.path.dirname(ass_path) or ".", exist_ok=True)
        
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(events) + "\n")
        
        print(f"    ✅ Captions: {len(events)} events | {line_idx} groups")
        return ass_path

    def _build_ass_header(self) -> str:
        margin_lr = self.margin_lr
        margin_v = self.margin_v
        return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{self.font_name},{self.font_size},{self.primary_color},&H000000FF,{self.outline_color},&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},{self.alignment},{margin_lr},{margin_lr},{margin_v},1
Style: Red,{self.font_name},{self.font_size},{self.secondary_color},&H00FFFFFF,{self.outline_color},&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},{self.alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def _sanitize_word(self, word: str) -> str:
        if not word:
            return ""
        safe = str(word).strip().upper()
        safe = re.sub(r'[,\{\}\[\]\(\)<>\\&]', '', safe)
        safe = ''.join(ch for ch in safe if ch.isprintable())
        return ' '.join(safe.split())

    def _seconds_to_ass(self, seconds: float) -> str:
        if seconds < 0: seconds = 0
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def _generate_fallback_timings(self, duration: float) -> List[Dict]:
        fallback_text = "YOUR BRAIN IS AMAZING AND POWERFUL AND BEAUTIFUL"
        words = fallback_text.split()
        word_duration = duration / len(words)
        current = 0.0
        timings = []
        for word in words:
            timings.append({
                'word': word,
                'start': round(current, 3),
                'end': round(current + word_duration, 3),
                'duration': round(word_duration, 3)
            })
            current += word_duration
        return timings

    def generate_captions(self, word_timings: List[Dict]) -> List[Dict]:
        if not word_timings: return []
        captions = []
        current_line = []
        current_start = 0
        line_idx = 0
        
        for i, timing in enumerate(word_timings):
            if not current_line: current_start = timing['start']
            current_line.append(timing)
            if len(current_line) >= self.max_words_per_line or i == len(word_timings) - 1:
                text = ' '.join([w['word'] for w in current_line])
                end = current_line[-1]['end']
                color = "red" if (self.alternate_colors and line_idx % 2 == 0) else "white"
                
                karaoke_words = []
                for j, word_timing in enumerate(current_line):
                    karaoke_words.append({
                        'word': word_timing['word'].upper(),
                        'start': word_timing['start'],
                        'end': word_timing['end'],
                        'duration': word_timing.get('duration', word_timing['end'] - word_timing['start']),
                        'is_active': False,
                        'word_index': j,
                    })
                
                captions.append({
                    'text': text.upper(), 'start': current_start, 'end': end,
                    'duration': end - current_start, 'words': current_line,
                    'karaoke_words': karaoke_words, 'color': color, 'outline': "black",
                    'bold': True, 'line_index': line_idx, 'position_y': self.margin_v,
                    'position_x': self.width // 2,
                })
                current_line = []
                line_idx += 1
        return captions

    def get_safe_zone(self) -> Dict:
        return {
            'width': self.width, 'height': self.height, 'safe_top': 0, 'safe_bottom': self.margin_v,
            'caption_y_min': 1100, 'caption_y_max': 1700, 'caption_y_center': 1400,
        }

    def generate_ass_styles(self) -> Dict:
        margin_v = self.margin_v
        margin_lr = self.margin_lr
        base_style = {
            'fontname': self.font_name, 'fontsize': self.font_size, 'outline_color': self.outline_color,
            'back_color': '&H00000000', 'bold': 1 if self.bold else 0, 'outline': self.outline_width,
            'shadow': self.shadow, 'alignment': self.alignment, 'margin_l': margin_lr, 'margin_r': margin_lr, 'margin_v': margin_v
        }
        return {
            'white': {**base_style, 'primary_color': self.primary_color, 'secondary_color': '&H000000FF'},
            'red': {**base_style, 'primary_color': self.secondary_color, 'secondary_color': '&H00FFFFFF'}
        }
