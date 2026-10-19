import unittest

from lab.cost import Price
from lab.m.m7_cost import compare, reported_in, wait_for_buckets
from lab.usage import Usage


class CostReconcileTest(unittest.TestCase):
    def test_deviation_pct(self):
        self.assertEqual(compare(1.00, 1.02, "USD", "USD"), {"computed": 1.0, "reported": 1.02, "currency": "USD",
                                                             "deviation_pct": 2.0, "note": "ok"})

    def test_currency_mismatch_not_compared(self):
        r = compare(1.00, 0.9, "USD", "EUR")
        self.assertIsNone(r["deviation_pct"])
        self.assertEqual(r["note"], "Währung")

    def test_reported_in_prefers_matching_currency(self):
        u = Usage(1, 0, 0, 0, 1, None, 0.43, "EUR")
        raw = {"cost": 0.5, "cost_currency": "USD", "cost_eur": 0.43}
        self.assertEqual(reported_in("USD", raw, u), (0.5, "USD"))
        self.assertEqual(reported_in("EUR", raw, u), (0.43, "EUR"))

    def test_m7c_waits_for_buckets(self):
        replies = [{"body": {"data": []}}, {"body": {"data": []}}, {"body": {"data": [1]}}]
        sleeps = []
        got = wait_for_buckets(lambda: replies.pop(0), sleeps.append, tries=3, delay=300)
        self.assertEqual(got, {"body": {"data": [1]}})
        self.assertEqual(sleeps, [300, 300])

    def test_m7c_gives_up_after_tries(self):
        got = wait_for_buckets(lambda: {"body": {"data": []}}, lambda s: None, tries=3, delay=300)
        self.assertIsNone(got)


if __name__ == "__main__":
    unittest.main()
