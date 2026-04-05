# ServiceDesk Plus MCP Server

MCP (Model Context Protocol) server để tích hợp với ServiceDesk Plus Cloud API v3.

**Reference:** https://www.manageengine.com/products/service-desk/sdpop-v3-api/

## 🎯 **Tính năng**

### **Request (Ticket) Management**
- ✅ CRUD operations cho requests
- ✅ Tìm kiếm và lọc với search_criteria
- ✅ Quản lý notes và tasks
- ✅ Assign, pickup, close requests
- ✅ Draft và Archive management

### **User Management (Admin)**
- ✅ CRUD operations cho users
- ✅ Tìm kiếm users

### **Change Management**
- ✅ CRUD operations cho changes
- ✅ Approve/Reject changes
- ✅ Change tasks

### **Project Management**
- ✅ CRUD operations cho projects
- ✅ Milestones management
- ✅ Project members và tasks

### **Release Management**
- ✅ CRUD operations cho releases
- ✅ Approve/Reject releases
- ✅ Release notes, tasks, worklogs

### **Task Management**
- ✅ CRUD operations cho general tasks

### **Authentication**
- ✅ API Key authentication qua `authtoken` header
- ✅ Async/await cho high performance
- ✅ Comprehensive error handling
- ✅ Pagination và filtering

## 📦 **Cài đặt**

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Tạo file `.env` với thông tin cấu hình:**
```env
SDP_BASE_URL=https://your-servicedesk-plus-instance.com
SDP_USERNAME=your_username
SDP_PASSWORD=your_password
SDP_API_KEY=your_api_key
```

3. **Chạy MCP server:**
```bash
python main.py
```

## ⚙️ **Cấu hình MCP Client**

### **Với Claude Desktop**

Thêm vào file cấu hình MCP (`~/.config/claude/desktop-config.json`):

```json
{
  "mcpServers": {
    "servicedesk-plus": {
      "command": "python",
      "args": ["/path/to/servicedeskplus_mcp/main.py"],
      "env": {
        "SDP_BASE_URL": "https://your-instance.com",
        "SDP_USERNAME": "your_username",
        "SDP_PASSWORD": "your_password"
      }
    }
  }
}
```

### **Với Cursor**

Thêm vào file cấu hình MCP:

```json
{
  "mcpServers": {
    "servicedesk-plus": {
      "command": "python",
      "args": ["/path/to/servicedeskplus_mcp/main.py"]
    }
  }
}
```

## 🛠️ **API Endpoints**

### **Ticket Management (15 tools)**
- `list_tickets` - Lấy danh sách tickets với bộ lọc
- `get_ticket` - Lấy thông tin chi tiết ticket
- `create_ticket` - Tạo ticket mới
- `update_ticket` - Cập nhật ticket
- `delete_ticket` - Xóa ticket
- `search_tickets` - Tìm kiếm tickets
- `add_ticket_comment` - Thêm comment
- `get_ticket_comments` - Lấy comments

### **CMDB - Configuration Items (7 tools)**
- `list_configuration_items` - Lấy danh sách CIs
- `get_configuration_item` - Lấy chi tiết CI
- `create_configuration_item` - Tạo CI mới
- `update_configuration_item` - Cập nhật CI
- `delete_configuration_item` - Xóa CI
- `get_ci_types` - Lấy loại CIs
- `get_ci_relationships` - Lấy relationships

### **Asset Management (10 tools)**
- `list_assets` - Lấy danh sách assets
- `get_asset` - Lấy chi tiết asset
- `create_asset` - Tạo asset mới
- `update_asset` - Cập nhật asset
- `delete_asset` - Xóa asset
- `get_asset_types` - Lấy loại assets
- `get_asset_categories` - Lấy danh mục assets
- `get_asset_locations` - Lấy vị trí assets
- `get_asset_models` - Lấy model assets
- `get_asset_vendors` - Lấy vendor assets

