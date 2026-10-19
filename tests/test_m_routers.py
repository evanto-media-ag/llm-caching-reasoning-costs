import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab import requests as rq
from lab.m import Ctx, m8_routers
from lab.targets import Target
from lab.transport import Response


class RoutersTest(unittest.TestCase):
    def test_m8_five_calls_per_variant(self):
        bodies = []

        def send(method, url, headers, body, timeout_s=180):
            bodies.append(body)
            return Response(200, {"usage": {"prompt_tokens": 9, "completion_tokens": 1}}, 5, {}, [])

        t = Target("requesty", "openai-chat", "https://x.test/v1", "requesty", ["anthropic/claude-sonnet-5"], {})
        with tempfile.TemporaryDirectory() as d, mock.patch.object(rq, "load_key", return_value="KEY"):
            now = [0.0]
            sleep = lambda s: now.__setitem__(0, now[0] + s)
            m8_routers.run(t, None, Ctx(date="2026-10-20", send=send, sleep=sleep, clock=lambda: now[0], root=Path(d)))
        self.assertEqual(len(bodies), 10)
        self.assertEqual(bodies[0]["requesty"], {"auto_cache": True})
        self.assertIn("cache_control", bodies[0]["messages"][0]["content"][0])
        self.assertNotIn("requesty", bodies[5])
        self.assertIsInstance(bodies[5]["messages"][0]["content"], str)

    def test_m8_records_upstream_provider(self):
        self.assertEqual(m8_routers.upstream({"response_headers": {"x-cortecs-provider": "google"}, "response_body": {}}), "google")
        self.assertEqual(m8_routers.upstream({"response_headers": {"x-provider-slug": "aws"}, "response_body": {}}), "aws")
        self.assertEqual(m8_routers.upstream({"response_headers": {}, "response_body": {"provider": "Anthropic"}}), "Anthropic")
        self.assertIsNone(m8_routers.upstream({"response_headers": {}, "response_body": {}}))


if __name__ == "__main__":
    unittest.main()
