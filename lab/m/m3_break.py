"""M3: does changing only the effort break the cache? A (e1), B (e2), C (e1 again)."""
from pathlib import Path

from lab.m import Ctx, Step, run_sequence
from lab.m.m1_cache import LARGE
from lab.requests import CacheSpec
from lab.targets import Target


def steps_for(t: Target) -> list[Step]:
    first = "medium" if t.name.startswith("openai") else "high"
    return [Step("A", first), Step("B", "low"), Step("C", first)]


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    cache = CacheSpec("explicit") if t.style == "anthropic" else CacheSpec()
    paths = []
    for m in [model] if model else t.models:
        paths += run_sequence(ctx, t, m, "M3", steps_for(t), cache, system_text=LARGE.read_text(), max_tokens=256)
    return paths
