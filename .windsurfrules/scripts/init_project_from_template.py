#!/usr/bin/env python3
"""
项目初始化脚本 - 根据通用架构模板创建新项目

用法:
    python init_project_from_template.py <项目名> [项目路径]
    
示例:
    python init_project_from_template.py MyNewAPI D:\Projects
    python init_project_from_template.py MyCodingDict  # 在当前目录创建
"""

import sys
import os
from pathlib import Path
from datetime import datetime


class ProjectInitializer:
    """项目初始化器"""
    
    def __init__(self, project_name: str, project_path: str = "."):
        self.project_name = project_name
        self.base_path = Path(project_path) / project_name
        self.creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def create_directory_structure(self):
        """创建目录结构"""
        print(f"📁 创建项目目录结构: {self.base_path}")
        
        # 核心目录（必需）
        core_dirs = [
            'data',                    # 核心数据目录（可改名为coding_dictionary等）
            'schema',                  # JSON Schema定义
            'spec',                    # 规范文档
            'scripts',                 # 维护脚本
            'tests',                   # 测试文件
            'examples',                # 示例代码
            'image/README',            # 图片资源
        ]
        
        # 文档目录（推荐）
        doc_dirs = [
            '项目文档',
        ]
        
        # 可选目录
        optional_dirs = [
            '项目备份',
            '归档文件',
            '测试报告',
            '自动生成文档',
        ]
        
        # 创建所有目录
        all_dirs = core_dirs + doc_dirs + optional_dirs
        for dir_name in all_dirs:
            dir_path = self.base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_name}/")
        
        print()
        
    def create_core_files(self):
        """创建核心文件"""
        print("📄 创建核心文件...")
        
        files = {
            'README.md': self._generate_readme(),
            'app.py': self._generate_app(),
            'requirements.txt': self._generate_requirements(),
            '.gitignore': self._generate_gitignore(),
            'pytest.ini': self._generate_pytest_ini(),
            'start_api.bat': self._generate_start_script(),
        }
        
        for filename, content in files.items():
            file_path = self.base_path / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ {filename}")
        
        print()
        
    def create_data_files(self):
        """创建示例数据文件"""
        print("📊 创建示例数据文件...")
        
        # 主数据文件
        data_file = self.base_path / 'data' / 'data.json'
        data_file.write_text('[]', encoding='utf-8')
        print(f"  ✅ data/data.json")
        
        # Schema文件
        schema_file = self.base_path / 'schema' / 'data.schema.json'
        schema_content = '''{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "数据Schema",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": {"type": "string"},
      "name": {"type": "string"}
    },
    "required": ["id", "name"]
  }
}'''
        schema_file.write_text(schema_content, encoding='utf-8')
        print(f"  ✅ schema/data.schema.json")
        
        print()
        
    def create_script_files(self):
        """创建基础脚本"""
        print("🔧 创建维护脚本...")
        
        scripts = {
            '_config.py': self._generate_config_script(),
            'validate_data.py': self._generate_validate_script(),
        }
        
        for filename, content in scripts.items():
            file_path = self.base_path / 'scripts' / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ scripts/{filename}")
        
        print()
        
    def create_test_files(self):
        """创建测试文件"""
        print("🧪 创建测试文件...")
        
        tests = {
            'conftest.py': self._generate_conftest(),
            'test_api.py': self._generate_test_api(),
        }
        
        for filename, content in tests.items():
            file_path = self.base_path / 'tests' / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ tests/{filename}")
        
        print()
        
    def print_next_steps(self):
        """打印后续步骤"""
        print("=" * 70)
        print("🎉 项目初始化完成！")
        print("=" * 70)
        print()
        print(f"📁 项目位置: {self.base_path}")
        print()
        print("📝 下一步操作:")
        print()
        print("1️⃣ 进入项目目录:")
        print(f"   cd {self.base_path}")
        print()
        print("2️⃣ 创建虚拟环境:")
        print("   python -m venv .venv")
        print("   .venv\\Scripts\\activate  # Windows")
        print()
        print("3️⃣ 安装依赖:")
        print("   pip install -r requirements.txt")
        print()
        print("4️⃣ 复制规则系统 (重要!):")
        print("   xcopy path\\to\\.windsurfrules .windsurfrules\\ /E /I")
        print("   # 或从已有项目复制")
        print()
        print("5️⃣ 修改规则系统配置:")
        print("   编辑 .windsurfrules/project-config.md")
        print("   编辑 .windsurfrules/scripts/check_project_structure.py")
        print()
        print("6️⃣ 初始化Git:")
        print("   git init")
        print("   git add .")
        print('   git commit -m "Initial commit"')
        print()
        print("7️⃣ 启动开发:")
        print("   python app.py")
        print("   # 或")
        print("   start_api.bat")
        print()
        print("=" * 70)
        
    def run(self):
        """执行初始化"""
        print()
        print("=" * 70)
        print(f"🚀 初始化项目: {self.project_name}")
        print("=" * 70)
        print()
        
        # 检查目录是否已存在
        if self.base_path.exists():
            print(f"❌ 错误: 目录已存在 {self.base_path}")
            print("   请选择其他项目名或删除现有目录")
            return False
        
        try:
            self.create_directory_structure()
            self.create_core_files()
            self.create_data_files()
            self.create_script_files()
            self.create_test_files()
            self.print_next_steps()
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    # ========== 文件内容生成器 ==========
    
    def _generate_readme(self):
        """生成README"""
        return f'''# {self.project_name}

**创建日期**: {self.creation_time}  
**项目类型**: FastAPI REST API + 数据字典  

---

## 📖 项目简介

{self.project_name} 是基于通用架构模板创建的Python API项目。

**核心特性**:
- 🎯 FastAPI REST API服务
- 🔒 JSON Schema数据验证
- 🧪 完整测试覆盖
- 📖 自动文档生成
- ⭐ AI规则系统集成

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
.venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方法1: 直接运行
python app.py

# 方法2: 使用脚本
start_api.bat
```

### 3. 访问API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 📁 项目结构

```
{self.project_name}/
├── app.py                  # FastAPI主应用
├── data/                   # 核心数据
├── schema/                 # JSON Schema
├── scripts/                # 维护脚本
├── tests/                  # 测试文件
└── .windsurfrules/         # AI规则系统
```

详细结构参见: `.windsurfrules/06-directory-architecture-template.md`

---

## 🔧 开发指南

### 数据验证

```bash
python scripts/validate_data.py
```

### 运行测试

```bash
pytest tests/
```

### 检查项目结构

```bash
python .windsurfrules/scripts/check_project_structure.py
```

---

## 📚 文档

- [API文档](./项目文档/)
- [架构模板](./.windsurfrules/06-directory-architecture-template.md)
- [开发规范](./.windsurfrules/README.md)

---

## 📝 变更日志

### v1.0.0 ({self.creation_time[:10]})
- 🎉 项目初始化
- ✅ 基础架构搭建

---

**维护者**: Your Name  
**许可证**: MIT
'''
    
    def _generate_app(self):
        """生成FastAPI应用"""
        return f'''#!/usr/bin/env python3
"""
{self.project_name} - FastAPI主应用

创建日期: {self.creation_time}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="{self.project_name}",
    version="1.0.0",
    description="{self.project_name} API服务",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {{
        "message": "Welcome to {self.project_name} API",
        "docs": "/docs",
        "health": "/health"
    }}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {{"status": "healthy", "service": "{self.project_name}"}}


@app.get("/api/v1/data")
async def get_data():
    """获取数据"""
    # TODO: 实现数据查询逻辑
    return {{"data": []}}


if __name__ == "__main__":
    print("🚀 启动 {self.project_name} API服务...")
    print("📖 API文档: http://localhost:8000/docs")
    print("💚 健康检查: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式自动重载
    )
'''
    
    def _generate_requirements(self):
        """生成依赖文件"""
        return '''# FastAPI核心
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# 数据验证
jsonschema==4.20.0

# 测试
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1

# 开发工具
black==23.11.0
flake8==6.1.0
'''
    
    def _generate_gitignore(self):
        """生成.gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# 测试
.pytest_cache/
.coverage
htmlcov/
测试报告/

# 日志
*.log

# 环境变量
.env
.env.local

# 构建
build/
dist/
*.egg-info/

# 临时文件
*.tmp
*.temp
~*
'''
    
    def _generate_pytest_ini(self):
        """生成pytest配置"""
        return '''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
asyncio_mode = auto
'''
    
    def _generate_start_script(self):
        """生成启动脚本"""
        return f'''@echo off
REM {self.project_name} 快速启动脚本
REM 创建日期: {self.creation_time}

echo.
echo ========================================
echo   {self.project_name} API 服务
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\\Scripts\\activate.bat" (
    echo [警告] 虚拟环境不存在
    echo [提示] 请先运行: python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\\Scripts\\activate.bat

REM 启动服务
echo [启动] 正在启动API服务...
echo.
python app.py

pause
'''
    
    def _generate_config_script(self):
        """生成配置脚本"""
        return f'''#!/usr/bin/env python3
"""
项目配置 - 单一事实源

