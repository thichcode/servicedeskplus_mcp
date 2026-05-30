#!/usr/bin/env python3

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server import InitializationOptions, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from sdp_client import ServiceDeskPlusClient
from config import Config

# Load environment variables
load_dotenv(override=True)

# Create MCP server
server = Server("servicedesk-plus")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List all available tools"""
    tools = [
        # ==================== TICKET MANAGEMENT ====================
        Tool(
            name="list_tickets",
            description="Lấy danh sách tickets từ ServiceDesk Plus với các bộ lọc tùy chọn",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng tickets tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái ticket",
                        "enum": ["open", "pending", "resolved", "closed", "cancelled", "on_hold"]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Lọc theo mức độ ưu tiên",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "requester": {
                        "type": "string",
                        "description": "Lọc theo người yêu cầu (email hoặc ID)"
                    }
                }
            }
        ),
        Tool(
            name="get_ticket",
            description="Lấy thông tin chi tiết của một ticket theo ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID của ticket cần lấy thông tin"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="create_ticket",
            description="Tạo ticket mới trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Tiêu đề của ticket"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết của ticket"
                    },
                    "requester": {
                        "type": "string",
                        "description": "Email hoặc ID của người yêu cầu"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Mức độ ưu tiên",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "category": {
                        "type": "string",
                        "description": "Danh mục của ticket"
                    },
                    "technician": {
                        "type": "string",
                        "description": "ID của technician được gán"
                    }
                },
                "required": ["subject", "description", "requester"]
            }
        ),
        Tool(
            name="update_ticket",
            description="Cập nhật thông tin của một ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID của ticket cần cập nhật"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Tiêu đề mới của ticket"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới của ticket"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["open", "pending", "resolved", "closed", "cancelled", "on_hold"]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Mức độ ưu tiên mới",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "technician": {
                        "type": "string",
                        "description": "ID của technician mới được gán"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="delete_ticket",
            description="Xóa một ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID của ticket cần xóa"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="search_tickets",
            description="Tìm kiếm tickets theo từ khóa",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Từ khóa tìm kiếm"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng kết quả tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_ticket_comment",
            description="Thêm comment vào một ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID của ticket"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Nội dung comment"
                    }
                },
                "required": ["ticket_id", "comment"]
            }
        ),
        Tool(
            name="get_ticket_comments",
            description="Lấy danh sách comments của một ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID của ticket"
                    }
                },
                "required": ["ticket_id"]
            }
        ),

        # ==================== ADVANCED REQUEST MANAGEMENT ====================

        Tool(
            name="assign_request",
            description="Gán request cho technician và group",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần gán"
                    },
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician"
                    },
                    "group_id": {
                        "type": "string",
                        "description": "ID của group (tùy chọn)"
                    }
                },
                "required": ["request_id", "technician_id"]
            }
        ),
        Tool(
            name="reassign_request",
            description="Gán lại request cho technician khác",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần gán lại"
                    },
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician mới"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Lý do gán lại (tùy chọn)"
                    }
                },
                "required": ["request_id", "technician_id"]
            }
        ),
        Tool(
            name="escalate_request",
            description="Escalate request lên cấp cao hơn",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần escalate"
                    },
                    "escalation_level": {
                        "type": "string",
                        "description": "Cấp độ escalate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Lý do escalate"
                    }
                },
                "required": ["request_id", "escalation_level", "reason"]
            }
        ),
        Tool(
            name="approve_request",
            description="Phê duyệt request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần phê duyệt"
                    },
                    "approval_comments": {
                        "type": "string",
                        "description": "Comments phê duyệt (tùy chọn)"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="reject_request",
            description="Từ chối request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần từ chối"
                    },
                    "rejection_reason": {
                        "type": "string",
                        "description": "Lý do từ chối"
                    },
                    "comments": {
                        "type": "string",
                        "description": "Comments bổ sung (tùy chọn)"
                    }
                },
                "required": ["request_id", "rejection_reason"]
            }
        ),
        Tool(
            name="get_request_approvals",
            description="Lấy thông tin phê duyệt của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="get_request_attachments",
            description="Lấy danh sách attachments của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="add_request_attachment",
            description="Thêm attachment vào request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Đường dẫn file cần upload"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả attachment (tùy chọn)"
                    }
                },
                "required": ["request_id", "file_path"]
            }
        ),
        Tool(
            name="delete_request_attachment",
            description="Xóa attachment khỏi request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "ID của attachment cần xóa"
                    }
                },
                "required": ["request_id", "attachment_id"]
            }
        ),
        Tool(
            name="get_request_history",
            description="Lấy lịch sử/timeline của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng bản ghi tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="get_request_sla_details",
            description="Lấy thông tin SLA của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="update_request_sla",
            description="Cập nhật SLA cho request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "sla_data": {
                        "type": "object",
                        "description": "Dữ liệu SLA cần cập nhật"
                    }
                },
                "required": ["request_id", "sla_data"]
            }
        ),
        Tool(
            name="get_request_templates",
            description="Lấy danh sách request templates có sẵn",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Lọc theo category (tùy chọn)"
                    }
                }
            }
        ),
        Tool(
            name="create_request_from_template",
            description="Tạo request từ template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "ID của template"
                    },
                    "request_data": {
                        "type": "object",
                        "description": "Dữ liệu request bổ sung"
                    }
                },
                "required": ["template_id", "request_data"]
            }
        ),
        Tool(
            name="close_request",
            description="Đóng request với closure code và resolution",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request cần đóng"
                    },
                    "closure_code": {
                        "type": "string",
                        "description": "Mã đóng request"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Mô tả giải pháp"
                    }
                },
                "required": ["request_id", "closure_code", "resolution"]
            }
        ),
        Tool(
            name="get_closure_codes",
            description="Lấy danh sách closure codes có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_request_worklog",
            description="Lấy worklog entries của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng bản ghi tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="add_worklog_entry",
            description="Thêm worklog entry vào request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả công việc"
                    },
                    "time_spent": {
                        "type": "string",
                        "description": "Thời gian đã tiêu tốn (tùy chọn)"
                    },
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician (tùy chọn)"
                    }
                },
                "required": ["request_id", "description"]
            }
        ),
        Tool(
            name="update_worklog_entry",
            description="Cập nhật worklog entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "worklog_id": {
                        "type": "string",
                        "description": "ID của worklog entry"
                    },
                    "update_data": {
                        "type": "object",
                        "description": "Dữ liệu cập nhật"
                    }
                },
                "required": ["request_id", "worklog_id", "update_data"]
            }
        ),
        Tool(
            name="get_request_custom_fields",
            description="Lấy custom fields của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="update_request_custom_fields",
            description="Cập nhật custom fields của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "custom_fields": {
                        "type": "object",
                        "description": "Custom fields cần cập nhật"
                    }
                },
                "required": ["request_id", "custom_fields"]
            }
        ),
        Tool(
            name="get_request_feedback",
            description="Lấy feedback/survey của request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="submit_request_feedback",
            description="Gửi feedback cho request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "rating": {
                        "type": "integer",
                        "description": "Đánh giá (1-5)"
                    },
                    "comments": {
                        "type": "string",
                        "description": "Comments (tùy chọn)"
                    },
                    "survey_responses": {
                        "type": "object",
                        "description": "Phản hồi khảo sát (tùy chọn)"
                    }
                },
                "required": ["request_id", "rating"]
            }
        ),
        Tool(
            name="get_request_notifications",
            description="Lấy danh sách notifications đã gửi cho request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    }
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="send_request_notification",
            description="Gửi notification cho request",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "ID của request"
                    },
                    "notification_type": {
                        "type": "string",
                        "description": "Loại notification"
                    },
                    "recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách email người nhận"
                    },
                    "custom_message": {
                        "type": "string",
                        "description": "Tin nhắn tùy chỉnh (tùy chọn)"
                    }
                },
                "required": ["request_id", "notification_type", "recipients"]
            }
        ),
        
        # ==================== USER MANAGEMENT ====================
        Tool(
            name="list_users",
            description="Lấy danh sách users từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng users tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="get_user",
            description="Lấy thông tin chi tiết của một user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần lấy thông tin"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_technicians",
            description="Lấy danh sách technicians từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng technicians tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    }
                }
            }
        ),
        
        # ==================== CMDB - CONFIGURATION ITEMS ====================
        Tool(
            name="list_configuration_items",
            description="Lấy danh sách Configuration Items (CIs) từ CMDB",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng CIs tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "ci_type": {
                        "type": "string",
                        "description": "Lọc theo loại CI (server, network_device, software, etc.)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái CI",
                        "enum": ["active", "inactive", "under_maintenance", "retired"]
                    }
                }
            }
        ),
        Tool(
            name="get_configuration_item",
            description="Lấy thông tin chi tiết của một Configuration Item",
            inputSchema={
                "type": "object",
                "properties": {
                    "ci_id": {
                        "type": "string",
                        "description": "ID của Configuration Item"
                    }
                },
                "required": ["ci_id"]
            }
        ),
        Tool(
            name="create_configuration_item",
            description="Tạo Configuration Item mới trong CMDB",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của Configuration Item"
                    },
                    "ci_type": {
                        "type": "string",
                        "description": "Loại CI (server, network_device, software, etc.)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái",
                        "enum": ["active", "inactive", "under_maintenance", "retired"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Vị trí"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Người sở hữu"
                    }
                },
                "required": ["name", "ci_type"]
            }
        ),
        Tool(
            name="update_configuration_item",
            description="Cập nhật thông tin Configuration Item",
            inputSchema={
                "type": "object",
                "properties": {
                    "ci_id": {
                        "type": "string",
                        "description": "ID của Configuration Item"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["active", "inactive", "under_maintenance", "retired"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Vị trí mới"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Người sở hữu mới"
                    }
                },
                "required": ["ci_id"]
            }
        ),
        Tool(
            name="delete_configuration_item",
            description="Xóa Configuration Item",
            inputSchema={
                "type": "object",
                "properties": {
                    "ci_id": {
                        "type": "string",
                        "description": "ID của Configuration Item cần xóa"
                    }
                },
                "required": ["ci_id"]
            }
        ),
        Tool(
            name="get_ci_types",
            description="Lấy danh sách các loại Configuration Items có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_ci_relationships",
            description="Lấy danh sách relationships của một Configuration Item",
            inputSchema={
                "type": "object",
                "properties": {
                    "ci_id": {
                        "type": "string",
                        "description": "ID của Configuration Item"
                    }
                },
                "required": ["ci_id"]
            }
        ),
        
        # ==================== ASSET MANAGEMENT ====================
        Tool(
            name="list_assets",
            description="Lấy danh sách assets từ ServiceDesk Plus với bộ lọc",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng assets tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "asset_type": {
                        "type": "string",
                        "description": "Lọc theo loại asset"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái asset",
                        "enum": ["in_use", "in_stock", "under_maintenance", "retired", "lost", "stolen"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Lọc theo vị trí"
                    }
                }
            }
        ),
        Tool(
            name="get_asset",
            description="Lấy thông tin chi tiết của một asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "string",
                        "description": "ID của asset cần lấy thông tin"
                    }
                },
                "required": ["asset_id"]
            }
        ),
        Tool(
            name="create_asset",
            description="Tạo asset mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của asset"
                    },
                    "asset_type": {
                        "type": "string",
                        "description": "Loại asset"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái",
                        "enum": ["in_use", "in_stock", "under_maintenance", "retired", "lost", "stolen"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Vị trí"
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Người được gán"
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Nhà cung cấp"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model"
                    },
                    "serial_number": {
                        "type": "string",
                        "description": "Số serial"
                    }
                },
                "required": ["name", "asset_type"]
            }
        ),
        Tool(
            name="update_asset",
            description="Cập nhật thông tin asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "string",
                        "description": "ID của asset"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["in_use", "in_stock", "under_maintenance", "retired", "lost", "stolen"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Vị trí mới"
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Người được gán mới"
                    }
                },
                "required": ["asset_id"]
            }
        ),
        Tool(
            name="delete_asset",
            description="Xóa asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "string",
                        "description": "ID của asset cần xóa"
                    }
                },
                "required": ["asset_id"]
            }
        ),
        Tool(
            name="get_asset_types",
            description="Lấy danh sách các loại assets có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_asset_categories",
            description="Lấy danh sách các danh mục assets có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_asset_locations",
            description="Lấy danh sách các vị trí assets có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_asset_models",
            description="Lấy danh sách các model assets có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_asset_vendors",
            description="Lấy danh sách các vendor assets có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== SOFTWARE LICENSE MANAGEMENT ====================
        Tool(
            name="list_software_licenses",
            description="Lấy danh sách software licenses",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng licenses tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "product": {
                        "type": "string",
                        "description": "Lọc theo sản phẩm"
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Lọc theo vendor"
                    }
                }
            }
        ),
        Tool(
            name="get_software_license",
            description="Lấy thông tin chi tiết của một software license",
            inputSchema={
                "type": "object",
                "properties": {
                    "license_id": {
                        "type": "string",
                        "description": "ID của software license"
                    }
                },
                "required": ["license_id"]
            }
        ),
        Tool(
            name="create_software_license",
            description="Tạo software license mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Tên sản phẩm"
                    },
                    "license_type": {
                        "type": "string",
                        "description": "Loại license"
                    },
                    "total_licenses": {
                        "type": "integer",
                        "description": "Tổng số licenses"
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Nhà cung cấp"
                    },
                    "purchase_date": {
                        "type": "string",
                        "description": "Ngày mua (YYYY-MM-DD)"
                    },
                    "expiry_date": {
                        "type": "string",
                        "description": "Ngày hết hạn (YYYY-MM-DD)"
                    },
                    "cost": {
                        "type": "number",
                        "description": "Chi phí"
                    }
                },
                "required": ["product", "license_type", "total_licenses"]
            }
        ),
        Tool(
            name="update_software_license",
            description="Cập nhật software license",
            inputSchema={
                "type": "object",
                "properties": {
                    "license_id": {
                        "type": "string",
                        "description": "ID của software license"
                    },
                    "product": {
                        "type": "string",
                        "description": "Tên sản phẩm mới"
                    },
                    "total_licenses": {
                        "type": "integer",
                        "description": "Tổng số licenses mới"
                    },
                    "expiry_date": {
                        "type": "string",
                        "description": "Ngày hết hạn mới (YYYY-MM-DD)"
                    }
                },
                "required": ["license_id"]
            }
        ),
        Tool(
            name="get_software_products",
            description="Lấy danh sách các software products có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_license_types",
            description="Lấy danh sách các license types có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== CONTRACT MANAGEMENT ====================
        Tool(
            name="list_contracts",
            description="Lấy danh sách contracts",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng contracts tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "contract_type": {
                        "type": "string",
                        "description": "Lọc theo loại contract"
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái contract",
                        "enum": ["active", "expired", "pending", "terminated"]
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Lọc theo vendor"
                    }
                }
            }
        ),
        Tool(
            name="get_contract",
            description="Lấy thông tin chi tiết của một contract",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_id": {
                        "type": "string",
                        "description": "ID của contract"
                    }
                },
                "required": ["contract_id"]
            }
        ),
        Tool(
            name="create_contract",
            description="Tạo contract mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên contract"
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Vendor"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Ngày bắt đầu (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Ngày kết thúc (YYYY-MM-DD)"
                    },
                    "contract_type": {
                        "type": "string",
                        "description": "Loại contract"
                    },
                    "value": {
                        "type": "number",
                        "description": "Giá trị contract"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    }
                },
                "required": ["name", "vendor", "start_date", "end_date"]
            }
        ),
        Tool(
            name="update_contract",
            description="Cập nhật contract",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_id": {
                        "type": "string",
                        "description": "ID của contract"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Ngày kết thúc mới (YYYY-MM-DD)"
                    },
                    "value": {
                        "type": "number",
                        "description": "Giá trị mới"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["active", "expired", "pending", "terminated"]
                    }
                },
                "required": ["contract_id"]
            }
        ),
        Tool(
            name="get_contract_types",
            description="Lấy danh sách các contract types có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_contract_vendors",
            description="Lấy danh sách các contract vendors có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== PURCHASE ORDER MANAGEMENT ====================
        Tool(
            name="list_purchase_orders",
            description="Lấy danh sách purchase orders",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng POs tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái PO",
                        "enum": ["draft", "pending_approval", "approved", "ordered", "received", "cancelled"]
                    },
                    "vendor": {
                        "type": "string",
                        "description": "Lọc theo vendor"
                    }
                }
            }
        ),
        Tool(
            name="get_purchase_order",
            description="Lấy thông tin chi tiết của một purchase order",
            inputSchema={
                "type": "object",
                "properties": {
                    "po_id": {
                        "type": "string",
                        "description": "ID của purchase order"
                    }
                },
                "required": ["po_id"]
            }
        ),
        Tool(
            name="create_purchase_order",
            description="Tạo purchase order mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor": {
                        "type": "string",
                        "description": "Vendor"
                    },
                    "items": {
                        "type": "array",
                        "description": "Danh sách items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "unit_price": {"type": "number"}
                            }
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả"
                    },
                    "expected_delivery": {
                        "type": "string",
                        "description": "Ngày giao hàng dự kiến (YYYY-MM-DD)"
                    }
                },
                "required": ["vendor", "items"]
            }
        ),
        Tool(
            name="update_purchase_order",
            description="Cập nhật purchase order",
            inputSchema={
                "type": "object",
                "properties": {
                    "po_id": {
                        "type": "string",
                        "description": "ID của purchase order"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["draft", "pending_approval", "approved", "ordered", "received", "cancelled"]
                    },
                    "expected_delivery": {
                        "type": "string",
                        "description": "Ngày giao hàng dự kiến mới (YYYY-MM-DD)"
                    }
                },
                "required": ["po_id"]
            }
        ),
        Tool(
            name="get_po_statuses",
            description="Lấy danh sách các PO statuses có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== VENDOR MANAGEMENT ====================
        Tool(
            name="list_vendors",
            description="Lấy danh sách vendors",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng vendors tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "vendor_type": {
                        "type": "string",
                        "description": "Lọc theo loại vendor"
                    }
                }
            }
        ),
        Tool(
            name="get_vendor",
            description="Lấy thông tin chi tiết của một vendor",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "ID của vendor"
                    }
                },
                "required": ["vendor_id"]
            }
        ),
        Tool(
            name="create_vendor",
            description="Tạo vendor mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên vendor"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại"
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ"
                    },
                    "vendor_type": {
                        "type": "string",
                        "description": "Loại vendor"
                    },
                    "website": {
                        "type": "string",
                        "description": "Website"
                    }
                },
                "required": ["name", "email"]
            }
        ),
        Tool(
            name="update_vendor",
            description="Cập nhật vendor",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "ID của vendor"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email mới"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại mới"
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ mới"
                    }
                },
                "required": ["vendor_id"]
            }
        ),
        Tool(
            name="get_vendor_types",
            description="Lấy danh sách các vendor types có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - SITES ====================
        Tool(
            name="list_sites",
            description="Lấy danh sách sites từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng sites tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "site_type": {
                        "type": "string",
                        "description": "Lọc theo loại site",
                        "enum": ["headquarters", "branch_office", "data_center", "warehouse", "retail_store", "manufacturing_plant"]
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái site"
                    }
                }
            }
        ),
        Tool(
            name="get_site",
            description="Lấy thông tin chi tiết của một site",
            inputSchema={
                "type": "object",
                "properties": {
                    "site_id": {
                        "type": "string",
                        "description": "ID của site cần lấy thông tin"
                    }
                },
                "required": ["site_id"]
            }
        ),
        Tool(
            name="create_site",
            description="Tạo site mới trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của site"
                    },
                    "site_type": {
                        "type": "string",
                        "description": "Loại site",
                        "enum": ["headquarters", "branch_office", "data_center", "warehouse", "retail_store", "manufacturing_plant"]
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ của site"
                    },
                    "city": {
                        "type": "string",
                        "description": "Thành phố"
                    },
                    "state": {
                        "type": "string",
                        "description": "Tỉnh/Bang"
                    },
                    "country": {
                        "type": "string",
                        "description": "Quốc gia"
                    },
                    "zip_code": {
                        "type": "string",
                        "description": "Mã bưu điện"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email liên hệ"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    }
                },
                "required": ["name", "site_type"]
            }
        ),
        Tool(
            name="update_site",
            description="Cập nhật thông tin của một site",
            inputSchema={
                "type": "object",
                "properties": {
                    "site_id": {
                        "type": "string",
                        "description": "ID của site cần cập nhật"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới của site"
                    },
                    "site_type": {
                        "type": "string",
                        "description": "Loại site mới",
                        "enum": ["headquarters", "branch_office", "data_center", "warehouse", "retail_store", "manufacturing_plant"]
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ mới"
                    },
                    "city": {
                        "type": "string",
                        "description": "Thành phố mới"
                    },
                    "state": {
                        "type": "string",
                        "description": "Tỉnh/Bang mới"
                    },
                    "country": {
                        "type": "string",
                        "description": "Quốc gia mới"
                    },
                    "zip_code": {
                        "type": "string",
                        "description": "Mã bưu điện mới"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại mới"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email liên hệ mới"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    }
                },
                "required": ["site_id"]
            }
        ),
        Tool(
            name="delete_site",
            description="Xóa một site",
            inputSchema={
                "type": "object",
                "properties": {
                    "site_id": {
                        "type": "string",
                        "description": "ID của site cần xóa"
                    }
                },
                "required": ["site_id"]
            }
        ),
        Tool(
            name="get_site_types",
            description="Lấy danh sách các loại site có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - USER GROUPS ====================
        Tool(
            name="list_user_groups",
            description="Lấy danh sách user groups từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng user groups tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "group_type": {
                        "type": "string",
                        "description": "Lọc theo loại group",
                        "enum": ["department", "project", "location_based", "role_based", "custom"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "Lọc theo site ID"
                    }
                }
            }
        ),
        Tool(
            name="get_user_group",
            description="Lấy thông tin chi tiết của một user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "ID của user group cần lấy thông tin"
                    }
                },
                "required": ["group_id"]
            }
        ),
        Tool(
            name="create_user_group",
            description="Tạo user group mới trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của user group"
                    },
                    "group_type": {
                        "type": "string",
                        "description": "Loại group",
                        "enum": ["department", "project", "location_based", "role_based", "custom"]
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan"
                    },
                    "manager": {
                        "type": "string",
                        "description": "ID của manager"
                    }
                },
                "required": ["name", "group_type"]
            }
        ),
        Tool(
            name="update_user_group",
            description="Cập nhật thông tin của một user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "ID của user group cần cập nhật"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới của user group"
                    },
                    "group_type": {
                        "type": "string",
                        "description": "Loại group mới",
                        "enum": ["department", "project", "location_based", "role_based", "custom"]
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan mới"
                    },
                    "manager": {
                        "type": "string",
                        "description": "ID của manager mới"
                    }
                },
                "required": ["group_id"]
            }
        ),
        Tool(
            name="delete_user_group",
            description="Xóa một user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "ID của user group cần xóa"
                    }
                },
                "required": ["group_id"]
            }
        ),
        Tool(
            name="get_group_types",
            description="Lấy danh sách các loại user group có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_group_permissions",
            description="Lấy danh sách permissions của một user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "ID của user group"
                    }
                },
                "required": ["group_id"]
            }
        ),
        Tool(
            name="update_group_permissions",
            description="Cập nhật permissions cho một user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string",
                        "description": "ID của user group"
                    },
                    "permissions": {
                        "type": "object",
                        "description": "Object chứa các permissions với level tương ứng",
                        "additionalProperties": {
                            "type": "string",
                            "enum": ["none", "read", "write", "admin"]
                        }
                    }
                },
                "required": ["group_id", "permissions"]
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - USERS & TECHNICIANS ====================
        Tool(
            name="list_admin_users",
            description="Lấy danh sách users (admin) từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng users tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái user",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    },
                    "role": {
                        "type": "string",
                        "description": "Lọc theo role",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "Lọc theo site ID"
                    }
                }
            }
        ),
        Tool(
            name="get_admin_user",
            description="Lấy thông tin chi tiết của một user (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần lấy thông tin"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="create_admin_user",
            description="Tạo user mới (admin) trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Tên đăng nhập"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email của user"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "Tên"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Họ"
                    },
                    "password": {
                        "type": "string",
                        "description": "Mật khẩu"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role của user",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site"
                    },
                    "department": {
                        "type": "string",
                        "description": "Phòng ban"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    }
                },
                "required": ["username", "email", "first_name", "last_name"]
            }
        ),
        Tool(
            name="update_admin_user",
            description="Cập nhật thông tin của một user (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần cập nhật"
                    },
                    "username": {
                        "type": "string",
                        "description": "Tên đăng nhập mới"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email mới"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Họ mới"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role mới",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site mới"
                    },
                    "department": {
                        "type": "string",
                        "description": "Phòng ban mới"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại mới"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="delete_admin_user",
            description="Xóa một user (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần xóa"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_admin_technicians",
            description="Lấy danh sách technicians (admin) từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng technicians tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "status": {
                        "type": "string",
                        "description": "Lọc theo trạng thái technician",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    },
                    "role": {
                        "type": "string",
                        "description": "Lọc theo role",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "Lọc theo site ID"
                    }
                }
            }
        ),
        Tool(
            name="get_admin_technician",
            description="Lấy thông tin chi tiết của một technician (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician cần lấy thông tin"
                    }
                },
                "required": ["technician_id"]
            }
        ),
        Tool(
            name="create_admin_technician",
            description="Tạo technician mới (admin) trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Tên đăng nhập"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email của technician"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "Tên"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Họ"
                    },
                    "password": {
                        "type": "string",
                        "description": "Mật khẩu"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role của technician",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site"
                    },
                    "department": {
                        "type": "string",
                        "description": "Phòng ban"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách kỹ năng"
                    },
                    "specializations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách chuyên môn"
                    }
                },
                "required": ["username", "email", "first_name", "last_name"]
            }
        ),
        Tool(
            name="update_admin_technician",
            description="Cập nhật thông tin của một technician (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician cần cập nhật"
                    },
                    "username": {
                        "type": "string",
                        "description": "Tên đăng nhập mới"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email mới"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "Tên mới"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Họ mới"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role mới",
                        "enum": ["admin", "manager", "technician", "user", "viewer"]
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site mới"
                    },
                    "department": {
                        "type": "string",
                        "description": "Phòng ban mới"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Số điện thoại mới"
                    },
                    "status": {
                        "type": "string",
                        "description": "Trạng thái mới",
                        "enum": ["active", "inactive", "locked", "pending_activation"]
                    },
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách kỹ năng mới"
                    },
                    "specializations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách chuyên môn mới"
                    }
                },
                "required": ["technician_id"]
            }
        ),
        Tool(
            name="delete_admin_technician",
            description="Xóa một technician (admin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "technician_id": {
                        "type": "string",
                        "description": "ID của technician cần xóa"
                    }
                },
                "required": ["technician_id"]
            }
        ),
        Tool(
            name="get_user_roles",
            description="Lấy danh sách các user roles có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_technician_roles",
            description="Lấy danh sách các technician roles có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="convert_user_to_technician",
            description="Chuyển đổi user thành technician trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần chuyển đổi thành technician"
                    },
                    "technician_data": {
                        "type": "object",
                        "description": "Dữ liệu bổ sung cho technician (tùy chọn)",
                        "additionalProperties": True
                    },
                    "delete_user_after_conversion": {
                        "type": "boolean",
                        "description": "Có xóa user sau khi chuyển đổi thành technician hay không",
                        "default": False
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="activate_admin_user",
            description="Kích hoạt tài khoản user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần kích hoạt"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="deactivate_admin_user",
            description="Vô hiệu hóa tài khoản user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần vô hiệu hóa"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="lock_admin_user",
            description="Khóa tài khoản user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần khóa"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="unlock_admin_user",
            description="Mở khóa tài khoản user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần mở khóa"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="reset_admin_user_password",
            description="Reset mật khẩu của user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần reset mật khẩu"
                    },
                    "new_password": {
                        "type": "string",
                        "description": "Mật khẩu mới"
                    }
                },
                "required": ["user_id", "new_password"]
            }
        ),
        Tool(
            name="update_admin_user_profile",
            description="Cập nhật thông tin profile của user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user cần cập nhật"
                    },
                    "profile_data": {
                        "type": "object",
                        "description": "Dữ liệu profile cần cập nhật",
                        "properties": {
                            "first_name": {"type": "string", "description": "Tên"},
                            "last_name": {"type": "string", "description": "Họ"},
                            "email": {"type": "string", "description": "Email"},
                            "phone": {"type": "string", "description": "Số điện thoại"},
                            "department": {"type": "string", "description": "Phòng ban"},
                            "job_title": {"type": "string", "description": "Chức vụ"},
                            "employee_id": {"type": "string", "description": "Mã nhân viên"},
                            "location": {"type": "string", "description": "Vị trí"},
                            "manager": {"type": "string", "description": "Quản lý"},
                            "cost_center": {"type": "string", "description": "Trung tâm chi phí"}
                        }
                    }
                },
                "required": ["user_id", "profile_data"]
            }
        ),
        Tool(
            name="search_admin_users",
            description="Tìm kiếm users theo từ khóa",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Từ khóa tìm kiếm"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng kết quả tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "search_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Các trường cần tìm kiếm (tùy chọn)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_admin_user_groups",
            description="Lấy danh sách groups mà user thuộc về",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="add_admin_user_to_group",
            description="Thêm user vào group",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    },
                    "group_id": {
                        "type": "string",
                        "description": "ID của group"
                    }
                },
                "required": ["user_id", "group_id"]
            }
        ),
        Tool(
            name="remove_admin_user_from_group",
            description="Xóa user khỏi group",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    },
                    "group_id": {
                        "type": "string",
                        "description": "ID của group"
                    }
                },
                "required": ["user_id", "group_id"]
            }
        ),
        Tool(
            name="bulk_create_admin_users",
            description="Tạo nhiều users cùng lúc",
            inputSchema={
                "type": "object",
                "properties": {
                    "users_data": {
                        "type": "array",
                        "description": "Danh sách dữ liệu users cần tạo",
                        "items": {
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "description": "Tên đăng nhập"},
                                "email": {"type": "string", "description": "Email"},
                                "first_name": {"type": "string", "description": "Tên"},
                                "last_name": {"type": "string", "description": "Họ"},
                                "password": {"type": "string", "description": "Mật khẩu"},
                                "role": {"type": "string", "description": "Vai trò"},
                                "department": {"type": "string", "description": "Phòng ban"},
                                "phone": {"type": "string", "description": "Số điện thoại"}
                            },
                            "required": ["username", "email", "first_name", "last_name"]
                        },
                        "minItems": 1,
                        "maxItems": 100
                    }
                },
                "required": ["users_data"]
            }
        ),
        Tool(
            name="get_admin_user_login_history",
            description="Lấy lịch sử đăng nhập của user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng bản ghi tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Ngày bắt đầu (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Ngày kết thúc (YYYY-MM-DD)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="get_admin_user_activity_log",
            description="Lấy nhật ký hoạt động của user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng bản ghi tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "activity_type": {
                        "type": "string",
                        "description": "Loại hoạt động cần lọc"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Ngày bắt đầu (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Ngày kết thúc (YYYY-MM-DD)"
                    }
                },
                "required": ["user_id"]
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - PERMISSIONS ====================
        Tool(
            name="get_permissions",
            description="Lấy danh sách tất cả permissions có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_role_permissions",
            description="Lấy danh sách permissions của một role",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_id": {
                        "type": "string",
                        "description": "ID của role"
                    }
                },
                "required": ["role_id"]
            }
        ),
        Tool(
            name="update_role_permissions",
            description="Cập nhật permissions cho một role",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_id": {
                        "type": "string",
                        "description": "ID của role"
                    },
                    "permissions": {
                        "type": "object",
                        "description": "Object chứa các permissions với level tương ứng",
                        "additionalProperties": {
                            "type": "string",
                            "enum": ["none", "read", "write", "admin"]
                        }
                    }
                },
                "required": ["role_id", "permissions"]
            }
        ),
        Tool(
            name="get_user_permissions",
            description="Lấy danh sách permissions của một user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="update_user_permissions",
            description="Cập nhật permissions cho một user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID của user"
                    },
                    "permissions": {
                        "type": "object",
                        "description": "Object chứa các permissions với level tương ứng",
                        "additionalProperties": {
                            "type": "string",
                            "enum": ["none", "read", "write", "admin"]
                        }
                    }
                },
                "required": ["user_id", "permissions"]
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - DEPARTMENTS ====================
        Tool(
            name="list_departments",
            description="Lấy danh sách departments từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng departments tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "department_type": {
                        "type": "string",
                        "description": "Lọc theo loại department"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "Lọc theo site ID"
                    }
                }
            }
        ),
        Tool(
            name="get_department",
            description="Lấy thông tin chi tiết của một department",
            inputSchema={
                "type": "object",
                "properties": {
                    "department_id": {
                        "type": "string",
                        "description": "ID của department cần lấy thông tin"
                    }
                },
                "required": ["department_id"]
            }
        ),
        Tool(
            name="create_department",
            description="Tạo department mới trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của department"
                    },
                    "department_type": {
                        "type": "string",
                        "description": "Loại department"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan"
                    },
                    "manager": {
                        "type": "string",
                        "description": "ID của manager"
                    }
                },
                "required": ["name", "department_type"]
            }
        ),
        Tool(
            name="update_department",
            description="Cập nhật thông tin của một department",
            inputSchema={
                "type": "object",
                "properties": {
                    "department_id": {
                        "type": "string",
                        "description": "ID của department cần cập nhật"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới của department"
                    },
                    "department_type": {
                        "type": "string",
                        "description": "Loại department mới"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan mới"
                    },
                    "manager": {
                        "type": "string",
                        "description": "ID của manager mới"
                    }
                },
                "required": ["department_id"]
            }
        ),
        Tool(
            name="delete_department",
            description="Xóa một department",
            inputSchema={
                "type": "object",
                "properties": {
                    "department_id": {
                        "type": "string",
                        "description": "ID của department cần xóa"
                    }
                },
                "required": ["department_id"]
            }
        ),
        Tool(
            name="get_department_types",
            description="Lấy danh sách các loại department có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - LOCATIONS ====================
        Tool(
            name="list_locations",
            description="Lấy danh sách locations từ ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng locations tối đa (mặc định: 50, tối đa: 1000)",
                        "default": 50
                    },
                    "location_type": {
                        "type": "string",
                        "description": "Lọc theo loại location"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "Lọc theo site ID"
                    }
                }
            }
        ),
        Tool(
            name="get_location",
            description="Lấy thông tin chi tiết của một location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "ID của location cần lấy thông tin"
                    }
                },
                "required": ["location_id"]
            }
        ),
        Tool(
            name="create_location",
            description="Tạo location mới trong ServiceDesk Plus",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của location"
                    },
                    "location_type": {
                        "type": "string",
                        "description": "Loại location"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả chi tiết"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan"
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ"
                    },
                    "floor": {
                        "type": "string",
                        "description": "Tầng"
                    },
                    "room": {
                        "type": "string",
                        "description": "Phòng"
                    }
                },
                "required": ["name", "location_type"]
            }
        ),
        Tool(
            name="update_location",
            description="Cập nhật thông tin của một location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "ID của location cần cập nhật"
                    },
                    "name": {
                        "type": "string",
                        "description": "Tên mới của location"
                    },
                    "location_type": {
                        "type": "string",
                        "description": "Loại location mới"
                    },
                    "description": {
                        "type": "string",
                        "description": "Mô tả mới"
                    },
                    "site_id": {
                        "type": "string",
                        "description": "ID của site liên quan mới"
                    },
                    "address": {
                        "type": "string",
                        "description": "Địa chỉ mới"
                    },
                    "floor": {
                        "type": "string",
                        "description": "Tầng mới"
                    },
                    "room": {
                        "type": "string",
                        "description": "Phòng mới"
                    }
                },
                "required": ["location_id"]
            }
        ),
        Tool(
            name="delete_location",
            description="Xóa một location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "ID của location cần xóa"
                    }
                },
                "required": ["location_id"]
            }
        ),
        Tool(
            name="get_location_types",
            description="Lấy danh sách các loại location có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # ==================== ADMIN MANAGEMENT - SYSTEM SETTINGS ====================
        Tool(
            name="get_system_settings",
            description="Lấy cài đặt hệ thống",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_system_settings",
            description="Cập nhật cài đặt hệ thống",
            inputSchema={
                "type": "object",
                "properties": {
                    "settings": {
                        "type": "object",
                        "description": "Object chứa các cài đặt hệ thống cần cập nhật"
                    }
                },
                "required": ["settings"]
            }
        ),
        Tool(
            name="get_email_settings",
            description="Lấy cài đặt email",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_email_settings",
            description="Cập nhật cài đặt email",
            inputSchema={
                "type": "object",
                "properties": {
                    "settings": {
                        "type": "object",
                        "description": "Object chứa các cài đặt email cần cập nhật"
                    }
                },
                "required": ["settings"]
            }
        ),
        Tool(
            name="get_notification_settings",
            description="Lấy cài đặt thông báo",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_notification_settings",
            description="Cập nhật cài đặt thông báo",
            inputSchema={
                "type": "object",
                "properties": {
                    "settings": {
                        "type": "object",
                        "description": "Object chứa các cài đặt thông báo cần cập nhật"
                    }
                },
                "required": ["settings"]
            }
        ),
        
        # ==================== REFERENCE DATA ====================
        Tool(
            name="get_categories",
            description="Lấy danh sách các danh mục ticket có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_priorities",
            description="Lấy danh sách các mức độ ưu tiên có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_statuses",
            description="Lấy danh sách các trạng thái ticket có sẵn",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    try:
        async with ServiceDeskPlusClient() as client:
            # ==================== TICKET MANAGEMENT ====================
            if name == "list_tickets":
                limit = arguments.get("limit", 50)
                status = arguments.get("status")
                priority = arguments.get("priority")
                requester = arguments.get("requester")
                result = await client.get_tickets(
                    limit=limit, 
                    status=status, 
                    priority=priority, 
                    requester=requester
                )
                
            elif name == "get_ticket":
                ticket_id = arguments["ticket_id"]
                result = await client.get_ticket(ticket_id)
                
            elif name == "create_ticket":
                result = await client.create_ticket(arguments)
                
            elif name == "update_ticket":
                ticket_id = arguments.pop("ticket_id")
                result = await client.update_ticket(ticket_id, arguments)
                
            elif name == "delete_ticket":
                ticket_id = arguments["ticket_id"]
                result = await client.delete_ticket(ticket_id)
                
            elif name == "search_tickets":
                query = arguments["query"]
                limit = arguments.get("limit", 50)
                result = await client.search_tickets(query, limit=limit)
                
            elif name == "add_ticket_comment":
                ticket_id = arguments["ticket_id"]
                comment = arguments["comment"]
                result = await client.add_ticket_comment(ticket_id, comment)
                
            elif name == "get_ticket_comments":
                ticket_id = arguments["ticket_id"]
                result = await client.get_ticket_comments(ticket_id)

            # ==================== ADVANCED REQUEST MANAGEMENT ====================

            elif name == "assign_request":
                request_id = arguments["request_id"]
                technician_id = arguments["technician_id"]
                group_id = arguments.get("group_id")
                result = await client.assign_request(request_id, technician_id, group_id)

            elif name == "reassign_request":
                request_id = arguments["request_id"]
                technician_id = arguments["technician_id"]
                reason = arguments.get("reason")
                result = await client.reassign_request(request_id, technician_id, reason)

            elif name == "escalate_request":
                request_id = arguments["request_id"]
                escalation_level = arguments["escalation_level"]
                reason = arguments["reason"]
                result = await client.escalate_request(request_id, escalation_level, reason)

            elif name == "approve_request":
                request_id = arguments["request_id"]
                approval_comments = arguments.get("approval_comments")
                result = await client.approve_request(request_id, approval_comments)

            elif name == "reject_request":
                request_id = arguments["request_id"]
                rejection_reason = arguments["rejection_reason"]
                comments = arguments.get("comments")
                result = await client.reject_request(request_id, rejection_reason, comments)

            elif name == "get_request_approvals":
                request_id = arguments["request_id"]
                result = await client.get_request_approvals(request_id)

            elif name == "get_request_attachments":
                request_id = arguments["request_id"]
                result = await client.get_request_attachments(request_id)

            elif name == "add_request_attachment":
                request_id = arguments["request_id"]
                file_path = arguments["file_path"]
                description = arguments.get("description")
                result = await client.add_request_attachment(request_id, file_path, description)

            elif name == "delete_request_attachment":
                request_id = arguments["request_id"]
                attachment_id = arguments["attachment_id"]
                result = await client.delete_request_attachment(request_id, attachment_id)

            elif name == "get_request_history":
                request_id = arguments["request_id"]
                limit = arguments.get("limit", 50)
                result = await client.get_request_history(request_id, limit)

            elif name == "get_request_sla_details":
                request_id = arguments["request_id"]
                result = await client.get_request_sla_details(request_id)

            elif name == "update_request_sla":
                request_id = arguments["request_id"]
                sla_data = arguments["sla_data"]
                result = await client.update_request_sla(request_id, sla_data)

            elif name == "get_request_templates":
                category = arguments.get("category")
                result = await client.get_request_templates(category)

            elif name == "create_request_from_template":
                template_id = arguments["template_id"]
                request_data = arguments["request_data"]
                result = await client.create_request_from_template(template_id, request_data)

            elif name == "close_request":
                request_id = arguments["request_id"]
                closure_code = arguments["closure_code"]
                resolution = arguments["resolution"]
                result = await client.close_request(request_id, closure_code, resolution)

            elif name == "get_closure_codes":
                result = await client.get_closure_codes()

            elif name == "get_request_worklog":
                request_id = arguments["request_id"]
                limit = arguments.get("limit", 50)
                result = await client.get_request_worklog(request_id, limit)

            elif name == "add_worklog_entry":
                request_id = arguments["request_id"]
                description = arguments["description"]
                time_spent = arguments.get("time_spent")
                technician_id = arguments.get("technician_id")
                result = await client.add_worklog_entry(request_id, description, time_spent, technician_id)

            elif name == "update_worklog_entry":
                request_id = arguments["request_id"]
                worklog_id = arguments["worklog_id"]
                update_data = arguments["update_data"]
                result = await client.update_worklog_entry(request_id, worklog_id, update_data)

            elif name == "get_request_custom_fields":
                request_id = arguments["request_id"]
                result = await client.get_request_custom_fields(request_id)

            elif name == "update_request_custom_fields":
                request_id = arguments["request_id"]
                custom_fields = arguments["custom_fields"]
                result = await client.update_request_custom_fields(request_id, custom_fields)

            elif name == "get_request_feedback":
                request_id = arguments["request_id"]
                result = await client.get_request_feedback(request_id)

            elif name == "submit_request_feedback":
                request_id = arguments["request_id"]
                rating = arguments["rating"]
                comments = arguments.get("comments")
                survey_responses = arguments.get("survey_responses")
                result = await client.submit_request_feedback(request_id, rating, comments, survey_responses)

            elif name == "get_request_notifications":
                request_id = arguments["request_id"]
                result = await client.get_request_notifications(request_id)

            elif name == "send_request_notification":
                request_id = arguments["request_id"]
                notification_type = arguments["notification_type"]
                recipients = arguments["recipients"]
                custom_message = arguments.get("custom_message")
                result = await client.send_request_notification(request_id, notification_type, recipients, custom_message)

            # ==================== REFERENCE DATA ====================

            elif name == "get_categories":
                result = await client.get_categories()

            elif name == "get_priorities":
                result = await client.get_priorities()

            elif name == "get_statuses":
                result = await client.get_statuses()

            # ==================== USER MANAGEMENT ====================
            elif name == "list_users":
                limit = arguments.get("limit", 50)
                result = await client.get_users(limit=limit)
                
            elif name == "get_user":
                user_id = arguments["user_id"]
                result = await client.get_user(user_id)
                
            elif name == "list_technicians":
                limit = arguments.get("limit", 50)
                result = await client.get_technicians(limit=limit)
                
            # ==================== CMDB - CONFIGURATION ITEMS ====================
            elif name == "list_configuration_items":
                limit = arguments.get("limit", 50)
                ci_type = arguments.get("ci_type")
                status = arguments.get("status")
                result = await client.get_configuration_items(
                    limit=limit, 
                    ci_type=ci_type, 
                    status=status
                )
                
            elif name == "get_configuration_item":
                ci_id = arguments["ci_id"]
                result = await client.get_configuration_item(ci_id)
                
            elif name == "create_configuration_item":
                result = await client.create_configuration_item(arguments)
                
            elif name == "update_configuration_item":
                ci_id = arguments.pop("ci_id")
                result = await client.update_configuration_item(ci_id, arguments)
                
            elif name == "delete_configuration_item":
                ci_id = arguments["ci_id"]
                result = await client.delete_configuration_item(ci_id)
                
            elif name == "get_ci_types":
                result = await client.get_ci_types()
                
            elif name == "get_ci_relationships":
                ci_id = arguments["ci_id"]
                result = await client.get_ci_relationships(ci_id)
                
            # ==================== ASSET MANAGEMENT ====================
            elif name == "list_assets":
                limit = arguments.get("limit", 50)
                asset_type = arguments.get("asset_type")
                status = arguments.get("status")
                location = arguments.get("location")
                result = await client.get_assets(
                    limit=limit, 
                    asset_type=asset_type, 
                    status=status, 
                    location=location
                )
                
            elif name == "get_asset":
                asset_id = arguments["asset_id"]
                result = await client.get_asset(asset_id)
                
            elif name == "create_asset":
                result = await client.create_asset(arguments)
                
            elif name == "update_asset":
                asset_id = arguments.pop("asset_id")
                result = await client.update_asset(asset_id, arguments)
                
            elif name == "delete_asset":
                asset_id = arguments["asset_id"]
                result = await client.delete_asset(asset_id)
                
            elif name == "get_asset_types":
                result = await client.get_asset_types()
                
            elif name == "get_asset_categories":
                result = await client.get_asset_categories()
                
            elif name == "get_asset_locations":
                result = await client.get_asset_locations()
                
            elif name == "get_asset_models":
                result = await client.get_asset_models()
                
            elif name == "get_asset_vendors":
                result = await client.get_asset_vendors()
                
            # ==================== SOFTWARE LICENSE MANAGEMENT ====================
            elif name == "list_software_licenses":
                limit = arguments.get("limit", 50)
                product = arguments.get("product")
                vendor = arguments.get("vendor")
                result = await client.get_software_licenses(
                    limit=limit, 
                    product=product, 
                    vendor=vendor
                )
                
            elif name == "get_software_license":
                license_id = arguments["license_id"]
                result = await client.get_software_license(license_id)
                
            elif name == "create_software_license":
                result = await client.create_software_license(arguments)
                
            elif name == "update_software_license":
                license_id = arguments.pop("license_id")
                result = await client.update_software_license(license_id, arguments)
                
            elif name == "get_software_products":
                result = await client.get_software_products()
                
            elif name == "get_license_types":
                result = await client.get_license_types()
                
            # ==================== CONTRACT MANAGEMENT ====================
            elif name == "list_contracts":
                limit = arguments.get("limit", 50)
                contract_type = arguments.get("contract_type")
                status = arguments.get("status")
                vendor = arguments.get("vendor")
                result = await client.get_contracts(
                    limit=limit, 
                    contract_type=contract_type, 
                    status=status, 
                    vendor=vendor
                )
                
            elif name == "get_contract":
                contract_id = arguments["contract_id"]
                result = await client.get_contract(contract_id)
                
            elif name == "create_contract":
                result = await client.create_contract(arguments)
                
            elif name == "update_contract":
                contract_id = arguments.pop("contract_id")
                result = await client.update_contract(contract_id, arguments)
                
            elif name == "get_contract_types":
                result = await client.get_contract_types()
                
            elif name == "get_contract_vendors":
                result = await client.get_contract_vendors()
                
            # ==================== PURCHASE ORDER MANAGEMENT ====================
            elif name == "list_purchase_orders":
                limit = arguments.get("limit", 50)
                status = arguments.get("status")
                vendor = arguments.get("vendor")
                result = await client.get_purchase_orders(
                    limit=limit, 
                    status=status, 
                    vendor=vendor
                )
                
            elif name == "get_purchase_order":
                po_id = arguments["po_id"]
                result = await client.get_purchase_order(po_id)
                
            elif name == "create_purchase_order":
                result = await client.create_purchase_order(arguments)
                
            elif name == "update_purchase_order":
                po_id = arguments.pop("po_id")
                result = await client.update_purchase_order(po_id, arguments)
                
            elif name == "get_po_statuses":
                result = await client.get_po_statuses()
                
            # ==================== VENDOR MANAGEMENT ====================
            elif name == "list_vendors":
                limit = arguments.get("limit", 50)
                vendor_type = arguments.get("vendor_type")
                result = await client.get_vendors(limit=limit, vendor_type=vendor_type)
                
            elif name == "get_vendor":
                vendor_id = arguments["vendor_id"]
                result = await client.get_vendor(vendor_id)
                
            elif name == "create_vendor":
                result = await client.create_vendor(arguments)
                
            elif name == "update_vendor":
                vendor_id = arguments.pop("vendor_id")
                result = await client.update_vendor(vendor_id, arguments)
                
            elif name == "get_vendor_types":
                result = await client.get_vendor_types()
                
            # ==================== ADMIN MANAGEMENT - SITES ====================
            elif name == "list_sites":
                limit = arguments.get("limit", 50)
                site_type = arguments.get("site_type")
                status = arguments.get("status")
                result = await client.get_sites(
                    limit=limit, 
                    site_type=site_type, 
                    status=status
                )
                
            elif name == "get_site":
                site_id = arguments["site_id"]
                result = await client.get_site(site_id)
                
            elif name == "create_site":
                result = await client.create_site(arguments)
                
            elif name == "update_site":
                site_id = arguments.pop("site_id")
                result = await client.update_site(site_id, arguments)
                
            elif name == "delete_site":
                site_id = arguments["site_id"]
                result = await client.delete_site(site_id)
                
            elif name == "get_site_types":
                result = await client.get_site_types()
                
            # ==================== ADMIN MANAGEMENT - USER GROUPS ====================
            elif name == "list_user_groups":
                limit = arguments.get("limit", 50)
                group_type = arguments.get("group_type")
                site_id = arguments.get("site_id")
                result = await client.get_user_groups(
                    limit=limit, 
                    group_type=group_type, 
                    site_id=site_id
                )
                
            elif name == "get_user_group":
                group_id = arguments["group_id"]
                result = await client.get_user_group(group_id)
                
            elif name == "create_user_group":
                result = await client.create_user_group(arguments)
                
            elif name == "update_user_group":
                group_id = arguments.pop("group_id")
                result = await client.update_user_group(group_id, arguments)
                
            elif name == "delete_user_group":
                group_id = arguments["group_id"]
                result = await client.delete_user_group(group_id)
                
            elif name == "get_group_types":
                result = await client.get_group_types()
                
            elif name == "get_group_permissions":
                group_id = arguments["group_id"]
                result = await client.get_group_permissions(group_id)
                
            elif name == "update_group_permissions":
                group_id = arguments.pop("group_id")
                result = await client.update_group_permissions(group_id, arguments)
                
            # ==================== ADMIN MANAGEMENT - USERS & TECHNICIANS ====================
            elif name == "list_admin_users":
                limit = arguments.get("limit", 50)
                status = arguments.get("status")
                role = arguments.get("role")
                site_id = arguments.get("site_id")
                result = await client.get_admin_users(
                    limit=limit, 
                    status=status, 
                    role=role, 
                    site_id=site_id
                )
                
            elif name == "get_admin_user":
                user_id = arguments["user_id"]
                result = await client.get_admin_user(user_id)
                
            elif name == "create_admin_user":
                result = await client.create_admin_user(arguments)
                
            elif name == "update_admin_user":
                user_id = arguments.pop("user_id")
                result = await client.update_admin_user(user_id, arguments)
                
            elif name == "delete_admin_user":
                user_id = arguments["user_id"]
                result = await client.delete_admin_user(user_id)
                
            elif name == "list_admin_technicians":
                limit = arguments.get("limit", 50)
                status = arguments.get("status")
                role = arguments.get("role")
                site_id = arguments.get("site_id")
                result = await client.get_admin_technicians(
                    limit=limit, 
                    status=status, 
                    role=role, 
                    site_id=site_id
                )
                
            elif name == "get_admin_technician":
                technician_id = arguments["technician_id"]
                result = await client.get_admin_technician(technician_id)
                
            elif name == "create_admin_technician":
                result = await client.create_admin_technician(arguments)
                
            elif name == "update_admin_technician":
                technician_id = arguments.pop("technician_id")
                result = await client.update_admin_technician(technician_id, arguments)
                
            elif name == "delete_admin_technician":
                technician_id = arguments["technician_id"]
                result = await client.delete_admin_technician(technician_id)
                
            elif name == "get_user_roles":
                result = await client.get_user_roles()
                
            elif name == "get_technician_roles":
                result = await client.get_technician_roles()

            elif name == "convert_user_to_technician":
                user_id = arguments["user_id"]
                technician_data = arguments.get("technician_data")
                delete_user_after_conversion = arguments.get("delete_user_after_conversion", False)
                result = await client.convert_user_to_technician(
                    user_id=user_id,
                    technician_data=technician_data,
                    delete_user_after_conversion=delete_user_after_conversion
                )

            elif name == "activate_admin_user":
                user_id = arguments["user_id"]
                result = await client.activate_admin_user(user_id)

            elif name == "deactivate_admin_user":
                user_id = arguments["user_id"]
                result = await client.deactivate_admin_user(user_id)

            elif name == "lock_admin_user":
                user_id = arguments["user_id"]
                result = await client.lock_admin_user(user_id)

            elif name == "unlock_admin_user":
                user_id = arguments["user_id"]
                result = await client.unlock_admin_user(user_id)

            elif name == "reset_admin_user_password":
                user_id = arguments["user_id"]
                new_password = arguments["new_password"]
                result = await client.reset_admin_user_password(user_id, new_password)

            elif name == "update_admin_user_profile":
                user_id = arguments["user_id"]
                profile_data = arguments["profile_data"]
                result = await client.update_admin_user_profile(user_id, profile_data)

            elif name == "search_admin_users":
                query = arguments["query"]
                limit = arguments.get("limit", 50)
                search_fields = arguments.get("search_fields")
                result = await client.search_admin_users(query, limit=limit, search_fields=search_fields)

            elif name == "get_admin_user_groups":
                user_id = arguments["user_id"]
                result = await client.get_admin_user_groups(user_id)

            elif name == "add_admin_user_to_group":
                user_id = arguments["user_id"]
                group_id = arguments["group_id"]
                result = await client.add_admin_user_to_group(user_id, group_id)

            elif name == "remove_admin_user_from_group":
                user_id = arguments["user_id"]
                group_id = arguments["group_id"]
                result = await client.remove_admin_user_from_group(user_id, group_id)

            elif name == "bulk_create_admin_users":
                users_data = arguments["users_data"]
                result = await client.bulk_create_admin_users(users_data)

            elif name == "get_admin_user_login_history":
                user_id = arguments["user_id"]
                limit = arguments.get("limit", 50)
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                result = await client.get_admin_user_login_history(
                    user_id, limit=limit, start_date=start_date, end_date=end_date
                )

            elif name == "get_admin_user_activity_log":
                user_id = arguments["user_id"]
                limit = arguments.get("limit", 50)
                activity_type = arguments.get("activity_type")
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                result = await client.get_admin_user_activity_log(
                    user_id, limit=limit, activity_type=activity_type,
                    start_date=start_date, end_date=end_date
                )

            # ==================== ADMIN MANAGEMENT - PERMISSIONS ====================
            elif name == "get_permissions":
                result = await client.get_permissions()
                
            elif name == "get_role_permissions":
                role_id = arguments["role_id"]
                result = await client.get_role_permissions(role_id)
                
            elif name == "update_role_permissions":
                role_id = arguments.pop("role_id")
                result = await client.update_role_permissions(role_id, arguments)
                
            elif name == "get_user_permissions":
                user_id = arguments["user_id"]
                result = await client.get_user_permissions(user_id)
                
            elif name == "update_user_permissions":
                user_id = arguments.pop("user_id")
                result = await client.update_user_permissions(user_id, arguments)
                
            # ==================== ADMIN MANAGEMENT - DEPARTMENTS ====================
            elif name == "list_departments":
                limit = arguments.get("limit", 50)
                department_type = arguments.get("department_type")
                site_id = arguments.get("site_id")
                result = await client.get_departments(
                    limit=limit, 
                    department_type=department_type, 
                    site_id=site_id
                )
                
            elif name == "get_department":
                department_id = arguments["department_id"]
                result = await client.get_department(department_id)
                
            elif name == "create_department":
                result = await client.create_department(arguments)
                
            elif name == "update_department":
                department_id = arguments.pop("department_id")
                result = await client.update_department(department_id, arguments)
                
            elif name == "delete_department":
                department_id = arguments["department_id"]
                result = await client.delete_department(department_id)
                
            elif name == "get_department_types":
                result = await client.get_department_types()
                
            # ==================== ADMIN MANAGEMENT - LOCATIONS ====================
            elif name == "list_locations":
                limit = arguments.get("limit", 50)
                location_type = arguments.get("location_type")
                site_id = arguments.get("site_id")
                result = await client.get_locations(
                    limit=limit, 
                    location_type=location_type, 
                    site_id=site_id
                )
                
            elif name == "get_location":
                location_id = arguments["location_id"]
                result = await client.get_location(location_id)
                
            elif name == "create_location":
                result = await client.create_location(arguments)
                
            elif name == "update_location":
                location_id = arguments.pop("location_id")
                result = await client.update_location(location_id, arguments)
                
            elif name == "delete_location":
                location_id = arguments["location_id"]
                result = await client.delete_location(location_id)
                
            elif name == "get_location_types":
                result = await client.get_location_types()
                
            # ==================== ADMIN MANAGEMENT - SYSTEM SETTINGS ====================
            elif name == "get_system_settings":
                result = await client.get_system_settings()
                
            elif name == "update_system_settings":
                result = await client.update_system_settings(arguments["settings"])
                
            elif name == "get_email_settings":
                result = await client.get_email_settings()
                
            elif name == "update_email_settings":
                result = await client.update_email_settings(arguments["settings"])
                
            elif name == "get_notification_settings":
                result = await client.get_notification_settings()
                
            elif name == "update_notification_settings":
                result = await client.update_notification_settings(arguments["settings"])

            # ==================== REFERENCE DATA ====================

            elif name == "get_categories":
                result = await client.get_categories()

            elif name == "get_priorities":
                result = await client.get_priorities()

            elif name == "get_statuses":
                result = await client.get_statuses()

            else:
                result = {"error": f"Unknown tool: {name}"}
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
                )
            ]
        )

async def main():
    """Main function to run the MCP server"""
    # Validate configuration
    config_validation = Config.validate_config()
    if not config_validation["valid"]:
        print("Configuration errors:")
        for issue in config_validation["issues"]:
            print(f"  - {issue}")
        return
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="servicedesk-plus",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(tools_changed=False),
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
