import datetime
import unittest
from unittest import mock

from lab import billing


class BillingTest(unittest.TestCase):
    def test_anthropic_cost_cents_string(self):
        payload = {"data": [{"starting_at": "2026-10-20T00:00:00Z",
                             "results": [{"amount": "123.45", "currency": "USD"}, {"amount": "0.55", "currency": "USD"}]}]}
        self.assertEqual(billing.normalize_reported_cost("anthropic_costs", payload),
                         [("2026-10-20T00:00:00Z", 1.24, "USD")])

    def test_openrouter_price_string_per_token(self):
        self.assertAlmostEqual(billing.per_million("0.000003"), 3.0)

    def test_cortecs_attempts_summed(self):
        payload = {"data": [{"request_id": "r1", "attempts": [{"cost": 0.002}, {"cost": 0.003}]}]}
        self.assertEqual(billing.normalize_reported_cost("cortecs_logs", payload), [("r1", 0.005, "EUR")])

    def test_openrouter_generation(self):
        payload = {"data": {"id": "gen-1", "total_cost": 0.0042}}
        self.assertEqual(billing.normalize_reported_cost("openrouter_generation", payload), [("gen-1", 0.0042, "USD")])

    def test_cortecs_logs_uses_range_parameter(self):
        urls = []
        fake = lambda method, url, headers, body: urls.append(url) or __import__("lab.transport", fromlist=["Response"]).Response(200, {"data": []}, 1, {}, [])
        with mock.patch.object(billing, "load_key", return_value="KEY"), mock.patch.object(billing, "send", fake):
            billing.cortecs_logs("24h")
        self.assertIn("range=24h", urls[0])
        self.assertNotIn("start=", urls[0])

    def test_missing_management_key_returns_none(self):
        start = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        with mock.patch.object(billing, "load_key", return_value=None):
            self.assertIsNone(billing.cortecs_logs())
            self.assertIsNone(billing.anthropic_usage(start, start))
            self.assertIsNone(billing.openai_costs(start, start))
            self.assertIsNone(billing.xai_usage(start, start))


if __name__ == "__main__":
    unittest.main()
