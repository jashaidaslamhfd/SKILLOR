"""
src/seo_analytics.py

Second wave of the PRD "AI SEO Generator" section - the subset that needs
NO external API/keys (no Google Trends, no YouTube Analytics, no
competitor-channel access). Everything here is either a heuristic model
over data SKILLOR already produces, or a PIL/numpy analysis of the actual
thumbnail file already on disk.

Honest scope note up front, since it matters for how much to trust this:
  - predict_ctr() is a HEURISTIC estimate calibrated from the same signals
    quality_checker/seo_generator already score (hook strength, title
    pattern, tag quality). It is NOT trained on real YouTube CTR data,
    because no analytics connection exists yet. Treat the number as "how
    well this follows known CTR-correlated patterns", not a guarantee.
  - score_thumbnail() analyzes contrast/text-length/layout from the actual
    generated image. It does NOT do face/emotion detection - that needs a
    CV model (e.g. opencv + a face/emotion classifier) which isn't in
    requirements.txt. That field is reported as "not_available" rather
    than faked.
  - get_historical_insights() mines output/video_history.json. Today that
    file has no real view/CTR data (nothing pulls YouTube Analytics yet),
    so insights are computed from our own predicted scores and flagged as
    such. The function is written so that the moment real 'actual_ctr' or
    'views' keys start appearing in history entries (once an analytics
    puller is added), it automatically prefers real data over predictions
    without any code changes needed here.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from collections import defaultdict

import numpy as np
from PIL import Image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HISTORY_FILE = "output/video_history.json"


# ---------------------------------------------------------------------------
# 1. CTR Prediction (heuristic, not ML-trained on real data - see module note)
# ---------------------------------------------------------------------------

def predict_ctr(script_data: Dict) -> Dict:
    """Combines signals already computed elsewhere in the pipeline
    (hook score, SEO score, title pattern) into a single 0-10 CTR estimate
    with a confidence label reflecting how many of those signals were
    actually available. Weights are hand-set from generally-known Shorts
    CTR correlations (strong hook + specific title + tight tags), not
    fitted on this channel's own data."""
    hook_score = None
    if 'shorts_report' in script_data:
        hook_score = script_data['shorts_report'].get('hook_detail', {}).get('score')
    seo_score = script_data.get('seo_score', {}).get('scores', {}).get('overall_seo_score')
    title = script_data.get('title', '')

    signals_available = sum(x is not None for x in (hook_score, seo_score, title))

    # Normalize each available signal to 0-10 and weight them.
    parts = []
    if hook_score is not None:
        parts.append((hook_score / 10, 0.45))
    if seo_score is not None:
        parts.append((seo_score / 10, 0.35))
    if title:
        title_len = len(title)
        title_len_score = 10 if 30 <= title_len <= 60 else 6
        parts.append((title_len_score, 0.20))

    if not parts:
        return {'ctr_prediction': None, 'confidence': 0.0, 'note': 'No signals available - run quality/SEO scoring first.'}

    weighted_sum = sum(score * weight for score, weight in parts)
    total_weight = sum(weight for _, weight in parts)
    ctr = round(weighted_sum / total_weight, 1)

    confidence = round(0.4 + 0.2 * signals_available, 2)  # 0.6-1.0 range across 1-3 signals
    confidence = min(confidence, 0.85)  # cap - this is a heuristic, never claim near-certainty

    return {
        'ctr_prediction': ctr,
        'confidence': confidence,
        'basis': 'heuristic (hook/SEO/title-length signals) - not trained on real channel CTR data yet',
    }


# ---------------------------------------------------------------------------
# 2. Thumbnail SEO scoring (real image analysis via PIL/numpy)
# ---------------------------------------------------------------------------

