# ServiceDesk Plus MCP Server

MCP (Model Context Protocol) server for **ManageEngine ServiceDesk Plus** — exposes the full REST API v3 as **141 MCP tools**. Works with both **Cloud** and **On-Premise** (v14.x+) instances.

## Features

- **141 tools** covering all SDP modules
- **Dual auth**: Cloud (`authtoken` header) + On-Premise (session cookie + `Authtoken` header)
- **stdio transport** — plug directly into VS Code, Cursor, Obsidian, Claude Desktop, or any MCP client
- **Async** — built on `aiohttp` (Cloud) and `requests` (On-Premise session)

## Quick Start

```bash
git clone https://github.com/thichcode/servicedeskplus_mcp.git
cd servicedeskplus_mcp
pip install -r requirements.txt
```

### Configure

```bash
cp env.example .env
```

Edit `.env`:

```env
# Cloud
SDP_BASE_URL=https://yourdomain.service-deskplus.com
SDP_API_KEY=your_api_key
SDP_API_TYPE=cloud

# On-Premise
SDP_BASE_URL=https://localhost:8080
SDP_API_KEY=your_api_key
SDP_API_TYPE=onpremise
SDP_USERNAME=administrator
SDP_PASSWORD=
```

Get your API key:
- **Cloud**: Admin → Users → Edit user → API Key
- **On-Premise**: Admin → OAuth token (or Users → API Key generation)

### Run

```bash
python main.py
```

The server starts on stdio and registers all tools. Connect your MCP client to `python main.py`.

## Client Configuration

### VS Code / Cursor

```json
{
  "mcp": {
    "servers": {
      "servicedesk-plus": {
        "command": "python",
        "args": ["path/to/main.py"],
        "cwd": "path/to/servicedeskplus_mcp"
      }
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "servicedesk-plus": {
      "command": "python",
      "args": ["path/to/main.py"]
    }
  }
}
```

## Available Tools (141)

### Ticket Management (33 tools)

| Tool | Description |
|------|-------------|
| `list_tickets` | List tickets with filters (status, priority, requester) |
| `get_ticket` | Get ticket details by ID |
| `create_ticket` | Create a new ticket |
| `update_ticket` | Update ticket fields |
| `delete_ticket` | Delete a ticket |
| `search_tickets` | Full-text search across tickets |
| `add_ticket_comment` | Add a comment to a ticket |
| `get_ticket_comments` | Get all comments on a ticket |
| `assign_request` | Assign to technician/group |
| `reassign_request` | Reassign to different technician/group |
| `escalate_request` | Escalate to higher level |
| `approve_request` | Approve a pending request |
| `reject_request` | Reject a pending request |
| `get_request_approvals` | Get approval status |
| `get_request_attachments` | List attachments |
| `add_request_attachment` | Upload an attachment |
| `delete_request_attachment` | Remove an attachment |
| `get_request_history` | Get activity history |
| `get_request_sla_details` | Get SLA info |
| `update_request_sla` | Update SLA settings |
| `get_request_templates` | List request templates |
| `create_request_from_template` | Create ticket from template |
| `close_request` | Close with resolution code |
| `get_closure_codes` | List available closure codes |
| `get_request_worklog` | Get work logs |
| `add_worklog_entry` | Add work log entry |
| `update_worklog_entry` | Update work log entry |
| `get_request_custom_fields` | Get custom field values |
| `update_request_custom_fields` | Update custom fields |
| `get_request_feedback` | Get requester feedback |
| `submit_request_feedback` | Submit feedback |
| `get_request_notifications` | Get notifications |
| `send_request_notification` | Send notification |

### User Management (4 tools)

| Tool | Description |
|------|-------------|
| `list_users` | List all users |
| `get_user` | Get user by ID |
| `list_technicians` | List all technicians |

### CMDB (6 tools)

| Tool | Description |
|------|-------------|
| `list_configuration_items` | List CIs |
| `get_configuration_item` | Get CI details |
| `create_configuration_item` | Create a CI |
| `update_configuration_item` | Update a CI |
| `delete_configuration_item` | Delete a CI |
| `get_ci_types` | List CI types |
| `get_ci_relationships` | List CI relationships |

### Asset Management (8 tools)

| Tool | Description |
|------|-------------|
| `list_assets` | List assets |
| `get_asset` | Get asset details |
| `create_asset` | Create an asset |
| `update_asset` | Update an asset |
| `delete_asset` | Delete an asset |
| `get_asset_types` | List asset types |
| `get_asset_categories` | List asset categories |
| `get_asset_locations` | List asset locations |
| `get_asset_models` | List asset models |
| `get_asset_vendors` | List asset vendors |

### Software License Management (5 tools)

| Tool | Description |
|------|-------------|
| `list_software_licenses` | List licenses |
| `get_software_license` | Get license details |
| `create_software_license` | Create a license |
| `update_software_license` | Update a license |
| `get_software_products` | List products |
| `get_license_types` | List license types |

### Contract Management (5 tools)

