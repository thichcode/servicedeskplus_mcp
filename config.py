"""
Configuration settings for ServiceDesk Plus MCP Server
Supports both Cloud and On-Premise API v3
"""

import os
import ssl
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for ServiceDesk Plus MCP Server"""

    # ServiceDesk Plus Connection Settings
    SDP_BASE_URL: str = os.getenv("SDP_BASE_URL", "https://localhost:8080")
    SDP_USERNAME: str = os.getenv("SDP_USERNAME", "")
    SDP_PASSWORD: str = os.getenv("SDP_PASSWORD", "")
    SDP_API_KEY: str = os.getenv("SDP_API_KEY", "")
    SDP_API_TYPE: str = os.getenv("SDP_API_TYPE", "onpremise")  # "cloud" or "onpremise"
    SDP_VERIFY_SSL: bool = os.getenv("SDP_VERIFY_SSL", "false").lower() in ["true", "1", "t", "yes"]

    # Request Settings
    REQUEST_TIMEOUT: int = int(os.getenv("SDP_TIMEOUT", "30"))
    DEFAULT_LIMIT: int = 20
    MAX_LIMIT: int = 1000

    # API Endpoints (ServiceDesk Plus API v3)
    API_ENDPOINTS = {
        "requests": "/api/v3/requests",
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
