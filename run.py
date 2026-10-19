"""CLI: python3 run.py <command> [--target T] [--model M] [--date D] [--path P]"""
import argparse
import datetime
import importlib
import sys
from pathlib import Path

from lab.archive import check_secrets
from lab.claims import load_claims, validate_claims
from lab.keys import load_key
from lab.targets import KEY_NAMES, load_targets

MEASUREMENTS = {"smoke": "smoke", "m1": "m1_cache", "m2": "m2_ttl", "m3": "m3_break", "m4": "m4_minimum",
                "m5": "m5_effort", "m6": "m6_hidden", "m7": "m7_cost", "m8": "m8_routers", "m9": "m9_prices"}


def _measure(args) -> int:
    from lab.m import Ctx
    module = importlib.import_module(f"lab.m.{MEASUREMENTS[args.command]}")
    ctx = Ctx(date=args.date)
    targets = load_targets()
    names = [args.target] if args.target else list(targets)
    for name in names:
        t = targets[name]
        if load_key(t.key_name) is None:
            print(f"{name}: skipped (no key) -> nicht gemessen")
            continue
        for path in module.run(t, args.model, ctx):
            print(path)
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=[*MEASUREMENTS, "report", "check-claims", "check-secrets", "check-article"])
    p.add_argument("--target")
    p.add_argument("--model")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--path")
    args = p.parse_args(argv)
    if args.command in MEASUREMENTS:
        return _measure(args)
    if args.command == "check-claims":
        errors = validate_claims(load_claims())
        print("\n".join(errors) or "claims ok")
        return 1 if errors else 0
    if args.command == "check-secrets":
        for name in KEY_NAMES:
            load_key(name)
        hits = check_secrets(Path("."))
        print("\n".join(map(str, hits)) or "no secrets found")
        return 1 if hits else 0
    if args.command == "report":
        from lab.report import write_tables
        write_tables(args.date)
        return 0
    from lab.articles import check_article
    errors = check_article(Path(args.path), load_claims())
    print("\n".join(errors) or "article ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
