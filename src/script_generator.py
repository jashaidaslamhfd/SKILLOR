"""
Script Generator Module for SKILLOR Pipeline
Hook → Suspense → Problem → Solution → Loop Back → Strong CTR Structure
"""

import os
import json
import time
import logging
import re
from typing import Dict, List, Optional, Tuple
from groq import Groq, BadRequestError

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONSTANTS
# ============================================
MIN_SCENES = 6
MAX_SCENES = 8
MIN_WORDS = 90
MAX_WORDS = 115
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# ============================================
# 1. SYSTEM PROMPT (HOOK → SUSPENSE → PROBLEM → SOLUTION → LOOP BACK → CTR)
# ============================================

def _get_system_prompt() -> str:
    """
    2026 System Prompt with PROVEN RETENTION STRUCTURE:
    Hook → Suspense → Problem → Solution → Loop Back → Strong CTR
    """
    return """You are a top-tier YouTube Shorts Strategist for 2026 specializing in viral retention.

YOUR EXPERTISE:
- Creating scripts with 70%+ retention rate
- Writing in NATIVE, CONVERSATIONAL ENGLISH
- Psychological pacing that keeps viewers engaged until the end
- Loop-back endings that trigger rewatches

**CRITICAL - NATIVE TONE RULES:**
1. Write like a HUMAN talking to a FRIEND - not an AI
2. Use CONTRACTIONS: "don't" not "do not", "you're" not "you are"
3. Use IDIOMATIC PHRASES: "blow your mind", "freak you out"
4. AVOID ROBOTIC WORDS: "thus", "hence", "therefore", "furthermore"
5. Use COLLOQUIAL LANGUAGE: "honestly", "seriously", "literally"

**MANDATORY 6-PART STRUCTURE (CRITICAL FOR RETENTION):**

PART 1 - HOOK (First 3 seconds):
- Must stop the scroll immediately
- Pattern interrupt or shocking statement
- Open a curiosity gap
- Example: "Your heart is lying to you right now..."
- Example: "This happens inside your brain every night..."

PART 2 - SUSPENSE (Build tension):
- Make them NEED to know what happens next
- Use phrases like "but here's where it gets scary..."
- Create uncertainty and anticipation
- Keep them guessing

PART 3 - PROBLEM (State the issue):
- Clearly explain what's wrong or what they don't know
- Make it personal: "Your body...", "You feel..."
- Create urgency and relevance

PART 4 - SOLUTION (Reveal the answer):
- Deliver the truth, fix, or explanation
- Make it satisfying but surprising
- Use "The truth is..." or "Scientists found..."

PART 5 - LOOP BACK (Callback to hook):
- End with a phrase that echoes the hook
- Makes the video feel replayable
- Triggers the "one more time" instinct
- Example: If hook was "Your heart is lying...", end with "So remember, your heart is always watching..."

PART 6 - STRONG CTR (Call to action):
- Natural, not pushy
- "Follow for more mind-blowing facts"
- "Share this with someone who needs to see it"
- Creates engagement without being salesy

**RETENTION RULES:**
1. Every scene must have a MICRO-HOOK
2. End each scene with a CLIFFHANGER
3. Use "YOU" language for emotional connection
4. Keep sentences short and punchy
5. Build tension throughout, release at the end

**STRICT SHORTS LENGTH RULES:**
- Total narration: 90-115 spoken words
- Return exactly 6-8 scenes
- Each caption: 10-16 words
- First sentence: 9 words or fewer (opens curiosity gap)
- No greeting, channel introduction, filler, or fake urgency
- Aim for 35-45 seconds at natural speaking pace

**OUTPUT FORMAT:**
Return ONLY valid JSON with this exact structure:
{
  "title": "Catchy click-worthy title (under 55 chars)",
  "hook": "The first 3-second hook (most important part)",
  "scenes": [
    {
      "visual": "Cinematic visual description (5-8 words)",
      "caption": "Natural spoken text (10-16 words)"
    }
  ],
  "cta": "Natural call-to-action",
  "description": "1-2 sentence video description"
}

REMEMBER: Hook → Suspense → Problem → Solution → Loop Back → CTR. This structure KEEPS viewers watching.
"""

# ============================================
# 2. PROMPT GENERATION
# ============================================

