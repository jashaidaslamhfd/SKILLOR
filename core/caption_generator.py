"""Auto-sync Caption Generator - Karaoke Word-by-Word + Pop Effects + Safe Zone"""

from typing import List, Dict
from config.settings import CAPTION_CONFIG


class CaptionGenerator:
    def __init__(self):
        self.max_words_per_line = getattr(CAPTION_CONFIG, 'MAX_WORDS_PER_LINE', 3)
        self.alternate_colors = getattr(CAPTION_CONFIG, 'ALTERNATE_COLORS', True)
        self.font_size = getattr(CAPTION_CONFIG, 'FONT_SIZE', 90)
        self.font_name = getattr(CAPTION_CONFIG, 'FONT_NAME', 'Arial')
        self.bold = getattr(CAPTION_CONFIG, 'BOLD', True)
        self.outline_width = getattr(CAPTION_CONFIG, 'OUTLINE_WIDTH', 4)
        self.shadow = getattr(CAPTION_CONFIG, 'SHADOW', 2)

    def generate_captions(self, word_timings: List[Dict]) -> List[Dict]:
        """Generate karaoke-style caption metadata (not the ASS file itself).
        Used by anything that wants structured caption data rather than a
        rendered subtitle file."""
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

                has_numbers = any(char.isdigit() for char in text)
                has_shock_words = any(w in text.lower() for w in ['shock', 'terrify', 'scary', 'dark', 'secret', 'truth', 'never', 'always', 'everyone', 'nobody'])

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
                    'has_numbers': has_numbers,
                    'has_shock_words': has_shock_words,
                    'position_y': 1400,
                    'position_x': 540,
                })

                current_line = []
                line_idx += 1

        print(f"    [CAPTIONS] {len(captions)} lines | {sum(len(c['words']) for c in captions)} words")
        return captions

    def generate_karaoke_ass(self, word_timings: List[Dict], ass_path: str, max_duration: float = None) -> str:
        """Generate ASS subtitle file with karaoke word-by-word highlighting.

        FIX (root cause of the "double/glitchy caption" visual bug): the
        previous version emitted TWO overlapping sets of Dialogue events for
        every group of words -- one "full line with embedded \\t() karaoke
        transform tags" line, PLUS a second full set of "individual active
        word" lines on top of it, at the *same* timestamps. libass renders
        both simultaneously, which is exactly what looked like a blurry/
        doubled/"filtered" caption on screen. This version emits exactly
        ONE Dialogue line per word -- no transform tags, no duplicate
        overlapping events -- so there is only ever one thing on screen at
        any instant, matching the simpler (and correct) approach already
        used elsewhere in this codebase's video assembler.

        FIX: Alignment is bottom-center (2) instead of middle-center (10).
        An Alignment of 10 combined with a large MarginV (1400) was
        previously fighting itself -- middle-center alignment treats
        MarginV very differently from bottom alignment, and the combination
        pushed captions toward the upper-middle of the frame instead of a
        clean, predictable spot near the bottom safe zone.

        FIX: MarginL/MarginR widened from 10 to 60, so long single words
        can no longer overflow past the left/right edges of a 1080px-wide
        9:16 frame (previously visible as captions being cut off at the
        screen edge).

        FIX: each word is sanitized (commas, braces, backslashes,
        non-printable characters stripped) before being placed into the
        Dialogue Text field. ASS Dialogue lines are comma-separated; a
        stray comma or unescaped brace inside a word shifts field
        boundaries and can merge timestamp text into the caption itself
        (previously visible as e.g. "WORD0:00:28.74" glued together).
        """
        width = 1080
        height = 1920
        font_size = self.font_size
        alignment = 2          # bottom-center
        margin_v = max(getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 280), 220)
        margin_lr = 60          # wide enough that long words can't clip off-screen

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,{self.font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},{alignment},{margin_lr},{margin_lr},{margin_v},1
Style: Red,{self.font_name},{font_size},&H000000FF,&H00FFFFFF,&H00000000,&H00000000,{1 if self.bold else 0},0,0,0,100,100,2,0,1,{self.outline_width},{self.shadow},{alignment},{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        def sanitize_word(word: str) -> str:
            w = str(word).strip().upper()
            w = w.replace(',', '')
            w = w.replace('{', '').replace('}', '')
            w = w.replace('\\', '')
            w = ''.join(ch for ch in w if ch.isprintable())
            return w.strip()

        # Sort + de-overlap timings up front (mirrors the same safety pass
        # used in video_assembler.py's caption renderer) so two words can
        # never be visible at the exact same instant due to estimated/
        # fallback timing overlap.
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
            if end <= start:
                continue
            clean_timings.append({**wt, 'start': start, 'end': end})

        lines = []
        line_idx = 0
        current_line = []

        for i, timing in enumerate(clean_timings):
            current_line.append(timing)

            if len(current_line) >= self.max_words_per_line or i == len(clean_timings) - 1:
                style = "Red" if line_idx % 2 == 0 else "White"

                # One Dialogue event per word -- single layer, no
                # duplicate/overlapping events, no embedded transform tags.
                for wt in current_line:
                    word = sanitize_word(wt.get('word', ''))
                    if not word:
                        continue
                    w_start = self._seconds_to_ass(wt['start'])
                    w_end = self._seconds_to_ass(wt['end'])
                    lines.append(f"Dialogue: 0,{w_start},{w_end},{style},,0,0,0,,{word}")

                current_line = []
                line_idx += 1

        if not lines:
            lines.append("Dialogue: 0,0:00:00.00,0:00:05.00,White,,0,0,0,, ")

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(header + "\n".join(lines) + "\n")

        print(f"    [CAPTIONS] Karaoke ASS: {len(lines)} events | {line_idx} groups | align:{alignment} marginV:{margin_v} marginLR:{margin_lr}")
        return ass_path

    def _seconds_to_ass(self, s: float) -> str:
        """Convert seconds to ASS time format"""
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sc = int(s % 60)
        cs = int((s % 1) * 100)
        return f"{h}:{m:02d}:{sc:02d}.{cs:02d}"

    def generate_ass_styles(self) -> Dict:
        """Returns style metadata (kept for backward compatibility with any
        other code that introspects style info; the ASS file itself no
        longer uses center/middle alignment -- see generate_karaoke_ass)."""
        margin_v = max(getattr(CAPTION_CONFIG, 'SAFE_ZONE_BOTTOM', 280), 220)

        return {
            'red': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': '&H000000FF',
                'secondary_color': '&H000000FF',
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': 2,
                'margin_v': margin_v,
            },
            'white': {
                'fontname': self.font_name,
                'fontsize': self.font_size,
                'primary_color': '&H00FFFFFF',
                'secondary_color': '&H00FFFFFF',
                'outline_color': '&H00000000',
                'back_color': '&H00000000',
                'bold': 1 if self.bold else 0,
                'outline': self.outline_width,
                'shadow': self.shadow,
                'alignment': 2,
                'margin_v': margin_v,
            },
        }

    def get_safe_zone(self) -> Dict:
        """Return YouTube Shorts safe zone for caption positioning"""
        return {
            'width': 1080,
            'height': 1920,
            'safe_top': 0,
            'safe_bottom': 350,
            'caption_y_min': 1100,
            'caption_y_max': 1700,
            'caption_y_center': 1400,
        }
