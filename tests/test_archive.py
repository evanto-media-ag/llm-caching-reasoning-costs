import json
import tempfile
import unittest
from pathlib import Path

from lab import archive, keys


class ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        keys._loaded.clear()
        keys._loaded.add("sk-test-123")

    def tearDown(self):
        keys._loaded.clear()
        self.tmp.cleanup()

    def _record(self, **over):
        rec = {k: None for k in archive.RECORD_KEYS}
        rec.update(over)
        return rec

    def test_write_record_refuses_secret(self):
        path = self.root / "r.json"
        with self.assertRaises(archive.SecretLeakError):
            archive.write_record(path, self._record(response_body={"error": "bad key sk-test-123"}))
        self.assertFalse(path.exists())

    def test_write_record_has_no_request_headers(self):
        with self.assertRaises(ValueError):
            archive.write_record(self.root / "r.json", self._record(request_headers={"x": "y"}))

    def test_write_record_roundtrip(self):
        path = self.root / "a" / "r.json"
        archive.write_record(path, self._record(status=200, response_body={"ok": True}))
        self.assertEqual(json.loads(path.read_text())["status"], 200)

    def test_check_secrets_finds_planted_key(self):
        bad = self.root / "data" / "x.json"
        bad.parent.mkdir(parents=True)
        bad.write_text('{"k": "sk-test-123"}')
        (self.root / "data" / "ok.json").write_text("{}")
        self.assertEqual(archive.check_secrets(self.root), [bad])

    def test_write_json_refuses_secret(self):
        with self.assertRaises(archive.SecretLeakError):
            archive.write_json(self.root / "x.json", {"k": "sk-test-123"})

    def test_run_dir_layout(self):
        self.assertEqual(archive.run_dir("2026-10-20", "xai", "M1", root=self.root),
                         self.root / "data" / "2026-10-20" / "xai" / "M1")


if __name__ == "__main__":
    unittest.main()
