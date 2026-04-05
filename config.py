"""
Configuration file for ServiceDesk Plus MCP Server
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for ServiceDesk Plus MCP Server"""
    
    # ServiceDesk Plus API Configuration
    SDP_BASE_URL = os.getenv("SDP_BASE_URL", "")
    SDP_USERNAME = os.getenv("SDP_USERNAME", "")
    SDP_PASSWORD = os.getenv("SDP_PASSWORD", "")
    SDP_API_KEY = os.getenv("SDP_API_KEY", "")
    
    # API Endpoints (ServiceDesk Plus Cloud API v3)
    # Reference: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
    API_ENDPOINTS = {
        # Request (Ticket) Management
        "requests": "/api/v3/requests",
        "request_notes": "/api/v3/requests/{request_id}/notes",
        "request_tasks": "/api/v3/requests/{request_id}/tasks",
        "request_filters": "/api/v3/list_view_filters/show_all",
        
        # Draft & Archive
        "drafts": "/api/v3/requests/draft",
        "archive": "/api/v3/requests/archive",
        
        # User Management (Admin)
        "users": "/api/v3/admin/user",
        
        # Change Management
        "changes": "/api/v3/changes",
        "change_approvals": "/api/v3/changes/{change_id}/approvals",
        "change_approval_levels": "/api/v3/changes/{change_id}/approval_levels",
        "change_tasks": "/api/v3/changes/{change_id}/tasks",
        
        # Project Management
        "projects": "/api/v3/projects",
        "milestones": "/api/v3/milestones",
        "project_members": "/api/v3/projects/{project_id}/members",
        "project_tasks": "/api/v3/projects/{project_id}/tasks",
        
        # Release Management
        "releases": "/api/v3/releases",
        "release_approvals": "/api/v3/releases/{release_id}/approvals",
        "release_approval_levels": "/api/v3/releases/{release_id}/approval_levels",
        "release_notes": "/api/v3/releases/{release_id}/notes",
        "release_tasks": "/api/v3/releases/{release_id}/tasks",
        "release_worklogs": "/api/v3/releases/{release_id}/worklogs",
        
        # Task Management
        "tasks": "/api/v3/tasks"
    }
    
    # Ticket Statuses
    TICKET_STATUSES = [
        "open",
        "pending",
        "resolved",
        "closed",
        "cancelled",
        "on_hold"
    ]
    
    # Ticket Priorities
    TICKET_PRIORITIES = [
        "low",
        "medium",
        "high",
        "critical"
    ]
    
    # Asset Statuses
    ASSET_STATUSES = [
        "in_use",
        "in_stock",
        "under_maintenance",
        "retired",
        "lost",
        "stolen"
    ]
    
    # CI Statuses
    CI_STATUSES = [
        "active",
        "inactive",
        "under_maintenance",
        "retired"
    ]
    
    # Contract Statuses
    CONTRACT_STATUSES = [
        "active",
        "expired",
        "pending",
        "terminated"
    ]
    
    # Purchase Order Statuses
    PO_STATUSES = [
        "draft",
        "pending_approval",
        "approved",
        "ordered",
        "received",
        "cancelled"
    ]
    
    # User Statuses
    USER_STATUSES = [
        "active",
        "inactive",
        "locked",
        "pending_activation"
    ]
    
    # User Roles
    USER_ROLES = [
        "admin",
        "manager",
        "technician",
        "user",
        "viewer"
    ]
    
    # Site Types
    SITE_TYPES = [
        "headquarters",
        "branch_office",
        "data_center",
        "warehouse",
        "retail_store",
        "manufacturing_plant"
    ]
    
    # Group Types
    GROUP_TYPES = [
        "department",
        "project",
        "location_based",
        "role_based",
        "custom"
    ]
    
    # Permission Levels
    PERMISSION_LEVELS = [
        "none",
        "read",
        "write",
        "admin"
    ]
    
    # Default pagination
    DEFAULT_LIMIT = 50
    MAX_LIMIT = 1000
    
    # Request timeout (seconds)
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not cls.SDP_BASE_URL:
            issues.append("SDP_BASE_URL is not set")
        
        if not cls.SDP_USERNAME:
            issues.append("SDP_USERNAME is not set")
        
        if not cls.SDP_PASSWORD:
            issues.append("SDP_PASSWORD is not set")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    @classmethod
    def get_auth_headers(cls) -> Dict[str, str]:
        """Get authentication headers for API requests (ServiceDesk Plus Cloud v3)
        
        Note: Cloud API uses 'authtoken' header for authentication
        Reference: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
        """
        return {
            "Accept": "application/vnd.manageengine.sdp.v3+json",
            "Content-Type": "application/x-www-form-urlencoded"
        } 