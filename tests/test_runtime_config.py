"""Regression tests for the runtime-config bugs fixed in the US-audience
refactor. Every test here maps to a bug that once shipped to production."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


class GitignoreSafetyTests(unittest.TestCase):
    """A `git add .` must never be able to commit credentials or the private
    voice reference (this trap existed: oauth_backup.json was written into
    the repo root with no ignore pattern)."""

    def setUp(self):
        self.gitignore = (ROOT / ".gitignore").read_text()

    def test_token_artifacts_are_ignored(self):
        for pattern in ("oauth_backup.json", "client_secrets*.json", "token*.json"):
            self.assertIn(pattern, self.gitignore, f".gitignore missing {pattern}")

    def test_voice_reference_is_ignored_and_untracked(self):
        self.assertIn("assets/voice_reference.wav", self.gitignore)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "assets/voice_reference.wav"],
            cwd=ROOT, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0, "voice reference must not be git-tracked")


class RequirementsTests(unittest.TestCase):
    """Every third-party top-level import must be declared somewhere."""

    @staticmethod
    def _declared_packages(text: str) -> str:
        """Only real requirement lines — comments must not count (the core
        file's footer NOTES mention removed packages by name)."""
        lines = [ln.split("#", 1)[0].strip() for ln in text.splitlines()]
        return "\n".join(ln for ln in lines if ln)

    def setUp(self):
        self.core = self._declared_packages((ROOT / "requirements.txt").read_text().lower())
        self.optional = self._declared_packages((ROOT / "requirements-optional.txt").read_text().lower())

    def test_previously_missing_imports_are_declared(self):
        self.assertIn("feedparser", self.core)   # scripts/fetch_trending_now.py crashed without it
        self.assertIn("edge-tts", self.core)     # emergency cloud TTS was undeclared

    def test_unused_google_genai_removed_from_core(self):
        self.assertNotIn("google-genai", self.core)

    def test_voice_clone_stack_is_optional_only(self):
        for pkg in ("chatterbox-tts", "torchaudio", "transformers"):
            self.assertNotIn(pkg, self.core)
            self.assertIn(pkg, self.optional)


class EnvWiringTests(unittest.TestCase):
    """The workflow's env vars must actually be read by code (the old
    KOKORO_VOICE/KOKORO_LANG_CODE/TTS_ENGINE/CHANNEL_LANGUAGE block was
    completely decorative — French config silently produced US audio)."""

    def test_kokoro_envs_are_honored(self):
        voice_generator = pytestless_import("voice_generator")
        old = {k: os.environ.get(k) for k in ("KOKORO_VOICE", "KOKORO_LANG_CODE", "TTS_ENGINE")}
        try:
            os.environ["KOKORO_VOICE"] = "af_heart"
            os.environ["KOKORO_LANG_CODE"] = "b"
            os.environ["TTS_ENGINE"] = "kokoro"
            import importlib
            importlib.reload(voice_generator)
            self.assertEqual(voice_generator.KOKORO_VOICE, "af_heart")
            self.assertEqual(voice_generator.KOKORO_LANG_CODE, "b")
            self.assertEqual(voice_generator.TTS_ENGINE, "kokoro")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            import importlib
            importlib.reload(voice_generator)

    def test_invalid_tts_engine_falls_back(self):
        voice_generator = pytestless_import("voice_generator")
        old = os.environ.get("TTS_ENGINE")
        try:
            os.environ["TTS_ENGINE"] = "banana"
            import importlib
            importlib.reload(voice_generator)
            self.assertEqual(voice_generator.TTS_ENGINE, "chatterbox")
        finally:
            if old is None:
                os.environ.pop("TTS_ENGINE", None)
            else:
                os.environ["TTS_ENGINE"] = old
            import importlib
            importlib.reload(voice_generator)


def pytestless_import(name):
    """Import a src module, skipping cleanly when its heavy deps are absent."""
    try:
        import importlib
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(f"{name} deps not installed here: {exc}")


class PublishAtTests(unittest.TestCase):
    """YT_SCHEDULE_PUBLISH was a dead env var with no publishAt logic; the
    helper must now always return a future US-peak slot in UTC."""

    def test_publish_at_is_future_peak_slot(self):
        uploader = pytestless_import("uploader")
        old = os.environ.get("YT_SCHEDULE_PUBLISH")
        try:
            from datetime import datetime, timedelta
            import pytz
            os.environ["YT_SCHEDULE_PUBLISH"] = "true"
            publish_at = uploader._compute_publish_at()
            parsed = datetime.strptime(publish_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
            self.assertGreaterEqual(parsed, datetime.now(pytz.UTC) + timedelta(minutes=25))
            slot_ny = parsed.astimezone(pytz.timezone("America/New_York"))
            self.assertIn((slot_ny.hour, slot_ny.minute), [(6, 0), (12, 30), (20, 0)])
        finally:
            if old is None:
                os.environ.pop("YT_SCHEDULE_PUBLISH", None)
            else:
                os.environ["YT_SCHEDULE_PUBLISH"] = old


class PublicApiTests(unittest.TestCase):
    """src/__init__.py once declared __all__ with zero resolvable names."""

    def test_every_advertised_name_is_lazy_mapped(self):
        import src
        self.assertGreater(len(src.__all__), 10)
        for name in src.__all__:
            self.assertIn(name, src._LAZY_EXPORTS, f"{name} in __all__ but has no lazy mapping")

    def test_unknown_attribute_still_raises(self):
        import src
        with self.assertRaises(AttributeError):
            src.DEFINITELY_NOT_A_REAL_EXPORT_123


if __name__ == "__main__":
    unittest.main()
