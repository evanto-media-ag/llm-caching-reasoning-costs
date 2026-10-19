import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lab import requests as rq
from lab.m import Ctx, m5_effort, m6_hidden
from lab.targets import Target
from lab.transport import Response

OK = Response(200, {"usage": {"prompt_tokens": 9, "completion_tokens": 1}}, 5, {}, [])


class EffortTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = mock.patch.object(rq, "load_key", return_value="KEY")
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)
        self.bodies = []

    def ctx(self, statuses):
        def send(method, url, headers, body, timeout_s=180):
            self.bodies.append(body)
            st = statuses.pop(0) if statuses else 200
            return OK if st == 200 else Response(st, {"error": {"message": "not supported"}}, 5, {}, [])
        return Ctx(date="2026-10-20", send=send, sleep=lambda s: None, root=Path(self.tmp.name))

    def test_m5_values_exact(self):
        t = Target("mistral", "openai-chat", "https://x.test/v1", "mistral", ["m"], {})
        m5_effort.run(t, None, self.ctx([]))
        self.assertEqual([b.get("reasoning_effort") for b in self.bodies],
                         [None, "none", "minimal", "low", "medium", "high", "xhigh", "max"])

    def test_m5_continues_after_400(self):
        t = Target("mistral", "openai-chat", "https://x.test/v1", "mistral", ["m"], {})
        paths = m5_effort.run(t, None, self.ctx([200, 400]))
        notes = [json.loads(p.read_text())["note"] for p in paths]
        self.assertEqual(len(paths), 8)
        self.assertTrue(notes[1].startswith("abgelehnt: http 400"))
        self.assertEqual(notes[2], "angenommen")

    def test_m5_anthropic_budget_tokens_probe(self):
        t = Target("anthropic", "anthropic", "https://x.test/v1", "anthropic", ["m"], {})
        m5_effort.run(t, None, self.ctx([]))
        self.assertEqual(self.bodies[-1]["thinking"], {"type": "enabled", "budget_tokens": 1024})
        self.assertNotIn("output_config", self.bodies[-1])

    def test_m5_gemini_level_and_budget_probe(self):
        t = Target("gemini", "gemini", "https://x.test/v1", "gemini", ["m"], {})
        m5_effort.run(t, None, self.ctx([]))
        self.assertEqual(self.bodies[-1]["generationConfig"]["thinkingConfig"],
                         {"thinkingLevel": "low", "thinkingBudget": 1024})

    def test_m6_visible_text(self):
        anth = {"content": [{"type": "thinking", "thinking": "hmm"}, {"type": "text", "text": "0.05"}]}
        self.assertEqual(m6_hidden.visible_text("anthropic", anth), ("0.05", "hmm"))
        chat = {"choices": [{"message": {"content": "0.05", "reasoning_content": "think"}}]}
        self.assertEqual(m6_hidden.visible_text("openai-chat", chat), ("0.05", "think"))
        resp = {"output": [{"type": "reasoning", "summary": [{"text": "s"}]},
                           {"type": "message", "content": [{"type": "output_text", "text": "0.05"}]}]}
        self.assertEqual(m6_hidden.visible_text("openai-responses", resp), ("0.05", "s"))
        mag = {"choices": [{"message": {"content": [
            {"type": "thinking", "thinking": [{"type": "text", "text": "ponder"}]}, {"type": "text", "text": "0.05"}]}}]}
        self.assertEqual(m6_hidden.visible_text("openai-chat", mag), ("0.05", "ponder"))
        gem = {"candidates": [{"content": {"parts": [{"text": "t", "thought": True}, {"text": "0.05"}]}}]}
        self.assertEqual(m6_hidden.visible_text("gemini", gem), ("0.05", "t"))


if __name__ == "__main__":
    unittest.main()
