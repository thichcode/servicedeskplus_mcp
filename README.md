# ServiceDesk Plus MCP Server

MCP (Model Context Protocol) server để tích hợp với ServiceDesk Plus API v3.

## API References

| Version | Documentation | Authentication |
|---------|--------------|----------------|
| **Cloud** | [sdpop-v3-api](https://www.manageengine.com/products/service-desk/sdpop-v3-api/) | `authtoken` header |
| **On-Premise** | [sdpod-v3-api](https://www.manageengine.com/products/service-desk/sdpod-v3-api/) | `Authorization: Zoho-oauthtoken` |

## 🎯 **Tính năng**

### **Request (Ticket) Management** (Cả 2 API)
- ✅ CRUD operations cho requests
- ✅ Notes, Tasks, Worklogs
- ✅ Assign, pickup, close requests
- ✅ Search và filtering

### **User Management** (Cả 2 API)
- ✅ CRUD operations cho users

### **Change Management** (Cả 2 API)
- ✅ CRUD operations cho changes
- ✅ Approvals, Tasks

### **Project Management** (Cả 2 API)
- ✅ CRUD operations cho projects
- ✅ Milestones, Members, Tasks

### **Release Management** (Cả 2 API)
- ✅ CRUD operations cho releases
- ✅ Notes, Tasks

### **Task Management** (Cả 2 API)
- ✅ CRUD operations cho general tasks

### **Problem Management** (Chỉ On-Premise)
- ✅ CRUD operations cho problems
- ✅ Notes, Tasks

### **Asset Management** (Chỉ On-Premise)
- ✅ CRUD operations cho assets

### **CMDB Management** (Chỉ On-Premise)
- ✅ CI Types, Configuration Items
- ✅ CI Relationships

### **Contract Management** (Chỉ On-Premise)
- ✅ CRUD operations cho contracts

### **Purchase Order Management** (Chỉ On-Premise)
- ✅ CRUD operations cho purchase orders

### **Solutions** (Chỉ On-Premise)
- ✅ Get solutions, topics

### **Space Management** (Chỉ On-Premise)
- ✅ Campuses, Buildings, Floors, Rooms

## 🚀 **Cài đặt**

### 1. Clone repository
```bash
git clone https://github.com/thichcode/servicedeskplus_mcp.git
cd servicedeskplus_mcp
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình
Copy `env.example` sang `.env` và điền thông tin:

```bash
# Cloud API
SDP_BASE_URL=https://yourdomain.service-deskplus.com
SDP_API_KEY=your_api_key_here
SDP_API_TYPE=cloud

# Hoặc On-Premise API
# SDP_BASE_URL=https://your-servicedesk.com:8443
# SDP_API_KEY=your_oauth_token_here
# SDP_API_TYPE=onpremise
```

### 4. Chạy server
```bash
python server.py
```

## 📡 **API Authentication**

### Cloud API
```python
headers = {
    "authtoken": "your_api_key",
    "Accept": "application/vnd.manageengine.sdp.v3+json"
}
```

### On-Premise API
```python
headers = {
    "Authorization": "Zoho-oauthtoken your_oauth_token",
    "Accept": "application/vnd.manageengine.sdp.v3+json"
}
```

## 📚 **Ví dụ sử dụng**

```python
from sdp_client import ServiceDeskPlusClient

# Cloud API
async with ServiceDeskPlusClient(api_type="cloud") as client:
    # Get requests
    requests = await client.get_requests(limit=10)
    
    # Create request
    new_request = await client.create_request({
        "subject": "Test Request",
        "description": "Description here"
    })

# On-Premise API
async with ServiceDeskPlusClient(api_type="onpremise") as client:
    # Get assets (On-Premise only)
    assets = await client.get_assets()
    
    # Get CMDB CIs (On-Premise only)
    computers = await client.get_configuration_items("ci_computer")
```

## 📋 **Yêu cầu**

- Python 3.8+
- aiohttp
- python-dotenv

## 📄 **License**

MIT License
