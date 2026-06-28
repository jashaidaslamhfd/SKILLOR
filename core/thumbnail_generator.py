"""
Thumbnail Generator - USA 2026 (HD FRAME-BASED)
FIXES APPLIED:
1. ✅ Resolution: 1280x720 (YouTube standard - NO CROP)
2. ✅ Frame-based thumbnails (actual video frame = higher CTR)
3. ✅ HD quality with LANCZOS resampling
4. ✅ USA-optimized colors (high contrast for feed)
5. ✅ 3 words max (clean, readable)
6. ✅ Bold text with shadow + outline
7. ✅ Platform-specific styles (YouTube/Facebook)
8. ✅ Topic-based color palettes
9. ✅ Dynamic emoji placement
10. ✅ High CTR design principles (2026)
"""

import os
import random
import math
import re
from typing import List, Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from config.settings import THUMBNAIL_CONFIG


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Load system bold fonts with fallbacks"""
    import platform
    candidates = []
    
    if platform.system() == 'Windows':
        candidates = [
            "C:/Windows/Fonts/Impact.ttf",
            "C:/Windows/Fonts/ArialBD.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
    elif platform.system() == 'Darwin':
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf"
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]
    
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


class ThumbnailGenerator:
    """HD Frame-Based Thumbnail Generator - USA 2026"""
    
    def __init__(self):
        # ═══════════════════════════════════════════════════════════
        # FIX: YouTube displays ALL thumbnails as 1280x720 LANDSCAPE
        # Even for Shorts! Portrait (1080x1920) gets CROPPED.
        # ═══════════════════════════════════════════════════════════
        self.width, self.height = 1280, 720
        
        # ============================================================
        # TOPIC-BASED COLOR PALETTES (USA 2026 - High CTR)
        # ============================================================
        self.topic_palettes = {
            'memory': {
                'bg': ['#0A0E1A', '#0D1220', '#050A1A'],
                'text': ['#FFD700', '#FFFFFF', '#4FC3F7'],
                'accent': '#FFD700',
                'emoji': '🧠',
                'style': 'mysterious',
                'mood': 'curious'
            },
            'forget': {
                'bg': ['#1A0A0A', '#120505', '#1A0D0A'],
                'text': ['#FF6B35', '#FFFFFF', '#FFB800'],
                'accent': '#FF6B35',
                'emoji': '🤔',
                'style': 'dramatic',
                'mood': 'concern'
            },
            'brain fog': {
                'bg': ['#0D0D1A', '#0A0A15', '#101020'],
                'text': ['#00D4FF', '#FFFFFF', '#E8E8E8'],
                'accent': '#00D4FF',
                'emoji': '🌫️',
                'style': 'misty',
                'mood': 'confused'
            },
            'sleep': {
                'bg': ['#0A0A1A', '#050510', '#0D0D20'],
                'text': ['#4A90D9', '#FFFFFF', '#B0C4DE'],
                'accent': '#4A90D9',
                'emoji': '😴',
                'style': 'calm',
                'mood': 'relaxed'
            },
            'stress': {
                'bg': ['#1A0505', '#1A0A0A', '#150A0A'],
                'text': ['#FF3366', '#FFFFFF', '#FF6B35'],
                'accent': '#FF3366',
                'emoji': '😰',
                'style': 'intense',
                'mood': 'urgent'
            },
            'health': {
                'bg': ['#0A1A0A', '#0D1A0D', '#081508'],
                'text': ['#00FF88', '#FFFFFF', '#4FC3F7'],
                'accent': '#00FF88',
                'emoji': '❤️',
                'style': 'clean',
                'mood': 'positive'
            },
            'science': {
                'bg': ['#050A1A', '#0A0F1E', '#080D18'],
                'text': ['#4FC3F7', '#FFFFFF', '#FFD700'],
                'accent': '#4FC3F7',
                'emoji': '🔬',
                'style': 'scientific',
                'mood': 'curious'
            },
            'default': {
                'bg': ['#0A0E1A', '#0D1220', '#080D18'],
                'text': ['#FFD700', '#FFFFFF', '#FF6B35'],
                'accent': '#FFD700',
                'emoji': '✨',
                'style': 'premium',
                'mood': 'curious'
            }
        }
        
        # ============================================================
        # PLATFORM-SPECIFIC STYLES
        # ============================================================
        self.platform_styles = {
            'youtube': {
                'text_size': 160,
                'shadow_depth': 14,
                'outline_width': 10,
                'contrast': 1.30,  # ═══ HIGHER FOR FEED VISIBILITY ═══
                'border_style': 'bold',
                'cta_style': 'click_now'
            },
            'facebook': {
                'text_size': 130,
                'shadow_depth': 10,
                'outline_width': 8,
                'contrast': 1.10,
                'border_style': 'soft',
                'cta_style': 'story_driven'
            }
        }
        
        self.font_size_emoji = 90
        self.font_size_banner = 50
        
        # ============================================================
        # EMOTION EFFECTS
        # ============================================================
        self.emotion_effects = {
            'curious': {'glow': '#FFD700', 'intensity': 0.7, 'pulse': True, 'overlay': 'warm'},
            'concern': {'glow': '#FF6B35', 'intensity': 0.8, 'pulse': True, 'overlay': 'warm'},
            'confused': {'glow': '#00D4FF', 'intensity': 0.5, 'pulse': False, 'overlay': 'cool'},
            'relaxed': {'glow': '#4A90D9', 'intensity': 0.3, 'pulse': False, 'overlay': 'cool'},
            'urgent': {'glow': '#FF3366', 'intensity': 0.9, 'pulse': True, 'overlay': 'warm'},
            'positive': {'glow': '#00FF88', 'intensity': 0.6, 'pulse': True, 'overlay': 'neutral'},
            'surprised': {'glow': '#FFFFFF', 'intensity': 0.85, 'pulse': True, 'overlay': 'neutral'},
            'default': {'glow': '#FFD700', 'intensity': 0.5, 'pulse': False, 'overlay': 'neutral'}
        }
        
        print(f"🖼️ ThumbnailGenerator initialized ({self.width}x{self.height})")

    # ============================================================
    # ANALYZE CONTENT
    # ============================================================
    def _analyze_content(self, topic: str, script: str = "") -> Dict:
        """Analyze content to determine visual style"""
        topic_lower = topic.lower()
        script_lower = script.lower()
        
        detected_topic = 'default'
        topic_keywords = {
            'memory': ['memory', 'remember', 'recall', 'reminisce'],
            'forget': ['forget', 'forgetting', 'forgot', 'blank'],
            'brain fog': ['brain fog', 'fog', 'foggy', 'cloudy', 'mental'],
            'focus': ['focus', 'concentrate', 'attention', 'distracted'],
            'sleep': ['sleep', 'dream', 'night', 'insomnia'],
            'tired': ['tired', 'exhausted', 'fatigue', 'drained'],
            'stress': ['stress', 'pressure', 'overwhelmed', 'burnout'],
            'anxiety': ['anxiety', 'worry', 'nervous', 'panic'],
            'health': ['health', 'wellness', 'fit', 'healthy'],
            'body': ['body', 'muscle', 'physical', 'strength'],
            'science': ['science', 'research', 'study', 'discovery'],
            'brain': ['brain', 'neuron', 'cognitive', 'mind'],
        }
        
        for key, keywords in topic_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                detected_topic = key
                break
        
        if script:
            for key, keywords in topic_keywords.items():
                if any(kw in script_lower for kw in keywords):
                    detected_topic = key
                    break
        
        return {
            'topic': detected_topic,
            'palette': self.topic_palettes.get(detected_topic, self.topic_palettes['default']),
            'mood': self.topic_palettes.get(detected_topic, {}).get('mood', 'curious'),
            'style': self.topic_palettes.get(detected_topic, {}).get('style', 'premium'),
            'emoji': self.topic_palettes.get(detected_topic, {}).get('emoji', '✨'),
        }

    # ============================================================
    # GET PLATFORM STYLE
    # ============================================================
    def _get_platform_style(self, platform: str = "youtube") -> Dict:
        if platform in self.platform_styles:
            return self.platform_styles[platform]
        return self.platform_styles['youtube']

    # ============================================================
    # CREATE BACKGROUND
    # ============================================================
    def _create_platform_background(self, color: str, style: str, mood: str, platform: str) -> Image.Image:
        """Create platform-specific background"""
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(color))
        
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        if platform == "youtube":
            for y in range(self.height):
                alpha = int(180 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        else:
            for y in range(self.height):
                alpha = int(120 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 20, 40, alpha))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        return img.convert("RGB")

    # ============================================================
    # ADD PLATFORM EFFECTS
    # ============================================================
    def _add_platform_effects(self, img: Image.Image, mood: str, platform: str) -> Image.Image:
        effect = self.emotion_effects.get(mood, self.emotion_effects['curious'])
        glow_color = _hex_to_rgb(effect['glow'])
        intensity = effect['intensity'] * (1.3 if platform == "youtube" else 0.8)
        
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        center_x, center_y = self.width // 2, self.height // 2 - 100
        
        for r in range(400, 100, -30):
            alpha = int(20 * intensity * (1 - r / 400))
            draw.ellipse(
                [center_x - r, center_y - r, center_x + r, center_y + r],
                outline=(glow_color[0], glow_color[1], glow_color[2], alpha),
                width=2
            )
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # ADD SHADOW
    # ============================================================
    def _add_platform_shadow(self, img: Image.Image, text: str, y: int,
                            font, color: str, mood: str, platform: str) -> Image.Image:
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        shadow_depth = 14 if platform == "youtube" else 10
        
        for offset in range(shadow_depth, 0, -2):
            alpha = int(60 * (1 - offset / shadow_depth))
            txt_draw.text(
                (x + offset, y_pos + offset),
                text,
                fill=(0, 0, 0, alpha),
                font=font
            )
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    # ============================================================
    # ADD TEXT WITH OUTLINE
    # ============================================================
    def _add_platform_text(self, img: Image.Image, text: str, y: int,
                          font, color: str, mood: str, platform: str) -> Image.Image:
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        outline_width = 10 if platform == "youtube" else 8
        
        # Outline
        for dx in range(-outline_width, outline_width + 1, 2):
            for dy in range(-outline_width, outline_width + 1, 2):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    txt_draw.text(
                        (x + dx, y_pos + dy),
                        text,
                        fill=(0, 0, 0, 200),
                        font=font
                    )
        
        # Main text
        txt_draw.text((x, y_pos), text, fill=color, font=font)
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    # ============================================================
    # ENHANCE IMAGE
    # ============================================================
    def _enhance_platform_image(self, img: Image.Image, mood: str, platform: str) -> Image.Image:
        """Enhance image for platform - HIGH CONTRAST for YouTube feed"""
        contrast_factor = 1.30 if platform == "youtube" else 1.10
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        
        sharpness_factor = 1.30 if platform == "youtube" else 1.10
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness_factor)
        
        color_factor = 1.20 if platform == "youtube" else 1.05
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(color_factor)
        
        return img

    # ============================================================
    # LANDSCAPE LAYOUT (1280x720)
    # ============================================================
    def _get_landscape_layout(self, words: List[str], platform: str) -> List[int]:
        """Get layout positions for landscape thumbnail (1280x720)"""
        n = len(words)
        if n == 2:
            return [
                self.height * 2 // 3 - 30,
                self.height * 2 // 3 + 90,
            ]
        else:  # 3 words
            return [
                self.height // 2 - 60,
                self.height // 2 + 60,
                self.height // 2 + 180,
            ]

    # ============================================================
    # DRAW LANDSCAPE EMOJI
    # ============================================================
    def _draw_landscape_emoji(self, img: Image.Image, emoji: str, y: int,
                               font, index: int, mood: str, platform: str) -> Image.Image:
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if index == 0:
            x = self.width - text_width - 60
        elif index == 1:
            x = 50
        else:
            x = self.width - text_width - 60
        
        adjusted_y = y - (text_height // 2)
        
        # Shadow
        for offset in range(4, 0, -1):
            draw.text(
                (x + offset, adjusted_y + offset),
                emoji,
                fill=(0, 0, 0, 150),
                font=font
            )
        draw.text((x, adjusted_y), emoji, font=font)
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # ADD LANDSCAPE BANNER
    # ============================================================
    def _add_landscape_banner(self, draw: ImageDraw.Draw, topic: str,
                               font, palette: Dict, platform: str) -> None:
        if platform == "youtube":
            topic_text = f"⚡ {topic[:25].upper()} ⚡"
        else:
            topic_text = f"📖 {topic[:25].upper()}"
        
        bbox = draw.textbbox((0, 0), topic_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        banner_y = 40
        padding = 18
        accent_color = palette.get('accent', '#FFD700')
        
        draw.rounded_rectangle(
            [
                (self.width // 2 - text_width // 2 - padding, banner_y - padding + 5),
                (self.width // 2 + text_width // 2 + padding, banner_y + text_height + padding + 5)
            ],
            radius=15,
            fill=_hex_to_rgba(accent_color, 200),
            outline=_hex_to_rgba("#FFFFFF", 150),
            width=2
        )
        
        x = (self.width - text_width) // 2
        draw.text((x, banner_y + 5), topic_text, fill="#FFFFFF", font=font)

    # ============================================================
    # ADD LANDSCAPE CTA
    # ============================================================
    def _add_landscape_cta(self, draw: ImageDraw.Draw, mood: str, platform: str) -> None:
        center_x = self.width // 2
        bottom_y = self.height - 70
        
        if platform == "youtube":
            glow_color = self.emotion_effects.get(mood, {}).get('glow', '#FFD700')
            for r in range(40, 25, -4):
                alpha = int(25 * (1 - r / 40))
                draw.ellipse(
                    [center_x - r, bottom_y - r, center_x + r, bottom_y + r],
                    outline=_hex_to_rgba(glow_color, alpha),
                    width=1
                )
            draw.ellipse(
                [center_x - 28, bottom_y - 28, center_x + 28, bottom_y + 28],
                fill=_hex_to_rgba(glow_color, 150),
                outline=(255, 255, 255, 200),
                width=3
            )
            points = [
                (center_x - 10, bottom_y - 14),
                (center_x + 12, bottom_y),
                (center_x - 10, bottom_y + 14)
            ]
            draw.polygon(points, fill=(255, 255, 255, 220))
        else:
            font = _load_font(24, bold=True)
            watch_text = "▶ WATCH"
            bbox = draw.textbbox((0, 0), watch_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            y = bottom_y - 15
            draw.rounded_rectangle(
                [x - 20, y - 10, x + text_width + 20, y + text_height + 10],
                radius=20,
                fill=(0, 0, 0, 180),
                outline=(255, 255, 255, 100),
                width=1
            )
            draw.text((x, y), watch_text, fill="#FFFFFF", font=font)

    # ============================================================
    # GENERATE THUMBNAIL FROM FRAME (PRIMARY METHOD - 2026)
    # ============================================================
    def generate_thumbnail_from_frame(
        self, 
        frame_path: str, 
        words: List[str],
        topic: str, 
        output_path: str,
        platform: str = "youtube",
        script: str = "", 
        hook: str = ""
    ) -> str:
        """
        Generate thumbnail from HD frame - PRIMARY 2026 METHOD.
        
        YouTube's algorithm gives higher CTR to thumbnails that match
        the actual video content. Frame-based thumbnails get 30%+ higher CTR.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Analyze content
        analysis = self._analyze_content(topic, script)
        palette = analysis['palette']
        mood = analysis['mood']
        
        print(f"    🎯 Frame-based thumbnail | Platform: {platform.upper()}")
        
        # Load and resize frame
        try:
            img = Image.open(frame_path).convert("RGB")
            img = img.resize((self.width, self.height), Image.LANCZOS)
            print(f"    ✅ Loaded frame → {self.width}x{self.height}")
        except Exception as e:
            print(f"    ⚠️ Frame load failed: {e}, using generated background")
            bg_hex = random.choice(palette['bg'])
            img = self._create_platform_background(bg_hex, analysis['style'], mood, platform)
        
        # ── Darken frame for text readability ──
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Bottom gradient (where text goes)
        for y in range(self.height):
            if y > self.height * 0.35:
                alpha = int(120 * ((y - self.height * 0.35) / (self.height * 0.65)))
                overlay_draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        
        # Top gradient (for banner)
        for y in range(int(self.height * 0.15)):
            alpha = int(80 * (1 - y / (self.height * 0.15)))
            overlay_draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        
        # ── Add mood glow ──
        effect = self.emotion_effects.get(mood, self.emotion_effects['curious'])
        glow_color = _hex_to_rgb(effect['glow'])
        glow_overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_overlay)
        cx, cy = self.width // 2, self.height // 2
        for r in range(350, 50, -25):
            alpha = int(15 * effect['intensity'] * (1 - r / 350))
            glow_draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                outline=(glow_color[0], glow_color[1], glow_color[2], alpha),
                width=2
            )
        img = Image.alpha_composite(img, glow_overlay)
        img = img.convert("RGB")
        
        # ── Add text overlays ──
        words_chunk = words[:3]
        while len(words_chunk) < 2:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "WHY", "BRAIN", "BODY"]))
        
        style_settings = self._get_platform_style(platform)
        font_size = style_settings['text_size']
        font_main = _load_font(font_size, bold=True)
        font_emoji = _load_font(self.font_size_emoji, bold=False)
        font_banner = _load_font(self.font_size_banner, bold=True)
        
        y_positions = self._get_landscape_layout(words_chunk, platform)
        
        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            if i == 0:
                color = palette['text'][0]
            elif i == 1:
                color = '#FFFFFF'
            else:
                color = palette['text'][2] if len(palette['text']) > 2 else '#FFFFFF'
            
            # Shadow
            img = self._add_platform_shadow(img, word, y, font_main, color, mood, platform)
            # Text with outline
            img = self._add_platform_text(img, word, y, font_main, color, mood, platform)
            
            # Emoji
            main_emoji = analysis['emoji']
            emoji = self._get_platform_emoji(word, topic, main_emoji, platform)
            if emoji:
                img = self._draw_landscape_emoji(img, emoji, y, font_emoji, i, mood, platform)
        
        # ── Banner ──
        draw = ImageDraw.Draw(img)
        self._add_landscape_banner(draw, topic, font_banner, palette, platform)
        
        # ── Border ──
        self._add_platform_border(draw, platform, palette)
        
        # ── CTA ──
        self._add_landscape_cta(draw, mood, platform)
        
        # ── Final enhancement ──
        img = self._enhance_platform_image(img, mood, platform)
        
        # ── Save ──
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=98, optimize=True, subsampling=0)
        
        print(f"    🎨 Thumbnail: {output_path}")
        print(f"    📝 Words: {words_chunk} | Resolution: {self.width}x{self.height}")
        
        return output_path

    # ============================================================
    # GET PLATFORM EMOJI
    # ============================================================
    def _get_platform_emoji(self, word: str, topic: str, default_emoji: str, platform: str) -> str:
        word_lower = word.lower()
        
        word_emojis = {
            'memory': '🧠', 'brain': '🧠', 'mind': '🧠',
            'forget': '🤔', 'forgot': '🤔',
            'fog': '🌫️', 'foggy': '🌫️',
            'focus': '🎯', 'concentrate': '🎯',
            'sleep': '😴', 'night': '🌙',
            'tired': '😩', 'exhausted': '😩',
            'stress': '😰', 'pressure': '😰',
            'anxiety': '😨', 'worry': '😨',
            'health': '❤️', 'body': '💪',
            'science': '🔬',
            'truth': '⚡', 'power': '⚡',
            'secret': '🔑', 'hidden': '🔑',
        }
        
        for key, emoji in word_emojis.items():
            if key in word_lower:
                return emoji
        
        if platform == "facebook":
            facebook_emojis = {
                'memory': '🧠', 'brain': '🧠',
                'forget': '🤔', 'stress': '😰',
                'sleep': '😴', 'health': '❤️',
            }
            for key, emoji in facebook_emojis.items():
                if key in word_lower or key in topic.lower():
                    return emoji
        
        return default_emoji

    # ============================================================
    # ADD PLATFORM BORDER
    # ============================================================
    def _add_platform_border(self, draw: ImageDraw.Draw, platform: str, palette: Dict) -> None:
        accent_color = palette.get('accent', '#FFD700')
        border_width = 12 if platform == "youtube" else 8
        padding = 15
        
        draw.rectangle(
            [
                (padding, padding),
                (self.width - padding, self.height - padding)
            ],
            outline=accent_color,
            width=border_width
        )
        
        inner_padding = padding + border_width + 4
        draw.rectangle(
            [
                (inner_padding, inner_padding),
                (self.width - inner_padding, self.height - inner_padding)
            ],
            outline="#FFFFFF",
            width=2 if platform == "youtube" else 1
        )

    # ============================================================
    # CONVENIENCE METHODS
    # ============================================================
    def generate_youtube_thumbnail_from_frame(
        self, frame_path: str, words: List[str],
        topic: str, output_path: str,
        script: str = "", hook: str = ""
    ) -> str:
        return self.generate_thumbnail_from_frame(
            frame_path, words, topic, output_path, "youtube", script, hook
        )

    def generate_facebook_thumbnail_from_frame(
        self, frame_path: str, words: List[str],
        topic: str, output_path: str,
        script: str = "", hook: str = ""
    ) -> str:
        return self.generate_thumbnail_from_frame(
            frame_path, words, topic, output_path, "facebook", script, hook
        )

    # ============================================================
    # LEGACY FALLBACK (PIL-only, if frame extraction fails)
    # ============================================================
    def generate_thumbnail(
        self, words: List[str], topic: str, 
        output_path: str, platform: str = "youtube",
        script: str = "", hook: str = ""
    ) -> str:
        """Legacy fallback - PIL-only thumbnail (if frame extraction fails)"""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        analysis = self._analyze_content(topic, script)
        palette = analysis['palette']
        mood = analysis['mood']
        
        bg_hex = random.choice(palette['bg'])
        img = self._create_platform_background(bg_hex, analysis['style'], mood, platform)
        img = self._add_platform_effects(img, mood, platform)
        
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "POWER", "BRAIN", "FOCUS"]))
        
        style_settings = self._get_platform_style(platform)
        font_size = style_settings['text_size']
        font_main = _load_font(font_size, bold=True)
        font_emoji = _load_font(self.font_size_emoji, bold=False)
        font_banner = _load_font(self.font_size_banner, bold=True)
        
        y_positions = self._get_landscape_layout(words_chunk, platform)
        
        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            if i == 0:
                color = palette['text'][0]
            elif i == 1:
                color = palette['text'][1]
            else:
                color = palette['text'][2] if len(palette['text']) > 2 else palette['text'][0]
            
            img = self._add_platform_shadow(img, word, y, font_main, color, mood, platform)
            img = self._add_platform_text(img, word, y, font_main, color, mood, platform)
            
            emoji = self._get_platform_emoji(word, topic, analysis['emoji'], platform)
            if emoji:
                img = self._draw_landscape_emoji(img, emoji, y, font_emoji, i, mood, platform)
        
        draw = ImageDraw.Draw(img)
        self._add_landscape_banner(draw, topic, font_banner, palette, platform)
        self._add_platform_border(draw, platform, palette)
        self._add_landscape_cta(draw, mood, platform)
        
        img = self._enhance
