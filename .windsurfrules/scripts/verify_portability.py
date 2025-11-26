#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则系统移植性验证脚本
检查规则系统是否完全可移植
"""

import os
import sys
from pathlib import Path
import re

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class PortabilityChecker:
    """移植性检查器"""
    
    def __init__(self, rules_dir: Path):
        self.rules_dir = rules_dir
        self.issues = []
        self.warnings = []
        self.info = []
        
    def check_all(self):
        """执行所有检查"""
        print("🔍 开始检查规则系统移植性...")
        print(f"📁 规则目录: {self.rules_dir}\n")
        
        self.check_directory_structure()
        self.check_hardcoded_paths()
        self.check_external_dependencies()
        self.check_project_specific_content()
        
        self.print_results()
        
    def check_directory_structure(self):
        """检查目录结构完整性"""
        print("📋 检查1: 目录结构完整性")
        
        # 必需的规则文件
        required_files = [
            'README.md',
            '00-core-principles.md',
            '01-file-operations.md',
            '02-directory-management.md',
            '03-naming-convention.md',
            '04-git-workflow.md',
            '05-change-synchronization.md',
            'config.json',
            'project-config.example.md',
        ]
        
        missing_files = []
        for file in required_files:
            file_path = self.rules_dir / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            for file in missing_files:
                self.issues.append(f"❌ 缺少必需文件: {file}")
        else:
            self.info.append("✅ 所有必需文件完整")
        
        # 检查scripts目录
        scripts_dir = self.rules_dir / "scripts"
        if not scripts_dir.exists():
            self.issues.append("❌ 缺少scripts目录")
        else:
            self.info.append("✅ scripts目录存在")
        
        print("✅ 目录结构检查完成\n")
        
    def check_hardcoded_paths(self):
        """检查硬编码路径"""
        print("📋 检查2: 硬编码路径")
        
        # 搜索实际使用的硬编码路径（排除字符串模式定义）
        hardcoded_found = False
        
        # 检查所有Python文件
        scripts_dir = self.rules_dir / "scripts"
        if scripts_dir.exists():
            for py_file in scripts_dir.glob("*.py"):
                # 跳过本检测脚本自身
                if py_file.name == 'verify_portability.py':
                    continue
                    
                content = py_file.read_text(encoding='utf-8')
                
                # 查找实际的绝对路径赋值（不是正则模式）
                # 例如: path = "C:\some\path" 或 path = "/home/user"
                patterns = [
                    r'=\s*["\'][A-Za-z]:\\[^"\']*["\']',  # Windows: = "C:\..."
                    r'=\s*["\']\/home\/[^"\']*["\']',     # Linux: = "/home/..."
                    r'=\s*["\']\/Users\/[^"\']*["\']',    # Mac: = "/Users/..."
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        for match in matches:
                            if not self._is_in_comment(content, match):
                                self.warnings.append(f"⚠️ 硬编码路径在 {py_file.name}: {match}")
                                hardcoded_found = True
        
        if not hardcoded_found:
            self.info.append("✅ 未发现硬编码路径")
        
        print("✅ 硬编码路径检查完成\n")
        
    def _is_in_comment(self, content: str, pattern: str) -> bool:
        """检查模式是否在注释中"""
        lines = content.split('\n')
        for line in lines:
            if pattern in line and line.strip().startswith('#'):
                return True
        return False
        
    def check_external_dependencies(self):
        """检查外部依赖"""
        print("📋 检查3: 外部依赖")
        
        # 检查scripts中的import语句
        scripts_dir = self.rules_dir / "scripts"
        if scripts_dir.exists():
            external_imports = set()
            standard_libs = {
                'os', 'sys', 'json', 'pathlib', 'datetime', 're', 
                'shutil', 'time', 'io', 'typing', 'traceback', 'subprocess'
            }
            # 允许的外部库（规则系统使用的）
            allowed_external = {
                'watchdog',     # 文件监控（可选功能）
                'jsonschema',   # JSON验证
                'pytest',       # 测试框架
            }
            # 内部模块（规则系统脚本）
            internal_modules = {
                'check_project_structure', 'check_directory_standards',
                'update_project_status', 'verify_portability', 'watch_and_check',
                'install_git_hooks', 'init_project_from_template',
                '_config',      # 脚本配置模块
            }
            # 项目代码模块（init脚本生成的示例代码）
            project_code_modules = {
                'app',          # FastAPI应用
                'uvicorn',      # ASGI服务器
                'fastapi',      # FastAPI框架
                'pydantic',     # 数据验证
            }
            
            for py_file in scripts_dir.glob("*.py"):
                content = py_file.read_text(encoding='utf-8')
                # 查找import语句
                import_matches = re.findall(r'^\s*import\s+(\w+)', content, re.MULTILINE)
                from_matches = re.findall(r'^\s*from\s+(\w+)', content, re.MULTILINE)
                
                all_imports = set(import_matches + from_matches)
                for imp in all_imports:
                    if (imp not in standard_libs and 
                        imp not in allowed_external and 
                        imp not in internal_modules and
                        imp not in project_code_modules):
                        external_imports.add(imp)
            
            if external_imports:
                for imp in external_imports:
                    self.warnings.append(f"⚠️ 未知外部依赖: {imp}")
            
            # 报告已知的外部依赖
            self.info.append("✅ 主要依赖: Python标准库")
            self.info.append("ℹ️ 可选依赖: watchdog (文件监控功能)")
        
        print("✅ 外部依赖检查完成\n")
        
    def check_project_specific_content(self):
        """检查项目特定内容"""
        print("📋 检查4: 项目特定内容")
        
        needs_modification = []
        
        # 1. 检查必须修改的配置文件
        config_file = self.rules_dir / "project-config.md"
        if config_file.exists():
            self.info.append("ℹ️ project-config.md 需要根据新项目修改")
            needs_modification.append("project-config.md (项目特定配置)")
        
        # 2. 检查需要调整的脚本（仅检查allowed_items）
        check_script = self.rules_dir / "scripts" / "check_project_structure.py"
        if check_script.exists():
            content = check_script.read_text(encoding='utf-8')
            if "'owlRD-prototype'" in content:
                needs_modification.append("check_project_structure.py (allowed_items中的代码目录名)")
        
        # 3. 检查可选修改的脚本
        update_script = self.rules_dir / "scripts" / "update_project_status.py"
        if update_script.exists():
            self.info.append("ℹ️ update_project_status.py 是可选功能，如使用需调整目录名")
        
        # 报告需要修改的文件
        if needs_modification:
            self.info.append("📝 移植时需要修改的文件:")
            for item in needs_modification:
                self.info.append(f"  • {item}")
        
        # 模板文件
        if (self.rules_dir / "project-config.example.md").exists():
            self.info.append("✅ 提供了 project-config.example.md 作为模板")
        
        print("✅ 项目特定内容检查完成\n")
        
    def print_results(self):
        """打印检查结果"""
        print("\n" + "="*60)
        print("📊 移植性检查结果")
        print("="*60 + "\n")
        
        # 问题
        if self.issues:
            print(f"❌ 发现 {len(self.issues)} 个问题:\n")
            for issue in self.issues:
                print(f"  {issue}")
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
        if not self.issues:
            if not self.warnings:
                print("🎉 完美！规则系统完全可移植，无需任何修改！")
            else:
                print("✅ 规则系统可移植，移植时需要修改配置文件")
        else:
            print("⚠️ 规则系统存在问题，请修复后再移植")
        print("="*60 + "\n")
        
        # 移植性评分
        self.calculate_score()
        
    def calculate_score(self):
        """计算移植性评分"""
        max_score = 100
        deductions = 0
        
        # 严重问题扣分
        deductions += len(self.issues) * 30
        
        # 警告扣分（区分严重程度）
        for warning in self.warnings:
            if '硬编码路径' in warning:
                deductions += 15  # 硬编码路径较严重
            elif '未知外部依赖' in warning:
                deductions += 10  # 未知依赖中等
        
        score = max(0, max_score - deductions)
        
        print("📊 移植性评分:")
        if score >= 95:
            rating = "⭐⭐⭐⭐⭐ 完美"
            comment = "规则系统设计优秀，完全可移植！"
        elif score >= 85:
            rating = "⭐⭐⭐⭐⭐ 优秀"
            comment = "移植性非常好，仅需简单配置"
        elif score >= 75:
            rating = "⭐⭐⭐⭐ 良好"
            comment = "移植性良好，需要一些调整"
        elif score >= 60:
            rating = "⭐⭐⭐ 一般"
            comment = "可以移植，但需要较多修改"
        else:
            rating = "⭐⭐ 需改进"
            comment = "存在较多问题，建议优化后再移植"
        
        print(f"  分数: {score}/100 {rating}")
        print(f"  评价: {comment}")
        print()


def main():
    """主函数"""
    # 获取规则目录
    script_dir = Path(__file__).parent  # scripts/
    rules_dir = script_dir.parent  # .windsurfrules/
    
    # 创建检查器并执行
    checker = PortabilityChecker(rules_dir)
    checker.check_all()
    
    # 返回错误码
    sys.exit(1 if checker.issues else 0)


if __name__ == "__main__":
    main()
