import json
import shutil
import tempfile
import unittest
from pathlib import Path

from lab.m import m7c
from lab.transport import Response

ROOT = Path(__file__).resolve().parents[1]


class M7cTest(unittest.TestCase):
    def test_own_usage_rows_filter_and_allowlist(self):
        payload = {"data": [{"results": [
            {"api_key_id": "key_me", "model": "gpt-5-mini", "num_model_requests": 2, "input_tokens": 10,
             "input_cached_tokens": 4, "input_cache_write_tokens": 0, "output_tokens": 3, "user_id": "u", "project_id": "p"},
            {"api_key_id": "key_other", "model": "gpt-5-mini", "num_model_requests": 9, "input_tokens": 99}]}]}
        rows = m7c.own_usage_rows(payload, "key_me")
        self.assertEqual(rows, [{"model": "gpt-5-mini", "num_model_requests": 2, "input_tokens": 10,
                                 "input_cached_tokens": 4, "input_cache_write_tokens": 0, "output_tokens": 3}])

    def test_unmatched_key_returns_no_rows(self):
        payload = {"data": [{"results": [{"api_key_id": None, "model": "gpt-5-mini", "input_tokens": 99}]}]}
        self.assertEqual(m7c.own_usage_rows(payload, None), [])

    def test_get_all_pages_follows_next_page_and_reports_errors(self):
        pages = [Response(200, {"data": [1], "has_more": True, "next_page": "p2"}, 1, {}, []),
                 Response(200, {"data": [2], "has_more": False}, 1, {}, [])]
        urls = []
        fake = lambda method, url, headers, body: urls.append(url) or pages.pop(0)
        self.assertEqual(m7c.get_all_pages("https://x.test/a?b=1", {}, fake), ({"data": [1, 2]}, None))
        self.assertIn("page=p2", urls[1])
        failing = lambda method, url, headers, body: Response(403, {"error": {"type": "permission_error"}}, 1, {}, [])
        self.assertEqual(m7c.get_all_pages("https://x.test/a", {}, failing), (None, "http 403"))

    def test_usage_totals_sum_rows_per_model(self):
        rows = [{"model": "a", "num_model_requests": 1, "input_tokens": 5, "output_tokens": 1},
                {"model": "a", "num_model_requests": 2, "input_tokens": 7, "output_tokens": 2}]
        self.assertEqual(m7c.usage_totals(rows)["a"]["input_tokens"], 12)
        self.assertEqual(m7c.usage_totals(rows)["a"]["num_model_requests"], 3)

    def test_record_totals_from_archive(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copy(ROOT / "targets.json", root / "targets.json")
            folder = root / "data" / "2026-10-20" / "openai-chat" / "M1"
            folder.mkdir(parents=True)
            body = {"usage": {"prompt_tokens": 100, "completion_tokens": 5, "prompt_tokens_details": {"cached_tokens": 64}}}
            for i in range(2):
                (folder / f"00{i}.json").write_text(json.dumps({"status": 200, "model": "gpt-5-mini", "response_body": body}))
            (folder / "009.json").write_text(json.dumps({"status": 429, "model": "gpt-5-mini", "response_body": {}}))
            derived = root / "data" / "2026-10-20" / "openai-chat" / "M7"
            derived.mkdir()
            (derived / "reconcile.json").write_text("[]")  # derived files are lists, not records
            totals = m7c.record_totals("2026-10-20", ["openai-chat"], root)
        self.assertEqual(totals["gpt-5-mini"], {"num_model_requests": 2, "input_tokens": 200,
                                                "input_cached_tokens": 128, "cache_write_tokens": 0, "output_tokens": 10})

    def test_provider_cost_by_model(self):
        rows = [{"line_item": "gpt-5-mini-2025-08-07, input", "amount": {"currency": "usd", "value": 0.5}},
                {"line_item": "gpt-5-mini-2025-08-07, output", "amount": {"currency": "usd", "value": 0.25}},
                {"line_item": "gpt-6.1-sol, input", "amount": {"currency": "usd", "value": 1.0}}]
        self.assertEqual(m7c.provider_cost_by_model(rows, ["gpt-5-mini", "gpt-6.1-sol"]), {"gpt-5-mini": 0.75, "gpt-6.1-sol": 1.0})

    def test_xai_cost_by_model(self):
        payload = {"timeSeries": [{"group": ["API grok-4.5"], "dataPoints": [{"values": [0.06]}, {"values": [0.01]}]},
                                  {"group": ["API grok-4.7"], "dataPoints": [{"values": [0.1]}]}]}
        self.assertEqual(m7c.xai_cost_by_model(payload), {"grok-4.5": 0.07, "grok-4.7": 0.1})

    def test_reported_cost_totals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copy(ROOT / "targets.json", root / "targets.json")
            folder = root / "data" / "2026-10-20" / "xai" / "smoke"
            folder.mkdir(parents=True)
            body = {"usage": {"input_tokens": 1, "output_tokens": 1, "cost_in_usd_ticks": 10_000_000_000}}
            (folder / "001.json").write_text(json.dumps({"status": 200, "model": "grok-4.7", "response_body": body}))
            (folder / "002.json").write_text("[1]")  # derived list files are skipped
            self.assertEqual(m7c.reported_cost_totals("2026-10-20", "xai", root), {"grok-4.7": 1.0})

    def test_model_prefix_match(self):
        self.assertEqual(m7c.base_model("gpt-5-mini-2025-08-07", ["gpt-5-mini", "gpt-5.6-luna"]), "gpt-5-mini")
        self.assertIsNone(m7c.base_model("gpt-4.1-nano-2025-04-14", ["gpt-5-mini"]))


if __name__ == "__main__":
    unittest.main()
