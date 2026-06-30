# SKILLOR — YouTube Shorts Automation System

**End-to-end automated pipeline** for creating and publishing viral YouTube Shorts, Facebook Reels, and Instagram Reels about Body + Brain Science.

## Pipeline Overview

```
Topic Discovery → Script Generation → Voice Synthesis → Footage Fetch → Caption Generation → Video Assembly → Thumbnail → Upload (YouTube, Facebook, Instagram)
```

## Features

- **AI Script Generation** — Groq LLM (llama-3.3-70b-versatile) generates viral-optimized scripts with hook → shock → suspense → story → CTR structure
- **Human-Like Voice** — Groq Orpheus TTS with "troy" voice for natural male narration
- **Karaoke Captions** — ASS subtitle format with word-by-word highlighting, auto-stretched to match audio duration
- **Stock Footage** — Automatic fetching from Pexels and Pixabay APIs with deduplication
- **Thumbnail Generation** — Dynamic topic-based color palettes with platform-specific styles
- **Multi-Platform Upload** — YouTube Shorts, Facebook Reels, Instagram Reels (via Graph APIs)
- **Google Trends** — Automated topic discovery from trending searches
- **Cloudinary Integration** — Video URL hosting required for Instagram uploads
- **GitHub Actions CI/CD** — Scheduled 3x daily automated video generation and upload
- **Metrics Tracking** — Upload success/failure tracking with daily statistics

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/SKILLOR.git
cd SKILLOR

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install FFmpeg (required)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# 4. Create .env file from template
cp .env.example .env
# Edit .env with your API keys

# 5. Run health check
python main.py --health-check

# 6. Generate and upload 1 video
python main.py

# 7. Generate without uploading
python main.py --skip-upload

# 8. Generate with specific topic
python main.py --topic "why your body jerks before sleep"

# 9. Generate multiple videos
python main.py --count 3
```

## Required API Keys

| Key | Purpose | Get From |
|-----|---------|----------|
| `GROQ_API_KEY` | AI script + TTS | [console.groq.com](https://console.groq.com) |
| `PEXELS_API_KEY` | Stock footage | [pexels.com/api](https://www.pexels.com/api/) |
| `PIXABAY_API_KEY` | Stock footage | [pixabay.com/api/docs](https://pixabay.com/api/docs/) |
| `GOOGLE_CLIENT_ID` | YouTube upload | [Google Cloud Console](https://console.cloud.google.com/) |
| `GOOGLE_CLIENT_SECRET` | YouTube upload | Google Cloud Console |
| `REFRESH_TOKEN` | YouTube upload | OAuth2 flow |
| `YOUTUBE_API_KEY` | YouTube analytics | Google Cloud Console |
| `FACEBOOK_ACCESS_TOKEN` | Facebook upload | [Facebook Developers](https://developers.facebook.com/) |
| `FACEBOOK_PAGE_ID` | Facebook upload | Your Facebook Page |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram upload | [Facebook Developers](https://developers.facebook.com/) |
| `INSTAGRAM_USER_ID` | Instagram upload | Your Instagram Business Account |
| `CLOUDINARY_CLOUD_NAME` | Video hosting | [cloudinary.com](https://cloudinary.com/) |
| `CLOUDINARY_API_KEY` | Video hosting | Cloudinary Dashboard |
| `CLOUDINARY_API_SECRET` | Video hosting | Cloudinary Dashboard |

## Project Structure

```
SKILLOR/
├── main.py                    # Entry point with argparse CLI
├── orchestrator.py            # Master pipeline orchestrator
├── .github/workflows/
│   └── auto-post.yml          # GitHub Actions CI/CD (3x daily)
├── config/
│   ├── settings.py            # All configuration dataclasses
│   └── prompts.py             # AI prompt templates
├── core/
│   ├── topic_engine.py        # Google Trends topic discovery
│   ├── hook_engine.py         # Self-correcting hook generator
│   ├── content_generator.py   # AI script + title generator
│   ├── audio_generator.py     # Groq Orpheus TTS
│   ├── caption_generator.py   # ASS karaoke caption engine
│   ├── footage_fetcher.py     # Pexels + Pixabay footage
│   ├── video_assembler.py     # FFmpeg video assembly
│   ├── thumbnail_generator.py # Dynamic thumbnail creator
│   ├── cloud_uploader.py      # Cloudinary video hosting
│   ├── metrics.py             # Upload tracking & stats
│   └── youtube_analytics.py   # YouTube performance data
├── uploaders/
│   ├── youtube_uploader.py    # YouTube Data API v3
│   ├── facebook_uploader.py   # Facebook Graph API
│   └── instagram_uploader.py  # Instagram Graph API
├── state/                     # Runtime state (used topics, clips)
├── output/                    # Generated videos, thumbnails
├── logs/                      # Application logs
└── requirements.txt           # Python dependencies
```

## GitHub Actions Setup

The workflow runs 3x daily at 12:00, 16:00, and 22:00 UTC. To enable:

1. Add all API keys as **Repository Secrets** in GitHub Settings → Secrets and variables → Actions
2. Ensure the workflow file is on the `main` branch
3. Manually trigger with "Run workflow" button to test

## Configuration

All settings are in `config/settings.py` using Python dataclasses:

- **VideoConfig** — Duration (42-55s), resolution (1080x1920), bitrate
- **AudioConfig** — Target duration, sample rate, voice settings
- **CaptionConfig** — Font size, colors, margins, karaoke settings
- **SEOConfig** — Hashtags, category ID, niche keywords
- **PlatformConfig** — Upload settings per platform

## License

Private repository. All rights reserved.
