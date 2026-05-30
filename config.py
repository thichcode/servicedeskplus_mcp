"""
Configuration settings for ServiceDesk Plus MCP Server
Supports both Cloud and On-Premise API v3
"""

import os
import ssl
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    """Configuration class for ServiceDesk Plus MCP Server"""

    # ServiceDesk Plus Connection Settings
    SDP_BASE_URL: str = os.getenv("SDP_BASE_URL", "https://localhost:8080")
    SDP_USERNAME: str = os.getenv("SDP_USERNAME", "")
    SDP_PASSWORD: str = os.getenv("SDP_PASSWORD", "")
    SDP_API_KEY: str = os.getenv("SDP_API_KEY", "")
    SDP_API_TYPE: str = os.getenv("SDP_API_TYPE", "onpremise")  # "cloud" or "onpremise"
    SDP_PORTAL_ID: str = os.getenv("SDP_PORTAL_ID", "1")
    SDP_VERIFY_SSL: bool = os.getenv("SDP_VERIFY_SSL", "false").lower() in ["true", "1", "t", "yes"]

    # Request Settings
    REQUEST_TIMEOUT: int = int(os.getenv("SDP_TIMEOUT", "30"))
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 1000

    # API Endpoints (ServiceDesk Plus API v3)
    API_ENDPOINTS = {
        "requests": "/api/v3/requests",
        "request_filters": "/api/v3/request_filters",
        "request_notes": "/api/v3/requests/{request_id}/notes",
        "request_tasks": "/api/v3/requests/{request_id}/tasks",
        "request_worklogs": "/api/v3/requests/{request_id}/worklogs",
        "request_approvals": "/api/v3/requests/{request_id}/approvals",
        "request_attachments": "/api/v3/requests/{request_id}/attachments",
        "request_history": "/api/v3/requests/{request_id}/history",
        "request_sla": "/api/v3/requests/{request_id}/sla",
        "request_templates": "/api/v3/request_templates",
        "request_closure_codes": "/api/v3/closure_codes",
        "request_custom_fields": "/api/v3/requests/{request_id}/custom_fields",
        "request_feedback": "/api/v3/requests/{request_id}/feedback",
        "request_notifications": "/api/v3/requests/{request_id}/notifications",
        "users": "/api/v3/users",
        "technicians": "/api/v3/technicians",
        "changes": "/api/v3/changes",
        "problems": "/api/v3/problems",
        "projects": "/api/v3/projects",
        "milestones": "/api/v3/milestones",
        "releases": "/api/v3/releases",
        "tasks": "/api/v3/tasks",
        "assets": "/api/v3/assets",
        "asset_types": "/api/v3/asset_types",
        "asset_categories": "/api/v3/asset_categories",
        "asset_locations": "/api/v3/asset_locations",
        "asset_models": "/api/v3/asset_models",
        "asset_vendors": "/api/v3/asset_vendors",
        "contracts": "/api/v3/contracts",
        "contract_types": "/api/v3/contract_types",
        "contract_vendors": "/api/v3/contract_vendors",
        "purchase_orders": "/api/v3/purchase_orders",
        "po_statuses": "/api/v3/purchase_order_statuses",
        "vendors": "/api/v3/vendors",
        "vendor_types": "/api/v3/vendor_types",
        "sites": "/api/v3/sites",
        "site_types": "/api/v3/site_types",
        "user_groups": "/api/v3/user_groups",
        "group_types": "/api/v3/group_types",
        "group_permissions": "/api/v3/user_groups/{group_id}/permissions",
        "admin_users": "/api/v3/users",
        "admin_technicians": "/api/v3/technicians",
        "user_roles": "/api/v3/roles",
        "technician_roles": "/api/v3/roles",
        "admin_user_groups": "/api/v3/user_groups/{user_id}/groups",
        "admin_user_login_history": "/api/v3/admin/users/{user_id}/login_history",
        "admin_user_activity_log": "/api/v3/admin/users/{user_id}/activity_log",
        "permissions": "/api/v3/roles",
        "role_permissions": "/api/v3/roles/{role_id}",
        "user_permissions": "/api/v3/users/{user_id}/permissions",
        "departments": "/api/v3/departments",
        "department_types": "/api/v3/department_types",
        "locations": "/api/v3/locations",
        "location_types": "/api/v3/location_types",
        "system_settings": "/api/v3/settings",
        "email_settings": "/api/v3/settings/mail",
        "notification_settings": "/api/v3/settings/notification",
        "software_licenses": "/api/v3/software_licenses",
        "software_products": "/api/v3/software_products",
        "license_types": "/api/v3/license_types",
        "ci_types": "/api/v3/cmdb/ci_types",
        "cmdb": "/api/v3/cmdb",
        "solutions": "/api/v3/solutions",
        "campuses": "/api/v3/campus",
        "buildings": "/api/v3/building",
        "floors": "/api/v3/floor",
        "rooms": "/api/v3/room",
        "categories": "/api/v3/categories",
        "priorities": "/api/v3/priorities",
        "statuses": "/api/v3/statuses",
        "urgencies": "/api/v3/urgencies",
        "impacts": "/api/v3/impacts",
    }

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        issues = []
        valid = True

        if not cls.SDP_BASE_URL:
            issues.append("SDP_BASE_URL is not set in environment")
            valid = False
        elif not (cls.SDP_BASE_URL.startswith("http://") or cls.SDP_BASE_URL.startswith("https://")):
            issues.append("SDP_BASE_URL must start with http:// or https://")
            valid = False

        if not cls.SDP_API_KEY:
            issues.append("SDP_API_KEY is not set in environment")
            valid = False

        return {"valid": valid, "issues": issues}

    @classmethod
    def ssl_context(cls):
        if cls.SDP_VERIFY_SSL:
            return None
        return ssl._create_unverified_context()
