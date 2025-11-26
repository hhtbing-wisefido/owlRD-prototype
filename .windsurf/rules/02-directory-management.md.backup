---
title: "Directory Management"
description: "目录管理规范"
trigger: always
---

# 📁 目录管理规范

**规则类型**: 通用规则 �? 
**强制级别**: 🔴 严格执行  
**适用场景**: 目录创建、组织和维护  
**版本**: v1.0.0  

---

## 📋 目录

- [核心原则](#核心原则)
- [根目录管理原则](#根目录管理原�?
- [目录分类方法](#目录分类方法)
- [目录命名规范](#目录命名规范)
- [目录层级控制](#目录层级控制)
- [禁止的目录操作](#禁止的目录操�?
- [目录结构最佳实践](#目录结构最佳实�?
- [目录维护指南](#目录维护指南)

---

## 🎯 核心原则

### 三大核心原则

#### 1. 📐 **简洁清�?* (Keep It Simple)
```
�?好的目录结构:
project/
├── src/           # 源代�?
├── docs/          # 文档
├── tests/         # 测试
└── scripts/       # 脚本

�?糟糕的目录结�?
project/
├── source_code/
├── source-files/
├── src/
├── code/
├── all_the_code/
└── my_project_source/
```

**原则**: 每个目的只有一个目录，避免功能重复

#### 2. 🎨 **分类明确** (Clear Categorization)
```
根据功能、类型、模块等清晰分类
避免"杂物抽屉"式的目录（misc/, other/, stuff/�?
```

**示例**:
```
�?正确分类:
docs/
├── api/          # API文档
├── guides/       # 使用指南
└── tutorials/    # 教程

�?模糊分类:
docs/
├── files/        # 什么文件？
├── stuff/        # 什么东西？
└── others/       # 太模糊了
```

#### 3. 🏗�?**结构稳定** (Stable Structure)
```
目录结构应该相对稳定
避免频繁创建、删除、重命名顶层目录
新需求优先使用现有目录的子目�?
```

---

## 🏠 根目录管理原�?

### 什么是根目录？

**项目根目�?* = 项目的最顶层目录，通常包含 `.git/` 文件夹的目录

### �?根目录应该包含什�?

#### 1. **必需的配置文�?*
```
.gitignore          # Git忽略规则
README.md           # 项目说明
LICENSE             # 许可证（如适用�?
```

#### 2. **项目管理文件**（可选）
```
.editorconfig       # 编辑器配�?
.prettierrc         # 代码格式化配�?
pyproject.toml      # Python项目配置
package.json        # Node.js项目配置
Cargo.toml          # Rust项目配置
pom.xml            # Java Maven配置
```

#### 3. **主要目录**
```
根据 project-config.md 定义的目录结�?
通常包括:
├── [代码主目录]/
├── [文档主目录]/
├── 知识�?                  �?只读参考（标配�?
├── [测试目录]/
├── [脚本目录]/
└── .windsurf/
```

**知识库目�?* 🔒:
- 所有项目的标准配置目录
- 存放源参考文件、技术文档、学习资�?
- 只读属�?- 只允许添加新文件，不允许修改、删除已有文�?
- 详见 project-config.md 中的知识库规�?

**.windsurf目录** 🔧:
- 规则系统专用目录
- 必须保持简洁专注，只包含规则系统本�?
- 详见下方".windsurf目录管理规则"

### �?根目录严格禁�?

#### 1. **禁止文档文件堆积**
```
�?错误:
/
├── README.md               �?允许
├── 功能说明.md             �?禁止
├── 部署指南.md             �?禁止
├── API文档.md              �?禁止
└── 开发笔�?md             �?禁止

�?正确:
/
├── README.md               �?项目总说�?
└── docs/                   �?文档目录
    ├── 功能说明.md
    ├── 部署指南.md
    ├── API文档.md
    └── 开发笔�?md
```

#### 2. **禁止临时文件**
```
�?禁止:
├── 临时笔记.txt
├── TODO.md
├── test.py
├── 新建文档.md
├── backup_20251125.zip
└── output.log

�?应该:
- 临时文件放在 .gitignore 的目录中
- 或者及时清�?
- 或者放在专门的临时目录
```

#### 3. **禁止数据文件**
```
�?禁止:
├── data.json
├── users.csv
├── database.sqlite
└── export_results.xlsx

�?应该:
- 示例数据 �?[代码目录]/data/
- 测试数据 �?tests/fixtures/
- 实际数据 �?添加�?.gitignore
```

#### 4. **禁止构建产物**
```
�?禁止:
├── dist/
├── build/
├── *.pyc
├── node_modules/
└── target/

�?应该:
- 添加�?.gitignore
- 或者在 CI/CD 中生�?
```

#### 5. **禁止随意创建顶层目录**
```
�?禁止:
├── my_scripts/       # 已有 scripts/
├── documents/        # 已有 docs/
├── temporary/        # 应该 .gitignore
├── backup/           # 应该 .gitignore
└── old_code/         # 应该删除或归�?

�?原则:
- 新目录必须有充分理由
- 优先使用现有目录的子目录
- 参�?project-config.md 定义
```

### 📊 根目录清洁度检�?

```markdown
根目录清洁度评分:

- 📁 只有 README.md + 配置文件 + 主要目录 = ⭐⭐⭐⭐�?(100�?
- 📁 有少量临时文�?(1-2�? = ⭐⭐⭐⭐ (80�?
- 📁 有多个文档文�?(3-5�? = ⭐⭐�?(60�?
- 📁 文件杂乱 (>10个文�? = ⭐⭐ (40�?
- 📁 完全混乱 (>20个文�? = �?(20�?

目标: 保持 ⭐⭐⭐⭐�?(100�?
```

---

## 🗂�?目录分类方法

### 按功能分�?

#### **代码类目�?*
```
src/ �?app/ �?[项目名]/
├── components/      # 组件
├── services/        # 服务
├── utils/          # 工具函数
├── models/         # 数据模型
└── config/         # 配置
```

#### **文档类目�?*
```
docs/ �?文档/ �?项目记录/
├── api/            # API文档
├── guides/         # 指南
├── tutorials/      # 教程
└── references/     # 参考资�?
```

#### **测试类目�?*
```
tests/ �?__tests__/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/           # 端到端测�?
└── fixtures/       # 测试数据
```

#### **工具类目�?*
```
scripts/ �?tools/
├── build/          # 构建脚本
├── deploy/         # 部署脚本
└── maintenance/    # 维护脚本
```

### 按时间分类（适用于文档）

```
docs/
├── archive/        # 归档（过时内容）
├── current/        # 当前有效
└── drafts/         # 草稿（未发布�?
```

或使用编�?
```
项目记录/
├── 1-归档/
├── 2-参考资�?
├── 3-功能说明/
└── 8-聊天记录/
```

### 按模�?业务分类（适用于代码）

```
src/
├── auth/           # 认证模块
├── user/           # 用户模块
├── product/        # 产品模块
└── order/          # 订单模块
```

---

## 🏷�?目录命名规范

### 命名风格选择

#### **代码目录** - 推荐小写字母 + 下划�?连字�?

```
�?推荐:
src/
├── user_service/
├── data-access/
├── api_routes/
└── common_utils/

⚠️ 可接�?(根据语言习惯):
src/
├── UserService/      # Java/C# 风格
├── user-service/     # kebab-case
├── user_service/     # snake_case
└── userService/      # camelCase (不推荐用于目�?
```

#### **文档目录** - 推荐中文或英文清晰命�?

```
�?推荐:
docs/
├── api/              # 英文简�?
├── tutorials/        # 英文标准
├── 部署指南/         # 中文清晰
└── 功能说明/         # 中文明确

或使用编�?
项目记录/
├── 1-归档/
├── 2-源参考对�?
├── 3-功能说明/
└── 4-部署运维/
```

### �?好的目录名称

**特征**:
- 🎯 **清晰明确** - 一看就知道是什�?
- 📏 **简短适中** - 2-3个单�?
- 🔤 **统一风格** - 全小写或全中�?
- 🚫 **无特殊字�?* - 避免空格、@�?�?

**示例**:
```
�?优秀:
- api/
- docs/
- tests/
- scripts/
- components/
- 功能说明/
- 部署运维/

�?良好:
- user-service/
- api_routes/
- test_reports/
- auto_generated/
```

### �?不好的目录名�?

**问题**:
- �?**模糊不清**
- �?**包含空格**
- �?**过长过短**
- �?**临时命名**
- �?**特殊字符**

**示例**:
```
�?避免:
- misc/                    # 太模�?
- stuff/                   # 太模�?
- 我的 文件/               # 包含空格
- 临时文件�?              # 临时命名
- a/                       # 太短
- this_is_a_very_long_directory_name_that_nobody_wants_to_type/  # 太长
- files@2025/              # 特殊字符
- new_folder/              # 未重命名
```

### 📝 命名检查清�?

创建新目录前检�?
- [ ] 名称是否清晰表达目录用途？
- [ ] 名称是否简短（< 20个字符）�?
- [ ] 是否避免了空格和特殊字符�?
- [ ] 是否与现有目录风格一致？
- [ ] 是否避免�?临时"�?新建"等字眼？

---

## 📊 目录层级控制

### 推荐的层级深�?

```
�?理想深度: 2-3�?
⚠️ 可接�? 4�?
�?避免: 5层以�?
```

### 层级示例

#### �?**良好的层�?* (3�?
```
project/
├── src/                    # �?�?
�?  ├── components/         # �?�?
�?  �?  ├── Button/        # �?�?
�?  �?  └── Input/         # �?�?
�?  └── services/          # �?�?
�?      ├── api/           # �?�?
�?      └── auth/          # �?�?
└── docs/                  # �?�?
    └── guides/            # �?�?
        └── getting-started.md  # �?�?
```

#### ⚠️ **可接受的层级** (4�?
```
project/
├── src/                    # �?�?
�?  ├── modules/            # �?�?
�?  �?  ├── user/          # �?�?
�?  �?  �?  ├── components/  # �?�?
�?  �?  �?  └── services/    # �?�?
```

#### �?**过深的层�?* (5�?)
```
�?避免:
project/
├── src/
�?  ├── app/
�?  �?  ├── modules/
�?  �?  �?  ├── feature/
�?  �?  �?  �?  ├── components/
�?  �?  �?  �?  �?  ├── shared/
�?  �?  �?  �?  �?  �?  └── Button.tsx  # �?层！太深了！
```

### 深层目录的替代方�?

**问题**: 目录嵌套太深 (>4�?

**解决方案**:

#### 方案1: 扁平化结�?
```
�?深层嵌套:
src/modules/user/components/forms/

�?扁平�?
src/user-forms/
```

#### 方案2: 分拆目录
```
�?单一深层:
docs/guides/tutorials/beginner/basics/

�?分拆:
docs/
├── tutorials-beginner/
└── tutorials-advanced/
```

#### 方案3: 使用命名空间
```
�?多层目录:
src/app/modules/user/profile/components/

�?命名文件:
src/components/
├── UserProfileAvatar.tsx
├── UserProfileSettings.tsx
└── UserProfileForm.tsx
```

---

## 🚫 禁止的目录操�?

### 1. �?**禁止在根目录随意创建顶层目录**

**错误操作**:
```bash
# 未经规划就创�?
mkdir 新建文件�?
mkdir temp
mkdir backup
mkdir files
```

**正确操作**:
```bash
# 1. 先检�?project-config.md
# 2. 确认是否需要新顶层目录
# 3. 优先使用现有目录的子目录
mkdir docs/new-section/
```

**决策流程**:
```
需要创建目�?
�?
├─ 问题1: 是顶层目录还是子目录�?
�? ├─ 顶层目录 �?是否�?project-config.md 中定义？
�? �? ├─ �?�?�?可以创建
�? �? └─ �?�?�?禁止创建，使用子目录
�? �?
�? └─ 子目�?�?�?可以创建（遵循命名规范）
```

### 2. �?**禁止创建功能重复的目�?*

**错误示例**:
```
project/
├── scripts/          # 已有脚本目录
├── tools/            # �?重复�?
├── utilities/        # �?重复�?
└── my_scripts/       # �?重复�?
```

**正确做法**:
```
project/
└── scripts/          # 统一的脚本目�?
    ├── build/
    ├── deploy/
    └── maintenance/
```

### 3. �?**禁止创建"杂物抽屉"式目�?*

**错误示例**:
```
�?避免:
├── misc/             # 杂项
├── other/            # 其他
├── stuff/            # 东西
├── files/            # 文件
├── temp/             # 临时（如果不清理�?
└── old/              # 旧的
```

**原因**: 这些目录会变成垃圾收集器，难以维�?

**正确做法**:
```
�?明确分类:
├── archive/          # 明确的归档目�?
�?  └── 2024/
├── drafts/           # 明确的草稿目�?
└── legacy/           # 明确的遗留代�?
    └── v1/
```

### 4. �?**禁止创建空目录长期存�?*

**问题**:
```
project/
├── future_features/   # 空目录，一直没�?
├── maybe_needed/      # 空目录，不确�?
└── planned/           # 空目录，计划�?
```

**原则**:
```
�?需要时创建，不要提前创建空目录
�?空目录超�?个月未使�?�?删除
�?Git 不追踪空目录（除非有 .gitkeep�?
```

### 5. �?**禁止频繁重命名顶层目�?*

**问题**:
```
# �?�?
mkdir project-docs/

# �?�?
mv project-docs/ docs/

# �?�?
mv docs/ documentation/

# �?�?
mv documentation/ project-documents/
```

**影响**:
- 破坏Git历史
- 破坏文档链接
- 破坏代码引用
- 团队成员困惑

**原则**:
```
�?创建前仔细规划命�?
�?顶层目录应该稳定
�?如需重命名，一次性完成并通知团队
```

---

## 💡 目录结构最佳实�?

### 最佳实�?1: **使用标准目录�?*

**原因**: 易于理解，符合社区习�?

**推荐的标准名�?*:

```
代码目录:
�?src/          - 源代�?(Source)
�?lib/          - 库文�?(Library)
�?app/          - 应用代码
�?components/   - 组件
�?services/     - 服务
�?utils/        - 工具函数
�?config/       - 配置

文档目录:
�?docs/         - 文档 (Documentation)
�?guides/       - 指南
�?tutorials/    - 教程
�?examples/     - 示例

测试目录:
�?tests/        - 测试
�?__tests__/    - 测试 (Jest风格)
�?spec/         - 规范测试

其他:
�?scripts/      - 脚本
�?tools/        - 工具
�?assets/       - 资源文件
�?public/       - 公共文件
�?dist/         - 构建输出
�?build/        - 构建输出
```

### 最佳实�?2: **使用 README.md 说明目录用�?*

**每个重要目录都应该有 README.md**

```
project/
├── src/
�?  └── README.md          # 说明源代码组�?
├── docs/
�?  └── README.md          # 文档索引
├── tests/
�?  └── README.md          # 测试说明
└── scripts/
    └── README.md          # 脚本使用说明
```

**README.md 示例**:
```markdown
# 📁 src/ - 源代码目�?

## 📋 目录结构

- `components/` - React组件
- `services/` - 业务服务
- `utils/` - 工具函数
- `types/` - TypeScript类型定义

## 🔧 组织原则

- 按功能模块组�?
- 每个模块独立目录
- 共享代码放在 common/
```

### 最佳实�?3: **使用 .gitkeep 保持空目�?*

**问题**: Git 不追踪空目录

**解决**:
```bash
# 创建目录并保持追�?
mkdir -p logs/
touch logs/.gitkeep
git add logs/.gitkeep
```

**适用场景**:
```
�?logs/          - 日志目录（运行时生成�?
�?uploads/       - 上传目录
�?cache/         - 缓存目录
�?tmp/           - 临时目录
```

### 最佳实�?4: **按项目阶段演进目录结�?*

#### 阶段1: 项目初期（简单结构）
```
project/
├── src/
├── tests/
└── README.md
```

#### 阶段2: 项目成长（适度复杂�?
```
project/
├── src/
�?  ├── components/
�?  ├── services/
�?  └── utils/
├── tests/
├── docs/
└── README.md
```

#### 阶段3: 项目成熟（完整结构）
```
project/
├── src/
�?  ├── modules/
�?  �?  ├── auth/
�?  �?  ├── user/
�?  �?  └── product/
�?  ├── shared/
�?  └── config/
├── tests/
├── docs/
├── scripts/
└── README.md
```

**原则**: 不要过早优化，根据需要演�?

---

## 🛠�?目录维护指南

### 定期清理检查清�?

#### 每周检�?
- [ ] 🗑�?删除临时文件和目�?
- [ ] 📁 检查是否有空目�?
- [ ] 📝 更新各目录的 README.md
- [ ] 🔍 查找重复功能的目�?

#### 每月检�?
- [ ] 📊 统计目录层级深度
- [ ] 🏗�?评估目录结构是否合理
- [ ] 📦 归档过时内容
- [ ] 🔄 重构过深的目�?

#### 重大更新后检�?
- [ ] 📋 更新 project-config.md
- [ ] 🗂�?整理新增的目�?
- [ ] 📖 更新文档中的目录引用
- [ ] �?运行目录规范检查脚�?

### 目录重构指南

**何时重构**:
- �?目录层级超过4�?
- �?功能重复的目�?
- �?"杂物抽屉"式目录堆�?
- �?难以找到文件

**如何重构**:

#### 步骤1: 规划新结�?
```markdown
## 当前结构问题
- src/app/modules/user/profile/components/  # 太深

## 目标结构
- src/user-profile/  # 扁平�?
```

#### 步骤2: 创建迁移计划
```bash
# 1. 创建新目�?
mkdir -p src/user-profile/

# 2. 移动文件
mv src/app/modules/user/profile/* src/user-profile/

# 3. 更新引用
# 使用 IDE 批量重命�?

# 4. 删除旧目�?
rm -rf src/app/modules/user/
```

#### 步骤3: 更新文档
- 更新 README.md
- 更新 project-config.md
- 通知团队成员

#### 步骤4: 提交变更
```bash
git add .
git commit -m "refactor: 重构目录结构，扁平化用户模块"
```

---

## 🔧 .windsurf目录管理规则

### 目录定位

`.windsurf/` �?*规则系统专用目录**，必须保持简洁专注�?

**设计原则**:
- �?只包含规则系统本�?
- �?可以直接复制到其他项目使�?
- �?不包含项目特定的分析报告
- �?不包含临时性的过程记录

---

### �?允许的文件类�?

#### 1. **核心规则文件** (必需)
```
�?00-core-principles.md          核心原则
�?01-file-operations.md          文件操作规范
�?02-directory-management.md     目录管理规范
�?03-naming-convention.md        命名规范
�?04-git-workflow.md            Git工作�?
�?05-change-synchronization.md  变更同步规则
�?06-directory-architecture-template.md  架构模板
```

#### 2. **配置文件** (必需)
```
�?config.json                    规则系统配置
�?project-config.md              项目特定配置
�?project-config.example.md      配置模板
```

#### 3. **使用文档** (建议)
```
�?README.md                      规则系统说明
�?架构模板使用指南.md             使用指南
�?规则同步说明.md                 同步策略
�?规则严格执行方案.md             执行方案
�?移植检查清�?md                 移植指南
```

#### 4. **工具脚本** (必需)
```
�?scripts/                       自动化脚本目�?
   ├── check_project_structure.py
   ├── check_directory_standards.py
   ├── verify_portability.py
   └── ...
```

---

### �?禁止的文件类�?

#### 1. **临时分析报告** �?
```
�?2025-11-26_xxx分析报告.md
�?xxx检查报�?md
�?xxx问题分析.md
�?xxx对比分析.md
```

**原因**: 
- 这些是特定时间点的分�?
- 完成后价值降�?
- 不是规则系统的核心内�?

**应放置在**: `项目记录/6-开发规�?` �?`项目记录/7-过程记录/`

---

#### 2. **项目特定对比文档** �?
```
�?A项目vs B项目对比.md
�?xxx项目规则检�?md
�?xxx项目特定说明.md
```

**原因**:
- 针对特定项目的分�?
- 不具有通用�?
- 移植到其他项目时无意�?

**应放置在**: `项目记录/6-开发规�?规则系统分析/`

---

#### 3. **过程记录性质的文�?* �?
```
�?带日期前缀的非规则文档
�?修复过程记录
�?讨论记录
�?临时笔记
```

**原因**:
- 这些是过程记录，不是规则
- 应该放在项目记录�?

**应放置在**: `项目记录/7-过程记录/`

---

### 📐 文件命名规范

#### .windsurf中的文件命名

```
�?核心规则:  00-05-[规则名].md
�?架构模板:  06-directory-architecture-template.md
�?配置文件:  config.json, project-config.md
�?使用文档:  [功能]使用指南.md, [功能]说明.md

�?禁止:     2025-11-26_xxx.md (带日期的临时文档)
�?禁止:     xxx分析.md, xxx报告.md (分析报告)
�?禁止:     临时xxx.md, 草稿xxx.md (临时文件)
```

---

### 🔍 违规文件检�?

#### 自动检查（通过Git Hook�?

```python
# 在pre-commit中检�?
def check_windsurfrules_violations():
    """检�?windsurfrules中的违规文件"""
    
    violations = []
    
    for file in Path('.windsurf').glob('*.md'):
        filename = file.name
        
        # 检�?: 是否有日期前缀的文档（临时文档特征�?
        if re.match(r'^\d{4}-\d{2}-\d{2}', filename):
            violations.append(f"临时文档: {filename}")
        
        # 检�?: 是否�?分析"�?报告"等关键词
        temp_keywords = ['分析', '报告', '检�?, '对比', '总结']
        if any(kw in filename for kw in temp_keywords):
            # 排除允许的文�?
            if filename not in ['规则严格执行方案.md', '移植检查清�?md']:
                violations.append(f"分析报告类文�? {filename}")
    
    if violations:
        print("�?.windsurf目录违规文件:")
        for v in violations:
            print(f"  - {v}")
        print("\n这些文件应移�? 项目记录/6-开发规�? �?项目记录/7-过程记录/")
        return False
    
    return True
```

---

### 📋 清理指南

#### 发现违规文件时的处理

**步骤1**: 识别文件类型
```bash
临时分析报告 �?项目记录/6-开发规�?规则系统分析/
过程记录     �?项目记录/7-过程记录/
已完成的检�?�?项目记录/1-归档/
```

**步骤2**: 移动文件（添加日期前缀�?
```bash
move .windsurf\xxx分析.md \
     项目记录\6-开发规范\规则系统分析\2025-11-26_xxx分析.md
```

**步骤3**: 验证
```bash
# 检�?windsurfrules是否清洁
python .windsurf\scripts\check_project_structure.py
```

---

### �?.windsurf标准结构

```
.windsurf/
├── scripts/                              工具脚本目录
�?  ├── check_project_structure.py
�?  ├── check_directory_standards.py
�?  ├── verify_portability.py
�?  ├── update_project_status.py
�?  ├── install_git_hooks.py
�?  └── ...
�?
├── 00-core-principles.md                 核心原则 �?
├── 01-file-operations.md                 文件操作规范 �?
├── 02-directory-management.md            目录管理规范 �?
├── 03-naming-convention.md               命名规范 �?
├── 04-git-workflow.md                    Git工作�?�?
├── 05-change-synchronization.md          变更同步 �?
├── 06-directory-architecture-template.md 架构模板 �?
�?
├── config.json                           规则配置 �?
├── project-config.md                     项目配置 (项目特定)
├── project-config.example.md             配置模板 �?
�?
├── README.md                             规则系统说明 �?
├── 架构模板使用指南.md                    使用指南
├── 规则同步说明.md                        同步策略
├── 规则严格执行方案.md                    执行方案
└── 移植检查清�?md                        移植指南

总计: 15-18个文�?+ scripts目录
```

**特征**:
- �?简洁：文件数量少，职责明确
- �?通用：可直接复制到其他项�?
- �?完整：包含规则、配置、工具、文�?
- �?可移植：无项目特定的临时内容

---

## �?目录管理检查清�?

### 创建新目录前

- [ ] 📋 是否查看�?project-config.md�?
- [ ] 🔍 是否检查了现有目录�?
- [ ] 🎯 是否有明确的目录用途？
- [ ] 📏 目录名称是否清晰简短？
- [ ] 🏗�?是否考虑了目录层级？
- [ ] 📝 是否准备创建 README.md�?

### 目录结构健康检�?

- [ ] �?根目录清洁（无杂乱文件）
- [ ] �?顶层目录数量合理�? 10个）
- [ ] �?目录层级控制�?层以�?
- [ ] �?无功能重复的目录
- [ ] �?�?杂物抽屉"式目�?
- [ ] �?无长期存在的空目�?
- [ ] �?目录命名统一规范
- [ ] �?重要目录都有 README.md

---

**规则维护**: AI开发规范系�? 
**最后更�?*: 2025-11-26  
**规则版本**: v1.0.0  
**适用项目**: 所有软件开发项�? 

---

## 🔗 相关规则

- 📄 [01-file-operations.md](01-file-operations.md) - 文件操作强制规则
- 🏷�?[03-naming-convention.md](03-naming-convention.md) - 文件命名规范
- ⚙️ [project-config.md](project-config.md) - 项目配置（目录结构定义）