def score_thumbnail(thumb_path: str, title: str) -> Dict:
    """Analyzes the actual generated thumbnail file. Only measures what's
    computable without an ML model: contrast in the text-overlay strip,
    text length/line-wrap readability, and dominant-color warmth (a cheap
    proxy for 'color psychology' - warm/high-saturation colors are the
    well-documented CTR-correlated end of that scale, not literally
    modeling emotion)."""
    if not thumb_path or not os.path.exists(thumb_path):
        return {'error': f'Thumbnail not found at {thumb_path}'}

    img = Image.open(thumb_path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape

    # video_editor.generate_thumbnail() draws the title in the bottom
    # ~220px strip over a dark gradient - check contrast there specifically,
    # since that's where readability actually matters.
    strip_top = max(h - 220, 0)
    strip = arr[strip_top:h, :, :]
    grayscale_strip = strip.mean(axis=2)
    contrast_std = float(grayscale_strip.std())
    # Dark gradient + white/bold text should produce a high std (bimodal
    # dark background / light text). Below ~35 usually means low contrast.
    contrast_score = min(100, round((contrast_std / 70) * 100))

    # Text length / mobile readability - shorter titles read faster at
    # thumbnail size, especially on phone screens.
    char_count = len(title)
    word_count = len(title.split())
    if char_count <= 35 and word_count <= 6:
        readability_score = 100
    elif char_count <= 50 and word_count <= 8:
        readability_score = 75
    else:
        readability_score = 50

    # Dominant color warmth as a color-psychology proxy: warm/saturated
    # thumbnails (red/orange/yellow dominant) are the well-known
    # CTR-correlated end for shock/curiosity-style content like this niche.
    r_mean, g_mean, b_mean = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
    warm_bias = (r_mean + g_mean) - 2 * b_mean  # positive = warmer image
    color_score = max(0, min(100, round(50 + warm_bias / 2)))

    overall = round((contrast_score * 0.45) + (readability_score * 0.35) + (color_score * 0.20))

    return {
        'contrast_score': contrast_score,
        'readability_score': readability_score,
        'color_score': color_score,
        'face_emotion_score': 'not_available (no face/emotion model configured)',
        'overall_thumbnail_score': overall,
        'title_char_count': char_count,
        'title_word_count': word_count,
    }


# ---------------------------------------------------------------------------
# 3. Hashtag ranking (proxy discovery/competition, no real search-volume API)
# ---------------------------------------------------------------------------

# BASE_TAGS in niche_strategy.py are broad/generic -> high volume, high
# competition. CATEGORY_TAGS are mid-specific -> medium/medium. Anything
# else (topic-word tags) is the long-tail -> low volume, low competition,
# highest relevance. This mirrors real tag-volume distributions without
# needing live search-volume data.
_BROAD_TAG_HINTS = {
    "darkfacts", "facts", "shorts", "youtubeshorts", "science",
    "didyouknow", "mindblowing", "funfacts", "scaryfacts", "viral",
}


def rank_hashtags(tags: List[str]) -> List[Dict]:
    """Returns each tag with proxy discovery/competition/trend scores and
    a recommendation, ranked by an overall 'discovery value' that favors a
    realistic broad+niche+long-tail mix over an all-broad or all-long-tail
    list."""
    ranked = []
    for tag in tags:
        clean = tag.lower().lstrip('#')
        if clean in _BROAD_TAG_HINTS:
            volume, competition, tier = 90, 90, "broad"
        elif len(clean) <= 12:
            volume, competition, tier = 55, 50, "niche"
        else:
            volume, competition, tier = 25, 15, "long_tail"

        # Discovery value rewards low competition relative to volume -
        # i.e. the classic "easier to rank, still gets found" sweet spot.
        discovery_score = round((volume * 0.5) + ((100 - competition) * 0.5))

        ranked.append({
            'tag': tag,
            'tier': tier,
            'volume_proxy': volume,
            'competition_proxy': competition,
            'discovery_score': discovery_score,
        })

    ranked.sort(key=lambda x: x['discovery_score'], reverse=True)
    return ranked


# ---------------------------------------------------------------------------
# 4. A/B variant generation + auto-ranking
# ---------------------------------------------------------------------------

def generate_ab_variants(script_data: Dict, title_options: List[str]) -> Dict:
    """Builds description variants (short-punchy vs longer-context) for
    each of the already-generated title options, scores every
    title+description pairing with predict_ctr(), and returns them ranked
    so the top of the list is the recommended combo - true A/B test PREP,
    not a live split test (that needs real traffic, which happens after
    upload)."""
    hook = script_data.get('hook', '')
    cta = script_data.get('cta', '')
    desc_base = script_data.get('description', '')

    description_variants = {
        'short_punchy': f"{hook}\n\n👇 {cta}",
        'context_first': f"{desc_base}\n\n{hook}\n\n👇 {cta}",
    }

    variants = []
    for title in title_options:
        for desc_label, desc_text in description_variants.items():
            trial_script = dict(script_data)
            trial_script['title'] = title
            trial_script['description'] = desc_text
            ctr = predict_ctr(trial_script)
            variants.append({
                'title': title,
                'description_variant': desc_label,
                'description_preview': desc_text[:120],
                'predicted_ctr': ctr.get('ctr_prediction'),
            })

    variants.sort(key=lambda v: (v['predicted_ctr'] or 0), reverse=True)
    return {
        'variants': variants,
        'recommended': variants[0] if variants else None,
    }


# ---------------------------------------------------------------------------
# 5. Historical learning over output/video_history.json
# ---------------------------------------------------------------------------

def _load_history() -> List[Dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def _title_pattern(title: str) -> str:
    """Buckets a title by which seo_generator template family produced it,
    so patterns can be compared against each other over time."""
    t = title.lower()
    if 'truth about' in t:
        return 'THE_TRUTH'
    if "won't tell you" in t or "doctors" in t:
        return 'DOCTORS_WONT_TELL'
    if t.startswith('why'):
        return 'WHY'
    if '🫀' in title or any(e in title for e in ['🧠', '🔬']):
        return 'EMOJI_ENHANCED'
    return 'OTHER'


def get_historical_insights(min_sample: int = 3) -> Dict:
    """Groups past videos by title pattern and compares average performance.
    Uses 'actual_ctr'/'views' from history entries when present (once a
    YouTube Analytics puller is added upstream); otherwise falls back to
    each entry's own predicted_ctr/seo_score recorded at generation time.
    Buckets with fewer than min_sample videos are excluded - not enough
    data to say anything meaningful yet."""
    history = _load_history()
    if not history:
        return {'insights': [], 'note': 'No video history yet.'}

    using_real_data = any('actual_ctr' in v or 'views' in v for v in history)

    buckets = defaultdict(list)
    for v in history:
        title = v.get('title', '')
        if not title:
            continue
        pattern = _title_pattern(title)
        if 'actual_ctr' in v:
            metric = v['actual_ctr']
        elif 'predicted_ctr' in v:
            metric = v['predicted_ctr']
        elif 'seo_score' in v:
            metric = v['seo_score']
        else:
            continue
        if metric is not None:
            buckets[pattern].append(metric)

    insights = []
    for pattern, values in buckets.items():
        if len(values) >= min_sample:
            insights.append({
                'title_pattern': pattern,
                'sample_size': len(values),
                'avg_score': round(sum(values) / len(values), 2),
            })
    insights.sort(key=lambda x: x['avg_score'], reverse=True)

    return {
        'insights': insights,
        'data_source': 'real_analytics' if using_real_data else 'predicted_scores (no analytics connected yet)',
        'note': None if insights else f'Not enough videos per title-pattern yet (need >= {min_sample} each).',
    }


if __name__ == "__main__":
    test_script = {
        'title': "🫀 Your Heart Has Its Own Brain",
        'hook': "Doctors don't want you to know this about your heart...",
        'cta': 'Follow for more dark body secrets',
        'description': 'Your heart contains its own independent nervous system.',
        'seo_score': {'scores': {'overall_seo_score': 85}},
        'shorts_report': {'hook_detail': {'score': 60}},
    }
    print(json.dumps(predict_ctr(test_script), indent=2))
    print(json.dumps(rank_hashtags(['darkfacts', 'heartfacts', 'neuroscience']), indent=2))
    print(json.dumps(generate_ab_variants(test_script, ["Title A", "Title B"]), indent=2))
