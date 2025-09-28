import argparse
import os

from .fetcher.fetch_data import fetch_consolidated, save_consolidated


def cmd_fetch(args: argparse.Namespace) -> None:
    data = fetch_consolidated()
    out = save_consolidated(data)
    print(out)


def cmd_check(args: argparse.Namespace) -> None:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    consolidated = os.path.join(base_dir, "data", "consolidated.json")
    from .checks.run_checks import evaluate_checks

    spec = os.path.join(base_dir, "src", "checks", "checks.jsonata")
    results = evaluate_checks(consolidated, spec)
    out_path = os.path.join(base_dir, "data", "checks_result.json")
    import json
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(out_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="asana-security-checks", description="Asana security checks")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="Fetch data and build consolidated.json")
    f.set_defaults(func=cmd_fetch)

    c = sub.add_parser("check", help="Run JSONata checks over consolidated.json")
    c.set_defaults(func=cmd_check)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
