"""Tables from the raw records. Every number in the articles comes from here."""
import json
import statistics
from collections import defaultdict
from pathlib import Path

from lab.m import _note
from lab.m.m8_routers import upstream
from lab.m.m9_prices import build_prices, price_from_listing
from lab.targets import load_targets
from lab.transport import Response
from lab.usage import Usage, extract_usage

MEASUREMENTS = ("M1", "M2", "M3", "M4", "M5", "M6", "M8")
SEQUENCES = ("M1", "M2", "M3", "M4", "M8")
DASH = "—"


def _load(date: str, root: Path) -> tuple[list[dict], int]:
    """Records with parsed usage; runs with any invalid record are dropped and counted."""
    targets = load_targets(root / "targets.json")
    records = []
    for t in targets.values():
        unit = tuple(t.extras["_cost_unit"]) if "_cost_unit" in t.extras else None
        for m in MEASUREMENTS:
            for f in sorted((root / "data" / date / t.name / m).glob("*.json")):
                r = json.loads(f.read_text())
                note = _note(Response(r["status"], r["response_body"], 0, {}, []), r["note"], "abgelehnt")
                note = r["note"] if r["note"].startswith("ungültig") else note  # drift notes are stored only
                usage = extract_usage(t.style, r["response_body"], unit) if r["status"] == 200 else None
                records.append({**r, "note": note, "usage": usage, "path": f.relative_to(root).as_posix()})
    # Cache sequences are only valid as a whole; M5/M6 calls are independent, so only the bad call goes.
    invalid = [r for r in records if r["note"].startswith("ungültig")]
    bad_runs = {(r["target"], r["model"], r["measurement"], r["run_id"]) for r in invalid if r["measurement"] in SEQUENCES}
    valid = [r for r in records if not r["note"].startswith("ungültig")
             and (r["target"], r["model"], r["measurement"], r["run_id"]) not in bad_runs]
    return valid, len(bad_runs) + sum(1 for r in invalid if r["measurement"] not in SEQUENCES)


def _pairs(records: list[dict], measurement: str) -> dict:
    """Last valid run per (target, model, variant) -> {step suffix: record}."""
    runs: dict = defaultdict(dict)
    for r in records:
        if r["measurement"] != measurement or r["usage"] is None:
            continue
        variant, _, step = r["step"].rpartition("-")
        runs[(r["target"], r["model"], variant or "-", r["run_id"])][step] = r
    last: dict = {}
    for (t, m, v, _), steps in runs.items():
        last[(t, m, v)] = steps
    return last


def _writes(u: Usage) -> int:
    return u.cache_write_5m + u.cache_write_1h


def _hit(u: Usage) -> float:
    return u.cache_read / u.input_total if u.input_total else 0.0


def _pct(x: float) -> str:
    return f"{x * 100:.0f} %"


def _caching(records: list[dict], invalid: int) -> str:
    lines = ["| Ziel | Modell | Variante | Write A | Read B | Treffer B |", "|---|---|---|---|---|---|"]
    for (t, m, v), s in sorted(_pairs(records, "M1").items()):
        if "A" in s and "B" in s:
            a, b = s["A"]["usage"], s["B"]["usage"]
            lines.append(f"| {t} | {m} | {v} | {_writes(a)} | {b.cache_read} | {_pct(_hit(b))} |")
    lines += ["", "M2 (nach Wartezeit):", "", "| Ziel | Modell | Variante | Read nach 5,5 min | Read nach 61 min |", "|---|---|---|---|---|"]
    for (t, m, v), s in sorted(_pairs(records, "M2").items()):
        if "B" in s:
            c = s.get("C")
            lines.append(f"| {t} | {m} | {v} | {s['B']['usage'].cache_read} | {c['usage'].cache_read if c else DASH} |")
    lines += ["", "M3 (Effort A → B → wie A):", "", "| Ziel | Modell | Read B | Read C |", "|---|---|---|---|"]
    for (t, m, _), s in sorted(_pairs(records, "M3").items()):
        if "B" in s:
            lines.append(f"| {t} | {m} | {s['B']['usage'].cache_read} | {s['C']['usage'].cache_read if 'C' in s else DASH} |")
    lines += ["", "M4 (unter / über Mindestgröße):", "", "| Ziel | Modell | Variante | Input | Read B |", "|---|---|---|---|---|"]
    for (t, m, v), s in sorted(_pairs(records, "M4").items()):
        if "B" in s:
            lines.append(f"| {t} | {m} | {v} | {s['B']['usage'].input_total} | {s['B']['usage'].cache_read} |")
    lines += ["", f"{invalid} ungültige Läufe ausgeschlossen (429/5xx, unvollständig ohne Usage oder verschobene Wartezeit)."]
    return "\n".join(lines)


