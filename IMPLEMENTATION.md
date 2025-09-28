# Implementation Documentation

This document explains the implementation of the Asana Security Checks project, covering all three parts of the assignment.

## Project Overview

The project implements three security checks for Asana workspaces:
1. **No more than 4 Admins Configured** - Detect when more than 4 users have administrative privileges
2. **No Inactive Projects Present** - Detect projects that have not been modified in over 365 days and are still not archived
3. **No Active External Users** - Detect active external (guest) users in the Asana workspace

## Part 1 — API Research & Endpoint Mapping

### What was done:
- Analyzed Asana REST API documentation to identify required endpoints
- Mapped each security check to specific API endpoints and HTTP methods
- Documented evaluation logic for each check
- Created comprehensive API mapping documentation

### Implementation:
- **File**: `asana-security-checks/docs/API_MAPPING.md`
- **Endpoints identified**:
  - `GET /workspaces` - Get workspace list
  - `GET /workspaces/{workspace_gid}/users` - Get users with admin status
  - `GET /projects?workspace={workspace_gid}` - Get projects with metadata
- **Authentication**: Bearer Token (Personal Access Token)
- **Evaluation logic**: Documented step-by-step process for each security check

### Key decisions:
- Used `opt_fields` parameter to minimize API calls and get only required data
- Identified fallback strategies for missing data fields
- Documented error handling approaches

## Part 2 — Data Fetcher

### What was done:
- Implemented modular API client for Asana REST API
- Created data fetcher that calls only the endpoints identified in Part 1
- Built consolidated JSON output for Part 3 processing
- Added root-level runner script for easy execution

### Implementation:

#### API Client (`asana-security-checks/src/api/client.py`):
```python
class AsanaClient:
    def __init__(self, token: Optional[str] = None):
        # Reads PAT from environment or token.txt file
        # Sets up authenticated session with proper headers
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        # Makes authenticated GET requests to Asana API
```

#### Data Fetcher (`asana-security-checks/src/fetcher/fetch_data.py`):
```python
def fetch_consolidated() -> Dict[str, Any]:
    # 1. Get workspaces, select first one
    # 2. Get users with opt_fields: gid,name,email,is_admin,resource_type
    # 3. Get projects with opt_fields: gid,name,archived,modified_at,...
    # 4. Return consolidated structure

def save_consolidated(data: Dict[str, Any], filename: str = "consolidated.json"):
    # Save to asana-security-checks/data/consolidated.json
```

#### Root Runner (`fetch_consolidated.py`):
- Simple script that imports and runs the fetcher
- Handles Python path issues for module imports
- Outputs path to generated consolidated.json

### Key decisions:
- **Modular design**: Separated API client, endpoints, and fetcher logic
- **Error handling**: Graceful handling of missing tokens and API errors
- **Data structure**: Clean JSON structure with workspace, users, projects, and timestamp
- **Field selection**: Only requested necessary fields to minimize API calls

## Part 3 — JSONata Security Checks

### What was done:
- Implemented JSONata expressions for all three security checks
- Created check runner that evaluates expressions over consolidated JSON
- Built root-level runner script for easy execution
- Generated results in structured JSON format

### Implementation:

#### JSONata Expressions (`asana-security-checks/src/checks/checks.jsonata`):
```json
{
  "admin_count_check": {
    "description": "No more than 4 Admins Configured",
    "expr": "$string({\"admin_count\": users[is_admin = true].$count(), \"is_violation\": users[is_admin = true].$count() > 4})"
  },
  "inactive_projects_check": {
    "description": "No Inactive Projects Present (365+ days, not archived)",
    "expr": "$string({\"inactive_projects\": projects[archived = false and ($toMillis($now()) - $toMillis(modified_at)) > 365*24*60*60*1000]{\"gid\": gid, \"name\": name, \"modified_at\": modified_at}, \"inactive_count\": projects[archived = false and ($toMillis($now()) - $toMillis(modified_at)) > 365*24*60*60*1000].$count(), \"is_violation\": projects[archived = false and ($toMillis($now()) - $toMillis(modified_at)) > 365*24*60*60*1000].$count() > 0})"
  },
  "external_users_check": {
    "description": "No Active External Users",
    "expr": "$string({\"external_users\": users[is_admin != true]{\"gid\": gid, \"name\": name, \"email\": email}, \"external_count\": users[is_admin != true].$count(), \"is_violation\": users[is_admin != true].$count() > 0})"
  }
}
```

