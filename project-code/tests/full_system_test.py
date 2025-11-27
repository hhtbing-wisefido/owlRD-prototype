#!/usr/bin/env python3
"""
owlRD完整系统测试脚本
测试后端API、前端编译、数据完整性、功能可用性

对齐源参考：
- 所有db/*.sql文件定义的表结构
- models/*.py的数据模型
- TDPv2-0916.md和25_Alarm_Notification_Flow.md的告警协议
- 告警级别使用L1/L2/L3/L5/L8/L9/DISABLE
- 告警时间字段使用timestamp

运行方式：
    # 交互式菜单
    python tests/full_system_test.py
    
    # 命令行参数
    python tests/full_system_test.py --all              # 运行所有测试
    python tests/full_system_test.py --backend          # 只测试后端API
    python tests/full_system_test.py --frontend         # 只测试前端编译
    python tests/full_system_test.py --api health       # 测试特定API分组
    python tests/full_system_test.py --list             # 列出所有测试
    python tests/full_system_test.py --report           # 查看最新测试报告

注意：
- 后端测试需要后端服务启动在 http://localhost:8000
- 前端测试需要Node.js环境
"""

import requests
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
import os
import time
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
DEFAULT_TENANT_ID = None  # 将在运行时获取
TEST_RESULTS = []
TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS = 0
BACKEND_PROCESS = None  # 追踪自动启动的后端进程

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
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

def auto_start_backend() -> Optional[subprocess.Popen]:
    """自动启动后端服务
    
    Returns:
        subprocess.Popen: 后端进程对象，如果启动失败返回None
    """
    print(f"\n{Colors.YELLOW}正在启动后端服务...{Colors.END}")
    
    # 确定后端目录路径
    tests_dir = Path(__file__).parent
    backend_dir = tests_dir.parent / 'backend'
    
    if not backend_dir.exists():
        print(f"{Colors.RED}✗ 找不到backend目录: {backend_dir}{Colors.END}")
        return None
    
    try:
        # 启动后端服务（允许交互）
        # 注意：不捕获stdout/stderr，让start_with_check.py的交互式询问能正常工作
        process = subprocess.Popen(
            [sys.executable, 'start_with_check.py'],
            cwd=str(backend_dir)
        )
        
        # 等待服务就绪（最多60秒，因为可能需要用户交互）
        print(f"{Colors.CYAN}等待后端服务就绪（如有端口占用提示请回答）...{Colors.END}")
        for i in range(60):
            time.sleep(1)
            
            if check_server_running():
                print(f"{Colors.GREEN}✓ 后端服务启动成功 ({BASE_URL}){Colors.END}")
                return process
            
            # 检查进程是否异常退出
            if process.poll() is not None:
                print(f"\n{Colors.RED}✗ 后端服务启动失败（进程已退出）{Colors.END}")
                return None
        
        print(f"\n{Colors.RED}✗ 后端服务启动超时（60秒）{Colors.END}")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"\n{Colors.RED}✗ 启动后端服务时出错: {e}{Colors.END}")
        return None

def cleanup_backend_service():
    """清理自动启动的后端服务"""
    global BACKEND_PROCESS
    
    if BACKEND_PROCESS is None:
        return
    
    try:
        print(f"\n{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
        response = input(f"{Colors.YELLOW}测试完成。是否关闭自动启动的后端服务？(Y/n): {Colors.END}").strip()
        
        if response.lower() in ['y', 'yes', '']:
            print(f"{Colors.CYAN}正在关闭后端服务...{Colors.END}")
            BACKEND_PROCESS.terminate()
            
            # 等待进程结束（最多5秒）
            try:
                BACKEND_PROCESS.wait(timeout=5)
                print(f"{Colors.GREEN}✓ 后端服务已关闭{Colors.END}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.YELLOW}⚠ 正常关闭超时，强制终止...{Colors.END}")
                BACKEND_PROCESS.kill()
                BACKEND_PROCESS.wait()
                print(f"{Colors.GREEN}✓ 后端服务已强制终止{Colors.END}")
        else:
            print(f"{Colors.CYAN}后端服务保持运行中{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.RED}清理后端服务时出错: {e}{Colors.END}")
    finally:
        BACKEND_PROCESS = None

def test_api_endpoint(
    method: str,
    endpoint: str,
    test_name: str,
    expected_status: int = 200,
    data: Dict = None,
    check_response: callable = None,
    params: Dict = None,
    use_api_prefix: bool = True
) -> Tuple[bool, Dict]:
    """测试API端点"""
    try:
        if use_api_prefix:
            url = f"{BASE_URL}{API_PREFIX}{endpoint}"
        else:
            url = f"{BASE_URL}{endpoint}"
        
        # 添加默认的tenant_id参数（如果需要）
        if params is None:
            params = {}
        if 'tenant_id' not in params and method == "GET":
            params['tenant_id'] = DEFAULT_TENANT_ID
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, params=params, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, params=params, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, timeout=10)
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
    
    test_api_endpoint("GET", "/health", "健康检查端点", use_api_prefix=False, params={})
    test_api_endpoint("GET", "/", "根路径", use_api_prefix=False, params={})

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
        # 注：跳过删除租户测试，因为租户有关联数据（用户、位置、住户等）
        # 删除租户需要级联删除，这是复杂的业务逻辑，不适合在基础测试中进行