### **Software License Management (6 tools)**
- `list_software_licenses` - Lấy danh sách licenses
- `get_software_license` - Lấy chi tiết license
- `create_software_license` - Tạo license mới
- `update_software_license` - Cập nhật license
- `get_software_products` - Lấy software products
- `get_license_types` - Lấy loại licenses

### **Contract Management (6 tools)**
- `list_contracts` - Lấy danh sách contracts
- `get_contract` - Lấy chi tiết contract
- `create_contract` - Tạo contract mới
- `update_contract` - Cập nhật contract
- `get_contract_types` - Lấy loại contracts
- `get_contract_vendors` - Lấy vendor contracts

### **Purchase Order Management (5 tools)**
- `list_purchase_orders` - Lấy danh sách POs
- `get_purchase_order` - Lấy chi tiết PO
- `create_purchase_order` - Tạo PO mới
- `update_purchase_order` - Cập nhật PO
- `get_po_statuses` - Lấy trạng thái POs

### **Vendor Management (5 tools)**
- `list_vendors` - Lấy danh sách vendors
- `get_vendor` - Lấy chi tiết vendor
- `create_vendor` - Tạo vendor mới
- `update_vendor` - Cập nhật vendor
- `get_vendor_types` - Lấy loại vendors

### **Admin Management - Sites (6 tools)**
- `list_sites` - Lấy danh sách sites
- `get_site` - Lấy chi tiết site
- `create_site` - Tạo site mới
- `update_site` - Cập nhật site
- `delete_site` - Xóa site
- `get_site_types` - Lấy loại sites

### **Admin Management - User Groups (8 tools)**
- `list_user_groups` - Lấy danh sách user groups
- `get_user_group` - Lấy chi tiết user group
- `create_user_group` - Tạo user group mới
- `update_user_group` - Cập nhật user group
- `delete_user_group` - Xóa user group
- `get_group_types` - Lấy loại groups
- `get_group_permissions` - Lấy permissions của group
- `update_group_permissions` - Cập nhật permissions cho group

### **Admin Management - Users & Technicians (12 tools)**
- `list_admin_users` - Lấy danh sách admin users
- `get_admin_user` - Lấy chi tiết admin user
- `create_admin_user` - Tạo admin user mới
- `update_admin_user` - Cập nhật admin user
- `delete_admin_user` - Xóa admin user
- `list_admin_technicians` - Lấy danh sách admin technicians
- `get_admin_technician` - Lấy chi tiết admin technician
- `create_admin_technician` - Tạo admin technician mới
- `update_admin_technician` - Cập nhật admin technician
- `delete_admin_technician` - Xóa admin technician
- `get_user_roles` - Lấy user roles
- `get_technician_roles` - Lấy technician roles

### **Admin Management - Permissions (5 tools)**
- `get_permissions` - Lấy danh sách permissions
- `get_role_permissions` - Lấy permissions của role
- `update_role_permissions` - Cập nhật permissions cho role
- `get_user_permissions` - Lấy permissions của user
- `update_user_permissions` - Cập nhật permissions cho user

### **Admin Management - Departments (6 tools)**
- `list_departments` - Lấy danh sách departments
- `get_department` - Lấy chi tiết department
- `create_department` - Tạo department mới
- `update_department` - Cập nhật department
- `delete_department` - Xóa department
- `get_department_types` - Lấy loại departments

### **Admin Management - Locations (6 tools)**
- `list_locations` - Lấy danh sách locations
- `get_location` - Lấy chi tiết location
- `create_location` - Tạo location mới
- `update_location` - Cập nhật location
- `delete_location` - Xóa location
- `get_location_types` - Lấy loại locations

### **Admin Management - System Settings (6 tools)**
- `get_system_settings` - Lấy system settings
- `update_system_settings` - Cập nhật system settings
- `get_email_settings` - Lấy email settings
- `update_email_settings` - Cập nhật email settings
- `get_notification_settings` - Lấy notification settings
- `update_notification_settings` - Cập nhật notification settings

