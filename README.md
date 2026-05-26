# ServiceDesk Plus MCP Server

MCP (Model Context Protocol) server dành cho **ManageEngine ServiceDesk Plus Cloud/On-Premise API v3** expose toàn bộ REST v3 dưới dạng các **Tool** chuẩn MCP. Dùng được ngay trên tất cả client MCP (VS Code, Cursor, Obsidian, CLI).

## API References

| Version | Endpoint | Header/example |
|---------|----------|----------------|
| Cloud | [sdpop-v3-api](https://www.manageengine.com/products/service-desk/sdpop-v3-api/) | `authtoken` |
| On-Premise | [sdpod-v3-api](https://www.manageengine.com/products/service-desk/sdpod-v3-api/) | `Zoho-oauthtoken` |

## Cách cài nhanh

```bash
git clone https://github.com/thichcode/servicedeskplus_mcp.git
cd servicedeskplus_mcp
pip install -r requirements.txt
```

### Cấu hình
```bash
cp env.example .env
```
`
# Cloud API  (trailing path NOT needed)
SDP_BASE_URL=https://yoursd.service-deskplus.com
SDP_API_KEY=xxxxxxxxxxxxxxxx
SDP_API_TYPE=cloud

# Hoặc On-Premise
# SDP_BASE_URL=https://your-sdp-host:8443
# SDP_API_TYPE=onpremise
```
Lấy token: Admin → Users → Generate API Key (Cloud); Admin → OAuth token (On-Prem).

---

## Chạy MCP Server (stdio)

```bash
python main.py
```
Output nhập chuẩn:
```
MCP server running on stdio://stdio
Registered tools: list_tickets, get_ticket, create_ticket, update_ticket, delete_ticket, assign_request, escalate_request, ...
```

Kết nối client (VS Code/Cursor/Obsidian) trỏ tới `stdout mcp`, tức là `python main.py`.

---

## Client Compatible Test

```python
import asyncio, mcp

async def main():
    params = mcp.stdio.get_stdio_parameters("python3 [./main.py]")
    async with mcp.ClientSession(params) as session:
        tools = await session.list_tools()
        print('Tools available:', len(tools))
        res = await session.call_tool('list_tickets', {'limit': 5, 'status': 'open'})
        print('Tickets:', res)

asyncio.run(main())
```
Nếu in ra danh sách ticket (hoặc lỗi xác thực) → server hoạt động đúng.

---

## Danh sách Tools tiêu biểu (hơn 40 tool)

| Tool | Mô tả | Input |
|------|-------|-------|
| `list_tickets` | Lấy danh sách tickets | `limit`, `status`, `priority`, `requester` |
| `get_ticket` | Chi tiết 1 ticket | `ticket_id` |
| `create_ticket` | Tạo ticket mới | `subject`, `description`, `requester`, `priority`, `category`, `technician` |
| `update_ticket` | Cập nhật ticket | `ticket_id`, `status`, `priority`, … |
| `delete_ticket` | Xóa ticket | `ticket_id` |
| `search_tickets` | Tìm kiếm theo từ khóa | `query`, `limit` |
| `add_ticket_comment` | Thêm comment | `ticket_id`, `comment` |
| `assign_request` | Gán request cho technician | `request_id`, `technician_id`, `group_id` |
| `escalate_request` | Escalate request cấp trên | `request_id`, `escalation_level`, `reason` |
| `approve_request` | Phê duyệt request | `request_id`, `approval_comments` |
| `reject_request` | Bác bỏ request | `request_id`, `rejection_reason`, `comments` |
| `close_request` | Đóng request | `request_id`, `closure_code`, `resolution` |
| `list_users` | Danh sách users | `limit` |
| `get_user` | Chi tiết user | `user_id` |
| `list_sites` | Danh sách sites | `limit`, `site_type`, `status` |
| `create_site` | Tạo site mới | `name`, `site_type`, `address`, `country`, ... |
| `list_admin_users` | Danh sách admin users | `limit`, `role`, `status` |
| `create_admin_user` | Tạo admin user | `username`, `email`, `first_name`, `last_name`, `role`, ... |
| `get_request_history` | Lịch sử request | `request_id`, `limit` |
| `get_request_sla_details` | Chi tiết SLA | `request_id` |
| `get_permissions` | Lấy permissions | — |
| `update_role_permissions` | Cập nhật permissions role | `role_id`, `permissions` |

Toàn bộ schema tools nằm trong **main.py** hàm `handle_list_tools()`, tự Registration MCP.

---

## Tài liệu thêm
- [main.py](main.py) — source MCP server
- [USAGE.md](USAGE.md) (trong repo) — hướng dẫn MCP chi tiết
- [sdp_client.py](sdp_client.py), [admin_client.py](admin_client.py), [config.py](config.py)

---

## Lỗi hay gặp & Debug
- **401 Unauthorized** → Kiểm tra `SDP_API_KEY` (Cloud) hay `Authorization: Zoho-oauthtoken` (On-Prem).
- **404 Not Found** → Kiểm tra `SDP_BASE_URL` không có đuôi `/` thừa.
- **Không thấy tools** → Đảm bảo vận hành `python main.py` trước (xuất ra danh sách tools).
- **TypeError / no module** → Cài `pip install mcp>=1.3.0 aiohttp python-dotenv`.

---

## Contributors
- [@thichcode](https://github.com/thichcode)

## License
MIT

[main]: main.py "Server MCP"
[USAGE]: USAGE.md "Hướng dẫn dùng MCP"
[sdp]: sdp_client.py "Client helper"
[admin]: admin_client.py "Admin client"
