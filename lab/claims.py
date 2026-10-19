"""Claims register: every factual statement in the articles is one row in claims.csv."""
import csv
import re
from pathlib import Path

COLUMNS = ("id", "claim_de", "claim_en", "source_url", "source_date", "target", "model", "measurement",
           "status", "evidence", "measured_on")
STATUSES = ("offen", "bestätigt", "widerlegt", "abweichend", "nicht messbar", "nicht gemessen")
MEASURED = ("bestätigt", "widerlegt", "abweichend")
_MEASUREMENT = re.compile(r"^M[1-9]$")


def load_claims(path: Path = Path("claims.csv")) -> dict[str, dict]:
    with path.open(newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def validate_claims(rows: dict[str, dict], root: Path = Path(".")) -> list[str]:
    errors = []
    for cid, r in rows.items():
        if r["status"] not in STATUSES:
            errors.append(f"{cid}: unknown status {r['status']!r}")
        m = r["measurement"]
        if m and not _MEASUREMENT.match(m):
            errors.append(f"{cid}: bad measurement {m!r}")
        if not m and r["status"] != "nicht messbar":
            errors.append(f"{cid}: measurement missing")
        if r["status"] in MEASURED:
            evidence = [p for p in r["evidence"].split(";") if p]
            if not evidence or not all((root / p).exists() for p in evidence):
                errors.append(f"{cid}: status {r['status']} needs existing evidence")
    return errors


def set_status(path: Path, claim_id: str, status: str, evidence: str, measured_on: str) -> None:
    rows = load_claims(path)
    rows[claim_id].update(status=status, evidence=evidence, measured_on=measured_on)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows.values())
