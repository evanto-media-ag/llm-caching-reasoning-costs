"""Usage parsing against real API responses captured on 2026-10-19 (calibration run)."""
import json
import unittest
from pathlib import Path

from lab.usage import extract_usage

F = Path(__file__).parent / "fixtures"
CASES = [  # file, style, cost_unit, input_total, cache_read, output, reported_cost, currency
    ("anthropic", "anthropic", None, 7229, 0, 4, None, None),
    ("openai-responses", "openai-responses", None, 4568, 0, 16, None, None),
    ("openai-chat", "openai-chat", None, 4568, 0, 4, None, None),
    ("xai", "openai-responses", None, 5802, 1152, 378, 0.012144, "USD"),
    ("gemini", "gemini", None, 5960, 0, 12, None, None),
    ("eurouter", "openai-chat", None, 7227, 0, 4, 0.01416810241, "EUR"),
    ("requesty", "openai-chat", None, 7227, 0, 4, 0.014494, "USD"),
    ("cortecs-residency", "openai-chat", ("EUR", 1e-6), 7227, 0, 4, 0.014312, "EUR"),
]


class RealFixturesTest(unittest.TestCase):
    def test_real_usage_blocks(self):
        for name, style, unit, inp, read, out, cost, cur in CASES:
            with self.subTest(name):
                u = extract_usage(style, json.loads((F / f"usage_{name}.json").read_text()), unit)
                self.assertEqual((u.input_total, u.cache_read, u.output, u.cost_currency), (inp, read, out, cur))
                if cost is None:
                    self.assertIsNone(u.reported_cost)
                else:
                    self.assertAlmostEqual(u.reported_cost, cost, places=9)


if __name__ == "__main__":
    unittest.main()
