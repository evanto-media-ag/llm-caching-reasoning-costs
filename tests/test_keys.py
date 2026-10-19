import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab import keys


class KeysTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.patch = mock.patch.object(keys, "KEY_DIR", self.dir)
        self.patch.start()
        # never touch the real production key in tests
        self.forbidden = mock.patch.object(keys, "_FORBIDDEN", self.dir / "no-production-key")
        self.forbidden.start()
        self.addCleanup(self.forbidden.stop)
        keys._loaded.clear()
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)

    def tearDown(self):
        self.env.stop()
        self.patch.stop()
        self.tmp.cleanup()

    def test_reads_file_and_strips(self):
        (self.dir / "xai").write_text("abc\n")
        self.assertEqual(keys.load_key("xai"), "abc")

    def test_missing_returns_none(self):
        self.assertIsNone(keys.load_key("gemini"))

    def test_env_fallback_for_anthropic_openai(self):
        os.environ["ANTHROPIC_API_KEY"] = "k1"
        self.assertEqual(keys.load_key("anthropic"), "k1")
        (self.dir / "anthropic-measure").write_text("k2")
        self.assertEqual(keys.load_key("anthropic"), "k2")

    def test_production_key_forbidden_by_content(self):
        prod = self.dir / "prod"
        prod.write_text("PROD\n")
        with mock.patch.object(keys, "_FORBIDDEN", prod):
            (self.dir / "cortecs-sovereign").write_text("PROD")
            with self.assertRaises(keys.ForbiddenKeyError):
                keys.load_key("cortecs-sovereign")
            (self.dir / "cortecs-residency").write_text("OTHER")
            self.assertEqual(keys.load_key("cortecs-residency"), "OTHER")
            (self.dir / "cortecs-sovereign").write_text("MEASURE")
            self.assertEqual(keys.load_key("cortecs-sovereign"), "MEASURE")
            self.assertIn("PROD", keys.loaded_secrets())  # read for the comparison -> must be redacted too
            (self.dir / "evil").symlink_to(prod)
            with self.assertRaises(keys.ForbiddenKeyError):
                keys.load_key("evil")

    def test_loaded_secrets_keeps_replaced_values(self):
        os.environ["ANTHROPIC_API_KEY"] = "env-key"
        keys.load_key("anthropic")
        (self.dir / "anthropic-measure").write_text("file-key")
        keys.load_key("anthropic")
        self.assertEqual(sorted(keys.loaded_secrets()), ["env-key", "file-key"])

    def test_loaded_secrets_tracks_values(self):
        (self.dir / "xai").write_text("s1")
        (self.dir / "gemini").write_text("s2")
        keys.load_key("xai")
        keys.load_key("gemini")
        self.assertEqual(sorted(keys.loaded_secrets()), ["s1", "s2"])


if __name__ == "__main__":
    unittest.main()
