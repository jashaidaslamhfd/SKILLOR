"""Generate the 500-topic MrNextep Body Glitch series catalogue.

Run from repository root:
    python scripts/generate_body_glitch_topics.py

The catalogue intentionally covers familiar, low-risk everyday phenomena.
It is not medical advice and excludes diagnoses, treatment claims and danger
bait. Every record includes a short series title, clean emojis, and thumbnail text.
"""
from __future__ import annotations

import json
from pathlib import Path


def _title_emoji(label: str) -> str:
    """One consistent curiosity emoji, selected from the phenomenon type."""
    lowered = label.lower()
    if any(word in lowered for word in ("eye", "vision", "float", "blink", "pupil", "tear")):
        return "👁️"
    if any(word in lowered for word in ("heart", "pulse", "blood", "vein", "chest", "flush")):
        return "🫀"
    if any(word in lowered for word in ("brain", "memory", "dream", "song", "deja", "think", "mind", "dizzy")):
        return "🧠"
    if any(word in lowered for word in ("stomach", "hunger", "hiccup", "throat", "swallow", "gut", "burp")):
        return "😮"
    if any(word in lowered for word in ("ear", "sound", "ring", "hear", "tinnitus")):
        return "👂"
    if any(word in lowered for word in ("sleep", "yawn", "tired", "rest", "night", "nap")):
        return "😴"
    if any(word in lowered for word in ("hand", "finger", "skin", "shiver", "chill", "wrinkle", "tingle")):
        return "✋"
    return "💡"


# Expanded list of 50 distinct body glitch phenomena
PHENOMENA = [
    ("Eye Twitch", "an eyelid twitching randomly", "EYE TWITCH?"),
    ("Stomach Growls", "your stomach growling when you are not hungry", "STOMACH NOISE?"),
    ("Goosebumps", "goosebumps appearing suddenly when chilled or moved", "WHY CHILLS?"),
    ("Ringing Ears", "your ears ringing in absolute silence", "EARS RING?"),
    ("Sudden Hiccups", "hiccups starting unexpectedly", "WHY HICCUPS?"),
    ("Runny Nose", "your nose running when you cry or eat hot food", "RUNNY NOSE?"),
    ("Wrinkled Hands", "your fingers and hands wrinkling in warm water", "WRINKLED HANDS?"),
    ("Nervous Shivers", "your body shivering during high nervous pressure", "WHY SHIVER?"),
    ("Sudden Blushing", "your face flushing hot when embarrassed", "WHY BLUSH?"),
    ("Spreading Yawns", "yawning spreading instantly from person to person", "WHY YAWN?"),
    ("Laughing Tears", "your eyes watering when you laugh uncontrollably", "LAUGHING TEARS?"),
    ("Brain Freeze", "brain freeze after swallowing cold ice cream", "BRAIN FREEZE?"),
    ("Pins Needles", "pins and needles in your foot after sitting awkwardly", "PINS NEEDLES?"),
    ("Sleeping Foot", "your foot falling asleep and feeling numb", "FOOT ASLEEP?"),
    ("Muscle Twitch", "a muscle twitching on its own under your skin", "MUSCLE TWITCH?"),
    ("Sleep Jerk", "your body sudden jerking as you fall asleep", "SLEEP JERK?"),
    ("Shaky Voice", "your voice shaking when speaking in front of crowds", "SHAKY VOICE?"),
    ("Cold Hands", "your hands feeling cold during stressful moments", "COLD HANDS?"),
    ("Hot Ears", "your ears suddenly burning hot for no clear reason", "HOT EARS?"),
    ("Throat Lump", "a feeling of a lump in your throat when sad", "THROAT LUMP?"),
    ("Phantom Vibrate", "feeling your phone vibrate in your pocket when it didn't", "PHANTOM RING?"),
    ("Eye Floaters", "tiny squiggly shapes floating across your vision", "EYE FLOATERS?"),
    ("Doorway Effect", "forgetting why you entered a room the second you cross the door", "FORGOT WHY?"),
    ("Song Earworm", "having a 5-second song loop stuck in your brain", "SONG STUCK?"),
    ("Photic Sneeze", "sneezing immediately when stepping into bright sunlight", "SUN SNEEZE?"),
    ("Deja Vu", "feeling like you've lived an exact new moment before", "DEJA VU?"),
    ("Hypnic Jerk", "feeling like you are falling right before falling asleep", "FALLING DREAM?"),
    ("Restless Legs", "an irresistible urge to move your legs at bedtime", "RESTLESS LEGS?"),
    ("Auditory Glitch", "hearing someone call your name when no one did", "HEARD NAME?"),
    ("Sleep Paralysis", "waking up unable to move your body for a few seconds", "CAN'T MOVE?"),
    ("Time Compression", "feeling like hours passed in minutes or vice versa", "TIME FLYING?"),
    ("Chills Music", "getting physical chills down your spine listening to music", "MUSIC CHILLS?"),
    ("Cold Sweat", "breaking into a cold sweat when nervous or ill", "COLD SWEAT?"),
    ("Dizzy Standing", "feeling lightheaded right after standing up fast", "DIZZY STANDING?"),
    ("Double Vision", "momentary blurry double vision when sleepy", "DOUBLE VISION?"),
    ("Heart Flutter", "feeling your heart skip a beat or extra flutter", "HEART FLUTTER?"),
    ("Yawn Stretch", "stretching your arms automatically while yawning", "YAWN STRETCH?"),
    ("Sneeze Halt", "a sneeze vanishing right as you are about to blow", "LOST SNEEZE?"),
    ("Tongue Burn", "losing taste sensation after hot coffee", "TONGUE BURN?"),
    ("Heavy Lids", "eyelids feeling ridiculously heavy during mid-day slumps", "HEAVY EYES?"),
    ("Dry Mouth", "your mouth instantly going dry before public speaking", "DRY MOUTH?"),
    ("Gag Reflex", "brushing back teeth triggering a sudden gag", "GAG REFLEX?"),
    ("Muscle Cramp", "a sudden charley horse cramp in your calf at night", "CHARLEY HORSE?"),
    ("Cold Tip Nose", "your nose tip feeling freezing cold indoor", "COLD NOSE?"),
    ("Pop Ears", "your ears popping when changing altitude", "POPPING EARS?"),
    ("Sweaty Palms", "palms sweating excessively during high tension", "SWEATY PALMS?"),
    ("Joint Pop", "knuckles or knees popping loudly when bending", "JOINTS POPPING?"),
    ("Bright Spot Vision", "seeing glowing spots after looking near bright light", "VISION SPOTS?"),
    ("Morning Voice", "your voice sounding noticeably deeper right after waking up", "MORNING VOICE?"),
    ("False Awakening", "dreaming that you woke up and started getting ready", "FALSE WAKE?"),
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
    "Why {phenomenon} happens suddenly",
]


def build_catalogue() -> list[dict]:
    records = []
    number = 1
    for short_label, phenomenon, thumbnail_text in PHENOMENA:
        for angle in ANGLES:
            title = f"{short_label} {_title_emoji(short_label)}"
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
    target.write_text(json.dumps(build_catalogue(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote 500 Body Glitch topics to {target}")


if __name__ == "__main__":
    main()
