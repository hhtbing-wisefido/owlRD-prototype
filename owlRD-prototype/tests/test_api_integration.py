#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API集成测试（前端→后端）

测试前后端接口集成
"""

import sys
import io
import requests

# 确保stdout使用UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api/v1"

def test_api_connectivity():
    """测试API连通性"""
    try:
        response = requests.get(f"http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            return ("API连通性", True, "后端服务正常")
        else:
            return ("API连通性", False, f"状态码: {response.status_code}")
    except Exception as e:
        return ("API连通性", False, f"无法连接: {str(e)}")


def main():
    """运行API集成测试"""
    print("="*80)
    print("API集成测试")
    print("="*80)
    
    results = [
        test_api_connectivity(),
    ]
    
    passed = 0
    failed = 0
    
    for name, success, detail in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} | {name}")
        if detail:
            print(f"       {detail}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n通过: {passed}/{passed+failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
