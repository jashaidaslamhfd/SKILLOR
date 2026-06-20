"""Viral Thumbnail Generator — 3 Big Words + Eye Pattern + Motion Blur + Asymmetric Layout"""

import os
import random
import math
from typing import List

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from config.settings import THUMBNAIL_CONFIG


def _hex_to_rgb(hex_color: str):
    """Convert '#rrggbb' → (r, g, b)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try system bold fonts, fall back cleanly to safe backup stacks."""
    candidates = [
        "arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "Impact.ttf",  # NEW: Impact = viral thumbnail standard
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class ThumbnailGenerator:
    def __init__(self):
        self.width, self.height = getattr(THUMBNAIL_CONFIG, 'RESOLUTION', (1080, 1920))

    def generate_thumbnail(self, words: List[str], topic: str, output_path: str) -> str:
        """Generate high-retention viral thumbnail with eye pattern + motion blur + asymmetric layout"""
        
        # FIX: Color psychology — orange/amber for curiosity, cyan for mystery
        bg_colors = [
            "#0A0A1A",  # Deep blue-black (mystery)
            "#1A0505",  # Dark red-black (urgency)
            "#0F1A0A",  # Dark green-black (intrigue)
            "#1A1005",  # Dark amber-black (curiosity)
            "#050A1A",  # Dark blue (science)
        ]
        bg_hex = random.choice(bg_colors)
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(bg_hex))

        # Add cinematic background effects
        img = self.add_background_effects(img)
        
        # NEW: Add motion blur speed lines — suggests video, not static
        img = self.add_motion_lines(img)
        
        # NEW: Add eye-catching shape (circle/arrow) — pattern interrupt
        img = self.add_pattern_interrupt(img)

        font_large = _load_font(getattr(THUMBNAIL_CONFIG, 'FONT_SIZE_MAIN', 140))
        font_small = _load_font(getattr(THUMBNAIL_CONFIG, 'FONT_SIZE_SUB', 50))
        font_emoji = _load_font(80)  # NEW: For emoji overlay

        # FIX: Asymmetric layout — words not perfectly centered
        # Creates visual tension = eye stops scrolling
        y_positions = [
            self.height // 5 + random.randint(-30, 30),      # Top word: slight offset
            self.height // 2 + random.randint(-20, 20),      # Middle: near center
            int(self.height * 0.72) + random.randint(-40, 40)  # Bottom: more offset
        ]

        # Ensure 3 words
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "LIES", "DARK", "HIDDEN"]))

        # FIX: Color psychology for text
        text_colors = [
            "#FF6B35",  # Orange = curiosity, urgency
            "#00D4FF",  # Cyan = mystery, science
            "#FFD700",  # Gold = value, premium
            "#FF3366",  # Pink-red = shock
            "#39FF14",  # Neon green = intrigue
        ]

        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            # FIX: Random slight rotation for each word — asymmetric tension
            rotation = random.randint(-5, 5) if i % 2 == 0 else 0
            
            color = text_colors[i % len(text_colors)]
            
            # NEW: Add emoji overlay for 3rd visual element
            emoji = self._get_emoji_for_word(word, topic)
            
            if getattr(THUMBNAIL_CONFIG, 'GLOW_EFFECT', True):
                img = self.add_glow(img, word, y, font_large, color, rotation)

            draw = ImageDraw.Draw(img)

            if getattr(THUMBNAIL_CONFIG, 'DROP_SHADOW', True):
                img = self.add_text_with_shadow(img, word, y, font_large, color, rotation)
            else:
                img = self.draw_rotated_text(img, word, (self.width // 2, y), font_large, color, rotation)

            # NEW: Draw emoji near word
            if emoji:
                self.draw_emoji(draw, emoji, y, font_emoji)

        # FIX: Topic banner at TOP (visible on Shorts shelf) instead of bottom
        draw = ImageDraw.Draw(img)
        self.add_topic_banner(draw, topic, font_small)

        # Add border frame
        self.add_border_frame(draw)

        # NEW: Add "play button" hint — suggests video content
        self.add_play_hint(draw)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        final_img = img.convert("RGB")
        final_img.save(output_path, "JPEG", quality=95)
        print(f"    🎨 Viral Thumbnail: {output_path} | Words: {words_chunk}")
        return output_path

    def _get_emoji_for_word(self, word: str, topic: str) -> str:
        """NEW: Select relevant emoji based on word/topic for 3rd visual element"""
        word_lower = word.lower()
        topic_lower = topic.lower()

        emoji_map = {
            'brain': '🧠', 'mind': '🧠', 'think': '🤔', 'memory': '🧩',
            'eye': '👁️', 'see': '👁️', 'watch': '👁️', 'look': '👀',
            'dark': '🌑', 'secret': '🤫', 'hidden': '🕵️', 'truth': '⚡',
            'sleep': '😴', 'dream': '💭', 'night': '🌙', 'fear': '😰',
            'body': '💪', 'heart': '❤️', 'blood': '🩸', 'nerve': '⚡',
            'science': '🔬', 'brain': '🧠', 'psychology': '🧠', 'neuron': '⚡',
        }

        # Check word first
        for key, emoji in emoji_map.items():
            if key in word_lower:
                return emoji

        # Check topic
        for key, emoji in emoji_map.items():
            if key in topic_lower:
                return emoji

        # Default based on topic sentiment
        if any(w in topic_lower for w in ['dark', 'secret', 'hidden', 'mystery']):
            return '🌑'
        elif any(w in topic_lower for w in ['brain', 'mind', 'think', 'memory']):
            return '🧠'
        elif any(w in topic_lower for w in ['sleep', 'dream', 'night']):
            return '🌙'

        return '⚡'  # Default: energy/electricity

    def draw_emoji(self, draw: ImageDraw.Draw, emoji: str, y: int, font):
        """NEW: Draw emoji as 3rd visual element — breaks text monotony"""
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        # Position emoji to the right of center, creating asymmetry
        x = int(self.width * 0.65) + random.randint(-20, 20)
        adjusted_y = y + random.randint(-30, 30)
        draw.text((x, adjusted_y), emoji, font=font)

    def add_topic_banner(self, draw: ImageDraw.Draw, topic: str, font):
        """NEW: Topic banner at TOP — visible on Shorts shelf"""
        topic_text = f"🔬 {topic.upper()} SCIENCE"
        bbox = draw.textbbox((0, 0), topic_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Banner background
        banner_y = 60
        banner_padding = 20
        draw.rounded_rectangle(
            [
                (self.width // 2 - text_width // 2 - banner_padding, banner_y - banner_padding),
                (self.width // 2 + text_width // 2 + banner_padding, banner_y + text_height + banner_padding)
            ],
            radius=15,
            fill="#FF6B35",  # Orange banner
            outline="#FFFFFF",
            width=3
        )

        # Banner text
        x = (self.width - text_width) // 2
        draw.text((x, banner_y), topic_text, fill="#FFFFFF", font=font)

    def add_pattern_interrupt(self, img: Image.Image) -> Image.Image:
        """NEW: Add eye-catching shape — circle or arrow that breaks the grid"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        shape_type = random.choice(['circle', 'arrow', 'burst'])

        if shape_type == 'circle':
            # Partial circle — creates tension
            x = random.choice([100, self.width - 100])
            y = random.randint(300, 1600)
            radius = random.randint(80, 150)
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                outline=(255, 107, 53, 180),  # Orange
                width=8
            )
        elif shape_type == 'arrow':
            # Arrow pointing to center
            x = random.choice([50, self.width - 50])
            y = self.height // 2
            points = [
                (x, y - 40), (x + 60 if x < 500 else x - 60, y),
                (x, y + 40), (x, y + 20), (x + 40 if x < 500 else x - 40, y),
                (x, y - 20)
            ]
            draw.polygon(points, fill=(0, 212, 255, 200))  # Cyan arrow
        else:  # burst
            # Speed lines from center
            center = (self.width // 2, self.height // 2)
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x1 = center[0] + math.cos(rad) * 200
                y1 = center[1] + math.sin(rad) * 200
                x2 = center[0] + math.cos(rad) * 350
                y2 = center[1] + math.sin(rad) * 350
                draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 100), width=3)

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    def add_motion_lines(self, img: Image.Image) -> Image.Image:
        """NEW: Add motion blur speed lines — suggests video, not static image"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Diagonal speed lines
        for i in range(5):
            x_start = random.randint(-100, self.width)
            y_start = random.randint(-100, 0)
            length = random.randint(300, 600)
            angle = random.uniform(30, 60)  # Diagonal

            x_end = x_start + int(length * math.cos(math.radians(angle)))
            y_end = y_start + int(length * math.sin(math.radians(angle)))

            alpha = random.randint(20, 60)
            draw.line(
                [(x_start, y_start), (x_end, y_end)],
                fill=(255, 255, 255, alpha),
                width=random.randint(2, 5)
            )

        # Apply slight blur for motion feel
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=2))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    def draw_rotated_text(self, img: Image.Image, text: str, position: tuple, font, color: str, rotation: int = 0) -> Image.Image:
        """NEW: Draw text with slight rotation for asymmetric tension"""
        if rotation == 0:
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            y = position[1] - (text_height // 2)
            draw.text((x, y), text, fill=color, font=font)
            return img

        # Create rotated text on transparent layer
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)

        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = position[1] - (text_height // 2)

        txt_draw.text((x, y), text, fill=color, font=font)

        # Rotate
        txt_layer = txt_layer.rotate(rotation, expand=False, center=(self.width // 2, position[1]))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    def add_background_effects(self, img: Image.Image) -> Image.Image:
        """Adds cinematic vignette + gradient overlays"""
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)

        # Vignette
        for i in range(0, self.height):
            edge_factor = abs(i - (self.height // 2)) / (self.height // 2)
            alpha = int(180 * (edge_factor ** 2) * 0.5)
            draw.line([(0, i), (self.width, i)], fill=(0, 0, 0, alpha))

        # NEW: Subtle radial gradient from center
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

    def add_glow(self, img: Image.Image, text: str, y: int, font, color: str, rotation: int = 0) -> Image.Image:
        """Enhanced glow with rotation support"""
        r, g, b = _hex_to_rgb(color)

        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        bbox = glow_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        adjusted_y = y - (text_height // 2)

        # Multi-pass glow
        for offset in range(28, 0, -5):
            alpha = int(90 * (1 - offset / 28))
            glow_color = (r, g, b, alpha)
            glow_draw.text((x, adjusted_y), text, fill=glow_color, font=font)

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=16))

        # Apply rotation to glow if needed
        if rotation != 0:
            glow_layer = glow_layer.rotate(rotation, expand=False, center=(self.width // 2, y))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, glow_layer)
        return img.convert("RGB")

    def add_text_with_shadow(self, img: Image.Image, text: str, y: int, font, color: str, rotation: int = 0) -> Image.Image:
        """Enhanced shadow with rotation support"""
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)

        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        adjusted_y = y - (text_height // 2)

        # Ultra-thick shadow (circular expansion)
        thickness = 8
        for dx in range(-thickness, thickness + 1, 2):
            for dy in range(-thickness, thickness + 1, 2):
                if dx*dx + dy*dy <= thickness*thickness:
                    txt_draw.text((x + dx, adjusted_y + dy), text, fill="black", font=font)

        # Main text
        txt_draw.text((x, adjusted_y), text, fill=color, font=font)

        # Rotate if needed
        if rotation != 0:
            txt_layer = txt_layer.rotate(rotation, expand=False, center=(self.width // 2, y))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    def add_play_hint(self, draw: ImageDraw.Draw):
        """NEW: Subtle play button triangle — suggests video content"""
        # Small triangle at bottom center
        center_x = self.width // 2
        bottom_y = self.height - 200
        size = 30

        points = [
            (center_x - size, bottom_y - size),
            (center_x + size, bottom_y),
            (center_x - size, bottom_y + size)
        ]
        draw.polygon(points, fill=(255, 255, 255, 180))

    def add_border_frame(self, draw: ImageDraw.Draw):
        """Enhanced border with gradient feel"""
        border_width = 14
        
        # Outer border: orange
        draw.rectangle(
            [
                (border_width // 2, border_width // 2),
                (self.width - border_width // 2, self.height - border_width // 2),
            ],
            outline="#FF6B35",  # Orange = curiosity
            width=border_width,
        )
        
        # Inner thin line: cyan
        inner_padding = border_width + 4
        draw.rectangle(
            [
                (inner_padding, inner_padding),
                (self.width - inner_padding, self.height - inner_padding),
            ],
            outline="#00D4FF",  # Cyan = mystery
            width=3,
        )
