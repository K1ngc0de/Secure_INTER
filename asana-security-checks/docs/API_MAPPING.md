# Part 1 — API Research & Endpoint Mapping

This document maps the Asana REST API endpoints to the three Security Checks implemented in this assignment, and outlines the evaluation logic for each check.

## Security Checks Overview

The three security checks to be implemented are:
1. **No more than 4 Admins Configured** - Detect when more than 4 users have administrative privileges
2. **No Inactive Projects Present** - Detect projects that have not been modified in over 365 days and are still not archived  
3. **No Active External Users** - Detect active external (guest) users in the Asana workspace

## Authentication & Base Configuration

- **Base URL**: `https://app.asana.com/api/1.0`
- **Authentication**: Bearer Token (Personal Access Token)
- **Headers**: 
  - `Authorization: Bearer {personal_access_token}`
  - `Content-Type: application/json`
- **Rate Limiting**: Asana API has rate limits (typically 100 requests per minute)

## Workspace Context

Before running checks, we need the target workspace GID. We can obtain workspaces via:

- **Method**: GET
- **Endpoint**: `/workspaces`
- **Purpose**: Select the workspace to scope subsequent calls.
- **Response**: Array of workspace objects with `gid`, `name`, `resource_type`

---

## Check 1 — No more than 4 Admins configured

- **Method**: GET
- **Endpoint**: `/workspaces/{workspace_gid}/users`
- **Query Parameters**: 
  - `opt_fields=is_admin,name,email,gid,resource_type`
- **Response**: Array of user objects
- **Evaluation logic**:
  1. Retrieve the list of users for the given workspace
  2. Count users where `is_admin == true`
  3. If count > 4 → **VIOLATION**, else **PASS**
  4. Return detailed info: `{admin_count, max_allowed: 4, admins: [...]}`

**Notes**:
- If the API version/plan does not expose `is_admin`, fallback approaches may involve using Organization/Team membership roles where available
- In this assignment, we assume `is_admin` is available on user objects scoped to a workspace
- Handle cases where user data might be incomplete or missing

---

## Check 2 — No Inactive Projects Present (>365d and not archived)

- **Method**: GET
- **Endpoint**: `/projects`
- **Query Parameters**: 
  - `workspace={workspace_gid}`
  - `opt_fields=gid,name,archived,modified_at,created_at,team,owner,permalink_url`
- **Response**: Array of project objects
- **Evaluation logic**:
  1. Retrieve all projects for the workspace
  2. Filter projects where `archived == false`
  3. Parse `modified_at` as an ISO-8601 datetime (format: `YYYY-MM-DDTHH:mm:ss.sssZ`)
  4. Calculate cutoff date: `current_date - 365 days`
  5. Compare: if `modified_at < cutoff_date` → mark as inactive
  6. If any inactive projects found → **VIOLATION**, else **PASS**
  7. Return detailed info: `{inactive_count, inactive_projects: [...], cutoff_date}`

**Notes**:
- If `modified_at` is missing/malformed, treat project as potentially inactive (flag for review)
- Record as `Unknown` days inactive for projects with invalid dates
- Consider timezone handling for accurate date comparisons
- Handle edge cases where projects might have future modification dates

---

## Check 3 — No Active External Users

- **Method**: GET
- **Endpoint**: `/workspaces/{workspace_gid}/users`
- **Query Parameters**: 
  - `opt_fields=email,workspaces,name,gid,is_admin,resource_type`
- **Response**: Array of user objects
- **Evaluation logic**:
  1. Retrieve all users for the given workspace
  2. Identify external users using multiple criteria:
     - Users where `is_admin == false` (non-admin users)
     - Users whose email domain does not match organization's primary domain
     - Users marked as `is_guest` or `is_external` (if available in API plan)
  3. For this assignment, treat "external_users" as non-admin users in the workspace
  4. If any external users present → **VIOLATION**, else **PASS**
  5. Return detailed info: `{external_count, external_users: [...], organization_domain}`

**Notes**:
- Exact identification of external users may depend on Org domain(s) and Asana plan fields
- Adjust logic to use `is_guest`/`is_external` when available in the API response
- Consider multiple email domains for organizations with subdomains
- Handle cases where email information might be missing or incomplete

---

## Supporting Endpoints

- Method: GET
- Endpoint: `/users/me` or `/organizations`
- Purpose: Obtain organization context or authenticated user info as needed.

---

## Error Handling & Edge Cases

### Common API Errors
- **401 Unauthorized**: Invalid or expired Personal Access Token
- **403 Forbidden**: Insufficient permissions for the requested resource
- **404 Not Found**: Workspace or resource doesn't exist
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Asana API server error

### Data Quality Issues
- Missing or malformed `modified_at` timestamps
- Incomplete user data (missing email, admin status)
- Empty or null responses from API endpoints
- Timezone inconsistencies in date fields

### Fallback Strategies
- Use default values for missing critical fields
- Implement retry logic with exponential backoff for rate limits
- Log warnings for data quality issues
- Graceful degradation when optional fields are unavailable

## Data Flow Summary

1. **Authentication**: Validate Personal Access Token
2. **Workspace Selection**: Fetch `workspaces` → select target workspace
3. **User Analysis**: Fetch `workspaces/{workspace_gid}/users` → evaluate Admin count and External users
4. **Project Analysis**: Fetch `projects?workspace={workspace_gid}` with `opt_fields` → evaluate inactive projects (365+ days, not archived)
5. **Consolidation**: Combine all data into a single JSON structure for further processing

The same mapping applies whether checks are implemented in Python or later via JSONata over a consolidated JSON file.

## Example API Response Structure

```json
{
  "workspaces": [{"gid": "123", "name": "My Workspace", "resource_type": "workspace"}],
  "users": [
    {"gid": "456", "name": "John Doe", "email": "john@company.com", "is_admin": true},
    {"gid": "789", "name": "Jane Smith", "email": "jane@external.com", "is_admin": false}
  ],
  "projects": [
    {
      "gid": "101", 
      "name": "Project Alpha", 
      "archived": false, 
      "modified_at": "2023-01-15T10:30:00.000Z"
    }
  ]
}
```


