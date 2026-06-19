"""Viral Thumbnail Generator — 3 Big Words, High Contrast Vertical Viewport Layering"""

import os
import random
from typing import List

from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
        """Generate high-retention viral thumbnail explicitly distributed across vertical space"""
        bg_hex = random.choice(THUMBNAIL_CONFIG.BG_COLORS)
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(bg_hex))

        # Build dynamic background ambience gradients
        img = self.add_background_effects(img)
        
        font_large = _load_font(THUMBNAIL_CONFIG.FONT_SIZE_MAIN)
        font_small = _load_font(THUMBNAIL_CONFIG.FONT_SIZE_SUB)

        # FIX: Adjusted vertical spacing points distributed uniformly across 1920 vertical bounds
        # Total heights center alignments distributed evenly across focal quadrants
        y_positions = [self.height // 4, self.height // 2, int(self.height * 0.75)]

        # Adjust text word payload length context to loop bounds safely
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append("TRUTH")

        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            color = THUMBNAIL_CONFIG.TEXT_COLORS[i % len(THUMBNAIL_CONFIG.TEXT_COLORS)]

            # Clean layer matrix transformations safely isolated from draw object
            if THUMBNAIL_CONFIG.GLOW_EFFECT:
                img = self.add_glow(img, word, y, font_large, color)

            # Draw binding assignment executed precisely prior to font layout drawing iterations
            draw = ImageDraw.Draw(img)

            if THUMBNAIL_CONFIG.DROP_SHADOW:
                self.add_text_with_shadow(draw, word, (self.width // 2, y), font_large, color)
            else:
                bbox = draw.textbbox((0, 0), word, font=font_large)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (self.width - text_width) // 2
                adjusted_y = y - (text_height // 2)
                draw.text((x, adjusted_y), word, fill=color, font=font_large)

        # Re-attach drawing instance boundary target explicitly for baseline annotations
        draw = ImageDraw.Draw(img)
        topic_text = f"#{topic.replace(' ', '')}"
        bbox = draw.textbbox((0, 0), topic_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, self.height - 120), topic_text, fill="#A3A3A3", font=font_small)

        self.add_border_frame(draw)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        # Convert explicitly to RGB format saving via JPEG payload definitions
        final_img = img.convert("RGB")
        final_img.save(output_path, "JPEG", quality=98)
        print(f"    🎨 Custom Thumbnail successfully structured -> {output_path}")
        return output_path

    def add_background_effects(self, img: Image.Image) -> Image.Image:
        """Adds cinematic vignette dark overlays for extreme contrast pop handles"""
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Symmetrical dark ambient shadows enclosing content inside from extreme edges
        for i in range(0, self.height):
            # Dynamic edge alpha scaling curves
            edge_factor = abs(i - (self.height // 2)) / (self.height // 2)
            alpha = int(220 * (edge_factor ** 2) * 0.45)
            draw.line([(0, i), (self.width, i)], fill=(0, 0, 0, alpha))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        return img.convert("RGB")

    def add_glow(self, img: Image.Image, text: str, y: int, font, color: str) -> Image.Image:
        """Applies advanced blurred backing maps to construct radioactive glow matrices"""
        r, g, b = _hex_to_rgb(color)

        glow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        # Safe bounding box processing trace outside global assignments
        bbox = glow_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        adjusted_y = y - (text_height // 2)

        # Multi-pass structural alpha dilation expansion step for high text contrast visibility
        for offset in range(32, 0, -6):
            alpha = int(75 * (1 - offset / 32))
            glow_color = (r, g, b, alpha)
            glow_draw.text((x, adjusted_y), text, fill=glow_color, font=font)

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=18))

        img = img.convert("RGBA")
        img = Image.alpha_composite(img, glow_layer)
        return img.convert("RGB")

    def add_text_with_shadow(self, draw: ImageDraw.Draw, text: str, position: tuple, font, color: str):
        """Builds an aggressive, ultra-thick black silhouette edge matrix"""
        x_center, y_center = position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        adjusted_y = y_center - (text_height // 2)

        # Ultra-deep outline shadow thickness configuration (8-directional sweep matrix)
        thickness = 10
        for dx in range(-thickness, thickness + 1, 3):
            for dy in range(-thickness, thickness + 1, 3):
                if dx*dx + dy*dy <= thickness*thickness: # Circular expansion threshold bounds
                    draw.text((x + dx, adjusted_y + dy), text, fill="black", font=font)

        # Top clear typography layer dump execution
        draw.text((x, adjusted_y), text, fill=color, font=font)

    def add_border_frame(self, draw: ImageDraw.Draw):
        """Applies a distinct framing boundary around the viewport limits"""
        border_width = 16
        draw.rectangle(
            [
                (border_width // 2, border_width // 2),
                (self.width - border_width // 2, self.height - border_width // 2),
            ],
            outline="#E11D48",  # Cyberpunk crimson red frame line
            width=border_width,
        )