def test_user_role_endpoints():
    """测试用户和角色API"""
    print_section("用户和角色管理API测试")
    
    # 角色（注意：没有斜杠）
    test_api_endpoint("GET", "/roles", "获取角色列表", params={})
    
    # 用户
    passed, users = test_api_endpoint(
        "GET", "/users/",
        "获取用户列表",
        check_response=lambda r: isinstance(r, list)
    )
    
    # 创建测试用户
    timestamp = int(datetime.now().timestamp())
    new_user = {
        "username": f"test_user_{timestamp}",
        "email": f"testuser{timestamp}@example.com",  # 使用唯一email
        "full_name": "测试用户",
        "role": "Nurse",
        "tenant_id": DEFAULT_TENANT_ID,
        "password": "TestPass123"
    }
    passed, created_user = test_api_endpoint(
        "POST", "/users/",
        "创建新用户",
        data=new_user,
        expected_status=201,
        params={}
    )
    
    if passed and created_user:
        user_id = created_user.get("user_id")
        # 删除用户
        test_api_endpoint(
            "DELETE", f"/users/{user_id}",
            f"删除用户 (ID: {user_id})",
            expected_status=200
        )

def test_location_endpoints():
    """测试位置管理API"""
    print_section("位置管理API测试")
    
    test_api_endpoint("GET", "/locations/", "获取位置列表")
    # 注意：Room和Bed API可能在Location下或单独端点
    # 暂时跳过，因为没有找到独立的rooms/beds端点
    
    # 创建测试位置
    new_location = {
        "location_name": "测试楼层",
        "location_type": "Institutional",  # 只能是Institutional或HomeCare
        "door_number": "TEST-301",  # 必需字段
        "is_public_area": False,
        "tenant_id": DEFAULT_TENANT_ID,
        "timezone": "Asia/Shanghai"
    }
    passed, location = test_api_endpoint(
        "POST", "/locations/",
        "创建新位置",
        data=new_location,
        expected_status=201,
        params={}
    )
    
    if passed and location:
        location_id = location.get("location_id")
        # 删除位置（204 No Content也是成功）
        test_api_endpoint(
            "DELETE", f"/locations/{location_id}",
            f"删除位置 (ID: {location_id})",
            expected_status=204
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
        "last_name": "测试住户",  # 必需字段
        "admission_date": datetime.now().date().isoformat(),
        "resident_status": "ACTIVE",
        "tenant_id": DEFAULT_TENANT_ID,
        "gender": "Male",
        "birth_year": 1940,
        "is_institutional": True  # 必需字段
    }
    passed, resident = test_api_endpoint(
        "POST", "/residents/",
        "创建新住户",
        data=new_resident,
        expected_status=201,
        params={}
    )
    
    if passed and resident:
        resident_id = resident.get("resident_id")
        # 删除住户
        test_api_endpoint(
            "DELETE", f"/residents/{resident_id}",
            f"删除住户 (ID: {resident_id})",
            expected_status=200
        )
    
    if passed and residents:
        # 测试住户联系人（注意：没有斜杠）
        test_api_endpoint("GET", "/resident_contacts", "获取住户联系人列表", params={})
        # 测试护理关联（注意：没有斜杠）
        test_api_endpoint("GET", "/resident_caregivers", "获取护理关联列表", params={})

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
        "device_name": "测试雷达设备",
        "device_type": "Radar",
        "device_model": "RD-3000",
        "manufacturer": "TestMfg",
        "comm_mode": "WiFi",
        "firmware_version": "1.0.0",
        "status": "online",  # 必须是online/offline/error/dormant/maintenance之一
        "installation_date_utc": datetime.now().isoformat(),
        "tenant_id": DEFAULT_TENANT_ID
    }
    passed, device = test_api_endpoint(
        "POST", "/devices/",
        "创建新设备",
        data=new_device,
        expected_status=201,
        params={}
    )
    
    if passed and device:
        device_id = device.get("device_id")
        # 删除设备
        test_api_endpoint(
            "DELETE", f"/devices/{device_id}",
            f"删除设备 (ID: {device_id})",
            expected_status=200
        )

def test_iot_data_endpoints():
    """测试IoT数据API"""
    print_section("IoT数据API测试")
    
    # IoT数据查询（使用query端点）
    test_api_endpoint("GET", "/iot-data/query", "查询IoT数据", params={'limit': 10})
    # 统计信息
    test_api_endpoint("GET", "/iot-data/statistics", "获取IoT数据统计")

def test_alert_endpoints():
    """测试告警API"""
    print_section("告警管理API测试")
    
    test_api_endpoint("GET", "/alerts/", "获取告警列表")
    test_api_endpoint("GET", "/alerts/statistics/summary", "获取告警统计", params={})
    test_api_endpoint("GET", "/alert-policies/", "获取告警策略列表", params={})

def test_card_endpoints():
    """测试卡片API"""
    print_section("卡片管理API测试")
    
    test_api_endpoint("GET", "/cards/", "获取卡片列表", params={'tenant_id': DEFAULT_TENANT_ID})

def test_care_quality_endpoints():
    """测试护理质量API"""
    print_section("护理质量API测试")
    
    test_api_endpoint("GET", "/care-quality/report", "获取护理质量报告", params={'tenant_id': DEFAULT_TENANT_ID})
    test_api_endpoint("GET", "/care-quality/quality-score", "获取质量评分", params={'tenant_id': DEFAULT_TENANT_ID})
    # spatial-coverage需要location_id，暂时跳过
    # test_api_endpoint("GET", "/care-quality/spatial-coverage", "获取空间覆盖", params={'tenant_id': DEFAULT_TENANT_ID, 'location_id': '40000000-0000-0000-0000-000000000001'})

