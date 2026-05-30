# SDP On-Premise API v3 - Complete Analysis

## Headers Required

Every API call requires these headers:

```
Accept: application/vnd.manageengine.sdp.v3+json
Content-Type: application/x-www-form-urlencoded
PORTALID: <portal_id>          # Required! Default: "1"
Authtoken: <api_key>           # For On-Premise (capital A)
```

## Data Format

### GET requests
Pass `input_data` as URL query parameter (URL-encoded JSON):
```
GET /api/v3/requests?input_data={"list_info":{"start_index":1,"row_count":10}}
```

### POST/PUT requests
Pass `input_data` as form-encoded body:
```
POST /api/v3/requests
Content-Type: application/x-www-form-urlencoded

input_data={"request":{"subject":"Test","requester":{"id":"4"}}}
```

### DELETE requests
No body needed, just the ID in URL:
```
DELETE /api/v3/requests/123
```

---

## Module-by-Module API Support

### Requests (Full CRUD ✅)

| Operation | Method | Endpoint | Notes |
|-----------|--------|----------|-------|
| List | GET | `/api/v3/requests` | `input_data` with `list_info` |
| Get | GET | `/api/v3/requests/{id}` | |
| Create | POST | `/api/v3/requests` | `requester` field required |
| Update | PUT | `/api/v3/requests/{id}` | |
| Delete | DELETE | `/api/v3/requests/{id}` | |
| Add Note | POST | `/api/v3/requests/{id}/notes` | `{"note":{"description":"..."}}` |
| Add Task | POST | `/api/v3/requests/{id}/tasks` | |
| Add Worklog | POST | `/api/v3/requests/{id}/worklogs` | |
| Add Attachment | POST | `/api/v3/requests/{id}/attachments` | multipart/form-data |
| Approve | PUT | `/api/v3/requests/{id}/approve` | |
| Reject | PUT | `/api/v3/requests/{id}/reject` | |

**Create request format:**
```json
{
  "request": {
    "subject": "Subject here",
    "description": "Description here",
    "requester": {"id": "4"},
    "priority": {"id": "3"},
    "category": {"id": "1"},
    "site": {"id": "304"},
    "group": {"id": "1"},
    "technician": {"id": "5"}
  }
}
```

### Problems (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/problems` |
| Get | GET | `/api/v3/problems/{id}` |
| Create | POST | `/api/v3/problems` |
| Update | PUT | `/api/v3/problems/{id}` |
| Delete | DELETE | `/api/v3/problems/{id}` |
| Add Note | POST | `/api/v3/problems/{id}/notes` |
| Add Task | POST | `/api/v3/problems/{id}/tasks` |
| Add Worklog | POST | `/api/v3/problems/{id}/worklogs` |

### Changes (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/changes` |
| Get | GET | `/api/v3/changes/{id}` |
| Create | POST | `/api/v3/changes` |
| Update | PUT | `/api/v3/changes/{id}` |
| Delete | DELETE | `/api/v3/changes/{id}` |
| Add Note | POST | `/api/v3/changes/{id}/notes` |
| Add Task | POST | `/api/v3/changes/{id}/tasks` |
| Add Worklog | POST | `/api/v3/changes/{id}/worklogs` |

### Projects (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/projects` |
| Get | GET | `/api/v3/projects/{id}` |
| Create | POST | `/api/v3/projects` |
| Update | PUT | `/api/v3/projects/{id}` |
| Delete | DELETE | `/api/v3/projects/{id}` |
| Members | CRUD | `/api/v3/projects/{id}/members` |
| Tasks | CRUD | `/api/v3/projects/{id}/tasks` |
| Milestones | CRUD | `/api/v3/projects/{id}/milestones` |
| Comments | CRUD | `/api/v3/projects/{id}/comments` |

### Releases (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/releases` |
| Get | GET | `/api/v3/releases/{id}` |
| Create | POST | `/api/v3/releases` |
| Update | PUT | `/api/v3/releases/{id}` |
| Delete | DELETE | `/api/v3/releases/{id}` |
| Notes | CRUD | `/api/v3/releases/{id}/notes` |
| Tasks | CRUD | `/api/v3/releases/{id}/tasks` |
| Worklogs | CRUD | `/api/v3/releases/{id}/worklogs` |

### Assets (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/assets` |
| Get | GET | `/api/v3/assets/{id}` |
| Create | POST | `/api/v3/assets` |
| Update | PUT | `/api/v3/assets/{id}` |
| Delete | DELETE | `/api/v3/assets/{id}` |

### Tasks (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/tasks` |
| Get | GET | `/api/v3/tasks/{id}` |
| Create | POST | `/api/v3/tasks` |
| Update | PUT | `/api/v3/tasks/{id}` |
| Delete | DELETE | `/api/v3/tasks/{id}` |

