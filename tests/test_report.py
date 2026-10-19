import json
import shutil
import tempfile
import unittest
from pathlib import Path

from lab.report import build_tables

ROOT = Path(__file__).resolve().parents[1]


def rec(target, model, meas, step, status=200, usage=None, note="ok", run_id="r1"):
    return {"ts": "t", "target": target, "model": model, "measurement": meas, "step": step, "run_id": run_id,
            "url": "u", "request_body": {}, "status": status,
            "response_body": {"usage": usage or {"input_tokens": 5, "output_tokens": 1}} if status == 200 else {"error": "x"},
            "response_headers": {}, "response_header_names": [], "duration_ms": 1, "note": note}


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copy(ROOT / "targets.json", self.root / "targets.json")
        self.addCleanup(self.tmp.cleanup)

    def put(self, i, r):
        d = self.root / "data" / "2026-10-20" / r["target"] / r["measurement"]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{i:03d}.json").write_text(json.dumps(r))

    def test_matrix_has_date_header(self):
        tables = build_tables("2026-10-20", self.root)
        self.assertTrue(tables["matrix.md"].startswith("Stand: 2026-10-20"))

    def test_cell_without_evidence_is_dash(self):
        tables = build_tables("2026-10-20", self.root)
        row = next(l for l in tables["matrix.md"].splitlines() if l.startswith("| xai "))
        self.assertEqual(set(c.strip() for c in row.strip("|").split("|")[1:]), {"—"})

    def test_invalid_runs_excluded(self):
        u = {"input_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 7000, "output_tokens": 1}
        hit = {"input_tokens": 10, "cache_read_input_tokens": 7000, "output_tokens": 1}
        self.put(1, rec("anthropic", "m", "M1", "explicit-A", usage=u, run_id="bad"))
        self.put(2, rec("anthropic", "m", "M1", "explicit-B", status=429, note="ungültig: http 429", run_id="bad"))
        self.put(3, rec("anthropic", "m", "M1", "explicit-A", usage=u, run_id="good"))
        self.put(4, rec("anthropic", "m", "M1", "explicit-B", usage=hit, run_id="good"))
        caching = build_tables("2026-10-20", self.root)["caching.md"]
        self.assertIn("| anthropic | m | explicit | 7000 | 7000 |", caching)
        self.assertIn("1 ungültige Läufe", caching)

    def test_stale_ok_note_is_reclassified(self):
        empty = {"status": "incomplete", "usage": {"input_tokens": 0, "output_tokens": 0}}
        r = rec("openai-responses", "m", "M1", "key-A", run_id="x")
        r["response_body"] = empty
        self.put(1, r)
        self.assertIn("1 ungültige Läufe", build_tables("2026-10-20", self.root)["caching.md"])


if __name__ == "__main__":
    unittest.main()
