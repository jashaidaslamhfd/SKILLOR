"""Generate the 500-topic MrNextep Body Glitch series catalogue.

Run from repository root:
    python scripts/generate_body_glitch_topics.py

The catalogue intentionally covers familiar, low-risk everyday phenomena.
It is not medical advice and excludes diagnoses, treatment claims and danger
bait. Every record includes a short five-word series title and thumbnail text.
"""
from __future__ import annotations

import json
from pathlib import Path

# (short title label, detailed topic wording, thumbnail text)
PHENOMENA = [
    ("Eye Twitch", "an eyelid twitching randomly", "EYE TWITCH?"),
    ("Stomach Growls", "your stomach growling when you are not hungry", "STOMACH NOISE?"),
    ("Goosebumps", "goosebumps appearing suddenly", "WHY CHILLS?"),
    ("Ringing Ears", "your ears ringing in silence", "EARS RING?"),
    ("Sudden Hiccups", "hiccups starting suddenly", "WHY HICCUPS?"),
    ("Runny Nose", "your nose running when you cry", "RUNNY NOSE?"),
    ("Wrinkled Hands", "your hands wrinkling in water", "WRINKLED HANDS?"),
    ("Nervous Shivers", "your body shivering when you feel nervous", "WHY SHIVER?"),
    ("Sudden Blushing", "your face blushing when embarrassed", "WHY BLUSH?"),
    ("Spreading Yawns", "yawning spreading from person to person", "WHY YAWN?"),
    ("Laughing Tears", "your eyes watering when you laugh", "LAUGHING TEARS?"),
    ("Brain Freeze", "brain freeze after cold food", "BRAIN FREEZE?"),
    ("Pins Needles", "pins and needles after sitting oddly", "PINS NEEDLES?"),
    ("Sleeping Foot", "your foot falling asleep", "FOOT ASLEEP?"),
    ("Muscle Twitch", "a muscle twitching on its own", "MUSCLE TWITCH?"),
    ("Sleep Jerk", "your body jerking as you fall asleep", "SLEEP JERK?"),
    ("Shaky Voice", "your voice shaking when nervous", "SHAKY VOICE?"),
    ("Cold Hands", "your hands feeling cold under stress", "COLD HANDS?"),
    ("Hot Ears", "your ears suddenly feeling hot", "HOT EARS?"),
    ("Sweaty Palms", "your palms sweating when nervous", "SWEATY PALMS?"),
    ("Stomach Butterflies", "butterflies in your stomach before something important", "BUTTERFLIES?"),
    ("Throat Lump", "a lump in your throat when emotional", "THROAT LUMP?"),
    ("Dry Mouth", "your mouth going dry when nervous", "DRY MOUTH?"),
    ("Clicking Jaw", "your jaw clicking when you chew", "JAW CLICK?"),
    ("Cracking Knees", "your knees cracking when you move", "KNEES CRACK?"),
    ("Stomach Drop", "your stomach dropping during a scare", "STOMACH DROP?"),
    ("Racing Heart", "your heart racing when nervous", "HEART RACING?"),
    ("Standing Dizzy", "feeling dizzy after standing up", "STAND DIZZY?"),
    ("Light Sneezes", "sneezing in bright light", "LIGHT SNEEZE?"),
    ("Eye Floaters", "seeing eye floaters in bright light", "EYE FLOATERS?"),
    ("Phantom Buzz", "feeling a phone buzz that did not happen", "PHONE BUZZ?"),
    ("Stuck Songs", "a song getting stuck in your head", "SONG STUCK?"),
    ("Deja Vu", "deja vu feeling strangely familiar", "DEJA VU?"),
    ("Room Forgetting", "forgetting why you entered a room", "WHY HERE?"),
    ("Name Forgetting", "forgetting a name right after hearing it", "NAME GONE?"),
    ("Night Memories", "embarrassing memories returning at night", "WHY REMEMBER?"),
    ("Body Alarm", "waking up before your alarm", "BEFORE ALARM?"),
    ("Heartbeat Sound", "hearing your heartbeat at night", "HEART SOUND?"),
    ("Fast Hunger", "getting hungry at the same time daily", "WHY HUNGRY?"),
    ("Mood Music", "music changing your mood quickly", "MUSIC MOOD?"),
    ("Silent Discomfort", "silence feeling uncomfortable", "AWKWARD SILENCE?"),
    ("Name Notice", "your brain noticing your own name", "HEARD MY NAME?"),
    ("Time Speed", "time feeling faster as you get older", "TIME FASTER?"),
    ("Deep Sleep", "your brain needing deep sleep", "DEEP SLEEP?"),
    ("Green Vision", "seeing more shades of green", "WHY GREEN?"),
    ("Stress Memory", "stress making it hard to remember", "STRESS MEMORY?"),
    ("Cold Shiver", "shivering when you feel cold", "COLD SHIVER?"),
    ("Tired Body", "your body feeling heavy when tired", "BODY HEAVY?"),
    ("Body Freeze", "your body freezing when scared", "BODY FREEZE?"),
    ("Dream Vanish", "dreams disappearing after you wake up", "DREAM GONE?"),
]

ANGLES = [
    "Why {phenomenon} happens",
    "The simple science behind {phenomenon}",
    "What your body does during {phenomenon}",
    "Why {phenomenon} feels so strange",
    "The real reason for {phenomenon}",
    "What triggers {phenomenon}",
    "Why your brain notices {phenomenon}",
    "The body signal behind {phenomenon}",
    "What changes inside you during {phenomenon}",
    "Why {phenomenon} can feel sudden",
]


def build_catalogue() -> list[dict]:
    records = []
    number = 1
    for short_label, phenomenon, thumbnail_text in PHENOMENA:
        for angle in ANGLES:
            # Body Glitch #001: Eye Twitch = five title words in YouTube's
            # practical tokenization: Body / Glitch / 001 / Eye / Twitch.
            title = f"Body Glitch #{number:03d}: {short_label}"
            records.append({
                "series_number": number,
                "series_title": title,
                "topic": phenomenon,
                "angle": angle.format(phenomenon=phenomenon),
                "thumbnail_text": thumbnail_text,
                "pillar": "weird_body_glitches",
            })
            number += 1
    assert len(records) == 500
    return records


def main() -> None:
    target = Path(__file__).resolve().parents[1] / "data" / "body_glitch_topics.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_catalogue(), indent=2), encoding="utf-8")
    print(f"Wrote 500 Body Glitch topics to {target}")


if __name__ == "__main__":
    main()
