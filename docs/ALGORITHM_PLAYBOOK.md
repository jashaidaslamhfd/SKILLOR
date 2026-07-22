# SKILLOR Algorithm Playbook — YouTube Shorts & Facebook Reels (2026)

> Honest note first: nobody outside Google/Meta can "fetch the algorithm".
> What *is* available are the publicly documented ranking signals, platform
> policy pages, creator-insider disclosures, and large-cohort measurements.
> This playbook maps each confirmed signal to a concrete setting in this
> repo — and marks honestly what remains a manual creator task.
> Re-verify quarterly; feeds change every few months.

---

## 1. YouTube Shorts algorithm (2026) → what we do about it

### Confirmed ranking signals

| Signal | What the feed measures | Where it lives in this repo |
|---|---|---|
| **Viewed vs. swiped** (first 1–3 s decides) | % of shown viewers who don't swipe | Hook gate: scene-1 max 8 words / ≤5 s audio (`MIN_HOOK_SCORE`, `MAX_HOOK_SECONDS`), no cold intros |
| **Retention past 3 s (~50%+ in test cohort) / watch-through** | Test cohorts of 100–1,000 viewers; distribution expands every few hours if thresholds hold (~65% retention sub-30 s, ~50% for 30–60 s) | `TARGET 40–55 s` videos sit in the 30–60 s tier → we optimize for the 50% bar. Story arc enforced in code (Hook→Suspense→Problem→Solution→Payoff→Loop-back) — retries instead of shipping weak arcs |
| **Replays / loop rate** | Seamless rewatches count >100% completion | Loop-back scene (enforced: final scene must echo hook concepts) + `generate_srt` captions + tight 40–55 s runtime make natural loops |
| **Satisfaction & engagement** | Likes/comments/shares per view; post-watch surveys | Pinned comment from SEO package, question-style suspense beats, no fear-bait policy (script prompt), honest-payoff descriptions |
| **Consistency of cadence** | Channel-level reliability signal; quality still beats volume | 3 runs/day, DST-safe gate, 2 h minimum gap (`ENFORCE_POSTING_GAP`), wide windows that absorb GitHub cron delays |
| **First 6–24 h are decisive** | Initial cohort performance expands reach in steps | `publishAt` hits exact US peaks (06:00 / 12:30 / 20:00 NY) so cohorts see videos when Shorts usage peaks |
| **AI-content labeling** | Properly labeled AI = normal distribution; unlabeled realistic AI = suppressed; mass-produced AI w/o human value = demonetized | `containsSyntheticMedia: true` on every upload + `YT_DECLARE_SYNTHETIC_MEDIA=true` |
| **Originality / inauthentic-content policy** | Mass-produced, repetitious, template-spam = YPP removal risk (July 2025 policy rename) | Channel-wide media-hash ledger blocks any repeated visual; 500-topic fixed catalogue with per-episode topics; per-video titles/tags; quality gates reject near-duplicates (`anti_spam.py`, content fingerprints) |

Sources: vexub.com/blog/youtube-shorts-algorithm ·
dataslayer.ai/blog/youtube-algorithm-2025-how-to-get-your-videos-recommended ·
socialpilot.co/youtube-marketing/youtube-algorithm

---

## 2. Facebook Reels algorithm (2026) → what we do about it

| Signal | What Meta measures | Where it lives here |
|---|---|---|
| **Watch time + completion** (top signal) | Completion-weighted distribution boosts | Same arc engineering as YT; captions burned-in (85% watch muted) |
| **Same-day boost (Oct 2025)** | New Reels get ~+50% distribution on day 0 | Daily 3× schedule; `FB_STAGGER_MINUTES=120` so the FB boost fires on its own window, not competing with YouTube's |
| **Shares & saves** (strongest interactions; DMs/Stories accelerate) | Meaningful social interactions over passive likes | Story-arc "worth sharing" payoffs; no beg-CTAs |
| **Engagement-bait demotion** | "Like / share / comment below!" is explicitly punished | Spoken CTA auto-switches to **FB-safe follow-style** when `FB_UPLOAD_ENABLED=true`; FB caption builder strips any slipped bait words (`uploader._build_facebook_description`) |
| **Original content priority** | Reposts, watermarked clips, and unoriginal AI slop suppressed; Meta even compares creator/page identity | No TikTok watermarks ever; all visuals generated fresh per scene + hash ledger; synthetic-media honesty on YT side |
| **UTIS interest surveys (Jan 2026)** | In-feed "how well does this match your interests?" surveys tune recommendations beyond behavior | Sharp micro-niche (Body Glitches) scores high on relevance surveys — niche discipline in `TOPIC_STRATEGY=body_glitch_series`, off-niche trend contamination blocked |
| **Length sweet spot 15–30 s** | Shorter Reels complete ~45% more | Known trade-off: our 40–55 s is optimized for YouTube's 30–60 s tier. If FB becomes a priority channel, add a dedicated ≤30 s FB cut (roadmap item) rather than shortening YouTube |