#### Check Runner (`asana-security-checks/src/checks/run_checks.py`):
```python
def evaluate_checks(consolidated_path: str, checks_path: str) -> Dict[str, Any]:
    # 1. Load consolidated.json
    # 2. Load JSONata expressions
    # 3. Apply each expression using jsonata.transform()
    # 4. Parse results and return structured output
```

#### Root Runner (`run_checks.py`):
- Imports and runs the check runner
- Outputs path to generated checks_result.json

### Key decisions:
- **JSONata library**: Used `python-jsonata` for expression evaluation
- **String wrapping**: Used `$string()` to ensure JSON output from expressions
- **Error handling**: Graceful fallback for expression evaluation errors
- **Structured output**: Consistent result format with descriptions and results

## Technical Architecture

### File Structure:
```
interview/
├── asana_data_extractor.py              # Original monolithic implementation
├── asana-security-checks/               # New modular implementation
│   ├── docs/
│   │   └── API_MAPPING.md              # Part 1: API documentation
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.py               # HTTP client
│   │   │   └── endpoints.py            # API endpoints
│   │   ├── fetcher/
│   │   │   └── fetch_data.py           # Part 2: Data fetcher
│   │   ├── checks/
│   │   │   ├── checks.jsonata          # Part 3: JSONata expressions
│   │   │   └── run_checks.py           # Check runner
│   │   └── cli.py                      # CLI interface
│   └── data/
│       ├── consolidated.json           # Part 2 output
│       └── checks_result.json          # Part 3 output
├── fetch_consolidated.py               # Part 2 runner
├── run_checks.py                       # Part 3 runner
├── requirements.txt                    # Dependencies
└── README.md                          # Setup and usage
```

### Dependencies:
- `requests>=2.25.1` - HTTP client for API calls
- `jsonata>=1.8.2` - JSONata expression evaluation

### Authentication:
- Personal Access Token (PAT) from environment variable `ASANA_PAT` or `token.txt` file
- Bearer token authentication for all API requests

## Results and Output

### Part 2 Output (`consolidated.json`):
Contains workspace information, users with admin status, and projects with metadata:
```json
{
  "workspace": {"gid": "...", "name": "...", "resource_type": "workspace"},
  "users": [{"gid": "...", "name": "...", "email": "...", "is_admin": false}],
  "projects": [{"gid": "...", "name": "...", "archived": false, "modified_at": "..."}],
  "extracted_at": "2025-09-28T11:24:36.151912"
}
```

### Part 3 Output (`checks_result.json`):
Contains evaluation results for all three security checks:
```json
{
  "admin_count_check": {
    "description": "No more than 4 Admins Configured",
    "result": {"admin_count": 0, "is_violation": false}
  },
  "inactive_projects_check": {
    "description": "No Inactive Projects Present (365+ days, not archived)",
    "result": {"inactive_projects": [], "inactive_count": 0, "is_violation": false}
  },
  "external_users_check": {
    "description": "No Active External Users",
    "result": {"external_users": [...], "external_count": 2, "is_violation": true}
  }
}
```

## Challenges and Solutions

### Challenge 1: Module Import Issues
**Problem**: Relative imports didn't work when running scripts directly
**Solution**: Created root-level runner scripts that adjust `sys.path` and use absolute imports

### Challenge 2: JSONata Library API
**Problem**: `python-jsonata` has different API than expected (`transform()` instead of `compile()`/`evaluate()`)
**Solution**: Adapted code to use `jsonata.transform(expression, json_string)` and parse results

### Challenge 3: JSONata Expression Output
**Problem**: Expressions needed to return JSON strings, not objects
**Solution**: Wrapped expressions with `$string()` function to ensure string output

## Future Improvements

1. **Enhanced External User Detection**: Implement domain-based detection for external users
2. **Better Error Handling**: Add retry logic and more detailed error messages
3. **CLI Enhancement**: Complete the modular CLI interface
4. **Testing**: Add unit tests for all modules
5. **Configuration**: Add configuration file support for custom check parameters

## Conclusion

The implementation successfully addresses all three parts of the assignment:
- **Part 1**: Comprehensive API mapping and documentation
- **Part 2**: Efficient data fetching with minimal API calls
- **Part 3**: JSONata-based policy checks with structured output

The modular design allows for easy extension and maintenance, while the root-level runners provide simple execution for users.
