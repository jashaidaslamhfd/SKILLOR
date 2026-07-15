"""
src/seo_generator.py

PRD "AI SEO Generator" feature, adapted to SKILLOR's dark-facts Shorts niche.
Pure post-processing on top of an already-generated script_data dict — no
extra LLM calls, so it's free and instant to run for every video.

Produces:
  - title_options: 5 SEO-friendly title variants (different hook angles)
  - description: CTR-optimized YouTube description (reuses the same shape
    uploader.py already builds, factored out here so it's the single
    source of truth)
  - hashtags: deduplicated, ranked hashtag list
  - pinned_comment: a comment worth auto-pinning post-upload to seed
    engagement (main.py/uploader.py can pin it via commentThreads.insert)
  - playlist_suggestion: which existing playlist this video best fits
  - seo_score: 0-100 with a breakdown, so low-scoring videos can be
    flagged the same way quality_checker flags weak scripts

Nothing here calls the network or an LLM - it's deterministic string/rule
based scoring, matching the pattern already used in quality_checker.py and
anti_spam.py.
"""

import re
import logging
import random
from typing import Dict, List

from niche_strategy import generate_seo_tags, _make_seo_title, get_topic_category

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TITLE_MAX_LEN = 70          # YouTube truncates further titles in search UI
DESCRIPTION_MAX_LEN = 5000  # YouTube hard limit
PINNED_COMMENT_MAX_LEN = 200

# Existing playlists this channel maintains (edit to match your real
# playlist names/IDs - used only for suggestion text, not an API call).
PLAYLISTS_BY_CATEGORY = {
    "Brain": "Dark Brain Facts",
    "Body": "Dark Body Facts",
    "Mystery": "Body Mysteries",
    "Health": "Health & Science Shorts",
}

# EXPANDED TITLE TEMPLATES (20+ variations for diversity)
_TITLE_TEMPLATES = [
    # Specific, credible, human-sounding patterns. Avoid fake conspiracy,
    # "shocking", and "this is real" phrases that make automated content obvious.
    "{topic}",
    "Why {topic} Happens",
    "How {topic} Controls Your Day",
    "What {topic} Does to Your Body",
    "The Science Behind {topic}",
    "What Your Body Clock Is Doing Right Now",
    "Your Body Does This Every Day",
    "The Daily Signal Your Body Follows",
]

# HIGH-VOLUME TAGS BY CATEGORY
_HIGH_VOLUME_TAGS = {
    "Brain": ["neuroscience", "brainfacts", "mindblowing", "psychology", "brainpower", "cognitivescience"],
    "Body": ["humanbody", "anatomy", "healthfacts", "biology", "physiology", "bodysecrets"],
    "Mystery": ["mystery", "unsolved", "creepyfacts", "paranormal", "weirdfacts", "conspiracy"],
    "Health": ["healthtips", "wellness", "medicalfacts", "science", "healthyliving", "nutrition"],
}

# TRENDING TAGS (YouTube Shorts specific)
_TRENDING_TAGS = ["shorts", "viralfacts", "didyouknow", "interestingfacts", "education", "sciencefacts"]


def _clean_topic_for_title(topic: str) -> str:
    """Templates like 'The Truth About Why Your Heart Skips a Beat' read
    awkwardly - strip a leading 'Why'/'The' so templated titles stay
    grammatical. Deliberately does NOT strip a leading 'Your' - personal
    'YOU language' is a core retention technique used throughout this
    codebase (see niche_strategy/script_generator), so dropping it here
    would silently undo that for any templated title that wins on score."""
    t = topic.strip()
    t = re.sub(r'^(why|the)\s+', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^(secret|hidden|shocking)\s+', '', t, flags=re.IGNORECASE)
    return t[0].upper() + t[1:] if t else topic


def generate_title_options(topic: str, script_data: Dict, n: int = 5) -> List[str]:
    """Returns up to n distinct SEO-friendly title variants for the same
    video. First option is always the enhanced original AI title (already
    proven in production via niche_strategy._make_seo_title); the rest are
    template-driven alternates so there's real angle diversity, not just
    punctuation changes."""
    base_title = script_data.get('title') or topic
    options = [_make_seo_title(base_title, topic)]

    clean_topic = _clean_topic_for_title(topic)
    seen = {options[0].lower()}
    
    # Shuffle templates for variety (but keep original first)
    templates = _TITLE_TEMPLATES.copy()
    random.shuffle(templates)
    
    for template in templates:
        if len(options) >= n:
            break
        candidate = template.format(topic=clean_topic)[:TITLE_MAX_LEN]
        if candidate.lower() not in seen:
            options.append(candidate)
            seen.add(candidate.lower())

    return options[:n]


def generate_hashtags(topic: str, category: str, n: int = 8) -> List[str]:
    """Wraps niche_strategy.generate_seo_tags() into ready-to-use hashtags,
    ranked broad-first (helps discovery) then niche-specific (helps
    relevance). Capped at n since YouTube only surfaces the first few
    hashtags above the title anyway, and Shorts specifically rewards a
    tight, relevant set over a long list."""
    # Get base tags from niche_strategy
    tags = generate_seo_tags(topic, category)
    
    # Add category-specific high-volume tags
    volume_tags = _HIGH_VOLUME_TAGS.get(category, ["science", "facts", "education"])
    
    # Add trending tags (YouTube Shorts specific)
    trending_tags = random.sample(_TRENDING_TAGS, min(3, len(_TRENDING_TAGS)))
    
    # Combine all tags
    all_tags = tags + volume_tags + trending_tags
    
    # Deduplicate while preserving order
    seen = set()
    unique_tags = []
    for tag in all_tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)
    
    return [f"#{t}" for t in unique_tags[:n]]


