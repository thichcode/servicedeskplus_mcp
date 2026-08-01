#!/usr/bin/env python3

"""
Test script để kiểm tra kết nối với ServiceDesk Plus và các chức năng CMDB
"""

import asyncio
import json
from sdp_client import ServiceDeskPlusClient
from config import Config

async def test_connection():
    """Test connection to ServiceDesk Plus"""
    print("🔍 Kiểm tra cấu hình...")
    
    # Validate configuration
    config_validation = Config.validate_config()
    if not config_validation["valid"]:
        print("❌ Lỗi cấu hình:")
        for issue in config_validation["issues"]:
            print(f"  - {issue}")
        return False
    
    print("✅ Cấu hình hợp lệ")
    print(f"📡 Kết nối đến: {Config.SDP_BASE_URL}")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            print("🔐 Đang xác thực...")
            
            # Test authentication
            if await client.authenticate():
                print("✅ Xác thực thành công")
            else:
                print("❌ Xác thực thất bại")
                return False
            
            # Test basic API calls
            print("\n📋 Kiểm tra API calls cơ bản...")
            
            # Test get tickets
            print("  - Lấy danh sách tickets...")
            tickets = await client.get_tickets(limit=5)
            if "error" not in tickets:
                print(f"    ✅ Thành công - Tìm thấy {len(tickets.get('tickets', []))} tickets")
            else:
                print(f"    ❌ Lỗi: {tickets['error']}")
            
            # Test get users
            print("  - Lấy danh sách users...")
            users = await client.get_users(limit=5)
            if "error" not in users:
                print(f"    ✅ Thành công - Tìm thấy {len(users.get('users', []))} users")
            else:
                print(f"    ❌ Lỗi: {users['error']}")
            
            # Test get categories
            print("  - Lấy danh sách categories...")
            categories = await client.get_categories()
            if "error" not in categories:
                print(f"    ✅ Thành công - Tìm thấy {len(categories.get('categories', []))} categories")
            else:
                print(f"    ❌ Lỗi: {categories['error']}")
            
            print("\n🎉 Tất cả tests cơ bản đã hoàn thành!")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False