Sources: posteverywhere.ai/blog/how-the-facebook-algorithm-works ·
outfy.com/blog/facebook-algorithm · socialmediaexaminer.com/facebooks-2026-rules-for-reach-relevance

---

## 3. The 8-beat story arc (enforced, not advisory)

Every script must pass `script_generator._validate_script` arc checks:

1. **HOOK** (scene 1, 6–8 words, ≤5 s) — the surprising glitch, no filler.
2. **SUSPENSE** (scene 2) — must contain an open question (`?`) — enforced.
3. **PROBLEM** (scene 3) — the relatable confusion/myth.
4. **EXPLANATION** (scenes 4–5) — mechanism in plain steps.
5. **NORMAL VS NOTE** (scene 6) — context, no diagnosing.
6. **PAYOFF** (scene 7) — the clear science answer (loop-earning moment).
7. **LOOP-BACK** (scene 8) — must share ≥1 concept word with the hook — enforced.
8. **CTA** (outro scene appended by `main.py`) — platform-safe (see §4).

## 4. CTA policy per platform

| Platform | Spoken CTA (baked in video) | Caption/description CTA |
|---|---|---|
| YouTube | "Follow/subscribe …" allowed | Full like/subscribe nudges OK |
| Facebook (when enabled) | **only** follow-style; bait words blocked in `main.py` | bait words stripped + swapped in `uploader.py` |

Rationale: one audio track serves both platforms; Meta punishes bait,
YouTube tolerates it. The safe common denominator is follow-style —
and "follow for the next one" still converts fine on YouTube.

## 5. Anti-spam guardrails (both platforms)

- 2 h minimum gap enforced (`ENFORCE_POSTING_GAP=true`) — no burst posting.
- 3/day max, each a distinct catalogue topic; content fingerprints + upload
  state block re-uploads (`uploader._existing_youtube_upload`).
- Channel-wide media hash ledger — no image/clip ever repeats across videos.
- Off-niche trend contamination blocked; strict `body_glitch_series` strategy.
- FB/YT staggered (`FB_STAGGER_MINUTES=120`) — no duplicate-minute crossfire.
- No engagement bait, fear bait, fake urgency, or "doctors don't want you
  to know" phrasing (script prompt + `anti_spam.py` + medical-accuracy pass
  with auto-disclaimer).

## 6. Monetization guardrails (YPP / FB monetization)

1. **AI disclosure is always on** (`containsSyntheticMedia`) — unlabeled
   realistic AI is a suppression/demonetization path; labeled AI is not.
2. **Originality**: fresh visuals per scene, per-episode topics, unique
   metadata. Avoid the "mass-produced template" pattern the July-2025 YPP
   policy targets: keep quality gates at 85, and review one video daily.
3. **Medical safety**: accuracy check + auto-disclaimer; titles are factual,
   not fear-bait (advertiser-friendly category).
4. **Music licensing**: verify tracks per `assets/music/ATTRIBUTION.md`
   before turning monetization on.
5. **Human-in-the-loop**: YouTube's policies still reward visible creator
   involvement — pin comments, answer 5–10 comments/day, occasional
   Community post. This is the one part automation cannot fake.
6. **Kids/audience settings**: `YT_MADE_FOR_KIDS=false` — correct for
   science-mystery content; wrong settings kill monetization eligibility.

## 7. 14-day channel-revival plan (why "days, not months" is realistic)

Shorts distribution reacts within **hours**: each video is tested on a
100–1,000-viewer cohort; pass the retention bar and reach expands in steps
through the first 6–24 h. A revived *cadence* fixes the compound signal
within days:

- **Days 1–3**: 3 videos/day at exact slots (06:00/12:30/20:00 NY).
  Fix any fail-fast secret errors immediately. Goal: zero skipped slots.
- **Days 4–7**: check YouTube Studio → Content → Shorts → "Viewed vs
  swiped away" — kill any Episode pattern under ~65% swipe-survival by
  tightening hooks (edit `score_hook` weights if a pattern emerges).
- **Days 8–14**: `python src/analytics_updater.py` runs daily in Actions;
  cross-reference `data/video_history.json` hook_score vs actual views.
  Feed winners back: prefer catalogue topics adjacent to top-quartile
  videos (same pillar keywords).
- **Throughout**: reply to first-hour comments (session signal), pin the
  generated pinned-comment, zero off-niche uploads.
- **Do not**: buy engagement, repost watermarked clips, or spike volume
  >3/day — all three are distribution-killers on both platforms.

## 8. Roadmap (not yet automated)

- ≤30 s **Facebook-native cut** of each video (FB completion rates).
- Winner-topic feedback loop auto-weighting catalogue selection from
  `analytics_updater` metrics (currently manual, §7 day 8–14).
- GPU voice-clone runner for a truly unique channel voice.