### CMDB (Read + CI CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List CIs | GET | `/api/v3/cmdb/{ci_type}` |
| Get CI | GET | `/api/v3/cmdb/{ci_type}/{id}` |
| Create CI | POST | `/api/v3/cmdb/{ci_type}` |
| Update CI | PUT | `/api/v3/cmdb/{ci_type}/{id}` |
| Delete CI | DELETE | `/api/v3/cmdb/{ci_type}/{id}` |
| CI Relationships | GET | `/api/v3/cmdb/relationships` |

### Contracts (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/contracts` |
| Get | GET | `/api/v3/contracts/{id}` |
| Create | POST | `/api/v3/contracts` |
| Update | PUT | `/api/v3/contracts/{id}` |
| Delete | DELETE | `/api/v3/contracts/{id}` |
| Types | GET | `/api/v3/contract_types` |
| Notes | CRUD | `/api/v3/contracts/{id}/notes` |

### Purchase Orders (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/purchase_orders` |
| Get | GET | `/api/v3/purchase_orders/{id}` |
| Create | POST | `/api/v3/purchase_orders` |
| Update | PUT | `/api/v3/purchase_orders/{id}` |
| Delete | DELETE | `/api/v3/purchase_orders/{id}` |
| Notes | CRUD | `/api/v3/purchase_orders/{id}/notes` |

### Vendors (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/vendors` |
| Get | GET | `/api/v3/vendors/{id}` |
| Create | POST | `/api/v3/vendors` |
| Update | PUT | `/api/v3/vendors/{id}` |
| Delete | DELETE | `/api/v3/vendors/{id}` |

### Solutions (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/solutions` |
| Get | GET | `/api/v3/solutions/{id}` |
| Create | POST | `/api/v3/solutions` |
| Update | PUT | `/api/v3/solutions/{id}` |
| Delete | DELETE | `/api/v3/solutions/{id}` |
| Topics | CRUD | `/api/v3/topics` |

### Space (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Campuses | CRUD | `/api/v3/campus` |
| Buildings | CRUD | `/api/v3/building` |
| Floors | CRUD | `/api/v3/floor` |
| Rooms | CRUD | `/api/v3/room` |

### Reference Data (Read Only ✅)

| Data | Method | Endpoint |
|------|--------|----------|
| Categories | GET | `/api/v3/categories` |
| Priorities | GET | `/api/v3/priorities` |
| Statuses | GET | `/api/v3/statuses` |
| Urgencies | GET | `/api/v3/urgencies` |
| Impacts | GET | `/api/v3/impacts` |
| Closure Codes | GET | `/api/v3/closure_codes` |
| Request Templates | GET | `/api/v3/request_templates` |

### Announcements (Full CRUD ✅)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v3/announcements` |
| Get | GET | `/api/v3/announcements/{id}` |
| Create | POST | `/api/v3/announcements` |
| Update | PUT | `/api/v3/announcements/{id}` |
| Delete | DELETE | `/api/v3/announcements/{id}` |

---

## Operations NOT in v3 API (Admin UI Only)

The following operations are **NOT available** through the v3 REST API. They require the Admin UI or legacy `/sdpapi/` endpoints:

| Operation | Reason |
|-----------|--------|
| User CRUD (create/update/delete) | `site` field is read-only; `role` cannot be set during creation |
| Technician CRUD | Same limitations as user CRUD |
| Group CRUD | POST/PUT return "Extra key found in JSON" |
| Site assignment to users | `site` field is read-only in v3 API |
| Group member management | Group creation not supported |
| Department CRUD | POST/PUT return "Invalid HTTP method" |
| Location CRUD | Endpoint returns 404 |
| Permission management | No endpoint available |
| Lock/Unlock users | No endpoint available |
| Activate/Deactivate users | No endpoint available |
| Reset password | No endpoint available |
| Convert user to technician | No endpoint available |
| Login history | No endpoint available |
| Activity log | No endpoint available |
| Bulk operations | No endpoint available |
| System settings | Read-only |
| Email settings | Read-only |
| Notification settings | Read-only |

---

## Your Real-World Scenarios

### Scenario 1: User can't see requests at a site

**Root cause:** User not assigned to the site.

**How site visibility works in SDP:**
1. Requests have a `site` field
2. Users need to be in a group that's associated with that site
3. OR users need the `Resources not in any site` role to see unassigned requests

**Via API:**
- ✅ Create request with site: `{"request": {"site": {"id": "304"}}}` → Works
- ✅ Get request with site info: `GET /api/v3/requests/{id}` → Returns `site` field
- ❌ Assign site to user: `site` field is read-only → **Must use Admin UI**

**Via Admin UI:**
1. Go to Admin → Users → Edit user
2. Set "Site" field
3. Save

### Scenario 2: Update group owner loses members

**Root cause:** Group creation/update via v3 API is not supported.

**How it works in SDP:**
1. Groups have a `group_head` (owner) and `members` list
2. When updating group via API, if `members` is not included, SDP may clear them
3. This is a known SDP behavior

**Via Admin UI:**
1. Go to Admin → User Groups → Edit group
2. Change group head
3. **IMPORTANT:** Verify members are still listed before saving
4. If members are lost, manually re-add them

**Prevention:**
- Always read the group first to get current members
- Include the full members list when updating the group head
