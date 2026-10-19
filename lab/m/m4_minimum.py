"""M4: just below vs. just above the documented minimum cacheable size."""
import glob
import json
from pathlib import Path

from lab.m import Ctx, Step, run_sequence
from lab.m.m1_cache import LARGE
from lab.requests import CacheSpec
from lab.targets import Target

# Documented minimums (docs read 2026-10-18), tokens.
MINIMUMS = {("anthropic", "claude-sonnet-5-5"): 512, ("anthropic", "claude-haiku-5-5"): 512,
            ("anthropic", "claude-sonnet-5"): 1024, ("openai-responses", "gpt-6.1-sol"): 1024,
            ("openai-responses", "gpt-5.6-luna"): 1024, ("openai-responses", "gpt-5-mini"): 1024,
            ("gemini", "gemini-3.8-flash"): 4096}


def tokens_per_char(ctx: Ctx, t: Target) -> float | None:
    for f in sorted(glob.glob(str(ctx.root / "data" / "*" / t.name / "calib" / "*.json"))):
        r = json.loads(Path(f).read_text())
        if r["status"] == 200:
            from lab.usage import extract_usage
            return extract_usage(t.style, r["response_body"]).input_total / len(LARGE.read_text())
    return None


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    ratio = tokens_per_char(ctx, t)
    text = LARGE.read_text()
    cache = CacheSpec("explicit") if t.style == "anthropic" else CacheSpec()
    paths = []
    for (name, m), minimum in MINIMUMS.items():
        if name != t.name or (model and m != model) or ratio is None:
            continue
        for label, factor in (("below", 0.9), ("above", 1.1)):
            cut = text[: int(minimum * factor / ratio)]
            paths += run_sequence(ctx, t, m, "M4", [Step(f"{label}-A"), Step(f"{label}-B")], cache, system_text=cut, max_tokens=64)
    return paths
