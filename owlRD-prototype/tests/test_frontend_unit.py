#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端单元测试（独立于frontend/package.json）

测试前端组件的基本功能
"""

import sys
import io
from pathlib import Path

# 确保stdout使用UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_frontend_components():
    """测试前端组件存在性"""
    frontend_dir = Path(__file__).parent.parent / "frontend" / "src"
    
    # 检查关键目录
    components_dir = frontend_dir / "components"
    pages_dir = frontend_dir / "pages"
    services_dir = frontend_dir / "services"
    forms_dir = components_dir / "forms" if components_dir.exists() else None
    
    results = []
    
    if components_dir.exists():
        comp_count = len(list(components_dir.glob("**/*.tsx")))
        results.append(("组件目录", True, f"找到{comp_count}个组件"))
    else:
        results.append(("组件目录", False, "目录不存在"))
    
    if pages_dir.exists():
        page_count = len(list(pages_dir.glob("**/*.tsx")))
        results.append(("页面目录", True, f"找到{page_count}个页面"))
    else:
        results.append(("页面目录", False, "目录不存在"))
    
    if services_dir.exists():
        service_count = len(list(services_dir.glob("**/*.ts")))
        results.append(("服务目录", True, f"找到{service_count}个服务"))
    else:
        results.append(("服务目录", False, "目录不存在"))
    
    # 检查表单组件（新建/编辑功能）
    if forms_dir and forms_dir.exists():
        form_files = list(forms_dir.glob("*Form.tsx"))
        results.append(("表单组件", True, f"找到{len(form_files)}个表单"))
    else:
        results.append(("表单组件", False, "表单目录不存在"))
    
    # 检查模态框组件（包含删除功能）
    if components_dir and components_dir.exists():
        modal_files = list(components_dir.glob("**/*Modal.tsx"))
        results.append(("模态框组件", True, f"找到{len(modal_files)}个模态框"))
    else:
        results.append(("模态框组件", False, "组件目录不存在"))
    
    return results


def main():
    """运行前端单元测试"""
    print("="*80)
    print("前端单元测试")
    print("="*80)
    
    results = test_frontend_components()
    
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
