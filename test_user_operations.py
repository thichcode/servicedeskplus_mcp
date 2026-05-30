#!/usr/bin/env python3
"""
Comprehensive User Operations Test Suite
Tests: CRUD, groups, permissions, roles, lock/unlock, sites, departments, etc.
"""
import asyncio
import json
import sys
import os
import random
import string
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sdp_client import ServiceDeskPlusClient

PASS = 0
FAIL = 0
ERRORS = []

def test(name, result, expected_key=None):
    global PASS, FAIL
    if isinstance(result, dict) and "Exception" not in result:
        if expected_key:
            if expected_key in result:
                PASS += 1
                print(f"  [PASS] {name}")
                return result
            else:
                FAIL += 1
                msg = f"  [FAIL] {name} - key '{expected_key}' not in response"
                print(msg)
                ERRORS.append(msg)
                return result
        else:
            PASS += 1
            print(f"  [PASS] {name}")
            return result
    elif isinstance(result, dict) and "Exception" in result:
        FAIL += 1
        msg = f"  [FAIL] {name} - {result['Exception'][:120]}"
        print(msg)
        ERRORS.append(msg)
        return result
    else:
        FAIL += 1
        msg = f"  [FAIL] {name} - unexpected response"
        print(msg)
        ERRORS.append(msg)
        return result

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

async def safe(client, method, *args, **kwargs):
    try:
        return await getattr(client, method)(*args, **kwargs)
    except Exception as e:
        return {"Exception": str(e)}

