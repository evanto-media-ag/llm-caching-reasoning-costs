"""Load API keys from ~/.llm-keys/<name>. Values are never printed or logged."""
import hashlib
import os
from pathlib import Path

KEY_DIR = Path.home() / ".llm-keys"

# The production Managed-AI account must never be used for measurements.
_FORBIDDEN = Path.home() / ".cortecs-sovereign-key"
_ENV_FALLBACK = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
# Every value ever loaded stays here, so a replaced key is still redacted.
_loaded: set[str] = set()


class ForbiddenKeyError(Exception):
    pass


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_text().strip().encode()).hexdigest()


def _check(path: Path) -> None:
    if not _FORBIDDEN.is_file():
        return
    # Read only to compare; the value joins the redaction set so it can never be archived either.
    _loaded.add(_FORBIDDEN.read_text().strip())
    if path.resolve() == _FORBIDDEN.resolve() or (path.is_file() and _digest(path) == _digest(_FORBIDDEN)):
        raise ForbiddenKeyError(f"{path.name} is the production Managed-AI key")


def load_key(name: str) -> str | None:
    candidates = [KEY_DIR / f"{name}-measure", KEY_DIR / name] if name in _ENV_FALLBACK else [KEY_DIR / name]
    for path in candidates:
        if path.is_symlink() or path.exists():
            _check(path)
        if path.is_file():
            value = path.read_text().strip()
            if value:
                _loaded.add(value)
                return value
    env = _ENV_FALLBACK.get(name)
    value = os.environ.get(env, "").strip() if env else ""
    if value:
        _loaded.add(value)
        return value
    return None


def loaded_secrets() -> list[str]:
    return list(_loaded)
