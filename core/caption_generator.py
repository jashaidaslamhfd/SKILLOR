"""
Caption Generator - Production Ready (FIXED)
OPTIMIZED FOR: 35-54 Male USA/UK Audience

FIXES:
1. No overlapping events (clean word-by-word)
2. 60px margins (no text cutoff)
3. Full special character sanitization
4. Bottom-center alignment (2) forced
5. Auto-fallback timings
6. Multiple font fallbacks
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from config.settings import CAPTION_CONFIG


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load system bold fonts with multiple fallbacks"""
    import platform
    
    candidates = []
    
    # Windows
    if platform.system() == 'Windows':
        candidates = [
            "C:/Windows/Fonts/ArialBD.ttf",
            "C:/Windows/Fonts/Arial.ttf",
            "C:/Windows/Fonts/Impact.ttf",
        ]
    # macOS
    elif platform.system() == 'Darwin':
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    # Linux
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/arial/arialbd.ttf",
        ]
    
    # Try each candidate
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    
    # Last resort - default font
    try:
        return ImageFont.load_default()
    except:
        # Absolute fallback
        return ImageFont.load_default()


class CaptionGenerator:
    """Production Caption Generator - Fixed"""
    
    def __init__(self):
        # Load from config
        self.max_words_per_line = getattr(CAPTION_CONFIG, 'MAX_WORDS_PER_LINE', 3)
        self.alternate_colors = getattr(CAPTION_CONFIG, 'ALTERNATE_COLORS', True)
        self.font_size = getattr(CAPTION_CONFIG, 'FONT_SIZE', 88)
        self.font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'Arial')
        self.bold = getattr(CAPTION_CONFIG, 'BOLD', True)
        self.outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 7)
        self.shadow = getattr(CAPTION_CONFIG, 'SHADOW', 3)
        
        # Colors
        self.primary_color = getattr(CAPTION_CONFIG, 'PRIMARY_COLOR', '&H00FFFFFF')
        self.secondary_color = getattr(CAPTION_CONFIG, 'SECONDARY_COLOR', '&H0000FFFF')
        self.outline_color = getattr(CAPTION_CONFIG, 'OUTLINE_COLOR', '&H00000000')
        
        # FIX: Force bottom-center alignment (2)
        self.alignment = 2
        self.margin_v = max(getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 350), 
                           getattr(CAPTION_CONFIG, 'MARGIN_V', 280))
        
        # Frame size
        self.width = 1080
        self.height = 1920
        
        # FIX: Wider margins to prevent cutoff
        self.margin_lr = 80
        
        print(f"📝 CaptionGenerator initialized (font: {self.font_size}px, align: {self.alignment})")

    # ============================================================
    # GENERATE KARAOKE ASS SUBTITLES (FIXED)
    # ============================================================
    
    def generate_karaoke_ass(
        self, 
        word_timings: List[Dict], 
        ass_path: str, 
        max_duration: Optional[float] = None
    ) -> str:
        """
        Generate ASS subtitle file with karaoke word-by-word highlighting
        
        FIXES:
        1. NO overlapping events (one event per word)
        2. 80px margins (no text cutoff)
        3. Bottom-center alignment (2)
        4. Full sanitization
        5. Fallback timings if missing
        """
        
        # ============================================================
        # Step 1: Validate and clean timings
        # ============================================================
        if not word_timings:
            print("    ⚠️ No word timings, generating fallback")
            word_timings = self._generate_fallback_timings(max_duration or 48.0)
        
        # Sort by start time
        sorted_timings = sorted(word_timings, key=lambda w: w.get('start', 0))
        
        # Clean timings (remove overlaps)
        clean_timings = []
        for idx, wt in enumerate(sorted_timings):
            start = wt.get('start', 0)
            end = wt.get('end', start + 0.3)
            
            # Cap at max duration
            if max_duration is not None:
                if start >= max_duration:
                    continue
                end = min(end, max_duration)
            
            # Prevent overlap with next word
            if idx + 1 < len(sorted_timings):
                next_start = sorted_timings[idx + 1].get('start', end)
                if end > next_start:
                    end = max(start + 0.05, next_start - 0.01)
            
            if end <= start:
                continue
            
            clean_timings.append({**wt, 'start': start, 'end': end})
        
        if not clean_timings:
            print("    ⚠️ No valid timings, using fallback")
            clean_timings = self._generate_fallback_timings(max_duration or 48.0)
        
        # ============================================================
        # Step 2: Build ASS header
        # ============================================================
        header = self._build_ass_header()
        
        # ============================================================
        # Step 3: Generate dialogue events (ONE per word)
        # ============================================================
        events = []
        line_idx = 0
        current_line = []
        
        for idx, wt in enumerate(clean_timings):
            word = self._sanitize_word(wt.get('word', ''))
            if not word:
                continue
            
            current_line.append(wt)
            
            # Create new line when max words reached
            if len(current_line) >= self.max_words_per_line or idx == len(clean_timings) - 1:
                style = "Red" if line_idx % 2 == 0 else "White"
                
                # ONE event per word - NO overlapping
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
        
        # Ensure at least one event
        if not events:
            fallback_text = "YOUR BRAIN IS AMAZING"
            events.append(
                f"Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,,{fallback_text}"
            )
        
        # ============================================================
        # Step 4: Write to file
        # ============================================================
        os.makedirs(os.path.dirname(ass_path) or ".", exist_ok=True)
        
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(events) + "\n")
        
        print(f"    ✅ Captions: {len(events)} events | {line_idx} groups")
        return ass_path

    # ============================================================
    # BUILD ASS HEADER (FIXED)
    # ============================================================
    
    def _build_ass_header(self) -> str:
        """Build ASS header with correct formatting"""
        
        # FIX: Force bottom-center alignment (2)
        # FIX: Wider margins (80px) to prevent text cutoff
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

    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _sanitize_word(self, word: str) -> str:
        """
        FULL SANITIZATION for ASS subtitle format
        
        Removes:
        - Commas (break ASS field parsing)
        - Braces (ASS override tags)
        - Backslashes (escape issues)
        - Non-printable characters
        - Special symbols that break rendering
        """
        if not word:
            return ""
        
        # Convert to string and uppercase
        safe = str(word).strip().upper()
        
        # Remove ASS-breaking characters
        safe = safe.replace(',', '')
        safe = safe.replace('{', '').replace('}', '')
        safe = safe.replace('\\', '')
        safe = safe.replace('[', '').replace(']', '')
        safe = safe.replace('(', '').replace(')', '')
        safe = safe.replace('<', '').replace('>', '')
        safe = safe.replace('&', '')
        
        # Remove non-printable characters
        safe = ''.join(ch for ch in safe if ch.isprintable())
        
        # Remove extra spaces
        safe = ' '.join(safe.split())
        
        # Remove empty strings
        if not safe or len(safe) < 1:
            return ""
        
        return safe

    def _seconds_to_ass(self, seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.cc)"""
        if seconds < 0:
            seconds = 0
        
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def _generate_fallback_timings(self, duration: float) -> List[Dict]:
        """Generate fallback word timings if TTS boundaries are missing"""
        fallback_text = "YOUR BRAIN IS AMAZING AND POWERFUL AND BEAUTIFUL"
        words = fallback_text.split()
        
        if not words:
            words = ["YOUR", "BRAIN", "IS", "AMAZING"]
        
        # Ensure at least 3 words
        while len(words) < 3:
            words.append("BRAIN")
        
        timings = []
        word_duration = duration / len(words)
        current = 0.0
        
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
        """Generate caption metadata for video assembler"""
        if not word_timings:
            return []
        
        captions = []
        current_line = []
        current_start = 0
        line_idx = 0
        
        for i, timing in enumerate(word_timings):
            if not current_line:
                current_start = timing['start']
            
            current_line.append(timing)
            
            if len(current_line) >= self.max_words_per_line or i == len(word_timings) - 1:
                text = ' '.join([w['word'] for w in current_line])
                end = current_line[-1]['end']
                
                if self.alternate_colors:
                    color = "red" if line_idx % 2 == 0 else "white"
                else:
                    color = "white"
                
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
                    'text': text.upper(),
                    'start': current_start,
                    'end': end,
                    'duration': end - current_start,
                    'words': current_line,
                    'karaoke_words': karaoke_words,
                    'color': color,
                    'outline': "black",
                    'bold': True,
                    'line_index': line_idx,
                    'position_y': self.margin_v,
                    'position_x': self.width // 2,
                })
                
                current_line = []
                line_idx += 1
        
        print(f"    [CAPTIONS] {len(captions)} lines | {sum(len(c['words']) for c in captions)} words")
        return captions

    def get_safe_zone(self) -> Dict:
        """Return YouTube Shorts safe zone for caption positioning"""
        return {
            'width': self.width,
            'height': self.height,
            'safe_top': 0,
            'safe_bottom': self.margin_v,
            'caption_y_min': 1100,
            'caption_y_max': 1700,
            'caption_y_center': 1400,
        }

    def generate_ass_styles(self) -> Dict:
        """Return style metadata for ASS file generation"""
        margin_v = self.margin_v
        margin_lr = self.margin_lr
        
        return {
            'white': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': self.primary_color,
                'secondary_color': '&H000000FF',
                'outline_color': self.outline_color,
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': self.alignment,
                'margin_l': margin_lr,
                'margin_r': margin_lr,
                'margin_v': margin_v,
            },
            'red': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': self.secondary_color,
                'secondary_color': '&H00FFFFFF',
                'outline_color': self.outline_color,
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': self.alignment,
                'margin_l': margin_lr,
                'margin_r': margin_lr,
                'margin_v': margin_v,
            }
        }


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING CAPTION GENERATOR (FIXED)\n" + "="*60)
    
    # Sample word timings
    test_timings = [
        {'word': 'Your', 'start': 0.0, 'end': 0.5},
        {'word': 'brain', 'start': 0.5, 'end': 1.0},
        {'word': 'is', 'start': 1.0, 'end': 1.3},
        {'word': 'amazing', 'start': 1.3, 'end': 2.0},
        {'word': 'and', 'start': 2.0, 'end': 2.3},
        {'word': 'powerful', 'start': 2.3, 'end': 3.2},
    ]
    
    generator = CaptionGenerator()
    
    # Generate ASS file
    test_output = "test_captions.ass"
    generator.generate_karaoke_ass(test_timings, test_output, max_duration=5.0)
    
    print(f"\n✅ Captions saved: {test_output}")
    
    # Show safe zone
    safe_zone = generator.get_safe_zone()
    print(f"\n📊 Safe Zone:")
    print(f"   Bottom: {safe_zone['safe_bottom']}px")
    print(f"   Caption Y: {safe_zone['caption_y_center']}px")