"""M8: does the cache survive 5 follow-up calls through a router? (a) best effort, (b) plain."""
from dataclasses import replace
from pathlib import Path

from lab.m import Ctx, Step, run_sequence
from lab.m.m1_cache import LARGE
from lab.requests import CacheSpec
from lab.targets import Target

GAP_S = 20
# Best-effort pinning per router (docs 2026-10-18/19). Cortecs: cache_control only on Bedrock Claude.
PINNING = {"cortecs-residency": {"allowed_providers": ["amazon_ireland"]},
           "requesty": {"requesty": {"auto_cache": True}},
           "openrouter": {"provider": {"order": ["anthropic"]}},
           "eurouter": {}}


def upstream(record: dict) -> str | None:
    h = record.get("response_headers") or {}
    body = record.get("response_body") if isinstance(record.get("response_body"), dict) else {}
    return h.get("x-cortecs-provider") or h.get("x-provider-slug") or body.get("provider") or None


def _claude(t: Target) -> str | None:
    return next((m for m in t.models if "claude" in m), None)


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    m = model or _claude(t)
    if m is None:
        return []
    steps = [Step("1")] + [Step(str(i), wait_s=GAP_S) for i in range(2, 6)]
    text = LARGE.read_text()
    best = replace(t, extras={**t.extras, **PINNING.get(t.name, {})})
    cache_best = CacheSpec("explicit", "1h", key="RUN") if t.style != "anthropic" else CacheSpec("explicit", "1h")
    paths = run_sequence(ctx, best, m, "M8", [replace(s, name=f"best-{s.name}") for s in steps], cache_best,
                         system_text=text, max_tokens=64)
    paths += run_sequence(ctx, t, m, "M8", [replace(s, name=f"plain-{s.name}") for s in steps], CacheSpec(),
                          system_text=text, max_tokens=64)
    if t.name == "requesty":  # does auto_cache alone place the breakpoints?
        auto = replace(t, extras={**t.extras, "requesty": {"auto_cache": True}})
        paths += run_sequence(ctx, auto, m, "M8", [replace(s, name=f"autocache-{s.name}") for s in steps], CacheSpec(),
                              system_text=text, max_tokens=64)
    if t.name == "openrouter":  # stickiness without provider.order, only a session id
        paths += run_sequence(ctx, t, m, "M8", [replace(s, name=f"session-{s.name}") for s in steps],
                              CacheSpec("explicit", "1h", key="RUN"), system_text=text, max_tokens=64)
    return paths
