#!/usr/bin/env python3
"""
完整CRUD功能测试脚本
测试所有5个资源的CRUD操作（共20个测试）
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
TENANT_ID = "10000000-0000-0000-0000-000000000001"

# 测试结果统计
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "details": []
}

def log_test(resource: str, operation: str, success: bool, message: str = ""):
    """记录测试结果"""
    results["total"] += 1
    if success:
        results["passed"] += 1
        status = "✅ PASS"
    else:
        results["failed"] += 1
        status = "❌ FAIL"
    
    result = {
        "resource": resource,
        "operation": operation,
        "status": status,
        "message": message
    }
    results["details"].append(result)
    print(f"{status} | {resource:12} | {operation:8} | {message}")

def test_users():
    """测试Users CRUD"""
    resource = "Users"
    
    # CREATE
    try:
        user_data = {
            "tenant_id": TENANT_ID,
            "username": "test_user",
            "password": "Test123456",
            "email": "test@example.com",
            "role": "Director",  # 使用系统预置角色
            "status": "active"
        }
        response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
        if response.status_code in [200, 201]:
            user_id = response.json().get("user_id")
            log_test(resource, "CREATE", True, f"Created user_id: {user_id[:8]}...")
        else:
            log_test(resource, "CREATE", False, f"Status: {response.status_code}, Detail: {response.text[:100]}")
    except Exception as e:
        log_test(resource, "CREATE", False, str(e))
    
    # READ
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/?tenant_id={TENANT_ID}")
        if response.status_code == 200:
            users = response.json()
            log_test(resource, "READ", True, f"Found {len(users)} users")
        else:
            log_test(resource, "READ", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "READ", False, str(e))
    
    # UPDATE
    try:
        if 'user_id' in locals():
            update_data = {"email": "updated@example.com"}
            response = requests.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data)
            if response.status_code == 200:
                log_test(resource, "UPDATE", True, "Email updated")
            else:
                log_test(resource, "UPDATE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "UPDATE", False, "No user_id available")
    except Exception as e:
        log_test(resource, "UPDATE", False, str(e))
    
    # DELETE
    try:
        if 'user_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
            if response.status_code == 200:
                log_test(resource, "DELETE", True, "User deleted")
            else:
                log_test(resource, "DELETE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "DELETE", False, "No user_id available")
    except Exception as e:
        log_test(resource, "DELETE", False, str(e))

def test_roles():
    """测试Roles CRUD"""
    resource = "Roles"
    
    # CREATE
    try:
        role_data = {
            "tenant_id": TENANT_ID,
            "role_name": "test_role",
            "role_code": "TEST_ROLE",
            "description": "Test role for CRUD testing",
            "permissions": {"read": True, "write": False}
        }
        response = requests.post(f"{BASE_URL}/api/v1/roles/", json=role_data)
        if response.status_code == 200:
            role_id = response.json().get("role_id")
            log_test(resource, "CREATE", True, f"Created role_id: {role_id[:8]}...")
        else:
            log_test(resource, "CREATE", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "CREATE", False, str(e))
    
    # READ
    try:
        response = requests.get(f"{BASE_URL}/api/v1/roles/?tenant_id={TENANT_ID}")
        if response.status_code == 200:
            roles = response.json()
            log_test(resource, "READ", True, f"Found {len(roles)} roles")
        else:
            log_test(resource, "READ", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "READ", False, str(e))
    
    # UPDATE
    try:
        if 'role_id' in locals():
            update_data = {"description": "Updated description"}
            response = requests.put(f"{BASE_URL}/api/v1/roles/{role_id}", json=update_data)
            if response.status_code == 200:
                log_test(resource, "UPDATE", True, "Description updated")
            else:
                log_test(resource, "UPDATE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "UPDATE", False, "No role_id available")
    except Exception as e:
        log_test(resource, "UPDATE", False, str(e))
    
    # DELETE
    try:
        if 'role_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/v1/roles/{role_id}")
            if response.status_code == 200:
                log_test(resource, "DELETE", True, "Role deleted")
            else:
                log_test(resource, "DELETE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "DELETE", False, "No role_id available")
    except Exception as e:
        log_test(resource, "DELETE", False, str(e))

def test_locations():
    """测试Locations CRUD"""
    resource = "Locations"
    
    # CREATE
    try:
        location_data = {
            "tenant_id": TENANT_ID,
            "location_tag": "TEST-001",
            "location_name": "Test Room",
            "location_type": "BEDROOM",
            "is_public_space": False
        }
        response = requests.post(f"{BASE_URL}/api/v1/locations/", json=location_data)
        if response.status_code == 200:
            location_id = response.json().get("location_id")
            log_test(resource, "CREATE", True, f"Created location_id: {location_id[:8]}...")
        else:
            log_test(resource, "CREATE", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "CREATE", False, str(e))
    
    # READ
    try:
        response = requests.get(f"{BASE_URL}/api/v1/locations/?tenant_id={TENANT_ID}")
        if response.status_code == 200:
            locations = response.json()
            log_test(resource, "READ", True, f"Found {len(locations)} locations")
        else:
            log_test(resource, "READ", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "READ", False, str(e))
    
    # UPDATE
    try:
        if 'location_id' in locals():
            update_data = {"location_name": "Updated Room"}
            response = requests.put(f"{BASE_URL}/api/v1/locations/{location_id}", json=update_data)
            if response.status_code == 200:
                log_test(resource, "UPDATE", True, "Name updated")
            else:
                log_test(resource, "UPDATE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "UPDATE", False, "No location_id available")
    except Exception as e:
        log_test(resource, "UPDATE", False, str(e))
    
    # DELETE
    try:
        if 'location_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/v1/locations/{location_id}")
            if response.status_code == 200:
                log_test(resource, "DELETE", True, "Location deleted")
            else:
                log_test(resource, "DELETE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "DELETE", False, "No location_id available")
    except Exception as e:
        log_test(resource, "DELETE", False, str(e))

def test_devices():
    """测试Devices CRUD"""
    resource = "Devices"
    
    # CREATE
    try:
        device_data = {
            "tenant_id": TENANT_ID,
            "device_name": "Test Device",
            "device_type": "RADAR",
            "device_model": "V1.0",
            "status": "online"
        }
        response = requests.post(f"{BASE_URL}/api/v1/devices/", json=device_data)
        if response.status_code == 200:
            device_id = response.json().get("device_id")
            log_test(resource, "CREATE", True, f"Created device_id: {device_id[:8]}...")
        else:
            log_test(resource, "CREATE", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "CREATE", False, str(e))
    
    # READ
    try:
        response = requests.get(f"{BASE_URL}/api/v1/devices/?tenant_id={TENANT_ID}")
        if response.status_code == 200:
            devices = response.json()
            log_test(resource, "READ", True, f"Found {len(devices)} devices")
        else:
            log_test(resource, "READ", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "READ", False, str(e))
    
    # UPDATE
    try:
        if 'device_id' in locals():
            update_data = {"status": "offline"}
            response = requests.put(f"{BASE_URL}/api/v1/devices/{device_id}", json=update_data)
            if response.status_code == 200:
                log_test(resource, "UPDATE", True, "Status updated")
            else:
                log_test(resource, "UPDATE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "UPDATE", False, "No device_id available")
    except Exception as e:
        log_test(resource, "UPDATE", False, str(e))
    
    # DELETE
    try:
        if 'device_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/v1/devices/{device_id}")
            if response.status_code == 200:
                log_test(resource, "DELETE", True, "Device deleted")
            else:
                log_test(resource, "DELETE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "DELETE", False, "No device_id available")
    except Exception as e:
        log_test(resource, "DELETE", False, str(e))

def test_residents():
    """测试Residents CRUD"""
    resource = "Residents"
    
    # CREATE
    try:
        resident_data = {
            "tenant_id": TENANT_ID,
            "last_name": "测试",
            "resident_account": "TEST001",
            "status": "active",
            "admission_date": datetime.now().isoformat()
        }
        response = requests.post(f"{BASE_URL}/api/v1/residents/", json=resident_data)
        if response.status_code == 200:
            resident_id = response.json().get("resident_id")
            log_test(resource, "CREATE", True, f"Created resident_id: {resident_id[:8]}...")
        else:
            log_test(resource, "CREATE", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "CREATE", False, str(e))
    
    # READ
    try:
        response = requests.get(f"{BASE_URL}/api/v1/residents/?tenant_id={TENANT_ID}")
        if response.status_code == 200:
            residents = response.json()
            log_test(resource, "READ", True, f"Found {len(residents)} residents")
        else:
            log_test(resource, "READ", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(resource, "READ", False, str(e))
    
    # UPDATE
    try:
        if 'resident_id' in locals():
            update_data = {"status": "discharged"}
            response = requests.put(f"{BASE_URL}/api/v1/residents/{resident_id}", json=update_data)
            if response.status_code == 200:
                log_test(resource, "UPDATE", True, "Status updated")
            else:
                log_test(resource, "UPDATE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "UPDATE", False, "No resident_id available")
    except Exception as e:
        log_test(resource, "UPDATE", False, str(e))
    
    # DELETE
    try:
        if 'resident_id' in locals():
            response = requests.delete(f"{BASE_URL}/api/v1/residents/{resident_id}")
            if response.status_code == 200:
                log_test(resource, "DELETE", True, "Resident deleted")
            else:
                log_test(resource, "DELETE", False, f"Status: {response.status_code}")
        else:
            log_test(resource, "DELETE", False, "No resident_id available")
    except Exception as e:
        log_test(resource, "DELETE", False, str(e))

def main():
    """主测试函数"""
    print("=" * 80)
    print("完整CRUD功能测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # 执行所有测试
    test_users()
    test_roles()
    test_locations()
    test_devices()
    test_residents()
    
    # 输出结果
    print()
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print()
    
    # 保存详细报告
    report_file = f"crud_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"详细报告已保存到: {report_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
