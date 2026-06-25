"""
Thumbnail Generator - AI-POWERED EDITION
Generates thumbnails DYNAMICALLY based on video content

FEATURES:
1. Dynamic background based on topic (Memory, Stress, Sleep, etc.)
2. AI-suggested color palettes per topic
3. Text styling based on emotional tone
4. Layout adaptation based on content type
5. Professional effects matching video mood
6. Topic-specific emojis and icons
7. Dynamic font sizes based on word length
8. Emotion-based color grading
"""

import os
import random
import math
import re
from typing import List, Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from config.settings import THUMBNAIL_CONFIG


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert '#rrggbb' to (r, g, b)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert '#rrggbb' to (r, g, b, a)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Load system bold fonts with fallback"""
    import platform
    
    candidates = []
    
    if platform.system() == 'Windows':
        candidates = [
            "C:/Windows/Fonts/Impact.ttf",
            "C:/Windows/Fonts/ArialBD.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    elif platform.system() == 'Darwin':
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    
    try:
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()


class ThumbnailGenerator:
    """AI-Powered Thumbnail Generator - Dynamic Content-Based"""
    
    def __init__(self):
        self.width, self.height = getattr(THUMBNAIL_CONFIG, 'RESOLUTION', (1080, 1920))
        
        # ============================================================
        # TOPIC-BASED COLOR PALETTES
        # ============================================================
        self.topic_palettes = {
            # Memory Topics
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
            'focus': {
                'bg': ['#0A1A0A', '#0D1A0D', '#050F05'],
                'text': ['#39FF14', '#FFFFFF', '#00FF88'],
                'accent': '#39FF14',
                'emoji': '🎯',
                'style': 'sharp',
                'mood': 'determined'
            },
            
            # Sleep Topics
            'sleep': {
                'bg': ['#0A0A1A', '#050510', '#0D0D20'],
                'text': ['#4A90D9', '#FFFFFF', '#B0C4DE'],
                'accent': '#4A90D9',
                'emoji': '😴',
                'style': 'calm',
                'mood': 'relaxed'
            },
            'tired': {
                'bg': ['#1A0A0A', '#1A0A05', '#1A0D0A'],
                'text': ['#FF6B35', '#FFFFFF', '#FFB800'],
                'accent': '#FF6B35',
                'emoji': '😩',
                'style': 'heavy',
                'mood': 'exhausted'
            },
            
            # Stress Topics
            'stress': {
                'bg': ['#1A0505', '#1A0A0A', '#150A0A'],
                'text': ['#FF3366', '#FFFFFF', '#FF6B35'],
                'accent': '#FF3366',
                'emoji': '😰',
                'style': 'intense',
                'mood': 'urgent'
            },
            'anxiety': {
                'bg': ['#1A0A1A', '#150A15', '#1A0D1A'],
                'text': ['#FF6B6B', '#FFFFFF', '#FFB8B8'],
                'accent': '#FF6B6B',
                'emoji': '😨',
                'style': 'tense',
                'mood': 'worried'
            },
            
            # Health/Wellness
            'health': {
                'bg': ['#0A1A0A', '#0D1A0D', '#081508'],
                'text': ['#00FF88', '#FFFFFF', '#4FC3F7'],
                'accent': '#00FF88',
                'emoji': '❤️',
                'style': 'clean',
                'mood': 'positive'
            },
            'body': {
                'bg': ['#0A0D1A', '#0A0F20', '#0D1220'],
                'text': ['#FF6B35', '#FFFFFF', '#FFD700'],
                'accent': '#FF6B35',
                'emoji': '💪',
                'style': 'energetic',
                'mood': 'empowered'
            },
            
            # Science/Education
            'science': {
                'bg': ['#050A1A', '#0A0F1E', '#080D18'],
                'text': ['#4FC3F7', '#FFFFFF', '#FFD700'],
                'accent': '#4FC3F7',
                'emoji': '🔬',
                'style': 'scientific',
                'mood': 'curious'
            },
            'brain': {
                'bg': ['#0A0A1A', '#0D0D20', '#050510'],
                'text': ['#FFD700', '#FFFFFF', '#4FC3F7'],
                'accent': '#FFD700',
                'emoji': '🧠',
                'style': 'premium',
                'mood': 'fascinated'
            },
            
            # Default
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
        # EMOTIONAL EFFECTS
        # ============================================================
        self.emotion_effects = {
            'curious': {'glow': '#4FC3F7', 'intensity': 0.3},
            'concern': {'glow': '#FF6B35', 'intensity': 0.4},
            'dramatic': {'glow': '#FF3366', 'intensity': 0.5},
            'calm': {'glow': '#4A90D9', 'intensity': 0.2},
            'urgent': {'glow': '#FF0000', 'intensity': 0.6},
            'positive': {'glow': '#00FF88', 'intensity': 0.3},
            'empowered': {'glow': '#FF6B35', 'intensity': 0.4},
            'fascinated': {'glow': '#FFD700', 'intensity': 0.3},
            'determined': {'glow': '#39FF14', 'intensity': 0.4},
            'relaxed': {'glow': '#4A90D9', 'intensity': 0.2},
            'worried': {'glow': '#FF6B6B', 'intensity': 0.5},
            'confused': {'glow': '#00D4FF', 'intensity': 0.3},
        }
        
        self.font_size_main = 160
        self.font_size_sub = 60
        self.font_size_emoji = 90
        self.font_size_banner = 50
        
        print(f"🖼️ AI-Powered ThumbnailGenerator initialized")

    # ============================================================
    # ANALYZE CONTENT - Detect Topic & Mood
    # ============================================================
    
    def _analyze_content(self, topic: str, script: str = "") -> Dict:
        """Analyze content to determine visual style"""
        topic_lower = topic.lower()
        script_lower = script.lower()
        
        # Detect primary topic
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
        
        # If script provided, use it for better detection
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
    # GENERATE THUMBNAIL - Based on Content
    # ============================================================
    
    def generate_thumbnail(self, words: List[str], topic: str, output_path: str, 
                           script: str = "", hook: str = "") -> str:
        """
        Generate AI-powered thumbnail based on video content
        
        Args:
            words: 3 words for thumbnail
            topic: Video topic
            output_path: Save path
            script: Full script (for context)
            hook: Hook text (for additional context)
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # ============================================================
        # Step 1: Analyze content
        # ============================================================
        analysis = self._analyze_content(topic, script)
        palette = analysis['palette']
        mood = analysis['mood']
        style = analysis['style']
        main_emoji = analysis['emoji']
        
        print(f"    🎯 Detected: {analysis['topic']} | Mood: {mood} | Style: {style}")
        
        # ============================================================
        # Step 2: Create background based on topic
        # ============================================================
        bg_hex = random.choice(palette['bg'])
        img = self._create_dynamic_background(bg_hex, style, mood)
        
        # ============================================================
        # Step 3: Add mood-based effects
        # ============================================================
        img = self._add_mood_effects(img, mood)
        
        # ============================================================
        # Step 4: Add style-based overlays
        # ============================================================
        img = self._add_style_overlays(img, style)
        
        # ============================================================
        # Step 5: Prepare words
        # ============================================================
        words_chunk = words[:3]
        while len(words_chunk) < 3:
            words_chunk.append(random.choice(["TRUTH", "SECRET", "POWER", "BRAIN", "FOCUS"]))
        
        # ============================================================
        # Step 6: Dynamic font sizing based on word length
        # ============================================================
        font_size = self._calculate_dynamic_font_size(words_chunk)
        font_main = _load_font(font_size, bold=True)
        font_emoji = _load_font(self.font_size_emoji, bold=False)
        font_banner = _load_font(self.font_size_banner, bold=True)
        
        # ============================================================
        # Step 7: Layout based on content
        # ============================================================
        y_positions = self._get_dynamic_layout(words_chunk, style)
        
        # ============================================================
        # Step 8: Draw words with topic-based styling
        # ============================================================
        for i, (word, y) in enumerate(zip(words_chunk, y_positions)):
            # Color based on word position
            if i == 0:
                color = palette['text'][0]
            elif i == 1:
                color = palette['text'][1]
            else:
                color = palette['text'][2] if len(palette['text']) > 2 else palette['text'][0]
            
            # Shadow
            img = self._add_dynamic_shadow(img, word, y, font_main, color, mood)
            
            # Text with outline
            img = self._add_text_with_outline(img, word, y, font_main, color, mood)
            
            # Highlight on first word
            if i == 0:
                img = self._add_highlight_effect(img, word, y, font_main)
            
            # Emoji based on topic
            emoji = self._get_dynamic_emoji(word, topic, main_emoji, i)
            if emoji:
                img = self._draw_emoji(img, emoji, y, font_emoji, i, mood)
        
        # ============================================================
        # Step 9: Topic banner
        # ============================================================
        draw = ImageDraw.Draw(img)
        self._add_dynamic_banner(draw, topic, font_banner, palette)
        
        # ============================================================
        # Step 10: Border based on style
        # ============================================================
        self._add_dynamic_border(draw, style, palette)
        
        # ============================================================
        # Step 11: Play button
        # ============================================================
        self._add_play_button(draw, mood)
        
        # ============================================================
        # Step 12: Final enhancement
        # ============================================================
        img = self._enhance_image(img, mood)
        
        # ============================================================
        # Step 13: Save
        # ============================================================
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95, optimize=True)
        
        print(f"    🎨 Thumbnail: {output_path}")
        print(f"    📝 Words: {words_chunk} | Mood: {mood}")
        
        return output_path

    # ============================================================
    # DYNAMIC BACKGROUND
    # ============================================================
    
    def _create_dynamic_background(self, color: str, style: str, mood: str) -> Image.Image:
        """Create background based on style and mood"""
        img = Image.new("RGB", (self.width, self.height), _hex_to_rgb(color))
        
        # Gradient overlay
        gradient = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Dynamic gradient based on style
        if style == 'premium' or style == 'scientific':
            # Gold/dark gradient
            for y in range(self.height):
                alpha = int(150 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        
        elif style == 'dramatic' or style == 'intense':
            # Dark red gradient
            for y in range(self.height):
                alpha = int(180 * (y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(30, 0, 0, alpha))
        
        elif style == 'calm' or style == 'misty':
            # Blue gradient
            for y in range(self.height):
                alpha = int(100 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 30, 60, alpha))
        
        else:
            # Default gradient
            for y in range(self.height):
                alpha = int(120 * (1 - y / self.height))
                draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, gradient)
        return img.convert("RGB")

    # ============================================================
    # MOOD EFFECTS
    # ============================================================
    
    def _add_mood_effects(self, img: Image.Image, mood: str) -> Image.Image:
        """Add effects based on emotional mood"""
        effect = self.emotion_effects.get(mood, self.emotion_effects['curious'])
        glow_color = _hex_to_rgb(effect['glow'])
        intensity = effect['intensity']
        
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Mood-based glow
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
    # STYLE OVERLAYS
    # ============================================================
    
    def _add_style_overlays(self, img: Image.Image, style: str) -> Image.Image:
        """Add style-specific overlays"""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        if style == 'scientific':
            # Grid pattern for science
            for x in range(0, self.width, 60):
                draw.line([(x, 0), (x, self.height)], fill=(0, 100, 200, 10), width=1)
            for y in range(0, self.height, 60):
                draw.line([(0, y), (self.width, y)], fill=(0, 100, 200, 10), width=1)
        
        elif style == 'premium':
            # Diagonal gold lines
            for i in range(3):
                x = i * 300 - 200
                points = [(x, -100), (x + 400, self.height + 100)]
                draw.line(points, fill=(255, 215, 0, 15), width=2)
        
        elif style == 'dramatic':
            # Dark corners
            for i in range(0, self.height, 10):
                alpha = int(30 * (i / self.height))
                draw.line([(0, i), (self.width, i)], fill=(20, 0, 0, alpha))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        return img.convert("RGB")

    # ============================================================
    # DYNAMIC FONT SIZE
    # ============================================================
    
    def _calculate_dynamic_font_size(self, words: List[str]) -> int:
        """Calculate font size based on word length"""
        max_len = max(len(w) for w in words)
        
        if max_len <= 5:
            return 170
        elif max_len <= 7:
            return 150
        elif max_len <= 10:
            return 130
        else:
            return 110

    # ============================================================
    # DYNAMIC LAYOUT
    # ============================================================
    
    def _get_dynamic_layout(self, words: List[str], style: str) -> List[int]:
        """Get layout based on style"""
        if style == 'premium' or style == 'scientific':
            # Centered, professional
            return [
                self.height // 5,
                self.height // 2,
                int(self.height * 0.73)
            ]
        elif style == 'dramatic':
            # Off-center, dramatic
            return [
                self.height // 6 + 20,
                self.height // 2 - 30,
                int(self.height * 0.75) + 20
            ]
        else:
            # Default
            return [
                self.height // 5 + random.randint(-20, 20),
                self.height // 2 + random.randint(-15, 15),
                int(self.height * 0.73) + random.randint(-20, 20)
            ]

    # ============================================================
    # DYNAMIC SHADOW
    # ============================================================
    
    def _add_dynamic_shadow(self, img: Image.Image, text: str, y: int,
                            font, color: str, mood: str) -> Image.Image:
        """Add shadow based on mood"""
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        # Shadow intensity based on mood
        shadow_depth = 14 if mood in ['dramatic', 'urgent', 'intense'] else 10
        
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
    # TEXT WITH OUTLINE
    # ============================================================
    
    def _add_text_with_outline(self, img: Image.Image, text: str, y: int,
                                 font, color: str, mood: str) -> Image.Image:
        """Add text with outline based on mood"""
        txt_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_layer)
        
        bbox = txt_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y_pos = y - (text_height // 2)
        
        # Outline width based on mood
        outline_width = 10 if mood in ['dramatic', 'urgent', 'intense'] else 8
        
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
        
        # Glow for dramatic mood
        if mood in ['dramatic', 'urgent', 'intense']:
            glow_layer = txt_layer.copy()
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=12))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, glow_layer)
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, txt_layer)
        return img.convert("RGB")

    # ============================================================
    # HIGHLIGHT EFFECT
    # ============================================================
    
    def _add_highlight_effect(self, img: Image.Image, text: str, y: int,
                                font) -> Image.Image:
        """Add 3D highlight effect"""
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
    # DYNAMIC EMOJI
    # ============================================================
    
    def _get_dynamic_emoji(self, word: str, topic: str, default_emoji: str, 
                           index: int) -> str:
        """Get dynamic emoji based on word and topic"""
        word_lower = word.lower()
        
        # Word-based emojis
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
        
        return default_emoji

    def _draw_emoji(self, img: Image.Image, emoji: str, y: int,
                    font, index: int, mood: str) -> Image.Image:
        """Draw emoji with mood-based styling"""
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
        
        # Emoji glow for dramatic mood
        if mood in ['dramatic', 'urgent', 'intense']:
            glow_layer = overlay.copy()
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=10))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, glow_layer)
        
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
    # DYNAMIC BANNER
    # ============================================================
    
    def _add_dynamic_banner(self, draw: ImageDraw.Draw, topic: str, 
                            font, palette: Dict):
        """Add banner based on topic palette"""
        topic_text = f"⚡ {topic[:20].upper()} ⚡"
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
    # DYNAMIC BORDER
    # ============================================================
    
    def _add_dynamic_border(self, draw: ImageDraw.Draw, style: str, palette: Dict):
        """Add border based on style"""
        accent_color = palette.get('accent', '#FFD700')
        border_width = 10
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
            width=2
        )

    # ============================================================
    # PLAY BUTTON
    # ============================================================
    
    def _add_play_button(self, draw: ImageDraw.Draw, mood: str):
        """Add play button with mood-based styling"""
        center_x = self.width // 2
        bottom_y = self.height - 150
        
        # Glow color based on mood
        glow_color = self.emotion_effects.get(mood, {}).get('glow', '#FFD700')
        
        # Glow circle
        for r in range(60, 40, -5):
            alpha = int(30 * (1 - r / 60))
            draw.ellipse(
                [center_x - r, bottom_y - r, center_x + r, bottom_y + r],
                outline=_hex_to_rgba(glow_color, alpha),
                width=1
            )
        
        # Main circle
        draw.ellipse(
            [center_x - 40, bottom_y - 40, center_x + 40, bottom_y + 40],
            fill=_hex_to_rgba(glow_color, 150),
            outline=(255, 255, 255, 200),
            width=3
        )
        
        # Play triangle
        points = [
            (center_x - 15, bottom_y - 18),
            (center_x + 15, bottom_y),
            (center_x - 15, bottom_y + 18)
        ]
        draw.polygon(points, fill=(255, 255, 255, 220))

    # ============================================================
    # ENHANCE IMAGE
    # ============================================================
    
    def _enhance_image(self, img: Image.Image, mood: str) -> Image.Image:
        """Enhance image based on mood"""
        # Contrast based on mood
        contrast_factor = 1.1 if mood in ['dramatic', 'urgent', 'intense'] else 1.05
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
        
        # Sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)
        
        return img


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING AI-POWERED THUMBNAIL GENERATOR\n" + "="*60)
    
    generator = ThumbnailGenerator()
    
    # Test with different topics
    test_cases = [
        ("forgetting names", ["MEMORY", "LOSS", "BRAIN"]),
        ("brain fog", ["BRAIN", "FOG", "STOP"]),
        ("sleep problems", ["SLEEP", "FIX", "NOW"]),
        ("stress relief", ["STRESS", "OUT", "CALM"]),
        ("memory tips", ["MEMORY", "HACKS", "PROVEN"]),
    ]
    
    for i, (topic, words) in enumerate(test_cases):
        output_path = f"test_thumbnail_{i+1}.jpg"
        generator.generate_thumbnail(
            words=words,
            topic=topic,
            output_path=output_path,
            script=f"This video is about {topic}. It explains the science behind why {topic} happens to men after 35."
        )
        print(f"   ✅ Generated: {output_path}")
    
    print(f"\n✅ All thumbnails generated!")