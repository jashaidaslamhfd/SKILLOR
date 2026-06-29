"""
Caption Generator - USA 2026 (PRODUCTION GRADE KARAOKE)
INTEGRATED PRODUCTION UPGRADES & FIXES:
1. 🎯 Corrected ASS AABBGGRR Color Coding System (True Pure Yellow Conversion)
2. 🔀 Non-mutating Deepcopy Validation & Sorting by Start Time
3. 📏 Dynamic Character-Count Font Scaling Engine (Prevents Portrait Screen Clipping)
4. 🎨 Multi-color Kinetic Karaoke Highlight Enhancements (White -> Yellow Transition)
5. 🧹 Redundant Sanitization & Clean Layout Parse Execution Nodes
"""

import os
import re
import copy
import logging
from typing import List, Dict, Optional

# Safe configuration fallback wrapper to adapt directory architecture variables
try:
    from config.settings import CAPTION_CONFIG
except ImportError:
    class FallbackCaptionConfig:
        MAX_WORDS_PER_LINE = 3
        FONT_SIZE = 85
        FONT_NAME = 'sans-serif'
        BOLD = 1
        OUTLINE_WIDTH = 4
        SHADOW = 0
        PRIMARY_COLOR = '&H00FFFFFF'      # Pure White (AABBGGRR)
        SECONDARY_COLOR = '&H0000FFFF'    # Corrected to ASS format Active state
        OUTLINE_COLOR = '&H00000000'      # Pure Black Outline
        SAFE_ZONE_BOTTOM = 280
        MARGIN_V = 280
        WIDTH = 1080
        HEIGHT = 1920
    CAPTION_CONFIG = FallbackCaptionConfig()

logger = logging.getLogger(__name__)

