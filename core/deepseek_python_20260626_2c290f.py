"""
Thumbnail Generator - PLATFORM-SPECIFIC EDITION
Generates thumbnails DYNAMICALLY based on platform and video content

FEATURES:
1. YouTube Thumbnail: Bold, high-CTR, 3 words + emoji
2. Facebook Thumbnail: Story-driven, engagement-focused, softer colors
3. Dynamic background based on topic
4. AI-suggested color palettes per topic
5. Platform-specific styling
6. Topic-specific emojis and icons
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
    import platform
    candidates = []
    
    if platform.system() == 'Windows':
        candidates = ["C:/Windows/Fonts/Impact.ttf", "C:/Windows/Fonts/ArialBD.ttf", "C:/Windows/Fonts/arial.ttf"]
    elif platform.system() == 'Darwin':
        candidates = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"]
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
    """Platform-Specific Thumbnail Generator"""
    
    def __init__(self):
        self.width, self.height = getattr(THUMBNAIL_CONFIG, 'RESOLUTION', (1080, 1920))
        
        # ============================================================
        # TOPIC-BASED COLOR PALETTES
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
                'contrast': 1.15,
                'border_style': 'bold',
                'cta_style': 'click_now'
            },
            'facebook': {
                'text_size': 130,
                'shadow_depth': 10,
                'outline_width': 8,
                'contrast': 1.05,
                'border_style': 'soft',
                'cta_style': 'story_driven'
            }
        }
        
        self.font_size_emoji = 90
        self.font_size_banner = 50
        
        print(f"🖼️ Platform-Specific ThumbnailGenerator initialized")

    # ============================================================
    # PLATFORM-SPECIFIC ANALYZE
    # ============================================================
    
    def _get_platform_style(self, platform: str = "youtube") -> Dict:
        """Get platform-specific style settings"""
        if platform in self.platform_styles:
            return self.platform_styles[platform]
        return self.platform_styles['youtube']

    # ============================================================
    # MAIN GENERATE - PLATFORM SPECIFIC
    # ============================================================
    
    def generate_thumbnail(self, words: List[str], topic: str, output_path: str,
                           platform: str = "youtube", script: str = "", hook: str = "") -> str:
        """
        Generate platform-specific thumbnail
        
        Args:
            words: 3 words for thumbnail
            topic: Video topic
            output_path: Save path
            platform: "youtube" or "facebook"
            script: Full script (for context)
            hook: Hook text (for additional context)
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Get platform style
        style_settings = self._get_platform_style(platform)
        
        # Analyze content
        analysis = self._analyze_content(topic, script)
        palette = analysis['palette']
        mood = analysis['mood']
        style = analysis['style']
        main_emoji = analysis['emoji']
        
        print(f"    🎯 Platform: {platform.upper()} | Topic: {analysis['topic']} | Mood: {mood}")
        
        # Create background
        bg_hex = random.choice(palette['bg'])
        img = self._create_platform_background(bg_hex, style, mood, platform)
        
        # Add platform-specific effects
        img = self._add_platform_effects(img, mood, platform)
        
        # Prepare words
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "POWER", "BRAIN", "FOCUS"]))
        
        # Platform-specific font size
        font_size = style_settings['text_size']
        font_main = _load_font(font_size, bold=True)
        font_emoji = _load_font(self.font_size_emoji, bold=False)
        font_banner = _load_font(self.font_size_banner, bold=True)
        
        # Layout
        y_positions = self._get_platform_layout(words_chunk, platform)
        
        # Draw words with platform-specific styling
        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            if i == 0:
                color = palette['text'][0]
            elif i == 1:
                color = palette['text'][1]
            else:
                color = palette['text'][2] if len(palette['text']) > 2 else palette['text'][0]
            
            img = self._add_platform_shadow(img, word, y, font_main, color, mood, platform)
            img = self._add_platform_text(img, word, y, font_main, color, mood, platform)
            
            if i == 0:
                img = self._add_highlight_effect(img, word, y, font_main)
            
            emoji = self._get_platform_emoji(word, topic, main_emoji, platform)
            if emoji:
                img = self._draw_platform_emoji(img, emoji, y, font_emoji, i, mood, platform)
        
        # Platform-specific banner
        draw = ImageDraw.Draw(img)
        self._add_platform_banner(draw, topic, font_banner, palette, platform)
        
        # Platform-specific border
        self._add_platform_border(draw, platform, palette)
        
        # Platform-specific CTA
        self._add_platform_cta(draw, mood, platform)
        
        # Final enhancement
        img = self._enhance_platform_image(img, mood, platform)
        
        # Save
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95, optimize=True)
        
        print(f"    🎨 {platform.upper()} Thumbnail: {output_path}")
        print(f"    📝 Words: {words_chunk} | Mood: {mood}")
        
        return output_path

    # ============================================================
    # PLATFORM-SPECIFIC BACKGROUND
    # ============================================================
    
    def _create_platform_background(self, color: str, style: str, mood: str, platform: str) -> Image.Image:
        """Create platform-specific background"""
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(color))
        
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        if platform == "youtube":
            # Bold gradient for YouTube
            for y in range(self.height):
                alpha = int(180 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        else:
            # Softer gradient for Facebook
            for y in range(self.height):
                alpha = int(120 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 20, 40, alpha))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        return img.convert("RGB")

    # ============================================================
    # PLATFORM-SPECIFIC EFFECTS
    # ============================================================
    
    def _add_platform_effects(self, img: Image.Image, mood: str, platform: str) -> Image.Image:
        """Add platform-specific effects"""
        effect = self.emotion_effects.get(mood, self.emotion_effects['curious'])
        glow_color = _hex_to_rgb(effect['glow'])
        intensity = effect['intensity'] * (1.2 if platform == "youtube" else 0.8)
        
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
    # PLATFORM-SPECIFIC LAYOUT
    # ============================================================
    
    def _get_platform_layout(self, words: List[str], platform: str) -> List[int]:
        """Get platform-specific layout"""
        if platform == "youtube":
            return [
                self.height // 5,
                self.height // 2,
                int(self.height * 0.73)
            ]
        else:
            # Facebook - slightly different for story feel
            return [
                self.height // 5 + 20,
                self.height // 2 - 20,
                int(self.height * 0.75) - 10
            ]

    # ============================================================
    # PLATFORM-SPECIFIC SHADOW
    # ============================================================
    
    def _add_platform_shadow(self, img: Image.Image, text: str, y: int,
                            font, color: str, mood: str, platform: str) -> Image.Image:
        """Add platform-specific shadow"""
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
    # PLATFORM-SPECIFIC TEXT
    # ============================================================
    
    def _add_platform_text(self, img: Image.Image, text: str, y: int,
                          font, color: str, mood: str, platform: str) -> Image.Image:
        """Add platform-specific text with outline"""
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        outline_width = 10 if platform == "youtube" else 8
        
        for dx in range(-outline_width, outline_width + 1, 2):
            for dy in range(-outline_width, outline_width + 1, 2):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    txt_draw.text(
                        (x + dx, y_pos + dy),
                        text,
                        fill=(0, 0, 0, 200),
                        font=font
                    )
        
        txt_draw.text((x, y_pos), text, fill=color, font=font)
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    # ============================================================
    # PLATFORM-SPECIFIC EMOJI
    # ============================================================
    
    def _get_platform_emoji(self, word: str, topic: str, default_emoji: str, platform: str) -> str:
        """Get platform-specific emoji"""
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
            'science': '🔬', 'brain': '🧠',
            'truth': '⚡', 'power': '⚡',
            'secret': '🔑', 'hidden': '🔑',
        }
        
        for key, emoji in word_emojis.items():
            if key in word_lower:
                return emoji
        
        # Facebook specific emojis
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

    def _draw_platform_emoji(self, img: Image.Image, emoji: str, y: int,
                            font, index: int, mood: str, platform: str) -> Image.Image:
        """Draw platform-specific emoji"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if index == 0:
            x = int(self.width * 0.72)
        elif index == 1:
            x = int(self.width * 0.28)
        else:
            x = int(self.width * 0.72)
        
        adjusted_y = y - (text_height // 2) + random.randint(-15, 15)
        
        # Platform-specific emoji size
        size_multiplier = 1.2 if platform == "youtube" else 1.0
        
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
    # PLATFORM-SPECIFIC BANNER
    # ============================================================
    
    def _add_platform_banner(self, draw: ImageDraw.Draw, topic: str,
                            font, palette: Dict, platform: str) -> None:
        """Add platform-specific banner"""
        if platform == "youtube":
            topic_text = f"⚡ {topic[:20].upper()} ⚡"
        else:
            topic_text = f"📖 {topic[:20].upper()}"
        
        bbox = draw.textbbox((0, 0), topic_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        banner_y = 70
        padding = 25
        accent_color = palette.get('accent', '#FF6B35')
        
        draw.rounded_rectangle(
            [
                (self.width // 2 - text_width // 2 - padding, banner_y - padding),
                (self.width // 2 + text_width // 2 + padding, banner_y + text_height + padding)
            ],
            radius=20,
            fill=_hex_to_rgba(accent_color, 200),
            outline=_hex_to_rgba("#FFFFFF", 150),
            width=2
        )
        
        x = (self.width - text_width) // 2
        draw.text((x, banner_y), topic_text, fill="#FFFFFF", font=font)

    # ============================================================
    # PLATFORM-SPECIFIC BORDER
    # ============================================================
    
    def _add_platform_border(self, draw: ImageDraw.Draw, platform: str, palette: Dict) -> None:
        """Add platform-specific border"""
        accent_color = palette.get('accent', '#FFD700')
        border_width = 12 if platform == "youtube" else 8
        padding = 15
        
        # Outer border
        draw.rectangle(
            [
                (padding, padding),
                (self.width - padding, self.height - padding)
            ],
            outline=accent_color,
            width=border_width
        )
        
        # Inner accent border
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
    # PLATFORM-SPECIFIC CTA
    # ============================================================
    
    def _add_platform_cta(self, draw: ImageDraw.Draw, mood: str, platform: str) -> None:
        """Add platform-specific call to action"""
        center_x = self.width // 2
        bottom_y = self.height - 150
        
        if platform == "youtube":
            # Bold play button for YouTube
            glow_color = self.emotion_effects.get(mood, {}).get('glow', '#FFD700')
            
            for r in range(60, 40, -5):
                alpha = int(30 * (1 - r / 60))
                draw.ellipse(
                    [center_x - r, bottom_y - r, center_x + r, bottom_y + r],
                    outline=_hex_to_rgba(glow_color, alpha),
                    width=1
                )
            
            draw.ellipse(
                [center_x - 40, bottom_y - 40, center_x + 40, bottom_y + 40],
                fill=_hex_to_rgba(glow_color, 150),
                outline=(255, 255, 255, 200),
                width=3
            )
            
            points = [
                (center_x - 15, bottom_y - 18),
                (center_x + 15, bottom_y),
                (center_x - 15, bottom_y + 18)
            ]
            draw.polygon(points, fill=(255, 255, 255, 220))
        
        else:
            # Facebook - soft "Watch" text
            font = _load_font(30, bold=True)
            watch_text = "▶ WATCH"
            bbox = draw.textbbox((0, 0), watch_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            y = bottom_y - 20
            
            # Background pill
            draw.rounded_rectangle(
                [x - 30, y - 15, x + text_width + 30, y + text_height + 15],
                radius=30,
                fill=(0, 0, 0, 180),
                outline=(255, 255, 255, 100),
                width=1
            )
            draw.text((x, y), watch_text, fill="#FFFFFF", font=font)

    # ============================================================
    # PLATFORM-SPECIFIC ENHANCE
    # ============================================================
    
    def _enhance_platform_image(self, img: Image.Image, mood: str, platform: str) -> Image.Image:
        """Enhance image based on platform"""
        contrast_factor = 1.15 if platform == "youtube" else 1.05
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        
        sharpness_factor = 1.15 if platform == "youtube" else 1.05
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness_factor)
        
        return img

    # ============================================================
    # HELPER METHODS (Same as before)
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
    
    def _add_highlight_effect(self, img: Image.Image, text: str, y: int,
                                font) -> Image.Image:
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        txt_draw.text(
            (x - 2, y_pos - 2),
            text,
            fill=(255, 255, 255, 80),
            font=font
        )
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")
    
    # ============================================================
    # CONVENIENCE METHODS
    # ============================================================
    
    def generate_youtube_thumbnail(self, words: List[str], topic: str, output_path: str,
                                   script: str = "", hook: str = "") -> str:
        """Generate YouTube thumbnail (bold, high-CTR)"""
        return self.generate_thumbnail(words, topic, output_path, "youtube", script, hook)
    
    def generate_facebook_thumbnail(self, words: List[str], topic: str, output_path: str,
                                   script: str = "", hook: str = "") -> str:
        """Generate Facebook thumbnail (story-driven, engagement)"""
        return self.generate_thumbnail(words, topic, output_path, "facebook", script, hook)


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING PLATFORM-SPECIFIC THUMBNAIL GENERATOR\n" + "="*60)
    
    generator = ThumbnailGenerator()
    
    test_words = ["MEMORY", "BRAIN", "FOG"]
    test_topic = "forgetting names"
    
    # YouTube Thumbnail
    yt_path = "test_thumbnail_youtube.jpg"
    generator.generate_youtube_thumbnail(test_words, test_topic, yt_path)
    print(f"✅ YouTube Thumbnail: {yt_path}")
    
    # Facebook Thumbnail
    fb_path = "test_thumbnail_facebook.jpg"
    generator.generate_facebook_thumbnail(test_words, test_topic, fb_path)
    print(f"✅ Facebook Thumbnail: {fb_path}")
    
    print(f"\n✅ Both thumbnails generated!")