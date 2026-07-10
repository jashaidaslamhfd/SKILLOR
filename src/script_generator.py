"""
Script Generator Module for SKILLOR Pipeline
OPTIMIZED FOR: HIGH RETENTION + VIRAL POTENTIAL (2026 Standards)
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
MAX_TOKENS = 3000

# ============================================
# 1. RETENTION-OPTIMIZED SYSTEM PROMPT
# ============================================

def _get_system_prompt() -> str:
    """
    2026 System Prompt focused on RETENTION and VIRALITY.
    """
    return """You are a top-tier Social Media Strategist for 2026 specializing in YouTube Shorts/Facebook Reels.

YOUR EXPERTISE:
- Creating VIRAL scripts with 70%+ retention rate
- Pattern Interrupt Hooks that stop the scroll
- Psychological pacing that keeps viewers engaged
- Loopable content that encourages rewatches

RETENTION RULES (CRITICAL):
1. **Pattern Interrupt Hook**: First 3 seconds must be SHOCKING or COUNTER-INTUITIVE
   - "Your heart is lying to you right now..."
   - "This happens inside your brain every night..."
   - "Doctors don't want you to know this..."

2. **The "3-Second Rule"**: Every scene must have a MICRO-HOOK
   - Start each scene with tension
   - End each scene with a CLIFFHANGER
   - Example: "...but that's only half the story"

3. **"YOU" Language**: Use direct personal address
   - "Your brain", "Your heart", "You feel"
   - Creates emotional connection
   - Increases watch time

4. **Pacing**: Short, punchy sentences (5-10 words max)
   - NOT a short script - use multiple punchy sentences per scene
   - Total word count MUST be 130-170 words
   - Each scene: 15-20 words (spoken in 3-5 seconds)

5. **Visual Engagement**: Each scene needs CINEMATIC visuals
   - Use words: cinematic, macro-lens, high-contrast, dramatic lighting
   - No static or generic images

6. **Loopable Outro**: End should naturally lead back to the start
   - Encourages rewatching
   - Increases total watch time

7. **Emotional Arc**: 
   - Hook (Curiosity/Shock) → Build Tension → Reveal → Relief/Resolution
   - Every scene moves the emotional needle

OUTPUT FORMAT:
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
  "cta": "Natural call-to-action that fits the end",
  "description": "1-2 sentence video description"
}

REMEMBER: Retention is EVERYTHING. Every word, every scene, every visual must serve to KEEP THE VIEWER WATCHING.
"""


# ============================================
# 2. PROMPT GENERATION
# ============================================

def _default_prompt(topic: str) -> str:
    """
    Default prompt for script generation.
    Includes word count constraints and structure requirements.
    """
    return f"""
Create a HIGH-RETENTION 45-second viral script for YouTube Shorts on: "{topic}"

TARGET AUDIENCE: USA adults 18+ (dark mystery/science niche)

SCRIPT REQUIREMENTS:

1. **HOOK** (First 3 seconds - CRITICAL):
   - Must stop the scroll immediately
   - Pattern interrupt or shocking statement
   - Example: "Your body is lying to you right now..."

2. **SCENES** ({MIN_SCENES}-{MAX_SCENES} scenes):
   - Each scene: 3-5 seconds duration
   - Each scene: 15-20 words caption
   - Each scene: Cinematic visual description
   - Each scene: Must end with a cliffhanger or transition

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
   - Scientific but accessible

Return ONLY valid JSON with title, hook, scenes, cta, and description.

SCENE FORMAT:
{{
  "visual": "Cinematic description (macro-lens, high-contrast, dramatic lighting)",
  "caption": "Punchy, engaging text (ends with cliffhanger)"
}}

