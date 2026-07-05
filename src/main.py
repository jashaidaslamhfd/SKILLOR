import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from script_generator import generate_script
from image_generator import _generate_one as generate_images
from voice_generator import generate_voice_segments
from video_editor import build_video, generate_thumbnail
from uploader import upload_all
from niche_strategy import (
    get_script_prompt_for_niche, get_random_topic, get_topic_category,
    generate_seo_tags, validate_script_for_medical_accuracy, auto_add_disclaimer,
)
from quality_checker import QualityChecker
from scheduler import USAPeakTimeScheduler
from anti_spam import AntiSpamSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_SCRIPT_ATTEMPTS = 3

class SKILLORPipeline:
    def __init__(self):
        self.quality_checker = QualityChecker()
        self.scheduler = USAPeakTimeScheduler()
        self.anti_spam = AntiSpamSystem()
        self.video_history = self._load_video_history()

    def _load_video_history(self) -> list:
        history_file = "output/video_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_video_history(self, video_data: dict):
        os.makedirs("output", exist_ok=True)
        self.video_history.append(video_data)
        if len(self.video_history) > 50:
            self.video_history = self.video_history[-50:]
        with open("output/video_history.json", 'w') as f:
            json.dump(self.video_history, f, indent=2)

    def _generate_and_check_once(self, topic: str) -> dict:
        category = get_topic_category(topic)
        specialized_prompt = get_script_prompt_for_niche(topic) # Ab Dark prompt aayega
        script_data = generate_script(topic, custom_prompt=specialized_prompt)

        med_check = validate_script_for_medical_accuracy(script_data)
        if not med_check['valid']:
            script_data = auto_add_disclaimer(script_data) # Medical disclaimer auto lag jayega

        quality_result = self.quality_checker.check_script_quality(script_data)
        spam_result = self.anti_spam.check_for_spam_risks(script_data, self.video_history)
        tags = generate_seo_tags(topic, category, script_data.get('title', '')) # SEO har video ka alag

        script_data['topic'] = topic
        script_data['category'] = category
        script_data['quality_scores'] = quality_result['scores']
        script_data['spam_risk'] = spam_result['spam_risk_level']
        script_data['tags'] = tags # Tags upload me use honge

        return {
            "script_data": script_data,
            "quality_approved": quality_result['approved'],
            "quality_score": quality_result['scores'].get('overall_quality', 0),
            "spam_ok": spam_result['spam_risk_level'] not in ['CRITICAL', 'HIGH'],
            "spam_level": spam_result['spam_risk_level'],
        }

    def generate_with_niche_strategy(self, topic: str = None) -> dict:
        fixed_topic = topic
        best_attempt = None
        last_error = None
        for attempt in range(1, MAX_SCRIPT_ATTEMPTS + 1):
            current_topic = fixed_topic or get_random_topic() # Dark topics list se
            try:
                result = self._generate_and_check_once(current_topic)
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt} failed: {e}")
                continue
            if best_attempt is None or result['quality_score'] > best_attempt['quality_score']:
                best_attempt = result
            if result['quality_approved'] and result['spam_ok']:
                return result['script_data']

        if best_attempt is None:
            raise RuntimeError(
                f"All {MAX_SCRIPT_ATTEMPTS} script-generation attempts failed - "
                f"last error: {last_error}"
            )
        return best_attempt['script_data']

    def run_pipeline(self, topic: str = None) -> dict:
        logger.info("\n🚀 STARTING SKILLOR - DARK BODY MYSTERY PIPELINE")

        # Scheduler was being instantiated but never actually used - wire it
        # in for its two genuinely useful bits: warn if we're posting too
        # soon after the last video (spam-flag risk), and log which peak
        # slot this run falls into (informational - GitHub Actions cron
        # controls the actual trigger time, this doesn't block anything).
        if self.video_history:
            last_posted_at = self.video_history[-1].get('posted_at')
            if last_posted_at:
                try:
                    last_dt = datetime.fromisoformat(last_posted_at)
                    if not self.scheduler.validate_posting_interval(last_dt):
                        logger.warning("Posting sooner than the recommended 2h gap since the last video - proceeding anyway, but keep an eye on spam flags.")
                except Exception as e:
                    logger.warning(f"Could not validate posting interval: {e}")

        script_data = self.generate_with_niche_strategy(topic)

        logger.info("\n🎨 PHASE 2: IMAGE GENERATION")
        image_paths = []
        used_hashes = set()
        used_fallbacks = set()

        for i, scene in enumerate(script_data['scenes']):
            try:
                res = generate_images(i, scene, used_hashes, used_fallbacks)
                image_paths.append(res['path'])
            except Exception as e:
                logger.error(f"Scene {i} image failed: {e}")

        logger.info("\n🔊 PHASE 3: VOICE GENERATION - DARK MALE")
        # CRITICAL CHANGE: am_adam + slow speed
        audio_segments = generate_voice_segments(script_data['scenes'], voice="am_adam", speed=0.95)

        logger.info("\n🎬 PHASE 4: BUILD VIDEO")
        final_video = build_video(image_paths, audio_segments, script_data['scenes'])
        thumb_path = generate_thumbnail(image_paths[0], script_data['title'])

        logger.info("\n📤 PHASE 5: UPLOAD WITH SEO TAGS")
        upload_result = upload_all(final_video, thumb_path, script_data) # tags auto jayenge
        self._save_video_history({'title': script_data['title'], 'posted_at': datetime.now(timezone.utc).isoformat()})

        logger.info(f"\n✅ DONE: {script_data['title']}")
        return {'success': True}

    def run_daily_batch(self, num_videos: int = 3):
        for i in range(num_videos):
            self.run_pipeline()
            if i < num_videos - 1: time.sleep(300) # 5 min gap

def main():
    pipeline = SKILLORPipeline()
    topic = os.environ.get("VIDEO_TOPIC") # Agar specific topic dena ho
    pipeline.run_pipeline(topic=topic)

if __name__ == "__main__":
    main()