def _normalise_tags(tags: List[str], limit: int = 3) -> List[str]:
    """Return unique clean hashtag words regardless of whether callers pass
    `science`, `#science`, or a mixture of both."""
    clean, seen = [], set()
    for raw in tags or []:
        tag = re.sub(r"[^A-Za-z0-9_]", "", str(raw).lstrip("#")).strip()
        if tag and tag.lower() not in seen:
            seen.add(tag.lower())
            clean.append(tag)
        if len(clean) >= limit:
            break
    return clean


def generate_description(script_data: Dict, tags: List[str]) -> str:
    """Build one concise description exactly once.

    `main.py` stores the LLM's original summary as `summary`. We never feed a
    previously formatted YouTube description back into this function; that
    was the cause of duplicated paragraphs, dividers, CTAs and hashtags.
    """
    hook = re.sub(r"\s+", " ", script_data.get("hook", "")).strip()
    summary = re.sub(r"\s+", " ", script_data.get("summary", "")).strip()
    if not summary:
        candidate = script_data.get("description", "")
        # Old runs may contain an already-formatted description. Do not nest it.
        if "━━━━━━━━" not in candidate and "#" not in candidate and len(candidate) <= 500:
            summary = re.sub(r"\s+", " ", candidate).strip()
    if not summary:
        summary = "A clear, concise explanation of how this process works in your body."

    # Avoid repeating the same sentence as both hook and summary.
    parts = []
    if hook:
        parts.append(hook[:140].rstrip(" .") + ".")
    if summary and summary.lower() not in hook.lower():
        parts.append(summary[:320].rstrip())

    # Keyword-rich context line. 2026 YouTube guidance rewards a longer,
    # keyword-natural description (search snippet + categorisation) over a
    # bare hook+hashtags block. Built from the video's own tags so it stays
    # relevant and never keyword-stuffed.
    context_tags = _normalise_tags(tags, 4)
    if context_tags:
        readable = ", ".join(t.replace("_", " ") for t in context_tags)
        parts.append(
            f"Learn the science behind {readable}. "
            "Subscribe for more dark body & brain facts in under a minute."
        )

    # #Shorts FIRST so YouTube categorises this correctly as a Short, then
    # up to 3 topic hashtags (YouTube only surfaces the first 3 above the
    # title, and ignores everything past 15). #Shorts is deduped against the
    # topic tags so it never appears twice.
    ht_words = ["Shorts"] + [t for t in _normalise_tags(tags, 3) if t.lower() != "shorts"]
    hashtags = " ".join(f"#{tag}" for tag in ht_words[:4])
    if hashtags:
        parts.append(hashtags)
    return "\n\n".join(parts)[:DESCRIPTION_MAX_LEN]


def generate_pinned_comment(script_data: Dict) -> str:
    """A short comment worth pinning right after upload to seed the first
    reply/engagement signal. Keep it a genuine question or prompt - not an
    engagement-bait command like 'like if you agree', which YouTube's spam
    systems increasingly downrank."""
    topic = script_data.get('topic', script_data.get('title', 'this'))
    
    # Multiple comment templates for variety
    comment_templates = [
        f"Did you know this about {topic.lower()}? Curious what surprised you most 👇",
        f"What's your reaction to this {topic.lower()} fact? Let me know 👇",
        f"Which part of this {topic.lower()} explanation blew your mind the most? 🤯",
        f"Did you already know this about {topic.lower()}? Or was it a shock? 👇",
        "What should I explain next? Drop your suggestions below! 🔬",
    ]
    
    comment = random.choice(comment_templates)
    return comment[:PINNED_COMMENT_MAX_LEN]


def suggest_playlist(category: str) -> str:
    return PLAYLISTS_BY_CATEGORY.get(category, "Dark Body Facts")


