"""
YouTube Automation System - Main Orchestrator (Production & Cron-Ready)
"""

import asyncio
import os
import traceback
from datetime import datetime

from config.settings import VIDEO_CONFIG, PLATFORM_CONFIG, API_KEYS
from core.topic_engine import ViralTopicEngine
from core.content_generator import ContentGenerator
from core.audio_generator import AudioGenerator
from core.footage_fetcher import FootageFetcher
from core.video_assembler import VideoAssembler
from core.thumbnail_generator import ThumbnailGenerator

# ⚙️ PRODUCTION TOGGLE
# Jab Cron Job chale aur automatic upload karna ho, toh isko True rakhein.
PRODUCTION_MODE = True 

if PRODUCTION_MODE:
    try:
        from core.youtube_uploader import YouTubeUploader
    except ImportError:
        YouTubeUploader = None
else:
    YouTubeUploader = None


class YouTubeAutomationSystem:
    def __init__(self):
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        
        # 🚀 PRODUCTION MODE ACTIVE: Real uploader initialize ho raha hai
        if PRODUCTION_MODE and YouTubeUploader:
            self.youtube_uploader = YouTubeUploader()
            print("📺 Production Mode: YouTube Uploader successfully connected.")
        else:
            self.youtube_uploader = None
            print("🧪 Testing Mode: Uploads are bypassed.")
        
        self.fb_uploader = None
        self.ig_uploader = None
        
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def create_video(self, topic_data):
        topic = topic_data['query']
        angle = self.topic_engine.get_topic_angle(topic_data) if hasattr(self.topic_engine, 'get_topic_angle') else "psychological mystery"
        
        print(f"\n🎬 Creating video for: {topic}")
        
        # 1. Generate Content
        script_data = self.content_gen.generate_script(topic, angle)
        
        # Safe extraction logic
        script_text = ""
        if isinstance(script_data, dict):
            script_text = (
                script_data.get('full_script')
                or script_data.get('script')
                or script_data.get('script_text')
                or script_data.get('text')
                or ""
            )
            if not script_text and 'segments' in script_data:
                script_text = " ".join([seg.get('text', '') for seg in script_data['segments'] if 'text' in seg])
        elif isinstance(script_data, str):
            script_text = script_data
            script_data = {'full_script': script_text, 'segments': []}

        if not script_text:
            script_text = f"Discover the shocking truth behind {topic}."
            
        print(f"   ✍️ Script resolved safely ({len(script_text.split())} words)")
        
        # 2. Generate Audio & Timings
        print(f"   🎙️ Generating TTS voice and parsing timestamps...")
        audio_data = await self.audio_gen.generate_audio_with_timings(script_text, self.output_dir)
        
        # 3. Fetch Clips / Footage
        segments = script_data.get('segments') or [{'type': 'story', 'duration': audio_data['total_duration'], 'is_pause': False}]

        print(f"   🔍 Downloading semantic background clips...")
        footage_clips = self.footage_fetcher.fetch_footage_for_script(segments, topic)
        footage_dir = os.path.join(self.output_dir, "footage")
        self.footage_fetcher.download_footage(footage_clips, footage_dir)

        # 4. Assemble Final Video
        output_video_path = os.path.join(self.output_dir, f"render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

        video_path = self.video_assembler.create_video(
            script_segments=segments,
            audio_data=audio_data,
            footage_clips=footage_clips,
            word_timings=audio_data['word_timings'],
            output_path=output_video_path
        )
        
        # 5. Generate Thumbnail Concept with 3-arguments structure
        thumbnail_path = os.path.join(self.output_dir, "thumb_preview.jpg")
        thumb_words = self.content_gen.generate_thumbnail_words(topic)
        self.thumbnail_gen.generate_thumbnail(thumb_words, topic, thumbnail_path)

        # 6. Generate viral title + SEO data
        title = self.content_gen.generate_title(topic)
        seo_data = self.content_gen.generate_seo(topic, script_text)

        return {
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "duration": audio_data['total_duration'],
            "title": title,
            "description": seo_data['description'],
            "tags": seo_data['tags']
        }

    async def run(self):
        status_label = "PRODUCTION" if PRODUCTION_MODE else "TESTING"
        print(f"🚀 Starting Automation System in [{status_label} MODE]...")
        
        try:
            topics = self.topic_engine.fetch_trending_topics()
        except Exception:
            topics = []
            
        if not topics:
            print("⚠️ Live Trends Rate-Limited. Injecting local dark psychology testing node...")
            topics = [
                {"query": "cognitive dissonance", "category": "psychology"}
            ]
            
        # ✨ CRITICAL FIX: Slicing the topic array to exactly 1 item.
        # Is se loop sirf ek martaba chalega aur server resources 50% bacha lega!
        topics = topics[:1]
            
        for i, topic in enumerate(topics):
            print(f"\n{'='*50}")
            print(f"Video Job 1/1: {topic['query']}")
            print(f"{'='*50}")
            
            try:
                video_data = await self.create_video(topic)
                
                print(f"\n✅ Video compilation complete!")
                print(f"   📁 File: {video_data['video_path']}")
                print(f"   ⏱️  Duration: {video_data['duration']:.1f}s")
                print(f"   📝 Title: {video_data['title']}")
                
                # 📤 AUTO UPLOAD LAYER
                if self.youtube_uploader:
                    print("📤 Initiating automated YouTube Shorts upload...")
                    await self.youtube_uploader.upload_video(
                        file_path=video_data['video_path'],
                        title=video_data['title'],
                        description=video_data['description'],
                        tags=video_data['tags']
                    )
                    print("🎉 Video successfully processed and pushed live to YouTube!")
                else:
                    print("🌐 [INFO] Upload skipped. (System is in preview or uploader is offline)")
                    
            except Exception as e:
                print(f"❌ Error processing automation execution: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run())
