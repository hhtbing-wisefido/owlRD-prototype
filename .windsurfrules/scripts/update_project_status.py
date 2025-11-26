#!/usr/bin/env python3
"""
项目状态自动更新脚本

功能：
- 自动扫描项目文件统计代码行数
- 自动检测Git提交数
- 自动更新项目状态.json文件
- 可以在每次重要提交前运行

使用：
    python update_project_status.py
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import os


def count_lines_in_file(file_path: Path) -> int:
    """统计文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0


def count_code_lines(directory: Path, extensions: list) -> int:
    """统计指定目录下特定扩展名文件的总行数"""
    total_lines = 0
    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            # 排除node_modules和其他不需要统计的目录
            if 'node_modules' in str(file_path):
                continue
            if '__pycache__' in str(file_path):
                continue
            if '.venv' in str(file_path):
                continue
            if 'dist' in str(file_path):
                continue
            total_lines += count_lines_in_file(file_path)
    return total_lines


def get_git_commit_count() -> str:
    """获取Git提交总数"""
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "unknown"
    except:
        return "unknown"


def check_services_running() -> dict:
    """检查服务运行状态"""
    backend_running = False
    frontend_running = False
    
    try:
        # 检查端口8000 (后端)
        result = subprocess.run(
            ['powershell', '-Command', 'Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet'],
            capture_output=True,
            text=True,
            timeout=2
        )
        backend_running = result.stdout.strip().lower() == 'true'
    except:
        pass
    
    try:
        # 检查端口3000 (前端)
        result = subprocess.run(
            ['powershell', '-Command', 'Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet'],
            capture_output=True,
            text=True,
            timeout=2
        )
        frontend_running = result.stdout.strip().lower() == 'true'
    except:
        pass
    
    return {
        "backend": backend_running,
        "frontend": frontend_running
    }


def count_files(directory: Path, pattern: str) -> int:
    """统计匹配模式的文件数量"""
    return len(list(directory.rglob(pattern)))


def update_project_status():
    """更新项目状态文件"""
    
    # 项目根目录 (脚本在.windsurfrules/scripts/目录下)
    project_root = Path(__file__).parent.parent.parent  # .windsurfrules/scripts/ -> .windsurfrules/ -> 项目根/
    backend_dir = project_root / "owlRD-prototype" / "backend"
    frontend_dir = project_root / "owlRD-prototype" / "frontend"
    docs_dir = project_root / "项目记录"
    
    print("🔍 扫描项目文件...")
    
    # 统计代码行数
    backend_lines = count_code_lines(backend_dir / "app", ['.py'])
    frontend_lines = count_code_lines(frontend_dir / "src", ['.tsx', '.ts'])
    doc_lines = count_code_lines(docs_dir, ['.md'])
    
    # 统计文件数量
    python_files = count_files(backend_dir / "app", "*.py")
    tsx_files = count_files(frontend_dir / "src", "*.tsx")
    ts_files = count_files(frontend_dir / "src", "*.ts")
    
    # Git提交数
    git_commits = get_git_commit_count()
    
    # 检查服务状态
    services = check_services_running()
    
    # 读取现有状态
    status_file = project_root / "项目记录" / "项目状态.json"
    with open(status_file, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    # 更新统计数据
    status['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    status['code_statistics']['backend_lines'] = backend_lines
    status['code_statistics']['frontend_lines'] = frontend_lines
    status['code_statistics']['documentation_lines'] = doc_lines
    status['code_statistics']['total_lines'] = backend_lines + frontend_lines + doc_lines
    status['code_statistics']['git_commits'] = git_commits
    
    # 更新文件统计
    status['code_statistics']['python_files'] = python_files
    status['code_statistics']['typescript_files'] = tsx_files + ts_files
    
    # 更新服务运行状态
    if 'runtime_status' not in status:
        status['runtime_status'] = {}
    
    status['runtime_status'] = {
        "backend_server": "运行中" if services['backend'] else "已停止",
        "frontend_server": "运行中" if services['frontend'] else "已停止",
        "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存更新后的状态
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    print("✅ 项目状态已更新！")
    print(f"\n📊 统计结果:")
    print(f"   后端代码: {backend_lines:,} 行 ({python_files} 个Python文件)")
    print(f"   前端代码: {frontend_lines:,} 行 ({tsx_files + ts_files} 个TypeScript文件)")
    print(f"   文档: {doc_lines:,} 行")
    print(f"   总计: {backend_lines + frontend_lines + doc_lines:,} 行")
    print(f"   Git提交: {git_commits} 次")
    print(f"\n🖥️  服务状态:")
    print(f"   后端服务器: {'🟢 运行中' if services['backend'] else '⚪ 已停止'}")
    print(f"   前端服务器: {'🟢 运行中' if services['frontend'] else '⚪ 已停止'}")
    print(f"\n📝 状态文件: {status_file}")


if __name__ == "__main__":
    try:
        update_project_status()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
