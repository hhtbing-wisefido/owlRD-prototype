#!/usr/bin/env python3
"""
批量移除API文件中对StorageService的await调用
因为StorageService是同步的，不应该使用await
"""

import os
import re
from pathlib import Path

def fix_await_storage(file_path):
    """修复单个文件中的await storage调用"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 移除 await storage.method() 的await
    # 匹配模式：await xxx_storage.method(...)
    patterns = [
        (r'(\s+)await\s+(\w+_storage\.(find_all|find_by_id|create|update|delete|get|save_all|load_all)\()', r'\1\2'),
        (r'(\s+)await\s+(self\.\w+_storage\.(find_all|find_by_id|create|update|delete|get|save_all|load_all)\()', r'\1\2'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """批量处理所有API文件"""
    api_dir = Path("app/api/v1")
    
    if not api_dir.exists():
        print(f"❌ Directory not found: {api_dir}")
        return
    
    print("🔧 Fixing await calls in API files...")
    fixed_count = 0
    
    for py_file in api_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        if fix_await_storage(py_file):
            print(f"✅ Fixed: {py_file.name}")
            fixed_count += 1
        else:
            print(f"⏭️  Skipped: {py_file.name} (no changes needed)")
    
    print(f"\n🎉 Done! Fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
