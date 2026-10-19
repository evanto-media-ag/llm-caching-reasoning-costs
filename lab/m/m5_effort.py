"""M5: which effort values does a target accept, reject or silently remap?"""
import uuid
from pathlib import Path

from lab.m import Ctx, call
from lab.requests import CacheSpec, build_request
from lab.targets import Target

EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
PUZZLE = ("A bat and a ball cost 1.10 EUR in total. The bat costs 1.00 EUR more than the ball. "
          "How much does the ball cost? Answer with the amount only.")
SYSTEM = "You are a careful assistant."
MAX_TOKENS = 2048


def _send(ctx: Ctx, t: Target, model: str, step: str, run_id: str, url: str, headers: dict, body: dict) -> Path:
    for _ in range(3):
        resp, path = call(ctx, t.name, model, "M5", step, run_id, url, headers, body, note="angenommen",
                          error_label="abgelehnt")
        if not (resp.status == 429 or resp.status >= 500):
            return path
        ctx.sleep(float(resp.headers.get("retry-after", 30)))
    return path


def _probes(t: Target, model: str) -> list[tuple[str, str, dict, dict]]:
    """Extra requests that test documented rejections."""
    if t.style == "anthropic":
        url, h, b = build_request(t, model, system=SYSTEM, user=PUZZLE, effort=None, cache=CacheSpec(), max_tokens=MAX_TOKENS)
        return [("budget_tokens", url, h, {**b, "thinking": {"type": "enabled", "budget_tokens": 1024}})]
    if t.style == "gemini":
        url, h, b = build_request(t, model, system=SYSTEM, user=PUZZLE, effort="low", cache=CacheSpec(), max_tokens=MAX_TOKENS)
        b["generationConfig"]["thinkingConfig"]["thinkingBudget"] = 1024
        return [("level+budget", url, h, b)]
    return []


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    paths = []
    for m in [model] if model else t.models:
        run_id = uuid.uuid4().hex[:8]
        for effort in (None, *EFFORTS):
            url, h, b = build_request(t, m, system=SYSTEM, user=PUZZLE, effort=effort, cache=CacheSpec(), max_tokens=MAX_TOKENS)
            paths.append(_send(ctx, t, m, f"effort-{effort or 'default'}", run_id, url, h, b))
        for step, url, h, b in _probes(t, m):
            paths.append(_send(ctx, t, m, step, run_id, url, h, b))
    return paths
