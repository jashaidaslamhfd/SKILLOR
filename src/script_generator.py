"""
Script Generator Module for SKILLOR Pipeline
FULLY FIXED - JSON Cleaning + Native Tone + Retention Optimization
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
MIN_SCENES = 8
MAX_SCENES = 12
MIN_WORDS = 130
MAX_WORDS = 170
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# ============================================
# 1. SYSTEM PROMPT (NATIVE TONE + RETENTION)
# ============================================

def _get_system_prompt() -> str:
    """
    2026 System Prompt with NATIVE ENGLISH TONE and RETENTION FOCUS.
    """
    return """You are a top-tier Social Media Strategist for 2026 specializing in YouTube Shorts/Facebook Reels.

YOUR EXPERTISE:
- Creating VIRAL scripts with 70%+ retention rate
- Writing in NATIVE, CONVERSATIONAL ENGLISH (USA/UK)
- Pattern Interrupt Hooks that stop the scroll
- Psychological pacing that keeps viewers engaged

**CRITICAL - NATIVE TONE RULES:**
1. Write like a HUMAN talking to a FRIEND - not an AI
2. Use CONTRACTIONS: "don't" not "do not", "you're" not "you are"
3. Use IDIOMATIC PHRASES: "blow your mind", "freak you out", "makes total sense"
4. AVOID ROBOTIC WORDS: "thus", "hence", "therefore", "furthermore"
5. Use COLLOQUIAL LANGUAGE: "honestly", "seriously", "literally"
6. Keep it NATURAL - read it aloud, it should sound like a real person

**RETENTION RULES (CRITICAL):**
1. **Pattern Interrupt Hook**: First 3 seconds must be SHOCKING or COUNTER-INTUITIVE
   - "Your heart is lying to you right now..."
   - "This happens inside your brain every night..."

2. **The "3-Second Rule"**: Every scene must have a MICRO-HOOK
   - Start each scene with tension
   - End each scene with a CLIFFHANGER
   - Example: "...but that's only half the story"

3. **"YOU" Language**: Use direct personal address
   - "Your brain", "Your heart", "You feel"
   - Creates emotional connection

4. **Emotional Arc**: 
   - Hook (Curiosity/Shock) → Build Tension → Reveal → Relief/Resolution

5. **Loopable Outro**: End should naturally lead back to the start
   - Encourages rewatching

**OUTPUT FORMAT:**
Return ONLY valid JSON with this exact structure:
{
  "title": "Catchy click-worthy title (under 55 chars)",
  "hook": "The first 3-second hook (most important part)",
  "scenes": [
    {
      "visual": "Cinematic visual description (5-8 words)",
      "caption": "Punchy spoken text (15-20 words)"
    }
  ],
  "cta": "Natural call-to-action",
  "description": "1-2 sentence video description"
}

REMEMBER: Write like a HUMAN, not an AI. Be NATURAL. Be CONVERSATIONAL. Focus on RETENTION.
"""


# ============================================
# 2. PROMPT GENERATION
# ============================================

def _default_prompt(topic: str) -> str:
    """
    Default prompt with NATIVE TONE and RETENTION enforcement.
    """
    return f"""
Create a HIGH-RETENTION 45-second viral script for YouTube Shorts on: "{topic}"

**CRITICAL - NATIVE ENGLISH TONE:**
- Write like a HUMAN talking to a friend
- Use CONTRACTIONS: "don't", "you're", "that's"
- Use IDIOMS: "blow your mind", "freak you out", "makes total sense"
- AVOID: "thus", "hence", "therefore", "furthermore"
- Sound NATURAL when read aloud

**SCRIPT REQUIREMENTS:**

1. **HOOK** (First 3 seconds - CRITICAL):
   - Must stop the scroll immediately
   - Use conversational tone
   - Pattern interrupt or shocking statement

2. **SCENES** ({MIN_SCENES}-{MAX_SCENES} scenes):
   - Each scene: 15-20 words caption
   - Each scene: Must end with a cliffhanger
   - Each scene: Cinematic visual description

3. **WORD COUNT** (HARD REQUIREMENT):
   - Total: {MIN_WORDS}-{MAX_WORDS} words
   - Count your words BEFORE finalizing

4. **STRUCTURE**:
   - Scene 1: Hook + Setup
   - Scenes 2-6: Build tension + Reveal information
   - Scenes 7-10: Climax + Resolution
   - Final scene: CTA + Loopable outro

5. **TONE**:
   - Dark, mysterious, factual
   - Engaging, not boring
   - NATURAL, CONVERSATIONAL

**SCENE FORMAT:**
{{
  "visual": "Cinematic description (macro-lens, high-contrast, dramatic lighting)",
  "caption": "Punchy, engaging text (ends with cliffhanger)"
}}

