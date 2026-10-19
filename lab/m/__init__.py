"""Shared runner plumbing: one Ctx per run, one archived record per call."""
import datetime
import re
import time
import uuid
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

from lab.archive import run_dir, write_record
from lab.requests import CacheSpec, build_request
from lab.targets import Target
from lab.transport import Response, send

USER = "Reply with the single word OK."
_DRIFT = 0.10  # a wait that is off by more than 10 % (laptop asleep) invalidates the run


@dataclass
class Ctx:
    date: str
    send: Callable = send
    sleep: Callable = time.sleep
    clock: Callable = time.time
    root: Path = field(default_factory=lambda: Path("."))


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name or "none")


def _note(resp: Response, note: str, error_label: str = "fehler") -> str:
    if resp.status == 200:
        body = resp.body if isinstance(resp.body, dict) else {}
        if body.get("status") == "incomplete" and not (body.get("usage") or {}).get("input_tokens"):
            return "ungültig: unvollständig ohne Usage"
        return note
    if resp.status == 429 or resp.status >= 500:
        return f"ungültig: http {resp.status}"
    return f"{error_label}: http {resp.status} {str(resp.body)[:300]}"


def call(ctx: Ctx, target: str, model: str | None, measurement: str, step: str, run_id: str | None,
         url: str, headers: dict, body: dict | None, method: str = "POST", note: str = "ok",
         error_label: str = "fehler") -> tuple[Response, Path]:
    resp = ctx.send(method, url, headers, body)
    folder = run_dir(ctx.date, target, measurement, root=ctx.root)
    seq = len(list(folder.glob("*.json"))) + 1 if folder.exists() else 1
    path = folder / f"{seq:03d}-{_safe(step)}-{_safe(model)}.json"
    record = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "target": target,
              "model": model, "measurement": measurement, "step": step, "run_id": run_id, "url": url,
              "request_body": body, "status": resp.status, "response_body": resp.body,
              "response_headers": resp.headers, "response_header_names": resp.header_names,
              "duration_ms": resp.duration_ms, "note": _note(resp, note, error_label)}
    write_record(path, record)
    return resp, path


@dataclass
class Step:
    name: str
    effort: str | None = None
    wait_s: float = 0


def run_sequence(ctx: Ctx, t: Target, model: str, measurement: str, steps: list[Step], cache: CacheSpec, *,
                 system_text: str, max_tokens: int = 16, attempts: int = 3) -> list[Path]:
    """Run steps as one cache sequence. 429/5xx or a drifted wait invalidates the run and restarts it with
    a fresh run id (the invalid records stay archived); any other HTTP error ends the sequence."""
    paths: list[Path] = []
    for _ in range(attempts):
        run_id = uuid.uuid4().hex[:8]
        spec = replace(cache, key=run_id) if cache.key == "RUN" else cache
        system = f"[run {run_id}]\n{system_text}"
        restart = False
        for st in steps:
            note = "ok"
            if st.wait_s:
                t0 = ctx.clock()
                ctx.sleep(st.wait_s)
                elapsed = ctx.clock() - t0
                if abs(elapsed - st.wait_s) > _DRIFT * st.wait_s:
                    note = f"ungültig: Wartezeit {elapsed:.0f} s statt {st.wait_s:.0f} s"
            url, headers, body = build_request(t, model, system=system, user=USER, effort=st.effort, cache=spec,
                                               max_tokens=max_tokens)
            resp, path = call(ctx, t.name, model, measurement, st.name, run_id, url, headers, body, note=note)
            paths.append(path)
            final = _note(resp, note)
            if final.startswith("ungültig"):
                restart = True
                ctx.sleep(float(resp.headers.get("retry-after", 30)) if resp.status == 429 else 0)
                break
            if final.startswith("fehler"):
                return paths
        if not restart:
            return paths
    return paths
