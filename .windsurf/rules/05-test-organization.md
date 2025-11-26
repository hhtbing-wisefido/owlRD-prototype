---
title: "Test Organization"
description: "测试组织规范"
trigger: always
---

# 05 - 测试组织规范

**规则类别**: 强制执行  
**适用范围**: 所有包含测试的项目  
**优先�?*: 🔴 �? 
**版本**: v1.0  
**创建日期**: 2025-11-26  

---

## 📋 目录

- [核心原则](#核心原则)
- [标准目录结构](#标准目录结构)
- [错误的放置位置](#错误的放置位�?
- [正确的放置位置](#正确的放置位�?
- [.gitignore规则](#gitignore规则)
- [AI规则遵守](#ai规则遵守)
- [自动检查](#自动检�?
- [示例场景](#示例场景)

---

## 🎯 核心原则

### 原则1: 测试产物归属原则 🎯

**规则**: 测试产生的所有产物必须放�?`tests/` 目录�?

**理由**:
- �?测试报告是测试的产物
- �?与测试代码保持逻辑关联
- �?便于统一管理和清�?
- �?符合单一职责原则
- �?易于.gitignore配置

**核心逻辑**:
```
测试代码 �?tests/test_*.py
测试产物 �?tests/test_reports/
         └─ 与测试代码在同一目录树下
```

---

## 🗂�?标准目录结构

### Python项目（pytest�?

```
{项目名}-prototype/
└── tests/                      # 测试根目�?
    ├── test_*.py               # 测试文件
    ├── conftest.py             # pytest配置
    ├── README.md               # 测试文档
    �?
    ├── unit/                   # 单元测试（可选）
    �?  └── test_*.py
    �?
    ├── integration/            # 集成测试（可选）
    �?  └── test_*.py
    �?
    ├── e2e/                    # 端到端测试（可选）
    �?  └── test_*.py
    �?
    ├── fixtures/               # 测试fixtures（可选）
    �?  └── *.json
    �?
    ├── test_data/              # 测试数据（可选）
    �?  └── *.json
    �?
    └── test_reports/           # �?测试报告（gitignored�?
        ├── coverage/           # 覆盖率报�?
        �?  ├── index.html
        �?  └── ...
        ├── pytest_report.html  # pytest HTML报告
        ├── junit.xml           # JUnit格式报告
        └── test_results.json   # JSON格式报告
```

### JavaScript/Node.js项目（Jest/Vitest�?

```
{项目名}-frontend/
└── tests/
    ├── *.test.js               # 测试文件
    ├── setup.js                # 测试配置
    └── test_reports/           # 测试报告
        ├── coverage/           # 覆盖率报�?
        └── test-report.html    # HTML报告
```

### 全栈项目

```
{项目名}-prototype/
├── backend/
�?  └── tests/
�?      ├── test_*.py
�?      └── test_reports/      # 后端测试报告
�?
└── frontend/
    └── tests/
        ├── *.test.js
        └── test_reports/      # 前端测试报告
```

---

## �?错误的放置位�?

### 错误1: 与tests/并列 �?

```
{项目名}-prototype/
├── tests/              �?测试代码
└── test_reports/       �?错误！应该在tests/�?
```

**问题**:
- �?测试报告与测试代码分�?
- �?目录结构不清�?
- �?违反逻辑归属原则
- �?难以统一管理

---

### 错误2: 在根目录 �?

```
项目根目�?
├── {项目名}-prototype/
├── 项目记录/
└── 测试报告/           �?严重错误！违反根目录清洁规则
```

**问题**:
- �?严重违反根目录清洁规�?
- �?测试报告与代码完全分�?
- �?不符合架构模�?
- �?混淆�?测试报告"�?项目文档"的概�?

---

### 错误3: 在项目记�?�?�?

```
项目记录/
└── 测试报告/           �?错误！测试报告不是项目文�?
```

**问题**:
- �?测试报告是临时产物，不是文档
- �?应该在代码目录下，而非文档目录
- �?违反了项目记�?�?大分类定�?

---

## �?正确的放置位�?

```
{项目名}-prototype/
└── tests/
    ├── test_api.py          �?测试代码
    ├── test_models.py       �?测试代码
    └── test_reports/        �?测试报告（与测试代码在一起）
        ├── coverage/
        �?  ├── index.html
        �?  └── coverage.json
        ├── pytest_report.html
        ├── junit.xml
        └── test_results.json
```

**优点**:
- �?测试代码和报告在一�?
- �?逻辑清晰，符合归属原�?
- �?便于管理和清�?
- �?符合架构模板
- �?易于.gitignore配置

---

## 🔒 .gitignore规则

### 必须配置

测试报告不应该提交到Git，必须添加到 `.gitignore`:

```gitignore
# 测试报告（在tests/下）
**/tests/test_reports/
**/tests/coverage/
**/tests/.pytest_cache/
**/tests/__pycache__/
**/tests/*.xml
**/tests/*.html

# 或者针对特定项�?
{项目名}-prototype/tests/test_reports/
{项目名}-prototype/tests/coverage/
```

### 不要配置

�?**错误**：在根目录配�?
```gitignore
test_reports/     # �?这样无法匹配正确位置
测试报告/         # �?这是严重错误，不应该在根目录
```

---

## 🤖 AI规则遵守

### @rules:all - AI必须遵守的规�?

当AI被要求移动、创建或组织测试报告时：

#### 规则A: 检查测试报告位�?�?

**必须执行**:
```
1. 检查测试报告是否在 tests/ 目录�?
2. 如不在，确定正确位置
3. 迁移到正确位�?
4. 验证.gitignore配置
```

#### 规则B: 正确的放置位�?�?

**唯一允许的位�?*:
```
�?{项目名}-prototype/tests/test_reports/
�?{项目名}-backend/tests/test_reports/
�?{项目名}-frontend/tests/test_reports/
```

**严格禁止的位�?*:
```
�?{项目名}-prototype/test_reports/     # 与tests/并列
�?项目根目�?测试报告/                  # 在根目录
�?项目根目�?test_reports/             # 在根目录
�?项目记录/测试报告/                   # 在项目记录下
```

#### 规则C: 验证.gitignore �?

**必须确保**:
```gitignore
**/tests/test_reports/
**/tests/coverage/
```

### AI操作清单

移动测试报告时，AI必须�?

```bash
# �?正确操作
Move-Item "test_reports" "{项目名}-prototype/tests/test_reports"

# �?验证.gitignore
Add-Content .gitignore "**/tests/test_reports/"

# �?错误操作
Move-Item "测试报告" "."                              # 移到根目�?
Move-Item "test_reports" "{项目名}-prototype/"       # 与tests/并列
Move-Item "测试报告" "项目记录/"                      # 移到项目记录
```

### AI自检清单

- [ ] 测试报告�?`tests/` 目录下？
- [ ] 没有在根目录�?
- [ ] 没有�?`tests/` 并列�?
- [ ] 没有在项目记�?下？
- [ ] `.gitignore` 配置正确�?
- [ ] 路径使用 `**/tests/test_reports/` 模式�?

---

## 🔍 自动检�?

### check_project_structure.py 增强

```python
def check_test_reports_location(self):
    """检查测试报告位�?""
    print("📋 检�? 测试报告位置")
    
    # 查找代码主目�?
    code_patterns = ['*-prototype', '*-backend', '*-frontend', 
                    '*-api', '*-dict', '*-coding-dict']
    
    code_dirs = []
    for pattern in code_patterns:
        code_dirs.extend(list(self.project_root.glob(pattern)))
    
    for code_dir in code_dirs:
        # 检查是否有tests/目录
        tests_dir = code_dir / "tests"
        if not tests_dir.exists():
            continue
        
        # 正确位置
        correct_location = tests_dir / "test_reports"
        
        # 检查是否错误放在代码目录下（与tests/并列�?
        wrong_location = code_dir / "test_reports"
        if wrong_location.exists():
            self.errors.append(
                f"�?测试报告位置错误: {wrong_location.relative_to(self.project_root)}\n"
                f"   应该移动�? {correct_location.relative_to(self.project_root)}"
            )
    
    # 检查根目录
    root_test_reports = [
        self.project_root / "test_reports",
        self.project_root / "测试报告",
        self.project_root / "Test_Reports"
    ]
    
    for wrong_dir in root_test_reports:
        if wrong_dir.exists():
            self.errors.append(
                f"�?严重违规：测试报告在根目�? {wrong_dir.name}\n"
                f"   违反根目录清洁规则！\n"
                f"   应该移动�? <项目代码目录>/tests/test_reports/"
            )
    
    print("�?测试报告位置检查完成\n")
```

### 手动检�?

```bash
# 检查test_reports位置
find . -name "test_reports" -type d

# 正确位置应该显示
./owlRD-prototype/tests/test_reports  �?

# 错误位置
./owlRD-prototype/test_reports         �?与tests/并列
./test_reports                         �?在根目录
./测试报告                             �?在根目录
```

---

## 📝 示例场景

### 场景1: Python项目（pytest�?

#### pytest.ini配置

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 报告输出配置 - 全部输出到tests/test_reports/
addopts = 
    --html=tests/test_reports/pytest_report.html
    --self-contained-html
    --junitxml=tests/test_reports/junit.xml
    --cov=app
    --cov-report=html:tests/test_reports/coverage
    --cov-report=json:tests/test_reports/coverage.json
```

#### 运行测试

```bash
# 运行测试
pytest

# 查看覆盖率报�?
open tests/test_reports/coverage/index.html

# 查看pytest报告
open tests/test_reports/pytest_report.html
```

---

### 场景2: Node.js项目（Jest�?

#### jest.config.js配置

```javascript
module.exports = {
  testMatch: ["**/tests/**/*.test.js"],
  coverageDirectory: "tests/test_reports/coverage",
  reporters: [
    "default",
    ["jest-html-reporter", {
      outputPath: "tests/test_reports/test-report.html"
    }],
    ["jest-junit", {
      outputDirectory: "tests/test_reports",
      outputName: "junit.xml"
    }]
  ]
};
```

#### package.json脚本

```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch"
  }
}
```

---

### 场景3: Vitest项目

#### vitest.config.js配置

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reportsDirectory: 'tests/test_reports/coverage',
      reporter: ['html', 'json', 'text']
    },
    reporters: ['default', 'html'],
    outputFile: {
      html: 'tests/test_reports/test-report.html'
    }
  }
});
```

---

## 🚨 违规处理

### 发现违规

如果发现测试报告位置错误�?

1. **立即报错** - 检查脚本必须报�?
2. **提供解决方案** - 告知正确位置
3. **停止执行** - 不通过检�?

### 修正步骤

```bash
# 场景1: 测试报告在代码目录下（与tests/并列�?
# 当前错误位置: owlRD-prototype/test_reports/
# 正确位置: owlRD-prototype/tests/test_reports/

# 1. 移动到正确位�?
Move-Item "owlRD-prototype/test_reports" "owlRD-prototype/tests/test_reports"

# 2. 更新.gitignore
echo "**/tests/test_reports/" >> .gitignore

# 3. 验证
python .windsurf/scripts/check_project_structure.py
```

```bash
# 场景2: 测试报告在根目录
# 当前错误位置: 测试报告/
# 正确位置: owlRD-prototype/tests/test_reports/

# 1. 移动到正确位�?
Move-Item "测试报告" "owlRD-prototype/tests/test_reports"

# 2. 更新.gitignore（如果还没有�?
echo "**/tests/test_reports/" >> .gitignore

# 3. 验证
python .windsurf/scripts/check_project_structure.py
```

---

## 🎯 测试报告 vs 测试文档

### 明确区分

| 类型 | 位置 | 提交Git | 说明 |
|------|------|---------|------|
| **测试报告** | `tests/test_reports/` | �?不提�?| 临时产物，每次运行生�?|
| **测试文档** | `项目记录/3-功能说明/测试文档/` | �?提交 | 永久文档，说明如何测�?|

### 测试报告（临时产物）

```
tests/test_reports/
├── coverage/              # 覆盖率报告（每次运行生成�?
├── pytest_report.html     # pytest报告（每次运行生成）
└── junit.xml             # CI/CD用报告（每次运行生成�?

特点�?
- �?不提交到Git�?gitignored�?
- 🔄 每次测试运行重新生成
- 📊 用于查看最新测试结�?
```

### 测试文档（永久文档）

```
项目记录/3-功能说明/
└── 测试指南.md             # 如何运行测试（提交到Git�?
    ├── 测试环境配置
    ├── 测试运行方法
    ├── 测试用例说明
    └── 测试报告解读

特点�?
- �?提交到Git
- 📝 永久保存
- 📖 说明性文�?
```

---

## 📚 相关规则

- **02-directory-management.md** - 目录管理规范
- **06-directory-architecture-template.md** - 架构模板
- **07-strict-directory-control.md** - 严格目录控制

---

## �?检查清�?

项目测试组织检查清单：

- [ ] 测试报告�?`tests/test_reports/` �?
- [ ] 没有在根目录
- [ ] 没有�?`tests/` 并列
- [ ] 没有在项目记�?�?
- [ ] `.gitignore` 正确配置 `**/tests/test_reports/`
- [ ] 测试配置文件指向正确路径
- [ ] README.md 说明测试报告位置（如需要）

---

## 🎯 总结

### 核心规则

**测试报告必须放在 `tests/` 目录�?*

### 正确位置

```
{项目名}-prototype/tests/test_reports/
{项目名}-backend/tests/test_reports/
{项目名}-frontend/tests/test_reports/
```

### AI必须遵守

移动测试报告时，必须放在 `tests/` 下，严禁放在根目录或与tests/并列

### 自动检�?

检查脚本会验证位置是否正确，违规立即报�?

---

**规则版本**: v1.0  
**创建日期**: 2025-11-26  
**最后更�?*: 2025-11-26  
**规则状�?*: �?生效  
**强制级别**: 🔴 必须遵守  
**适用范围**: 所有包含测试的项目

🎯 **AI注意**: 这是 @rules:all 的一部分，AI必须严格遵守�?
