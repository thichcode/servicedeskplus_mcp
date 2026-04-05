"""
ServiceDesk Plus API Client - v3 API (Cloud Version)
Compatible with ServiceDesk Plus Cloud API v3
Reference: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
"""

import aiohttp
import asyncio
import json
from urllib.parse import urlencode
from typing import Dict, Any, List, Optional
from config import Config


class ServiceDeskPlusClient:
    """Client for interacting with ServiceDesk Plus Cloud API v3"""
    
    def __init__(self):
        self.base_url = Config.SDP_BASE_URL.rstrip('/')
        self.api_key = Config.SDP_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self._auth_valid = False
        
    async def __aenter__(self):
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
            
    async def authenticate(self) -> bool:
        """Authenticate with ServiceDesk Plus using API Key"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
        if self._auth_valid:
            return True
            
        if not self.api_key:
            print("API Key not configured")
            return False
            
        try:
            async with self.session.get(
                f"{self.base_url}{Config.API_ENDPOINTS['requests']}",
                headers=self._get_headers(),
                params={"input_data": "{}"}
            ) as response:
                if response.status in [200, 201]:
                    self._auth_valid = True
                    return True
                else:
                    print(f"Authentication failed: {response.status} - {await response.text()}")
                    return False
                        
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API v3 requests"""
        return {
            "Accept": "application/vnd.manageengine.sdp.v3+json",
            "Content-Type": "application/x-www-form-urlencoded",
            "authtoken": self.api_key
        }
            
    def _prepare_input_data(self, data: Optional[Dict[str, Any]] = None) -> str:
        """Prepare input_data for API v3"""
        if data is None:
            return "{}"
        return urlencode({"input_data": json.dumps(data)})
            
    async def _make_request(
        self, 
        method: str, 
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to ServiceDesk Plus API v3"""
        if not await self.authenticate():
            raise Exception("Authentication failed")
            
        url = f"{self.base_url}{endpoint}"
        
        request_kwargs = {
            "headers": self._get_headers(),
        }
        
        if method in ["POST", "PUT"] and data:
            request_kwargs["data"] = self._prepare_input_data(data)
            
        try:
            async with self.session.request(method, url, **request_kwargs) as response:
                response_text = await response.text()
                
                if response.status in [200, 201]:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"raw_response": response_text}
                else:
                    raise Exception(f"API request failed: {response.status} - {response_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Request failed: {e}")

    # ==================== REQUEST (TICKET) MANAGEMENT ====================
    
    async def get_requests(
        self, 
        limit: int = 20,
        filter_by: Optional[str] = None,
        search_criteria: Optional[List[Dict]] = None,
        sort_field: str = "created_time",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get list of requests with optional filtering and sorting"""
        input_data = {
            "list_info": {
                "row_count": min(limit, Config.MAX_LIMIT),
                "start_index": 1,
                "sort_field": sort_field,
                "sort_order": sort_order
            }
        }
        
        if filter_by:
            input_data["list_info"]["filter_by"] = {"name": filter_by}
            
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
            
        return await self._make_request("GET", Config.API_ENDPOINTS["requests"], data=input_data)
        
    async def get_request(self, request_id: str) -> Dict[str, Any]:
        """Get specific request details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}"
        )
        
    async def create_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new request - subject is mandatory"""
        if "subject" not in request_data:
            raise ValueError("Required field 'subject' is missing")
            
        wrapper = {"request": request_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["requests"], data=wrapper)
        
    async def update_request(self, request_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing request"""
        wrapper = {"request": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}",
            data=wrapper
        )
        
    async def delete_request(self, request_id: str) -> Dict[str, Any]:
        """Delete a request"""
        return await self._make_request(
            "DELETE",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}"
        )
        
    async def close_request(
        self,
        request_id: str,
        closure_code: str,
        closure_comments: Optional[str] = None,
        requester_ack_resolution: bool = True
    ) -> Dict[str, Any]:
        """Close a request"""
        closure_data = {
            "request": {
                "closure_info": {
                    "closure_code": {"name": closure_code},
                    "closure_comments": closure_comments or "",
                    "requester_ack_resolution": requester_ack_resolution
                }
            }
        }
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}/close",
            data=closure_data
        )
        
    async def assign_request(
        self,
        request_id: str,
        technician_id: Optional[str] = None,
        group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assign request to technician and/or group"""
        assignment_data = {"request": {}}
        
        if technician_id:
            assignment_data["request"]["technician"] = {"id": technician_id}
        if group_id:
            assignment_data["request"]["group"] = {"id": group_id}
            
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}/assign",
            data=assignment_data
        )
        
    async def pickup_request(self, request_id: str) -> Dict[str, Any]:
        """Pick up an unassigned request"""
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}/pickup"
        )
        
    async def add_resolution(self, request_id: str, resolution_content: str) -> Dict[str, Any]:
        """Add resolution to a request"""
        resolution_data = {
            "request": {
                "resolution": {
                    "content": resolution_content
                }
            }
        }
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}/resolution",
            data=resolution_data
        )
        
    async def get_request_summary(self, request_id: str) -> Dict[str, Any]:
        """Get request summary"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['requests']}/{request_id}/summary"
        )
        
    async def get_request_filters(self) -> Dict[str, Any]:
        """Get all available request filters"""
        return await self._make_request(
            "GET",
            Config.API_ENDPOINTS["request_filters"]
        )

    # ==================== REQUEST NOTES ====================
    
    async def add_request_note(self, request_id: str, text: str, show_to_requester: bool = False) -> Dict[str, Any]:
        """Add a note to a request"""
        note_data = {
            "note": {
                "text": text,
                "show_to_requester": show_to_requester
            }
        }
        return await self._make_request(
            "POST",
            f"{Config.API_ENDPOINTS['request_notes'].format(request_id=request_id)}",
            data=note_data
        )
        
    async def get_request_notes(self, request_id: str) -> Dict[str, Any]:
        """Get notes for a request"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['request_notes'].format(request_id=request_id)}"
        )

    # ==================== REQUEST TASKS ====================
    
    async def get_request_tasks(self, request_id: str) -> Dict[str, Any]:
        """Get tasks for a request"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['request_tasks'].format(request_id=request_id)}"
        )
        
    async def create_request_task(self, request_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a task for a request"""
        wrapper = {"request_task": task_data}
        return await self._make_request(
            "POST",
            f"{Config.API_ENDPOINTS['request_tasks'].format(request_id=request_id)}",
            data=wrapper
        )

    # ==================== DRAFT MANAGEMENT ====================
    
    async def get_drafts(self, limit: int = 20) -> Dict[str, Any]:
        """Get draft requests"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        return await self._make_request("GET", Config.API_ENDPOINTS["drafts"], data=input_data)
        
    async def create_draft(self, draft_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a draft request"""
        wrapper = {"request": draft_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["drafts"], data=wrapper)

    # ==================== ARCHIVE MANAGEMENT ====================
    
    async def get_archived_requests(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get archived requests"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["archive"], data=input_data)
        
    async def restore_request(self, request_id: str) -> Dict[str, Any]:
        """Restore a request from trash"""
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['archive']}/{request_id}/restore"
        )
        
    async def permanent_delete_request(self, request_id: str) -> Dict[str, Any]:
        """Permanently delete a request from trash"""
        return await self._make_request(
            "DELETE",
            f"{Config.API_ENDPOINTS['archive']}/{request_id}"
        )

    # ==================== USER MANAGEMENT (Admin) ====================
    
    async def get_users(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of users"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["users"], data=input_data)
        
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get specific user details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['users']}/{user_id}"
        )
        
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        required_fields = ["name", "email_id"]
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Required field '{field}' is missing")
                
        wrapper = {"user": user_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["users"], data=wrapper)
        
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user"""
        wrapper = {"user": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['users']}/{user_id}",
            data=wrapper
        )
        
    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user"""
        return await self._make_request(
            "DELETE",
            f"{Config.API_ENDPOINTS['users']}/{user_id}"
        )

    # ==================== CHANGE MANAGEMENT ====================
    
    async def get_changes(
        self,
        limit: int = 20,
        filter_by: Optional[str] = None,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of changes"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if filter_by:
            input_data["list_info"]["filter_by"] = {"name": filter_by}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["changes"], data=input_data)
        
    async def get_change(self, change_id: str) -> Dict[str, Any]:
        """Get specific change details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['changes']}/{change_id}"
        )
        
    async def create_change(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new change"""
        if "subject" not in change_data:
            raise ValueError("Required field 'subject' is missing")
        wrapper = {"change": change_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["changes"], data=wrapper)
        
    async def update_change(self, change_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing change"""
        wrapper = {"change": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['changes']}/{change_id}",
            data=wrapper
        )
        
    async def approve_change(self, change_id: str, approval_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Approve a change"""
        data = {"change_approval": approval_data or {}}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['changes']}/{change_id}/approve",
            data=data
        )
        
    async def reject_change(self, change_id: str, rejection_reason: str) -> Dict[str, Any]:
        """Reject a change"""
        data = {
            "change_approval": {
                "comments": rejection_reason
            }
        }
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['changes']}/{change_id}/reject",
            data=data
        )

    # ==================== PROJECT MANAGEMENT ====================
    
    async def get_projects(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of projects"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["projects"], data=input_data)
        
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get specific project details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['projects']}/{project_id}"
        )
        
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        if "name" not in project_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"project": project_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["projects"], data=wrapper)
        
    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project"""
        wrapper = {"project": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['projects']}/{project_id}",
            data=wrapper
        )

    # ==================== MILESTONE MANAGEMENT ====================
    
    async def get_milestones(
        self,
        project_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of milestones"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if project_id:
            input_data["project"] = {"id": project_id}
        return await self._make_request("GET", Config.API_ENDPOINTS["milestones"], data=input_data)
        
    async def get_milestone(self, milestone_id: str) -> Dict[str, Any]:
        """Get specific milestone details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['milestones']}/{milestone_id}"
        )
        
    async def create_milestone(self, milestone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new milestone"""
        if "name" not in milestone_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"milestone": milestone_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["milestones"], data=wrapper)

    # ==================== RELEASE MANAGEMENT ====================
    
    async def get_releases(
        self,
        limit: int = 20,
        filter_by: Optional[str] = None,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of releases"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if filter_by:
            input_data["list_info"]["filter_by"] = {"name": filter_by}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["releases"], data=input_data)
        
    async def get_release(self, release_id: str) -> Dict[str, Any]:
        """Get specific release details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['releases']}/{release_id}"
        )
        
    async def create_release(self, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new release"""
        if "name" not in release_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"release": release_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["releases"], data=wrapper)
        
    async def update_release(self, release_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing release"""
        wrapper = {"release": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['releases']}/{release_id}",
            data=wrapper
        )
        
    async def approve_release(self, release_id: str) -> Dict[str, Any]:
        """Approve a release"""
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['releases']}/{release_id}/approve"
        )
        
    async def reject_release(self, release_id: str, rejection_reason: str) -> Dict[str, Any]:
        """Reject a release"""
        data = {"release_approval": {"comments": rejection_reason}}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['releases']}/{release_id}/reject",
            data=data
        )

    # ==================== TASK MANAGEMENT ====================
    
    async def get_tasks(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of tasks"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["tasks"], data=input_data)
        
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get specific task details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['tasks']}/{task_id}"
        )
        
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        if "name" not in task_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"task": task_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["tasks"], data=wrapper)
        
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        wrapper = {"task": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['tasks']}/{task_id}",
            data=wrapper
        )
        
    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task"""
        return await self._make_request(
            "DELETE",
            f"{Config.API_ENDPOINTS['tasks']}/{task_id}"
        )
