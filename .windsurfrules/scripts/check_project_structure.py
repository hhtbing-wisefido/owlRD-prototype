#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构检查脚本
用于检查项目是否符合规范，发现违规的目录和文件
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime


class ProjectStructureChecker:
    """项目结构检查器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        self.info = []
        
    def check_all(self):
        """执行所有检查"""
        print("🔍 开始检查项目结构...")
        print(f"📁 项目根目录: {self.project_root}\n")
        
        self.check_root_directory()
        self.check_project_records()
        self.check_knowledge_base()
        self.check_directory_depth()
        
        self.print_results()
        
    def check_root_directory(self):
        """检查根目录清洁度"""
        print("📋 检查1: 根目录清洁度")
        
        # 允许的文件和目录
        allowed_items = {
            '.git', '.vscode', '.windsurfrules', 'owlRD-prototype',
            'scripts', '知识库', '项目记录',
            '.gitignore', 'README.md'
        }
        
        # 遍历根目录
        for item in self.project_root.iterdir():
            if item.name not in allowed_items:
                self.errors.append(f"❌ 根目录发现不允许的项: {item.name}")
        
        # 检查是否有文档文件堆积
        for item in self.project_root.glob("*.md"):
            if item.name != "README.md":
                self.errors.append(f"❌ 根目录不允许文档文件: {item.name}")
        
        # 检查临时文件
        temp_patterns = ["*.tmp", "*.temp", "*.log", "*临时*", "*test*"]
        for pattern in temp_patterns:
            for item in self.project_root.glob(pattern):
                self.warnings.append(f"⚠️ 根目录发现临时文件: {item.name}")
        
        print("✅ 根目录检查完成\n")
        
    def check_project_records(self):
        """检查项目记录目录"""
        print("📋 检查2: 项目记录目录结构")
        
        records_dir = self.project_root / "项目记录"
        if not records_dir.exists():
            self.errors.append("❌ 项目记录目录不存在")
            return
        
        # 必需的8个编号目录
        required_dirs = {
            "1-归档", "2-源参考对照", "3-功能说明", "4-部署运维",
            "5-问题分析", "6-开发规范", "7-过程记录", "8-聊天记录"
        }
        
        # 允许的文件
        allowed_files = {"README.md", "项目状态.json"}
        
        # 获取实际的一级目录和文件
        actual_items = set()
        dirs_found = set()
        files_found = set()
        
        for item in records_dir.iterdir():
            actual_items.add(item.name)
            if item.is_dir():
                dirs_found.add(item.name)
            else:
                files_found.add(item.name)
        
        # 检查必需目录
        missing_dirs = required_dirs - dirs_found
        for dir_name in missing_dirs:
            self.warnings.append(f"⚠️ 缺少必需目录: 项目记录/{dir_name}")
        
        # 检查额外目录（重点！）
        extra_dirs = dirs_found - required_dirs
        for dir_name in extra_dirs:
            if not re.match(r'^\d+-', dir_name):
                self.errors.append(f"❌ 发现没有编号前缀的目录: 项目记录/{dir_name}")
            else:
                self.errors.append(f"❌ 发现不在8大分类中的目录: 项目记录/{dir_name}")
        
        # 检查重复目录（同一功能的不同命名）
        if extra_dirs:
            for extra in extra_dirs:
                # 去掉编号前缀比较
                extra_clean = re.sub(r'^\d+-', '', extra)
                for req in required_dirs:
                    req_clean = re.sub(r'^\d+-', '', req)
                    if extra_clean == req_clean and extra != req:
                        self.errors.append(
                            f"❌ 发现重复目录: 项目记录/{extra} "
                            f"(已有 {req})"
                        )
        
        # 检查额外文件
        extra_files = files_found - allowed_files
        for file_name in extra_files:
            self.warnings.append(f"⚠️ 项目记录根目录发现额外文件: {file_name}")
        
        print(f"✅ 项目记录检查完成 (发现 {len(dirs_found)} 个目录)\n")
        
    def check_knowledge_base(self):
        """检查知识库目录"""
        print("📋 检查3: 知识库目录")
        
        kb_dir = self.project_root / "知识库"
        if not kb_dir.exists():
            self.warnings.append("⚠️ 知识库目录不存在（建议创建）")
            return
        
        # 检查README
        readme = kb_dir / "README.md"
        if not readme.exists():
            self.warnings.append("⚠️ 知识库缺少 README.md")
        
        self.info.append("ℹ️ 知识库目录存在（只读参考）")
        print("✅ 知识库检查完成\n")
        
    def check_directory_depth(self, max_depth: int = 4):
        """检查目录层级深度"""
        print(f"📋 检查4: 目录层级深度（限制 {max_depth} 层）")
        
        def get_depth(path: Path) -> int:
            """计算相对于项目根目录的深度"""
            try:
                relative = path.relative_to(self.project_root)
                return len(relative.parts)
            except ValueError:
                return 0
        
        deep_dirs = []
        for dirpath, dirnames, filenames in os.walk(self.project_root):
            path = Path(dirpath)
            
            # 跳过 .git 和 node_modules
            if '.git' in path.parts or 'node_modules' in path.parts:
                continue
            
            depth = get_depth(path)
            if depth > max_depth:
                deep_dirs.append((path, depth))
        
        if deep_dirs:
            for path, depth in sorted(deep_dirs, key=lambda x: x[1], reverse=True):
                relative = path.relative_to(self.project_root)
                self.warnings.append(f"⚠️ 目录层级过深 ({depth}层): {relative}")
        
        print(f"✅ 层级检查完成 (最大深度: {max([d for _, d in deep_dirs] or [0])}层)\n")
        
    def print_results(self):
        """打印检查结果"""
        print("\n" + "="*60)
        print("📊 检查结果汇总")
        print("="*60 + "\n")
        
        # 错误
        if self.errors:
            print(f"❌ 发现 {len(self.errors)} 个错误:\n")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # 警告
        if self.warnings:
            print(f"⚠️ 发现 {len(self.warnings)} 个警告:\n")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # 信息
        if self.info:
            print(f"ℹ️ 信息:\n")
            for info in self.info:
                print(f"  {info}")
            print()
        
        # 总结
        print("="*60)
        if not self.errors and not self.warnings:
            print("🎉 恭喜！项目结构完全符合规范！")
        elif not self.errors:
            print("✅ 项目结构基本符合规范，有少量警告需要注意")
        else:
            print("⚠️ 项目结构存在问题，请根据错误提示进行修正")
        print("="*60 + "\n")
        
        # 生成JSON报告
        self.save_report()
        
    def save_report(self):
        """保存检查报告为JSON"""
        report = {
            "check_time": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "status": "failed" if self.errors else ("warning" if self.warnings else "passed")
            }
        }
        
        report_file = self.project_root / ".windsurfrules" / "scripts" / "structure_check_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告已保存: {report_file}")


def main():
    """主函数"""
    import sys
    
    # 获取项目根目录
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # 默认为脚本所在目录的父目录的父目录
        # 脚本位置: .windsurfrules/scripts/xxx.py
        script_dir = Path(__file__).parent  # .windsurfrules/scripts/
        project_root = script_dir.parent.parent  # 项目根/
    
    # 创建检查器并执行
    checker = ProjectStructureChecker(project_root)
    checker.check_all()
    
    # 返回错误码
    sys.exit(1 if checker.errors else 0)


if __name__ == "__main__":
    main()
