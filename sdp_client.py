"""
ServiceDesk Plus API Client - v3 API (Supports both Cloud and On-Premise)
Reference: 
- Cloud: https://www.manageengine.com/products/service-desk/sdpop-v3-api/
- On-Premise: https://www.manageengine.com/products/service-desk/sdpod-v3-api/
"""

import aiohttp
import json
import re
from urllib.parse import urlencode
from typing import Dict, Any, List, Optional
from config import Config


class ServiceDeskPlusClient:
    """Client for interacting with ServiceDesk Plus API v3
    
    Supports both Cloud and On-Premise versions with appropriate authentication.
    
    Note for On-Premise (v14.7):
    - Requires BOTH session cookie (via web login) AND Authtoken header
    - Uses `Authtoken` header (capital A)
    """
    
    def __init__(self, api_type: str = "cloud"):
        self.base_url = Config.SDP_BASE_URL.rstrip('/')
        self.api_key = Config.SDP_API_KEY
        self.username = Config.SDP_USERNAME
        self.password = Config.SDP_PASSWORD
        self.session: Optional[aiohttp.ClientSession] = None
        self._http_session: Optional[requests.Session] = None
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
        if self._auth_valid:
            return True
            
        if not self.api_key:
            print("API Key not configured")
            return False
            
        try:
            if self.api_type == "onpremise":
                return await self._authenticate_onpremise()
            else:
                return await self._authenticate_cloud()
                        
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    async def _authenticate_cloud(self) -> bool:
        """Authenticate with Cloud API"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
        async with self.session.get(
            f"{self.base_url}{Config.API_ENDPOINTS['requests']}",
            headers=self._get_headers(),
            params={"input_data": "{}"}
        ) as response:
            if response.status in [200, 201]:
                self._auth_valid = True
                return True
            else:
                text = await response.text()
                print(f"Authentication failed: {response.status} - {text}")
                return False
    
    async def _authenticate_onpremise(self) -> bool:
        """Authenticate with On-Premise API (requires session cookie + Authtoken)
        
        SDP On-Premise v14.7 requires BOTH:
        1. A valid session cookie (via web login)
        2. The Authtoken header
        """
        try:
            import requests as req
        except ImportError:
            raise Exception("requests library required for On-Premise auth")
        
        self._http_session = req.Session()
        self._http_session.verify = False
        
        # Step 1: Get login page for CSRF token
        r = self._http_session.get(f"{self.base_url}/", timeout=Config.REQUEST_TIMEOUT)
        csrf_match = re.search(r'name="sdplogincsrfparam" value="([^"]+)"', r.text)
        if not csrf_match:
            print("Could not find CSRF token")
            return False
        
        csrf_val = csrf_match.group(1)
        
        # Step 2: Login with credentials
        login_data = {
            "j_username": self.username or "administrator",
            "j_password": self.password or "",
            "sdplogincsrfparam": csrf_val
        }
        r = self._http_session.post(
            f"{self.base_url}/j_security_check",
            data=login_data,
            headers={"Accept": "application/json"},
            timeout=Config.REQUEST_TIMEOUT
        )
        
        if r.status_code != 200:
            print(f"Login failed: {r.status_code}")
            return False
            
        # Step 3: Verify API access with session + Authtoken
        import urllib.parse
        input_data = json.dumps({"list_info": {"start_index": 1, "row_count": 1}})
        url = f"{self.base_url}{Config.API_ENDPOINTS['requests']}?input_data={urllib.parse.quote(input_data)}"
        r = self._http_session.get(
            url,
            headers=self._get_headers(),
            timeout=Config.REQUEST_TIMEOUT
        )
        
        if r.status_code in [200, 201]:
            self._auth_valid = True
            return True
        else:
            print(f"On-Premise API auth failed: {r.status_code} - {r.text[:200]}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API v3 requests based on API type"""
        base_headers = {
            "Accept": "application/vnd.manageengine.sdp.v3+json",
            "Content-Type": "application/x-www-form-urlencoded",
            "PORTALID": Config.SDP_PORTAL_ID
        }
        
        if self.api_type == "onpremise":
            base_headers["Authtoken"] = self.api_key
        else:
            base_headers["authtoken"] = self.api_key
            
        return base_headers
    
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
        headers = self._get_headers()
        
        if self.api_type == "onpremise" and self._http_session:
            return await self._make_onpremise_request(method, url, data, headers)
        else:
            return await self._make_aiohttp_request(method, url, data, headers)
    
    async def _make_onpremise_request(self, method, url, data, headers):
        """Make request using requests.Session (for On-Premise with session cookies)"""
        kw = {"headers": headers, "timeout": Config.REQUEST_TIMEOUT}
        try:
            if method == "GET":
                if data:
                    sep = "&" if "?" in url else "?"
                    url += sep + urlencode({"input_data": json.dumps(data)})
                r = self._http_session.get(url, **kw)
            elif method == "POST":
                kw["data"] = {"input_data": json.dumps(data)} if data else {}
                r = self._http_session.post(url, **kw)
            elif method == "PUT":
                kw["data"] = {"input_data": json.dumps(data)} if data else {}
                r = self._http_session.put(url, **kw)
            elif method == "DELETE":
                r = self._http_session.delete(url, **kw)
            
            if r.status_code in [200, 201]:
                return r.json()
            else:
                raise Exception(f"API request failed: {r.status_code} - {r.text[:500]}")
        except Exception as e:
            if "API request failed" in str(e):
                raise
            raise Exception(f"Request failed: {e}")
    
    async def _make_aiohttp_request(self, method, url, data, headers):
        """Make request using aiohttp (for Cloud API)"""
        try:
            async with self.session.request(
                method, url,
                headers=headers,
                data=urlencode({"input_data": json.dumps(data)}).encode() if data else None,
                timeout=aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
            ) as response:
                text = await response.text()
                if response.status in [200, 201]:
                    return json.loads(text)
                else:
                    raise Exception(f"API request failed: {response.status} - {text[:500]}")
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
                "description": text,
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

    # ==================== TICKET ALIASES (main.py compatibility) ====================

    async def get_tickets(self, limit: int = 50, status: Optional[str] = None, priority: Optional[str] = None, requester: Optional[str] = None) -> Dict[str, Any]:
        return await self.get_requests(limit=limit)

    async def get_request_worklog(self, request_id: str, limit: int = 20) -> Dict[str, Any]:
        return await self.get_request_worklogs(request_id)

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return await self.get_request(ticket_id)

    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.create_request(ticket_data)

    async def update_ticket(self, ticket_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.update_request(ticket_id, update_data)

    async def delete_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return await self.delete_request(ticket_id)

    async def search_tickets(self, query: str, limit: int = 20) -> Dict[str, Any]:
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1, "search_criteria": [{"field": "subject", "condition": "contains", "value": query}]}}
        return await self._make_request("GET", Config.API_ENDPOINTS["requests"], data=input_data)

    async def get_technicians(self, limit: int = 20) -> Dict[str, Any]:
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        return await self._make_request("GET", Config.API_ENDPOINTS["technicians"], data=input_data)

    # ==================== REQUEST COMMENTS ====================

    async def add_ticket_comment(self, request_id: str, comment: str) -> Dict[str, Any]:
        comment_data = {"comment": {"content": comment}}
        return await self._make_request("POST", Config.API_ENDPOINTS["request_notes"].format(request_id=request_id), data=comment_data)

    async def get_ticket_comments(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_notes"].format(request_id=request_id))

    # ==================== REQUEST ADVANCED OPERATIONS ====================

    async def reassign_request(self, request_id: str, technician_id: Optional[str] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if technician_id:
            data["technician"] = {"id": technician_id}
        if reason:
            data["reason"] = reason
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['requests']}/{request_id}/reassign", data={"request": data})

    async def escalate_request(self, request_id: str, escalation_level: Optional[str] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if escalation_level:
            data["escalation_level"] = escalation_level
        if reason:
            data["reason"] = reason
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['requests']}/{request_id}/escalate", data={"request": data})

    async def approve_request(self, request_id: str, approval_comments: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if approval_comments:
            data["approval_comments"] = approval_comments
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['requests']}/{request_id}/approve", data={"request": data})

    async def reject_request(self, request_id: str, rejection_reason: Optional[str] = None, comments: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if rejection_reason:
            data["rejection_reason"] = rejection_reason
        if comments:
            data["comments"] = comments
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['requests']}/{request_id}/reject", data={"request": data})

    async def get_request_approvals(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_approvals"].format(request_id=request_id))

    async def get_request_attachments(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_attachments"].format(request_id=request_id))

    async def add_request_attachment(self, request_id: str, file_path: str, description: Optional[str] = None) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["request_attachments"].format(request_id=request_id), data={"file": file_path, "description": description or ""})

    async def delete_request_attachment(self, request_id: str, attachment_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['request_attachments'].format(request_id=request_id)}/{attachment_id}")

    async def get_request_history(self, request_id: str, limit: int = 50) -> Dict[str, Any]:
        input_data = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        return await self._make_request("GET", Config.API_ENDPOINTS["request_history"].format(request_id=request_id), data=input_data)

    async def get_request_sla_details(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_sla"].format(request_id=request_id))

    async def update_request_sla(self, request_id: str, sla_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["request_sla"].format(request_id=request_id), data={"sla": sla_data})

    async def get_request_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": 50, "start_index": 1}}
        if category:
            input_data["category"] = {"name": category}
        return await self._make_request("GET", Config.API_ENDPOINTS["request_templates"], data=input_data)

    async def create_request_from_template(self, template_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", f"{Config.API_ENDPOINTS['request_templates']}/{template_id}/requests", data={"request": request_data})

    async def get_closure_codes(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_closure_codes"])

    async def add_worklog_entry(self, request_id: str, description: str, time_spent: Optional[str] = None, technician_id: Optional[str] = None) -> Dict[str, Any]:
        worklog = {"description": description}
        if time_spent:
            worklog["time_spent"] = time_spent
        if technician_id:
            worklog["technician"] = {"id": technician_id}
        return await self._make_request("POST", Config.API_ENDPOINTS["request_worklogs"].format(request_id=request_id), data={"worklog": worklog})

    async def update_worklog_entry(self, request_id: str, worklog_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['request_worklogs'].format(request_id=request_id)}/{worklog_id}", data={"worklog": update_data})

    async def get_request_custom_fields(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_custom_fields"].format(request_id=request_id))

    async def update_request_custom_fields(self, request_id: str, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["request_custom_fields"].format(request_id=request_id), data={"custom_fields": custom_fields})

    async def get_request_feedback(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_feedback"].format(request_id=request_id))

    async def submit_request_feedback(self, request_id: str, rating: int, comments: Optional[str] = None, survey_responses: Optional[Dict] = None) -> Dict[str, Any]:
        feedback: Dict[str, Any] = {"rating": rating}
        if comments:
            feedback["comments"] = comments
        if survey_responses:
            feedback["survey_responses"] = survey_responses
        return await self._make_request("POST", Config.API_ENDPOINTS["request_feedback"].format(request_id=request_id), data={"feedback": feedback})

    async def get_request_notifications(self, request_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["request_notifications"].format(request_id=request_id))

    async def send_request_notification(self, request_id: str, notification_type: Optional[str] = None, recipients: Optional[str] = None, custom_message: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if notification_type:
            data["notification_type"] = notification_type
        if recipients:
            data["recipients"] = recipients
        if custom_message:
            data["custom_message"] = custom_message
        return await self._make_request("POST", Config.API_ENDPOINTS["request_notifications"].format(request_id=request_id), data={"notification": data})

    # ==================== REFERENCE DATA ====================

    async def get_categories(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["categories"])

    async def get_priorities(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["priorities"])

    async def get_statuses(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["statuses"])

    # ==================== CMDB ====================

    async def get_ci_relationships(self, ci_id: Optional[str] = None) -> Dict[str, Any]:
        endpoint = Config.API_ENDPOINTS["cmdb"] + "/relationships"
        if ci_id:
            endpoint += f"?ci_id={ci_id}"
        return await self._make_request("GET", endpoint)

    # ==================== ASSET REFERENCE DATA ====================

    async def get_asset_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["asset_types"])

    async def get_asset_categories(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["asset_categories"])

    async def get_asset_locations(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["asset_locations"])

    async def get_asset_models(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["asset_models"])

    async def get_asset_vendors(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["asset_vendors"])

    # ==================== SOFTWARE LICENSE MANAGEMENT ====================

    async def get_software_licenses(self, limit: int = 20, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["software_licenses"], data=input_data)

    async def get_software_license(self, license_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['software_licenses']}/{license_id}")

    async def create_software_license(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["software_licenses"], data={"software_license": license_data})

    async def update_software_license(self, license_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['software_licenses']}/{license_id}", data={"software_license": update_data})

    async def get_software_products(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["software_products"])

    async def get_license_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["license_types"])

    # ==================== CONTRACT REFERENCE DATA ====================

    async def get_contract_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["contract_types"])

    async def get_contract_vendors(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["contract_vendors"])

    async def update_contract(self, contract_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['contracts']}/{contract_id}", data={"contract": update_data})

    # ==================== PURCHASE ORDER REFERENCE DATA ====================

    async def update_purchase_order(self, po_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['purchase_orders']}/{po_id}", data={"purchase_order": update_data})

    async def get_po_statuses(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["po_statuses"])

    # ==================== VENDOR MANAGEMENT ====================

    async def get_vendors(self, limit: int = 20, vendor_type: Optional[str] = None, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["vendors"], data=input_data)

    async def get_vendor(self, vendor_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['vendors']}/{vendor_id}")

    async def create_vendor(self, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["vendors"], data={"vendor": vendor_data})

    async def update_vendor(self, vendor_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['vendors']}/{vendor_id}", data={"vendor": update_data})

    async def get_vendor_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["vendor_types"])

    # ==================== ADMIN: SITES ====================

    async def get_sites(self, limit: int = 20, site_type: Optional[str] = None, status: Optional[str] = None, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["sites"], data=input_data)

    async def get_site(self, site_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['sites']}/{site_id}")

    async def create_site(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["sites"], data={"site": site_data})

    async def update_site(self, site_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['sites']}/{site_id}", data={"site": update_data})

    async def delete_site(self, site_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['sites']}/{site_id}")

    async def get_site_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["site_types"])

    # ==================== ADMIN: USER GROUPS ====================

    async def get_user_groups(self, limit: int = 20, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["user_groups"], data=input_data)

    async def get_user_group(self, group_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['user_groups']}/{group_id}")

    async def create_user_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["user_groups"], data={"group": group_data})

    async def update_user_group(self, group_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['user_groups']}/{group_id}", data={"group": update_data})

    async def delete_user_group(self, group_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['user_groups']}/{group_id}")

    async def get_group_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["group_types"])

    async def get_group_permissions(self, group_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["group_permissions"].format(group_id=group_id))

    async def update_group_permissions(self, group_id: str, permissions: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["group_permissions"].format(group_id=group_id), data={"permissions": permissions})

    # ==================== ADMIN: USERS ====================

    async def get_admin_users(self, limit: int = 20, role: Optional[str] = None, status: Optional[str] = None, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_users"], data=input_data)

    async def get_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}")

    async def create_admin_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["admin_users"], data={"user": user_data})

    async def update_admin_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}", data={"user": update_data})

    async def delete_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}")

    async def get_admin_user_groups(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_user_groups"].format(user_id=user_id))

    async def add_admin_user_to_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["admin_user_groups"].format(user_id=user_id), data={"group": {"id": group_id}})

    async def remove_admin_user_from_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['admin_user_groups'].format(user_id=user_id)}/{group_id}")

    async def get_admin_user_login_history(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_user_login_history"].format(user_id=user_id))

    async def get_admin_user_activity_log(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_user_activity_log"].format(user_id=user_id))

    # ==================== ADMIN: TECHNICIANS ====================

    async def get_admin_technicians(self, limit: int = 20, role: Optional[str] = None, status: Optional[str] = None, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_technicians"], data=input_data)

    async def get_admin_technician(self, technician_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['admin_technicians']}/{technician_id}")

    async def create_admin_technician(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["admin_technicians"], data={"technician": tech_data})

    async def update_admin_technician(self, technician_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_technicians']}/{technician_id}", data={"technician": update_data})

    async def delete_admin_technician(self, technician_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['admin_technicians']}/{technician_id}")

    # ==================== ADMIN: USER/TECHNICIAN OPERATIONS ====================

    async def get_user_roles(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["user_roles"])

    async def get_technician_roles(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["technician_roles"])

    async def convert_user_to_technician(self, user_id: str, role_id: Optional[str] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if role_id:
            data["role"] = {"id": role_id}
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/convert_to_technician", data={"technician": data})

    async def activate_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/activate")

    async def deactivate_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/deactivate")

    async def lock_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/lock")

    async def unlock_admin_user(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/unlock")

    async def reset_admin_user_password(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/reset_password")

    async def update_admin_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['admin_users']}/{user_id}/profile", data={"profile": profile_data})

    async def search_admin_users(self, query: str, limit: int = 20) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1, "search_criteria": [{"field": "name", "condition": "contains", "value": query}]}}
        return await self._make_request("GET", Config.API_ENDPOINTS["admin_users"], data=input_data)

    async def bulk_create_admin_users(self, users_data: list) -> Dict[str, Any]:
        return await self._make_request("POST", f"{Config.API_ENDPOINTS['admin_users']}/bulk", data={"users": users_data})

    # ==================== ADMIN: PERMISSIONS ====================

    async def get_permissions(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["permissions"])

    async def get_role_permissions(self, role_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["role_permissions"].format(role_id=role_id))

    async def update_role_permissions(self, role_id: str, permissions: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["role_permissions"].format(role_id=role_id), data={"permissions": permissions})

    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["user_permissions"].format(user_id=user_id))

    async def update_user_permissions(self, user_id: str, permissions: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["user_permissions"].format(user_id=user_id), data={"permissions": permissions})

    # ==================== ADMIN: DEPARTMENTS ====================

    async def get_departments(self, limit: int = 20, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["departments"], data=input_data)

    async def get_department(self, department_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['departments']}/{department_id}")

    async def create_department(self, dept_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["departments"], data={"department": dept_data})

    async def update_department(self, department_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['departments']}/{department_id}", data={"department": update_data})

    async def delete_department(self, department_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['departments']}/{department_id}")

    async def get_department_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["department_types"])

    # ==================== ADMIN: LOCATIONS ====================

    async def get_locations(self, limit: int = 20, search_criteria: Optional[list] = None) -> Dict[str, Any]:
        input_data: Dict[str, Any] = {"list_info": {"row_count": min(limit, Config.MAX_LIMIT), "start_index": 1}}
        if search_criteria:
            input_data["list_info"]["search_criteria"] = search_criteria
        return await self._make_request("GET", Config.API_ENDPOINTS["locations"], data=input_data)

    async def get_location(self, location_id: str) -> Dict[str, Any]:
        return await self._make_request("GET", f"{Config.API_ENDPOINTS['locations']}/{location_id}")

    async def create_location(self, loc_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", Config.API_ENDPOINTS["locations"], data={"location": loc_data})

    async def update_location(self, location_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", f"{Config.API_ENDPOINTS['locations']}/{location_id}", data={"location": update_data})

    async def delete_location(self, location_id: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", f"{Config.API_ENDPOINTS['locations']}/{location_id}")

    async def get_location_types(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["location_types"])

    # ==================== ADMIN: SYSTEM SETTINGS ====================

    async def get_system_settings(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["system_settings"])

    async def update_system_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["system_settings"], data={"settings": settings})

    async def get_email_settings(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["email_settings"])

    async def update_email_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["email_settings"], data={"settings": settings})

    async def get_notification_settings(self) -> Dict[str, Any]:
        return await self._make_request("GET", Config.API_ENDPOINTS["notification_settings"])

    async def update_notification_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("PUT", Config.API_ENDPOINTS["notification_settings"], data={"settings": settings})
