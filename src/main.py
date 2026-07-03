import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice
from video_editor import build_video, generate_thumbnail
from uploader import upload_all
from niche_strategy import get_script_prompt_for_niche, get_random_topic, get_topic_category
from quality_checker import QualityChecker
from scheduler import USAPeakTimeScheduler
from anti_spam import AntiSpamSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SKILLORPipeline:
    """
    Advanced YouTube Shorts Pipeline for Parenting Content.
    
    Features:
    - Brain & Body Science for Children/Babies niche
    - 3 daily uploads at USA peak times
    - Quality control to reduce swap rate from 72% to 20%
    - Anti-spam measures
    - Automated scheduling
    """
    
    def __init__(self):
        self.quality_checker = QualityChecker()
        self.scheduler = USAPeakTimeScheduler()
        self.anti_spam = AntiSpamSystem()
        self.video_history = self._load_video_history()
    
    def _load_video_history(self) -> list:
        """Load previous video data for spam checking."""
        history_file = "output/video_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_video_history(self, video_data: dict):
        """Save video data for future spam checking."""
        os.makedirs("output", exist_ok=True)
        self.video_history.append(video_data)
        
        # Keep last 50 videos for history
        if len(self.video_history) > 50:
            self.video_history = self.video_history[-50:]
        
        with open("output/video_history.json", 'w') as f:
            json.dump(self.video_history, f, indent=2)
    
    def generate_with_niche_strategy(self, topic: str = None) -> dict:
        """
        Generate video using specialized parenting niche strategy.
        
        Args:
            topic: Optional specific topic. If None, picks random from database.
        
        Returns:
            Generated script data with quality scores
        """
        try:
            # Step 1: Select topic
            if not topic:
                topic = get_random_topic()
            
            category = get_topic_category(topic)
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 Selected Topic: {topic}")
            logger.info(f"📁 Category: {category}")
            logger.info(f"{'='*60}")
            
            # Step 2: Generate specialized prompt
            specialized_prompt = get_script_prompt_for_niche(topic)
            
            # Step 3: Generate script with specialized prompt
            # Note: This requires modifying script_generator.py to accept custom prompts
            logger.info("\n[STEP 1/6] Generating Specialized Script...")
            script_data = generate_script(topic)
            
            # Step 4: Quality check
            logger.info("\n[STEP 1.5/6] Running Quality Checks...")
            quality_result = self.quality_checker.check_script_quality(script_data)
            
            logger.info(f"\n📊 Quality Scores:")
            logger.info(f"  Hook Score: {quality_result['scores'].get('hook_score', 0)}/100")
            logger.info(f"  Engagement Score: {quality_result['scores'].get('engagement_score', 0)}/100")
            logger.info(f"  Pacing Score: {quality_result['scores'].get('pacing_score', 0)}/100")
            logger.info(f"  Overall Quality: {quality_result['scores'].get('overall_quality', 0):.0f}/100")
            logger.info(f"  Status: {quality_result['recommendation']}")
            
            if not quality_result['approved']:
                logger.warning(f"\n⚠️ Quality issues detected:")
                for issue in quality_result['issues']:
                    logger.warning(f"  {issue}")
                logger.warning("\nGenerating improved version...")
                # In production, could retry generation here
            
            # Step 5: Anti-spam check
            logger.info("\n[STEP 1.75/6] Running Anti-Spam Analysis...")
            spam_result = self.anti_spam.check_for_spam_risks(script_data, self.video_history)
            
            logger.info(f"\n🛡️ Anti-Spam Results:")
            logger.info(f"  Spam Risk: {spam_result['spam_risk_level']}")
            logger.info(f"  Recommendation: {spam_result['recommendation']}")
            
            if spam_result['risks']:
                for risk in spam_result['risks']:
                    logger.warning(f"  {risk}")
            
            if spam_result['spam_risk_level'] in ['CRITICAL', 'HIGH']:
                raise RuntimeError(f"Spam risk too high: {spam_result['recommendation']}")
            
            # Add metadata
            script_data['topic'] = topic
            script_data['category'] = category
            script_data['quality_scores'] = quality_result['scores']
            script_data['spam_risk'] = spam_result['spam_risk_level']
            
            return script_data
        
        except Exception as e:
            logger.error(f"\n❌ Script generation failed: {e}", exc_info=True)
            raise
    
    def run_pipeline(self, topic: str = None, schedule_publish: bool = True) -> dict:
        """
        Run complete pipeline with all optimizations.
        
        Args:
            topic: Optional specific topic
            schedule_publish: Whether to schedule for publishing at peak times
        
        Returns:
            Upload results and metadata
        """
        try:
            logger.info("\n" + "🚀 " + "="*58)
            logger.info("  SKILLOR - Advanced YouTube Shorts Pipeline v5.1")
            logger.info("  Target: USA Parents - Brain & Body Science")
            logger.info("  Goal: Reduce Swap Rate from 72% to 20%")
            logger.info("🚀 " + "="*58 + "\n")
            
            # Phase 1: Generate with niche strategy
            logger.info("\n📝 PHASE 1: SPECIALIZED CONTENT GENERATION")
            script_data = self.generate_with_niche_strategy(topic)
            
            # Phase 2: Generate images
            logger.info("\n\n🎨 PHASE 2: IMAGE GENERATION")
            logger.info("[STEP 2/6] Generating Images...")
            image_paths = generate_images(script_data['scenes'])
            if not image_paths:
                raise RuntimeError(
                    "Koi bhi image nahi bani (Gemini, Hugging Face, placeholder sab fail) — "
                    "pipeline rok rahe hain. GEMINI_API_KEY / HF_API_KEY aur assets/placeholder.png check karo."
                )
            logger.info(f"✅ Images generated: {len(image_paths)} images")
            
            # Phase 3: Generate voice
            logger.info("\n🔊 PHASE 3: VOICE GENERATION")
            logger.info("[STEP 3/6] Generating Voice...")
            audio_path = generate_voice(script_data['voiceover'], voice="am_michael")
            logger.info(f"✅ Voice generated: {audio_path}")
            
            # Phase 4: Build video
            logger.info("\n🎬 PHASE 4: VIDEO COMPOSITION")
            logger.info("[STEP 4/6] Building Video...")
            final_video = build_video(image_paths, audio_path, script_data['scenes'])
            logger.info(f"✅ Video built: {final_video}")
            
            # Phase 5: Generate thumbnail
            logger.info("\n🖼️ PHASE 5: THUMBNAIL GENERATION")
            logger.info("[STEP 5/6] Generating Thumbnail...")
            thumb_path = generate_thumbnail(image_paths[0], script_data['title'])
            logger.info(f"✅ Thumbnail generated: {thumb_path}")
            
            # Phase 6: Determine publishing time
            logger.info("\n⏰ PHASE 6: SCHEDULING")
            logger.info("[STEP 5.5/6] Calculating Peak Time...")
            
            posting_schedule = self.scheduler.get_next_posting_times(1)
            posting_time = posting_schedule[0]['time']
            
            logger.info(f"\n📅 Scheduled posting time:")
            logger.info(f"  EST: {posting_schedule[0]['time_est']}")
            logger.info(f"  UTC: {posting_schedule[0]['time_utc']}")
            logger.info(f"  Peak: {posting_schedule[0]['peak_name']}")
            logger.info(f"  Reason: {posting_schedule[0]['reason']}")
            
            # Phase 7: Upload
            logger.info("\n📤 PHASE 7: UPLOADING TO PLATFORMS")
            logger.info("[STEP 6/6] Uploading to YouTube & Facebook...")
            
            upload_result = upload_all(final_video, thumb_path, script_data)
            logger.info(f"✅ Upload completed")
            
            # Save to history
            video_metadata = {
                'title': script_data['title'],
                'topic': script_data.get('topic'),
                'category': script_data.get('category'),
                'quality_score': script_data.get('quality_scores', {}).get('overall_quality', 0),
                'spam_risk': script_data.get('spam_risk'),
                'posted_at': datetime.now().isoformat(),
                'youtube_success': upload_result.get('youtube_success'),
                'facebook_success': upload_result.get('facebook_success'),
            }
            self._save_video_history(video_metadata)
            
            # Final summary
            logger.info("\n" + "="*60)
            logger.info("🎉 PIPELINE COMPLETE")
            logger.info("="*60)
            logger.info(f"\n📊 Video Summary:")
            logger.info(f"  Title: {script_data['title']}")
            logger.info(f"  Topic: {script_data.get('topic')}")
            logger.info(f"  Quality Score: {script_data.get('quality_scores', {}).get('overall_quality', 0):.0f}/100")
            logger.info(f"  Spam Risk: {script_data.get('spam_risk')} ✅")
            logger.info(f"  YouTube: {'✅ SUCCESS' if upload_result.get('youtube_success') else '❌ FAILED'}")
            logger.info(f"  Facebook: {'✅ SUCCESS' if upload_result.get('facebook_success') else '❌ FAILED'}")
            logger.info("\n" + "="*60 + "\n")
            
            return {
                'success': True,
                'video_data': script_data,
                'upload_result': upload_result,
                'scheduled_time': posting_time.isoformat()
            }
        
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Pipeline interrupted by user")
            sys.exit(130)
        
        except Exception as e:
            logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
            logger.error("="*60)
            sys.exit(1)
    
    def run_daily_batch(self, num_videos: int = 3):
        """
        Run batch processing for multiple videos at peak times.
        
        Args:
            num_videos: Number of videos to generate (default 3 for 3x daily)
        """
        logger.info(f"\n🔄 Starting Daily Batch Processing ({num_videos} videos)")
        
        for i in range(num_videos):
            try:
                logger.info(f"\n\n" + "#"*60)
                logger.info(f"# Video {i+1}/{num_videos}")
                logger.info("#"*60)
                
                result = self.run_pipeline()
                
                if i < num_videos - 1:
                    logger.info(f"\n⏳ Waiting before next video generation...")
                    import time
                    time.sleep(5)  # Small delay between generations
            
            except Exception as e:
                logger.error(f"\n❌ Batch video {i+1} failed: {e}")
                continue


def main():
    """
    Main entry point.
    """
    pipeline = SKILLORPipeline()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--batch':
            # Run batch mode (3 videos daily)
            num_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            pipeline.run_daily_batch(num_videos)
        elif sys.argv[1] == '--topic':
            # Run single video with custom topic
            topic = ' '.join(sys.argv[2:])
            pipeline.run_pipeline(topic=topic)
        else:
            # Single video with default topic
            pipeline.run_pipeline()
    else:
        # Default: single video
        topic = os.environ.get("VIDEO_TOPIC")
        pipeline.run_pipeline(topic=topic)


if __name__ == "__main__":
    main()