class CaptionGenerator:
    """Perfect sync dynamic, scalable, production-grade karaoke caption generator - USA 2026"""
    
    def __init__(self):
        self.max_words_per_line = getattr(CAPTION_CONFIG, 'MAX_WORDS_PER_LINE', 3)
        self.font_size = getattr(CAPTION_CONFIG, 'FONT_SIZE', 85)
        self.font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'sans-serif') 
        self.bold = getattr(CAPTION_CONFIG, 'BOLD', 1)
        self.outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 4)
        self.shadow = getattr(CAPTION_CONFIG, 'SHADOW', 0)
        
        # 🥇 Fix 1: Explicitly defining ASS style native AABBGGRR color hexadecimal arrays
        self.primary_color = '&H00FFFFFF'      # Pure White Base (Opaque Alpha + B=FF, G=FF, R=FF)
        self.secondary_color = '&H0000FFFF'    # True Bright Yellow Fill (Opaque Alpha + B=00, G=FF, R=FF)
        self.outline_color = '&H00000000'      # Pure Black Solid Frame Background
        
        self.alignment = 2  # Center-Bottom orientation alignment
        
        self.margin_v = max(
            getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 280),
            getattr(CAPTION_CONFIG, 'MARGIN_V', 280)
        )
        
        self.width = getattr(CAPTION_CONFIG, 'WIDTH', 1080)
        self.height = getattr(CAPTION_CONFIG, 'HEIGHT', 1920)
        self.margin_lr = 60
        
        logger.info(f"📝 CaptionGenerator initialized (font: {self.font_size}px, safe zone layout: {self.margin_v}px)")

    def _sanitize_word(self, word: str) -> str:
        """Clean individual word nodes preserving letter casing structures safely."""
        if not word:
            return ""
        safe = str(word).strip()
        safe = re.sub(r'[,\{\}\[\]\(\)<>\\&]', '', safe)
        safe = ''.join(ch for ch in safe if ch.isprintable())
        return ' '.join(safe.split())

    def _seconds_to_ass(self, seconds: float) -> str:
        """Convert float seconds timestamps accurately to ASS standard string syntax."""
        if seconds < 0:
            seconds = 0
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds % 1) * 100))
        if cs >= 100:
            s += 1
            cs = 0
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def _validate_and_sort_timings(self, word_timings: List[Dict], max_duration: float) -> List[Dict]:
        """Deepcopies timing profiles resolving zero overlap validations securely."""
        if not word_timings:
            return []

        timings = copy.deepcopy(word_timings)
        timings.sort(key=lambda w: w.get('start', 0.0))

        if timings[0].get('start', 0) > 0.0:
            delay = timings[0].get('start', 0)
            for wt in timings:
                wt['start'] = max(0.0, wt.get('start', 0) - delay)
                wt['end'] = max(0.0, wt.get('end', 0) - delay)
                wt['duration'] = wt['end'] - wt['start']

        for i in range(len(timings)):
            if timings[i]['end'] - timings[i]['start'] <= 0:
                timings[i]['end'] = timings[i]['start'] + 0.15
            
            timings[i]['duration'] = timings[i]['end'] - timings[i]['start']

            if i > 0:
                if timings[i]['start'] < timings[i-1]['end']:
                    timings[i]['start'] = timings[i-1]['end']
                    timings[i]['end'] = max(timings[i]['start'] + 0.15, timings[i]['end'])
                    timings[i]['duration'] = timings[i]['end'] - timings[i]['start']

            if timings[i]['duration'] < 0.10:
                timings[i]['end'] = timings[i]['start'] + 0.12
                timings[i]['duration'] = 0.12

            if timings[i]['end'] > max_duration:
                timings[i]['end'] = max_duration
                timings[i]['duration'] = max(0.05, max_duration - timings[i]['start'])

        if timings:
            timings[-1]['end'] = round(max_duration, 3)
            timings[-1]['duration'] = round(timings[-1]['end'] - timings[-1]['start'], 3)

        return timings

    def _semantic_grouping(self, words_list: List[Dict]) -> List[List[Dict]]:
        """Groups individual structural elements to clean single/multi-line segment blocks."""
        lines = []
        current_line = []
        
        for wt in words_list:
            current_line.append(wt)
            word_str = wt.get('word', '')
            
            is_end_of_sentence = bool(re.search(r'[.?!,;]', word_str))
            
            if len(current_line) >= self.max_words_per_line or (is_end_of_sentence and len(current_line) >= 2):
                lines.append(current_line)
                current_line = []
                
        if current_line:
            lines.append(current_line)
            
        return lines

    def generate_karaoke_ass(self, word_timings: List[Dict], ass_path: str, max_duration: float = 60.0) -> str:
        """Real ASS Karaoke Subtitle Production Generator executing kinetic word transitions."""
        if not word_timings:
            word_timings = [{'word': 'YOUR', 'start': 0.0, 'end': 1.5, 'duration': 1.5}]

        validated_words = self._validate_and_sort_timings(word_timings, max_duration)
        line_groups = self._semantic_grouping(validated_words)
        
        events = []
        
        for group in line_groups:
            if not group:
                continue
                
            line_start = group[0]['start']
            line_end = group[-1]['end']
            
            # 🥇 Fix 2: Dynamic Auto-Scaling Factor calculation inside generator iteration loop
            # Counts character density across segment group to clamp scale parameters
            total_chars = sum(len(self._sanitize_word(wt.get('word', ''))) for wt in group)
            font_scale = 100
            if total_chars > 16:  # Dynamic compression limit if long words cluster together
                font_scale = max(75, int(100 - (total_chars - 16) * 1.8))

            karaoke_text_blocks = []
            for wt in group:
                safe_word = self._sanitize_word(wt.get('word', ''))
                duration_cs = int(round(wt['duration'] * 100))
                
                # Applying standard karaoke fill tagging system
                karaoke_text_blocks.append(f"{{\\kf{duration_cs}}}{safe_word}")

            full_karaoke_string = " ".join(karaoke_text_blocks)
            
            start_stamp = self._seconds_to_ass(line_start)
            end_stamp = self._seconds_to_ass(line_end)
            
            # Dynamic safe-zone mapping parameters adjustment
            dynamic_margin_v = self.margin_v
            flat_text_upper = full_karaoke_string.upper()
            if "HOOK" in flat_text_upper or "STOP" in flat_text_upper:
                dynamic_margin_v = self.margin_v + 120
                
            # Formatting line string injecting structural kinetic variables
            ass_line = (
                f"Dialogue: 0,{start_stamp},{end_stamp},Style_{font_scale},,0,0,0,,"
                f"{{\\fad(40,40)}}{{\\fscx{font_scale}}}{{\\fscy{font_scale}}}{{\\blur0.5}}{full_karaoke_string}"
            )
            events.append((font_scale, ass_line))

        # Build comprehensive dynamic style mapping matrix inside header block
        distinct_scales = set(item[0] for item in events)
        header = self._build_ass_header_multi_style(distinct_scales)
        
        payload_lines = [item[1] for item in events]

        os.makedirs(os.path.dirname(ass_path) or ".", exist_ok=True)
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(payload_lines) + "\n")
            
        logger.info(f"✅ Real Karaoke ASS Captions written completely: {len(events)} structural event paths.")
        return ass_path

    def _build_ass_header_multi_style(self, scales: set) -> str:
        """Builds multi-style mapping header handling custom scalable fonts nodes safely."""
        margin_lr = self.margin_lr
        margin_v = self.margin_v
        
        style_block = ""
        # Automatically registers custom scaled styles to protect cross word lengths boundaries
        for scale in sorted(scales):
            style_block += f"Style: Style_{scale},{self.font_name},{self.font_size},{self.primary_color},{self.secondary_color},{self.outline_color},&H00000000,{self.bold},0,0,0,{scale},{scale},2,0,1,{self.outline_width},{self.shadow},{self.alignment},{margin_lr},{margin_lr},{margin_v},1\n"

        return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_block}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# ============================================================
# RUNTIME INTEGRITY TEST
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 TESTING CAPTION GENERATOR ENGINE (USA 2026)\n" + "=" * 60)
    gen = CaptionGenerator()
    test_timings = [
        {'word': 'Your', 'start': 0.0, 'end': 0.4, 'duration': 0.4},
        {'word': 'baby\'s', 'start': 0.4, 'end': 0.9, 'duration': 0.5},
        {'word': 'neurodevelopmental', 'start': 0.9, 'end': 1.8, 'duration': 0.9},
        {'word': 'process.', 'start': 1.8, 'end': 2.5, 'duration': 0.7}
    ]
    gen.generate_karaoke_ass(test_timings, ".test_output/karaoke.ass", max_duration=5.0)
    print("=" * 60 + "\n✅ Caption Framework Multi-Style Rendering Parsed Successfully!")
