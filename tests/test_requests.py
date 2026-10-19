import unittest
from unittest import mock

from lab import requests as rq
from lab.targets import Target


def T(name, style, extras=None, base="https://x.test/v1"):
    return Target(name, style, base, name, ["m"], extras or {})


class RequestsTest(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(rq, "load_key", return_value="KEY")
        p.start()
        self.addCleanup(p.stop)

    def build(self, t, effort=None, cache=rq.CacheSpec()):
        return rq.build_request(t, "m", system="SYS", user="USR", effort=effort, cache=cache, max_tokens=64)

    def test_anthropic_explicit_cache_1h(self):
        url, headers, body = self.build(T("anthropic", "anthropic"), cache=rq.CacheSpec("explicit", "1h"))
        self.assertTrue(url.endswith("/messages"))
        self.assertEqual(body["system"][0]["cache_control"], {"type": "ephemeral", "ttl": "1h"})
        self.assertNotIn("cache_control", body)
        self.assertIn("anthropic-version", headers)
        self.assertEqual(headers["x-api-key"], "KEY")

    def test_anthropic_auto_cache(self):
        _, _, body = self.build(T("anthropic", "anthropic"), cache=rq.CacheSpec("auto"))
        self.assertEqual(body["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("cache_control", body["system"][0])

    def test_anthropic_effort(self):
        _, _, body = self.build(T("anthropic", "anthropic"), effort="max")
        self.assertEqual(body["output_config"]["effort"], "max")

    def test_openai_responses_effort_and_cache_key(self):
        url, headers, body = self.build(T("openai-responses", "openai-responses"), effort="low", cache=rq.CacheSpec(key="r1"))
        self.assertTrue(url.endswith("/responses"))
        self.assertEqual(body["reasoning"], {"effort": "low"})
        self.assertEqual(body["prompt_cache_key"], "r1")
        self.assertIs(body["store"], False)
        self.assertEqual(headers["authorization"], "Bearer KEY")

    def test_openai_chat_effort(self):
        url, _, body = self.build(T("openai-chat", "openai-chat", {"_max_tokens_field": "max_completion_tokens"}), effort="high")
        self.assertTrue(url.endswith("/chat/completions"))
        self.assertEqual(body["reasoning_effort"], "high")
        self.assertEqual(body["max_completion_tokens"], 64)
        self.assertNotIn("_max_tokens_field", body)

    def test_gemini_level_vs_budget(self):
        url, headers, body = self.build(T("gemini", "gemini"), effort="low")
        self.assertTrue(url.endswith("/models/m:generateContent"))
        self.assertEqual(headers["x-goog-api-key"], "KEY")
        cfg = body["generationConfig"]["thinkingConfig"]
        self.assertEqual(cfg, {"thinkingLevel": "low"})
        _, _, body = self.build(T("gemini", "gemini", {"_thinking": "budget"}), effort="0")
        self.assertEqual(body["generationConfig"]["thinkingConfig"], {"thinkingBudget": 0})

    def test_router_extras_merged(self):
        t = T("requesty", "openai-chat", {"requesty": {"auto_cache": True}, "provider": {"order": ["a"]}})
        _, _, body = self.build(t, cache=rq.CacheSpec("explicit", "1h", key="r1"))
        self.assertEqual(body["requesty"], {"auto_cache": True})
        self.assertEqual(body["provider"], {"order": ["a"]})
        self.assertEqual(body["messages"][0]["content"][0]["cache_control"], {"type": "ephemeral", "ttl": "1h"})
        self.assertEqual(body["prompt_cache_key"], "r1")
        self.assertEqual(body["max_tokens"], 64)

    def test_xai_conv_id_header(self):
        _, headers, _ = self.build(T("xai", "openai-responses"), cache=rq.CacheSpec(key="r1"))
        self.assertEqual(headers["x-grok-conv-id"], "r1")

    def test_no_effort_sends_no_effort_field(self):
        _, _, body = self.build(T("mistral", "openai-chat"))
        self.assertNotIn("reasoning_effort", body)
        self.assertEqual(body["messages"][0], {"role": "system", "content": "SYS"})


class ModelsUrlTest(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(rq, "load_key", return_value="KEY")
        p.start()
        self.addCleanup(p.stop)

    def test_models_request_per_style(self):
        url, headers = rq.models_request(T("anthropic", "anthropic"))
        self.assertEqual((url, headers["x-api-key"]), ("https://x.test/v1/models", "KEY"))
        url, headers = rq.models_request(T("gemini", "gemini"))
        self.assertEqual(headers, {"x-goog-api-key": "KEY"})
        url, headers = rq.models_request(T("xai", "openai-responses"))
        self.assertEqual(headers, {"authorization": "Bearer KEY"})


if __name__ == "__main__":
    unittest.main()
