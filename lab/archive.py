"""Archive one JSON record per API call. Refuses to write anything that contains a loaded key."""
import json
from pathlib import Path

from lab.keys import loaded_secrets

RECORD_KEYS = ("ts", "target", "model", "measurement", "step", "run_id", "url", "request_body",
               "status", "response_body", "response_headers", "response_header_names", "duration_ms", "note")


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


_SKIP = {".git", ".superpowers", "__pycache__"}


def check_secrets(root: Path = Path(".")) -> list[Path]:
    """Every file that would be published (the repo goes public), not only the data folders."""
    hits = []
    for file in sorted(root.rglob("*")):
        if file.is_file() and not _SKIP & set(file.relative_to(root).parts) and _leaks(file.read_text(errors="replace")):
            hits.append(file)
    return hits


def write_json(path: Path, obj) -> None:
    """Derived data (reconciliations, billing payloads) with the same leak check as records."""
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    if _leaks(text):
        raise SecretLeakError(f"{path} would contain an API key; not written")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")
