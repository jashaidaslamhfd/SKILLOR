"""Auto-sync Caption Generator — Karaoke Word-by-Word + Pop Effects + Safe Zone"""

from typing import List, Dict
from config.settings import CAPTION_CONFIG


class CaptionGenerator:
    def __init__(self):
        self.max_words_per_line = getattr(CAPTION_CONFIG, 'MAX_WORDS_PER_LINE', 3)  # FIX: 3 words optimal
        self.alternate_colors = getattr(CAPTION_CONFIG, 'ALTERNATE_COLORS', True)
        self.font_size = getattr(CAPTION_CONFIG, 'FONT_SIZE', 90)
        self.font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'Arial')
        self.bold = getattr(CAPTION_CONFIG, 'BOLD', True)
        self.outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 4)
        self.shadow = getattr(CAPTION_CONFIG, 'SHADOW', 2)
        self.alignment = getattr(CAPTION_CONFIG, 'ALIGNMENT', 10)  # 10 = center

    def generate_captions(self, word_timings: List[Dict]) -> List[Dict]:
        """
        FIX: Generate karaoke-style captions with word-by-word highlighting
        Each word has individual timing for pop-in + scale animation
        """
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

            # FIX: 3 words per line — optimal for readability + speed
            if len(current_line) >= self.max_words_per_line or i == len(word_timings) - 1:
                text = ' '.join([w['word'] for w in current_line])
                end = current_line[-1]['end']

                # FIX: Detect numbers/emojis for visual boost
                has_numbers = any(char.isdigit() for char in text)
                has_shock_words = any(w in text.lower() for w in ['shock', 'terrify', 'scary', 'dark', 'secret', 'truth', 'never', 'always', 'everyone', 'nobody'])

                # Alternate colors: even lines = RED, odd lines = WHITE
                if self.alternate_colors:
                    color = "red" if line_idx % 2 == 0 else "white"
                else:
                    color = "white"

                # FIX: Build per-word karaoke data
                karaoke_words = []
                for j, word_timing in enumerate(current_line):
                    karaoke_words.append({
                        'word': word_timing['word'].upper(),
                        'start': word_timing['start'],
                        'end': word_timing['end'],
                        'duration': word_timing.get('duration', word_timing['end'] - word_timing['start']),
                        'is_active': False,  # Set by renderer based on current time
                        'word_index': j,
                    })

                captions.append({
                    'text': text.upper(),
                    'start': current_start,
                    'end': end,
                    'duration': end - current_start,
                    'words': current_line,
                    'karaoke_words': karaoke_words,  # NEW: Individual word data
                    'color': color,
                    'outline': "black",
                    'bold': True,
                    'line_index': line_idx,
                    'has_numbers': has_numbers,  # NEW: For number boost effect
                    'has_shock_words': has_shock_words,  # NEW: For emphasis
                    # FIX: Position in safe zone (lower 40% of 1920 = 1150-1850)
                    'position_y': 1400,  # Safe from YouTube UI overlay
                    'position_x': 540,   # Center of 1080
                })

                current_line = []
                line_idx += 1

        print(f"    📝 Captions: {len(captions)} lines | {sum(len(c['words']) for c in captions)} words")
        return captions

    def generate_karaoke_ass(self, word_timings: List[Dict], ass_path: str) -> str:
        """
        NEW: Generate ASS subtitle file with karaoke word-by-word highlighting
        Each word scales up when active, creating Netflix-style effect
        """
        width = 1080
        height = 1920
        font_size = self.font_size
        margin_v = 1400  # Safe zone: lower 40%

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{self.font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},10,10,10,{margin_v},1
Style: Red,{self.font_name},{font_size},&H000000FF,&H00FFFFFF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},10,10,10,{margin_v},1
Style: ActiveWhite,{self.font_name},{int(font_size*1.15)},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,110,110,2,0,1,{self.outline_width+1},{self.shadow},10,10,10,{margin_v},1
Style: ActiveRed,{self.font_name},{int(font_size*1.15)},&H000000FF,&H00FFFFFF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,110,110,2,0,1,{self.outline_width+1},{self.shadow},10,10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        lines = []
        line_idx = 0
        current_line = []
        current_start = 0

        for i, timing in enumerate(word_timings):
            if not current_line:
                current_start = timing['start']

            current_line.append(timing)

            if len(current_line) >= self.max_words_per_line or i == len(word_timings) - 1:
                base_style = "Red" if line_idx % 2 == 0 else "White"
                active_style = "ActiveRed" if line_idx % 2 == 0 else "ActiveWhite"

                # Build karaoke line: each word has its own timing
                # Inactive words: normal size, Inactive color
                # Active word: 115% size, Active color
                karaoke_text = ""
                for j, wt in enumerate(current_line):
                    word = str(wt.get('word', '')).strip().upper()
                    if not word:
                        continue

                    word_start = self._seconds_to_ass(wt['start'])
                    word_end = self._seconds_to_ass(wt['end'])

                    # FIX: Karaoke tag — word appears with scale animation
                    # \t() = transform, \fs() = font size
                    if j == 0:
                        # First word: start with full size
                        karaoke_text += f"{{\\{active_style}\\fs{font_size*1.15}}}{word}{{\\r}}{word_end}"
                    else:
                        # Subsequent words: pop in with scale
                        karaoke_text += f" {{\\t({word_start},{word_end},\\fs{font_size*1.15}\\fscx110\\fscy110)}}{word}"

                # Full line timing
                line_start = self._seconds_to_ass(current_start)
                line_end = self._seconds_to_ass(current_line[-1]['end'])

                lines.append(f"Dialogue: 0,{line_start},{line_end},{base_style},,0,0,0,,{karaoke_text}")

                # Also add individual word highlights for precise karaoke
                for j, wt in enumerate(current_line):
                    word = str(wt.get('word', '')).strip().upper()
                    if not word:
                        continue

                    word_start = self._seconds_to_ass(wt['start'])
                    word_end = self._seconds_to_ass(wt['end'])

                    # Active word: bigger, brighter
                    lines.append(
                        f"Dialogue: 1,{word_start},{word_end},{active_style},,0,0,0,,"
                        f"{{\\fs{font_size*1.15}\\fscx115\\fscy115}}{word}"
                    )

                current_line = []
                line_idx += 1

        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,, ")

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")

        print(f"    📝 Karaoke ASS: {len(lines)} events | {line_idx} lines")
        return ass_path

    def _seconds_to_ass(self, s: float) -> str:
        """Convert seconds to ASS time format"""
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sc = int(s % 60)
        cs = int((s % 1) * 100)
        return f"{h}:{m:02d}:{sc:02d}.{cs:02d}"

    def generate_ass_styles(self) -> Dict:
        """Generate ASS subtitle styles for Red/White alternating + Active states"""
        margin_v = 1400  # FIX: Safe zone, lower 40%

        return {
            'red': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': '&H000000FF',  # Red (BGR)
                'secondary_color': '&H000000FF',
                'outline_color': '&H00000000',  # Black outline
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': 10,  # Center
                'margin_v': margin_v,
            },
            'white': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': '&H00FFFFFF',  # White
                'secondary_color': '&H00FFFFFF',
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': 10,
                'margin_v': margin_v,
            },
            'active_red': {  # NEW: Bigger, brighter for active word
                'fontname': self.font_name,
                'fontsize': int(self.font_size * 1.15),
                'primary_color': '&H000000FF',
                'secondary_color': '&H00FFFFFF',
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': 1,
                'outline': self.outline_width + 1,
                'shadow': self.shadow,
                'alignment': 10,
                'margin_v': margin_v,
                'scale_x': 115,
                'scale_y': 115,
            },
            'active_white': {  # NEW
                'fontname': self.font_name,
                'fontsize': int(self.font_size * 1.15),
                'primary_color': '&H00FFFFFF',
                'secondary_color': '&H000000FF',
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': 1,
                'outline': self.outline_width + 1,
                'shadow': self.shadow,
                'alignment': 10,
                'margin_v': margin_v,
                'scale_x': 115,
                'scale_y': 115,
            }
        }

    def get_safe_zone(self) -> Dict:
        """NEW: Return YouTube Shorts safe zone for caption positioning"""
        return {
            'width': 1080,
            'height': 1920,
            'safe_top': 0,      # Title area
            'safe_bottom': 350,  # Subscribe button area
            'caption_y_min': 1100,  # Start captions here
            'caption_y_max': 1700,  # End captions here
            'caption_y_center': 1400,  # Default position
                    }
