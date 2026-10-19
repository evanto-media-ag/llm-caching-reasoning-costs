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

    def test_sovereign_key_forbidden(self):
        with self.assertRaises(keys.ForbiddenKeyError):
            keys.load_key("cortecs-sovereign")
        (self.dir / "evil").symlink_to(Path.home() / ".cortecs-sovereign-key")
        with self.assertRaises(keys.ForbiddenKeyError):
            keys.load_key("evil")

    def test_loaded_secrets_tracks_values(self):
        (self.dir / "xai").write_text("s1")
        (self.dir / "gemini").write_text("s2")
        keys.load_key("xai")
        keys.load_key("gemini")
        self.assertEqual(sorted(keys.loaded_secrets()), ["s1", "s2"])


if __name__ == "__main__":
    unittest.main()
