"""
ServiceDesk Plus API Client - v3 API (Supports both Cloud and On-Premise)
Reference: 
- Cloud: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
- On-Premise: https://www.manageengine.com/products/service-desk/sdpod-v3-api/
"""

import aiohttp
import json
from urllib.parse import urlencode
from typing import Dict, Any, List, Optional
from config import Config


class ServiceDeskPlusClient:
    """Client for interacting with ServiceDesk Plus API v3
    
    Supports both Cloud and On-Premise versions with appropriate authentication.
    """
    
    def __init__(self, api_type: str = "cloud"):
        """Initialize the client
        
        Args:
            api_type: "cloud" for Cloud API, "onpremise" for On-Premise API
        """
        self.base_url = Config.SDP_BASE_URL.rstrip('/')
        self.api_key = Config.SDP_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self._auth_valid = False
        self.api_type = api_type
        
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
        """Authenticate with ServiceDesk Plus"""
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
        """Get headers for API v3 requests based on API type"""
        base_headers = {
            "Accept": "application/vnd.manageengine.sdp.v3+json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if self.api_type == "onpremise":
            base_headers["Authorization"] = f"Zoho-oauthtoken {self.api_key}"
        else:
            base_headers["authtoken"] = self.api_key
            
        return base_headers
            
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
        """Get list of requests with optional filtering"""
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
        closure_comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close a request"""
        closure_data = {
            "request": {
                "closure_info": {
                    "closure_code": {"name": closure_code},
                    "closure_comments": closure_comments or ""
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
        
    async def get_request_filters(self) -> Dict[str, Any]:
        """Get all available request filters"""
        return await self._make_request(
            "GET",
            Config.API_ENDPOINTS["request_filters"]
        )

    # ==================== REQUEST NOTES ====================
    
    async def add_request_note(
        self, 
        request_id: str, 
        text: str, 
        show_to_requester: bool = False
    ) -> Dict[str, Any]:
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

    # ==================== REQUEST WORKLOGS (On-Premise only) ====================
    
    async def get_request_worklogs(self, request_id: str) -> Dict[str, Any]:
        """Get worklogs for a request (On-Premise API)"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['request_worklogs'].format(request_id=request_id)}"
        )
        
    async def add_request_worklog(
        self,
        request_id: str,
        description: str,
        hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """Add worklog to a request (On-Premise API)"""
        worklog_data = {"description": description}
        if hours:
            worklog_data["hours"] = hours
            
        wrapper = {"request_worklog": worklog_data}
        return await self._make_request(
            "POST",
            f"{Config.API_ENDPOINTS['request_worklogs'].format(request_id=request_id)}",
            data=wrapper
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
        if "name" not in user_data or "email_id" not in user_data:
            raise ValueError("Required fields 'name' and 'email_id' are missing")
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

    # ==================== PROBLEM MANAGEMENT (On-Premise only) ====================
    
    async def get_problems(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of problems (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["problems"], data=input_data)
        
    async def get_problem(self, problem_id: str) -> Dict[str, Any]:
        """Get specific problem details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['problems']}/{problem_id}"
        )
        
    async def create_problem(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new problem"""
        if "subject" not in problem_data:
            raise ValueError("Required field 'subject' is missing")
        wrapper = {"problem": problem_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["problems"], data=wrapper)

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

    # ==================== ASSET MANAGEMENT (On-Premise only) ====================
    
    async def get_assets(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of assets (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["assets"], data=input_data)
        
    async def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get specific asset details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['assets']}/{asset_id}"
        )
        
    async def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new asset (name and product are required)"""
        if "name" not in asset_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"asset": asset_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["assets"], data=wrapper)
        
    async def update_asset(self, asset_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing asset"""
        wrapper = {"asset": update_data}
        return await self._make_request(
            "PUT",
            f"{Config.API_ENDPOINTS['assets']}/{asset_id}",
            data=wrapper
        )
        
    async def delete_asset(self, asset_id: str) -> Dict[str, Any]:
        """Delete an asset"""
        return await self._make_request(
            "DELETE",
            f"{Config.API_ENDPOINTS['assets']}/{asset_id}"
        )

    # ==================== CONTRACT MANAGEMENT (On-Premise only) ====================
    
    async def get_contracts(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of contracts (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["contracts"], data=input_data)
        
    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """Get specific contract details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['contracts']}/{contract_id}"
        )
        
    async def create_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contract"""
        if "name" not in contract_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {"contract": contract_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["contracts"], data=wrapper)

    # ==================== PURCHASE ORDER MANAGEMENT (On-Premise only) ====================
    
    async def get_purchase_orders(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of purchase orders (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["purchase_orders"], data=input_data)
        
    async def get_purchase_order(self, po_id: str) -> Dict[str, Any]:
        """Get specific purchase order details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['purchase_orders']}/{po_id}"
        )
        
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new purchase order"""
        wrapper = {"purchase_order": po_data}
        return await self._make_request("POST", Config.API_ENDPOINTS["purchase_orders"], data=wrapper)

    # ==================== CMDB MANAGEMENT (On-Premise only) ====================
    
    async def get_ci_types(self) -> Dict[str, Any]:
        """Get list of CI types (On-Premise API)"""
        return await self._make_request("GET", Config.API_ENDPOINTS["ci_types"])
        
    async def get_configuration_items(
        self,
        ci_type_api_name: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of CIs for a specific CI type"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        endpoint = f"{Config.API_ENDPOINTS['cmdb']}/{ci_type_api_name}"
        return await self._make_request("GET", endpoint, data=input_data)
        
    async def get_configuration_item(self, ci_type_api_name: str, ci_id: str) -> Dict[str, Any]:
        """Get specific CI details"""
        endpoint = f"{Config.API_ENDPOINTS['cmdb']}/{ci_type_api_name}/{ci_id}"
        return await self._make_request("GET", endpoint)
        
    async def create_configuration_item(
        self,
        ci_type_api_name: str,
        ci_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new CI for a specific CI type"""
        if "name" not in ci_data:
            raise ValueError("Required field 'name' is missing")
        wrapper = {ci_type_api_name: ci_data}
        endpoint = f"{Config.API_ENDPOINTS['cmdb']}/{ci_type_api_name}"
        return await self._make_request("POST", endpoint, data=wrapper)
        
    async def update_configuration_item(
        self,
        ci_type_api_name: str,
        ci_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing CI"""
        wrapper = {ci_type_api_name: update_data}
        endpoint = f"{Config.API_ENDPOINTS['cmdb']}/{ci_type_api_name}/{ci_id}"
        return await self._make_request("PUT", endpoint, data=wrapper)
        
    async def delete_configuration_item(
        self,
        ci_type_api_name: str,
        ci_ids: List[str]
    ) -> Dict[str, Any]:
        """Delete one or more CIs"""
        ids_param = ",".join(ci_ids)
        endpoint = f"{Config.API_ENDPOINTS['cmdb']}/{ci_type_api_name}?ids={ids_param}"
        return await self._make_request("DELETE", endpoint)

    # ==================== SOLUTIONS (On-Premise only) ====================
    
    async def get_solutions(
        self,
        limit: int = 20,
        search_criteria: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Get list of solutions (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["solutions"], data=input_data)
        
    async def get_solution(self, solution_id: str) -> Dict[str, Any]:
        """Get specific solution details"""
        return await self._make_request(
            "GET",
            f"{Config.API_ENDPOINTS['solutions']}/{solution_id}"
        )

    # ==================== SPACE MANAGEMENT (On-Premise only) ====================
    
    async def get_campuses(self, limit: int = 20) -> Dict[str, Any]:
        """Get list of campuses (On-Premise API)"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        return await self._make_request("GET", Config.API_ENDPOINTS["campuses"], data=input_data)
        
    async def get_buildings(
        self,
        campus_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of buildings"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if campus_id:
            input_data["campus"] = {"id": campus_id}
        return await self._make_request("GET", Config.API_ENDPOINTS["buildings"], data=input_data)
        
    async def get_floors(
        self,
        building_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of floors"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if building_id:
            input_data["building"] = {"id": building_id}
        return await self._make_request("GET", Config.API_ENDPOINTS["floors"], data=input_data)
        
    async def get_rooms(
        self,
        floor_id: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of rooms"""
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if floor_id:
            input_data["floor"] = {"id": floor_id}
        return await self._make_request("GET", Config.API_ENDPOINTS["rooms"], data=input_data)
