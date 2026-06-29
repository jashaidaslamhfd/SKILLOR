"""
Content Generator — USA 2026 Viral Formula
Handles LLM script generation, title variations, and thumbnail keywords via Groq API.
"""

import os
import re
import json
import logging
from typing import List, Dict, Optional

# FIX: Import API_KEYS from settings to access credentials
from config.settings import API_KEYS

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from core.hook_engine import HookEngine
except ImportError:
    HookEngine = None

try:
    import prompts
except ImportError:
    prompts = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentGenerator:
    """Production Content Generator — USA 2026"""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        
        # 🥇 FIX: Load GROQ key securely from config settings API_KEYS
        self.groq_api_key = API_KEYS.GROQ_API_KEY
        
        if not self.groq_api_key:
            logger.error("❌ GROQ_API_KEY is not set in environment or config.")
            # Fallback to direct env check just in case
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            
        if Groq and self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
        else:
            self.client = None
            if not Groq:
                logger.warning("⚠️ Groq library not installed.")
            if not self.groq_api_key:
                logger.warning("⚠️ Groq API key is missing.")

        # 🥇 FIX: Pass the loaded API key directly to HookEngine
        if HookEngine:
            self.hook_engine = HookEngine(use_cache=False, api_key=self.groq_api_key)
        else:
            self.hook_engine = None

    def _call_groq(self, prompt: str, temperature: float = 0.7) -> str:
        """Helper to call Groq LLM API with exception handling."""
        if not self.client:
            logger.error("❌ Groq client not initialized. Check API keys.")
            raise ValueError("Groq client not initialized.")
            
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=temperature,
                max_tokens=2048
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {e}")
            raise e

    def generate_script(self, topic: str) -> Dict:
        """Generate full script based on the USA 2026 viral formula format."""
        logger.info(f"📝 Generating script for topic: {topic}")
        
        # Try hook engine first to get a validated hook
        hook_text = "Your body is doing something right now..."
        hook_score = 85
        if self.hook_engine:
            try:
                hook_res = self.hook_engine.generate_perfect_hook(topic)
                hook_text = hook_res.get('hook', hook_text)
                v_score = hook_res.get('validation')
                if v_score and hasattr(v_score, 'score'):
                    hook_score = v_score.score
            except Exception as e:
                logger.warning(f"⚠️ Hook engine fallback triggered: {e}")

        # Groq prompt template formatting
        prompt = f"""
Create a highly viral YouTube Short script (USA Audience 2026) about: {topic}

Use this exact structure:
1. Hook (1.5s): {hook_text}
2. Shock Moment (surprising scientific statement)
3. Suspense/Educational Story (why it happens to the body)
4. Call to Action (like, comment, share)

CRITICAL RULES:
- Casual, confident, authoritative American English.
- Do not mention age or gender.
- Total length must be 42-55 seconds (approx. 115-135 words).
- Output valid JSON format keys: 'hook', 'shock', 'suspense', 'story', 'ctr', 'full_script', 'segments'.
"""
        response_text = self._call_groq(prompt, temperature=0.6)
        
        # Clean up Markdown formatting from LLM responses if present
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            script_data = json.loads(clean_json)
        except json.JSONDecodeError:
            logger.warning("⚠️ LLM response was not valid JSON, parsing basic text blocks.")
            script_data = self._parse_text_fallback(response_text, hook_text)

        # Append additional execution metadata
        script_data['hook_score'] = hook_score / 10.0
        script_data['word_count'] = len(script_data.get('full_script', '').split())
        return script_data

    def _parse_text_fallback(self, text: str, hook: str) -> Dict:
        """Fallback parser if LLM fails to return pure JSON structure."""
        segments = [
            {'type': 'hook', 'text': hook, 'duration': 2.5},
            {'type': 'shock', 'text': "Let's uncover why this occurs.", 'duration': 3.0},
            {'type': 'story', 'text': text[:100], 'duration': 35.0},
            {'type': 'ctr', 'text': "Subscribe for daily science facts.", 'duration': 2.5}
        ]
        return {
            'hook': hook,
            'shock': "Shock moment placeholder",
            'suspense': "Suspense detail placeholder",
            'story': text,
            'ctr': "Subscribe for more",
            'full_script': text,
            'segments': segments
        }

    def generate_title(self, topic: str) -> str:
        """Generate click-through-rate (CTR) optimized title for YouTube."""
        logger.info(f"🎯 Generating title for topic: {topic}")
        prompt = f"Write a CTR optimized, viral YouTube Shorts title for: '{topic}'. Max 50 chars. Curios/Urgency style."
        return self._call_groq(prompt, temperature=0.7).replace('"', '').strip()

    def generate_thumbnail_words(self, topic: str) -> List[str]:
        """Extract high impact thumbnail keywords."""
        logger.info(f"🖼️ Generating thumbnail words for: {topic}")
        prompt = f"Extract 2-4 punchy, emotional/curiosity words for a thumbnail for topic: '{topic}'. Return as comma-separated list."
        res = self._call_groq(prompt, temperature=0.5)
        return [w.strip() for w in res.split(',')]

    def format_script_segments(self, script_data: Dict) -> List[Dict]:
        """Convert a standard script into timed cinematic segments."""
        segments = []
        full_text = script_data.get('full_script', '')
        # Basic parsing logic
        sentences = re.split(r'[.?!]', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_time = 0.0
        for s in sentences:
            duration = max(1.5, len(s.split()) * 0.38) # WPM scale
            segments.append({
                'text': s,
                'start': current_time,
                'duration': duration,
                'type': 'educational'
            })
            current_time += duration
        return segments


# ============================================================
# EXECUTION TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 TESTING CONTENT GENERATOR (USA 2026)\n" + "=" * 60)
    
    generator = ContentGenerator()
    test_topic = "why your body jerks before sleep"
    
    print(f"\n📝 Testing script generation for: '{test_topic}'")
    script = generator.generate_script(test_topic)
    
    print("\n✅ Script Result:")
    print(f"   Hook: {script.get('hook')}")
    print(f"   Word Count: {script.get('word_count')}")
    
    print(f"\n🎯 Title: {generator.generate_title(test_topic)}")
    print(f"🖼️ Thumb words: {generator.generate_thumbnail_words(test_topic)}")
