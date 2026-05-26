# Hướng dẫn dùng MCP Server ServiceDesk Plus

Repo **servicedeskplus_mcp** expose toàn bộ REST API v3 ServiceDesk Plus (Cloud & On-Prem) dưới dạng **Tool** theo chuẩn **Model Context Protocol (MCP)**. Server chạy trên Python, tương thích tất cả client MCP: VS Code, Cursor, Obsidian, CLI.

## 1. Cài MCP server

### Dependencies
```bash
pip install -r requirements.txt
```
Python 3.10+

### Cấu hình credentials (từ repo gốc)
```bash
cp env.example .env
```
Chỉnh sửa `.env`:
```env
# Cloud API
SDP_BASE_URL=https://yoursd.service-deskplus.com
SDP_API_KEY=your_cloud_api_key
SDP_API_TYPE=cloud

# Hoặc On-Premise
# SDP_BASE_URL=https://your-ip:8443
# SDP_API_TYPE=onpremise
```
- Lấy API Key Cloud: Admin → Users → Generate API Key
- Lấy OAuth Token On-Prem: Admin → OAuth tokens

### Chạy MCP Server
```bash
python main.py
```
Output chuẩn:
```
MCP server running on stdio://stdio
Registered tools: list_tickets, get_ticket, create_ticket, update_ticket, delete_ticket, assign_request, escalate_request, map_role_permissions, ...
```
Sau đó client MCP (VS Code/Cursor/Obsidian) kết nối tới `stdio://` này, tức là shell `python /path/to/main.py`.

## 2. Kết nối MCP từ Client

### VS Code
Cài extension **Model Context Protocol** (Works With AI...

Thêm vào `settings.json`:
```json
{
  "mcp.servers": {
    "servicedesk-plus": {
      "command": "python3",
      "args": ["/tmp/servicedeskplus_mcp/main.py"]
    }
  }
}
```
Sau đó bạn thấy panel **Tools** hiển thị toàn bộ API: `list_tickets`, `create_ticket`, v.v.

### Cursor / Obsidian / CLI
- Cursor: chỉnh cấu hình tương tự trong `cursor.mcp.json`
- Obsidian: dùng plugin MCP (áp dụng cấu hình server giống)

## 3. Gọi Tool từ client

Ví dụ (Python CLI):
```python
import asyncio, mcp

async def main():
    params = mcp.stdio.get_stdio_parameters("python /tmp/servicedeskplus_mcp/main.py")
    async with mcp.ClientSession(params) as session:
        tools = await session.list_tools()
        print('Số tool:', len(tools))
        ticket_resp = await session.call_tool('list_tickets', {
            'limit': 5,
            'status': 'open'
        })
        print('Tickets:', ticket_resp)

asyncio.run(main())
```

Output hợp lệ: `Tickets: {"tickets": [...], ...}` tức MCP server hoạt động.

## 4. Mô tả API + Tools

MCP Server đăng ký sẵn ≈40 tool tương ứng với API v3 ServiceDesk Plus:

- **Quản lý: Request/Ticket**
  - `list_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `delete_ticket`
  - `add_ticket_comment`, `get_ticket_comments`, `search_tickets`, `assign_request`
  - `escalate_request`, `approve_request`, `reject_request`, `close_request`, `get_closure_codes`

- **Quản trị: Site/User/Group/Permissions**
  - `list_sites`, `create_site`, `list_admin_users`, `create_admin_user`, `update_admin_technician`
  - `get_permissions`, `get_role_permissions`, `update_role_permissions`

- **Asset/CMDB (On-Prem only)**

  - `list_assets`, `get_asset`, `get_configuration_items`

Full danh sách tool xem source code `main.py` tại:
```python
@server.list_tools
def handle_list_tools():
    return tools_list  # khoảng 40 tools
```

## 5. Tải thư viện helpers (tùy chọn)

- `sdp_client.py` — wrapper async tiện cho người dùng Python
- `admin_client.py` — helper CRUD admin users/technicians
- `config.py` — load .env an toàn

## 6. Debug phổ biến

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| 401 | Sai token / thiếu OAuth header | Kiểm tra `SDP_API_KEY` & `SDP_API_TYPE`; Lấy đúng token từ Admin |
| 404 | URL sai (thừa /) | Đảm bảo `SDP_BASE_URL` ko có / tận cùng |
| Tools không hiển thị | Server chưa chạy hoặc lỗi import | Chạy `python main.py` và kiểm tra output console chương trình |
| Phiên bản Python thiếu | `mcp>=1.3.0` | `pip install mcp aiohttp python-dotenv` |

## 7. Deploy (nếu cần)

### Systemd service (Linux)
```ini
[Unit]
Description=ServiceDeskPlus MCP Server
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/servicedeskplus_mcp
ExecStart=/usr/bin/python3 /path/to/servicedeskplus_mcp/main.py
Restart=always
EnvironmentFile=/path/to/servicedeskplus_mcp/.env

[Install]
WantedBy=multi-user.target
```
### Docker (Dockerfile)
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "main.py" ]
```

Chạy:
```bash
docker build -t servicedeskplus-mcp .
docker run -v $(pwd)/.env:/app/.env servicedeskplus-mcp
```
Server xuất ra: `stdio://stdio — running`

## 8. Tài liệu chính thức
- [quyển repo](https://github.com/thichcode/servicedeskplus_mcp)
- [API Cloud](https://www.manageengine.com/products/service-desk/sdpop-v3-api/)
- [API On-Prem](https://www.manageengine.com/products/service-desk/sdpod-v3-api/)

---

**Tham gia đóng góp**
PR welcome — test, doc, bug fixes.

@thichcode 2026
