"""Every factual sentence in an article carries <!-- claim:C-nnn --> right after it."""
import re
from pathlib import Path

_MARKER = re.compile(r"<!--\s*claim:(C-\d{3})\s*-->")
_LABELS = {"nicht gemessen": ("(nicht gemessen)", "(not measured)"),
           "nicht messbar": ("(nicht messbar)", "(not measurable)")}


def _sentence_before(text: str, pos: int) -> str:
    start = max(text.rfind(". ", 0, pos - 3), text.rfind("\n", 0, pos))
    return text[start + 1:pos]


def check_article(md: Path, claims: dict[str, dict]) -> list[str]:
    text = md.read_text()
    errors = []
    for m in _MARKER.finditer(text):
        cid = m.group(1)
        claim = claims.get(cid)
        if claim is None:
            errors.append(f"{cid}: unknown claim")
        elif claim["status"] == "offen":
            errors.append(f"{cid}: claim still open")
        elif claim["status"] in _LABELS and not any(l in _sentence_before(text, m.start()) for l in _LABELS[claim["status"]]):
            errors.append(f"{cid}: status '{claim['status']}' needs the label {_LABELS[claim['status']][0]} in the sentence")
    return errors
