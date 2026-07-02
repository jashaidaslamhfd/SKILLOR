import random
from datetime import datetime

# 2026 USA Trends - High CTR topics
TRENDING_TOPICS = {
    'mystery': [
        "Area 51 whistleblower 2026 leak",
        "FBI declassified files that vanished",
        "GPS coordinates banned by Google Maps",
        "The sound NASA recorded in space",
        "Flight 370 new evidence 2026"
    ],
    'science': [
        "Why time stops in black hole - visual proof",
        "NASA found ocean on Mars yesterday",
        "Your phone is listening - MIT study",
        "We live in simulation - new code found",
        "Quantum computer broke physics last week"
    ],
    'human_behaviour': [
        "Why you can't stop scrolling - brain scan",
        "Psychology of people who don't text back",
        "Your sleeping position reveals trauma",
        "144 times: phone check addiction test",
        "Why we like toxic people - dopamine trap"
    ]
}

# High CTR keywords - title me hone chahiye
VIRAL_KEYWORDS = ['secret', 'banned', 'deleted', 'lied', 'hidden', 'shock', 'truth', 'warning', 'stop', 'wait']

def select_topic(niche='auto'):
    """
    Swap Rate Fix: Sirf viral topic dega
    CTR 8%+ guarantee topics only
    """
    if niche == 'auto':
        # Human behaviour USA me best chal raha 2026
        niche = 'human_behaviour'

    topics = TRENDING_TOPICS.get(niche, TRENDING_TOPICS['human_behaviour'])

    # Trend boost: Weekend pe 'mystery', Weekday pe 'human_behaviour'
    weekday = datetime.now().weekday()
    if weekday >= 5 and niche!= 'mystery': # Sat-Sun
        topics = TRENDING_TOPICS['mystery']
        niche = 'mystery'

    topic = random.choice(topics)

    # CTR boost: ensure viral keyword hai
    if not any(kw in topic.lower() for kw in VIRAL_KEYWORDS):
        topic = f"The hidden {topic}"

    print(f"[Topic] Selected: {topic} | Niche: {niche}")
    return topic, niche
