"""
Uploaders package — Platform-specific upload handlers for YouTube, Facebook, Instagram.

FIX M12: Proper __init__.py with lazy imports to avoid circular dependencies
and missing dependency errors at module load time.
"""

__all__ = ['YouTubeUploader', 'FacebookUploader', 'InstagramUploader']


def __getattr__(name):
    """Lazy import — only load uploader when first accessed, not at import time."""
    if name == 'YouTubeUploader':
        from uploaders.youtube_uploader import YouTubeUploader
        return YouTubeUploader
    elif name == 'FacebookUploader':
        from uploaders.facebook_uploader import FacebookUploader
        return FacebookUploader
    elif name == 'InstagramUploader':
        from uploaders.instagram_uploader import InstagramUploader
        return InstagramUploader
    raise AttributeError(f"module 'uploaders' has no attribute {name}")
