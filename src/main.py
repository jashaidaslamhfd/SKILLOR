import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from script_generator import generate_script
# Import fixed: yahan se hum _generate_one ko as generate_images import kar rahe hain
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
        specialized_prompt = get_script_prompt_for_niche(topic)
        script_data = generate_script(topic, custom_prompt=specialized_prompt)
        
        med_check = validate_script_for_medical_accuracy(script_data)
        if not med_check['valid']:
            script_data = auto_add_disclaimer(script_data)
            
        quality_result = self.quality_checker.check_script_quality(script_data)
        spam_result = self.anti_spam.check_for_spam_risks(script_data, self.video_history)
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
        fixed_topic = topic
        best_attempt = None
        for attempt in range(1, MAX_SCRIPT_ATTEMPTS + 1):
            current_topic = fixed_topic or get_random_topic()
            try:
                result = self._generate_and_check_once(current_topic)
            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")
                continue
            if best_attempt is None or result['quality_score'] > best_attempt['quality_score']:
                best_attempt = result
            if result['quality_approved'] and result['spam_ok']:
                return result['script_data']
        return best_attempt['script_data']

    def run_pipeline(self, topic: str = None) -> dict:
        logger.info("\n🚀 STARTING SKILLOR PIPELINE")
        script_data = self.generate_with_niche_strategy(topic)

        # --- FIX: IMAGE GENERATION LOOP ---
        logger.info("\n🎨 PHASE 2: IMAGE GENERATION")
        image_paths = []
        used_hashes = set()
        used_fallbacks = set()

        for i, scene in enumerate(script_data['scenes']):
            try:
                # generate_images ab loop mein sahi arguments le raha hai
                res = generate_images(i, scene, used_hashes, used_fallbacks)
                image_paths.append(res['path'])
            except Exception as e:
                logger.error(f"Scene {i} image failed: {e}")

        # --- VOICE & VIDEO ---
        audio_segments = generate_voice_segments(script_data['scenes'], voice="am_michael")
        final_video = build_video(image_paths, audio_segments, script_data['scenes'])
        thumb_path = generate_thumbnail(image_paths[0], script_data['title'])
        
        upload_result = upload_all(final_video, thumb_path, script_data)
        self._save_video_history({'title': script_data['title'], 'posted_at': datetime.now().isoformat()})
        
        return {'success': True}

    def run_daily_batch(self, num_videos: int = 3):
        for i in range(num_videos):
            self.run_pipeline()
            if i < num_videos - 1: time.sleep(5)

def main():
    pipeline = SKILLORPipeline()
    topic = os.environ.get("VIDEO_TOPIC")
    pipeline.run_pipeline(topic=topic)

if __name__ == "__main__":
    main()
