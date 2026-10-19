import unittest

from lab.cost import Price, compute_cost
from lab.usage import Usage


class CostTest(unittest.TestCase):
    def test_cost_formula_spec(self):
        u = Usage(5100, 4000, 1000, 0, 200, None, None, None)
        p = Price(3, 15, 0.3, 3.75, 6, "USD")
        self.assertAlmostEqual(compute_cost(u, p), 0.00825)

    def test_cost_falls_back_to_input_price(self):
        u = Usage(5100, 4000, 1000, 0, 0, None, None, None)
        p = Price(3, 15, None, None, None, "USD")
        self.assertAlmostEqual(compute_cost(u, p), 5100 * 3 / 1e6)

    def test_cost_1h_without_1h_price_uses_input(self):
        u = Usage(1000, 0, 0, 1000, 0, None, None, None)
        p = Price(3, 15, 0.3, 3.75, None, "USD")
        self.assertAlmostEqual(compute_cost(u, p), 1000 * 3 / 1e6)

    def test_billed_input_never_negative(self):
        u = Usage(10, 4000, 0, 0, 0, None, None, None)
        p = Price(3, 15, 0.3, None, None, "USD")
        self.assertAlmostEqual(compute_cost(u, p), 4000 * 0.3 / 1e6)


if __name__ == "__main__":
    unittest.main()