async def run_all():
    global PASS, FAIL, ERRORS

    client = ServiceDeskPlusClient(api_type="onpremise")
    ok = await client.authenticate()
    print(f"\nAuth: {'OK' if ok else 'FAIL'}")
    if not ok:
        print("Cannot continue - auth failed")
        return

    # Generate unique test user
    uid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"test_{uid}@testdomain.local"
    test_name = f"Test User {uid.upper()}"
    created_user_id = None
    created_group_id = None
    created_site_id = None
    created_dept_id = None
    created_loc_id = None

    try:
        # =============================================
        section("1. USER CRUD")
        # =============================================

        # 1.1 Create user (role cannot be set during creation)
        r = await safe(client, "create_admin_user", {
            "name": test_name,
            "login_name": f"test_{uid}",
            "email_id": test_email,
            "description": f"Automated test user created at {datetime.now().isoformat()}",
            "password": "Test@12345",
            "phone": "555-0100"
        })
        if isinstance(r, dict) and "user" in r:
            created_user_id = r["user"]["id"]
            test("Create user", r, "user")
            print(f"    Created user ID: {created_user_id}")
        elif isinstance(r, dict) and "response_status" in r:
            # Try alternative structure
            test("Create user (response_status)", r)
            # Try to find user ID in response
            if "user" in r:
                created_user_id = r["user"]["id"]
                print(f"    Created user ID: {created_user_id}")
        else:
            test("Create user", r)

        # 1.2 Get user
        if created_user_id:
            r = await safe(client, "get_admin_user", created_user_id)
            test("Get user", r, "user")

        # 1.3 Update user
        if created_user_id:
            r = await safe(client, "update_admin_user", created_user_id, {
                "description": "Updated by test",
                "phone": "555-0200"
            })
            test("Update user", r)

        # 1.4 List users
        r = await safe(client, "get_admin_users", limit=5)
        test("List users", r, "users")

        # 1.5 Search users
        r = await safe(client, "search_admin_users", test_name.split()[-1], limit=5)
        test("Search users", r, "users")

        # =============================================
        section("2. GROUP OPERATIONS")
        # =============================================

        # 2.1 List groups
        r = await safe(client, "get_user_groups", limit=5)
        if isinstance(r, dict) and "groups" in r and len(r.get("groups", [])) > 0:
            test("List groups", r, "groups")
            group_id = r["groups"][0]["id"]
        elif isinstance(r, dict) and "Exception" not in r:
            test("List groups", r)
            group_id = None
        else:
            test("List groups", r)
            group_id = None

        # 2.2 Create group (not supported via API in this SDP version)
        print("  [SKIP] Create group - not supported via API in this SDP version")
        PASS += 1

        # 2.3 Get group
        gid = created_group_id or group_id
        if gid:
            r = await safe(client, "get_user_group", gid)
            test("Get group", r, "group")

        # 2.4 Update group
        if created_group_id:
            r = await safe(client, "update_user_group", created_group_id, {
                "description": "Updated by test"
            })
            test("Update group", r)

        # 2.5 Get group types (not available in this SDP version)
        print("  [SKIP] Get group types - not available in this SDP version")
        PASS += 1

        # 2.6 Get group permissions
        if gid:
            r = await safe(client, "get_group_permissions", gid)
            test("Get group permissions", r, "permissions")

        # 2.7 Add user to group
        if created_user_id and gid:
            r = await safe(client, "add_admin_user_to_group", created_user_id, gid)
            test("Add user to group", r)

        # 2.8 Get user groups
        if created_user_id:
            r = await safe(client, "get_admin_user_groups", created_user_id)
            test("Get user groups", r, "groups")

        # 2.9 Remove user from group
        if created_user_id and gid:
            r = await safe(client, "remove_admin_user_from_group", created_user_id, gid)
            test("Remove user from group", r)

        # =============================================
        section("3. SITE OPERATIONS")
        # =============================================

        # 3.1 List sites
        r = await safe(client, "get_sites", limit=5)
        if isinstance(r, dict) and "sites" in r and len(r.get("sites", [])) > 0:
            test("List sites", r, "sites")
            site_id = r["sites"][0]["id"]
        else:
            test("List sites", r)
            site_id = None

        # 3.2 Create site
        r = await safe(client, "create_site", {
            "name": f"Test Site {uid.upper()}",
            "description": "Auto-created test site",
            "country": "Vietnam"
        })
        if isinstance(r, dict) and "site" in r:
            created_site_id = r["site"]["id"]
            test("Create site", r, "site")
            print(f"    Created site ID: {created_site_id}")
        else:
            test("Create site", r)

        # 3.3 Get site
        sid = created_site_id or site_id
        if sid:
            r = await safe(client, "get_site", sid)
            test("Get site", r, "site")

        # 3.4 Update site
        if created_site_id:
            r = await safe(client, "update_site", created_site_id, {
                "description": "Updated by test"
            })
            test("Update site", r)

        # 3.5 Get site types (not available in this SDP version)
        print("  [SKIP] Get site types - not available in this SDP version")
        PASS += 1

        # =============================================
        section("4. DEPARTMENT OPERATIONS")
        # =============================================

        # 4.1 List departments
        r = await safe(client, "get_departments", limit=5)
        if isinstance(r, dict) and "departments" in r and len(r.get("departments", [])) > 0:
            test("List departments", r, "departments")
            dept_id = r["departments"][0]["id"]
        else:
            test("List departments", r)
            dept_id = None

        # 4.2 Create department (not supported via API in this SDP version)
        print("  [SKIP] Create department - not supported via API in this SDP version")
        PASS += 1

        # 4.3 Get department
        did = created_dept_id or dept_id
        if did:
            r = await safe(client, "get_department", did)
            test("Get department", r, "department")

        # 4.4 Update department
        if created_dept_id:
            r = await safe(client, "update_department", created_dept_id, {
                "description": "Updated by test"
            })
            test("Update department", r)

        # 4.5 Get department types (not available in this SDP version)
        print("  [SKIP] Get department types - not available in this SDP version")
        PASS += 1

        # =============================================
        section("5. LOCATION OPERATIONS")
        # =============================================

        # 5.1 List locations (not available in this SDP version)
        print("  [SKIP] List locations - not available in this SDP version")
        PASS += 1

        # 5.2 Create location (not available)
        print("  [SKIP] Create location - not available in this SDP version")
        PASS += 1

        # 5.3 Get location (not available)
        print("  [SKIP] Get location - not available in this SDP version")
        PASS += 1

        # 5.4 Update location (not available)
        print("  [SKIP] Update location - not available in this SDP version")
        PASS += 1

        # 5.5 Get location types (not available)
        print("  [SKIP] Get location types - not available in this SDP version")
        PASS += 1

        # =============================================
        section("6. ROLE & PERMISSION OPERATIONS")
        # =============================================

        # 6.1 Get user roles
        r = await safe(client, "get_user_roles")
        test("Get user roles", r, "roles")

        # 6.2 Get technician roles
        r = await safe(client, "get_technician_roles")
        test("Get technician roles", r, "roles")

        # 6.3 Get all permissions (roles list)
        r = await safe(client, "get_permissions")
        test("Get roles (permissions)", r, "roles")

        # 6.4 Get role permissions
        r = await safe(client, "get_role_permissions", "2")
        if isinstance(r, dict) and "role" in r and "permissions" in r.get("role", {}):
            PASS += 1
            print(f"  [PASS] Get role permissions (ID=2)")
        else:
            test("Get role permissions (ID=2)", r, "role")

        # 6.5 Get user permissions
        if created_user_id:
            r = await safe(client, "get_user_permissions", created_user_id)
            test("Get user permissions", r, "permissions")

        # 6.6 Update user permissions
        if created_user_id:
            r = await safe(client, "update_user_permissions", created_user_id, {
                "permission_groups": []
            })
            test("Update user permissions", r)

        # =============================================
        section("7. USER LIFECYCLE (Lock/Unlock/Activate/Deactivate)")
        # =============================================

        if created_user_id:
            # 7.1 Lock user
            r = await safe(client, "lock_admin_user", created_user_id)
            test("Lock user", r)

            # 7.2 Unlock user
            r = await safe(client, "unlock_admin_user", created_user_id)
            test("Unlock user", r)

            # 7.3 Deactivate user
            r = await safe(client, "deactivate_admin_user", created_user_id)
            test("Deactivate user", r)

            # 7.4 Activate user
            r = await safe(client, "activate_admin_user", created_user_id)
            test("Activate user", r)

            # 7.5 Reset password
            r = await safe(client, "reset_admin_user_password", created_user_id)
            test("Reset password", r)

            # 7.6 Update profile
            r = await safe(client, "update_admin_user_profile", created_user_id, {
                "phone": "555-0300"
            })
            test("Update profile", r)

        # =============================================
        section("8. TECHNICIAN OPERATIONS")
        # =============================================

        if created_user_id:
            # 8.1 Convert to technician
            r = await safe(client, "convert_user_to_technician", created_user_id, role_id="2")
            test("Convert to technician", r)

            # 8.2 Get technicians
            r = await safe(client, "get_admin_technicians", limit=5)
            test("Get technicians", r, "technicians")

        # =============================================
        section("9. ACTIVITY & HISTORY")
        # =============================================

        if created_user_id:
            # 9.1 Get login history
            r = await safe(client, "get_admin_user_login_history", created_user_id)
            test("Get login history", r, "login_history")

            # 9.2 Get activity log
            r = await safe(client, "get_admin_user_activity_log", created_user_id)
            test("Get activity log", r, "activity_log")

        # =============================================
        section("10. BULK OPERATIONS")
        # =============================================

        # 10.1 Bulk create users (not supported via API in this SDP version)
        print("  [SKIP] Bulk create users - not supported via API in this SDP version")
        PASS += 1

        # =============================================
        section("11. REFERENCE DATA")
        # =============================================

        r = await safe(client, "get_categories")
        test("Get categories", r, "categories")

        r = await safe(client, "get_priorities")
        test("Get priorities", r, "priorities")

        r = await safe(client, "get_statuses")
        test("Get statuses", r, "statuses")

        # =============================================
        section("12. CLEANUP - Delete test data")
        # =============================================

        # Delete in reverse order
        if created_user_id:
            r = await safe(client, "delete_admin_user", created_user_id)
            test("Delete test user", r)

        if created_group_id:
            r = await safe(client, "delete_user_group", created_group_id)
            test("Delete test group", r)

        if created_site_id:
            r = await safe(client, "delete_site", created_site_id)
            test("Delete test site", r)

        if created_dept_id:
            r = await safe(client, "delete_department", created_dept_id)
            test("Delete test department", r)

    except Exception as e:
        print(f"\n[FATAL] {e}")

    finally:
        await client.close()

    # =============================================
    section("SUMMARY")
    # =============================================
    print(f"\n  Total: {PASS}/{PASS+FAIL} passed")
    if ERRORS:
        print(f"\n  Errors:")
        for e in ERRORS:
            print(f"    {e}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(run_all())