**Return ONLY valid JSON with title, hook, scenes, cta, and description.**

**REMEMBER:** Retention is EVERYTHING. Write like a HUMAN. Make every second count.
"""


# ============================================
# 3. JSON CLEANING FUNCTION
# ============================================

def _clean_json_response(raw_reply: str) -> Dict:
    """
    Cleans and extracts JSON from LLM response.
    Handles markdown code blocks, extra text, and malformed JSON.
    """
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
    
    # Fix trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # NOTE: We intentionally do NOT blanket-convert single quotes to double
    # quotes here. Groq's response_format={"type": "json_object"} already
    # guarantees valid double-quoted JSON, and the system prompt asks for
    # natural contractions ("don't", "you're"), which contain apostrophes.
    # Converting those apostrophes to '"' corrupts the JSON mid-string
    # (this was the root cause of the "Expecting ',' delimiter" errors).
    
    # Remove control characters
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
    
    # Fix unescaped newlines in strings
    json_str = re.sub(r'(?<!\\)\n', ' ', json_str)
    
    # Try to parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}")
        logger.debug(f"Cleaned JSON: {json_str[:500]}...")
        
        # Fallback: Try to extract with regex
        fallback = {}
        
        # Extract title
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', json_str)
        if title_match:
            fallback['title'] = title_match.group(1)
        
        # Extract hook
        hook_match = re.search(r'"hook"\s*:\s*"([^"]+)"', json_str)
        if hook_match:
            fallback['hook'] = hook_match.group(1)
        
        # Extract scenes
        scenes_match = re.search(r'"scenes"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
        if scenes_match:
            scenes_str = scenes_match.group(1)
            scenes = []
            # Find all scene objects
            scene_blocks = re.finditer(r'\{[^{}]*\}', scenes_str, re.DOTALL)
            for block in scene_blocks:
                scene_str = block.group(0)
                visual_match = re.search(r'"visual"\s*:\s*"([^"]+)"', scene_str)
                caption_match = re.search(r'"caption"\s*:\s*"([^"]+)"', scene_str)
                if visual_match and caption_match:
                    scenes.append({
                        'visual': visual_match.group(1),
                        'caption': caption_match.group(1)
                    })
            if scenes:
                fallback['scenes'] = scenes
        
        # Extract CTA
        cta_match = re.search(r'"cta"\s*:\s*"([^"]+)"', json_str)
        if cta_match:
            fallback['cta'] = cta_match.group(1)
        
        # Extract description
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', json_str)
        if desc_match:
            fallback['description'] = desc_match.group(1)
        
        if fallback:
            logger.info("✅ Extracted data using regex fallback")
            return fallback
        
        raise ValueError(f"Could not parse JSON from response: {raw_reply[:200]}")


# ============================================
# 4. SCRIPT VALIDATION & NORMALIZATION
# ============================================

def _normalize_scenes(script_data: Dict) -> Dict:
    """
    Normalizes scene data from various formats.
    Ensures all required fields are present.
    """
    normalized = []
    
    for s in script_data.get('scenes', []):
        # Try different field names
        visual = s.get('visual') or s.get('description') or s.get('image') or ''
        caption = s.get('caption') or s.get('text') or s.get('speech') or ''
        
        # Clean and validate
        visual = visual.strip()
        caption = caption.strip()
        
        if visual and caption:
            normalized.append({
                "visual": visual,
                "caption": caption
            })
        elif caption and not visual:
            # If only caption exists, generate a generic visual
            normalized.append({
                "visual": f"Dark cinematic shot of {caption[:30]}...",
                "caption": caption
            })
    
    script_data['scenes'] = normalized
    script_data['voiceover'] = ' '.join(s['caption'] for s in normalized)
    
    return script_data


def _validate_script(script_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validates script for quality and completeness.
    
    Returns:
        (is_valid, issues_list)
    """
    issues = []
    
    # Check required fields
    required_fields = ['title', 'hook', 'scenes', 'cta']
    for field in required_fields:
        if not script_data.get(field):
            issues.append(f"Missing required field: {field}")
    
    # Check scenes
    scenes = script_data.get('scenes', [])
    if len(scenes) < MIN_SCENES:
        issues.append(f"Too few scenes: {len(scenes)} (minimum {MIN_SCENES})")
    elif len(scenes) > MAX_SCENES:
        issues.append(f"Too many scenes: {len(scenes)} (maximum {MAX_SCENES})")
    
    # Check word count
    voiceover = script_data.get('voiceover', '')
    word_count = len(voiceover.split())
    if word_count < MIN_WORDS - 10:
        issues.append(f"Too few words: {word_count} (minimum {MIN_WORDS})")
    elif word_count > MAX_WORDS + 10:
        issues.append(f"Too many words: {word_count} (maximum {MAX_WORDS})")
    
    # Check each scene
    for i, scene in enumerate(scenes):
        if not scene.get('visual'):
            issues.append(f"Scene {i+1} missing visual description")
        if not scene.get('caption'):
            issues.append(f"Scene {i+1} missing caption")
    
    return len(issues) == 0, issues