def _effort(records: list[dict]) -> str:
    rows: dict = defaultdict(dict)
    for r in records:
        if r["measurement"] == "M5":
            label = "✓ " + str(r["usage"].reasoning if r["usage"].reasoning is not None else "?") if r["status"] == 200 else f"✗ {r['status']}"
            rows[(r["target"], r["model"])][r["step"]] = label
    cols = ["effort-default", "effort-none", "effort-minimal", "effort-low", "effort-medium", "effort-high",
            "effort-xhigh", "effort-max", "budget_tokens", "level+budget"]
    lines = ["Zelle: ✓ Reasoning-Tokens bzw. ✗ HTTP-Status", "",
             "| Ziel | Modell | " + " | ".join(c.removeprefix("effort-") for c in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for (t, m), cells in sorted(rows.items()):
        lines.append(f"| {t} | {m} | " + " | ".join(cells.get(c, DASH) for c in cols) + " |")
    return "\n".join(lines)


def _cost(date: str, root: Path) -> str:
    lines = ["| Ziel | Modell | Aufrufe | Abweichung Median | Min | Max | Hinweis |", "|---|---|---|---|---|---|---|"]
    for f in sorted((root / "data" / date).glob("*/M7/reconcile.json")):
        by: dict = defaultdict(list)
        for row in json.loads(f.read_text()):
            by[(row["model"], row["note"])].append(row["deviation_pct"])
        for (m, note), devs in sorted(by.items()):
            d = [x for x in devs if x is not None]
            fmt = lambda x: f"{x:+.1f} %" if x is not None else DASH
            lines.append(f"| {f.parts[-3]} | {m} | {len(devs)} | {fmt(statistics.median(d) if d else None)} | "
                         f"{fmt(min(d) if d else None)} | {fmt(max(d) if d else None)} | {note} |")
    return "\n".join(lines)


def _routers(records: list[dict]) -> str:
    lines = ["| Ziel | Modell | Variante | Treffer in Aufruf 2–5 | Upstream |", "|---|---|---|---|---|"]
    for (t, m, v), s in sorted(_pairs(records, "M8").items()):
        follow = [s[k] for k in ("2", "3", "4", "5") if k in s]
        hits = sum(1 for r in follow if r["usage"].cache_read > 0)
        ups = sorted({upstream(r) or "?" for r in s.values()})
        lines.append(f"| {t} | {m} | {v} | {hits}/{len(follow)} | {', '.join(ups)} |")
    return "\n".join(lines)


def _prices(date: str, root: Path) -> str:
    lines = ["| Ziel | Modell | Input | Output | Read-Faktor | Write 5 min | Write 1 h | Währung | Quelle |",
             "|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda x: DASH if x is None else f"{x:g}"
    for t, models in sorted(build_prices(date, root).items()):
        for m, p in sorted(models.items()):
            factor = lambda x: DASH if x is None or not p["input"] else f"{x / p['input']:.3g}×"
            src = "API" if p["source"].startswith("api:") else "Preisseite"
            lines.append(f"| {t} | {m} | {fmt(p['input'])} | {fmt(p['output'])} | {factor(p['cache_read'])} | "
                         f"{factor(p['cache_write_5m'])} | {factor(p['cache_write_1h'])} | {p['currency']} | {src} |")
    return "\n".join(lines)


def _matrix(date: str, root: Path, records: list[dict]) -> str:
    cols = ["Caching", "Write gemeldet", "TTL 5,5 min", "Effort bricht Cache", "Mindestgröße", "Effort-Werte",
            "Kosten pro Aufruf", "Preise per API"]
    cells: dict = defaultdict(dict)
    for (t, m, v), s in _pairs(records, "M1").items():
        if "A" in s and "B" in s:
            best = max(_hit(s["B"]["usage"]), cells[t].get("_hit", 0.0))
            cells[t]["_hit"] = best
            cells[t]["Caching"] = f"ja ({_pct(best)})" if best > 0 else "nein"
            if _writes(s["A"]["usage"]) > 0:
                cells[t]["Write gemeldet"] = "ja"
            else:
                cells[t].setdefault("Write gemeldet", "nein")
    for (t, m, v), s in _pairs(records, "M2").items():
        if "B" in s and v in ("-", "5m"):
            cells[t]["TTL 5,5 min"] = "Treffer" if s["B"]["usage"].cache_read > 0 else "verfallen"
    for (t, m, _), s in _pairs(records, "M3").items():
        if "A" in s and "B" in s:
            broke = s["B"]["usage"].cache_read < 0.5 * s["B"]["usage"].input_total
            prev = cells[t].get("Effort bricht Cache")
            now = "ja" if broke else "nein"
            cells[t]["Effort bricht Cache"] = now if prev in (None, now) else "teils"
    for (t, m, v), s in _pairs(records, "M4").items():
        if v == "below" and "B" in s:
            above = _pairs(records, "M4").get((t, m, "above"), {}).get("B")
            ok = s["B"]["usage"].cache_read == 0 and above and above["usage"].cache_read > 0
            cells[t]["Mindestgröße"] = "bestätigt" if ok else "abweichend"
    m5: dict = defaultdict(list)
    for r in records:
        if r["measurement"] == "M5" and r["step"].startswith("effort-") and r["step"] != "effort-default":
            m5[(r["target"], r["model"])].append(r["status"] == 200)
    accepted: dict = defaultdict(list)
    for (t, m), ok in m5.items():
        accepted[t].append((sum(ok), len(ok)))
    for t, counts in accepted.items():
        lo, hi, n = min(c for c, _ in counts), max(c for c, _ in counts), max(n for _, n in counts)
        cells[t]["Effort-Werte"] = f"{lo}/{n}" if lo == hi else f"{lo}–{hi}/{n}"
    for f in (root / "data" / date).glob("*/M7/reconcile.json"):
        rows = json.loads(f.read_text())
        cells[f.parts[-3]]["Kosten pro Aufruf"] = "ja" if any(r["stage"] == "M7a" for r in rows) else "nein"
    for t, models in build_prices(date, root).items():
        if any(p["source"].startswith("api:") for p in models.values()):
            cells[t]["Preise per API"] = "ja"
    lines = [f"Stand: {date}", "", "| Ziel | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for t in load_targets(root / "targets.json"):
        lines.append(f"| {t} | " + " | ".join(cells[t].get(c, DASH) for c in cols) + " |")
    return "\n".join(lines)


def build_tables(date: str, root: Path = Path(".")) -> dict[str, str]:
    records, invalid = _load(date, root)
    head = f"Stand: {date}\n\n"
    return {"matrix.md": _matrix(date, root, records), "caching.md": head + _caching(records, invalid),
            "effort.md": head + _effort(records), "cost.md": head + _cost(date, root),
            "routers.md": head + _routers(records), "prices.md": head + _prices(date, root)}


def write_tables(date: str, root: Path = Path(".")) -> None:
    out = root / "tables" / date
    out.mkdir(parents=True, exist_ok=True)
    for name, text in build_tables(date, root).items():
        (out / name).write_text(text + "\n")
