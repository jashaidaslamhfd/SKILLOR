import re
import time
import json
import logging
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    Groq = None

# ============================================================
# CONSTANTS & SETTINGS (Separation of Concerns)
# ============================================================
MODEL_NAME = "llama-3.3-70b-versatile"

MODERN_OPENERS = [
    "Your body is ALREADY",
    "Nobody ever explains why your body",
    "This is why YOU keep experiencing",
    "The real reason behind",
    "You've felt this your whole life"
]

PROMPT_TEMPLATES = [
    """Write 5 DIFFERENT modern hooks for this topic: {topic}
RULES: Statements only, use "you/your", urgency, 8-10 words, end with "...". No age/gender.""",
    """Write 5 PUNCHY curiosity hooks for this topic: {topic}
RULES: High mystery statement, use "you/your", urgency, 8-10 words, end with "...". No age/gender.""",
    """Write 5 CONTRAERIAN hooks for this topic: {topic}
RULES: Bust a myth, use "you/your", urgency, 8-10 words, end with "...". No age/gender."""
]

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hook_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HookValidationResult:
    hook: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    word_count: int = 0
    score: int = 0
    ai_feedback: Dict = field(default_factory=dict)


class HookEngine:
    def __init__(self, use_cache: bool = False, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = MODEL_NAME
        self.client = None
        self.max_attempts = 3
        self.use_cache = use_cache
        self._cache = {}
        self._cache_file = "hook_cache.json"
        self._used_hooks = set()
        self._history_file = "hook_history.json"
        
        if use_cache:
            self._load_cache()
        else:
            logger.info("⚠️ Cache disabled - generating fresh hooks every time")
        
        self._init_client()

    def _init_client(self):
        if not Groq or not self.api_key:
            logger.warning("⚠️ Groq client not configured or missing API key")
            return
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info("✅ Groq client initialized")
        except Exception as e:
            logger.error(f"❌ Groq init failed: {e}")
            self.client = None

    def _load_cache(self):
        try:
            if Path(self._cache_file).exists():
                with open(self._cache_file, 'r') as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded {len(self._cache)} cached hooks")
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
            self._cache = {}

    def _save_cache(self):
        if not self.use_cache:
            return
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    def _get_cached_hook(self, topic: str) -> Optional[str]:
        if not self.use_cache:
            return None
        cache_key = topic.lower().strip()
        cached = self._cache.get(cache_key)
        if cached and 'timestamp' in cached:
            age = time.time() - cached['timestamp']
            if age < 7 * 24 * 3600:
                logger.info(f"Cache hit for: {topic}")
                return cached['hook']
        return None

    def _cache_hook(self, topic: str, hook: str):
        if not self.use_cache:
            return
        cache_key = topic.lower().strip()
        self._cache[cache_key] = {
            'hook': hook,
            'timestamp': time.time(),
            'created': datetime.now().isoformat()
        }
        self._save_cache()

    def _call_groq(self, prompt: str, max_tokens: int = 250, json_mode: bool = False) -> str:
        if not self.client:
            logger.warning("⚠️ Groq client unavailable")
            return ""
        
        response_format = {"type": "json_object"} if json_mode else {"type": "text"}
        
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    timeout=30
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq error (attempt {attempt+1}): {e}")
                time.sleep(2)
        return ""

    def _sanitize_hook(self, text: str) -> str:
        """Priority 3: Aggressive string sanitization"""
        # Remove markdown/bullet symbols
        text = re.sub(r'[*#-]', '', text)
        # Remove numbering
        text = re.sub(r'^\d+\.\s*', '', text)
        # Remove quotes
        text = text.strip('"\'')
        # Fix Word count (force exactly 8-10 words by truncation if needed)
        words = text.split()
        if len(words) > 10:
            text = " ".join(words[:10])
        elif len(words) < 8 and not text.endswith("..."):
            text = text.rstrip('.') + "..."
            
        return text.strip()

    def _check_semantic_similarity(self, new_hook: str, threshold: float = 0.8) -> bool:
        """Priority 1: Simple Jaccard Similarity checker to prevent repetition"""
        new_words = set(new_hook.lower().split())
        for used in self._used_hooks:
            used_words = set(used.lower().split())
            if not new_words or not used_words:
                continue
            intersection = new_words.intersection(used_words)
            union = new_words.union(used_words)
            similarity = len(intersection) / len(union)
            if similarity >= threshold:
                return True # Too similar
        return False

    # ============================================================
    # FIX 1 & 2: AI-DRIVEN VALIDATION & WEIGHTED SCORING
    # ============================================================
    def validate_hook_ai(self, hook: str, topic: str) -> HookValidationResult:
        """Uses LLM to evaluate hook quality against 2026 YT metrics"""
        errors = []
        warnings = []
        
        prompt = f"""
Evaluate this YouTube Short hook for the topic: "{topic}"
Hook: "{hook}"

Analyze strictly on these rules and return a JSON output:
1. Curiosity (0-30 points): Does it make you want to keep watching?
2. Personalization (0-20 points): Uses "you" or "your"?
3. Emotion/Relatability (0-15 points): Does it touch on a human feeling?
4. Urgency (0-15 points): Uses words like 'already', 'right now', 'been'?
5. Length/Clarity (0-20 points): 8-10 words, ends with '...', not a question?

Return JSON format strictly:
{{
    "curiosity": int,
    "personalization": int,
    "emotion": int,
    "urgency": int,
    "length": int,
    "is_valid": boolean,
    "reason": "string describing issues if invalid"
}}
"""
        raw_ai = self._call_groq(prompt, max_tokens=200, json_mode=True)
        
        ai_score_data = {}
        try:
            ai_score_data = json.loads(raw_ai)
        except Exception:
            logger.warning("⚠️ AI evaluation JSON parsing failed, setting default fallback")
            ai_score_data = {"curiosity": 10, "personalization": 10, "emotion": 5, "urgency": 5, "length": 5, "is_valid": False, "reason": "Parsing failed"}
        
        total_score = sum([
            ai_score_data.get('curiosity', 0),
            ai_score_data.get('personalization', 0),
            ai_score_data.get('emotion', 0),
            ai_score_data.get('urgency', 0),
            ai_score_data.get('length', 0)
        ])
        
        # Determine logical check requirements
        is_valid = ai_score_data.get('is_valid', True) and (total_score >= 65)
        if not is_valid:
            errors.append(f"AI rejected: {ai_score_data.get('reason', 'Quality score too low')}")
            
        return HookValidationResult(
            hook=hook,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            word_count=len(hook.split()),
            score=total_score,
            ai_feedback=ai_score_data
        )

    # ============================================================
    # FIX 5: MULTI-AGENT ADAPTIVE RETRY
    # ============================================================
    def rewrite_hook_adaptive(self, invalid_hook: str, feedback: str, topic: str, attempt: int) -> str:
        """Applies contextual feedback depending on retry iteration"""
        instructions = {
            1: "Make the hook significantly shorter (strictly 8-10 words).",
            2: "Increase the curiosity gap. Ensure it hits universal emotion.",
            3: "Avoid generic phrases. Make it punchy and statement-based."
        }
        instruction = instructions.get(attempt, "Refine the hook completely based on 2026 YT standards.")
        
        prompt = f"""
Rewrite this failing hook. 
FAILED HOOK: "{invalid_hook}"
TOPIC: {topic}
PREVIOUS REASON: {feedback}

INSTRUCTION FOR THIS ATTEMPT: {instruction}

RULES: 
- 8 to 10 words.
- MUST end with "..."
- Statements ONLY (no questions).
- Use "you" or "your".

Return ONLY the raw rewritten hook string. No intro, no quotes.
"""
        raw = self._call_groq(prompt, max_tokens=50)
        return self._sanitize_hook(raw)

    def _generate_dynamic_fallback(self, topic: str) -> str:
        opener = random.choice(MODERN_OPENERS)
        return f"{opener} {topic} in a way you never knew..."

    # ============================================================
    # FIX 3: GENERATE PERFECT HOOK WITH RANDOMIZED PROMPTS
    # ============================================================
    def generate_perfect_hook(self, topic: str) -> Dict:
        if self.use_cache:
            cached = self._get_cached_hook(topic)
            if cached:
                validation = self.validate_hook_ai(cached, topic)
                return {'hook': cached, 'validation': validation, 'status': 'cached', 'attempts': 0}
        
        logger.info(f"🚀 Generating fresh hook for: {topic}")
        
        # Priority 1: Prompt Randomization
        template = random.choice(PROMPT_TEMPLATES)
        prompt = f"""{template.format(topic=topic)}
Openers to use/inspire from: {', '.join(MODERN_OPENERS)}
Return ONLY 5 hooks, one per line. No numbers, no symbols, no backticks.
"""
        raw = self._call_groq(prompt, max_tokens=300)
        hooks = [self._sanitize_hook(h) for h in raw.split('\n') if h.strip()]
        
        if not hooks:
            hooks = [self._generate_dynamic_fallback(topic)]

        for hook in hooks:
            # Priority 1: Similarity Detection
            if self._check_semantic_similarity(hook):
                logger.info(f"⏭️ Skipping semantically similar hook: '{hook}'")
                continue
                
            validation = self.validate_hook_ai(hook, topic)
            logger.info(f"🧪 Testing: '{hook}' → AI Score: {validation.score}/100")
            
            if validation.is_valid:
                logger.info(f"✅ PERFECT HOOK FOUND!")
                self._used_hooks.add(hook)
                self._save_hook_history(topic, hook, validation.score, "success")
                if self.use_cache:
                    self._cache_hook(topic, hook)
                return {'hook': hook, 'validation': validation, 'status': 'perfect', 'attempts': 1}
            
            # Adaptive Retries
            current_hook = hook
            for attempt in range(1, self.max_attempts):
                reason = validation.errors[0] if validation.errors else "Quality issue"
                rewritten = self.rewrite_hook_adaptive(current_hook, reason, topic, attempt)
                rewritten = self._sanitize_hook(rewritten)
                
                new_validation = self.validate_hook_ai(rewritten, topic)
                logger.info(f"🔄 Retry {attempt}: Score {new_validation.score}/100")
                
                if new_validation.is_valid:
                    logger.info(f"✅ CORRECTED after {attempt} attempts!")
                    self._used_hooks.add(rewritten)
                    self._save_hook_history(topic, rewritten, new_validation.score, "corrected")
                    if self.use_cache:
                        self._cache_hook(topic, rewritten)
                    return {'hook': rewritten, 'validation': new_validation, 'status': 'corrected', 'attempts': attempt + 1}
                
                current_hook = rewritten
                validation = new_validation

        logger.warning(f"⚠️ All correction attempts failed for {topic}, using dynamic fallback")
        fallback = self._generate_dynamic_fallback(topic)
        validation = self.validate_hook_ai(fallback, topic)
        self._used_hooks.add(fallback)
        self._save_hook_history(topic, fallback, validation.score, "fallback")
        
        return {'hook': fallback, 'validation': validation, 'status': 'fallback', 'attempts': self.max_attempts}

    # ============================================================
    # FIX 8: HOOK HISTORY LOGGING
    # ============================================================
    def _save_hook_history(self, topic: str, hook: str, score: int, status: str):
        record = {
            "topic": topic,
            "hook": hook,
            "date": datetime.now().isoformat(),
            "score": score,
            "status": status
        }
        try:
            history = []
            if Path(self._history_file).exists():
                with open(self._history_file, 'r') as f:
                    history = json.load(f)
            history.append(record)
            with open(self._history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save history: {e}")

    def get_cache_stats(self) -> Dict:
        return {
            'cached_hooks': len(self._cache),
            'cache_enabled': self.use_cache,
            'used_hooks_count': len(self._used_hooks)
        }

# ============================================================
# EXECUTION TEST
# ============================================================
if __name__ == "__main__":
    print("🚀 INITIALIZING ADVANCED HOOK ENGINE TESTING\n" + "="*60)
    
    # Kripya apna real GROQ API Key yahan paste karein
    YOUR_GROQ_API_KEY = "gsk_..." 
    
    engine = HookEngine(use_cache=False, api_key=YOUR_GROQ_API_KEY)
    
    topics = [
        "why your body jerks before sleep", 
        "why a song gets stuck in your head"
    ]
    
    for topic in topics:
        print(f"\n📝 Processing Topic: {topic}")
        result = engine.generate_perfect_hook(topic)
        print(f"👉 Final Hook: '{result['hook']}'")
        print(f"📈 Total AI Score: {result['validation'].score}/100")
        print(f"📊 AI Breakdown: {json.dumps(result['validation'].ai_feedback, indent=2)}")
        print(f"🏷️ Status: {result['status']} | Attempts: {result['attempts']}")
        time.sleep(2)

    print("\n✅ Hook Engine refactoring & testing complete!")