# ============================================
# 5. RETENTION ANALYSIS
# ============================================

def analyze_retention_potential(script_data: Dict) -> Dict:
    """
    Analyzes script for retention potential.
    Returns score (0-100) and suggestions.
    """
    scenes = script_data.get('scenes', [])
    score = 0
    suggestions = []
    
    # Check scene count
    if MIN_SCENES <= len(scenes) <= MAX_SCENES:
        score += 20
    else:
        suggestions.append(f"Optimal scene count: {MIN_SCENES}-{MAX_SCENES}, currently {len(scenes)}")
    
    # Check hook
    hook = script_data.get('hook', '')
    if hook:
        hook_words = len(hook.split())
        if 5 <= hook_words <= 15:
            score += 15
        else:
            suggestions.append("Hook should be 5-15 words for maximum impact")
        
        # Check for pattern interrupt
        if any(word in hook.lower() for word in ['lying', 'secret', 'truth', 'never', 'always', 'actually']):
            score += 10
    
    # Check "YOU" language
    voiceover = script_data.get('voiceover', '')
    you_count = voiceover.lower().count('you')
    if you_count >= len(scenes) * 1.5:
        score += 15
    else:
        suggestions.append("Use more 'YOU' language for personal connection")
    
    # Check cliffhangers
    cliffhanger_count = 0
    for scene in scenes:
        caption = scene.get('caption', '')
        if any(word in caption.lower() for word in ['...', 'but', 'however', 'yet', 'still', 'though']):
            cliffhanger_count += 1
    
    if cliffhanger_count >= len(scenes) * 0.7:
        score += 20
    else:
        suggestions.append(f"Only {cliffhanger_count}/{len(scenes)} scenes have cliffhangers - aim for 70%+")
    
    # Check word count
    word_count = len(voiceover.split())
    if MIN_WORDS <= word_count <= MAX_WORDS:
        score += 20
    else:
        suggestions.append(f"Word count: {word_count} (target: {MIN_WORDS}-{MAX_WORDS})")
    
    # Check for loopable outro
    cta = script_data.get('cta', '')
    if any(word in cta.lower() for word in ['follow', 'share', 'subscribe', 'comment']):
        score += 10
    
    return {
        'retention_score': min(100, score),
        'suggestions': suggestions,
        'scenes': len(scenes),
        'word_count': word_count,
        'you_count': you_count,
        'cliffhanger_ratio': cliffhanger_count / len(scenes) if scenes else 0,
        'is_viral_ready': score >= 80
    }


# ============================================
# 6. MAIN GENERATE FUNCTION
# ============================================

