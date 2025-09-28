#!/usr/bin/env python3
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "asana-security-checks", "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from checks.run_checks import evaluate_checks  # type: ignore


def main() -> None:
    consolidated = os.path.join(BASE_DIR, "asana-security-checks", "data", "consolidated.json")
    spec = os.path.join(BASE_DIR, "asana-security-checks", "src", "checks", "checks.jsonata")
    out_path = os.path.join(BASE_DIR, "asana-security-checks", "data", "checks_result.json")

    results = evaluate_checks(consolidated, spec)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(out_path)


if __name__ == "__main__":
    main()
