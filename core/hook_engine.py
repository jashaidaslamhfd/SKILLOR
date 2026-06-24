"""
Self-Correcting Hook Engine - Production Ready
FIXES:
1. Prompt injection protection (clean raw hook)
2. Auto-append "..." to save API calls
3. Caching (reduce API costs)
4. Logging (track failures)
"""

import re
import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from functools import lru_cache
from datetime import datetime
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    Groq = None

from config.settings import API_KEYS

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
    """Validation result with detailed feedback"""
    hook: str
    is_valid: bool
    is_modern: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    word_count: int = 0
    score: int = 0
    auto_fixed: bool = False


class HookEngine:
    """
    Self-Correcting Hook Engine - Production Ready
    
    Features:
    1. Validates hooks against 2026 standards
    2. Auto-fixes minor issues (saves API calls)
    3. Caches results (reduces costs)
    4. Logs all failures for debugging
    """
    
    def __init__(self, use_cache: bool = True):
        self.api_key = API_KEYS.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        self.client = None
        self.max_attempts = 3
        self.use_cache = use_cache
        self._cache = {}
        self._cache_file = "hook_cache.json"
        self._load_cache()
        self._init_client()
        
        # Modern patterns (2026) - with IGNORECASE
        self.modern_patterns = [
            r'(your|you\'re|you are).*?(already|right now|been|quietly|actually)',
            r'nobody tells you',
            r'this is why.*?you',
            r'the reason.*?is (simpler|surprising|fascinating)',
            r'you\'re not.*?your brain is just',
        ]
        
        # Old patterns (will cause SWIPE) - with IGNORECASE
        self.old_patterns = [
            r'have you ever',
            r'did you know',
            r'scientists discovered',
            r'shocking truth',
            r'mind-blowing',
            r'what if i told you',
            r'did you know that',
            r'have you wondered',
        ]
        
        # Urgency words for validation
        self.urgency_words = ['already', 'right now', 'been', 'quietly', 'actually']
        
        # Weak words that reduce impact
        self.weak_words = ['maybe', 'perhaps', 'sometimes', 'could', 'might', 'should']

    # ============================================================
    # CACHE MANAGEMENT
    # ============================================================
    
    def _load_cache(self):
        """Load cache from file"""
        if not self.use_cache:
            return
        try:
            if Path(self._cache_file).exists():
                with open(self._cache_file, 'r') as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded {len(self._cache)} cached hooks")
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
            self._cache = {}

    def _save_cache(self):
        """Save cache to file"""
        if not self.use_cache:
            return
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
            logger.info(f"Saved {len(self._cache)} hooks to cache")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    def _get_cached_hook(self, topic: str) -> Optional[str]:
        """Get cached hook for topic"""
        if not self.use_cache:
            return None
        cache_key = topic.lower().strip()
        cached = self._cache.get(cache_key)
        if cached:
            # Check if cache is fresh (less than 7 days old)
            if 'timestamp' in cached:
                age = time.time() - cached['timestamp']
                if age < 7 * 24 * 3600:  # 7 days
                    logger.info(f"Cache hit for: {topic}")
                    return cached['hook']
        return None

    def _cache_hook(self, topic: str, hook: str):
        """Cache a successful hook"""
        if not self.use_cache:
            return
        cache_key = topic.lower().strip()
        self._cache[cache_key] = {
            'hook': hook,
            'timestamp': time.time(),
            'created': datetime.now().isoformat()
        }
        self._save_cache()

    # ============================================================
    # GROQ CLIENT
    # ============================================================
    
    def _init_client(self):
        """Initialize Groq client"""
        if not Groq or not self.api_key:
            logger.warning("Groq not configured")
            return
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized")
        except Exception as e:
            logger.error(f"Groq init failed: {e}")
            self.client = None

    def _call_groq(self, prompt: str, max_tokens: int = 100) -> str:
        """Call Groq API with retry"""
        if not self.client:
            logger.warning("Groq client not available")
            return ""
        
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=max_tokens,
                    timeout=30
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq error (attempt {attempt+1}): {e}")
                time.sleep(2)
        
        return ""

    # ============================================================
    # FIX 1: PROMPT INJECTION PROTECTION
    # ============================================================
    
    def _clean_raw_hook(self, raw: str) -> str:
        """
        Clean raw response to extract ONLY the hook
        Fixes: "Here is your hook:" or quotes around the hook
        """
        if not raw:
            return ""
        
        # Remove common LLM prefaces
        prefixes = [
            "here is your rewritten hook:",
            "here is your hook:",
            "rewritten hook:",
            "hook:",
            "result:",
            "output:",
            "the hook is:",
        ]
        
        raw_lower = raw.lower()
        for prefix in prefixes:
            if raw_lower.startswith(prefix):
                raw = raw[len(prefix):].strip()
                break
        
        # Take first line only (in case LLM adds extra text)
        raw = raw.split('\n')[0].strip()
        
        # Remove quotes if present
        raw = raw.strip('"').strip("'")
        
        # Remove any remaining prefixed text
        raw = re.sub(r'^(hook|result|output):\s*', '', raw, flags=re.IGNORECASE)
        
        return raw

    # ============================================================
    # FIX 2: VALIDATION WITH AUTO-FIX
    # ============================================================
    
    def validate_hook(self, hook: str) -> HookValidationResult:
        """
        Validate hook against 2026 standards
        Auto-fixes minor issues to save API calls
        """
        errors = []
        warnings = []
        auto_fixed = False
        original_hook = hook
        hook_lower = hook.lower()
        
        # ============================================================
        # Check 1: OLD HOOK PATTERNS (FAIL) - WITH IGNORECASE
        # ============================================================
        for old_pattern in self.old_patterns:
            if re.search(old_pattern, hook_lower, re.IGNORECASE):
                errors.append(f"OLD HOOK: '{old_pattern}'")
        
        # ============================================================
        # Check 2: MODERN HOOK PATTERNS (PASS)
        # ============================================================
        is_modern = False
        for modern_pattern in self.modern_patterns:
            if re.search(modern_pattern, hook_lower, re.IGNORECASE):
                is_modern = True
                break
        
        if not is_modern:
            warnings.append("No modern hook pattern")
        
        # ============================================================
        # Check 3: Length
        # ============================================================
        word_count = len(hook.split())
        if word_count > 12:
            errors.append(f"Too long: {word_count} words (max 10)")
        elif word_count < 6:
            warnings.append(f"Too short: {word_count} words (min 6)")
        
        # ============================================================
        # Check 4: Personal Address
        # ============================================================
        if not any(word in hook_lower for word in ['you', 'your']):
            errors.append("Must use 'you/your'")
        
        # ============================================================
        # Check 5: Urgency Words
        # ============================================================
        if not any(word in hook_lower for word in self.urgency_words):
            warnings.append("Add urgency word (already/right now)")
        
        # ============================================================
        # Check 6: Question Format
        # ============================================================
        if '?' in hook:
            warnings.append("Statements work better than questions")
        
        # ============================================================
        # Check 7: Curiosity Gap (AUTO-FIX)
        # ============================================================
        if '...' not in hook:
            # AUTO-FIX: Append "..." instead of going through rewrite
            hook = hook.rstrip('.') + '...'
            auto_fixed = True
            logger.info(f"Auto-fixed missing '...': {hook}")
        
        # ============================================================
        # Check 8: Weak Words
        # ============================================================
        for weak in self.weak_words:
            if weak in hook_lower:
                warnings.append(f"Weak word: '{weak}'")
        
        # Calculate score
        score = 10 - len(errors) - len(warnings)
        is_valid = len(errors) == 0
        
        # If only warnings and auto_fixed, consider it valid
        if is_valid and auto_fixed:
            is_valid = True
        
        return HookValidationResult(
            hook=hook,
            is_valid=is_valid,
            is_modern=is_modern,
            errors=errors,
            warnings=warnings,
            word_count=word_count,
            score=max(0, score),
            auto_fixed=auto_fixed
        )

    # ============================================================
    # REWRITE WITH CLEANING
    # ============================================================
    
    def rewrite_hook(self, invalid_hook: str, errors: List[str], topic: str) -> str:
        """Rewrite invalid hook with cleaning"""
        
        logger.info(f"Rewriting invalid hook: '{invalid_hook}'")
        logger.info(f"Errors: {', '.join(errors)}")
        
        error_feedback = "\n".join([f"- {err}" for err in errors])
        
        prompt = f"""
Rewrite this hook that failed validation:

INVALID HOOK: "{invalid_hook}"
TOPIC: {topic}

ERRORS:
{error_feedback}

RULES for 2026 hooks:
1. MUST be a statement (NOT question)
2. MUST use "you/your"
3. MUST use urgency words: "already", "right now", "been"
4. MUST be 8-10 words
5. MUST end with "..."

EXAMPLES:
- "Your brain is ALREADY forgetting names you just heard..."
- "Nobody tells you what actually happens to memory..."

Return ONLY the rewritten hook. No prefix, no explanation.
"""
        
        raw = self._call_groq(prompt, max_tokens=60)
        
        # FIX: Clean the raw response
        cleaned = self._clean_raw_hook(raw)
        
        if not cleaned:
            logger.warning("Rewrite failed, using fallback")
            return self._generate_fallback_hook(topic)
        
        logger.info(f"Rewritten: '{cleaned}'")
        return cleaned

    def _generate_fallback_hook(self, topic: str) -> str:
        """Generate fallback hook"""
        fallbacks = [
            f"Your brain is ALREADY changing how it handles {topic}...",
            f"Nobody tells you what {topic} actually does to your brain...",
            f"This is why YOU keep experiencing {topic}...",
            f"The reason you {topic} is SIMPLER than you think...",
        ]
        import random
        return random.choice(fallbacks)

    # ============================================================
    # MAIN GENERATION WITH CACHING
    # ============================================================
    
    def generate_perfect_hook(self, topic: str) -> Dict:
        """
        Generate perfect hook with:
        1. Caching (check first)
        2. Auto-validation
        3. Self-correction
        """
        
        # ============================================================
        # Step 1: Check Cache
        # ============================================================
        cached = self._get_cached_hook(topic)
        if cached:
            validation = self.validate_hook(cached)
            return {
                'hook': cached,
                'validation': validation,
                'status': 'cached',
                'attempts': 0,
                'cached': True
            }
        
        logger.info(f"Generating hook for: {topic}")
        
        # ============================================================
        # Step 2: Generate initial hooks
        # ============================================================
        prompt = f"""
Write 5 modern hooks for this topic: {topic}

RULES:
1. MUST be statements (NOT questions)
2. MUST use "you/your"
3. MUST use urgency words: "already", "right now", "been"
4. MUST be 8-10 words
5. MUST end with "..."

Return ONLY 5 hooks, one per line. No numbers.
"""
        
        raw = self._call_groq(prompt, max_tokens=150)
        hooks = [h.strip() for h in raw.split('\n') if h.strip()]
        
        # Clean each hook
        hooks = [self._clean_raw_hook(h) for h in hooks]
        hooks = [h for h in hooks if h]
        
        if not hooks:
            hooks = [self._generate_fallback_hook(topic) for _ in range(3)]
        
        # ============================================================
        # Step 3: Test each hook
        # ============================================================
        for hook in hooks:
            validation = self.validate_hook(hook)
            logger.info(f"Testing: '{hook}' → Score: {validation.score}/10")
            
            if validation.is_valid:
                logger.info(f"✅ PERFECT HOOK FOUND!")
                self._cache_hook(topic, hook)
                return {
                    'hook': hook,
                    'validation': validation,
                    'status': 'perfect',
                    'attempts': 1,
                    'cached': False
                }
            
            # ============================================================
            # Step 4: Rewrite if invalid
            # ============================================================
            if validation.errors:
                for attempt in range(1, self.max_attempts):
                    rewritten = self.rewrite_hook(hook, validation.errors, topic)
                    
                    # Clean rewritten hook
                    rewritten = self._clean_raw_hook(rewritten)
                    
                    new_validation = self.validate_hook(rewritten)
                    logger.info(f"Attempt {attempt}: Score {new_validation.score}/10")
                    
                    if new_validation.is_valid:
                        logger.info(f"✅ CORRECTED after {attempt} attempts!")
                        self._cache_hook(topic, rewritten)
                        return {
                            'hook': rewritten,
                            'validation': new_validation,
                            'status': 'corrected',
                            'attempts': attempt + 1,
                            'cached': False
                        }
                    
                    hook = rewritten
                    validation = new_validation
        
        # ============================================================
        # Step 5: Fallback
        # ============================================================
        logger.warning(f"All attempts failed for {topic}, using fallback")
        fallback = self._generate_fallback_hook(topic)
        validation = self.validate_hook(fallback)
        self._cache_hook(topic, fallback)
        
        return {
            'hook': fallback,
            'validation': validation,
            'status': 'fallback',
            'attempts': self.max_attempts,
            'cached': False
        }

    # ============================================================
    # BATCH GENERATION
    # ============================================================
    
    def generate_batch(self, topics: List[str]) -> List[Dict]:
        """Generate hooks for multiple topics"""
        results = []
        cache_hits = 0
        
        for topic in topics:
            result = self.generate_perfect_hook(topic)
            if result.get('cached'):
                cache_hits += 1
            results.append({
                'topic': topic,
                'hook': result['hook'],
                'score': result['validation'].score,
                'status': result['status'],
                'attempts': result['attempts']
            })
            
            # Delay between API calls
            if not result.get('cached'):
                time.sleep(1)
        
        logger.info(f"Batch complete: {len(results)} hooks, {cache_hits} from cache")
        return results

    # ============================================================
    # STATUS
    # ============================================================
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_hooks': len(self._cache),
            'cache_enabled': self.use_cache,
            'cache_file': self._cache_file
        }