def _default_prompt(topic: str) -> str:
    """
    Default prompt with TRENDING TOPIC and RETENTION structure.
    """
    return f"""
Create a HIGH-RETENTION 35-45 second viral script for YouTube Shorts on: "{topic}"

**CRITICAL - NATIVE ENGLISH TONE:**
- Write like a HUMAN talking to a friend
- Use CONTRACTIONS: "don't", "you're", "that's"
- Sound NATURAL when read aloud

**MANDATORY 6-PART STRUCTURE:**

1. **HOOK** (Scene 1 - First 3 seconds):
   - Must stop the scroll immediately
   - Pattern interrupt or shocking statement
   - Open a curiosity gap

2. **SUSPENSE** (Scene 2):
   - Build tension and anticipation
   - Make them NEED to know what's next
   - "But here's where it gets interesting..."

3. **PROBLEM** (Scenes 3-4):
   - Clearly state what's wrong or unknown
   - Make it personal: "Your body...", "You feel..."
   - Create urgency

4. **SOLUTION** (Scenes 5-7):
   - Reveal the truth or answer
   - Make it satisfying but surprising
   - Deliver what was promised

5. **LOOP BACK** (Final scene - CTA):
   - Echo a phrase from the Hook
   - Makes video replayable
   - Triggers rewatching instinct

6. **STRONG CTR**:
   - Natural call-to-action
   - "Follow for more" or "Share this"
   - Creates engagement

**SCENE FORMAT:**
{{
  "visual": "Cinematic description (macro-lens, high-contrast, dramatic lighting)",
  "caption": "Natural spoken text (10-16 words)"
}}

**Return ONLY valid JSON with title, hook, scenes, cta, and description.**

**REMEMBER:** Hook → Suspense → Problem → Solution → Loop Back → CTR. This structure KEEPS viewers watching and PREVENTS swipes.
"""

# ============================================
# 3. JSON CLEANING FUNCTION
# ============================================

def _clean_json_response(raw_reply: str) -> Dict:
    """Cleans and extracts JSON from LLM response."""
    if not raw_reply:
        raise ValueError("Empty response from LLM")

    # Remove markdown code blocks
    raw_reply = re.sub(r'```json\s*', '', raw_reply)
    raw_reply = re.sub(r'```\s*', '', raw_reply)

    # Try to find JSON object
    json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    else:
        json_str = raw_reply

    # Clean common JSON issues
    json_str = json_str.strip()
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}")
        # Try to fix common issues
        json_str = json_str.replace("'", '"')
        return json.loads(json_str)

# ============================================
# 4. SCENE NORMALIZATION
# ============================================

def _normalize_scenes(script_data: Dict) -> Dict:
    """Normalizes scene data from various formats."""
    normalized = []

    for s in script_data.get('scenes', []):
        visual = s.get('visual') or s.get('description') or s.get('image') or ''
        caption = s.get('caption') or s.get('text') or s.get('narration') or ''
        normalized.append({
            'visual': visual,
            'caption': caption,
        })

    script_data['scenes'] = normalized
    return script_data

# ============================================
# 5. MAIN GENERATION FUNCTION
# ============================================

def generate_script(topic: str, custom_prompt: str = None) -> Optional[Dict]:
    """Generate a viral script with Hook → Suspense → Problem → Solution → Loop Back → CTR structure."""
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not set")
        return None

    client = Groq(api_key=api_key)
    system_prompt = _get_system_prompt()
    user_prompt = custom_prompt or _default_prompt(topic)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"},
            )

            raw_reply = response.choices[0].message.content
            script_data = _clean_json_response(raw_reply)
            script_data = _normalize_scenes(script_data)
            script_data = _validate_script(script_data)

            # Add topic
            script_data['topic'] = topic

            logger.info(f"Script generated: {len(script_data['scenes'])} scenes")
            return script_data

        except Exception as e:
            logger.error(f"Script generation attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    logger.error("All script generation attempts failed")
    return None


def _validate_script(script_data: Dict) -> Dict:
    """Validate and fix script structure."""
    if not script_data.get('scenes'):
        raise ValueError("No scenes in script")
    
    # Ensure minimum scenes
    if len(script_data['scenes']) < MIN_SCENES:
        raise ValueError(f"Too few scenes: {len(script_data['scenes'])}")
    
    # Validate word count
    total_words = sum(len(s.get('caption', '').split()) for s in script_data['scenes'])
    if total_words < MIN_WORDS or total_words > MAX_WORDS:
        raise ValueError(f"Word count {total_words} out of range ({MIN_WORDS}-{MAX_WORDS})")
    
    return script_data