### **User Management (3 tools)**
- `list_users` - Lấy danh sách users
- `get_user` - Lấy thông tin user
- `list_technicians` - Lấy danh sách technicians

### **Reference Data (3 tools)**
- `get_categories` - Lấy danh mục tickets
- `get_priorities` - Lấy mức độ ưu tiên
- `get_statuses` - Lấy trạng thái tickets

## 🎯 **Ví dụ Sử Dụng**

### **Quản lý Infrastructure:**
```
"Tạo Configuration Item cho server database mới 'DB-SRV-001'"
"Lấy danh sách tất cả network devices đang hoạt động"
"Tạo asset cho switch mới và gán vào data center"
```

### **Quản lý Software:**
```
"Tạo software license cho Adobe Creative Suite với 50 licenses"
"Kiểm tra số lượng licenses còn lại cho Microsoft Office"
"Cập nhật license Adobe với ngày hết hạn mới"
```

### **Quản lý Contracts:**
```
"Tạo contract bảo trì với vendor Dell cho 3 năm"
"Lấy danh sách contracts sắp hết hạn trong 30 ngày tới"
"Cập nhật contract Microsoft với giá trị mới"
```

### **Quản lý Procurement:**
```
"Tạo purchase order cho 20 monitors từ vendor HP"
"Kiểm tra trạng thái purchase order PO-2024-001"
"Cập nhật PO với ngày giao hàng mới"
```

### **Quản lý Admin:**
```
"Tạo site mới 'Branch Office Hanoi' với loại branch_office"
"Tạo user group 'IT Support Team' và gán permissions"
"Tạo admin user 'john.doe' với role technician"
"Cập nhật permissions cho role 'manager'"
"Tạo department 'Software Development'"
"Lấy danh sách tất cả locations trong site 'Headquarters'"
"Cập nhật email settings cho thông báo tickets"
```

## 📊 **Tính năng Nổi Bật**

- **🔄 Async/await** - Hiệu suất cao với async operations
- **🛡️ Error handling** - Xử lý lỗi toàn diện
- **🔐 Authentication** - Hỗ trợ Basic Auth và API Key
- **📄 Pagination** - Quản lý dữ liệu lớn hiệu quả
- **🔍 Filtering** - Bộ lọc linh hoạt cho tất cả endpoints
- **📝 Validation** - Kiểm tra dữ liệu đầu vào
- **📊 Logging** - Ghi log chi tiết cho debugging
- **⚙️ Configuration** - Quản lý cấu hình linh hoạt

## 🚀 **Lợi Ích**

1. **Centralized Management** - Quản lý tập trung toàn bộ IT infrastructure
2. **Compliance Tracking** - Theo dõi compliance với licenses và contracts
3. **Asset Lifecycle** - Quản lý toàn bộ lifecycle của assets
4. **Vendor Management** - Quản lý hiệu quả các vendor relationships
5. **Procurement Automation** - Tự động hóa quy trình mua sắm
6. **Reporting & Analytics** - Báo cáo và phân tích dữ liệu CMDB
7. **AI Integration** - Tích hợp AI để tự động hóa các tác vụ

## 📚 **Tài liệu Chi tiết**

- [📖 Hướng dẫn sử dụng chi tiết](USAGE.md)
- [🏗️ Tính năng CMDB](CMDB_FEATURES.md)
- [🧪 Test Connection](test_connection.py)

## 🔧 **Troubleshooting**

Chạy script test để kiểm tra kết nối:
```bash
python test_connection.py
```

Kiểm tra logs để debug:
```bash
python main.py --verbose
```

---

**Version:** 2.0.0  
**Total Tools:** 100+ tools  
**CMDB Support:** ✅ Full Support  
**Admin Management:** ✅ Full Support  
**License:** MIT 