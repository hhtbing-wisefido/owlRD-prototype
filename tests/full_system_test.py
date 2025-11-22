#!/usr/bin/env python3
"""
owlRD系统全自动测试脚本
测试所有API端点、数据完整性、功能可用性

运行方式：
    python scripts/full_system_test.py

注意：需要后端服务已启动在 http://localhost:8000
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_RESULTS = []
TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS = 0

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印测试标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_section(text: str):
    """打印测试章节"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}► {text}{Colors.END}")
    print(f"{Colors.YELLOW}{'-'*80}{Colors.END}")

def test_result(test_name: str, passed: bool, details: str = ""):
    """记录测试结果"""
    global TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS, TEST_RESULTS
    
    TOTAL_TESTS += 1
    if passed:
        PASSED_TESTS += 1
        status = f"{Colors.GREEN}✓ PASS{Colors.END}"
    else:
        FAILED_TESTS += 1
        status = f"{Colors.RED}✗ FAIL{Colors.END}"
    
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")
    
    TEST_RESULTS.append({
        'test': test_name,
        'passed': passed,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

def check_server_running() -> bool:
    """检查服务器是否运行"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_api_endpoint(
    method: str,
    endpoint: str,
    test_name: str,
    expected_status: int = 200,
    data: Dict = None,
    check_response: callable = None
) -> Tuple[bool, Dict]:
    """测试API端点"""
    try:
        url = f"{BASE_URL}{API_PREFIX}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            test_result(test_name, False, f"未知的HTTP方法: {method}")
            return False, {}
        
        # 检查状态码
        status_ok = response.status_code == expected_status
        
        # 尝试解析JSON
        try:
            response_data = response.json()
        except:
            response_data = {}
        
        # 额外的响应检查
        if check_response and status_ok:
            check_ok = check_response(response_data)
            if not check_ok:
                test_result(test_name, False, f"响应检查失败 | 状态码: {response.status_code}")
                return False, response_data
        
        if status_ok:
            test_result(test_name, True, f"状态码: {response.status_code}")
        else:
            test_result(test_name, False, f"期望状态码: {expected_status}, 实际: {response.status_code}")
        
        return status_ok, response_data
    
    except requests.exceptions.Timeout:
        test_result(test_name, False, "请求超时")
        return False, {}
    except requests.exceptions.ConnectionError:
        test_result(test_name, False, "连接失败 - 服务器未运行?")
        return False, {}
    except Exception as e:
        test_result(test_name, False, f"异常: {str(e)}")
        return False, {}

def test_health_endpoints():
    """测试健康检查端点"""
    print_section("健康检查端点测试")
    
    test_api_endpoint("GET", "/../health", "健康检查端点")
    test_api_endpoint("GET", "/../", "根路径")

def test_tenant_endpoints():
    """测试租户API"""
    print_section("租户管理API测试")
    
    # 获取租户列表
    passed, data = test_api_endpoint(
        "GET", "/tenants/",
        "获取租户列表",
        check_response=lambda r: isinstance(r, list)
    )
    
    # 创建租户
    new_tenant = {
        "tenant_name": "测试养老院",
        "contact_person": "张经理",
        "contact_email": "test@example.com",
        "contact_phone": "13800138000"
    }
    passed, created = test_api_endpoint(
        "POST", "/tenants/",
        "创建新租户",
        data=new_tenant,
        expected_status=201
    )
    
    if passed and created:
        tenant_id = created.get("tenant_id")
        # 获取单个租户
        test_api_endpoint(
            "GET", f"/tenants/{tenant_id}",
            f"获取租户详情 (ID: {tenant_id})"
        )

def test_user_role_endpoints():
    """测试用户和角色API"""
    print_section("用户和角色管理API测试")
    
    # 角色
    test_api_endpoint("GET", "/roles/", "获取角色列表")
    
    # 用户
    passed, users = test_api_endpoint(
        "GET", "/users/",
        "获取用户列表",
        check_response=lambda r: isinstance(r, list)
    )
    
    # 创建测试用户
    new_user = {
        "username": f"test_user_{datetime.now().timestamp()}",
        "email": "testuser@example.com",
        "full_name": "测试用户",
        "role_id": 1
    }
    test_api_endpoint(
        "POST", "/users/",
        "创建新用户",
        data=new_user,
        expected_status=201
    )

def test_location_endpoints():
    """测试位置管理API"""
    print_section("位置管理API测试")
    
    test_api_endpoint("GET", "/locations/", "获取位置列表")
    test_api_endpoint("GET", "/rooms/", "获取房间列表")
    test_api_endpoint("GET", "/beds/", "获取床位列表")
    
    # 创建测试位置
    new_location = {
        "location_name": "测试楼层",
        "location_type": "FACILITY",
        "is_public_area": False
    }
    passed, location = test_api_endpoint(
        "POST", "/locations/",
        "创建新位置",
        data=new_location,
        expected_status=201
    )

def test_resident_endpoints():
    """测试住户管理API"""
    print_section("住户管理API测试")
    
    passed, residents = test_api_endpoint(
        "GET", "/residents/",
        "获取住户列表",
        check_response=lambda r: isinstance(r, list)
    )
    
    # 创建测试住户
    new_resident = {
        "resident_account": f"R{int(datetime.now().timestamp())}",
        "anonymous_name": "测试住户",
        "admission_date": datetime.now().date().isoformat(),
        "resident_status": "ACTIVE"
    }
    passed, resident = test_api_endpoint(
        "POST", "/residents/",
        "创建新住户",
        data=new_resident,
        expected_status=201
    )
    
    if passed and residents:
        # 测试住户联系人
        test_api_endpoint("GET", "/resident-contacts/", "获取住户联系人列表")
        # 测试护理关联
        test_api_endpoint("GET", "/resident-caregivers/", "获取护理关联列表")

def test_device_endpoints():
    """测试设备管理API"""
    print_section("设备管理API测试")
    
    passed, devices = test_api_endpoint(
        "GET", "/devices/",
        "获取设备列表",
        check_response=lambda r: isinstance(r, list)
    )
    
    # 创建测试设备
    new_device = {
        "device_sn": f"TEST{int(datetime.now().timestamp())}",
        "device_type": "RADAR",
        "device_model": "RD-3000",
        "device_status": "ACTIVE"
    }
    test_api_endpoint(
        "POST", "/devices/",
        "创建新设备",
        data=new_device,
        expected_status=201
    )

def test_iot_data_endpoints():
    """测试IoT数据API"""
    print_section("IoT数据API测试")
    
    test_api_endpoint("GET", "/iot-data/", "获取IoT数据列表")
    test_api_endpoint("GET", "/iot-data/latest", "获取最新IoT数据")
    
    # 创建测试IoT数据
    new_iot_data = {
        "device_id": 1,
        "data_type": "PERSON_MATRIX",
        "data_value": {"test": "data"},
        "quality_score": 95.0
    }
    test_api_endpoint(
        "POST", "/iot-data/",
        "创建IoT数据",
        data=new_iot_data,
        expected_status=201
    )

def test_alert_endpoints():
    """测试告警API"""
    print_section("告警管理API测试")
    
    test_api_endpoint("GET", "/alerts/", "获取告警列表")
    test_api_endpoint("GET", "/alert-policies/", "获取告警策略列表")

def test_card_endpoints():
    """测试卡片API"""
    print_section("卡片管理API测试")
    
    test_api_endpoint("GET", "/cards/", "获取卡片列表")

def test_care_quality_endpoints():
    """测试护理质量API"""
    print_section("护理质量API测试")
    
    test_api_endpoint("GET", "/care-quality/reports", "获取护理质量报告")
    test_api_endpoint("GET", "/care-quality/trends", "获取护理质量趋势")

def test_standard_codes_endpoints():
    """测试标准编码API"""
    print_section("标准编码API测试")
    
    test_api_endpoint("GET", "/standard-codes/snomed", "获取SNOMED编码")
    test_api_endpoint("GET", "/standard-codes/loinc", "获取LOINC编码")

def test_api_documentation():
    """测试API文档端点"""
    print_section("API文档可访问性测试")
    
    try:
        # 测试本地Swagger
        response = requests.get(f"{BASE_URL}/docs-local", timeout=5)
        test_result("本地Swagger UI (/docs-local)", response.status_code == 200)
        
        # 测试国内CDN版本
        response = requests.get(f"{BASE_URL}/docs-cn", timeout=5)
        test_result("国内CDN Swagger (/docs-cn)", response.status_code == 200)
        
        # 测试OpenAPI规范
        response = requests.get(f"{BASE_URL}/api/openapi.json", timeout=5)
        test_result("OpenAPI规范 (/api/openapi.json)", 
                   response.status_code == 200 and 'openapi' in response.json())
        
    except Exception as e:
        test_result("API文档测试", False, f"异常: {str(e)}")

def test_data_integrity():
    """测试数据完整性"""
    print_section("数据完整性检查")
    
    # 检查示例数据是否存在
    endpoints_to_check = [
        ("/tenants/", "租户数据"),
        ("/roles/", "角色数据"),
        ("/users/", "用户数据"),
        ("/locations/", "位置数据"),
        ("/residents/", "住户数据"),
        ("/devices/", "设备数据"),
    ]
    
    for endpoint, name in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                has_data = isinstance(data, list) and len(data) > 0
                test_result(f"{name}存在性检查", has_data, 
                           f"找到 {len(data)} 条记录" if has_data else "无数据")
            else:
                test_result(f"{name}存在性检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            test_result(f"{name}存在性检查", False, f"异常: {str(e)}")

def generate_report():
    """生成测试报告"""
    print_header("测试报告")
    
    # 统计信息
    pass_rate = (PASSED_TESTS / TOTAL_TESTS * 100) if TOTAL_TESTS > 0 else 0
    
    print(f"\n{Colors.BOLD}测试统计:{Colors.END}")
    print(f"  总测试数: {TOTAL_TESTS}")
    print(f"  {Colors.GREEN}通过: {PASSED_TESTS}{Colors.END}")
    print(f"  {Colors.RED}失败: {FAILED_TESTS}{Colors.END}")
    print(f"  通过率: {pass_rate:.1f}%")
    
    # 失败的测试
    if FAILED_TESTS > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}失败的测试:{Colors.END}")
        for result in TEST_RESULTS:
            if not result['passed']:
                print(f"  ✗ {result['test']}")
                if result['details']:
                    print(f"    {result['details']}")
    
    # 保存JSON报告
    report_file = Path(__file__).parent.parent / "test_reports" / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': TOTAL_TESTS,
            'passed': PASSED_TESTS,
            'failed': FAILED_TESTS,
            'pass_rate': pass_rate
        },
        'tests': TEST_RESULTS
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.BLUE}详细报告已保存: {report_file}{Colors.END}")
    
    # 总结
    print(f"\n{Colors.BOLD}测试结论:{Colors.END}")
    if pass_rate == 100:
        print(f"{Colors.GREEN}✓ 所有测试通过！系统状态良好。{Colors.END}")
        return 0
    elif pass_rate >= 80:
        print(f"{Colors.YELLOW}⚠ 大部分测试通过，但有一些问题需要修复。{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}✗ 测试失败率较高，系统可能存在严重问题。{Colors.END}")
        return 2

def main():
    """主测试流程"""
    print_header("owlRD 系统全自动测试")
    
    print(f"{Colors.BOLD}测试配置:{Colors.END}")
    print(f"  后端地址: {BASE_URL}")
    print(f"  API前缀: {API_PREFIX}")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务器
    print(f"\n{Colors.BOLD}检查服务器状态...{Colors.END}")
    if not check_server_running():
        print(f"{Colors.RED}✗ 后端服务器未运行！{Colors.END}")
        print(f"\n请先启动后端服务器:")
        print(f"  cd backend")
        print(f"  python start_with_check.py")
        return 1
    
    print(f"{Colors.GREEN}✓ 后端服务器正在运行{Colors.END}")
    
    # 执行测试
    try:
        test_health_endpoints()
        test_api_documentation()
        test_tenant_endpoints()
        test_user_role_endpoints()
        test_location_endpoints()
        test_resident_endpoints()
        test_device_endpoints()
        test_iot_data_endpoints()
        test_alert_endpoints()
        test_card_endpoints()
        test_care_quality_endpoints()
        test_standard_codes_endpoints()
        test_data_integrity()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n\n{Colors.RED}测试过程中发生错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 生成报告
    return generate_report()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
