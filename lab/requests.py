"""Build (url, headers, body) per API style. One place that knows every wire format."""
from dataclasses import dataclass

from lab.keys import load_key
from lab.targets import Target

ANTHROPIC_VERSION = "2023-06-01"


@dataclass
class CacheSpec:
    mode: str = "none"  # none | auto | explicit
    ttl: str = "5m"     # 5m | 1h
    key: str | None = None  # prompt_cache_key / x-grok-conv-id


def _marker(cache: CacheSpec) -> dict:
    return {"type": "ephemeral", "ttl": "1h"} if cache.ttl == "1h" else {"type": "ephemeral"}


def _body_extras(t: Target) -> dict:
    return {k: v for k, v in t.extras.items() if not k.startswith("_")}


def _anthropic(t, model, system, user, effort, cache, max_tokens, key):
    sys_block = {"type": "text", "text": system}
    if cache.mode == "explicit":
        sys_block["cache_control"] = _marker(cache)
    body = {"model": model, "max_tokens": max_tokens, "system": [sys_block],
            "messages": [{"role": "user", "content": user}]}
    if cache.mode == "auto":
        body["cache_control"] = _marker(cache)
    if effort:
        body["output_config"] = {"effort": effort}
    headers = {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}
    return f"{t.base_url}/messages", headers, body


def _responses(t, model, system, user, effort, cache, max_tokens, key):
    body = {"model": model, "instructions": system, "input": user, "max_output_tokens": max_tokens, "store": False}
    if effort:
        body["reasoning"] = {"effort": effort}
    headers = {"authorization": f"Bearer {key}"}
    if cache.key:
        body["prompt_cache_key"] = cache.key
        if t.name == "xai":
            headers["x-grok-conv-id"] = cache.key
    return f"{t.base_url}/responses", headers, body


def _chat(t, model, system, user, effort, cache, max_tokens, key):
    sys_msg = {"role": "system", "content": system}
    if cache.mode == "explicit":
        sys_msg["content"] = [{"type": "text", "text": system, "cache_control": _marker(cache)}]
    body = {"model": model, "messages": [sys_msg, {"role": "user", "content": user}],
            t.extras.get("_max_tokens_field", "max_tokens"): max_tokens}
    if effort:
        body["reasoning_effort"] = effort
    if cache.key:
        body["prompt_cache_key"] = cache.key
    return f"{t.base_url}/chat/completions", {"authorization": f"Bearer {key}"}, body


def _gemini(t, model, system, user, effort, cache, max_tokens, key):
    gen = {"maxOutputTokens": max_tokens}
    if effort is not None:
        if t.extras.get("_thinking") == "budget":
            gen["thinkingConfig"] = {"thinkingBudget": int(effort)}
        else:
            gen["thinkingConfig"] = {"thinkingLevel": effort}
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": gen}
    return f"{t.base_url}/models/{model}:generateContent", {"x-goog-api-key": key}, body


_BUILDERS = {"anthropic": _anthropic, "openai-responses": _responses, "openai-chat": _chat, "gemini": _gemini}


def build_request(t: Target, model: str, *, system: str, user: str, effort: str | None, cache: CacheSpec,
                  max_tokens: int) -> tuple[str, dict[str, str], dict]:
    key = load_key(t.key_name)
    if key is None:
        raise LookupError(f"no key for {t.key_name}")
    url, headers, body = _BUILDERS[t.style](t, model, system, user, effort, cache, max_tokens, key)
    return url, headers, {**body, **_body_extras(t)}


def models_request(t: Target) -> tuple[str, dict[str, str]]:
    key = load_key(t.key_name)
    if key is None:
        raise LookupError(f"no key for {t.key_name}")
    if t.style == "anthropic":
        return f"{t.base_url}/models", {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION}
    if t.style == "gemini":
        return f"{t.base_url}/models", {"x-goog-api-key": key}
    return f"{t.base_url}/models", {"authorization": f"Bearer {key}"}
