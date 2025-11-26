#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Hooks 安装脚本
在Git提交前自动检查项目结构
"""

import os
import sys
from pathlib import Path


def install_pre_commit_hook(project_root: Path):
    """安装 pre-commit hook"""
    
    git_dir = project_root / ".git"
    if not git_dir.exists():
        print("❌ 错误: 未找到 .git 目录，请确保在Git仓库中运行此脚本")
        return False
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit_file = hooks_dir / "pre-commit"
    
    # Pre-commit hook 内容
    hook_content = """#!/bin/sh
# Git Pre-commit Hook - 项目结构检查

echo "🔍 运行项目结构检查..."

# 运行检查脚本
python .windsurfrules/scripts/check_project_structure.py

# 检查返回码
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 项目结构检查失败！"
    echo "⚠️ 请修正上述问题后再提交"
    echo ""
    echo "💡 如果确定要跳过检查，使用: git commit --no-verify"
    echo ""
    exit 1
fi

echo "✅ 项目结构检查通过"
echo ""
exit 0
"""
    
    # Windows 版本（.bat）
    hook_content_bat = """@echo off
REM Git Pre-commit Hook - 项目结构检查

echo 🔍 运行项目结构检查...
echo.

python .windsurfrules\\scripts\\check_project_structure.py

if errorlevel 1 (
    echo.
    echo ❌ 项目结构检查失败！
    echo ⚠️ 请修正上述问题后再提交
    echo.
    echo 💡 如果确定要跳过检查，使用: git commit --no-verify
    echo.
    exit /b 1
)

echo ✅ 项目结构检查通过
echo.
exit /b 0
"""
    
    try:
        # 写入 pre-commit hook
        with open(pre_commit_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(hook_content)
        
        # Linux/Mac 需要设置执行权限
        if sys.platform != 'win32':
            os.chmod(pre_commit_file, 0o755)
        
        # Windows 额外创建 .bat 版本
        if sys.platform == 'win32':
            pre_commit_bat = hooks_dir / "pre-commit.bat"
            with open(pre_commit_bat, 'w', encoding='utf-8') as f:
                f.write(hook_content_bat)
        
        print(f"✅ Git pre-commit hook 已安装: {pre_commit_file}")
        print()
        print("📋 说明:")
        print("  - 每次 git commit 前会自动检查项目结构")
        print("  - 如果检查失败，提交会被阻止")
        print("  - 使用 git commit --no-verify 可以跳过检查")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("🔧 Git Hooks 安装工具")
    print("="*60)
    print()
    
    # 获取项目根目录
    # 脚本位置: .windsurfrules/scripts/xxx.py
    script_dir = Path(__file__).parent  # .windsurfrules/scripts/
    project_root = script_dir.parent.parent  # 项目根/
    
    print(f"📁 项目目录: {project_root}")
    print()
    
    # 安装 hook
    success = install_pre_commit_hook(project_root)
    
    if success:
        print("="*60)
        print("🎉 安装完成！")
        print("="*60)
    else:
        print("="*60)
        print("❌ 安装失败")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
