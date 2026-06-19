"""Auto-sync Caption Generator - Red/White Alternating + Center Screen + Bold"""

from typing import List, Dict
from config.settings import CAPTION_CONFIG


class CaptionGenerator:
    def __init__(self):
        self.max_words_per_line = CAPTION_CONFIG.MAX_WORDS_PER_LINE
        self.alternate_colors = CAPTION_CONFIG.ALTERNATE_COLORS
        
    def generate_captions(self, word_timings: List[Dict]) -> List[Dict]:
        """Process word timings for better caption display with Red/White alternating colors"""
        captions = []
        current_line = []
        current_start = 0
        
        for i, timing in enumerate(word_timings):
            if not current_line:
                current_start = timing['start']
            
            current_line.append(timing)
            
            # 2026: Shorter lines (2 words) for faster retention
            if len(current_line) >= self.max_words_per_line or i == len(word_timings) - 1:
                text = ' '.join([w['word'] for w in current_line])
                end = current_line[-1]['end']
                
                # Alternate colors: even lines = RED, odd lines = WHITE
                line_idx = len(captions)
                if self.alternate_colors:
                    color = "red" if line_idx % 2 == 0 else "white"
                    outline = "black"
                else:
                    color = "white"
                    outline = "black"
                
                captions.append({
                    'text': text.upper(),  # ALL CAPS for impact
                    'start': current_start,
                    'end': end,
                    'words': current_line,
                    'color': color,
                    'outline': outline,
                    'bold': True,
                    'line_index': line_idx
                })
                current_line = []
        
        return captions
    
    def generate_ass_styles(self) -> Dict:
        """Generate ASS subtitle styles for Red/White alternating captions"""
        return {
            'red': {
                'fontname': CAPTION_CONFIG.FONT_NAME,
                'fontsize': CAPTION_CONFIG.FONT_SIZE,
                'primary_color': '&H000000FF',  # Red in ASS format (BGR)
                'secondary_color': '&H000000FF',
                'outline_color': '&H00000000',  # Black outline
                'back_color': '&H00000000',
                'bold': CAPTION_CONFIG.BOLD,
                'outline': CAPTION_CONFIG.OUTLINE_WIDTH,
                'shadow': CAPTION_CONFIG.SHADOW,
                'alignment': CAPTION_CONFIG.ALIGNMENT,  # 10 = center
                'margin_v': CAPTION_CONFIG.MARGIN_V,  # 960 = center of 1920
            },
            'white': {
                'fontname': CAPTION_CONFIG.FONT_NAME,
                'fontsize': CAPTION_CONFIG.FONT_SIZE,
                'primary_color': '&H00FFFFFF',  # White
                'secondary_color': '&H00FFFFFF',
                'outline_color': '&H00000000',  # Black outline
                'back_color': '&H00000000',
                'bold': CAPTION_CONFIG.BOLD,
                'outline': CAPTION_CONFIG.OUTLINE_WIDTH,
                'shadow': CAPTION_CONFIG.SHADOW,
                'alignment': CAPTION_CONFIG.ALIGNMENT,
                'margin_v': CAPTION_CONFIG.MARGIN_V,
            }
                }
