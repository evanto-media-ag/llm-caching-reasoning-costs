"""Smoke run: list models, then one tiny call per configured model."""
from pathlib import Path

from lab.m import Ctx, call
from lab.requests import CacheSpec, build_request, models_request
from lab.targets import Target

SMALL = Path(__file__).resolve().parents[2] / "prompts" / "small.txt"


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    paths = []
    url, headers = models_request(t)
    _, path = call(ctx, t.name, None, "smoke", "models", None, url, headers, None, method="GET")
    paths.append(path)
    for m in [model] if model else t.models:
        url, headers, body = build_request(t, m, system="You are a test.", user=SMALL.read_text().strip(),
                                           effort=None, cache=CacheSpec(), max_tokens=32)
        _, path = call(ctx, t.name, m, "smoke", "call", None, url, headers, body)
        paths.append(path)
    return paths