def test_standard_codes_endpoints():
    """测试标准编码API"""
    print_section("标准编码API测试")
    
    # 注意：如果这些端点不存在，可以跳过
    # test_api_endpoint("GET", "/standard-codes/snomed", "获取SNOMED编码")
    # test_api_endpoint("GET", "/standard-codes/loinc", "获取LOINC编码")
    pass  # 跳过，因为API可能未实现

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
        ("/tenants/", "租户数据", {}),
        ("/roles", "角色数据", {'tenant_id': DEFAULT_TENANT_ID}),
        ("/users/", "用户数据", {'tenant_id': DEFAULT_TENANT_ID}),
        ("/locations/", "位置数据", {'tenant_id': DEFAULT_TENANT_ID}),
        ("/residents/", "住户数据", {'tenant_id': DEFAULT_TENANT_ID}),
        ("/devices/", "设备数据", {'tenant_id': DEFAULT_TENANT_ID}),
    ]
    
    for endpoint, name, params in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{API_PREFIX}{endpoint}", params=params, timeout=5)
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
    
    # 保存JSON报告到tests/test_reports/
    report_file = Path(__file__).parent / "test_reports" / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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

def get_default_tenant_id() -> str:
    """获取默认租户ID - 直接使用init_sample_data.py的固定ID"""
    global DEFAULT_TENANT_ID
    return "10000000-0000-0000-0000-000000000001"


# ============================================================================
# 前端测试辅助函数
# ============================================================================

def check_nodejs_installed():
    """检查Node.js和npm是否安装"""
    try:
        # Windows下需要使用shell=True和正确的编码
        node_result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # 忽略编码错误
            timeout=5,
            shell=True
        )
        npm_result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5,
            shell=True
        )
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            node_ver = node_result.stdout.strip()
            npm_ver = npm_result.stdout.strip()
            return True, f"Node.js {node_ver}, npm {npm_ver}"
        return False, "Node.js或npm未正确安装"
    except FileNotFoundError:
        return False, "Node.js未安装"
    except Exception as e:
        return False, f"检查失败: {str(e)}"


# ============================================================================
# 前端构建测试
# ============================================================================

def test_frontend_build():
    """测试前端TypeScript编译和构建"""
    print_section("前端编译测试")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # 检查前端目录
    if not frontend_dir.exists():
        test_result("前端目录检查", False, "frontend目录不存在")
        return
    test_result("前端目录检查", True)
    
    # 检查Node.js环境
    node_installed, node_info = check_nodejs_installed()
    if not node_installed:
        test_result("Node.js环境检查", False, node_info)
        print(f"{Colors.YELLOW}  建议: 安装Node.js https://nodejs.org/{Colors.END}")
        return
    test_result("Node.js环境检查", True, node_info)
    
    # 检查package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        test_result("package.json检查", False)
        return
    test_result("package.json检查", True)
    
    # 检查node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        test_result("依赖安装检查", False, "node_modules不存在")
        print(f"{Colors.YELLOW}  建议: cd frontend && npm install{Colors.END}")
        return
    test_result("依赖安装检查", True)
    
    try:
        # 运行TypeScript编译
        print(f"{Colors.BLUE}▶ 运行 TypeScript 编译...{Colors.END}")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120,
            shell=True
        )
        
        if result.returncode == 0:
            dist_dir = frontend_dir / "dist"
            if dist_dir.exists():
                files = list(dist_dir.glob("**/*"))
                test_result("前端构建", True, f"生成{len(files)}个文件")
            else:
                test_result("前端构建", False, "dist目录未生成")
        else:
            error_msg = result.stderr[-200:] if result.stderr else "未知错误"
            test_result("前端构建", False, f"构建失败")
            if error_msg:
                print(f"{Colors.YELLOW}  错误: {error_msg}{Colors.END}")
            
    except subprocess.TimeoutExpired:
        test_result("前端构建", False, "构建超时（>120秒）")
    except Exception as e:
        test_result("前端构建", False, f"异常: {str(e)}")


