"""
Configuration settings for ServiceDesk Plus MCP Server
Supports both Cloud and On-Premise API v3
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for ServiceDesk Plus MCP Server"""
    
    # ServiceDesk Plus Connection Settings
    SDP_BASE_URL: str = os.getenv("SDP_BASE_URL", "https://your-servicedesk-plus.com")
    SDP_USERNAME: str = os.getenv("SDP_USERNAME", "")
    SDP_PASSWORD: str = os.getenv("SDP_PASSWORD", "")
    SDP_API_KEY: str = os.getenv("SDP_API_KEY", "")
    SDP_API_TYPE: str = os.getenv("SDP_API_TYPE", "cloud")  # "cloud" or "onpremise"
    
    # Request Settings
    REQUEST_TIMEOUT: int = 30
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 1000
    
    # API Endpoints (ServiceDesk Plus Cloud API v3)
    # Reference: 
    # - Cloud: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
    # - On-Premise: https://www.manageengine.com/products/service-desk/sdpod-v3-api/
    API_ENDPOINTS = {
        # Request (Ticket) Management
        "requests": "/api/v3/requests",
        "request_notes": "/api/v3/requests/{request_id}/notes",
        "request_tasks": "/api/v3/requests/{request_id}/tasks",
        "request_worklogs": "/api/v3/requests/{request_id}/worklogs",
        "request_filters": "/api/v3/list_view_filters/show_all",
        
        # User Management (Admin)
        "users": "/api/v3/admin/user",
        
        # Change Management
        "changes": "/api/v3/changes",
        "change_approvals": "/api/v3/changes/{change_id}/approvals",
        "change_tasks": "/api/v3/changes/{change_id}/tasks",
        
        # Problem Management (On-Premise)
        "problems": "/api/v3/problems",
        "problem_notes": "/api/v3/problems/{problem_id}/notes",
        "problem_tasks": "/api/v3/problems/{problem_id}/tasks",
        
        # Project Management
        "projects": "/api/v3/projects",
        "milestones": "/api/v3/milestones",
        "project_members": "/api/v3/projects/{project_id}/members",
        "project_tasks": "/api/v3/projects/{project_id}/tasks",
        
        # Release Management
        "releases": "/api/v3/releases",
        "release_notes": "/api/v3/releases/{release_id}/notes",
        "release_tasks": "/api/v3/releases/{release_id}/tasks",
        
        # Task Management
        "tasks": "/api/v3/tasks",
        
        # ============ On-Premise Only Modules ============
        
        # Asset Management
        "assets": "/api/v3/assets",
        
        # CMDB
        "cmdb": "/api/v3/cmdb",
        "ci_types": "/api/v3/cmdb/types",
        "ci_relationships": "/api/v3/cmdb/relationships",
        
        # Contract Management
        "contracts": "/api/v3/contracts",
        "contract_notes": "/api/v3/contracts/{contract_id}/notes",
        
        # Purchase Order Management
        "purchase_orders": "/api/v3/purchase_orders",
        
        # Solutions
        "solutions": "/api/v3/solutions",
        "topics": "/api/v3/topics",
        
        # Space Management
        "campuses": "/api/v3/campus",
        "buildings": "/api/v3/building",
        "floors": "/api/v3/floor",
        "rooms": "/api/v3/room",
        
        # Announcements
        "announcements": "/api/v3/announcements"
    }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration settings"""
        issues = []
        
        if not cls.SDP_BASE_URL or cls.SDP_BASE_URL == "https://your-servicedesk-plus.com":
            issues.append("SDP_BASE_URL is not configured")
            
        if not cls.SDP_API_KEY:
            issues.append("SDP_API_KEY is not configured")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    @classmethod
    def get_auth_headers(cls) -> Dict[str, str]:
        """Get authentication headers for API requests
        
        Cloud API uses 'authtoken' header
        On-Premise API uses 'Authorization: Zoho-oauthtoken' header
        
        Reference:
        - Cloud: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
        - On-Premise: https://www.manageengine.com/products/service-desk/sdpod-v3-api/
        """
        base_headers = {
            "Accept": "application/vnd.manageengine.sdp.v3+json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if cls.SDP_API_TYPE == "onpremise":
            base_headers["Authorization"] = f"Zoho-oauthtoken {cls.SDP_API_KEY}"
        else:
            base_headers["authtoken"] = cls.SDP_API_KEY
            
        return base_headers
