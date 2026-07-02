name: 🎬 USA Parent-First Pipeline - Low Retention Fix (2026)

on:
  schedule:
    # FIX 1: Timings change. Parents active slots, not baby bedtime
    # 08:00 AM EST - Parents morning scroll while baby busy
    - cron: '0 13 * * *'
    # 12:30 PM EST - Lunch break, high parent phone usage  
    - cron: '30 17 * * *'
    # 07:30 PM EST - Prime time: parents + baby both awake, co-viewing
    - cron: '30 0 * * *'
    
  workflow_dispatch:

jobs:
  automate_shorts:
    runs-on: ubuntu-latest
    timeout-minutes: 120 # FIX 2: Baby niche = heavy SFX + captions. 45min me fail hota tha

    steps:
      - name: 📥 Checkout System Repository Codes
        uses: actions/checkout@v4

      - name: 🐍 Initialize Python Execution Node (3.11)
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: 🎛️ Install Native Core System Binaries (FFmpeg + Espeak + ImageMagick)
        run: |
          sudo apt update
          sudo apt install -y ffmpeg espeak-ng libxml2-dev libxslt-dev imagemagick
          # ImageMagick = captions/hook text ke liye zaroori

      - name: 📦 Build Deep Dependency Cache & Modules Lock
        run: |
          python -m pip install --upgrade pip setuptools wheel
          if [ -f requirements.txt ]; then 
            pip install -r requirements.txt
          else
            find . -name "requirements.txt" -exec pip install -r {} \;
          fi

      - name: 🔍 Pre-Flight: Validate COPPA + Retention Config
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
        run: |
          MAIN_PATH=$(find . -name "main.py" | head -n 1)
          if [ -z "$MAIN_PATH" ]; then
            echo "❌ CRITICAL: main.py missing"
            exit 1
          fi
          cd $(dirname "$MAIN_PATH")
          # FIX 3: Health check me ab retention score bhi check hoga
          python main.py --health-check --validate-hooks

      - name: 🚀 Run Content Pipeline - Parent Optimized
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
          REFRESH_TOKEN: ${{ secrets.REFRESH_TOKEN }}
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          CLOUDINARY_CLOUD_NAME: ${{ secrets.CLOUDINARY_CLOUD_NAME }}
          CLOUDINARY_API_KEY: ${{ secrets.CLOUDINARY_API_KEY }}
          CLOUDINARY_API_SECRET: ${{ secrets.CLOUDINARY_API_SECRET }}
          
          # FIX 4:
