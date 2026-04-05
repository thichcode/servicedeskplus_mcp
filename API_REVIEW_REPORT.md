# ServiceDesk Plus API v3 Review Report

**Ngày review:** 2026-04-05  
**Phiên bản API:** ServiceDesk Plus On-Premises v3  
**Nguồn tài liệu:** https://www.manageengine.com/products/service-desk/sdpop-v3-api/

---

## 1. Tổng quan Issues

| Mức độ | Số lượng | Mô tả |
|--------|----------|--------|
| 🔴 Critical | 5 | API endpoint sai, Authentication sai, Content-Type sai |
| 🟠 High | 3 | Mandatory fields validation sai |
| 🟡 Medium | 4 | Accept header thiếu |
| 🟢 Low | 2 | Các vấn đề nhỏ |

---

## 2. Issues Chi tiết

### 2.1 🔴 CRITICAL: API Endpoints Sai

**Vấn đề:** Code sử dụng endpoint `/api/v3/tickets` nhưng API chính thức dùng `/api/v3/requests`

| Module | Endpoint Hiện tại | Endpoint Đúng (API v3) |
|--------|-------------------|------------------------|
| Tickets/Requests | `/api/v3/tickets` | `/api/v3/requests` |
| Users | `/api/v3/users` | `/api/v3/users` (đúng) |
| Technicians | `/api/v3/technicians` | `/api/v3/technicians` (đúng) |
| Assets | `/api/v3/assets` | `/api/v3/assets` (đúng) |
| CMDB CI | `/api/v3/cmdb/ci` | `/api/v3/cmdb/{ci_type_api_name}` |

**Ảnh hưởng:** Tất cả operations liên quan đến tickets sẽ fail

**Chi tiết CMDB:**
- API đúng: `/api/v3/cmdb/{ci_type_api_name}` (ví dụ: `/api/v3/cmdb/ci_computer`)
- Code hiện tại: `/api/v3/cmdb/ci` (sai hoàn toàn)
- CI Type API name là dynamic, ví dụ: `ci_computer`, `ci_server`, `ci_network`

---

### 2.2 🔴 CRITICAL: Authentication Method Sai

**Vấn đề:** Code sử dụng Basic Auth nhưng API v3 dùng OAuth/Zoho Token

**Headers hiện tại (sai):**
```python
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-Key": cls.SDP_API_KEY  # Không đúng format
}
auth = aiohttp.BasicAuth(self.username, self.password)
```

**Headers đúng theo API v3:**
```python
headers = {
    "Accept": "application/vnd.manageengine.sdp.v3+json",
    "Authorization": "Zoho-oauthtoken {access_token}"
}
```

**Ghi chú:** 
- ServiceDesk Plus On-Premise có thể hỗ trợ Basic Auth cho On-Premise version
- Tuy nhiên header `Authorization` cần đúng format
- API Key nên được dùng qua parameter hoặc header đúng

---

### 2.3 🔴 CRITICAL: Content-Type và Data Format Sai

**Vấn đề:** Code dùng `application/json` nhưng API v3 yêu cầu `application/x-www-form-urlencoded`

**Format hiện tại (sai):**
```python
async with self.session.request(
    method="POST",
    url=url,
    json=json_data  # Sai: dùng json parameter
)
```

**Format đúng theo API v3:**
```python
# Data phải được wrap trong 'input_data' parameter
data = urlencode({"input_data": json.dumps(request_data)}).encode()

# Hoặc dùng form data
form = aiohttp.FormData()
form.add_field('input_data', json.dumps(request_data))
```

**Ví dụ Request body đúng:**
```json
{
  "request": {
    "subject": "Test Request",
    "description": "Description here",
    "requester": {
      "id": "123456"
    }
  }
}
```

---

### 2.4 🔴 CRITICAL: Accept Header Thiếu

**Vấn đề:** Code không có Accept header đúng format

**Header cần thêm:**
```python
"Accept": "application/vnd.manageengine.sdp.v3+json"
```

---

### 2.5 🔴 CRITICAL: CMDB CI API Endpoint Dynamic

**Vấn đề:** CMDB API endpoint phụ thuộc vào CI Type API name

**Code hiện tại:**
```python
"configuration_items": "/api/v3/cmdb/ci",
"ci_types": "/api/v3/cmdb/ci_types",
```

**Đúng theo API:**
```python
# List CI by Type - endpoint thay đổi theo ci_type_api_name
# Ví dụ: /api/v3/cmdb/ci_computer (list computers)
#         /api/v3/cmdb/ci_server (list servers)

# Get CI Types list
"ci_types": "/api/v3/cmdb/types"  # Endpoint để lấy danh sách CI types
```

---

### 2.6 🟠 HIGH: Mandatory Fields Validation Sai

**Assets Module:**
| Trường | Validation Hiện tại | Validation Đúng (API) |
|--------|---------------------|----------------------|
| create_asset | `name`, `asset_type` | `name`, `product` |

**Chi tiết:** API yêu cầu `product` (Product ID/Object) không phải `asset_type`

**Request Module:**
| Trường | Validation Hiện tại | Validation Đúng (API) |
|--------|---------------------|----------------------|
| create_request | `subject`, `description`, `requester` | Chỉ `subject` là mandatory |

