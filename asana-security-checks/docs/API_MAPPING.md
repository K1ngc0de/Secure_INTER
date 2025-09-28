# Part 1 — API Research & Endpoint Mapping

This document maps the Asana REST API endpoints to the three Security Checks implemented in this assignment, and outlines the evaluation logic for each check.

## Workspace Context

Before running checks, we need the target workspace GID. We can obtain workspaces via:

- Method: GET
- Endpoint: `/workspaces`
- Purpose: Select the workspace to scope subsequent calls.

---

## Check 1 — No more than 4 Admins configured

- Method: GET
- Endpoint: `/workspaces/{workspace_gid}/users`
- Opt fields: `is_admin,name,email,gid`
- Evaluation logic:
  - Retrieve the list of users for the given workspace.
  - Count users where `is_admin == true`.
  - If count > 4 → VIOLATION, else PASS.

Notes:
- If the API version/plan does not expose `is_admin`, fallback approaches may involve using Organization/Team membership roles where available. In this assignment, we assume `is_admin` is available on user objects scoped to a workspace.

---

## Check 2 — No Inactive Projects Present (>365d and not archived)

- Method: GET
- Endpoint: `/projects`
- Query params: `workspace={workspace_gid}`
- Opt fields: `gid,name,archived,modified_at,created_at,team,owner`
- Evaluation logic:
  - Retrieve all projects for the workspace.
  - Filter projects where `archived == false`.
  - Parse `modified_at` as an ISO-8601 datetime.
  - Compare with `now - 365 days`. If `modified_at < cutoff` → mark as inactive.
  - If any inactive projects found → VIOLATION, else PASS.

Notes:
- If `modified_at` is missing/malformed, treat project as potentially inactive (flag for review), or record as `Unknown` days inactive.

---

## Check 3 — No Active External Users

- Method: GET
- Endpoint: `/workspaces/{workspace_gid}/users`
- Opt fields: `email,workspaces,name,gid`
- Evaluation logic:
  - Identify external (guest) users as those whose email domain does not match the organization’s primary domain(s), or by `is_guest` if available in the plan.
  - For this assignment, we treat “external_users” as the users in the workspace not marked as admins and belonging to a different email domain than the organization (or classified as external by the existing data set).
  - If any external users present → VIOLATION, else PASS.

Notes:
- Exact identification of external users may depend on Org domain(s) and Asana plan fields. Adjust logic to use `is_guest`/`is_external` when available.

---

## Supporting Endpoints

- Method: GET
- Endpoint: `/users/me` or `/organizations`
- Purpose: Obtain organization context or authenticated user info as needed.

---

## Data Flow Summary

1. Fetch `workspaces` → select target workspace.
2. Fetch `workspaces/{workspace_gid}/users` → evaluate Admin count and External users.
3. Fetch `projects?workspace={workspace_gid}` with `opt_fields` → evaluate inactive projects (365+ days, not archived).

The same mapping applies whether checks are implemented in Python or later via JSONata over a consolidated JSON file.


