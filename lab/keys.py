"""Load API keys from ~/.llm-keys/<name>. Values are never printed or logged."""
import os
from pathlib import Path

KEY_DIR = Path.home() / ".llm-keys"

# The production Managed-AI account must never be used for measurements.
_FORBIDDEN = Path.home() / ".cortecs-sovereign-key"
_ENV_FALLBACK = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
_loaded: dict[str, str] = {}


class ForbiddenKeyError(Exception):
    pass


def _check(path: Path) -> None:
    if path.resolve() == _FORBIDDEN.resolve():
        raise ForbiddenKeyError(f"{path} points to the production Managed-AI key")


def load_key(name: str) -> str | None:
    if name == "cortecs-sovereign":
        raise ForbiddenKeyError("cortecs-sovereign is the production Managed-AI key")
    candidates = [KEY_DIR / f"{name}-measure", KEY_DIR / name] if name in _ENV_FALLBACK else [KEY_DIR / name]
    for path in candidates:
        if path.is_symlink() or path.exists():
            _check(path)
        if path.is_file():
            value = path.read_text().strip()
            if value:
                _loaded[name] = value
                return value
    env = _ENV_FALLBACK.get(name)
    value = os.environ.get(env, "").strip() if env else ""
    if value:
        _loaded[name] = value
        return value
    return None


def loaded_secrets() -> list[str]:
    return list(_loaded.values())
