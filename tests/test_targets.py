import json
import unittest
from pathlib import Path

from lab.targets import KEY_NAMES, load_targets


class TargetsTest(unittest.TestCase):
    def test_targets_json_has_no_secrets(self):
        text = Path("targets.json").read_text()
        for prefix in ("sk-", "xai-", "eur_", "AIza"):
            self.assertNotIn(f'"{prefix}', text)
        for t in load_targets().values():
            self.assertIn(t.key_name, KEY_NAMES)

    def test_load_targets_types(self):
        t = load_targets()["anthropic"]
        self.assertEqual((t.name, t.style), ("anthropic", "anthropic"))
        self.assertIsInstance(t.models, list)


if __name__ == "__main__":
    unittest.main()
