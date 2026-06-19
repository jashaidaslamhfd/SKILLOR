"""
YouTube Automation System - Main Orchestrator (Testing Optimized)
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

class YouTubeAutomationSystem:
    def __init__(self):
        self.topic_engine = ViralTopicEngine()
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator()
        self.footage_fetcher = FootageFetcher()
        self.video_assembler = VideoAssembler()
        self.thumbnail_gen = ThumbnailGenerator()
        
        # 🧪 TESTING MODE: Uploaders completely detached to prevent channel spam
        self.youtube_uploader = None
        self.fb_uploader = None
        self.ig_uploader = None
        
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def create_video(self, topic_data):
        topic = topic_data['query']
        angle = self.topic_engine.get_topic_angle(topic_data)
        
        print(f"\n🎬 Creating video for: {topic}")
        
        # 1. Generate Content
        script_data = self.content_gen.generate_script(topic, angle)
        print(f"   ✍️ Script generated ({len(script_data['script'].split())} words)")
        
        # 2. Generate Audio & Timings
        print(f"   🎙️ Generating TTS voice and parsing timestamps...")
        audio_data = await self.audio_gen.generate_audio_with_timings(script_data['script'], self.output_dir)
        
        # 3. Fetch Clips / Footage
        print(f"   🔍 Downloading semantic background clips...")
        footage_clips = await self.footage_fetcher.fetch_footage(script_data['keywords'], audio_data['total_duration'])
        
        # 4. Assemble Final Video (with fixed precision subtitles & absolute path lookup)
        output_video_path = os.path.join(self.output_dir, f"render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        video_path = self.video_assembler.create_video(
            script_segments=script_data['segments'],
            audio_data=audio_data,
            footage_clips=footage_clips,
            word_timings=audio_data['word_timings'],
            output_path=output_video_path
        )
        
        # 5. Generate Thumbnail Concept for review
        thumbnail_path = os.path.join(self.output_dir, "thumb_preview.jpg")
        self.thumbnail_gen.generate_thumbnail(topic, thumbnail_path)
        
        return {
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "duration": audio_data['total_duration'],
            "title": script_data.get('title', 'Test Automation Video'),
            "description": script_data.get('description', '')
        }

    async def run(self):
        print("🚀 Starting Automation System in [TESTING MODE]...")
        print("⚠️ All uploads are bypassed. Output files will be stored in 'output/' directory.")
        
        topics = self.topic_engine.get_trending_topics()
        if not topics:
            print("❌ No trending topics discovered.")
            return
            
        for i, topic in enumerate(topics):
            print(f"\n{'='*50}")
            print(f"Video {i+1}/{len(topics)}: {topic['query']}")
            print(f"{'='*50}")
            
            try:
                video_data = await self.create_video(topic)
                
                print(f"\n✅ Video {i+1} compilation complete! [SAVED LOCALLY]")
                print(f"   📁 File: {video_data['video_path']}")
                print(f"   🖼️  Thumbnail preview: {video_data['thumbnail_path']}")
                print(f"   ⏱️  Duration: {video_data['duration']:.1f}s")
                print(f"   📝 Title: {video_data['title']}")
                print(f"   🌐 [INFO] Upload skipped to protect production channel spam limits.")
                
                if i < len(topics) - 1:
                    print(f"\n⏳ Waiting 10 seconds before next test video...")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ Error processing test video {i+1}: {e}")
                traceback.print_exc()
                continue

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run())
