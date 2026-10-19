"""Plain HTTP via urllib. HTTP errors come back as a Response, never as an exception."""
import http.client
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

# Only these response headers are kept; everything else (cookies, ...) is dropped.
_KEEP = ("request-id", "x-request-id", "retry-after", "openai-processing-ms",
         # routers name the upstream provider here (needed for cache stability, M8)
         "x-cortecs-provider", "x-cortecs-model", "x-provider-slug", "x-provider-id", "x-model-used", "x-routing-strategy")


@dataclass
class Response:
    status: int
    body: dict | str
    duration_ms: int
    headers: dict[str, str]
    header_names: list[str]  # names only, values dropped (shows e.g. that no cost header exists)


def _keep(headers) -> dict[str, str]:
    out = {}
    for name, value in headers.items():
        low = name.lower()
        if low in _KEEP or low.startswith("x-ratelimit-"):
            out[low] = value
    return out


def _parse(raw: bytes) -> dict | str:
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except ValueError:
        return text


def send(method: str, url: str, headers: dict[str, str], body: dict | None, timeout_s: int = 180) -> Response:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"content-type": "application/json", **headers})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status, raw, hdrs = resp.status, resp.read(), resp.headers
    except urllib.error.HTTPError as err:
        status, raw, hdrs = err.code, err.read(), err.headers
    except (urllib.error.URLError, OSError, http.client.HTTPException) as err:
        # timeouts, refused or dropped connections: a result to archive (599 -> invalid run), not a crash
        return Response(599, f"{type(err).__name__}: {err}", int((time.monotonic() - start) * 1000), {}, [])
    duration = int((time.monotonic() - start) * 1000)
    return Response(status, _parse(raw), duration, _keep(hdrs), sorted({n.lower() for n in hdrs.keys()}))