**Chi tiết:** API chỉ yêu cầu `subject` là bắt buộc

---

### 2.7 🟠 HIGH: Requester Format

**Vấn đề:** Requester validation có thể không đúng format

**API yêu cầu requester như object:**
```json
"requester": {
  "id": "123456"
}
```

**Hoặc theo email:**
```json
"requester": {
  "email_id": "user@example.com"
}
```

---

### 2.8 🟠 HIGH: Asset Required Fields

**Code hiện tại:**
```python
required_fields = ["name", "asset_type"]
```

**Đúng theo API:**
```python
required_fields = ["name", "product"]  # product là required
```

---

### 2.9 🟡 MEDIUM: Missing Product Endpoint

**Thiếu:** `/api/v3/products` endpoint cho việc quản lý products

**API có:**
- Product Type: `/api/v3/admin/product_type`
- Product: `/api/v3/admin/product`

---

### 2.10 🟡 MEDIUM: Software License Endpoint

**Code hiện tại:**
```python
"software_licenses": "/api/v3/software_licenses",
"software_products": "/api/v3/software_products",
```

**Cần xác minh:** API v3 có thể dùng different endpoint structure cho licenses

---

### 2.11 🟡 MEDIUM: Site/Location Structure

**Vấn đề:** API v3 có Space module với hierarchical structure

**API v3 Space Module:**
- Campus: `/api/v3/campus`
- Building: `/api/v3/building`
- Non Building: `/api/v3/non_building`
- Floor: `/api/v3/floor`
- Room: `/api/v3/room`
- Room Partition: `/api/v3/room_partition`

**Code hiện tại chỉ có Sites và Locations đơn giản**

---

### 2.12 🟡 MEDIUM: Missing Contract/SLA Associations

**Vấn đề:** Code thiếu một số associations quan trọng

**Thiếu trong Asset:**
- Contract associations
- Software License associations
- Depreciation details

---

### 2.13 🟢 LOW: Response Status Code Handling

**Cải thiện:** API trả về response với cấu trúc:
```json
{
  "response_status": {
    "status_code": 2000,
    "status": "success"
  }
}
```

**Code nên kiểm tra `response_status.status_code` thay vì chỉ HTTP status**

---

### 2.14 🟢 LOW: Pagination Parameter Format

**Code hiện tại:**
```python
params = {"limit": min(limit, Config.MAX_LIMIT)}
```

**API v3 dùng:**
```python
# input_data chứa các filter parameters
input_data = {
    "list_info": {
        "start_index": 1,
        "page_size": 50
    }
}
```

---

## 3. Danh sách cần Sửa đổi

### 3.1 Priority 1 (Critical - Blockers)

- [ ] Đổi endpoint `/api/v3/tickets` → `/api/v3/requests`
- [ ] Fix CMDB endpoint: `/api/v3/cmdb/ci` → `/api/v3/cmdb/{ci_type_api_name}`
- [ ] Fix authentication: Thêm đúng Accept header và Authorization format
- [ ] Fix Content-Type: `application/json` → `application/x-www-form-urlencoded`
- [ ] Wrap data trong `input_data` parameter

### 3.2 Priority 2 (High - Important)

- [ ] Fix asset validation: `asset_type` → `product`
- [ ] Fix request validation: chỉ require `subject`
- [ ] Fix requester format: string → object

### 3.3 Priority 3 (Medium - Enhancement)

- [ ] Thêm Product endpoints
- [ ] Implement Space module (Campus, Building, Floor, Room)
- [ ] Fix pagination format
- [ ] Fix response status code handling

### 3.4 Priority 4 (Low - Nice to have)

- [ ] Thêm Contract/Software License associations cho Asset
- [ ] Thêm Software License management endpoints

---

## 4. Recommendations

### 4.1 Test với API thực tế

Trước khi fix, nên test với ServiceDesk Plus On-Premise instance thực tế để xác nhận:
- Authentication method nào được enable (Basic Auth vs OAuth)
- API version và endpoints thực tế

### 4.2 Documentation Reference

- Main API Index: https://www.manageengine.com/products/service-desk/sdpod-v3-api/getting-started/api-index.html
- Request API: https://www.manageengine.com/products/service-desk/sdpod-v3-api/requests/request.html
- Asset API: https://www.manageengine.com/products/service-desk/sdpod-v3-api/assets/asset.html
- CMDB API: https://www.manageengine.com/products/service-desk/sdpod-v3-api/cmdb/configuration_item.html

### 4.3 Suggested Implementation

Nên tạo một migration script để:
1. Map lại tất cả endpoints đúng
2. Implement dual authentication support (Basic Auth cho On-Premise, OAuth cho Cloud)
3. Fix data format theo API specification
4. Thêm proper error handling cho API response structure

---

## 5. Summary

| Issue Type | Count | Impact |
|------------|-------|--------|
| Critical | 5 | API sẽ fail hoàn toàn |
| High | 3 | Functionality không đúng |
| Medium | 4 | Missing features |
| Low | 2 | Enhancement |

**Kết luận:** Code hiện tại cần được refactor lớn để tuân thủ ServiceDesk Plus API v3 specification. Các critical issues cần được fix trước khi code có thể hoạt động đúng với API thực tế.
