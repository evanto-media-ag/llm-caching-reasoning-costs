"""M2: does the cache survive past its TTL? A, wait 5.5 min, B; Anthropic 1 h adds C after 61 min."""
from pathlib import Path

from lab.m import Ctx, Step, run_sequence
from lab.m.m1_cache import LARGE
from lab.requests import CacheSpec
from lab.targets import Target

FIVE_MIN_PLUS = 330
ONE_HOUR_PLUS = 3660


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    m = model or t.models[0]
    text = LARGE.read_text()
    if t.style == "anthropic":
        paths = run_sequence(ctx, t, m, "M2", [Step("5m-A"), Step("5m-B", wait_s=FIVE_MIN_PLUS)],
                             CacheSpec("explicit", "5m"), system_text=text)
        return paths + run_sequence(ctx, t, m, "M2", [Step("1h-A"), Step("1h-B", wait_s=FIVE_MIN_PLUS),
                                                      Step("1h-C", wait_s=ONE_HOUR_PLUS - FIVE_MIN_PLUS)],
                                    CacheSpec("explicit", "1h"), system_text=text)
    return run_sequence(ctx, t, m, "M2", [Step("A"), Step("B", wait_s=FIVE_MIN_PLUS)], CacheSpec(), system_text=text)
