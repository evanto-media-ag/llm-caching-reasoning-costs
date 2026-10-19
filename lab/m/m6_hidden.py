"""M6: reported reasoning tokens vs. what the response actually shows (answer and thinking text)."""
import uuid
from pathlib import Path

from lab.m import Ctx, call
from lab.m.m5_effort import MAX_TOKENS, PUZZLE, SYSTEM
from lab.requests import CacheSpec, build_request
from lab.targets import Target


def visible_text(style: str, body: dict) -> tuple[str, str]:
    """-> (answer text, visible thinking/reasoning text)"""
    if style == "anthropic":
        blocks = body.get("content") or []
        return ("".join(b.get("text", "") for b in blocks if b.get("type") == "text"),
                "".join(b.get("thinking", "") for b in blocks if b.get("type") == "thinking"))
    if style == "openai-responses":
        answer, thinking = [], []
        for item in body.get("output") or []:
            if item.get("type") == "reasoning":
                thinking += [s.get("text", "") for s in item.get("summary") or []]
            for c in item.get("content") or []:
                if c.get("type") == "output_text":
                    answer.append(c.get("text", ""))
        return "".join(answer), "".join(thinking)
    if style == "gemini":
        parts = ((body.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
        return ("".join(p.get("text", "") for p in parts if not p.get("thought")),
                "".join(p.get("text", "") for p in parts if p.get("thought")))
    msg = ((body.get("choices") or [{}])[0].get("message")) or {}
    return msg.get("content") or "", msg.get("reasoning_content") or msg.get("reasoning") or ""


def run(t: Target, model: str | None, ctx: Ctx) -> list[Path]:
    paths = []
    for m in [model] if model else t.models:
        url, h, b = build_request(t, m, system=SYSTEM, user=PUZZLE, effort="high", cache=CacheSpec(), max_tokens=MAX_TOKENS)
        _, path = call(ctx, t.name, m, "M6", "effort-high", uuid.uuid4().hex[:8], url, h, b)
        paths.append(path)
    return paths
