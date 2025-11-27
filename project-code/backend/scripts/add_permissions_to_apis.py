"""
批量为API端点添加基本权限检查的脚本
用于快速集成权限系统
"""

import os
import re
from pathlib import Path


API_DIR = Path(__file__).parent.parent / "app" / "api" / "v1"

# 需要更新的API文件
TARGET_FILES = [
    "devices.py",
    "locations.py",
    "residents.py",
    "alerts.py",
    "alert_policies.py",
]

# 导入语句模板
IMPORTS_TO_ADD = """from app.dependencies.auth import get_current_user_from_token, require_role
from app.middleware.permissions import check_tenant_access, check_manage_permission"""


def add_permission_imports(file_path: Path) -> bool:
    """添加权限相关的导入"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有权限导入
    if "get_current_user_from_token" in content:
        print(f"  ✓ {file_path.name} already has permission imports")
        return False
    
    # 在from fastapi import后面添加Depends
    if "from fastapi import" in content and "Depends" not in content:
        content = re.sub(
            r'(from fastapi import [^)]+)',
            r'\1, Depends',
            content
        )
    
    # 添加typing imports
    if "from typing import" in content and "Dict, Any" not in content:
        content = re.sub(
            r'(from typing import [^)]+)',
            r'\1, Dict, Any',
            content
        )
    
    # 在第一个router定义之前添加权限导入
    content = re.sub(
        r'(router = APIRouter\(\))',
        f'{IMPORTS_TO_ADD}\n\n\\1',
        content,
        count=1
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Added permission imports to {file_path.name}")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Adding permission checks to API endpoints")
    print("=" * 60)
    
    for filename in TARGET_FILES:
        file_path = API_DIR / filename
        if not file_path.exists():
            print(f"  ✗ {filename} not found, skipping")
            continue
        
        print(f"\nProcessing {filename}...")
        add_permission_imports(file_path)
    
    print("\n" + "=" * 60)
    print("✓ Permission imports added!")
    print("=" * 60)
    print("\n注意: 需要手动为每个端点添加权限检查逻辑")
    print("示例:")
    print("  current_user: Dict[str, Any] = Depends(get_current_user_from_token)")
    print("  check_tenant_access(current_user, tenant_id)")


if __name__ == "__main__":
    main()
