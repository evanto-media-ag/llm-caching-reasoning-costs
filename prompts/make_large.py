"""Generate prompts/large.txt deterministically: a fictional spare-parts catalogue.

Neutral, copyright-free, reproducible. Content does not matter for caching; size does.
Usage: python3 prompts/make_large.py [ITEMS]
"""
import random
import sys
from pathlib import Path

PARTS = ["valve", "bearing", "gasket", "sensor", "relay", "pump", "filter", "bracket", "coupling", "fuse"]
MATERIALS = ["steel", "brass", "aluminium", "nylon", "ceramic", "copper"]
WAREHOUSES = ["Regensburg", "Hamburg", "Leipzig", "Graz", "Basel"]


def catalogue(items: int) -> str:
    rng = random.Random(20261019)
    lines = ["You are the assistant of a fictional spare-parts warehouse. The catalogue below is reference data.",
             "Answer only the question after the catalogue, as briefly as possible.", "", "CATALOGUE"]
    for i in range(1, items + 1):
        lines.append(f"Item {i:04d}: {rng.choice(MATERIALS)} {rng.choice(PARTS)}, size {rng.randint(4, 120)} mm, "
                     f"stock {rng.randint(0, 900)} units in {rng.choice(WAREHOUSES)}, "
                     f"unit price {rng.randint(1, 499)}.{rng.randint(0, 99):02d} EUR.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    items = int(sys.argv[1]) if len(sys.argv) > 1 else 160
    Path(__file__).with_name("large.txt").write_text(catalogue(items))