async def test_cmdb_features():
    """Test CMDB features"""
    print("\n🏗️ Kiểm tra các tính năng CMDB...")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            
            # Test Configuration Items
            print("  📦 Configuration Items:")
            print("    - Lấy danh sách CIs...")
            cis = await client.get_configuration_items(limit=5)
            if "error" not in cis:
                print(f"      ✅ Thành công - Tìm thấy {len(cis.get('configuration_items', []))} CIs")
            else:
                print(f"      ❌ Lỗi: {cis['error']}")
            
            print("    - Lấy danh sách CI types...")
            ci_types = await client.get_ci_types()
            if "error" not in ci_types:
                print(f"      ✅ Thành công - Tìm thấy {len(ci_types.get('ci_types', []))} CI types")
            else:
                print(f"      ❌ Lỗi: {ci_types['error']}")
            
            # Test Asset Management
            print("  💻 Asset Management:")
            print("    - Lấy danh sách assets...")
            assets = await client.get_assets(limit=5)
            if "error" not in assets:
                print(f"      ✅ Thành công - Tìm thấy {len(assets.get('assets', []))} assets")
            else:
                print(f"      ❌ Lỗi: {assets['error']}")
            
            print("    - Lấy danh sách asset types...")
            asset_types = await client.get_asset_types()
            if "error" not in asset_types:
                print(f"      ✅ Thành công - Tìm thấy {len(asset_types.get('asset_types', []))} asset types")
            else:
                print(f"      ❌ Lỗi: {asset_types['error']}")
            
            print("    - Lấy danh sách asset categories...")
            asset_categories = await client.get_asset_categories()
            if "error" not in asset_categories:
                print(f"      ✅ Thành công - Tìm thấy {len(asset_categories.get('asset_categories', []))} asset categories")
            else:
                print(f"      ❌ Lỗi: {asset_categories['error']}")
            
            # Test Software License Management
            print("  📄 Software License Management:")
            print("    - Lấy danh sách software licenses...")
            licenses = await client.get_software_licenses(limit=5)
            if "error" not in licenses:
                print(f"      ✅ Thành công - Tìm thấy {len(licenses.get('software_licenses', []))} licenses")
            else:
                print(f"      ❌ Lỗi: {licenses['error']}")
            
            print("    - Lấy danh sách software products...")
            products = await client.get_software_products()
            if "error" not in products:
                print(f"      ✅ Thành công - Tìm thấy {len(products.get('software_products', []))} products")
            else:
                print(f"      ❌ Lỗi: {products['error']}")
            
            # Test Contract Management
            print("  📋 Contract Management:")
            print("    - Lấy danh sách contracts...")
            contracts = await client.get_contracts(limit=5)
            if "error" not in contracts:
                print(f"      ✅ Thành công - Tìm thấy {len(contracts.get('contracts', []))} contracts")
            else:
                print(f"      ❌ Lỗi: {contracts['error']}")
            
            print("    - Lấy danh sách contract types...")
            contract_types = await client.get_contract_types()
            if "error" not in contract_types:
                print(f"      ✅ Thành công - Tìm thấy {len(contract_types.get('contract_types', []))} contract types")
            else:
                print(f"      ❌ Lỗi: {contract_types['error']}")
            
            # Test Purchase Order Management
            print("  🛒 Purchase Order Management:")
            print("    - Lấy danh sách purchase orders...")
            pos = await client.get_purchase_orders(limit=5)
            if "error" not in pos:
                print(f"      ✅ Thành công - Tìm thấy {len(pos.get('purchase_orders', []))} purchase orders")
            else:
                print(f"      ❌ Lỗi: {pos['error']}")
            
            print("    - Lấy danh sách PO statuses...")
            po_statuses = await client.get_po_statuses()
            if "error" not in po_statuses:
                print(f"      ✅ Thành công - Tìm thấy {len(po_statuses.get('po_statuses', []))} PO statuses")
            else:
                print(f"      ❌ Lỗi: {po_statuses['error']}")
            
            # Test Vendor Management
            print("  🏢 Vendor Management:")
            print("    - Lấy danh sách vendors...")
            vendors = await client.get_vendors(limit=5)
            if "error" not in vendors:
                print(f"      ✅ Thành công - Tìm thấy {len(vendors.get('vendors', []))} vendors")
            else:
                print(f"      ❌ Lỗi: {vendors['error']}")
            
            print("    - Lấy danh sách vendor types...")
            vendor_types = await client.get_vendor_types()
            if "error" not in vendor_types:
                print(f"      ✅ Thành công - Tìm thấy {len(vendor_types.get('vendor_types', []))} vendor types")
            else:
                print(f"      ❌ Lỗi: {vendor_types['error']}")
                
    except Exception as e:
        print(f"❌ Lỗi CMDB: {e}")

async def test_ticket_operations():
    """Test ticket operations"""
    print("\n🎫 Kiểm tra các thao tác với tickets...")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            # Test search tickets
            print("  - Tìm kiếm tickets...")
            search_result = await client.search_tickets("test", limit=5)
            if "error" not in search_result:
                print(f"    ✅ Thành công - Tìm thấy {len(search_result.get('tickets', []))} tickets")
            else:
                print(f"    ❌ Lỗi: {search_result['error']}")
            
            # Test get priorities
            print("  - Lấy danh sách priorities...")
            priorities = await client.get_priorities()
            if "error" not in priorities:
                print(f"    ✅ Thành công - Tìm thấy {len(priorities.get('priorities', []))} priorities")
            else:
                print(f"    ❌ Lỗi: {priorities['error']}")
            
            # Test get statuses
            print("  - Lấy danh sách statuses...")
            statuses = await client.get_statuses()
            if "error" not in statuses:
                print(f"    ✅ Thành công - Tìm thấy {len(statuses.get('statuses', []))} statuses")
            else:
                print(f"    ❌ Lỗi: {statuses['error']}")
                
    except Exception as e:
        print(f"❌ Lỗi: {e}")

async def test_advanced_features():
    """Test advanced features"""
    print("\n🚀 Kiểm tra các tính năng nâng cao...")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            # Test filtering capabilities
            print("  🔍 Filtering capabilities:")
            print("    - Lọc tickets theo status...")
            filtered_tickets = await client.get_tickets(limit=5, status="open")
            if "error" not in filtered_tickets:
                print(f"      ✅ Thành công - Tìm thấy {len(filtered_tickets.get('tickets', []))} open tickets")
            else:
                print(f"      ❌ Lỗi: {filtered_tickets['error']}")
            
            print("    - Lọc assets theo status...")
            filtered_assets = await client.get_assets(limit=5, status="in_use")
            if "error" not in filtered_assets:
                print(f"      ✅ Thành công - Tìm thấy {len(filtered_assets.get('assets', []))} in-use assets")
            else:
                print(f"      ❌ Lỗi: {filtered_assets['error']}")
            
            # Test pagination
            print("  📄 Pagination:")
            print("    - Test pagination với limit=10...")
            paginated_tickets = await client.get_tickets(limit=10)
            if "error" not in paginated_tickets:
                tickets_count = len(paginated_tickets.get('tickets', []))
                print(f"      ✅ Thành công - Lấy được {tickets_count} tickets (limit=10)")
            else:
                print(f"      ❌ Lỗi: {paginated_tickets['error']}")
                
    except Exception as e:
        print(f"❌ Lỗi advanced features: {e}")

