"""M9: list prices as the APIs publish them (model listings), plus manual page excerpts.

prices/<date>/prices.json: {target: {model: Price fields + "source"}}
"""
import json
from dataclasses import asdict
from pathlib import Path

from lab.cost import Price
from lab.m import Ctx, call
from lab.requests import models_request
from lab.targets import Target


def _f(v) -> float | None:
    return None if v in (None, "") else float(v)


def _per_token(v) -> float | None:
    return None if v in (None, "") else float(v) * 1e6


def price_from_listing(target: str, item: dict) -> Price | None:
    p = item.get("pricing")
    if target.startswith("cortecs") and isinstance(p, dict) and "input_token" in p:
        write = _f(p.get("cache_write_cost"))
        if write is not None and write < p["input_token"]:  # Cortecs puts Gemini storage rates here
            write = None
        return Price(p["input_token"], p["output_token"], _f(p.get("cache_read_cost")), write, None, p.get("currency", "EUR"))
    if target == "requesty" and "input_price" in item:
        tier = (p or [{}])[0] if isinstance(p, list) else {}
        return Price(_per_token(item["input_price"]), _per_token(item["output_price"]), _per_token(item.get("cached_price")),
                     _per_token(tier.get("caching_5m_price", item.get("caching_price"))), _per_token(tier.get("caching_1h_price")), "USD")
    if target == "xai" and "prompt_text_token_price" in item:  # USD cents per 100M tokens
        c = lambda k: None if item.get(k) is None else item[k] / 100 / 100
        return Price(c("prompt_text_token_price"), c("completion_text_token_price"), c("cached_prompt_text_token_price"),
                     None, None, "USD")
    if isinstance(p, dict) and "prompt" in p:  # OpenRouter-style (OpenRouter, EU Router)
        return Price(_per_token(p["prompt"]), _per_token(p["completion"]), _per_token(p.get("input_cache_read")),
                     _per_token(p.get("input_cache_write")), _per_token(p.get("input_cache_write_1h")), p.get("currency", "USD"))
    return None


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    url, headers = models_request(t)
    if t.name.startswith("cortecs"):
        url += "?extended=true"
    _, path = call(ctx, t.name, None, "M9", "models", None, url, headers, None, method="GET")
    return [path]


def build_prices(date: str, root: Path = Path(".")) -> dict:
    """Listing prices for every configured model, then manual page prices (prices/<date>/manual.json) on top."""
    from lab.targets import load_targets
    out: dict = {}
    for name, t in load_targets(root / "targets.json").items():
        files = sorted((root / "data" / date / name / "M9").glob("*.json"))
        if not files:
            continue
        body = json.loads(files[-1].read_text())["response_body"]
        items = {(i.get("id") or i.get("name", "")).removeprefix("models/"): i
                 for i in (body.get("data") or body.get("models") or []) if isinstance(i, dict)}
        for m in t.models:
            price = price_from_listing(name, items.get(m, {}))
            if price:
                out.setdefault(name, {})[m] = {**asdict(price), "source": f"api:{files[-1].as_posix()}"}
    manual = root / "prices" / date / "manual.json"
    if manual.exists():
        for name, models in json.loads(manual.read_text()).items():
            for m, spec in models.items():
                out.setdefault(name, {}).setdefault(m, spec)
    return out
