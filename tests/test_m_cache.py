import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab import requests as rq
from lab.m import Ctx, Step, run_sequence
from lab.m import m3_break
from lab.requests import CacheSpec
from lab.targets import Target
from lab.transport import Response

OK = Response(200, {"usage": {"prompt_tokens": 9, "completion_tokens": 1}}, 5, {}, [])


class FakeSend:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.bodies = []

    def __call__(self, method, url, headers, body, timeout_s=180):
        self.bodies.append(body)
        status = self.statuses.pop(0) if self.statuses else 200
        return OK if status == 200 else Response(status, {"error": "x"}, 5, {}, [])


class SequenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = mock.patch.object(rq, "load_key", return_value="KEY")
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)
        self.t = Target("mistral", "openai-chat", "https://x.test/v1", "mistral", ["m"], {})

    def ctx(self, send, clock=None):
        return Ctx(date="2026-10-20", send=send, sleep=lambda s: None, clock=clock or (lambda: 0.0), root=Path(self.tmp.name))

    def test_m1_sequence(self):
        send = FakeSend([])
        paths = run_sequence(self.ctx(send), self.t, "m", "M1", [Step("A"), Step("B")], CacheSpec(key="RUN"), system_text="BIG")
        self.assertEqual(len(paths), 2)
        self.assertEqual(send.bodies[0], send.bodies[1])
        run_id = send.bodies[0]["prompt_cache_key"]
        self.assertIn(f"[run {run_id}]", send.bodies[0]["messages"][0]["content"])

    def test_m1_retry_on_429_marks_invalid(self):
        send = FakeSend([200, 429, 200, 200])
        paths = run_sequence(self.ctx(send), self.t, "m", "M1", [Step("A"), Step("B")], CacheSpec(key="RUN"), system_text="BIG")
        self.assertEqual(len(send.bodies), 4)
        self.assertNotEqual(send.bodies[0]["prompt_cache_key"], send.bodies[2]["prompt_cache_key"])
        notes = [__import__("json").loads(p.read_text())["note"] for p in paths]
        self.assertEqual(notes, ["ok", "ungültig: http 429", "ok", "ok"])

    def test_client_error_stops_without_retry(self):
        send = FakeSend([400])
        paths = run_sequence(self.ctx(send), self.t, "m", "M1", [Step("A"), Step("B")], CacheSpec(), system_text="BIG")
        self.assertEqual(len(send.bodies), 1)
        self.assertTrue(__import__("json").loads(paths[0].read_text())["note"].startswith("fehler: http 400"))

    def test_m2_sleep_drift_invalid(self):
        ticks = iter([0.0, 450.0] + [0.0, 300.0] * 5)  # first wait drifts by 50 %, retry is exact
        send = FakeSend([])
        paths = run_sequence(self.ctx(send, clock=lambda: next(ticks)), self.t, "m", "M2",
                             [Step("A"), Step("B", wait_s=300)], CacheSpec(), system_text="BIG")
        notes = [__import__("json").loads(p.read_text())["note"] for p in paths]
        self.assertTrue(notes[1].startswith("ungültig: Wartezeit"))
        self.assertEqual(notes[2:], ["ok", "ok"])

    def test_m3_changes_only_effort(self):
        send = FakeSend([])
        steps = m3_break.steps_for(self.t)
        run_sequence(self.ctx(send), self.t, "m", "M3", steps, CacheSpec(), system_text="BIG")
        a, b = send.bodies[0], send.bodies[1]
        diff = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        self.assertEqual(diff, {"reasoning_effort"})


if __name__ == "__main__":
    unittest.main()
