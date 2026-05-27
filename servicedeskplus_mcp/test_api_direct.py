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
ssl_verify = os.getenv("SDP_SSL_VERIFY", "False").lower() in ("true", "1", "yes")

if not api_key:
    raise ValueError("❌ SDP_API_KEY chưa được cấu hình trong .env")

# Disable SSL verification for requests globally
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Session
session = requests.Session()
session.headers.update({"Authorization": f"Zoho-oauthtoken {api_key}"})
session.verify = False

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
    headers = {"Authorization": f"Zoho-oauthtoken {api_key}", "Accept": "application/json"}

    try:
        print(f"→ Chạy {method} {url}")
        print(f"→ Headers: {headers}")
        if payload:
            print(f"→ Payload: {json.dumps(payload) if isinstance(payload, dict) else payload}")

        if method == "GET":
            resp = session.get(url, headers=headers, params=params, verify=False)
        elif method == "POST":
            # SDP On-Premise yêu cầu input_data là chuỗi JSON trong form-data
            data = {"input_data": json.dumps(payload)} if payload else None
            print(f"→ Form-data: {data}")
            resp = session.post(url, headers=headers, data=data, verify=False)
        elif method == "PUT":
            data = {"input_data": json.dumps(payload)} if payload else None
            resp = session.put(url, headers=headers, data=data, verify=False)

        if resp.status_code == 400:
            print(f"⚠️ {name} → {resp.status_code} | Error: {resp.text}")
            # In thêm headers gửi đi để debug
            print(f"→ Request Headers: {dict(resp.request.headers)}")
            print(f"→ Payload: {data}")
        else:
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ {name} → {resp.status_code} | Sample: {data.get('result', {})}")
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
    
    # Test create_ticket (tạo ticket mẫu)
    sample_ticket = {
        "subject": "[Test] MCP Server Check",
        "description": "Test từ Hermes Agent - bỏ qua nếu thấy ticket này.",
        "requester": {"id": 1},
        "priority": {"name": "Medium"},
        "status": {"name": "Open"},
        "category": {"name": "Technical"},
    }
    test_endpoint("create_ticket", endpoints["create_ticket"], method="POST", payload=sample_ticket)