def _score_title(title: str) -> int:
    """0-100. Rewards length in the sweet spot, a power word, and presence
    of a number - all correlate with higher Shorts CTR without tipping into
    all-caps/clickbait territory that risks a policy strike."""
    if not title:
        return 0
    
    score = 30  # Base score
    
    # Length sweet spot (30-60 chars is YouTube's favorite)
    length = len(title)
    if 30 <= length <= 55:
        score += 30
    elif 20 <= length < 30:
        score += 20
    elif length < 20:
        score += 10
    else:
        score += 5
    
    # Reward useful specificity, not manipulative clickbait.
    useful_words = ["why", "how", "what", "science", "body", "brain", "sleep", "daily", "your"]
    if any(re.search(r"\b" + re.escape(w) + r"\b", title.lower()) for w in useful_words):
        score += 20
    clickbait = ["shocking", "won't believe", "doctors won't", "forbidden", "this is real", "blow your mind", "secret rhythms", "hidden truth"]
    if any(w in title.lower() for w in clickbait):
        score -= 30

    # Numbers (CTR booster)
    if re.search(r'\d', title):
        score += 15
    
    # Emojis (attention grabber)
    if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', title):
        score += 10
    
    # Question marks (curiosity)
    if '?' in title:
        score += 10
    
    # Personal pronouns (YOU/Your)
    if re.search(r'\b(your|you)\b', title, re.IGNORECASE):
        score += 10
    
    # Exclamation marks (limited)
    exclamation_count = title.count('!')
    if exclamation_count == 1:
        score += 5
    elif exclamation_count > 2:
        score -= 5
    
    # Penalties
    if title.isupper():
        score -= 20
    if len(set(title)) < 10:  # Too repetitive
        score -= 10
    
    return max(0, min(score, 100))


def _score_description(description: str, hook: str) -> int:
    """0-100. Rewards putting the hook in the visible first ~125 chars
    (before YouTube's 'Show more' cutoff) and including hashtags."""
    if not description:
        return 0
    score = 20
    if hook and hook[:60].lower() in description[:150].lower():
        score += 30
    if '#' in description:
        score += 15
    # 2026: #Shorts explicitly helps YouTube categorise short-form content.
    if '#shorts' in description.lower():
        score += 10
    length = len(description)
    if 150 <= length <= 1000:
        score += 25
    elif length > 0:
        score += 10
    return max(0, min(score, 100))


def _score_tags(tags: List[str]) -> int:
    """0-100. Rewards having enough tags for reach without over-stuffing
    (YouTube ignores tags past a certain total character budget, and
    excessive tagging is itself a spam-flag risk anti_spam.py watches for)."""
    if not tags:
        return 0
    count = len(tags)
    if 8 <= count <= 15:
        score = 90
    elif count < 8:
        score = 50 + count * 5
    else:
        score = max(40, 90 - (count - 15) * 5)

    unique_ratio = len(set(t.lower() for t in tags)) / count
    score = int(score * unique_ratio)
    return max(0, min(score, 100))


def calculate_seo_score(title: str, description: str, tags: List[str], script_data: Dict) -> Dict:
    """Overall 0-100 SEO score plus a per-component breakdown, mirroring
    the shape quality_checker.check_script_quality() returns so both can be
    logged/displayed the same way in main.py."""
    hook = script_data.get('hook', '')
    components = {
        'title_score': _score_title(title),
        'description_score': _score_description(description, hook),
        'tags_score': _score_tags(tags),
    }
    overall = round(sum(components.values()) / len(components))
    components['overall_seo_score'] = overall

    if overall >= 85:
        rating = "🟢 EXCELLENT"
    elif overall >= 70:
        rating = "🟡 GOOD"
    elif overall >= 50:
        rating = "🟠 NEEDS WORK"
    else:
        rating = "🔴 POOR"

    return {'scores': components, 'rating': rating}


def generate_seo_package(topic: str, script_data: Dict) -> Dict:
    """Single entry point main.py can call once per video. Returns
    everything the PRD's 'AI SEO Generator' section asks for, scoped to
    what actually applies to a YouTube Short (chapters are skipped - not
    supported on sub-60s videos)."""
    category = get_topic_category(topic)
    tags = generate_seo_tags(topic, category, script_data.get('title', ''))
    title_options = generate_title_options(topic, script_data)
    # Score every candidate and pick the best-scoring one instead of
    # always taking title_options[0] - the score was previously computed
    # only for logging and never actually influenced which title got
    # used, so a weak title could ship even when a stronger option was
    # sitting right there in the list.
    chosen_title = max(title_options, key=_score_title) if title_options else script_data.get('title', 'Untitled')
    description = generate_description(script_data, tags)
    hashtags = generate_hashtags(topic, category)
    pinned_comment = generate_pinned_comment(script_data)
    playlist = suggest_playlist(category)
    seo_score = calculate_seo_score(chosen_title, description, tags, script_data)

    logger.info(f"SEO package built for '{topic}' - score: {seo_score['scores']['overall_seo_score']}/100 ({seo_score['rating']})")

    return {
        'title_options': title_options,
        'chosen_title': chosen_title,
        'description': description,
        'tags': tags,
        'hashtags': hashtags,
        'pinned_comment': pinned_comment,
        'playlist_suggestion': playlist,
        'seo_score': seo_score,
    }


if __name__ == "__main__":
    import json
    test_script = {
        'title': 'Your Heart Has Its Own Brain',
        'hook': "Doctors don't want you to know this about your heart...",
        'cta': 'Follow for more dark body secrets',
        'description': 'Your heart contains its own independent nervous system.',
    }
    result = generate_seo_package("Your Heart Has Its Own Brain", test_script)
    print(json.dumps(result, indent=2, ensure_ascii=False))
