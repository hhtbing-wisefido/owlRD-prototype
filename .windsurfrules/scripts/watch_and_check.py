#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监控自动检查脚本
监控项目目录变化，自动触发结构检查
"""

import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from check_project_structure import ProjectStructureChecker


class ProjectWatcher(FileSystemEventHandler):
    """项目文件监控器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.last_check_time = 0
        self.check_interval = 5  # 秒，防止频繁检查
        
    def should_check(self, event):
        """判断是否需要检查"""
        # 跳过的路径
        skip_paths = ['.git', 'node_modules', 'venv', '__pycache__', '.windsurfrules']
        for skip in skip_paths:
            if skip in str(event.src_path):
                return False
        
        # 只检查目录创建/删除/重命名
        if event.is_directory:
            if event.event_type in ['created', 'deleted', 'moved']:
                return True
        
        return False
    
    def run_check(self):
        """运行检查"""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return
        
        self.last_check_time = current_time
        print(f"\n{'='*60}")
        print(f"🔍 触发自动检查 - {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")
        
        checker = ProjectStructureChecker(self.project_root)
        checker.check_all()
    
    def on_created(self, event):
        """文件/目录创建时"""
        if self.should_check(event):
            print(f"📁 检测到创建: {Path(event.src_path).name}")
            self.run_check()
    
    def on_deleted(self, event):
        """文件/目录删除时"""
        if self.should_check(event):
            print(f"🗑️ 检测到删除: {Path(event.src_path).name}")
            self.run_check()
    
    def on_moved(self, event):
        """文件/目录移动时"""
        if self.should_check(event):
            print(f"📦 检测到移动: {Path(event.src_path).name} → {Path(event.dest_path).name}")
            self.run_check()


def main():
    """主函数"""
    print("="*60)
    print("👁️ 项目结构监控 - 自动检查模式")
    print("="*60)
    print()
    
    # 获取项目根目录
    # 脚本位置: .windsurfrules/scripts/xxx.py
    script_dir = Path(__file__).parent  # .windsurfrules/scripts/
    project_root = script_dir.parent.parent  # 项目根/
    
    print(f"📁 监控目录: {project_root}")
    print(f"⏱️ 检查间隔: 5秒")
    print(f"🔍 监控事件: 目录创建/删除/移动")
    print()
    print("💡 提示: 按 Ctrl+C 停止监控")
    print("="*60)
    print()
    
    # 先执行一次检查
    print("🔍 初始检查...")
    checker = ProjectStructureChecker(project_root)
    checker.check_all()
    
    # 创建监控器
    event_handler = ProjectWatcher(project_root)
    observer = Observer()
    observer.schedule(event_handler, str(project_root), recursive=True)
    
    # 启动监控
    observer.start()
    print(f"\n✅ 监控已启动！正在监控项目变化...\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n⏹️ 监控已停止")
    
    observer.join()


if __name__ == "__main__":
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("❌ 缺少依赖: watchdog")
        print("💡 安装命令: pip install watchdog")
        sys.exit(1)
    
    main()
