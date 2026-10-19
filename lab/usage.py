"""Normalize provider usage blocks. input_total always INCLUDES cached tokens."""
from dataclasses import dataclass

_USD_PER_TICK = 1e-10  # xAI: 10^10 ticks = 1 USD


@dataclass
class Usage:
    input_total: int
    cache_read: int
    cache_write_5m: int  # default-TTL write (Anthropic 5 min, OpenAI default)
    cache_write_1h: int
    output: int  # includes reasoning/thinking tokens
    reasoning: int | None
    reported_cost: float | None
    cost_currency: str | None


def _cost(u: dict) -> tuple[float | None, str | None]:
    if "cost_in_usd_ticks" in u:
        return u["cost_in_usd_ticks"] * _USD_PER_TICK, "USD"
    if "cost_eur" in u:
        return float(u["cost_eur"]), "EUR"
    if "cost" in u and u["cost"] is not None:
        return float(u["cost"]), u.get("cost_currency") or "USD"
    return None, None


def _anthropic(u: dict) -> Usage:
    read = u.get("cache_read_input_tokens") or 0
    write = u.get("cache_creation_input_tokens") or 0
    split = u.get("cache_creation") or {}
    w1h = split.get("ephemeral_1h_input_tokens") or 0
    w5m = split.get("ephemeral_5m_input_tokens", write - w1h) or 0
    thinking = (u.get("output_tokens_details") or {}).get("thinking_tokens")
    return Usage(u.get("input_tokens", 0) + read + write, read, w5m, w1h, u.get("output_tokens", 0), thinking, None, None)


def _responses(u: dict) -> Usage:
    inp = u.get("input_tokens_details") or {}
    out = u.get("output_tokens_details") or {}
    return Usage(u.get("input_tokens", 0), inp.get("cached_tokens") or 0, inp.get("cache_write_tokens") or 0, 0,
                 u.get("output_tokens", 0), out.get("reasoning_tokens"), *_cost(u))


def _chat(u: dict) -> Usage:
    inp = u.get("prompt_tokens_details") or {}
    out = u.get("completion_tokens_details") or {}
    write = inp.get("cache_write_tokens") or inp.get("cache_creation_tokens") or inp.get("caching_tokens") or 0
    return Usage(u.get("prompt_tokens", 0), inp.get("cached_tokens") or 0, write, 0,
                 u.get("completion_tokens", 0), out.get("reasoning_tokens"), *_cost(u))


def _gemini(u: dict) -> Usage:
    thoughts = u.get("thoughtsTokenCount")
    output = (u.get("candidatesTokenCount") or 0) + (thoughts or 0)
    return Usage(u.get("promptTokenCount", 0), u.get("cachedContentTokenCount") or 0, 0, 0, output, thoughts, None, None)


_PARSERS = {"anthropic": ("usage", _anthropic), "openai-responses": ("usage", _responses),
            "openai-chat": ("usage", _chat), "gemini": ("usageMetadata", _gemini)}


def extract_usage(style: str, body: dict) -> Usage:
    field, parse = _PARSERS[style]
    return parse(body.get(field) or {})
