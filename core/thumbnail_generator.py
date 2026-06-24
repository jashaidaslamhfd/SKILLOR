"""
Thumbnail Generator - Production Ready
OPTIMIZED FOR: 35-54 Male USA/UK Audience

FEATURES:
1. 3 BIG words + 1 emoji (High contrast, readable)
2. Dark navy/dark backgrounds (credible science feel)
3. Gold/White text (trustworthy, not clickbait)
4. Motion blur speed lines (suggests video content)
5. Asymmetric layout (visual tension = stops scrolling)
6. Cinematic vignette + gradient
7. Pattern interrupt (circle/arrow shapes)
8. Border frame (orange + cyan)
"""

import os
import random
import math
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from config.settings import THUMBNAIL_CONFIG


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert '#rrggbb' to (r, g, b)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load system bold fonts with fallback"""
    import platform
    
    candidates = []
    
    # Windows
    if platform.system() == 'Windows':
        candidates = [
            "C:/Windows/Fonts/ArialBD.ttf",
            "C:/Windows/Fonts/Impact.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    # macOS
    elif platform.system() == 'Darwin':
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    # Linux
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "arialbd.ttf",
        ]
    
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    
    # Last resort - default font
    return ImageFont.load_default()


class ThumbnailGenerator:
    """Production Thumbnail Generator for 35-54 Male Audience"""
    
    def __init__(self):
        self.width, self.height = getattr(THUMBNAIL_CONFIG, 'RESOLUTION', (1080, 1920))
        self.style = getattr(THUMBNAIL_CONFIG, 'STYLE', 'credible')
        
        # Colors
        self.bg_colors = getattr(THUMBNAIL_CONFIG, 'BG_COLORS', [
            "#050A1A", "#0A0F1E", "#080D18", "#060B15", "#0D1220"
        ])
        self.text_colors = getattr(THUMBNAIL_CONFIG, 'TEXT_COLORS', [
            "#FFD700", "#FFFFFF", "#4FC3F7", "#E8E8E8", "#FFF9C4"
        ])
        self.accent_colors = getattr(THUMBNAIL_CONFIG, 'ACCENT_COLORS', [
            "#4A90D9", "#FFD700", "#FFFFFF"
        ])
        
        # Font sizes
        self.font_size_main = getattr(THUMBNAIL_CONFIG, 'FONT_SIZE_MAIN', 130)
        self.font_size_sub = getattr(THUMBNAIL_CONFIG, 'FONT_SIZE_SUB', 52)
        self.font_size_emoji = 80
        
        print(f"🖼️ ThumbnailGenerator initialized")

    # ============================================================
    # MAIN GENERATE METHOD
    # ============================================================
    
    def generate_thumbnail(self, words: List[str], topic: str, output_path: str) -> str:
        """
        Generate high-retention viral thumbnail
        
        Args:
            words: List of 3 words for thumbnail (e.g., ['MEMORY', 'BRAIN', 'FOG'])
            topic: Topic for emoji selection
            output_path: Where to save the thumbnail
        
        Returns:
            Path to generated thumbnail
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # ============================================================
        # Step 1: Create background
        # ============================================================
        bg_hex = random.choice(self.bg_colors)
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(bg_hex))
        
        # ============================================================
        # Step 2: Add cinematic background effects
        # ============================================================
        img = self._add_background_effects(img)
        
        # ============================================================
        # Step 3: Add motion lines (suggests video content)
        # ============================================================
        img = self._add_motion_lines(img)
        
        # ============================================================
        # Step 4: Add pattern interrupt (circle/arrow)
        # ============================================================
        img = self._add_pattern_interrupt(img)
        
        # ============================================================
        # Step 5: Prepare words (ensure 3 words)
        # ============================================================
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "LIES", "DARK", "HIDDEN"]))
        
        # ============================================================
        # Step 6: Get fonts
        # ============================================================
        font_large = _load_font(self.font_size_main)
        font_emoji = _load_font(self.font_size_emoji)
        
        # ============================================================
        # Step 7: Asymmetric layout - visual tension
        # ============================================================
        y_positions = [
            self.height // 5 + random.randint(-30, 30),       # Top word
            self.height // 2 + random.randint(-20, 20),       # Middle word
            int(self.height * 0.72) + random.randint(-40, 40) # Bottom word
        ]
        
        # ============================================================
        # Step 8: Draw each word with random rotation
        # ============================================================
        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            rotation = random.randint(-6, 6) if i % 2 == 0 else 0
            color = self.text_colors[i % len(self.text_colors)]
            
            # Add glow effect
            if getattr(THUMBNAIL_CONFIG, 'GLOW_EFFECT', False):
                img = self._add_glow(img, word, y, font_large, color, rotation)
            
            # Add shadow
            if getattr(THUMBNAIL_CONFIG, 'DROP_SHADOW', True):
                img = self._add_text_with_shadow(img, word, y, font_large, color, rotation)
            else:
                img = self._draw_rotated_text(img, word, y, font_large, color, rotation)
            
            # Add emoji near word (3rd visual element)
            emoji = self._get_emoji_for_word(word, topic)
            if emoji:
                img = self._draw_emoji(img, emoji, y, font_emoji)
        
        # ============================================================
        # Step 9: Add topic banner at top
        # ============================================================
        draw = ImageDraw.Draw(img)
        font_small = _load_font(self.font_size_sub)
        self._add_topic_banner(draw, topic, font_small)
        
        # ============================================================
        # Step 10: Add border frame
        # ============================================================
        self._add_border_frame(draw)
        
        # ============================================================
        # Step 11: Add subtle play button hint
        # ============================================================
        self._add_play_hint(draw)
        
        # ============================================================
        # Step 12: Save
        # ============================================================
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95)
        print(f"    🎨 Thumbnail: {output_path} | Words: {words_chunk}")
        
        return output_path

    # ============================================================
    # BACKGROUND EFFECTS
    # ============================================================
    
    def _add_background_effects(self, img: Image.Image) -> Image.Image:
        """Add cinematic vignette + radial gradient"""
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Vignette
        for i in range(0, self.height):
            edge_factor = abs(i - (self.height // 2)) / (self.height // 2)
            alpha = int(180 * (edge_factor ** 2) * 0.5)
            draw.line([(0, i), (self.width, i)], fill=(0, 0, 0, alpha))
        
        # Subtle radial gradient from center
        center_x, center_y = self.width // 2, self.height // 2
        for r in range(0, 400, 20):
            alpha = int(30 * (1 - r / 400))
            draw.ellipse(
                [center_x - r, center_y - r, center_x + r, center_y + r],
                outline=(0, 212, 255, alpha),
                width=2
            )
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        return img.convert("RGB")

    # ============================================================
    # MOTION LINES
    # ============================================================
    
    def _add_motion_lines(self, img: Image.Image) -> Image.Image:
        """Add speed lines suggesting video content"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Diagonal speed lines
        for i in range(6):
            x_start = random.randint(-100, self.width)
            y_start = random.randint(-100, 0)
            length = random.randint(300, 600)
            angle = random.uniform(30, 60)
            
            x_end = x_start + int(length * math.cos(math.radians(angle)))
            y_end = y_start + int(length * math.sin(math.radians(angle)))
            
            alpha = random.randint(20, 50)
            draw.line(
                [(x_start, y_start), (x_end, y_end)],
                fill=(255, 255, 255, alpha),
                width=random.randint(2, 4)
            )
        
        # Slight blur for motion feel
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=2))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # PATTERN INTERRUPT
    # ============================================================
    
    def _add_pattern_interrupt(self, img: Image.Image) -> Image.Image:
        """Add eye-catching shape (circle/arrow) - breaks visual grid"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        shape_type = random.choice(['circle', 'arrow'])
        
        if shape_type == 'circle':
            x = random.choice([100, self.width - 100])
            y = random.randint(300, 1600)
            radius = random.randint(80, 150)
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                outline=(255, 107, 53, 150),
                width=6
            )
        else:  # arrow
            x = random.choice([50, self.width - 50])
            y = self.height // 2
            points = [
                (x, y - 40),
                (x + 60 if x < 500 else x - 60, y),
                (x, y + 40),
                (x, y + 20),
                (x + 40 if x < 500 else x - 40, y),
                (x, y - 20)
            ]
            draw.polygon(points, fill=(0, 212, 255, 180))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # EMOJI
    # ============================================================
    
    def _get_emoji_for_word(self, word: str, topic: str) -> str:
        """Select relevant emoji based on word/topic"""
        word_lower = word.lower()
        topic_lower = topic.lower()
        
        emoji_map = {
            'memory': '🧠', 'brain': '🧠', 'mind': '🧠',
            'forget': '🤔', 'think': '🤔',
            'fog': '🌫️', 'foggy': '🌫️',
            'name': '👤', 'names': '👤',
            'room': '🚪', 'door': '🚪',
            'word': '💬', 'words': '💬',
            'stress': '😰', 'anxiety': '😰',
            'sleep': '😴', 'tired': '😴',
            'health': '❤️', 'body': '💪',
            'science': '🔬',
            'truth': '⚡', 'secret': '🤫', 'dark': '🌑',
        }
        
        # Check word first
        for key, emoji in emoji_map.items():
            if key in word_lower:
                return emoji
        
        # Check topic
        for key, emoji in emoji_map.items():
            if key in topic_lower:
                return emoji
        
        # Default
        return '🧠'

    def _draw_emoji(self, img: Image.Image, emoji: str, y: int, font) -> Image.Image:
        """Draw emoji as 3rd visual element"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        
        x = int(self.width * 0.65) + random.randint(-20, 20)
        adjusted_y = y + random.randint(-30, 30)
        
        draw.text((x, adjusted_y), emoji, font=font)
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # TEXT WITH SHADOW
    # ============================================================
    
    def _add_text_with_shadow(self, img: Image.Image, text: str, y: int, 
                               font, color: str, rotation: int = 0) -> Image.Image:
        """Draw text with shadow and optional rotation"""
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        adjusted_y = y - (text_height // 2)
        
        # Shadow
        thickness = 8
        for dx in range(-thickness, thickness + 1, 2):
            for dy in range(-thickness, thickness + 1, 2):
                if dx*dx + dy*dy <= thickness*thickness:
                    txt_draw.text(
                        (x + dx, adjusted_y + dy), 
                        text, 
                        fill="black", 
                        font=font
                    )
        
        # Main text
        txt_draw.text((x, adjusted_y), text, fill=color, font=font)
        
        # Rotate if needed
        if rotation != 0:
            txt_layer = txt_layer.rotate(rotation, expand=False, center=(self.width // 2, y))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    def _draw_rotated_text(self, img: Image.Image, text: str, y: int,
                            font, color: str, rotation: int = 0) -> Image.Image:
        """Draw rotated text without shadow"""
        if rotation == 0:
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            y_pos = y - (text_height // 2)
            draw.text((x, y_pos), text, fill=color, font=font)
            return img
        
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        txt_draw.text((x, y_pos), text, fill=color, font=font)
        txt_layer = txt_layer.rotate(rotation, expand=False, center=(self.width // 2, y))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    # ============================================================
    # GLOW EFFECT
    # ============================================================
    
    def _add_glow(self, img: Image.Image, text: str, y: int,
                   font, color: str, rotation: int = 0) -> Image.Image:
        """Add glow effect behind text"""
        r, g, b = _hex_to_rgb(color)
        
        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        bbox = glow_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        # Multi-pass glow
        for offset in range(28, 0, -5):
            alpha = int(90 * (1 - offset / 28))
            glow_color = (r, g, b, alpha)
            glow_draw.text((x, y_pos), text, fill=glow_color, font=font)
        
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=16))
        
        if rotation != 0:
            glow_layer = glow_layer.rotate(rotation, expand=False, center=(self.width // 2, y))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, glow_layer)
        return img.convert("RGB")

    # ============================================================
    # TOPIC BANNER
    # ============================================================
    
    def _add_topic_banner(self, draw: ImageDraw.Draw, topic: str, font):
        """Add topic banner at TOP (visible on Shorts shelf)"""
        topic_text = f"🧠 {topic[:20].upper()} SCIENCE"
        bbox = draw.textbbox((0, 0), topic_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        banner_y = 60
        banner_padding = 20
        
        draw.rounded_rectangle(
            [
                (self.width // 2 - text_width // 2 - banner_padding, banner_y - banner_padding),
                (self.width // 2 + text_width // 2 + banner_padding, banner_y + text_height + banner_padding)
            ],
            radius=15,
            fill="#FF6B35",
            outline="#FFFFFF",
            width=3
        )
        
        x = (self.width - text_width) // 2
        draw.text((x, banner_y), topic_text, fill="#FFFFFF", font=font)

    # ============================================================
    # BORDER FRAME
    # ============================================================
    
    def _add_border_frame(self, draw: ImageDraw.Draw):
        """Add border frame (orange outer + cyan inner)"""
        border_width = 14
        
        # Outer: Orange
        draw.rectangle(
            [
                (border_width // 2, border_width // 2),
                (self.width - border_width // 2, self.height - border_width // 2),
            ],
            outline="#FF6B35",
            width=border_width,
        )
        
        # Inner: Cyan
        inner_padding = border_width + 4
        draw.rectangle(
            [
                (inner_padding, inner_padding),
                (self.width - inner_padding, self.height - inner_padding),
            ],
            outline="#00D4FF",
            width=3,
        )

    # ============================================================
    # PLAY HINT
    # ============================================================
    
    def _add_play_hint(self, draw: ImageDraw.Draw):
        """Add subtle play button triangle"""
        center_x = self.width // 2
        bottom_y = self.height - 200
        size = 30
        
        points = [
            (center_x - size, bottom_y - size),
            (center_x + size, bottom_y),
            (center_x - size, bottom_y + size)
        ]
        draw.polygon(points, fill=(255, 255, 255, 150))


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING THUMBNAIL GENERATOR\n" + "="*60)
    
    generator = ThumbnailGenerator()
    
    # Test with sample words
    test_words = ["MEMORY", "BRAIN", "FOG"]
    test_topic = "forgetting names"
    test_output = "test_thumbnail.jpg"
    
    generator.generate_thumbnail(test_words, test_topic, test_output)
    
    print(f"\n✅ Thumbnail saved: {test_output}")