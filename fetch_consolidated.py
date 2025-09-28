#!/usr/bin/env python3
import os
import sys

# Add asana-security-checks/src to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "asana-security-checks", "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from fetcher.fetch_data import fetch_consolidated, save_consolidated  # type: ignore


def main() -> None:
    data = fetch_consolidated()
    out = save_consolidated(data)
    print(out)


if __name__ == "__main__":
    main()