def generate_script(
    topic: str, 
    custom_prompt: Optional[str] = None, 
    max_retries: int = MAX_RETRIES
) -> Dict:
    """
    Generates a RETENTION-OPTIMIZED script using Groq LLM.
    
    Features:
    - JSON cleaning with regex fallback
    - Native English tone enforcement
    - Automatic validation and retry
    - Retention analysis
    
    Args:
        topic: Topic for the script
        custom_prompt: Optional custom prompt
        max_retries: Maximum retry attempts
    
    Returns:
        Script data dictionary
    
    Raises:
        RuntimeError: If generation fails after all retries
        ValueError: If GROQ_API_KEY is missing
    """
    # Check API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Please set it in environment variables.")
    
    # Initialize client
    client = Groq(api_key=api_key)
    
    # Prepare prompt
    prompt = custom_prompt or _default_prompt(topic)
    messages = [
        {"role": "system", "content": _get_system_prompt()},
        {"role": "user", "content": prompt}
    ]
    
    last_error = None
    best_script = None
    best_score = 0
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Generating script (Attempt {attempt}/{max_retries})")
            
            # Call Groq API
            completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            raw_reply = completion.choices[0].message.content
            
            # Clean JSON
            script_data = _clean_json_response(raw_reply)
            
            # Normalize scenes
            script_data = _normalize_scenes(script_data)
            
            # Add metadata
            script_data['topic'] = topic
            script_data['generated_at'] = time.time()
            script_data['attempt'] = attempt
            
            # Validate
            is_valid, issues = _validate_script(script_data)
            
            if is_valid:
                # Analyze retention
                retention = analyze_retention_potential(script_data)
                script_data['retention_analysis'] = retention
                
                score = retention['retention_score']
                
                # Track best script
                if score > best_score:
                    best_script = script_data
                    best_score = score
                
                if score >= 80:
                    logger.info(f"✅ Excellent script! Retention score: {score}/100")
                    logger.info(f"📊 {len(script_data['scenes'])} scenes, {len(script_data['voiceover'].split())} words")
                    return script_data
                else:
                    logger.warning(f"⚠️ Good but could be better (Score: {score}/100)")
                    # Add corrective feedback
                    messages.append({"role": "assistant", "content": raw_reply})
                    messages.append({"role": "user", "content": (
                        f"The script is good but retention could be improved. "
                        f"Current score: {score}/100. Issues: {', '.join(retention['suggestions'][:3])}. "
                        f"Rewrite the script with these improvements while keeping the topic '{topic}'. "
                        f"Return ONLY valid JSON with the same structure."
                    )})
            else:
                logger.warning(f"⚠️ Validation issues: {', '.join(issues[:3])}")
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({"role": "user", "content": (
                    f"The script has validation issues: {', '.join(issues[:3])}. "
                    f"Rewrite it to fix these issues. Keep the same topic '{topic}'. "
                    f"Return ONLY valid JSON with the same structure."
                )})
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            messages.append({"role": "user", "content": (
                "The previous response was not valid JSON. "
                "Please return ONLY valid JSON with this exact structure: "
                '{"title": "...", "hook": "...", "scenes": [{"visual": "...", "caption": "..."}], "cta": "..."}'
            )})
            
        except BadRequestError as e:
            logger.error(f"❌ Groq API error: {e}")
            last_error = e
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            last_error = e
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
    
    # If we have a best script, return it
    if best_script:
        logger.warning(f"⚠️ Using best available script (Score: {best_score}/100)")
        return best_script
    
    # Complete failure
    raise RuntimeError(
        f"❌ Script generation failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


# ============================================
# 7. BATCH GENERATION
# ============================================

def generate_multiple_scripts(
    topics: List[str],
    max_retries: int = MAX_RETRIES,
    delay: float = 2.0
) -> List[Dict]:
    """
    Generates scripts for multiple topics.
    
    Args:
        topics: List of topics
        max_retries: Retries per script
        delay: Delay between generations
    
    Returns:
        List of script data dictionaries
    """
    scripts = []
    failed = []
    
    for i, topic in enumerate(topics):
        logger.info(f"📝 Generating script {i+1}/{len(topics)}: {topic}")
        
        try:
            script = generate_script(topic, max_retries=max_retries)
            scripts.append(script)
            logger.info(f"✅ Script {i+1} generated successfully")
        except Exception as e:
            logger.error(f"❌ Script {i+1} failed: {e}")
            failed.append({'topic': topic, 'error': str(e)})
        
        if i < len(topics) - 1:
            time.sleep(delay)
    
    logger.info(f"📊 Generated {len(scripts)}/{len(topics)} scripts successfully")
    if failed:
        logger.warning(f"⚠️ Failed scripts: {len(failed)}")
    
    return scripts, failed


# ============================================
# 8. SCRIPT EXPORT
# ============================================

def export_script(script_data: Dict, output_path: str = "output/script.json") -> str:
    """
    Exports script data to JSON file.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📄 Script exported to: {output_path}")
    return output_path


# ============================================
# 9. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("SCRIPT GENERATOR - FULLY FIXED (JSON Cleaning + Native Tone)")
    print("="*70)
    print()
    
    # Test single generation
    test_topic = "Why Your Brain Lies to You"
    print(f"🧪 Testing with topic: {test_topic}")
    print("-" * 70)
    
    try:
        script = generate_script(test_topic)
        
        print("✅ Script generated successfully!")
        print()
        print(f"📌 TITLE: {script.get('title')}")
        print(f"🎯 HOOK: {script.get('hook')}")
        print(f"📊 SCENES: {len(script.get('scenes', []))}")
        print(f"📝 WORDS: {len(script.get('voiceover', '').split())}")
        print(f"📢 CTA: {script.get('cta')}")
        
        if 'retention_analysis' in script:
            analysis = script['retention_analysis']
            print()
            print("📈 RETENTION ANALYSIS:")
            print(f"   Score: {analysis.get('retention_score')}/100")
            print(f"   Viral Ready: {analysis.get('is_viral_ready')}")
            if analysis.get('suggestions'):
                print("   Suggestions:")
                for suggestion in analysis['suggestions'][:3]:
                    print(f"     - {suggestion}")
        
        print()
        print("📄 FIRST SCENE PREVIEW:")
        scenes = script.get('scenes', [])
        if scenes:
            print(f"   Visual: {scenes[0].get('visual')}")
            print(f"   Caption: {scenes[0].get('caption')}")
        
        print()
        print("-" * 70)
        print("✅ Script generator is ready for production!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