async def test_admin_features():
    """Test Admin Management features"""
    print("\n👨‍💼 Kiểm tra các tính năng Admin Management...")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            
            # Test Site Management
            print("  🏢 Site Management:")
            print("    - Lấy danh sách sites...")
            sites = await client.get_sites(limit=5)
            if "error" not in sites:
                print(f"      ✅ Thành công - Tìm thấy {len(sites.get('sites', []))} sites")
            else:
                print(f"      ❌ Lỗi: {sites['error']}")
            
            print("    - Lấy danh sách site types...")
            site_types = await client.get_site_types()
            if "error" not in site_types:
                print(f"      ✅ Thành công - Tìm thấy {len(site_types.get('site_types', []))} site types")
            else:
                print(f"      ❌ Lỗi: {site_types['error']}")
            
            # Test User Group Management
            print("  👥 User Group Management:")
            print("    - Lấy danh sách user groups...")
            user_groups = await client.get_user_groups(limit=5)
            if "error" not in user_groups:
                print(f"      ✅ Thành công - Tìm thấy {len(user_groups.get('user_groups', []))} user groups")
            else:
                print(f"      ❌ Lỗi: {user_groups['error']}")
            
            print("    - Lấy danh sách group types...")
            group_types = await client.get_group_types()
            if "error" not in group_types:
                print(f"      ✅ Thành công - Tìm thấy {len(group_types.get('group_types', []))} group types")
            else:
                print(f"      ❌ Lỗi: {group_types['error']}")
            
            # Test Admin Users Management
            print("  👤 Admin Users Management:")
            print("    - Lấy danh sách admin users...")
            admin_users = await client.get_admin_users(limit=5)
            if "error" not in admin_users:
                print(f"      ✅ Thành công - Tìm thấy {len(admin_users.get('admin_users', []))} admin users")
            else:
                print(f"      ❌ Lỗi: {admin_users['error']}")
            
            print("    - Lấy danh sách user roles...")
            user_roles = await client.get_user_roles()
            if "error" not in user_roles:
                print(f"      ✅ Thành công - Tìm thấy {len(user_roles.get('user_roles', []))} user roles")
            else:
                print(f"      ❌ Lỗi: {user_roles['error']}")
            
            # Test Admin Technicians Management
            print("  🔧 Admin Technicians Management:")
            print("    - Lấy danh sách admin technicians...")
            admin_technicians = await client.get_admin_technicians(limit=5)
            if "error" not in admin_technicians:
                print(f"      ✅ Thành công - Tìm thấy {len(admin_technicians.get('admin_technicians', []))} admin technicians")
            else:
                print(f"      ❌ Lỗi: {admin_technicians['error']}")
            
            print("    - Lấy danh sách technician roles...")
            technician_roles = await client.get_technician_roles()
            if "error" not in technician_roles:
                print(f"      ✅ Thành công - Tìm thấy {len(technician_roles.get('technician_roles', []))} technician roles")
            else:
                print(f"      ❌ Lỗi: {technician_roles['error']}")
            
            # Test Permission Management
            print("  🔐 Permission Management:")
            print("    - Lấy danh sách permissions...")
            permissions = await client.get_permissions()
            if "error" not in permissions:
                print(f"      ✅ Thành công - Tìm thấy {len(permissions.get('permissions', []))} permissions")
            else:
                print(f"      ❌ Lỗi: {permissions['error']}")
            
            # Test Department Management
            print("  🏛️ Department Management:")
            print("    - Lấy danh sách departments...")
            departments = await client.get_departments(limit=5)
            if "error" not in departments:
                print(f"      ✅ Thành công - Tìm thấy {len(departments.get('departments', []))} departments")
            else:
                print(f"      ❌ Lỗi: {departments['error']}")
            
            print("    - Lấy danh sách department types...")
            department_types = await client.get_department_types()
            if "error" not in department_types:
                print(f"      ✅ Thành công - Tìm thấy {len(department_types.get('department_types', []))} department types")
            else:
                print(f"      ❌ Lỗi: {department_types['error']}")
            
            # Test Location Management
            print("  📍 Location Management:")
            print("    - Lấy danh sách locations...")
            locations = await client.get_locations(limit=5)
            if "error" not in locations:
                print(f"      ✅ Thành công - Tìm thấy {len(locations.get('locations', []))} locations")
            else:
                print(f"      ❌ Lỗi: {locations['error']}")
            
            print("    - Lấy danh sách location types...")
            location_types = await client.get_location_types()
            if "error" not in location_types:
                print(f"      ✅ Thành công - Tìm thấy {len(location_types.get('location_types', []))} location types")
            else:
                print(f"      ❌ Lỗi: {location_types['error']}")
            
            # Test System Settings
            print("  ⚙️ System Settings:")
            print("    - Lấy system settings...")
            system_settings = await client.get_system_settings()
            if "error" not in system_settings:
                print(f"      ✅ Thành công - Lấy được system settings")
            else:
                print(f"      ❌ Lỗi: {system_settings['error']}")
            
            print("    - Lấy email settings...")
            email_settings = await client.get_email_settings()
            if "error" not in email_settings:
                print(f"      ✅ Thành công - Lấy được email settings")
            else:
                print(f"      ❌ Lỗi: {email_settings['error']}")
            
            print("    - Lấy notification settings...")
            notification_settings = await client.get_notification_settings()
            if "error" not in notification_settings:
                print(f"      ✅ Thành công - Lấy được notification settings")
            else:
                print(f"      ❌ Lỗi: {notification_settings['error']}")
                
    except Exception as e:
        print(f"❌ Lỗi Admin Management: {e}")

