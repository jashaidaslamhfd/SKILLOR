"""
YouTube Automation System - Main Orchestrator (Testing & Rate-Limit Bypass Optimized)
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
        angle = self.topic_engine.get_topic_angle(topic_data) if hasattr(self.topic_engine, 'get_topic_angle') else "psychological mystery"
        
        print(f"\n🎬 Creating video for: {topic}")
        
        # 1. Generate Content
        script_data = self.content_gen.generate_script(topic, angle)
        
        # Safe extraction logic to prevent KeyError: 'script'
        script_text = ""
        if isinstance(script_data, dict):
            # FIX: ContentGenerator.generate_script() returns the key 'full_script',
            # not 'script'/'script_text'/'text'. The old lookup never matched it,
            # so the real AI-generated script was silently discarded every time
            # and the generic fallback line was used instead.
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
        keywords = script_data.get('keywords', f"psychology,{topic}")
        print(f"   🔍 Downloading semantic background clips...")
        footage_clips = await self.footage_fetcher.fetch_footage(keywords, audio_data['total_duration'])
        
        # 4. Assemble Final Video (with fixed precision subtitles & absolute path lookup)
        output_video_path = os.path.join(self.output_dir, f"render_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        
        segments = script_data.get('segments') or [{'type': 'story', 'duration': audio_data['total_duration'], 'is_pause': False}]
        
        video_path = self.video_assembler.create_video(
            script_segments=segments,
            audio_data=audio_data,
            footage_clips=footage_clips,
            word_timings=audio_data['word_timings'],
            output_path=output_video_path
        )
        
        # 5. Generate Thumbnail Concept for review
        thumbnail_path = os.path.join(self.output_dir, "thumb_preview.jpg")
        self.thumbnail_gen.generate_thumbnail(topic, thumbnail_path)

        # 6. Generate the actual viral title + SEO description/tags
        # FIX: these were written in ContentGenerator but never called from main.py,
        # so every test video used the generic "The Truth About {topic}" title
        # and a placeholder description with no real tags. Now we generate the
        # real values so the testing-mode output reflects what would actually
        # be uploaded later (no upload happens here, this is just preview data).
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
        print("🚀 Starting Automation System in [TESTING MODE]...")
        print("⚠️ All uploads are bypassed. Output files will be stored in 'output/' directory.")
        
        # FIX: Try fetching live, if 429 rate limit occurs, use mock topics instantly
        try:
            topics = self.topic_engine.fetch_trending_topics()
        except Exception:
            topics = []
            
        if not topics:
            print("⚠️ Live Trends Rate-Limited (429) or Blocked. Injecting local dark psychology testing nodes...")
            topics = [
                {"query": "cognitive dissonance", "category": "psychology"},
                {"query": "dark psychology secrets", "category": "behavior"}
            ]
            
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
                print(f"   📄 Description:\n{video_data['description']}")
                print(f"   🏷️  Tags: {', '.join(video_data['tags'])}")
                
                if i < len(topics) - 1:
                    print(f"\n⏳ Waiting 10 seconds before next test video...")
                    await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"❌ Error processing test video {i+1}: {e}")
                traceback.print_exc()
                continue

if __name__ == "__main__":
    asyncio.run(YouTubeAutomationSystem().run())
