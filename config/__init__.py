"""
Config package — Application configuration, API keys, and prompt templates.

FIX M13: Proper __init__.py with lazy imports so that importing config
doesn't fail if .env is missing (properties evaluate lazily).
"""

__all__ = ['API_KEYS', 'VIDEO_CONFIG', 'AUDIO_CONFIG', 'CAPTION_CONFIG',
           'SEO_CONFIG', 'UPLOAD_CONFIG', 'APIKeys', 'VideoConfig', 'AudioConfig',
           'CaptionConfig', 'SEOConfig', 'UploadConfig']


def __getattr__(name):
    """Lazy import — only load config when first accessed."""
    if name in __all__:
        from config import settings as _settings
        return getattr(_settings, name)
    raise AttributeError(f"module 'config' has no attribute {name}")
