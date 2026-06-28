# ============================================================
# BABY HOOKS - FORCED ATTENTION
# ============================================================
BABY_HOOKS = [
    # ── Urgency Hooks (Forced Attention) ──
    "Your baby's brain is growing RIGHT NOW at 100,000 new neurons every minute...",
    "The first 1000 days decide your child's entire future brain power...",
    "What your baby's brain is secretly doing while they sleep will AMAZE you...",
    "Your newborn's brain has already started THIS incredible process...",
    "The one thing that builds your baby's brain faster than ANYTHING else...",
    "Your baby's brain has MORE connections than stars in the galaxy...",
    "This simple activity TRIPLES your baby's brain growth...",
    "Your baby's brain is ALREADY processing language before they speak...",
    "The surprising reason your baby cries — it's brain development...",
    "Your child's brain is doing THIS every single night without fail...",
    
    # ── Curiosity Hooks (Forced Watching) ──
    "Nobody tells you what your baby's brain is doing RIGHT NOW...",
    "What your baby's brain does during tummy time is INCREDIBLE...",
    "The science behind your baby's first smile is BRAIN GROWTH...",
    "Your toddler's brain is wired for THIS — and it's AMAZING...",
    "Your baby's brain is built through play — here's HOW...",
    "The first year of brain development changes EVERYTHING...",
    "Your baby's brain can do THIS before they can even talk...",
    "What happens in your baby's brain when you sing to them...",
    "Your baby's brain processes YOUR voice differently than others...",
]

# ============================================================
# BABY CTAS - FORCED ENGAGEMENT (Like + Comment + Share)
# ============================================================
BABY_CTAS = [
    # ── Forced Like ──
    "👍 DOUBLE TAP if your baby does this!",
    "❤️ Like if you're AMAZED by your baby's brain!",
    "👍 Hit LIKE if you knew this about your baby!",
    "❤️ Like if this BLEW YOUR MIND about babies!",
    
    # ── Forced Comment ──
    "👇 Comment 'BABY' if your little one does this too!",
    "💬 What does YOUR baby do that amazes you? Comment below!",
    "👇 Does YOUR baby do this? Comment YES or NO!",
    "💬 Tag a NEW PARENT who needs to see this!",
    "👇 Comment 'ME' if this is YOUR baby!",
    "💬 Share YOUR baby's milestone in the comments!",
    
    # ── Forced Share ──
    "📌 SAVE this — every parent needs to know this!",
    "🗣️ SHARE this with every new mom you know!",
    "📌 SHARE with a parent who has a baby under 1!",
    "🗣️ TAG someone who needs to see this baby science!",
    
    # ── Combined (Forced Like + Comment) ──
    "👍 Like AND Comment 'BRAIN' if you love baby science!",
    "❤️ Like AND Share if you want more baby brain tips!",
    "👍 Like AND Tag a new parent in the comments!",
]

# ============================================================
# GENERATE SCRIPT - FORCED ENGAGEMENT
# ============================================================
def generate_script(self, topic: str, angle: str = "",
                    shock_angle: str = "", pattern: str = "memory_insight",
                    suspense_score: int = 70) -> Dict:
    """Generate complete script with FORCED engagement hooks"""
    
    print(f"\n🎬 Generating script for: {topic}")
    
    # ═══════════════════════════════════════════════════════════
    # FIX: Use BABY hooks (strong, emotional, curiosity-driven)
    # ═══════════════════════════════════════════════════════════
    hook = random.choice(BABY_HOOKS)
    print(f"   Hook: '{hook}'")
    
    # ── Generate rest of script ──
    prompt = format_prompt(
        VIRAL_SCRIPT_GENERATOR,
        topic=topic,
        angle=angle or f"Understanding your baby's brain development",
        shock_angle=shock_angle or f"your baby's brain is quietly processing everything",
    )
    
    raw = self._call_groq(prompt, max_tokens=500) if self.client else ""
    
    # ── Extract parts ──
    shock = self._clean(self._extract("SHOCK", raw))
    suspense = self._clean(self._extract("SUSPENSE", raw))
    story = self._clean(self._extract("STORY", raw))
    ctr = self._clean(self._extract("CTR", raw))
    
    # ── Fallbacks ──
    if not shock:
        shock = self._get_unique_shock_fact()
    
    if not suspense:
        suspense = "And the reason behind this might explain everything about your baby's development..."
    
    if not story:
        story = f"The science behind {topic} is simpler than you'd think. Your baby's brain is actually building thousands of new connections every single second. And the part that really matters is how deeply your baby learns from you, even when you're not trying to teach them."
    
    if not ctr:
        ctr = random.choice(BABY_CTAS)
    
    # ── Build segments with FORCED CTAs ──
    wps = AUDIO_CONFIG.WORDS_PER_MINUTE / 60.0
    segments = []
    t = 0.0
    
    def add_segment(stype, text, is_pause=False, dur=None):
        nonlocal t
        if not text and not is_pause:
            return
        if is_pause:
            duration = dur or 0.4
        else:
            duration = dur or round(len(text.split()) / wps, 2)
        segments.append({
            'type': stype,
            'text': '' if is_pause else text,
            'duration': duration,
            'start': round(t, 2),
            'is_pause': is_pause
        })
        t += duration
    
    add_segment('hook', hook)
    add_segment('pause', '', is_pause=True, dur=0.5)
    add_segment('shock', shock)
    add_segment('pause', '', is_pause=True, dur=0.3)
    add_segment('suspense', suspense)
    add_segment('pause', '', is_pause=True, dur=0.4)
    
    # Split story
    if '...' in story:
        parts = story.split('...', 1)
        add_segment('story', parts[0].strip() + '...')
        add_segment('pause', '', is_pause=True, dur=0.4)
        if parts[1].strip():
            add_segment('story', parts[1].strip())
    else:
        words = story.split()
        mid = len(words) // 2
        if mid > 3:
            add_segment('story', ' '.join(words[:mid]) + '...')
            add_segment('pause', '', is_pause=True, dur=0.35)
            add_segment('story', ' '.join(words[mid:]))
        else:
            add_segment('story', story)
    
    add_segment('pause', '', is_pause=True, dur=0.4)
    
    # ═══════════════════════════════════════════════════════════
    # FIX: Add FORCED CTA (Like + Comment + Share)
    # ═══════════════════════════════════════════════════════════
    cta = random.choice(BABY_CTAS)
    add_segment('ctr', cta)
    
    full_script = ' '.join(s['text'] for s in segments if not s.get('is_pause'))
    word_count = len(full_script.split())
    
    print(f"   Words: {word_count}")
    print(f"   Duration: {round(t, 2)}s")
    print(f"   CTA: '{cta}'")
    
    return {
        'full_script': full_script,
        'segments': segments,
        'word_count': word_count,
        'duration': round(t, 2),
        'hook': hook,
        'hook_score': 9,
        'shock': shock,
        'suspense': suspense,
        'story': story,
        'ctr': cta
                        }
