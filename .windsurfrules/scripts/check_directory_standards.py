"""
项目记录目录规范检查脚本
自动检查目录结构、编号、文件位置是否符合规范

运行: python scripts/check_directory_standards.py
"""

import os
from pathlib import Path
from datetime import datetime
import json

# 项目根目录
# 脚本位置: .windsurfrules/scripts/xxx.py
PROJECT_ROOT = Path(__file__).parent.parent.parent  # .windsurfrules/scripts/ -> .windsurfrules/ -> 项目根/
RECORDS_DIR = PROJECT_ROOT / "项目记录"

# 规范定义
EXPECTED_TOP_DIRS = {
    "1-归档": "历史过时文档",
    "2-源参考对照": "源参考对照检查",
    "3-功能说明": "功能详细说明",
    "4-部署运维": "部署和运维文档",
    "5-问题分析": "问题分析和修复报告",
    "6-开发规范": "开发规范和最佳实践",
    "7-过程记录": "开发过程记录",
    "8-聊天记录": "AI对话记录"
}

EXPECTED_SUB_DIRS = {
    "2-源参考对照": {
        "1-数据库Schema对照": "Schema检查清单",
        "2-技术文档理解": "文档理解检查",
        "3-自动化验证": "自动化验证体系",
        "4-完成度报告": "完成度统计",
        "5-版本历史": "历史版本快照"
    }
}

# 不应该出现在根目录的文件模式
FORBIDDEN_ROOT_PATTERNS = [
    "AUTO_",  # 自动生成报告应该在子目录
    "URGENT_",  # 紧急报告应该在问题分析或归档
    "临时",
    "测试",
    "temp",
    "test"
]

class DirectoryStandardChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = {
            "total_dirs": 0,
            "total_files": 0,
            "archived_files": 0,
            "process_records": 0,
            "chat_logs": 0
        }
    
    def check(self):
        """执行所有检查"""
        print("🔍 项目记录目录规范检查")
        print("=" * 80)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"检查目录: {RECORDS_DIR}")
        print("=" * 80)
        print()
        
        # 1. 检查顶层目录
        self.check_top_directories()
        
        # 2. 检查子目录结构
        self.check_sub_directories()
        
        # 3. 检查根目录文件
        self.check_root_files()
        
        # 4. 检查临时文件
        self.check_temporary_files()
        
        # 5. 检查聊天记录完整性
        self.check_chat_logs()
        
        # 6. 统计信息
        self.collect_statistics()
        
        # 7. 输出结果
        self.print_results()
        
        return len(self.issues) == 0
    
    def check_top_directories(self):
        """检查顶层目录是否完整"""
        print("📁 检查顶层目录结构...")
        
        existing_dirs = set()
        for item in RECORDS_DIR.iterdir():
            if item.is_dir():
                existing_dirs.add(item.name)
        
        # 检查必需目录
        for dir_name in EXPECTED_TOP_DIRS.keys():
            if dir_name not in existing_dirs:
                self.issues.append(f"❌ 缺少必需目录: {dir_name}")
            else:
                print(f"  ✅ {dir_name}")
        
        # 检查多余目录
        unexpected_dirs = existing_dirs - set(EXPECTED_TOP_DIRS.keys())
        if unexpected_dirs:
            for dir_name in unexpected_dirs:
                if not dir_name.startswith("."):  # 忽略隐藏目录
                    self.warnings.append(f"⚠️  未预期的目录: {dir_name}")
        
        print()
    
    def check_sub_directories(self):
        """检查子目录结构"""
        print("📂 检查子目录结构...")
        
        for parent_dir, expected_subs in EXPECTED_SUB_DIRS.items():
            parent_path = RECORDS_DIR / parent_dir
            if not parent_path.exists():
                continue
            
            print(f"  检查 {parent_dir}...")
            existing_subs = set()
            for item in parent_path.iterdir():
                if item.is_dir():
                    existing_subs.add(item.name)
            
            # 检查必需子目录
            for sub_dir in expected_subs.keys():
                if sub_dir not in existing_subs:
                    self.issues.append(f"❌ {parent_dir} 缺少子目录: {sub_dir}")
                else:
                    print(f"    ✅ {sub_dir}")
        
        print()
    
    def check_root_files(self):
        """检查根目录文件规范"""
        print("📄 检查根目录文件...")
        
        allowed_root_files = {"README.md", "项目状态.json"}
        
        for item in RECORDS_DIR.iterdir():
            if item.is_file():
                if item.name not in allowed_root_files:
                    self.issues.append(f"❌ 根目录不应包含文件: {item.name}")
                else:
                    print(f"  ✅ {item.name}")
                
                # 检查禁止的文件名模式
                for pattern in FORBIDDEN_ROOT_PATTERNS:
                    if pattern in item.name:
                        self.issues.append(
                            f"❌ 根目录文件名不符合规范: {item.name} (包含 '{pattern}')"
                        )
        
        print()
    
    def check_temporary_files(self):
        """检查临时文件和需要归档的文件"""
        print("🗑️  检查临时文件...")
        
        temp_keywords = ["临时", "temp", "测试", "test", "进度", "待办", "TODO"]
        
        for root, dirs, files in os.walk(RECORDS_DIR):
            # 跳过归档目录
            if "归档" in root or "archive" in root.lower():
                continue
            
            for file in files:
                if not file.endswith(".md"):
                    continue
                
                file_lower = file.lower()
                for keyword in temp_keywords:
                    if keyword in file_lower:
                        rel_path = os.path.relpath(
                            os.path.join(root, file), RECORDS_DIR
                        )
                        self.warnings.append(
                            f"⚠️  可能的临时文件: {rel_path}"
                        )
                        break
        
        print()
    
    def check_chat_logs(self):
        """检查聊天记录完整性"""
        print("💬 检查聊天记录...")
        
        chat_dir = RECORDS_DIR / "8-聊天记录"
        if not chat_dir.exists():
            self.issues.append("❌ 聊天记录目录不存在")
            return
        
        chat_files = list(chat_dir.glob("*.md"))
        self.stats["chat_logs"] = len(chat_files)
        
        # 检查是否有每日记录
        dates = set()
        for file in chat_files:
            # 解析文件名中的日期 YYYY-MM-DD
            try:
                date_str = file.stem.split("_")[0]
                dates.add(date_str)
                print(f"  ✅ {file.name}")
            except:
                self.warnings.append(f"⚠️  聊天记录文件名格式不规范: {file.name}")
        
        print(f"  找到 {len(dates)} 天的聊天记录")
        print()
    
    def collect_statistics(self):
        """收集统计信息"""
        print("📊 收集统计信息...")
        
        # 统计目录数
        self.stats["total_dirs"] = sum(
            1 for _ in RECORDS_DIR.rglob("*") if _.is_dir()
        )
        
        # 统计文件数
        self.stats["total_files"] = sum(
            1 for _ in RECORDS_DIR.rglob("*.md")
        )
        
        # 统计归档文件
        archive_dir = RECORDS_DIR / "1-归档"
        if archive_dir.exists():
            self.stats["archived_files"] = len(list(archive_dir.glob("*")))
        
        # 统计过程记录
        process_dir = RECORDS_DIR / "7-过程记录"
        if process_dir.exists():
            self.stats["process_records"] = len(list(process_dir.glob("*.md")))
        
        print()
    
    def print_results(self):
        """输出检查结果"""
        print("=" * 80)
        print("📈 检查结果")
        print("=" * 80)
        print()
        
        # 统计信息
        print("📊 统计信息:")
        print(f"  总目录数: {self.stats['total_dirs']}")
        print(f"  总文档数: {self.stats['total_files']}")
        print(f"  归档文件: {self.stats['archived_files']}")
        print(f"  过程记录: {self.stats['process_records']}")
        print(f"  聊天记录: {self.stats['chat_logs']} 天")
        print()
        
        # 问题
        if self.issues:
            print(f"❌ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"  {issue}")
            print()
        
        # 警告
        if self.warnings:
            print(f"⚠️  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        # 总结
        if not self.issues and not self.warnings:
            print("✅ 检查完成：目录结构完全符合规范！")
        elif not self.issues:
            print("✅ 检查完成：没有发现严重问题，有一些警告需要注意。")
        else:
            print("❌ 检查完成：发现问题需要修复！")
        
        print("=" * 80)
        
        # 保存检查报告
        self.save_report()
    
    def save_report(self):
        """保存检查报告"""
        # 保存到tests/test_reports/目录，而不是项目记录根目录
        report_dir = PROJECT_ROOT / "owlRD-prototype" / "tests" / "test_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "directory_check_report.json"
        
        report = {
            "check_time": datetime.now().isoformat(),
            "statistics": self.stats,
            "issues": self.issues,
            "warnings": self.warnings,
            "status": "pass" if not self.issues else "fail"
        }
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 检查报告已保存: {report_file}")


if __name__ == "__main__":
    checker = DirectoryStandardChecker()
    success = checker.check()
    exit(0 if success else 1)
