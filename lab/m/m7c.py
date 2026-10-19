"""M7c: our archived usage vs. the provider's aggregated admin usage/cost API (same day, same key).

Admin APIs cover the whole organisation: only rows of our own key (usage) or our models (costs) are kept,
and only allowlisted fields are archived.
"""
import datetime
import json
from collections import defaultdict
from pathlib import Path

from lab.archive import write_json
from lab.cost import Price, compute_cost
from lab.keys import load_key
from lab.m import Ctx
from lab.m.m9_prices import build_prices
from lab.targets import Target, load_targets
from lab.transport import send
from lab.usage import extract_usage

USAGE_FIELDS = ("model", "num_model_requests", "input_tokens", "input_cached_tokens", "input_cache_write_tokens",
                "input_cache_write_12h_tokens", "output_tokens")
OPENAI_TARGETS = ("openai-responses", "openai-chat")


def own_usage_rows(payload: dict, key_id: str | None) -> list[dict]:
    if not key_id:  # an unmatched key must never fall back to rows without a key id
        return []
    return [{k: r[k] for k in USAGE_FIELDS if k in r}
            for b in payload.get("data") or [] for r in b.get("results") or [] if r.get("api_key_id") == key_id]


def usage_totals(rows: list[dict]) -> dict[str, dict]:
    out: dict = defaultdict(lambda: defaultdict(int))
    for r in rows:
        for k, v in r.items():
            if k != "model" and isinstance(v, int):
                out[r["model"]][k] += v
    return {m: dict(v) for m, v in out.items()}


def base_model(api_model: str, ours: list[str]) -> str | None:
    hits = [m for m in ours if api_model == m or api_model.startswith(m + "-")]
    return max(hits, key=len) if hits else None


def record_totals(date: str, targets: list[str], root: Path = Path(".")) -> dict[str, dict]:
    """Every call we made with these targets on that day (all measurements, incl. smoke/calibration)."""
    styles = {n: t.style for n, t in load_targets(root / "targets.json").items()}
    out: dict = defaultdict(lambda: defaultdict(int))
    for name in targets:
        for f in sorted((root / "data" / date / name).glob("*/*.json")):
            r = json.loads(f.read_text())
            if not isinstance(r, dict):
                continue
            body = r.get("response_body")
            if r.get("status") != 200 or not isinstance(body, dict) or "usage" not in body:
                continue
            u = extract_usage(styles[name], body)
            t = out[r["model"]]
            t["num_model_requests"] += 1
            t["input_tokens"] += u.input_total
            t["input_cached_tokens"] += u.cache_read
            t["cache_write_tokens"] += u.cache_write_5m + u.cache_write_1h
            t["output_tokens"] += u.output
    return {m: dict(v) for m, v in out.items()}


def provider_cost_by_model(rows: list[dict], models: list[str]) -> dict[str, float]:
    out: dict = defaultdict(float)
    for r in rows:
        b = base_model((r.get("line_item") or "").split(",")[0], models)
        if b:
            out[b] += float((r.get("amount") or {}).get("value") or 0)
    return {m: round(v, 10) for m, v in out.items()}


def our_cost_by_model(totals: dict[str, dict], prices: dict[str, dict]) -> dict[str, float]:
    from lab.usage import Usage
    out = {}
    for m, t in totals.items():
        if m in prices:
            p = Price(**{k: v for k, v in prices[m].items() if k != "source"})
            u = Usage(t["input_tokens"], t["input_cached_tokens"], t["cache_write_tokens"], 0, t["output_tokens"], None, None, None)
            out[m] = round(compute_cost(u, p), 10)
    return out


def xai_cost_by_model(payload: dict) -> dict[str, float]:
    out: dict = defaultdict(float)
    for series in payload.get("timeSeries") or []:
        model = (series.get("group") or [""])[0].removeprefix("API ").strip()
        out[model] += sum(sum(p.get("values") or []) for p in series.get("dataPoints") or [])
    return {m: round(v, 10) for m, v in out.items()}


def reported_cost_totals(date: str, target: str, root: Path = Path(".")) -> dict[str, float]:
    t = load_targets(root / "targets.json")[target]
    unit = tuple(t.extras["_cost_unit"]) if "_cost_unit" in t.extras else None
    out: dict = defaultdict(float)
    for f in sorted((root / "data" / date / target).glob("*/*.json")):
        r = json.loads(f.read_text())
        body = r.get("response_body") if isinstance(r, dict) else None
        if isinstance(r, dict) and r.get("status") == 200 and isinstance(body, dict) and "usage" in body:
            u = extract_usage(t.style, body, unit)
            out[r["model"]] += u.reported_cost or 0.0
    return {m: round(v, 10) for m, v in out.items()}