| Tool | Description |
|------|-------------|
| `list_contracts` | List contracts |
| `get_contract` | Get contract details |
| `create_contract` | Create a contract |
| `update_contract` | Update a contract |
| `get_contract_types` | List contract types |
| `get_contract_vendors` | List vendors |

### Purchase Order Management (5 tools)

| Tool | Description |
|------|-------------|
| `list_purchase_orders` | List POs |
| `get_purchase_order` | Get PO details |
| `create_purchase_order` | Create a PO |
| `update_purchase_order` | Update a PO |
| `get_po_statuses` | List PO statuses |

### Vendor Management (5 tools)

| Tool | Description |
|------|-------------|
| `list_vendors` | List vendors |
| `get_vendor` | Get vendor details |
| `create_vendor` | Create a vendor |
| `update_vendor` | Update a vendor |
| `get_vendor_types` | List vendor types |

### Admin: Sites (6 tools)

| Tool | Description |
|------|-------------|
| `list_sites` | List sites |
| `get_site` | Get site details |
| `create_site` | Create a site |
| `update_site` | Update a site |
| `delete_site` | Delete a site |
| `get_site_types` | List site types |

### Admin: User Groups (8 tools)

| Tool | Description |
|------|-------------|
| `list_user_groups` | List groups |
| `get_user_group` | Get group details |
| `create_user_group` | Create a group |
| `update_user_group` | Update a group |
| `delete_user_group` | Delete a group |
| `get_group_types` | List group types |
| `get_group_permissions` | Get group permissions |
| `update_group_permissions` | Update group permissions |

### Admin: Users & Technicians (22 tools)

| Tool | Description |
|------|-------------|
| `list_admin_users` | List admin users |
| `get_admin_user` | Get admin user details |
| `create_admin_user` | Create admin user |
| `update_admin_user` | Update admin user |
| `delete_admin_user` | Delete admin user |
| `list_admin_technicians` | List admin technicians |
| `get_admin_technician` | Get technician details |
| `create_admin_technician` | Create technician |
| `update_admin_technician` | Update technician |
| `delete_admin_technician` | Delete technician |
| `get_user_roles` | List user roles |
| `get_technician_roles` | List technician roles |
| `convert_user_to_technician` | Convert user to technician |
| `activate_admin_user` | Activate a user |
| `deactivate_admin_user` | Deactivate a user |
| `lock_admin_user` | Lock a user account |
| `unlock_admin_user` | Unlock a user account |
| `reset_admin_user_password` | Reset password |
| `update_admin_user_profile` | Update profile |
| `search_admin_users` | Search users |
| `get_admin_user_groups` | Get user's groups |
| `add_admin_user_to_group` | Add user to group |
| `remove_admin_user_from_group` | Remove user from group |
| `bulk_create_admin_users` | Bulk create users |
| `get_admin_user_login_history` | Get login history |
| `get_admin_user_activity_log` | Get activity log |

### Admin: Permissions (5 tools)

| Tool | Description |
|------|-------------|
| `get_permissions` | List all permissions |
| `get_role_permissions` | Get role permissions |
| `update_role_permissions` | Update role permissions |
| `get_user_permissions` | Get user permissions |
| `update_user_permissions` | Update user permissions |

### Admin: Departments & Locations (10 tools)

| Tool | Description |
|------|-------------|
| `list_departments` | List departments |
| `get_department` | Get department details |
| `create_department` | Create department |
| `update_department` | Update department |
| `delete_department` | Delete department |
| `get_department_types` | List department types |
| `list_locations` | List locations |
| `get_location` | Get location details |
| `create_location` | Create location |
| `update_location` | Update location |
| `delete_location` | Delete location |
| `get_location_types` | List location types |

### System Settings (6 tools)

| Tool | Description |
|------|-------------|
| `get_system_settings` | Get system settings |
| `update_system_settings` | Update system settings |
| `get_email_settings` | Get email config |
| `update_email_settings` | Update email config |
| `get_notification_settings` | Get notification config |
| `update_notification_settings` | Update notification config |

### Reference Data (3 tools)

| Tool | Description |
|------|-------------|
| `get_categories` | List categories |
| `get_priorities` | List priorities |
| `get_statuses` | List statuses |

## Architecture

```
AI Client (VS Code / Cursor / Obsidian / Claude Desktop)
    |
    | MCP stdio protocol
    v
main.py                  MCP Server (141 tools)
    |
    +-- config.py         Configuration & API endpoints
    +-- sdp_client.py     SDP API client (Cloud + On-Premise)
    |
    | HTTP REST API v3
    v
ServiceDesk Plus (Cloud or On-Premise)
```

## Testing

```bash
# Quick connection test
python test_connection.py

# Full integration test
python full_test.py
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `401 Unauthorized` | Check `SDP_API_KEY` in `.env` |
| `AuthToken in the request is invalid` | On-Premise: ensure `SDP_USERNAME`/`SDP_PASSWORD` are set for session login |
| `Invalid URL` (404) | Check `SDP_BASE_URL` — no trailing slash |
| `ModuleNotFoundError: mcp` | `pip install -r requirements.txt` |
| Server doesn't start | Run `python main.py` directly to see error output |

## License

MIT

## Author

[@thichcode](https://github.com/thichcode)
