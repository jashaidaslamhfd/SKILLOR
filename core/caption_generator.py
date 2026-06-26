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
7. ✅ IMPROVED: Syllable weight increased for better audio sync
8. ✅ IMPROVED: Fallback timings now stretch to full duration
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
        FIXED v4: Detect and fix caption sync issues:
        1. All captions crammed in first few seconds
        2. All captions crammed in last few seconds  
        3. Total caption span less than 35% of video duration
        4. ✅ NEW: Start/end boundary mismatch (captions fast in middle)
        5. IMPROVED: Better syllable weighting for audio sync
        """
        if not word_timings or max_duration <= 0:
            return word_timings

        last_end = word_timings[-1].get('end', 0.0)
        first_start = word_timings[0].get('start', 0.0)
        span = last_end - first_start

        # ✅ FIX: Check if captions end too early (gap > 15% at end)
        end_gap = max_duration - last_end
        # ✅ FIX: Check if average word duration is too fast (< 0.2s per word)
        avg_word_dur = span / max(1, len(word_timings))

        # If caption span covers less than 35% of video — timings are broken
        needs_fix = (
            (last_end < 5.0 and max_duration > 10.0) or   # All in first 5s
            (span < max_duration * 0.35) or                 # Span too short
            (end_gap > max_duration * 0.15 and last_end < max_duration * 0.85) or  # ✅ End too early
            (avg_word_dur < 0.20 and max_duration > 15.0)  # ✅ Words too fast
        )

        if needs_fix:
            logger.warning(f"⚠️ Caption timing fix: span={span:.1f}s on {max_duration:.1f}s video")
            total_words = len(word_timings)

            def syllable_count(word: str) -> int:
                w = str(word).lower().strip('.,!?;:\"\' ')
                count = len(re.findall(r'[aeiou]+', w)) if w else 0
                return max(1, count)

            # IMPROVED: Higher weight for longer words
            weights = []
            for w in word_timings:
                word = w.get('word', '')
                syl = syllable_count(word)
                # FIX: Increased weight for better sync
                weight = syl * 1.5 + (0.3 if len(word) > 7 else 0.1 if len(word) > 5 else 0)
                weights.append(max(0.6, weight))
            
            total_weight = sum(weights)
            scale = max_duration / total_weight
            
            cur = 0.0
            for i, w in enumerate(word_timings):
                d = max(0.15, weights[i] * scale)
                # Cap individual word duration to prevent unnatural long pauses
                d = min(d, 1.5)
                w['start'] = round(cur, 3)
                w['end'] = round(min(cur + d, max_duration), 3)
                w['duration'] = round(w['end'] - w['start'], 3)
                cur += d
                
            if word_timings:
                word_timings[-1]['end'] = round(max_duration, 3)
                word_timings[-1]['duration'] = round(word_timings[-1]['end'] - word_timings[-1]['start'], 3)

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
        """Generate fallback timings stretched to full duration"""
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
        # Ensure last word ends exactly at duration
        if timings:
            timings[-1]['end'] = round(duration, 3)
            timings[-1]['duration'] = round(duration - timings[-1]['start'], 3)
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


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING CAPTION GENERATOR\n" + "="*60)
    
    generator = CaptionGenerator()
    
    # Test with crammed timings (simulating bug)
    test_timings = [
        {'word': 'Your', 'start': 0.0, 'end': 0.3},
        {'word': 'brain', 'start': 0.3, 'end': 0.6},
        {'word': 'is', 'start': 0.6, 'end': 0.8},
        {'word': 'amazing', 'start': 0.8, 'end': 1.1},
        {'word': 'and', 'start': 1.1, 'end': 1.3},
        {'word': 'powerful', 'start': 1.3, 'end': 1.6},
    ]
    
    # Generate ASS file with stretching
    test_output = "test_captions.ass"
    generator.generate_karaoke_ass(test_timings, test_output, max_duration=48.0)
    
    print(f"\n✅ Captions saved: {test_output}")
    print("   Timings stretched to 48s")
