import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from script_generator import generate_script
from image_generator import generate_images
from voice_generator import generate_voice_segments          # FIX: was generate_voice (single-file)
from video_editor import build_video, generate_thumbnail
from uploader import upload_all
from niche_strategy import (
    get_script_prompt_for_niche, get_random_topic, get_topic_category,
    generate_seo_tags, validate_script_for_medical_accuracy, auto_add_disclaimer,  # FIX: now actually used
)
from quality_checker import QualityChecker
from scheduler import USAPeakTimeScheduler
from anti_spam import AntiSpamSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MAX_SCRIPT_ATTEMPTS = 3  # retry script generation this many times if quality/spam checks fail


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
            except Exception:
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

    def _generate_and_check_once(self, topic: str) -> dict:
        """One attempt: generate script, run medical/quality/spam checks."""
        category = get_topic_category(topic)
        specialized_prompt = get_script_prompt_for_niche(topic)

        logger.info("\n[STEP 1/6] Generating Specialized Script...")
        script_data = generate_script(topic, custom_prompt=specialized_prompt)

        # --- Medical accuracy / disclaimer check (FIX: was defined but never
        # called anywhere in the pipeline) ---
        med_check = validate_script_for_medical_accuracy(script_data)
        if not med_check['valid']:
            logger.warning(f"⚠️ Medical accuracy issue(s): {med_check['issues']} - auto-adding disclaimer scene")
            script_data = auto_add_disclaimer(script_data)
            med_check = validate_script_for_medical_accuracy(script_data)
            if not med_check['valid']:
                logger.warning(f"⚠️ Still flagged after disclaimer: {med_check['issues']}")
        for w in med_check['warnings']:
            logger.warning(f"  {w}")

        # --- Quality check ---
        logger.info("\n[STEP 1.5/6] Running Quality Checks...")
        quality_result = self.quality_checker.check_script_quality(script_data)

        logger.info("\n📊 Quality Scores:")
        logger.info(f"  Hook Score: {quality_result['scores'].get('hook_score', 0)}/100")
        logger.info(f"  Engagement Score: {quality_result['scores'].get('engagement_score', 0)}/100")
        logger.info(f"  Pacing Score: {quality_result['scores'].get('pacing_score', 0)}/100")
        logger.info(f"  Overall Quality: {quality_result['scores'].get('overall_quality', 0):.0f}/100")
        logger.info(f"  Status: {quality_result['recommendation']}")

        # --- Anti-spam check ---
        logger.info("\n[STEP 1.75/6] Running Anti-Spam Analysis...")
        spam_result = self.anti_spam.check_for_spam_risks(script_data, self.video_history)

        logger.info("\n🛡️ Anti-Spam Results:")
        logger.info(f"  Spam Risk: {spam_result['spam_risk_level']}")
        logger.info(f"  Recommendation: {spam_result['recommendation']}")
        for risk in spam_result['risks']:
            logger.warning(f"  {risk}")

        # --- SEO tags (FIX: previously no dynamic tags existed at all) ---
        tags = generate_seo_tags(topic, category, script_data.get('title', ''))

        script_data['topic'] = topic
        script_data['category'] = category
        script_data['quality_scores'] = quality_result['scores']
        script_data['spam_risk'] = spam_result['spam_risk_level']
        script_data['tags'] = tags

        return {
            "script_data": script_data,
            "quality_approved": quality_result['approved'],
            "quality_score": quality_result['scores'].get('overall_quality', 0),
            "spam_ok": spam_result['spam_risk_level'] not in ['CRITICAL', 'HIGH'],
            "spam_level": spam_result['spam_risk_level'],
        }

    def generate_with_niche_strategy(self, topic: str = None) -> dict:
        """
        Generate video script using specialized parenting niche strategy,
        retrying up to MAX_SCRIPT_ATTEMPTS times if quality/spam checks fail
        (FIX: previously it only logged a warning and proceeded anyway with
        no real retry - the "Generating improved version..." log line lied).
        """
        fixed_topic = topic
        best_attempt = None

        for attempt in range(1, MAX_SCRIPT_ATTEMPTS + 1):
            current_topic = fixed_topic or get_random_topic()
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 Attempt {attempt}/{MAX_SCRIPT_ATTEMPTS} - Topic: {current_topic}")
            logger.info(f"{'='*60}")

            try:
                result = self._generate_and_check_once(current_topic)
            except Exception as e:
                logger.error(f"❌ Script generation attempt {attempt} failed: {e}", exc_info=True)
                continue

            if best_attempt is None or result['quality_score'] > best_attempt['quality_score']:
                best_attempt = result

            if result['quality_approved'] and result['spam_ok']:
                logger.info(f"✅ Script approved on attempt {attempt}")
                return result['script_data']

            logger.warning(
                f"⚠️ Attempt {attempt} not approved "
                f"(quality={result['quality_score']:.0f}, spam={result['spam_level']}) - retrying..."
            )

        if best_attempt is None:
            raise RuntimeError("All script generation attempts failed outright")

        if not best_attempt['spam_ok']:
            # Never publish something the anti-spam system flagged as
            # CRITICAL/HIGH risk, even as a "best effort" fallback.
            raise RuntimeError(
                f"Spam risk too high after {MAX_SCRIPT_ATTEMPTS} attempts: {best_attempt['spam_level']}"
            )

        logger.warning(
            f"⚠️ Proceeding with best attempt after {MAX_SCRIPT_ATTEMPTS} tries "
            f"(quality={best_attempt['quality_score']:.0f}/100, not fully approved)"
        )
        return best_attempt['script_data']

    def run_pipeline(self, topic: str = None, schedule_publish: bool = True) -> dict:
        """
        Run complete pipeline with all optimizations.

        FIX (critical): this used to call sys.exit(1) on any failure, which
        raises SystemExit - a BaseException that `except Exception` in
        run_daily_batch() does NOT catch. That meant one failed video in a
        --batch run silently killed the ENTIRE remaining batch instead of
        continuing to the next video. Now this raises a normal exception and
        lets the caller decide what to do.
        """
        logger.info("\n" + "🚀 " + "="*58)
        logger.info("  SKILLOR - Advanced YouTube Shorts Pipeline v5.2")
        logger.info("  Target: USA Parents - Brain & Body Science")
        logger.info("  Goal: Reduce Swap Rate from 72% to 20%")
        logger.info("🚀 " + "="*58 + "\n")

        # Phase 1: Generate with niche strategy (script + quality + spam + SEO tags)
        logger.info("\n📝 PHASE 1: SPECIALIZED CONTENT GENERATION")
        script_data = self.generate_with_niche_strategy(topic)

        # Phase 2: Generate images
        logger.info("\n\n🎨 PHASE 2: IMAGE GENERATION")
        logger.info("[STEP 2/6] Generating Images...")
        image_paths = generate_images(script_data['scenes'])
        if not image_paths:
            raise RuntimeError(
                "Koi bhi image nahi bani (sab AI providers + fallback pool bhi fail) — "
                "pipeline rok rahe hain. API keys aur assets/fallback_images/ / assets/placeholder.png check karo."
            )
        if len(image_paths) < len(script_data['scenes']):
            logger.warning(
                f"⚠️ Only {len(image_paths)}/{len(script_data['scenes'])} scene images generated - "
                f"video will be built with the available images."
            )
        logger.info(f"✅ Images generated: {len(image_paths)} images")

        # Phase 3: Generate voice — ONE SEGMENT PER SCENE
        # FIX (critical crash bug): this used to call generate_voice() which
        # returns a single combined audio file PATH (a string), then passed
        # that string straight into build_video() where a list of per-scene
        # {"path","duration","caption"} dicts was required. That mismatch
        # broke voice/caption/clip sync and crashed the video build step on
        # every run. Now correctly calls generate_voice_segments().
        logger.info("\n🔊 PHASE 3: VOICE GENERATION")
        logger.info("[STEP 3/6] Generating Voice Segments (per scene)...")
        audio_segments = generate_voice_segments(script_data['scenes'], voice="am_michael")
        if len(audio_segments) != len(image_paths):
            # Keep them aligned in case an image layer skipped a scene entirely.
            min_len = min(len(audio_segments), len(image_paths), len(script_data['scenes']))
            logger.warning(f"⚠️ Trimming to {min_len} scenes to keep images/audio/captions aligned")
            audio_segments = audio_segments[:min_len]
            image_paths = image_paths[:min_len]
            script_data['scenes'] = script_data['scenes'][:min_len]
        logger.info(f"✅ Voice segments generated: {len(audio_segments)} segments")

        # Phase 4: Build video
        logger.info("\n🎬 PHASE 4: VIDEO COMPOSITION")
        logger.info("[STEP 4/6] Building Video...")
        final_video = build_video(image_paths, audio_segments, script_data['scenes'])
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

        logger.info("\n📅 Scheduled posting time:")
        logger.info(f"  EST: {posting_schedule[0]['time_est']}")
        logger.info(f"  UTC: {posting_schedule[0]['time_utc']}")
        logger.info(f"  Peak: {posting_schedule[0]['peak_name']}")
        logger.info(f"  Reason: {posting_schedule[0]['reason']}")

        # Phase 7: Upload
        logger.info("\n📤 PHASE 7: UPLOADING TO PLATFORMS")
        logger.info("[STEP 6/6] Uploading to YouTube & Facebook Reels...")

        upload_result = upload_all(final_video, thumb_path, script_data)
        logger.info("✅ Upload completed")

        # Save to history
        video_metadata = {
            'title': script_data['title'],
            'topic': script_data.get('topic'),
            'category': script_data.get('category'),
            'quality_score': script_data.get('quality_scores', {}).get('overall_quality', 0),
            'spam_risk': script_data.get('spam_risk'),
            'tags': script_data.get('tags'),
            'posted_at': datetime.now().isoformat(),
            'youtube_success': upload_result.get('youtube_success'),
            'facebook_success': upload_result.get('facebook_success'),
        }
        self._save_video_history(video_metadata)

        # Final summary
        logger.info("\n" + "="*60)
        logger.info("🎉 PIPELINE COMPLETE")
        logger.info("="*60)
        logger.info("\n📊 Video Summary:")
        logger.info(f"  Title: {script_data['title']}")
        logger.info(f"  Topic: {script_data.get('topic')}")
        logger.info(f"  Quality Score: {script_data.get('quality_scores', {}).get('overall_quality', 0):.0f}/100")
        logger.info(f"  Spam Risk: {script_data.get('spam_risk')}")
        logger.info(f"  YouTube: {'✅ SUCCESS' if upload_result.get('youtube_success') else '❌ FAILED'}")
        logger.info(f"  Facebook: {'✅ SUCCESS' if upload_result.get('facebook_success') else '❌ FAILED'}")
        logger.info("\n" + "="*60 + "\n")

        return {
            'success': True,
            'video_data': script_data,
            'upload_result': upload_result,
            'scheduled_time': posting_time.isoformat()
        }

    def run_daily_batch(self, num_videos: int = 3):
        """
        Run batch processing for multiple videos at peak times.
        Now correctly continues to the next video if one fails, because
        run_pipeline() raises normal exceptions instead of calling sys.exit().
        """
        logger.info(f"\n🔄 Starting Daily Batch Processing ({num_videos} videos)")
        results = []

        for i in range(num_videos):
            logger.info("\n\n" + "#"*60)
            logger.info(f"# Video {i+1}/{num_videos}")
            logger.info("#"*60)

            try:
                result = self.run_pipeline()
                results.append({"index": i + 1, "success": True, "result": result})
            except Exception as e:
                logger.error(f"❌ Batch video {i+1} failed: {e}", exc_info=True)
                results.append({"index": i + 1, "success": False, "error": str(e)})

            if i < num_videos - 1:
                logger.info("\n⏳ Waiting before next video generation...")
                import time
                time.sleep(5)

        succeeded = sum(1 for r in results if r["success"])
        logger.info(f"\n📦 Batch complete: {succeeded}/{num_videos} videos succeeded")
        return results


def main():
    """Main entry point."""
    pipeline = SKILLORPipeline()

    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == '--batch':
                num_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 3
                results = pipeline.run_daily_batch(num_videos)
                if not any(r["success"] for r in results):
                    sys.exit(1)
            elif sys.argv[1] == '--topic':
                topic = ' '.join(sys.argv[2:])
                pipeline.run_pipeline(topic=topic)
            else:
                pipeline.run_pipeline()
        else:
            topic = os.environ.get("VIDEO_TOPIC")
            pipeline.run_pipeline(topic=topic)

    except KeyboardInterrupt:
        logger.warning("\n⚠️ Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
