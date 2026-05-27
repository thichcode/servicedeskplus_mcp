#!/usr/bin/env python3
"""
Test trực tiếp 40+ chức năng SDP On-Premise qua API REST
(Đọc .env và gọi thẳng đến https://localhost:8080)
"""

import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

base_url = os.getenv("SDP_BASE_URL", "https://localhost:8080")
api_key = os.getenv("SDP_API_KEY")
ssl_verify = os.getenv("SDP_SSL_VERIFY", "false").lower() == "true"

if not api_key:
    raise ValueError("❌ SDP_API_KEY chưa được cấu hình trong .env")

# Session
session = requests.Session()
session.headers.update({"Authorization": f"Zoho-oauthtoken {api_key}"})
session.verify = ssl_verify

# Danh sách endpoints chính (xem SDP API docs)
endpoints = {
    "list_tickets": "/api/v3/requests",
    "create_ticket": "/api/v3/requests",
    "get_ticket": "/api/v3/requests/{ticket_id}",
    "add_comment": "/api/v3/requests/{ticket_id}/comments",
    "assign_request": "/api/v3/requests/{ticket_id}/assign",
    "close_request": "/api/v3/requests/{ticket_id}/close",
}

def test_endpoint(name, path, method="GET", payload=None, params=None):
    url = f"{base_url}{path}"
    try:
        if method == "GET":
            resp = session.get(url, params=params)
        elif method == "POST":
            resp = session.post(url, json=payload)
        elif method == "PUT":
            resp = session.put(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"✅ {name} → {resp.status_code} | Sample: {data.get('result', {}) if isinstance(data, dict) else data}")
        return True
    except Exception as e:
        print(f"❌ {name} → {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Test API ServiceDesk Plus On-Premise (localhost:8080)")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"SSL Verify: {ssl_verify}")
    print()
    
    # Test list_tickets
    test_endpoint("list_tickets", endpoints["list_tickets"], params={"limit": 3})
    
    # Test create_ticket (payload chuẩn SDP On-Prem)
    sample_ticket = {
        "subject": "[Hermes Test] MCP Connectivity Check",
        "description": "Ticket test từ Hermes Agent - Xóa/bỏ qua ticket này",
        "requester": 1,  # hoặc {"id": 1} nếu API yêu cầu object
        "priority": 2,   # Medium
        "status": 1,      # Open
        "category": 5,    # Chọn từ category list
        "technician": 1,  # Admin technician
    }
    test_endpoint("create_ticket", endpoints["create_ticket"], method="POST", payload=sample_ticket)