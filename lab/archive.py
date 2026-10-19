"""Archive one JSON record per API call. Refuses to write anything that contains a loaded key."""
import json
from pathlib import Path

from lab.keys import loaded_secrets

RECORD_KEYS = ("ts", "target", "model", "measurement", "step", "run_id", "url", "request_body",
               "status", "response_body", "response_headers", "duration_ms", "note")


class SecretLeakError(Exception):
    pass


def run_dir(date: str, target: str, measurement: str, root: Path = Path(".")) -> Path:
    return root / "data" / date / target / measurement


def _leaks(text: str) -> bool:
    return any(s and s in text for s in loaded_secrets())


def write_record(path: Path, record: dict) -> None:
    extra = set(record) - set(RECORD_KEYS)
    if extra:
        raise ValueError(f"unexpected record keys: {sorted(extra)}")
    text = json.dumps(record, ensure_ascii=False, indent=2)
    if _leaks(text):
        raise SecretLeakError(f"record for {path} contains an API key; not written")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")


def check_secrets(root: Path = Path(".")) -> list[Path]:
    hits = []
    for folder in ("data", "prices", "tables"):
        for file in sorted((root / folder).rglob("*")):
            if file.is_file() and _leaks(file.read_text(errors="replace")):
                hits.append(file)
    return hits