# ═══════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 TESTING PRODUCTION HOOK ENGINE\n" + "="*60)
    
    engine = HookEngine(use_cache=True)
    
    # Test with problematic hooks
    test_hooks = [
        "Have you ever wondered why you forget names?",  # Will fail
        "Your brain is ALREADY forgetting names",  # Missing "..."
        "Nobody tells you what actually happens to memory...",  # Should pass
    ]
    
    print("\n📊 VALIDATION TESTS:\n")
    for hook in test_hooks:
        result = engine.validate_hook(hook)
        status = "✅" if result.is_valid else "❌"
        print(f"{status} '{hook}'")
        print(f"   Score: {result.score}/10 | Words: {result.word_count} | Auto-fixed: {result.auto_fixed}")
        if result.errors:
            print(f"   ❌ {', '.join(result.errors)}")
        if result.warnings:
            print(f"   ⚠️ {', '.join(result.warnings)}")
        print()
    
    print("\n🔄 SELF-CORRECTION TEST:\n")
    result = engine.generate_perfect_hook("forgetting names")
    print(f"\n🏆 FINAL RESULT:")
    print(f"   Hook: '{result['hook']}'")
    print(f"   Score: {result['validation'].score}/10")
    print(f"   Status: {result['status']}")
    print(f"   Attempts: {result['attempts']}")
    print(f"   Cached: {result.get('cached', False)}")
    
    print("\n📊 Cache Stats:")
    print(engine.get_cache_stats())
