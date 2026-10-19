"""M7: computed cost (usage x list price) vs. cost the provider reports.

M7a: cost in the response (OpenRouter, EU Router, xAI, Requesty; Cortecs integer cost)
M7b: per request via a management API (Cortecs /manage/logs)
M7c: aggregated admin usage/cost APIs (OpenAI, Anthropic) — only with admin keys
"""
import datetime
import json
from pathlib import Path
from typing import Callable

from lab import billing
from lab.archive import write_json
from lab.cost import Price, compute_cost
from lab.m import Ctx, _note, call
from lab.m.m9_prices import build_prices
from lab.targets import Target
from lab.transport import Response
from lab.usage import Usage, extract_usage


def compare(computed: float, reported: float | None, computed_cur: str, reported_cur: str | None) -> dict:
    if reported is None:
        return {"computed": computed, "reported": None, "currency": computed_cur, "deviation_pct": None, "note": "nur berechnet"}
    if computed_cur != reported_cur:
        return {"computed": computed, "reported": reported, "currency": f"{computed_cur}/{reported_cur}",
                "deviation_pct": None, "note": "Währung"}
    dev = round((reported - computed) / computed * 100, 2) if computed else None
    return {"computed": computed, "reported": reported, "currency": computed_cur, "deviation_pct": dev, "note": "ok"}


def reported_in(currency: str, raw_usage: dict, u: Usage) -> tuple[float | None, str | None]:
    """Some routers report two currencies (EU Router: cost in USD and cost_eur); take the one matching the price."""
    if currency == "USD" and raw_usage.get("cost_currency") == "USD" and raw_usage.get("cost") is not None:
        return float(raw_usage["cost"]), "USD"
    return u.reported_cost, u.cost_currency


def wait_for_buckets(fetch: Callable[[], dict | None], sleep: Callable, tries: int = 3, delay: float = 300) -> dict | None:
    for i in range(tries):
        got = fetch()
        if got and (got.get("body") or {}).get("data"):
            return got
        if i < tries - 1:
            sleep(delay)
    return None


_LOG_FIELDS = ("request_id", "model")
_ATTEMPT_FIELDS = ("cost", "provider", "model", "tokens", "status")


def own_log_entries(payload: dict, own_ids: set[str]) -> list[dict]:
    """Management logs cover the whole account: keep only this run's requests and non-sensitive fields."""
    own_ids = {i for i in own_ids if i}  # error records carry no id; None must never match
    out = []
    for e in (payload.get("body") or {}).get("data") or []:
        if e.get("request_id") and e["request_id"] in own_ids:
            row = {k: e[k] for k in _LOG_FIELDS if k in e}
            row["attempts"] = [{k: a[k] for k in _ATTEMPT_FIELDS if k in a} for a in e.get("attempts") or []]
            out.append(row)
    return out


def reconcile(t: Target, date: str, root: Path = Path(".")) -> Path | None:
    prices = build_prices(date, root).get(t.name, {})
    unit = tuple(t.extras["_cost_unit"]) if "_cost_unit" in t.extras else None
    rows = []
    for f in sorted((root / "data" / date / t.name).glob("M[1-6]/*.json")):
        r = json.loads(f.read_text())
        resp = Response(r["status"], r["response_body"], 0, {}, [])
        if r["status"] != 200 or _note(resp, "ok") != "ok" or r["model"] not in prices:
            continue
        spec = {k: v for k, v in prices[r["model"]].items() if k != "source"}
        price = Price(**spec)
        u = extract_usage(t.style, r["response_body"], unit)
        reported, cur = reported_in(price.currency, (r["response_body"].get("usage") or {}), u)
        rows.append({"record": f.relative_to(root).as_posix(), "model": r["model"],
                     "stage": "M7a" if reported is not None else "-", **compare(compute_cost(u, price), reported, price.currency, cur)})
    if not rows:
        return None
    path = root / "data" / date / t.name / "M7" / "reconcile.json"
    write_json(path, rows)
    return path


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    paths = []
    if t.name == "eurouter":  # per-request lookup by x-request-id
        for f in sorted((ctx.root / "data" / ctx.date / t.name / "M1").glob("*.json"))[:4]:
            rid = json.loads(f.read_text())["response_headers"].get("x-request-id")
            got = rid and billing.eurouter_generation(rid)
            if got:
                write_json(ctx.root / "data" / ctx.date / t.name / "M7" / f"generation-{rid}.json", got)
    if t.name.startswith("cortecs"):  # M7b
        now = datetime.datetime.now(datetime.timezone.utc)
        got = billing.cortecs_logs(now - datetime.timedelta(hours=23), now)
        if got:
            own = {json.loads(f.read_text())["response_body"].get("id")
                   for f in (ctx.root / "data" / ctx.date / t.name).glob("M[1-8]/*.json")}
            write_json(ctx.root / "data" / ctx.date / t.name / "M7" / "manage-logs.json", own_log_entries(got, own))
    path = reconcile(t, ctx.date, ctx.root)
    return paths + ([path] if path else [])
