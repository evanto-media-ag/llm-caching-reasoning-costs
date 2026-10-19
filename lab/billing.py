"""Cost and usage as the providers report it (per call or aggregated). Returns None without the key.

Response shapes follow the provider docs of 2026-10-19 and are verified on the first real call.
"""
import datetime
import urllib.parse

from lab.keys import load_key
from lab.requests import ANTHROPIC_VERSION
from lab.transport import send


def per_million(per_token: str | float) -> float:
    return float(per_token) * 1e6


def _get(url: str, headers: dict, params: dict) -> dict:
    r = send("GET", f"{url}?{urllib.parse.urlencode(params)}", headers, None)
    return {"status": r.status, "body": r.body, "url": url, "params": params}


def _iso(t: datetime.datetime) -> str:
    return t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def openrouter_generation(gen_id: str) -> dict | None:
    key = load_key("openrouter")
    return key and _get("https://openrouter.ai/api/v1/generation", {"authorization": f"Bearer {key}"}, {"id": gen_id})


def eurouter_generation(request_id: str) -> dict | None:
    key = load_key("eurouter")
    return key and _get("https://api.eurouter.ai/api/v1/generation", {"authorization": f"Bearer {key}"}, {"id": request_id})


def cortecs_logs(start: datetime.datetime, end: datetime.datetime) -> dict | None:
    key = load_key("cortecs-management")
    return key and _get("https://api.cortecs.ai/v1/manage/logs", {"authorization": f"Bearer {key}"},
                        {"start": _iso(start), "end": _iso(end)})


def openai_usage(start: datetime.datetime, end: datetime.datetime, bucket: str = "1m") -> dict | None:
    key = load_key("openai-admin")
    return key and _get("https://api.openai.com/v1/organization/usage/completions", {"authorization": f"Bearer {key}"},
                        {"start_time": int(start.timestamp()), "end_time": int(end.timestamp()),
                         "bucket_width": bucket, "group_by": "model", "limit": 1440})


def openai_costs(start: datetime.datetime, end: datetime.datetime) -> dict | None:
    key = load_key("openai-admin")
    return key and _get("https://api.openai.com/v1/organization/costs", {"authorization": f"Bearer {key}"},
                        {"start_time": int(start.timestamp()), "end_time": int(end.timestamp()), "bucket_width": "1d"})


def _anthropic_admin(path: str, params: dict) -> dict | None:
    key = load_key("anthropic-admin")
    return key and _get(f"https://api.anthropic.com/v1/organizations/{path}",
                        {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}, params)


def anthropic_usage(start: datetime.datetime, end: datetime.datetime, bucket: str = "1m") -> dict | None:
    return _anthropic_admin("usage_report/messages", {"starting_at": _iso(start), "ending_at": _iso(end),
                                                      "bucket_width": bucket, "group_by[]": "model"})


def anthropic_costs(start: datetime.datetime, end: datetime.datetime) -> dict | None:
    return _anthropic_admin("cost_report", {"starting_at": _iso(start), "ending_at": _iso(end)})


def xai_usage(start: datetime.datetime, end: datetime.datetime) -> dict | None:
    key, team = load_key("xai-management"), load_key("xai-team-id")
    if not (key and team):
        return None
    r = send("POST", f"https://management-api.x.ai/v1/billing/teams/{team}/usage", {"authorization": f"Bearer {key}"},
             {"analyticsRequest": {"timeRange": {"startTime": _iso(start), "endTime": _iso(end)},
                                   "timeUnit": "TIME_UNIT_MINUTE", "groupBy": ["description"]}})
    return {"status": r.status, "body": r.body}


def normalize_reported_cost(source: str, payload: dict) -> list[tuple[str, float, str]]:
    """-> [(request_or_bucket_id, amount, currency)]"""
    if source == "anthropic_costs":  # cents as decimal strings, per daily bucket
        return [(b["starting_at"], round(sum(float(r["amount"]) for r in b["results"]) / 100, 10),
                 b["results"][0]["currency"] if b["results"] else "USD") for b in payload["data"]]
    if source == "openai_costs":
        return [(str(b["start_time"]), sum(r["amount"]["value"] for r in b["results"]),
                 (b["results"][0]["amount"]["currency"] if b["results"] else "usd").upper()) for b in payload["data"]]
    if source == "cortecs_logs":
        return [(t["request_id"], round(sum(a["cost"] for a in t["attempts"]), 10), "EUR") for t in payload["data"]]
    if source == "openrouter_generation":
        return [(payload["data"]["id"], payload["data"]["total_cost"], "USD")]
    if source == "eurouter_generation":
        d = payload.get("data", payload)
        return [(d.get("id", ""), d["cost_eur"], "EUR")]
    raise ValueError(f"unknown source {source}")
