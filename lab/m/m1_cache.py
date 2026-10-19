"""M1: cache write then read — identical call A, then B right away."""
from pathlib import Path

from lab.m import Ctx, Step, run_sequence
from lab.requests import CacheSpec
from lab.targets import Target

LARGE = Path(__file__).resolve().parents[2] / "prompts" / "large.txt"
KEYED = ("openai-responses", "xai", "mistral")  # caches that take a routing / cache key


def variants(t: Target) -> list[tuple[str, CacheSpec]]:
    if t.style == "anthropic":
        return [("explicit", CacheSpec("explicit")), ("auto", CacheSpec("auto"))]
    if t.name in KEYED:
        return [("nokey", CacheSpec()), ("key", CacheSpec(key="RUN"))]
    return [("default", CacheSpec())]


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    paths = []
    for m in [model] if model else t.models:
        for label, cache in variants(t):
            paths += run_sequence(ctx, t, m, "M1", [Step(f"{label}-A"), Step(f"{label}-B")], cache,
                                  system_text=LARGE.read_text(), max_tokens=64)
    return paths
