"""Viral Thumbnail Generator
3 Big Words, Suspense Style, Full HD
"""

import os
import random
from typing import List

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

from config.settings import THUMBNAIL_CONFIG


def _hex_to_rgb(hex_color: str):
    """Convert '#rrggbb' → (r, g, b)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try system bold fonts, fall back to Pillow default."""
    candidates = [
        "arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class ThumbnailGenerator:
    def __init__(self):
        self.width, self.height = THUMBNAIL_CONFIG.RESOLUTION

    def generate_thumbnail(self, words: List[str], topic: str, output_path: str) -> str:
        """Generate viral thumbnail with 3 big words"""
        # FIX: _hex_to_rgb helper added because Image.new() requires a tuple,
        # not a hex string; previously caused TypeError with bg_colors.
        bg_hex = random.choice(THUMBNAIL_CONFIG.BG_COLORS)
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(bg_hex))

        img = self.add_background_effects(img)
        draw = ImageDraw.Draw(img)

        font_large = _load_font(THUMBNAIL_CONFIG.FONT_SIZE_MAIN)
        font_small = _load_font(THUMBNAIL_CONFIG.FONT_SIZE_SUB)

        y_positions = [180, 360, 540]

        for i, (word, y) in enumerate(zip(words, y_positions)):
            color = THUMBNAIL_CONFIG.TEXT_COLORS[i % len(THUMBNAIL_CONFIG.TEXT_COLORS)]

            if THUMBNAIL_CONFIG.GLOW_EFFECT:
                img = self.add_glow(img, word, y, font_large, color)
                draw = ImageDraw.Draw(img)  # FIX: re-create draw after img reassignment

            if THUMBNAIL_CONFIG.DROP_SHADOW:
                self.add_text_with_shadow(draw, word, (self.width // 2, y), font_large, color)
            else:
                bbox = draw.textbbox((0, 0), word, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y), word, fill=color, font=font_large)

        topic_text = f"#{topic.replace(' ', '')}"
        bbox = draw.textbbox((0, 0), topic_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, self.height - 80), topic_text, fill="#888888", font=font_small)

        self.add_border_frame(draw)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path, "JPEG", quality=95)
        return output_path

    def add_background_effects(self, img: Image.Image) -> Image.Image:
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        for i in range(0, self.height, 2):
            alpha = int(255 * (1 - i / self.height) * 0.3)
            draw.line([(0, i), (self.width, i)], fill=(0, 0, 0, alpha))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        img = img.convert("RGB")
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        return img

    def add_glow(self, img: Image.Image, text: str, y: int, font, color: str) -> Image.Image:
        r, g, b = _hex_to_rgb(color)

        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        for offset in range(20, 0, -4):
            alpha = int(50 * (1 - offset / 20))
            glow_color = (r, g, b, alpha)
            bbox = glow_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            glow_draw.text((x, y), text, fill=glow_color, font=font)

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, glow_layer)
        return img.convert("RGB")

    def add_text_with_shadow(self, draw: ImageDraw.Draw, text: str, position: tuple, font, color: str):
        x, y = position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2

        shadow_offset = 6
        for dx in range(-shadow_offset, shadow_offset + 1, 2):
            for dy in range(-shadow_offset, shadow_offset + 1, 2):
                draw.text((x + dx, y + dy), text, fill="black", font=font)

        draw.text((x, y), text, fill=color, font=font)

    def add_border_frame(self, draw: ImageDraw.Draw):
        border_width = 8
        draw.rectangle(
            [
                (border_width // 2, border_width // 2),
                (self.width - border_width // 2, self.height - border_width // 2),
            ],
            outline="#ff0000",
            width=border_width,
        )
