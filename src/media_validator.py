"""Strict media checks used before rendering and uploading."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict

import numpy as np
from PIL import Image, ImageStat


class MediaValidationError(RuntimeError):
    pass


def validate_scene_image(path: str, min_side: int = 512) -> Dict:
    """Decode an image and reject error pages, corrupt, tiny or black assets."""
    if not path or not os.path.isfile(path):
        raise MediaValidationError(f"Image does not exist: {path}")
    try:
        with Image.open(path) as probe:
            probe.verify()
        with Image.open(path) as image:
            image = image.convert("RGB")
            width, height = image.size
            if min(width, height) < min_side:
                raise MediaValidationError(f"Image too small: {width}x{height}")
            sample = np.asarray(image.resize((64, 64)), dtype=np.float32)
            brightness = float(sample.mean())
            variation = float(sample.std())
            if brightness < 12.0:
                raise MediaValidationError(f"Near-black image: brightness={brightness:.1f}")
            if variation < 2.0:
                raise MediaValidationError(f"Almost blank image: variation={variation:.1f}")
            return {"width": width, "height": height, "brightness": brightness, "variation": variation}
    except MediaValidationError:
        raise
    except Exception as exc:
        raise MediaValidationError(f"Invalid image {path}: {exc}") from exc


def probe_video(path: str) -> Dict:
    """Use ffprobe to enforce a playable 9:16 Short with audio."""
    if not os.path.isfile(path) or os.path.getsize(path) < 100_000:
        raise MediaValidationError(f"Video missing or too small: {path}")
    command = [
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", path,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=True)
        data = json.loads(result.stdout)
    except Exception as exc:
        raise MediaValidationError(f"ffprobe failed: {exc}") from exc

    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise MediaValidationError("Rendered file must contain video and audio streams")
    width, height = int(video.get("width", 0)), int(video.get("height", 0))
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)
    if (width, height) != (1080, 1920):
        raise MediaValidationError(f"Wrong canvas {width}x{height}; expected 1080x1920")
    max_seconds = float(os.environ.get("TARGET_MAX_SECONDS", "55")) + 0.25
    if duration <= 0 or duration > max_seconds:
        raise MediaValidationError(f"Wrong duration {duration:.2f}s; maximum {max_seconds:.2f}s")
    return {"width": width, "height": height, "duration": duration}
