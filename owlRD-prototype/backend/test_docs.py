"""
测试所有文档端点是否正常工作
"""

import requests
import sys

# 测试地址
BASE_URL = "http://localhost:8000"

# 测试端点
endpoints = [
    ("/", "根路径健康检查"),
    ("/health", "详细健康检查"),
    ("/api/openapi.json", "OpenAPI规范"),
    ("/docs", "默认Swagger UI（可能白屏）"),
    ("/docs-cn", "国内CDN Swagger UI"),
    ("/docs-local", "本地Swagger UI（推荐）"),
    ("/docs-offline", "FastAPI内置文档"),
    ("/docs-simple", "极简HTML文档"),
]

def test_endpoint(endpoint, description):
    """测试单个端点"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {endpoint:25} {description:30} [{response.status_code}]")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint:25} {description:30} [ERROR: {e}]")
        return False

def main():
    """运行所有测试"""
    print("\n🦉 owlRD API文档端点测试")
    print("=" * 80)
    print(f"测试地址: {BASE_URL}")
    print("=" * 80)
    
    results = []
    for endpoint, description in endpoints:
        result = test_endpoint(endpoint, description)
        results.append(result)
    
    print("=" * 80)
    success_count = sum(results)
    total_count = len(results)
    print(f"\n测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有端点测试通过！")
        print(f"\n推荐访问: {BASE_URL}/docs-local")
        return 0
    else:
        print("⚠️  部分端点测试失败，请检查服务器状态")
        return 1

if __name__ == "__main__":
    sys.exit(main())