创建日期: {self.creation_time}
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 目录路径
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_DIR = PROJECT_ROOT / "schema"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "项目文档"

# 文件路径
DATA_FILE = DATA_DIR / "data.json"
SCHEMA_FILE = SCHEMA_DIR / "data.schema.json"

# 配置参数
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# 验证目录存在
def ensure_directories():
    """确保必需目录存在"""
    for dir_path in [DATA_DIR, SCHEMA_DIR, TESTS_DIR, DOCS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print(f"📁 项目根目录: {{PROJECT_ROOT}}")
    print(f"📊 数据目录: {{DATA_DIR}}")
    print(f"📋 Schema目录: {{SCHEMA_DIR}}")
    ensure_directories()
'''
    
    def _generate_validate_script(self):
        """生成验证脚本"""
        return f'''#!/usr/bin/env python3
"""
数据验证工具

用法: python validate_data.py
"""

import json
import jsonschema
from pathlib import Path
from _config import DATA_FILE, SCHEMA_FILE


def validate_data():
    """验证数据文件"""
    print("🔍 开始验证数据...")
    
    # 读取Schema
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema文件不存在: {{SCHEMA_FILE}}")
        return False
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # 读取数据
    if not DATA_FILE.exists():
        print(f"❌ 数据文件不存在: {{DATA_FILE}}")
        return False
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 验证
    try:
        jsonschema.validate(data, schema)
        print(f"✅ 数据验证通过！")
        print(f"   数据条目: {{len(data) if isinstance(data, list) else 1}}")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ 数据验证失败:")
        print(f"   {{e.message}}")
        return False


if __name__ == "__main__":
    import sys
    success = validate_data()
    sys.exit(0 if success else 1)
'''
    
    def _generate_conftest(self):
        """生成pytest配置"""
        return '''"""Pytest配置和fixture"""
import pytest


@pytest.fixture
def sample_data():
    """示例数据fixture"""
    return []


@pytest.fixture
def api_client():
    """API客户端fixture"""
    from fastapi.testclient import TestClient
    from app import app
    return TestClient(app)
'''
    
    def _generate_test_api(self):
        """生成API测试"""
        return f'''"""API测试"""
import pytest


def test_root_endpoint(api_client):
    """测试根路径"""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_health_check(api_client):
    """测试健康检查"""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_data(api_client):
    """测试数据获取"""
    response = api_client.get("/api/v1/data")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
'''


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python init_project_from_template.py <项目名> [项目路径]")
        print()
        print("示例:")
        print("  python init_project_from_template.py MyNewAPI")
        print("  python init_project_from_template.py MyCodingDict D:\\Projects")
        sys.exit(1)
    
    project_name = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    initializer = ProjectInitializer(project_name, project_path)
    success = initializer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
