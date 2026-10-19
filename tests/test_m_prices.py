import unittest

from lab.cost import Price
from lab.m.m9_prices import price_from_listing


class PriceListingTest(unittest.TestCase):
    def test_cortecs_eur_per_million(self):
        item = {"pricing": {"currency": "EUR", "input_token": 1.975, "output_token": 9.874,
                            "cache_read_cost": 0.197, "cache_write_cost": 2.468}}
        self.assertEqual(price_from_listing("cortecs-residency", item), Price(1.975, 9.874, 0.197, 2.468, None, "EUR"))

    def test_cortecs_write_below_input_is_ignored(self):
        item = {"pricing": {"currency": "EUR", "input_token": 1.0, "output_token": 2.0, "cache_write_cost": 0.5}}
        self.assertIsNone(price_from_listing("cortecs-sovereign", item).cache_write_5m)

    def test_requesty_per_token_usd(self):
        item = {"input_price": 2e-06, "cached_price": 2e-07, "output_price": 1e-05,
                "pricing": [{"caching_5m_price": 2.5e-06, "caching_1h_price": 4e-06}]}
        p = price_from_listing("requesty", item)
        self.assertEqual((p.currency, round(p.input, 6), round(p.cache_read, 6), round(p.cache_write_1h, 6)), ("USD", 2.0, 0.2, 4.0))

    def test_xai_cents_per_100m(self):
        item = {"prompt_text_token_price": 20000, "cached_prompt_text_token_price": 5000, "completion_text_token_price": 60000}
        self.assertEqual(price_from_listing("xai", item), Price(2.0, 6.0, 0.5, None, None, "USD"))

    def test_openrouter_style_strings(self):
        item = {"pricing": {"prompt": "0.0000022", "completion": "0.000011", "input_cache_read": "0.00000022",
                            "input_cache_write": "0.00000275", "currency": "USD"}}
        p = price_from_listing("eurouter", item)
        self.assertEqual((round(p.input, 6), round(p.output, 6), round(p.cache_write_5m, 6), p.cache_write_1h), (2.2, 11.0, 2.75, None))

    def test_no_prices_returns_none(self):
        self.assertIsNone(price_from_listing("anthropic", {"id": "claude"}))


if __name__ == "__main__":
    unittest.main()


class SourceSubsetTest(unittest.TestCase):
    def test_subset_keeps_cache_fields(self):
        from lab.m.m9_prices import source_subset
        md = {"anthropic": {"models": {"claude-sonnet-5": {"cost": {"input": 2, "cache_read": 0.2, "cache_write": 2.5}}}}}
        ll = {"claude-sonnet-5": {"input_cost_per_token": 2e-06, "cache_creation_input_token_cost": 2.5e-06,
                                  "cache_creation_input_token_cost_above_1hr": 4e-06, "mode": "chat"}}
        got = source_subset(md, ll, ["claude-sonnet-5"])
        self.assertEqual(got["models.dev"]["claude-sonnet-5"], {"anthropic": {"input": 2, "cache_read": 0.2, "cache_write": 2.5}})
        self.assertEqual(got["litellm"]["claude-sonnet-5"]["cache_creation_input_token_cost_above_1hr"], 4e-06)
