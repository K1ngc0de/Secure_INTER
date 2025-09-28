import json
import os
from typing import Any, Dict

try:
    import jsonata
except ImportError as e:
    raise SystemExit("Please install python-jsonata: pip install jsonata")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_checks(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_checks(consolidated_path: str, checks_path: str) -> Dict[str, Any]:
    data = load_json(consolidated_path)
    checks_spec = load_checks(checks_path)

    results: Dict[str, Any] = {}
    for key, check in checks_spec.items():
        expr_str = check["expr"]
        try:
            transformed = jsonata.transform(expr_str, json.dumps(data))
            result_obj = json.loads(transformed)
        except Exception as exc:  # Fallback/diagnostics
            result_obj = {"error": str(exc)}
        results[key] = {
            "description": check.get("description"),
            "result": result_obj,
        }
    return results


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    consolidated = os.path.join(base_dir, "data", "consolidated.json")
    spec = os.path.join(base_dir, "src", "checks", "checks.jsonata")
    out_path = os.path.join(base_dir, "data", "checks_result.json")

    results = evaluate_checks(consolidated, spec)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved checks result → {out_path}")
