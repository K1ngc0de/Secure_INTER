#!/usr/bin/env python3
"""
Asana Data Extractor
Script for extracting data from Asana API:
- List of workspace users (admins and external users)
- List of projects with archived and modified_at fields
- Save to JSON file
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AsanaDataExtractor:
    def __init__(self, personal_access_token: str):
        """
        Initialize with Personal Access Token
        
        Args:
            personal_access_token: Asana access token
        """
        self.token = personal_access_token
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json"
        }
        
    def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Makes a request to Asana API
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            sys.exit(1)
    
    def get_workspaces(self) -> List[Dict]:
        """
        Gets list of workspaces
        
        Returns:
            List of workspaces
        """
        print("Getting list of workspaces...")
        data = self.make_request("workspaces")
        return data.get("data", [])
    
    def get_workspace_users(self, workspace_gid: str) -> Dict[str, List[Dict]]:
        """
        Gets workspace users (admins and external users)
        
        Args:
            workspace_gid: Workspace GID
            
        Returns:
            Dictionary with admins and external_users
        """
        print(f"Getting users for workspace {workspace_gid}...")
        
        # Get all workspace users
        users_data = self.make_request(f"workspaces/{workspace_gid}/users")
        all_users = users_data.get("data", [])
        
        # Separate into admins and external users
        admins = []
        external_users = []
        
        for user in all_users:
            if user.get("is_admin", False):
                admins.append(user)
            else:
                external_users.append(user)
        
        return {
            "admins": admins,
            "external_users": external_users
        }
    
    def get_workspace_projects(self, workspace_gid: str) -> List[Dict]:
        """
        Gets workspace projects with archived and modified_at fields
        
        Args:
            workspace_gid: Workspace GID
            
        Returns:
            List of projects
        """
        print(f"Getting projects for workspace {workspace_gid}...")
        
        # Parameters for getting projects with required fields
        params = {
            "workspace": workspace_gid,
            "opt_fields": "gid,name,archived,modified_at,created_at,public,color,notes,owner,team,permalink_url"
        }
        
        projects_data = self.make_request("projects", params)
        return projects_data.get("data", [])
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extracts all data from Asana
        
        Returns:
            Combined data as dictionary
        """
        print("Starting data extraction from Asana...")
        
        # Get workspaces
        workspaces = self.get_workspaces()
        if not workspaces:
            print("No workspaces found")
            return {}
        
        # Use first workspace (or can select by name)
        workspace = workspaces[0]
        workspace_gid = workspace["gid"]
        print(f"Using workspace: {workspace['name']} (GID: {workspace_gid})")
        
        # Get users
        users_data = self.get_workspace_users(workspace_gid)
        
        # Get projects
        projects = self.get_workspace_projects(workspace_gid)
        
        # Form final data
        result = {
            "workspace": workspace,
            "users": users_data,
            "projects": projects,
            "extracted_at": datetime.now().isoformat(),
            "total_admins": len(users_data["admins"]),
            "total_external_users": len(users_data["external_users"]),
            "total_projects": len(projects)
        }
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = "asana_data.json"):
        """
        Saves data to JSON file
        
        Args:
            data: Data to save
            filename: File name
        """
        print(f"Saving data to {filename}...")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Data successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
            sys.exit(1)
    
    def check_admin_count(self, users_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Security Check 1: Detect when more than 4 users have administrative privileges
        
        Args:
            users_data: Dictionary with admins and external_users
            
        Returns:
            Dictionary with check results
        """
        admin_count = len(users_data.get("admins", []))
        is_violation = admin_count > 4
        
        return {
            "check_name": "Admin Count Check",
            "description": "No more than 4 Admins Configured",
            "admin_count": admin_count,
            "max_allowed": 4,
            "is_violation": is_violation,
            "status": "VIOLATION" if is_violation else "PASS",
            "message": f"Found {admin_count} admins (max allowed: 4)" + (" - VIOLATION!" if is_violation else " - OK")
        }
    
    def check_inactive_projects(self, projects: List[Dict]) -> Dict[str, Any]:
        """
        Security Check 2: Detect projects that have not been modified in over 365 days and are not archived
        
        Args:
            projects: List of projects
            
        Returns:
            Dictionary with check results
        """
        inactive_projects = []
        cutoff_date = datetime.now() - timedelta(days=365)
        
        for project in projects:
            if not project.get("archived", False):
                modified_at_str = project.get("modified_at")
                if modified_at_str:
                    try:
                        # Parse ISO format date
                        modified_at = datetime.fromisoformat(modified_at_str.replace('Z', '+00:00'))
                        if modified_at < cutoff_date:
                            inactive_projects.append({
                                "gid": project.get("gid"),
                                "name": project.get("name"),
                                "modified_at": modified_at_str,
                                "days_inactive": (datetime.now() - modified_at.replace(tzinfo=None)).days
                            })
                    except (ValueError, TypeError):
                        # If date parsing fails, consider it inactive
                        inactive_projects.append({
                            "gid": project.get("gid"),
                            "name": project.get("name"),
                            "modified_at": modified_at_str,
                            "days_inactive": "Unknown"
                        })
        
        is_violation = len(inactive_projects) > 0
        
        return {
            "check_name": "Inactive Projects Check",
            "description": "No Inactive Projects Present",
            "inactive_projects_count": len(inactive_projects),
            "inactive_projects": inactive_projects,
            "is_violation": is_violation,
            "status": "VIOLATION" if is_violation else "PASS",
            "message": f"Found {len(inactive_projects)} inactive projects (not modified in 365+ days)" + (" - VIOLATION!" if is_violation else " - OK")
        }
    
    def check_active_external_users(self, users_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Security Check 3: Detect active external (guest) users in the workspace
        
        Args:
            users_data: Dictionary with admins and external_users
            
        Returns:
            Dictionary with check results
        """
        external_users = users_data.get("external_users", [])
        is_violation = len(external_users) > 0
        
        return {
            "check_name": "Active External Users Check",
            "description": "No Active External Users",
            "external_users_count": len(external_users),
            "external_users": external_users,
            "is_violation": is_violation,
            "status": "VIOLATION" if is_violation else "PASS",
            "message": f"Found {len(external_users)} active external users" + (" - VIOLATION!" if is_violation else " - OK")
        }
    
    def run_security_checks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all security checks on extracted data
        
        Args:
            data: Extracted data from Asana
            
        Returns:
            Dictionary with all security check results
        """
        print("\nRunning security checks...")
        
        users_data = data.get("users", {})
        projects = data.get("projects", [])
        
        checks = {
            "admin_count": self.check_admin_count(users_data),
            "inactive_projects": self.check_inactive_projects(projects),
            "active_external_users": self.check_active_external_users(users_data)
        }
        
        # Calculate overall security status
        violations = sum(1 for check in checks.values() if check["is_violation"])
        total_checks = len(checks)
        
        security_summary = {
            "total_checks": total_checks,
            "violations": violations,
            "passed": total_checks - violations,
            "overall_status": "VIOLATIONS FOUND" if violations > 0 else "ALL CHECKS PASSED",
            "checks": checks
        }
        
        return security_summary
    
    def print_security_report(self, security_data: Dict[str, Any]):
        """
        Print detailed security report
        
        Args:
            security_data: Security check results
        """
        print("\n" + "="*60)
        print("SECURITY AUDIT REPORT")
        print("="*60)
        print(f"Overall Status: {security_data['overall_status']}")
        print(f"Checks Passed: {security_data['passed']}/{security_data['total_checks']}")
        print(f"Violations Found: {security_data['violations']}")
        print("="*60)
        
        for check_name, check_data in security_data["checks"].items():
            print(f"\n{check_data['check_name']}: {check_data['status']}")
            print(f"Description: {check_data['description']}")
            print(f"Result: {check_data['message']}")
            
            # Show detailed information for violations
            if check_data["is_violation"]:
                if check_name == "admin_count":
                    print(f"  - Current admin count: {check_data['admin_count']}")
                    print(f"  - Maximum allowed: {check_data['max_allowed']}")
                
                elif check_name == "inactive_projects":
                    print(f"  - Inactive projects found: {check_data['inactive_projects_count']}")
                    for project in check_data['inactive_projects'][:5]:  # Show first 5
                        days = project['days_inactive']
                        print(f"    * {project['name']} (GID: {project['gid']}) - {days} days inactive")
                    if len(check_data['inactive_projects']) > 5:
                        print(f"    ... and {len(check_data['inactive_projects']) - 5} more")
                
                elif check_name == "active_external_users":
                    print(f"  - External users found: {check_data['external_users_count']}")
                    for user in check_data['external_users']:
                        print(f"    * {user.get('name', 'Unknown')} (GID: {user.get('gid', 'Unknown')})")
            
            print("-" * 40)
        
        print("="*60)

def main():
    """Main function"""
    # Read token from file
    try:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("File token.txt not found!")
        print("Create token.txt file and put your Personal Access Token in it")
        sys.exit(1)
    
    if not token:
        print("Token not found in token.txt file!")
        sys.exit(1)
    
    # Create extractor and extract data
    extractor = AsanaDataExtractor(token)
    data = extractor.extract_all_data()
    
    if data:
        # Save data
        extractor.save_to_json(data)
        
        # Print brief statistics
        print("\n" + "="*50)
        print("EXTRACTED DATA STATISTICS:")
        print("="*50)
        print(f"Workspace: {data['workspace']['name']}")
        print(f"Admins: {data['total_admins']}")
        print(f"External users: {data['total_external_users']}")
        print(f"Projects: {data['total_projects']}")
        print(f"Extraction time: {data['extracted_at']}")
        print("="*50)
        
        # Run security checks
        security_data = extractor.run_security_checks(data)
        
        # Print security report
        extractor.print_security_report(security_data)
        
        # Add security data to the main data and save again
        data["security_audit"] = security_data
        extractor.save_to_json(data, "asana_data_with_security.json")
        print(f"\nData with security audit saved to asana_data_with_security.json")
        
    else:
        print("Failed to extract data")

if __name__ == "__main__":
    main()