def _xai(ctx: Ctx) -> list[Path]:
    key, team = load_key("xai-management"), load_key("xai-team-id")
    if not (key and team):
        return []
    start = datetime.datetime.fromisoformat(ctx.date)
    body = {"analyticsRequest": {"timeRange": {"startTime": f"{ctx.date} 00:00:00",
                                               "endTime": (start + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"),
                                               "timezone": "Etc/GMT"},
                                 "timeUnit": "TIME_UNIT_DAY", "values": [{"name": "usd", "aggregation": "AGGREGATION_SUM"}],
                                 "groupBy": ["description"], "filters": []}}
    r = send("POST", f"https://management-api.x.ai/v1/billing/teams/{team}/usage", {"authorization": f"Bearer {key}"}, body)
    path = ctx.root / "data" / ctx.date / "xai" / "M7" / "admin-usage.json"
    ok = r.status == 200 and isinstance(r.body, dict)
    write_json(path, {"date": ctx.date, "status": r.status, "error": None if ok else f"http {r.status}",
                      "provider_cost_by_model": xai_cost_by_model(r.body) if ok else None,
                      "our_reported_cost_by_model": reported_cost_totals(ctx.date, "xai", ctx.root),
                      "note": "billing is per team; compared with every call archived for the xai target that day, "
                              "so other team traffic would show as a difference"})
    return [path]


def _day(date: str) -> tuple[int, int]:
    d = datetime.datetime.fromisoformat(date).replace(tzinfo=datetime.timezone.utc)
    return int(d.timestamp()), int((d + datetime.timedelta(days=1)).timestamp())


def get_all_pages(url: str, headers: dict, send_fn=send) -> tuple[dict | None, str | None]:
    """All pages of a paginated admin endpoint, or (None, error) — an error is never archived as "no usage".

    OpenAI uses two schemes: usage/costs return `next_page` (sent back as `page`), list endpoints such as
    projects and API keys return `last_id` (sent back as `after`)."""
    data, cursor = [], None
    while True:
        page_url = url if cursor is None else f"{url}{'&' if '?' in url else '?'}{cursor}"
        r = send_fn("GET", page_url, headers, None)
        if r.status != 200 or not isinstance(r.body, dict):
            return None, f"http {r.status}"
        data += r.body.get("data") or []
        if not r.body.get("has_more"):
            return {"data": data}, None
        if r.body.get("next_page"):
            cursor = f"page={r.body['next_page']}"
        elif r.body.get("last_id"):
            cursor = f"after={r.body['last_id']}"
        else:
            return None, "has_more without cursor"


def _openai(ctx: Ctx) -> list[Path]:
    key, mine = load_key("openai-admin"), load_key("openai")
    if not (key and mine):
        return []
    h = {"authorization": f"Bearer {key}"}
    path = ctx.root / "data" / ctx.date / "openai-responses" / "M7" / "admin-usage.json"
    projects, err = get_all_pages("https://api.openai.com/v1/organization/projects?limit=100", h)
    key_id = None
    for p in (projects or {}).get("data", []):  # match our key by its redacted value; the key itself never leaves this process
        keys, kerr = get_all_pages(f"https://api.openai.com/v1/organization/projects/{p['id']}/api_keys?limit=100", h)
        err = err or kerr
        for k in (keys or {}).get("data", []):
            red = k.get("redacted_value", "")
            if red[:3] == mine[:3] and red[-4:] == mine[-4:]:
                key_id = k["id"]
    start, end = _day(ctx.date)
    usage, uerr = get_all_pages(f"https://api.openai.com/v1/organization/usage/completions?start_time={start}&end_time={end}"
                                "&bucket_width=1d&group_by=api_key_id&group_by=model&limit=7", h)
    costs, cerr = get_all_pages(f"https://api.openai.com/v1/organization/costs?start_time={start}&end_time={end}"
                                "&bucket_width=1d&group_by=line_item&limit=7", h)
    ours = record_totals(ctx.date, list(OPENAI_TARGETS), ctx.root)
    models = list(ours)
    errors = [e for e in (err, uerr, cerr) if e] + ([] if key_id else ["own key not found among project keys"])
    if errors:  # never compare against a partial or foreign picture
        write_json(path, {"date": ctx.date, "ours": ours, "errors": errors, "provider_usage": None, "provider_cost_by_model": None})
        return [path]
    provider: dict = {}
    for m, v in usage_totals(own_usage_rows(usage, key_id)).items():
        b = base_model(m, models)
        if b:
            provider[b] = {k: provider.get(b, {}).get(k, 0) + v.get(k, 0) for k in set(v) | set(provider.get(b, {}))}
    cost_rows = [{"line_item": r.get("line_item"), "amount": r.get("amount"), "quantity": r.get("quantity")}
                 for b in costs.get("data", []) for r in b.get("results", [])
                 if base_model((r.get("line_item") or "").split(",")[0], models)]
    write_json(path, {"date": ctx.date, "key_id_matched": True, "ours": ours, "provider_usage": provider,
                      "provider_costs_by_line_item": cost_rows,
                      "provider_cost_by_model": provider_cost_by_model(cost_rows, models),
                      "our_cost_by_model": our_cost_by_model(ours, build_prices(ctx.date, ctx.root).get("openai-responses", {})),
                      "note": "usage is per key; costs are per project, so other traffic in the project would show as a difference"})
    return [path]


def _anthropic(ctx: Ctx) -> list[Path]:
    """Records whether the org-scoped key may read the usage report at all (individual orgs get 403)."""
    key = load_key("anthropic-admin")
    if not key:
        return []
    from lab.requests import ANTHROPIC_VERSION
    start, end = f"{ctx.date}T00:00:00Z", (datetime.datetime.fromisoformat(ctx.date) + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    h = {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}
    org = send("GET", "https://api.anthropic.com/v1/organizations/me", h, None)
    usage = send("GET", f"https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at={start}&ending_at={end}&bucket_width=1d", h, None)
    path = ctx.root / "data" / ctx.date / "anthropic" / "M7" / "admin-usage.json"
    err = usage.body.get("error", {}) if isinstance(usage.body, dict) else {}
    write_json(path, {"date": ctx.date, "org_type_name_suffix": "Individual Organization" if "Individual" in str(org.body) else "other",
                      "usage_report_status": usage.status, "error_type": err.get("type"), "error_message": err.get("message")})
    return [path]


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    if t.name == "openai-responses":
        return _openai(ctx)
    if t.name == "xai":
        return _xai(ctx)
    if t.name == "anthropic":
        return _anthropic(ctx)
    return []
