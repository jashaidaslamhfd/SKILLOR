# SKILLOR - YouTube/Facebook Automation System

**Skillor** is an IT HUB automation system for generating and uploading AI-powered short-form video content to YouTube and Facebook.

## Features

✅ **Automated Script Generation** - AI-powered script writing with Groq LLM
✅ **Dual Image Generation** - Google Gemini + Hugging Face FLUX.1 with fallback
✅ **Professional Voice Generation** - Kokoro TTS for natural-sounding voiceovers
✅ **Smart Video Editing** - Automated video composition with effects and captions
✅ **Batch Upload** - Direct upload to YouTube and Facebook Reels
✅ **Robust Error Handling** - Retry logic, timeouts, and comprehensive logging
✅ **Rate Limiting** - Built-in throttling for API stability

## System Architecture

```
┌─────────────────┐
│  Topic Input    │
└────────┬────────┘
         ↓
┌─────────────────────────┐
│  Script Generation      │ (Groq LLM)
│  - Title               │
│  - Voiceover           │
│  - Scenes (6-9)        │
└────────┬────────────────┘
         ↓
┌──────────────────────────────────────────┐
│  Image Generation (Per Scene)            │
│  1. Try Google Gemini                    │
│  2. Fallback to Hugging Face FLUX.1      │
│  3. Last resort: Placeholder             │
└────────┬─────────────────────────────────┘
         ↓
┌─────────────────┐
│  Voice Gen      │ (Kokoro TTS)
└────────┬────────┘
         ↓
┌──────────────────────────────────────┐
│  Video Composition                   │
│  - Sync audio with images            │
│  - Add captions                      │
│  - Apply effects (zoom, etc)         │
│  - Generate thumbnail                │
└────────┬─────────────────────────────┘
         ↓
┌────────────────────────────┐
│  Upload to Platforms       │
│  - YouTube (primary)       │
│  - Facebook Reels          │
└────────────────────────────┘
```

## Installation

### Requirements
- Python 3.9+
- FFmpeg
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/jashaidaslamhfd/SKILLOR.git
cd SKILLOR

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure your API keys in .env
```

## Configuration

### Required API Keys

1. **YouTube API**
   - Create service account at [Google Cloud Console](https://console.cloud.google.com)
   - Download JSON credentials
   - Set `YT_CLIENT_SECRET` environment variable

2. **Facebook API**
   - Get access token from [Facebook Developers](https://developers.facebook.com)
   - Set `FB_ACCESS_TOKEN` and `FB_PAGE_ID`

3. **Image Generation**
   - Google Gemini: [Get API key](https://ai.google.dev)
   - Hugging Face: [Get API key](https://huggingface.co/settings/tokens)

4. **LLM**
   - Groq: [Get API key](https://console.groq.com)

## Usage

### Basic Usage

```bash
# Export API keys
export GROQ_API_KEY="your_groq_key"
export GEMINI_API_KEY="your_gemini_key"
export HF_API_KEY="your_hf_key"
export YT_CLIENT_SECRET='{...}'
export FB_ACCESS_TOKEN="your_fb_token"
export FB_PAGE_ID="your_page_id"

# Run with custom topic
export VIDEO_TOPIC="Amazing Facts About Space"
python src/main.py
```

### With Docker

```bash
docker build -t skillor .
docker run --env-file .env skillor
```

## Troubleshooting

### Image Generation Fails
- **Check:** Verify GEMINI_API_KEY and HF_API_KEY are valid
- **Fallback:** Ensure `assets/placeholder.png` exists
- **Solution:** Try with placeholder images first

### Audio Generation Issues
- **Check:** Kokoro model is properly installed
- **Solution:** `pip install kokoro --upgrade`

### YouTube Upload Fails
- **Check:** Service account has YouTube Data API v3 enabled
- **Solution:** Enable API in Google Cloud Console
- **Credentials:** Verify YT_CLIENT_SECRET is valid JSON

### Facebook Upload Fails
- **Check:** Access token has necessary permissions
- **Permissions Needed:**
  - `pages_manage_metadata`
  - `pages_read_user_profile`
  - `pages_manage_posts`
  - `video_upload`

## File Structure

```
SKILLOR/
├── src/
│   ├── main.py                # Main pipeline entry point
│   ├── script_generator.py    # Script generation with Groq
│   ├── image_generator.py     # Image generation (Gemini/HF)
│   ├── voice_generator.py     # Voice generation (Kokoro TTS)
│   ├── video_editor.py        # Video composition & editing
│   └── uploader.py            # YouTube & Facebook upload
├── assets/
│   └── placeholder.png        # Fallback image for videos
├── output/                     # Generated videos & thumbnails
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Error Handling

### Retry Logic
- Script generation: 3 attempts with exponential backoff
- Hugging Face API: 3 attempts with rate limit handling
- YouTube upload: 3 attempts with 429/500+ error recovery
- Facebook upload: 3 attempts with throttling support

### Fallback Mechanisms
1. **Image Generation:**
   - Primary: Google Gemini
   - Fallback: Hugging Face FLUX.1
   - Last resort: Placeholder image

2. **Video Composition:**
   - Missing images → Placeholder
   - Missing audio → Runtime error
   - Invalid captions → Skip gracefully

## Performance Tips

1. **Parallel Processing:** Use multiple instances for batch operations
2. **Image Generation:** Hugging Face is faster; Gemini is higher quality
3. **Video Encoding:** Reduce resolution for faster rendering
4. **Rate Limiting:** Respect API quotas; use scheduled uploads

## Limitations

- YouTube Shorts: Max 60 seconds
- Facebook Reels: Max 90 seconds
- Thumbnail: 1280x720px recommended
- Description: YouTube max 5000 chars, Facebook max 63 chars

## Support

For issues and feature requests, visit:
- **GitHub Issues:** https://github.com/jashaidaslamhfd/SKILLOR/issues
- **Documentation:** Check logs in `output/` directory

## License

This project is open source and available under the MIT License.

---

**Made with ❤️ for content creators**
