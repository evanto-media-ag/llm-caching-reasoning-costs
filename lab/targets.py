"""Measurement targets from targets.json (no secrets in there, only key file names)."""
import json
from dataclasses import dataclass, field
from pathlib import Path

KEY_NAMES = ("anthropic", "openai", "gemini", "xai", "requesty", "mistral", "eurouter", "openrouter", "cortecs",
             "openai-admin", "anthropic-admin", "xai-management", "cortecs-management")


@dataclass
class Target:
    name: str
    style: str
    base_url: str
    key_name: str
    models: list[str]
    extras: dict = field(default_factory=dict)  # keys starting with "_" configure the builder, others go into the body


def load_targets(path: Path = Path("targets.json")) -> dict[str, Target]:
    raw = json.loads(path.read_text())
    return {name: Target(name, **spec) for name, spec in raw.items()}
