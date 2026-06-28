# ... (existing imports) ...

# ═══════════════════════════════════════════════════════════
# BABY NICHE CONFIG — USA Parents (High Emotional Impact)
# ═══════════════════════════════════════════════════════════
@dataclass
class BabyNicheConfig:
    # ── BABY TOPICS ──
    BABY_TOPICS: List[str] = field(default_factory=lambda: [
        "baby brain development",
        "child psychology explained",
        "parenting science",
        "baby milestones",
        "toddler brain growth",
        "newborn development",
        "baby sleep science",
        "breastfeeding brain benefits",
        "baby language development",
        "baby emotions explained",
    ])
    
    # ── BABY KEYWORDS ──
    BABY_KEYWORDS: List[str] = field(default_factory=lambda: [
        "baby brain", "child development", "parenting tips",
        "newborn milestones", "toddler psychology",
        "baby science", "brain growth", "parenting advice",
        "baby learning", "child brain", "mom life",
        "parenting hacks", "baby facts", "child psychology",
    ])
    
    # ── BABY HASHTAGS ──
    BABY_HASHTAGS: List[str] = field(default_factory=lambda: [
        "#BabyBrain", "#ParentingTips", "#ChildDevelopment",
        "#NewbornFacts", "#ToddlerLife", "#BabyScience",
        "#BrainDevelopment", "#ParentingHacks", "#BabyFacts",
        "#ChildPsychology", "#MomLife", "#DadLife",
        "#BabyMilestones", "#ParentingJourney", "#BabyLove",
    ])

# ── INSTANCE ──
BABY_CONFIG = BabyNicheConfig()
