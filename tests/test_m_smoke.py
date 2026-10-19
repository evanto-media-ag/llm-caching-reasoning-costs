import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab import requests as rq
from lab.m import Ctx, smoke
from lab.targets import Target
from lab.transport import Response


class SmokeTest(unittest.TestCase):
    def test_smoke_archives_one_call_per_model(self):
        calls = []

        def fake_send(method, url, headers, body, timeout_s=180):
            calls.append((method, url, body))
            return Response(200, {"usage": {"prompt_tokens": 9, "completion_tokens": 1}}, 5, {}, [])

        t = Target("mistral", "openai-chat", "https://x.test/v1", "mistral", ["a", "b"], {})
        with tempfile.TemporaryDirectory() as d, mock.patch.object(rq, "load_key", return_value="KEY"):
            ctx = Ctx(date="2026-10-20", send=fake_send, root=Path(d))
            paths = smoke.run(t, None, ctx)
            self.assertEqual(len(paths), 3)  # models list + 2 calls
            self.assertTrue(all(p.exists() for p in paths))
        self.assertEqual([c[0] for c in calls], ["GET", "POST", "POST"])


if __name__ == "__main__":
    unittest.main()