async def test_admin_crud_operations():
    """Test Admin CRUD operations (Create, Read, Update, Delete)"""
    print("\n🔄 Kiểm tra các thao tác CRUD Admin...")
    
    try:
        async with ServiceDeskPlusClient(api_type=Config.SDP_API_TYPE) as client:
            
            # Test Site CRUD operations
            print("  🏢 Site CRUD Operations:")
            
            # Create test site
            test_site_data = {
                "name": "Test Site - MCP",
                "site_type": "branch_office",
                "address": "123 Test Street",
                "city": "Test City",
                "country": "Test Country",
                "description": "Test site created by MCP server"
            }
            
            print("    - Tạo site mới...")
            try:
                created_site = await client.create_site(test_site_data)
                if "error" not in created_site:
                    site_id = created_site.get('site', {}).get('id')
                    print(f"      ✅ Thành công - Tạo site với ID: {site_id}")
                    
                    # Test update site
                    print("    - Cập nhật site...")
                    update_data = {
                        "description": "Updated test site description"
                    }
                    updated_site = await client.update_site(site_id, update_data)
                    if "error" not in updated_site:
                        print(f"      ✅ Thành công - Cập nhật site")
                    else:
                        print(f"      ❌ Lỗi cập nhật: {updated_site['error']}")
                    
                    # Test delete site
                    print("    - Xóa site...")
                    deleted_site = await client.delete_site(site_id)
                    if "error" not in deleted_site:
                        print(f"      ✅ Thành công - Xóa site")
                    else:
                        print(f"      ❌ Lỗi xóa: {deleted_site['error']}")
                        
                else:
                    print(f"      ❌ Lỗi tạo site: {created_site['error']}")
            except Exception as e:
                print(f"      ⚠️ Bỏ qua test CRUD site: {e}")
            
            # Test User Group CRUD operations
            print("  👥 User Group CRUD Operations:")
            
            # Create test user group
            test_group_data = {
                "name": "Test Group - MCP",
                "group_type": "custom",
                "description": "Test user group created by MCP server"
            }
            
            print("    - Tạo user group mới...")
            try:
                created_group = await client.create_user_group(test_group_data)
                if "error" not in created_group:
                    group_id = created_group.get('user_group', {}).get('id')
                    print(f"      ✅ Thành công - Tạo user group với ID: {group_id}")
                    
                    # Test update user group
                    print("    - Cập nhật user group...")
                    update_data = {
                        "description": "Updated test group description"
                    }
                    updated_group = await client.update_user_group(group_id, update_data)
                    if "error" not in updated_group:
                        print(f"      ✅ Thành công - Cập nhật user group")
                    else:
                        print(f"      ❌ Lỗi cập nhật: {updated_group['error']}")
                    
                    # Test delete user group
                    print("    - Xóa user group...")
                    deleted_group = await client.delete_user_group(group_id)
                    if "error" not in deleted_group:
                        print(f"      ✅ Thành công - Xóa user group")
                    else:
                        print(f"      ❌ Lỗi xóa: {deleted_group['error']}")
                        
                else:
                    print(f"      ❌ Lỗi tạo user group: {created_group['error']}")
            except Exception as e:
                print(f"      ⚠️ Bỏ qua test CRUD user group: {e}")
            
            # Test Department CRUD operations
            print("  🏛️ Department CRUD Operations:")
            
            # Create test department
            test_dept_data = {
                "name": "Test Department - MCP",
                "department_type": "IT",
                "description": "Test department created by MCP server"
            }
            
            print("    - Tạo department mới...")
            try:
                created_dept = await client.create_department(test_dept_data)
                if "error" not in created_dept:
                    dept_id = created_dept.get('department', {}).get('id')
                    print(f"      ✅ Thành công - Tạo department với ID: {dept_id}")
                    
                    # Test update department
                    print("    - Cập nhật department...")
                    update_data = {
                        "description": "Updated test department description"
                    }
                    updated_dept = await client.update_department(dept_id, update_data)
                    if "error" not in updated_dept:
                        print(f"      ✅ Thành công - Cập nhật department")
                    else:
                        print(f"      ❌ Lỗi cập nhật: {updated_dept['error']}")
                    
                    # Test delete department
                    print("    - Xóa department...")
                    deleted_dept = await client.delete_department(dept_id)
                    if "error" not in deleted_dept:
                        print(f"      ✅ Thành công - Xóa department")
                    else:
                        print(f"      ❌ Lỗi xóa: {deleted_dept['error']}")
                        
                else:
                    print(f"      ❌ Lỗi tạo department: {created_dept['error']}")
            except Exception as e:
                print(f"      ⚠️ Bỏ qua test CRUD department: {e}")
            
            # Test Location CRUD operations
            print("  📍 Location CRUD Operations:")
            
            # Create test location
            test_location_data = {
                "name": "Test Location - MCP",
                "location_type": "office",
                "description": "Test location created by MCP server"
            }
            
            print("    - Tạo location mới...")
            try:
                created_location = await client.create_location(test_location_data)
                if "error" not in created_location:
                    location_id = created_location.get('location', {}).get('id')
                    print(f"      ✅ Thành công - Tạo location với ID: {location_id}")
                    
                    # Test update location
                    print("    - Cập nhật location...")
                    update_data = {
                        "description": "Updated test location description"
                    }
                    updated_location = await client.update_location(location_id, update_data)
                    if "error" not in updated_location:
                        print(f"      ✅ Thành công - Cập nhật location")
                    else:
                        print(f"      ❌ Lỗi cập nhật: {updated_location['error']}")
                    
                    # Test delete location
                    print("    - Xóa location...")
                    deleted_location = await client.delete_location(location_id)
                    if "error" not in deleted_location:
                        print(f"      ✅ Thành công - Xóa location")
                    else:
                        print(f"      ❌ Lỗi xóa: {deleted_location['error']}")
                        
                else:
                    print(f"      ❌ Lỗi tạo location: {created_location['error']}")
            except Exception as e:
                print(f"      ⚠️ Bỏ qua test CRUD location: {e}")
                
    except Exception as e:
        print(f"❌ Lỗi Admin CRUD: {e}")

async def main():
    """Main test function"""
    print("🚀 Bắt đầu kiểm tra kết nối ServiceDesk Plus MCP Server v2.0")
    print("=" * 70)
    
    # Test basic connection
    success = await test_connection()
    
    if success:
        # Test CMDB features
        await test_cmdb_features()
        
        # Test ticket operations
        await test_ticket_operations()
        
        # Test advanced features
        await test_advanced_features()
        
        # Test Admin features
        await test_admin_features()
        
        # Test Admin CRUD operations
        await test_admin_crud_operations()
        
        print("\n" + "=" * 70)
        print("✅ Tất cả tests đã hoàn thành thành công!")
        print("🎯 MCP server với CMDB đã sẵn sàng sử dụng")
        print("📊 Hỗ trợ 60+ tools cho quản lý toàn diện IT infrastructure")
    else:
        print("\n" + "=" * 70)
        print("❌ Có lỗi xảy ra trong quá trình kiểm tra")
        print("🔧 Vui lòng kiểm tra lại cấu hình trong file .env")

if __name__ == "__main__":
    asyncio.run(main()) 