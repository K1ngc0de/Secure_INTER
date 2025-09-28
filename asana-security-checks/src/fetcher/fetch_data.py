import json
import os
from datetime import datetime
from typing import Any, Dict, List

from api.client import AsanaClient
from api.endpoints import WORKSPACES, WORKSPACE_USERS, PROJECTS


def _select_workspace(workspaces: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not workspaces:
        raise RuntimeError("No workspaces available")
    return workspaces[0]


def fetch_consolidated() -> Dict[str, Any]:
    client = AsanaClient()

    # workspaces
    workspaces_resp = client.get(WORKSPACES)
    workspaces = workspaces_resp.get("data", [])
    workspace = _select_workspace(workspaces)
    workspace_gid = workspace["gid"]

    # users (request specific fields to support checks)
    users_resp = client.get(
        WORKSPACE_USERS.format(workspace_gid=workspace_gid),
        params={"opt_fields": "gid,name,email,is_admin,resource_type"},
    )
    users = users_resp.get("data", [])

    # projects
    projects_resp = client.get(
        PROJECTS,
        params={
            "workspace": workspace_gid,
            "opt_fields": "gid,name,archived,modified_at,created_at,public,color,notes,owner,team,permalink_url",
        },
    )
    projects = projects_resp.get("data", [])

    return {
        "workspace": workspace,
        "users": users,
        "projects": projects,
        "extracted_at": datetime.now().isoformat(),
    }


essential_dirs = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

def save_consolidated(data: Dict[str, Any], filename: str = "consolidated.json") -> str:
    os.makedirs(essential_dirs, exist_ok=True)
    out_path = os.path.join(essential_dirs, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


if __name__ == "__main__":
    data = fetch_consolidated()
    path = save_consolidated(data)
    print(f"Saved consolidated JSON → {path}")
