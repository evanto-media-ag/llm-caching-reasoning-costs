import unittest

from lab.usage import extract_usage


class UsageTest(unittest.TestCase):
    def test_anthropic_input_total_includes_cache(self):
        body = {"usage": {"input_tokens": 100, "cache_read_input_tokens": 4000,
                          "cache_creation_input_tokens": 1000,
                          "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 1000},
                          "output_tokens": 50}}
        u = extract_usage("anthropic", body)
        self.assertEqual(u.input_total, 5100)
        self.assertEqual(u.cache_read, 4000)
        self.assertEqual((u.cache_write_5m, u.cache_write_1h), (0, 1000))
        self.assertEqual(u.output, 50)

    def test_anthropic_without_breakdown_counts_as_5m(self):
        body = {"usage": {"input_tokens": 10, "cache_creation_input_tokens": 500, "output_tokens": 1}}
        u = extract_usage("anthropic", body)
        self.assertEqual((u.cache_write_5m, u.cache_write_1h), (500, 0))

    def test_openai_chat_input_already_includes_cache(self):
        body = {"usage": {"prompt_tokens": 5000, "completion_tokens": 20,
                          "prompt_tokens_details": {"cached_tokens": 4096},
                          "completion_tokens_details": {"reasoning_tokens": 12}}}
        u = extract_usage("openai-chat", body)
        self.assertEqual((u.input_total, u.cache_read, u.output, u.reasoning), (5000, 4096, 20, 12))
        self.assertIsNone(u.reported_cost)

    def test_openai_responses_fields(self):
        body = {"usage": {"input_tokens": 5000, "output_tokens": 300,
                          "input_tokens_details": {"cached_tokens": 4000, "cache_write_tokens": 900},
                          "output_tokens_details": {"reasoning_tokens": 250}}}
        u = extract_usage("openai-responses", body)
        self.assertEqual((u.input_total, u.cache_read, u.cache_write_5m, u.reasoning), (5000, 4000, 900, 250))

    def test_xai_ticks_to_usd(self):
        body = {"usage": {"input_tokens": 1, "output_tokens": 1, "cost_in_usd_ticks": 12_345_000_000}}
        u = extract_usage("openai-responses", body)
        self.assertAlmostEqual(u.reported_cost, 1.2345)
        self.assertEqual(u.cost_currency, "USD")

    def test_eurouter_cost_eur(self):
        body = {"usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.5, "cost_currency": "USD", "cost_eur": 0.43}}
        u = extract_usage("openai-chat", body)
        self.assertEqual((u.reported_cost, u.cost_currency), (0.43, "EUR"))

    def test_router_cost_defaults_to_usd(self):
        body = {"usage": {"prompt_tokens": 1, "completion_tokens": 1, "cost": 0.002,
                          "prompt_tokens_details": {"cached_tokens": 0, "caching_tokens": 700}}}
        u = extract_usage("openai-chat", body)
        self.assertEqual((u.reported_cost, u.cost_currency, u.cache_write_5m), (0.002, "USD", 700))

    def test_cortecs_cost_unit_from_target(self):
        body = {"usage": {"prompt_tokens": 22, "completion_tokens": 4, "cost": 84}}
        u = extract_usage("openai-chat", body, cost_unit=("EUR", 1e-6))
        self.assertAlmostEqual(u.reported_cost, 84e-6)
        self.assertEqual(u.cost_currency, "EUR")

    def test_gemini_thoughts_as_reasoning(self):
        body = {"usageMetadata": {"promptTokenCount": 5000, "cachedContentTokenCount": 4096,
                                  "candidatesTokenCount": 100, "thoughtsTokenCount": 300}}
        u = extract_usage("gemini", body)
        self.assertEqual((u.input_total, u.cache_read, u.output, u.reasoning), (5000, 4096, 400, 300))


if __name__ == "__main__":
    unittest.main()