def test_frontend_lint():
    """测试前端代码质量"""
    print_section("前端代码质量测试")
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # 检查Node.js环境
    node_installed, node_info = check_nodejs_installed()
    if not node_installed:
        test_result("Node.js环境检查", False, node_info)
        print(f"{Colors.YELLOW}  💡 建议: 安装Node.js https://nodejs.org/{Colors.END}")
        return
    test_result("Node.js环境检查", True, node_info)
    
    # 检查node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        test_result("依赖安装检查", False, "node_modules不存在")
        print(f"{Colors.YELLOW}  💡 建议: cd frontend && npm install{Colors.END}")
        return
    test_result("依赖安装检查", True)
    
    try:
        print(f"{Colors.BLUE}▶ 运行 ESLint 检查...{Colors.END}")
        result = subprocess.run(
            ["npm", "run", "lint"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=60,
            shell=True
        )
        
        if result.returncode == 0:
            test_result("ESLint代码检查", True, "无错误和警告")
        else:
            warnings = result.stdout.count("warning")
            errors = result.stdout.count("error")
            test_result("ESLint代码检查", errors == 0, f"{errors}个错误, {warnings}个警告")
            
    except subprocess.TimeoutExpired:
        test_result("ESLint检查", False, "检查超时")
    except Exception as e:
        test_result("ESLint检查", False, f"异常: {str(e)}")


# ============================================================================
# 前端单元测试
# ============================================================================

def test_frontend_unit():
    """测试前端组件单元测试"""
    print_section("前端单元测试")
    
    # 运行tests/目录下的前端单元测试
    test_script = Path(__file__).parent / "test_frontend_unit.py"
    
    if not test_script.exists():
        test_result("前端单元测试脚本", False, "test_frontend_unit.py不存在")
        return
    
    try:
        print(f"{Colors.BLUE}▶ 运行前端单元测试...{Colors.END}")
        result = subprocess.run(
            ["python", str(test_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        # 解析输出获取详情
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'PASS' in line or 'FAIL' in line:
                print(f"  {line}")
        
        if result.returncode == 0:
            test_result("前端单元测试", True, "所有测试通过")
        else:
            test_result("前端单元测试", False, f"退出码: {result.returncode}")
            if result.stderr:
                print(f"{Colors.YELLOW}  stderr: {result.stderr[:200]}{Colors.END}")
            
    except subprocess.TimeoutExpired:
        test_result("前端单元测试", False, "测试超时")
    except Exception as e:
        test_result("前端单元测试", False, f"异常: {str(e)}")


# ============================================================================
# E2E端到端测试
# ============================================================================

def test_e2e():
    """E2E端到端测试"""
    print_section("E2E端到端测试")
    
    # 运行tests/目录下的E2E测试
    test_script = Path(__file__).parent / "test_e2e.py"
    
    if not test_script.exists():
        test_result("E2E测试脚本", False, "test_e2e.py不存在")
        return
    
    try:
        result = subprocess.run(
            ["python", str(test_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'PASS' in line or 'FAIL' in line:
                print(f"  {line}")
        
        if result.returncode == 0:
            test_result("E2E测试", True, "所有测试通过")
        else:
            test_result("E2E测试", False, f"退出码: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        test_result("E2E测试", False, "测试超时")
    except Exception as e:
        test_result("E2E测试", False, f"异常: {str(e)}")


# ============================================================================
# API集成测试
# ============================================================================

def test_api_integration():
    """API集成测试（前端→后端）"""
    print_section("API集成测试")
    
    # 运行tests/目录下的API集成测试
    test_script = Path(__file__).parent / "test_api_integration.py"
    
    if not test_script.exists():
        test_result("API集成测试脚本", False, "test_api_integration.py不存在")
        return
    
    try:
        result = subprocess.run(
            ["python", str(test_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'PASS' in line or 'FAIL' in line:
                print(f"  {line}")
        
        if result.returncode == 0:
            test_result("API集成测试", True, "所有测试通过")
        else:
            test_result("API集成测试", False, f"退出码: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        test_result("API集成测试", False, "测试超时")
    except Exception as e:
        test_result("API集成测试", False, f"异常: {str(e)}")


# ============================================================================
# Vitest单元测试（可选）
# ============================================================================

def test_vitest():
    """运行Vitest单元测试"""
    print_section("Vitest单元测试（可选）")
    
    tests_dir = Path(__file__).parent
    vitest_config = tests_dir / "vitest.config.ts"
    
    # 检查是否已配置Vitest（在tests/目录）
    if not vitest_config.exists():
        test_result("Vitest配置检查", False, "未找到vitest.config.ts")
        print(f"{Colors.YELLOW}  💡 配置方法: 查看 tests/README.md 的 'Vitest单元测试' 章节{Colors.END}")
        print(f"{Colors.YELLOW}  💡 快速配置:{Colors.END}")
        print(f"{Colors.YELLOW}     cd tests{Colors.END}")
        print(f"{Colors.YELLOW}     mv vitest_examples/vitest.config.example.ts vitest.config.ts{Colors.END}")
        print(f"{Colors.YELLOW}     npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom{Colors.END}")
        return
    
    test_result("Vitest配置检查", True, "已配置（tests/目录）")
    
    # 检查Node.js环境
    node_installed, node_info = check_nodejs_installed()
    if not node_installed:
        test_result("Node.js环境检查", False, node_info)
        return
    test_result("Node.js环境检查", True, node_info)
    
    # 检查Vitest依赖
    package_json = tests_dir / "package.json"
    if package_json.exists():
        import json
        with open(package_json, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
            dev_deps = pkg.get('devDependencies', {})
            if 'vitest' not in dev_deps:
                test_result("Vitest依赖检查", False, "未安装vitest")
                print(f"{Colors.YELLOW}  💡 安装: cd tests && npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom{Colors.END}")
                return
    
    test_result("Vitest依赖检查", True, "已安装")
    
    try:
        print(f"{Colors.BLUE}▶ 运行 Vitest 测试...{Colors.END}")
        result = subprocess.run(
            ["npm", "test", "--", "--run"],
            cwd=tests_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120,
            shell=True
        )
        
        # 解析测试结果
        output = result.stdout
        if 'Test Files' in output:
            test_result("Vitest单元测试", result.returncode == 0, "测试完成")
            print(f"{Colors.CYAN}  {output}{Colors.END}")
        else:
            test_result("Vitest单元测试", False, "无测试文件")
            
    except subprocess.TimeoutExpired:
        test_result("Vitest测试", False, "测试超时")
    except Exception as e:
        test_result("Vitest测试", False, f"异常: {str(e)}")


# ============================================================================
# Playwright E2E测试（可选）
# ============================================================================

def test_playwright():
    """运行Playwright E2E测试"""
    print_section("Playwright E2E测试（可选）")
    
    tests_dir = Path(__file__).parent
    playwright_config = tests_dir / "playwright.config.ts"
    
    # 检查是否已配置Playwright（在tests/目录）
    if not playwright_config.exists():
        test_result("Playwright配置检查", False, "未找到playwright.config.ts")
        print(f"{Colors.YELLOW}  💡 配置方法: 查看 tests/README.md 的 'Playwright E2E测试' 章节{Colors.END}")
        print(f"{Colors.YELLOW}  💡 快速配置:{Colors.END}")
        print(f"{Colors.YELLOW}     cd tests{Colors.END}")
        print(f"{Colors.YELLOW}     mv playwright_examples/playwright.config.example.ts playwright.config.ts{Colors.END}")
        print(f"{Colors.YELLOW}     npm install -D @playwright/test && npx playwright install{Colors.END}")
        return
    
    test_result("Playwright配置检查", True, "已配置（tests/目录）")
    
    # 检查Node.js环境
    node_installed, node_info = check_nodejs_installed()
    if not node_installed:
        test_result("Node.js环境检查", False, node_info)
        return
    test_result("Node.js环境检查", True, node_info)
    
    # 检查E2E测试文件
    playwright_examples_dir = tests_dir / "playwright_examples"
    test_files = list(playwright_examples_dir.glob("*.spec.ts"))
    if not test_files:
        test_result("E2E测试文件检查", False, "未找到测试文件")
        print(f"{Colors.YELLOW}  💡 创建测试: 在 playwright_examples/ 目录创建 *.spec.ts 文件{Colors.END}")
        return
    
    test_result("E2E测试文件检查", True, f"找到{len(test_files)}个测试文件")
    
    try:
        print(f"{Colors.BLUE}▶ 运行 Playwright E2E测试...{Colors.END}")
        result = subprocess.run(
            ["npx", "playwright", "test"],
            cwd=tests_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=180,
            shell=True
        )
        
        # 解析测试结果
        output = result.stdout
        if 'passed' in output or 'failed' in output:
            test_result("Playwright E2E测试", result.returncode == 0, "测试完成")
            print(f"{Colors.CYAN}  {output}{Colors.END}")
        else:
            test_result("Playwright E2E测试", False, "测试执行异常")
            
    except subprocess.TimeoutExpired:
        test_result("Playwright测试", False, "测试超时")
    except Exception as e:
        test_result("Playwright测试", False, f"异常: {str(e)}")


# ============================================================================
# 性能测试
# ============================================================================

def test_performance():
    """性能测试"""
    print_section("性能测试")
    
    print(f"{Colors.BOLD}后端性能测试：{Colors.END}")
    test_result("API响应时间测试", False, "测试未实现")
    print(f"{Colors.YELLOW}  💡 建议: 使用Locust进行压力测试{Colors.END}")
    
    print(f"\n{Colors.BOLD}前端性能测试：{Colors.END}")
    test_result("页面加载性能", False, "测试未实现")
    print(f"{Colors.YELLOW}  💡 建议: 使用Lighthouse进行性能分析{Colors.END}")


# ============================================================================
# 安全测试
# ============================================================================

def test_security():
    """安全测试"""
    print_section("安全测试")
    
    test_result("认证授权测试", False, "测试未实现")
    test_result("SQL注入防护", False, "测试未实现")
    test_result("XSS防护", False, "测试未实现")
    test_result("CSRF防护", False, "测试未实现")
    
    print(f"{Colors.YELLOW}  💡 建议: 使用OWASP ZAP或Burp Suite进行安全扫描{Colors.END}")


# ============================================================================
# 兼容性测试
# ============================================================================

def test_compatibility():
    """兼容性测试"""
    print_section("兼容性测试")
    
    test_result("Chrome浏览器", False, "测试未实现")
    test_result("Firefox浏览器", False, "测试未实现")
    test_result("Safari浏览器", False, "测试未实现")
    test_result("Edge浏览器", False, "测试未实现")
    test_result("移动端响应式", False, "测试未实现")
    
    print(f"{Colors.YELLOW}  💡 建议: 使用Playwright或BrowserStack进行跨浏览器测试{Colors.END}")


# ============================================================================
# 数据库测试
# ============================================================================

def test_database():
    """数据库测试"""
    print_section("数据库测试")
    
    test_result("数据一致性", False, "测试未实现")
    test_result("备份恢复", False, "测试未实现")
    
    print(f"{Colors.YELLOW}  💡 建议: 添加数据库迁移和一致性验证测试{Colors.END}")


# ============================================================================
# 压力测试
# ============================================================================

def test_stress():
    """压力测试"""
    print_section("压力测试")
    
    test_result("高并发测试", False, "测试未实现")
    test_result("长时间稳定性", False, "测试未实现")
    test_result("资源泄漏检测", False, "测试未实现")
    
    print(f"{Colors.YELLOW}  💡 建议: 使用Locust或Apache JMeter进行压力测试{Colors.END}")


# ============================================================================
# 冒烟测试（快速验证）
# ============================================================================

def test_smoke():
    """冒烟测试 - 快速验证核心功能"""
    print_section("冒烟测试（快速验证）")
    
    # 只测试最关键的端点
    test_health_endpoints()
    
    # 简单的CRUD测试
    print(f"\n{Colors.BOLD}快速CRUD测试：{Colors.END}")
    test_api_endpoint("GET", "/tenants/", "租户列表")
    test_api_endpoint("GET", "/users/", "用户列表", params={'tenant_id': DEFAULT_TENANT_ID})
    test_api_endpoint("GET", "/alerts/", "告警列表")


# ============================================================================
# 测试分组定义
# ============================================================================

TEST_GROUPS = {
    # 后端API测试
    'health': {
        'name': '健康检查',
        'category': 'backend',
        'tests': [test_health_endpoints]
    },
    'docs': {
        'name': 'API文档',
        'category': 'backend',
        'tests': [test_api_documentation]
    },
    'tenant': {
        'name': '租户管理',
        'category': 'backend',
        'tests': [test_tenant_endpoints]
    },
    'user': {
        'name': '用户和角色',
        'category': 'backend',
        'tests': [test_user_role_endpoints]
    },
    'location': {
        'name': '位置管理',
        'category': 'backend',
        'tests': [test_location_endpoints]
    },
    'resident': {
        'name': '住户管理',
        'category': 'backend',
        'tests': [test_resident_endpoints]
    },
    'device': {
        'name': '设备管理',
        'category': 'backend',
        'tests': [test_device_endpoints]
    },
    'iot': {
        'name': 'IoT数据',
        'category': 'backend',
        'tests': [test_iot_data_endpoints]
    },
    'alert': {
        'name': '告警管理',
        'category': 'backend',
        'tests': [test_alert_endpoints]
    },
    'card': {
        'name': '卡片管理',
        'category': 'backend',
        'tests': [test_card_endpoints]
    },
    'quality': {
        'name': '护理质量',
        'category': 'backend',
        'tests': [test_care_quality_endpoints]
    },
    'integrity': {
        'name': '数据完整性',
        'category': 'backend',
        'tests': [test_data_integrity]
    },
    
    # 前端测试
    'frontend-build': {
        'name': '前端构建',
        'category': 'frontend',
        'tests': [test_frontend_build]
    },
    'frontend-lint': {
        'name': '代码质量',
        'category': 'frontend',
        'tests': [test_frontend_lint]
    },
    'frontend-unit': {
        'name': '单元测试',
        'category': 'frontend',
        'tests': [test_frontend_unit]
    },
    
    # 集成测试
    'e2e': {
        'name': 'E2E端到端',
        'category': 'integration',
        'tests': [test_e2e]
    },
    'api-integration': {
        'name': 'API集成',
        'category': 'integration',
        'tests': [test_api_integration]
    },
    
    # 专项测试
    'performance': {
        'name': '性能测试',
        'category': 'specialist',
        'tests': [test_performance]
    },
    'security': {
        'name': '安全测试',
        'category': 'specialist',
        'tests': [test_security]
    },
    'compatibility': {
        'name': '兼容性测试',
        'category': 'specialist',
        'tests': [test_compatibility]
    },
    'database': {
        'name': '数据库测试',
        'category': 'specialist',
        'tests': [test_database]
    },
    'stress': {
        'name': '压力测试',
        'category': 'specialist',
        'tests': [test_stress]
    },
    
    # 快速测试
    'smoke': {
        'name': '冒烟测试',
        'category': 'quick',
        'tests': [test_smoke]
    }
}


def list_all_tests():
    """列出所有可用的测试"""
    print_header("可用的测试分组")
    
    categories = {
        'backend': ('后端API测试', Colors.BLUE),
        'frontend': ('前端测试', Colors.GREEN),
        'integration': ('集成测试', Colors.YELLOW),
        'specialist': ('专项测试', Colors.RED),
        'quick': ('快速测试', Colors.BLUE)
    }
    
    for category, (title, color) in categories.items():
        tests_in_category = [(gid, ginfo) for gid, ginfo in TEST_GROUPS.items() 
                             if ginfo.get('category') == category]
        
        if tests_in_category:
            print(f"\n{Colors.BOLD}{color}{title}：{Colors.END}")
            for group_id, group_info in tests_in_category:
                # 标记已实现和未实现的测试
                if category in ['backend', 'frontend', 'quick']:
                    status = f"{Colors.GREEN}✓{Colors.END}"
                else:
                    status = f"{Colors.YELLOW}○{Colors.END}"
                print(f"  {status} {color}{group_id:20}{Colors.END} - {group_info['name']}")
    
    print(f"\n{Colors.BOLD}使用方法：{Colors.END}")
    print(f"  python tests/full_system_test.py --api <group_id>")
    print(f"  python tests/full_system_test.py --backend      # 所有后端测试")
    print(f"  python tests/full_system_test.py --frontend     # 所有前端测试")
    print(f"  python tests/full_system_test.py --integration  # 集成测试")
    print(f"  python tests/full_system_test.py --specialist   # 专项测试")
    print(f"  python tests/full_system_test.py --all          # 所有测试")
    
    print(f"\n{Colors.BOLD}图例：{Colors.END}")
    print(f"  {Colors.GREEN}✓{Colors.END} 已实现   {Colors.YELLOW}○{Colors.END} 框架已搭建（待实现）")


def show_interactive_menu():
    """显示交互式菜单"""
    while True:
        print_header("owlRD 完整系统测试 - 交互式菜单")
        
        print(f"{Colors.BOLD}【核心功能测试】{Colors.END}")
        print(f"  {Colors.GREEN}1{Colors.END}. 运行所有测试（后端 + 前端 + 集成）")
        print(f"  {Colors.GREEN}2{Colors.END}. 运行所有后端API测试")
        print(f"  {Colors.GREEN}3{Colors.END}. 运行所有前端测试")
        print(f"  {Colors.GREEN}4{Colors.END}. 运行E2E端到端测试")
        print(f"  {Colors.GREEN}5{Colors.END}. 运行API集成测试")
        print(f"  {Colors.GREEN}6{Colors.END}. 运行冒烟测试（快速验证）")
        
        print(f"\n{Colors.BOLD}【专项测试】{Colors.END}")
        print(f"  {Colors.YELLOW}7{Colors.END}. 运行性能测试")
        print(f"  {Colors.YELLOW}8{Colors.END}. 运行安全测试")
        print(f"  {Colors.YELLOW}9{Colors.END}. 运行兼容性测试")
        print(f"  {Colors.YELLOW}10{Colors.END}. 运行数据库测试")
        print(f"  {Colors.YELLOW}11{Colors.END}. 运行压力测试")
        
        print(f"\n{Colors.BOLD}【分组和工具】{Colors.END}")
        print(f"  {Colors.BLUE}12{Colors.END}. 选择特定测试分组（交互式）")
        print(f"  {Colors.BLUE}13{Colors.END}. 查看最新测试报告")
        print(f"  {Colors.BLUE}14{Colors.END}. 列出所有可用测试")
        
        print(f"\n  {Colors.RED}0{Colors.END}. 退出")
        
        choice = input(f"\n{Colors.BOLD}请输入选项 (0-14): {Colors.END}").strip()
        
        if choice == '0':
            print(f"\n{Colors.BLUE}退出测试{Colors.END}")
            sys.exit(0)
        elif choice == '1':
            run_all_tests()
            break
        elif choice == '2':
            run_backend_tests()
            break
        elif choice == '3':
            run_frontend_tests()
            break
        elif choice == '4':
            run_test_group('e2e')
            break
        elif choice == '5':
            run_test_group('api-integration')
            break
        elif choice == '6':
            run_test_group('smoke')
            break
        elif choice == '7':
            run_test_group('performance')
            break
        elif choice == '8':
            run_test_group('security')
            break
        elif choice == '9':
            run_test_group('compatibility')
            break
        elif choice == '10':
            run_test_group('database')
            break
        elif choice == '11':
            run_test_group('stress')
            break
        elif choice == '12':
            show_test_group_menu()
            break
        elif choice == '13':
            show_latest_report()
        elif choice == '14':
            list_all_tests()
            input(f"\n{Colors.BOLD}按Enter返回菜单...{Colors.END}")
        else:
            print(f"{Colors.RED}无效选项，请重新选择{Colors.END}")


def show_test_group_menu():
    """显示测试分组选择菜单"""
    print_header("选择测试分组")
    
    groups = list(TEST_GROUPS.keys())
    for i, group_id in enumerate(groups, 1):
        group_info = TEST_GROUPS[group_id]
        print(f"  {Colors.GREEN}{i:2}{Colors.END}. {group_info['name']} ({group_id})")
    
    choice = input(f"\n{Colors.BOLD}请输入选项 (1-{len(groups)}): {Colors.END}").strip()
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(groups):
            group_id = groups[index]
            run_test_group(group_id)
        else:
            print(f"{Colors.RED}无效选项{Colors.END}")
    except ValueError:
        print(f"{Colors.RED}无效输入{Colors.END}")


def run_test_group(group_id: str):
    """运行特定测试分组"""
    if group_id not in TEST_GROUPS:
        print(f"{Colors.RED}错误: 测试分组 '{group_id}' 不存在{Colors.END}")
        return 1
    
    group_info = TEST_GROUPS[group_id]
    print_header(f"运行测试分组: {group_info['name']}")
    
    # 初始化
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    # 检查服务器（后端测试需要）
    if not group_id.startswith('frontend'):
        if not check_server():
            print(f"{Colors.RED}✗ 后端服务器未运行，无法执行测试{Colors.END}")
            return 1
        
        global DEFAULT_TENANT_ID
        DEFAULT_TENANT_ID = get_default_tenant_id()
    
    # 运行测试
    try:
        for test_func in group_info['tests']:
            test_func()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    # 生成报告
    return generate_report()


def run_backend_tests():
    """运行所有后端测试"""
    return run_all_backend_tests()


def run_frontend_tests():
    """运行所有前端测试"""
    print_header("owlRD 前端测试")
    
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    try:
        test_frontend_build()
        test_frontend_lint()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    return generate_report()


def run_all_tests():
    """运行所有测试（后端+前端+集成）"""
    print_header("owlRD 完整系统测试（所有测试）")
    
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    # 第一部分：后端测试
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}第一部分：后端API测试{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    if not check_server_running():
        print(f"{Colors.RED}✗ 后端服务器未运行，跳过后端测试{Colors.END}")
    else:
        global DEFAULT_TENANT_ID
        DEFAULT_TENANT_ID = get_default_tenant_id()
        
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
    
    # 第二部分：前端测试
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}第二部分：前端测试{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    try:
        test_frontend_build()
        test_frontend_lint()
        test_frontend_unit()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    # 第三部分：集成测试
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}第三部分：集成测试{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    try:
        test_e2e()
        test_api_integration()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    return generate_report()


def show_latest_report():
    """显示最新的测试报告"""
    report_dir = Path(__file__).parent / "test_reports"
    
    if not report_dir.exists():
        print(f"{Colors.YELLOW}测试报告目录不存在{Colors.END}")
        return
    
    reports = sorted(report_dir.glob("test_report_*.json"), reverse=True)
    
    if not reports:
        print(f"{Colors.YELLOW}没有找到测试报告{Colors.END}")
        return
    
    latest_report = reports[0]
    
    try:
        with open(latest_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print_header(f"测试报告 - {latest_report.name}")
        
        print(f"{Colors.BOLD}测试时间:{Colors.END} {data.get('timestamp', 'N/A')}")
        print(f"{Colors.BOLD}总测试数:{Colors.END} {data.get('total_tests', 0)}")
        print(f"{Colors.BOLD}通过数:{Colors.END} {Colors.GREEN}{data.get('passed_tests', 0)}{Colors.END}")
        print(f"{Colors.BOLD}失败数:{Colors.END} {Colors.RED}{data.get('failed_tests', 0)}{Colors.END}")
        print(f"{Colors.BOLD}通过率:{Colors.END} {data.get('pass_rate', 0):.1f}%")
        
        if data.get('failed_tests', 0) > 0:
            print(f"\n{Colors.BOLD}失败的测试：{Colors.END}")
            for result in data.get('test_results', []):
                if not result.get('passed'):
                    print(f"  {Colors.RED}✗{Colors.END} {result.get('name')}")
                    if result.get('details'):
                        print(f"    {result.get('details')}")
        
    except Exception as e:
        print(f"{Colors.RED}读取报告失败: {str(e)}{Colors.END}")


def run_all_backend_tests():
    """运行所有后端API测试（原main函数逻辑）"""
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    print_header("owlRD 后端API测试")
    
    print(f"{Colors.BOLD}测试配置:{Colors.END}")
    print(f"  后端地址: {BASE_URL}")
    print(f"  API前缀: {API_PREFIX}")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务器
    print(f"\n{Colors.BOLD}检查服务器状态...{Colors.END}")
    if not check_server_running():
        print(f"{Colors.RED}✗ 后端服务器未运行！{Colors.END}")
        
        # 询问是否自动启动
        response = input(f"\n{Colors.YELLOW}是否自动启动后端服务？(Y/n): {Colors.END}").strip()
        
        if response.lower() in ['y', 'yes', '']:
            global BACKEND_PROCESS
            BACKEND_PROCESS = auto_start_backend()
            
            if BACKEND_PROCESS is None:
                print(f"\n{Colors.RED}无法自动启动后端服务，请手动启动：{Colors.END}")
                print(f"  cd backend")
                print(f"  python start_with_check.py")
                return 1
        else:
            print(f"\n{Colors.CYAN}请手动启动后端服务器：{Colors.END}")
            print(f"  cd backend")
            print(f"  python start_with_check.py")
            return 1
    else:
        print(f"{Colors.GREEN}✓ 后端服务器正在运行{Colors.END}")
    
    # 获取默认租户ID
    print(f"\n{Colors.BOLD}获取默认租户ID...{Colors.END}")
    tenant_id = get_default_tenant_id()
    if tenant_id:
        print(f"{Colors.GREEN}✓ 默认租户ID: {tenant_id[:8]}...{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ 无法获取租户ID，部分测试可能失败{Colors.END}")
    
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
        cleanup_backend_service()
        return 1
    except Exception as e:
        print(f"\n\n{Colors.RED}测试过程中发生错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        cleanup_backend_service()
        return 1
    
    # 生成报告
    result = generate_report()
    
    # 清理自动启动的后端服务
    cleanup_backend_service()
    
    return result

def run_integration_tests():
    """运行所有集成测试"""
    print_header("owlRD 集成测试")
    
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    try:
        test_e2e()
        test_api_integration()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    return generate_report()


def run_specialist_tests():
    """运行所有专项测试"""
    print_header("owlRD 专项测试")
    
    global TEST_RESULTS, TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TEST_RESULTS = []
    TOTAL_TESTS = 0
    PASSED_TESTS = 0
    FAILED_TESTS = 0
    
    try:
        test_performance()
        test_security()
        test_compatibility()
        test_database()
        test_stress()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        return 1
    
    return generate_report()


def main():
    """主入口函数 - 解析命令行参数或显示菜单"""
    parser = argparse.ArgumentParser(
        description="owlRD完整系统测试 - 后端API + 前端 + E2E + 专项测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 交互式菜单
  python tests/full_system_test.py
  
  # 核心测试
  python tests/full_system_test.py --all              # 运行所有测试
  python tests/full_system_test.py --backend          # 只测试后端API
  python tests/full_system_test.py --frontend         # 只测试前端
  python tests/full_system_test.py --integration      # 集成测试
  python tests/full_system_test.py --specialist       # 专项测试
  
  # 特定分组
  python tests/full_system_test.py --api health       # 健康检查
  python tests/full_system_test.py --api alert        # 告警系统
  python tests/full_system_test.py --e2e              # E2E测试
  python tests/full_system_test.py --smoke            # 冒烟测试
  
  # 专项测试
  python tests/full_system_test.py --performance      # 性能测试
  python tests/full_system_test.py --security         # 安全测试
  python tests/full_system_test.py --compatibility    # 兼容性测试
  
  # 可选测试（需先配置）
  python tests/full_system_test.py --vitest           # Vitest单元测试
  python tests/full_system_test.py --playwright       # Playwright E2E测试
  
  # 工具
  python tests/full_system_test.py --list             # 列出所有测试
  python tests/full_system_test.py --report           # 查看最新报告
        """
    )
    
    # 核心测试参数
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--backend', action='store_true', help='运行所有后端API测试')
    parser.add_argument('--frontend', action='store_true', help='运行所有前端测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--specialist', action='store_true', help='运行专项测试')
    
    # 特定测试参数
    parser.add_argument('--api', metavar='GROUP', help='运行特定API测试分组')
    parser.add_argument('--e2e', action='store_true', help='运行E2E端到端测试')
    parser.add_argument('--smoke', action='store_true', help='运行冒烟测试')
    
    # 专项测试参数
    parser.add_argument('--performance', action='store_true', help='运行性能测试')
    parser.add_argument('--security', action='store_true', help='运行安全测试')
    parser.add_argument('--compatibility', action='store_true', help='运行兼容性测试')
    parser.add_argument('--database', action='store_true', help='运行数据库测试')
    parser.add_argument('--stress', action='store_true', help='运行压力测试')
    
    # 可选测试参数
    parser.add_argument('--vitest', action='store_true', help='运行Vitest单元测试（需先配置）')
    parser.add_argument('--playwright', action='store_true', help='运行Playwright E2E测试（需先配置）')
    
    # 工具参数
    parser.add_argument('--list', action='store_true', help='列出所有可用测试')
    parser.add_argument('--report', action='store_true', help='查看最新测试报告')
    
    args = parser.parse_args()
    
    # 处理命令行参数
    if args.list:
        list_all_tests()
        return 0
    elif args.report:
        show_latest_report()
        return 0
    elif args.all:
        return run_all_tests()
    elif args.backend:
        return run_backend_tests()
    elif args.frontend:
        return run_frontend_tests()
    elif args.integration:
        return run_integration_tests()
    elif args.specialist:
        return run_specialist_tests()
    elif args.e2e:
        return run_test_group('e2e')
    elif args.smoke:
        return run_test_group('smoke')
    elif args.performance:
        return run_test_group('performance')
    elif args.security:
        return run_test_group('security')
    elif args.compatibility:
        return run_test_group('compatibility')
    elif args.database:
        return run_test_group('database')
    elif args.stress:
        return run_test_group('stress')
    elif args.vitest:
        # 运行Vitest单元测试
        print_header("Vitest单元测试")
        test_vitest()
        return 0
    elif args.playwright:
        # 运行Playwright E2E测试
        print_header("Playwright E2E测试")
        test_playwright()
        return 0
    elif args.api:
        return run_test_group(args.api)
    else:
        # 无参数时显示交互式菜单
        show_interactive_menu()
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}程序被用户中断{Colors.END}")
        sys.exit(1)