Remember: Retention is EVERYTHING. Make every second count.
"""


# ============================================
# 3. SCRIPT VALIDATION & NORMALIZATION
# ============================================

def _normalize_scenes(script_data: Dict) -> Dict:
    """
    Normalizes scene data from various formats.
    Ensures all required fields are present.
    """
    normalized = []
    
    for s in script_data.get('scenes', []):
        visual = s.get('visual') or s.get('description') or ''
        caption = s.get('caption') or s.get('text') or ''
        
        # Clean and validate
        visual = visual.strip()
        caption = caption.strip()
        
        if visual and caption:
            normalized.append({
                "visual": visual,
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
        
        # Check for cliffhanger
        caption = scene.get('caption', '')
        if not any(word in caption.lower() for word in ['...', 'but', 'however', 'yet', 'still']):
            issues.append(f"Scene {i+1} may lack cliffhanger")
    
    return len(issues) == 0, issues


# ============================================
# 4. RETENTION ANALYSIS
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
        if any(word in hook.lower() for word in ['lying', 'secret', 'truth', 'never', 'always']):
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
        if any(word in caption.lower() for word in ['...', 'but', 'however', 'yet', 'still']):
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
    
    return {
        'retention_score': min(100, score),
        'suggestions': suggestions,
        'scenes': len(scenes),
        'word_count': word_count,
        'you_count': you_count,
        'cliffhanger_ratio': cliffhanger_count / len(scenes) if scenes else 0
    }


# ============================================
# 5. MAIN GENERATE FUNCTION (RETRY LOGIC)
# ============================================

def generate_script(
    topic: str, 
    custom_prompt: Optional[str] = None, 
    max_retries: int = MAX_RETRIES
) -> Dict:
    """
    Generates a RETENTION-OPTIMIZED script using Groq LLM.
    
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
            
            # Parse response
            raw_reply = completion.choices[0].message.content
            script_data = json.loads(raw_reply)
            
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
                f"The previous response was not valid JSON. "
                f"Please return ONLY valid JSON with this exact structure: "
                f'{{"title": "...", "hook": "...", "scenes": [{{"visual": "...", "caption": "..."}}], "cta": "..."}}'
            )})
            
        except BadRequestError as e:
            logger.error(f"❌ Groq API error: {e}")
            last_error = e
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
# 6. BATCH GENERATION
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
    
    for i, topic in enumerate(topics):
        logger.info(f"📝 Generating script {i+1}/{len(topics)}: {topic}")
        
        try:
            script = generate_script(topic, max_retries=max_retries)
            scripts.append(script)
            logger.info(f"✅ Script {i+1} generated successfully")
        except Exception as e:
            logger.error(f"❌ Script {i+1} failed: {e}")
            continue
        
        if i < len(topics) - 1:
            time.sleep(delay)
    
    logger.info(f"📊 Generated {len(scripts)}/{len(topics)} scripts successfully")
    return scripts


# ============================================
# 7. SCRIPT EXPORT
# ============================================

def export_script(script_data: Dict, output_path: str = "output/script.json"):
    """
    Exports script data to JSON file.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(script_data, f, indent=2)
    
    logger.info(f"📄 Script exported to: {output_path}")
    return output_path


# ============================================
# 8. MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Test the generator
    print("="*60)
    print("RETENTION-OPTIMIZED SCRIPT GENERATOR")
    print("="*60)
    print()
    
    # Test single generation
    test_topic = "Why Your Brain Lies to You"
    print(f"🧪 Testing with topic: {test_topic}")
    print()
    
    try:
        script = generate_script(test_topic)
        
        print("✅ Script generated successfully!")
        print(f"   Title: {script.get('title')}")
        print(f"   Hook: {script.get('hook')}")
        print(f"   Scenes: {len(script.get('scenes', []))}")
        print(f"   Words: {len(script.get('voiceover', '').split())}")
        
        if 'retention_analysis' in script:
            analysis = script['retention_analysis']
            print(f"   Retention Score: {analysis.get('retention_score')}/100")
            print(f"   Suggestions: {analysis.get('suggestions', [])[:2]}")
        
        print()
        print("📄 First scene preview:")
        scenes = script.get('scenes', [])
        if scenes:
            print(f"   Visual: {scenes[0].get('visual')}")
            print(f"   Caption: {scenes[0].get('caption')[:50]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
