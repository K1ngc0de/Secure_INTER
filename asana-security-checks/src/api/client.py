import os
from typing import Any, Dict, Optional

import requests

from .endpoints import BASE_URL


def _read_token_from_root() -> Optional[str]:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    token_file = os.path.join(root, "token.txt")
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return None


class AsanaClient:
    """Very small Asana HTTP client authenticated with PAT."""

    def __init__(self, token: Optional[str] = None) -> None:
        pat = token or os.getenv("ASANA_PAT") or _read_token_from_root()
        if not pat:
            raise RuntimeError("ASANA_PAT not set and token.txt not found at repo root")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {pat}",
            "Content-Type": "application/json",
        })

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}{path}"
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
