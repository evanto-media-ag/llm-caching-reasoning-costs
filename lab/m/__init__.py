"""Shared runner plumbing: one Ctx per run, one archived record per call."""
import datetime
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from lab.archive import run_dir, write_record
from lab.transport import Response, send


@dataclass
class Ctx:
    date: str
    send: Callable = send
    sleep: Callable = time.sleep
    clock: Callable = time.time
    root: Path = field(default_factory=lambda: Path("."))


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name or "none")


def call(ctx: Ctx, target: str, model: str | None, measurement: str, step: str, run_id: str | None,
         url: str, headers: dict, body: dict | None, method: str = "POST", note: str = "ok") -> tuple[Response, Path]:
    resp = ctx.send(method, url, headers, body)
    folder = run_dir(ctx.date, target, measurement, root=ctx.root)
    seq = len(list(folder.glob("*.json"))) + 1 if folder.exists() else 1
    path = folder / f"{seq:03d}-{_safe(step)}-{_safe(model)}.json"
    record = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "target": target,
              "model": model, "measurement": measurement, "step": step, "run_id": run_id, "url": url,
              "request_body": body, "status": resp.status, "response_body": resp.body,
              "response_headers": resp.headers, "response_header_names": resp.header_names,
              "duration_ms": resp.duration_ms, "note": note if resp.status == 200 else f"http {resp.status}"}
    write_record(path, record)
    return resp, path
