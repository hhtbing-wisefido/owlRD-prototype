# 📁 目录管理规范

**规则类型**: 通用规则 ✅  
**强制级别**: 🔴 严格执行  
**适用场景**: 目录创建、组织和维护  
**版本**: v1.0.0  

---

## 📋 目录

- [核心原则](#核心原则)
- [根目录管理原则](#根目录管理原则)
- [目录分类方法](#目录分类方法)
- [目录命名规范](#目录命名规范)
- [目录层级控制](#目录层级控制)
- [禁止的目录操作](#禁止的目录操作)
- [目录结构最佳实践](#目录结构最佳实践)
- [目录维护指南](#目录维护指南)

---

## 🎯 核心原则

### 三大核心原则

#### 1. 📐 **简洁清晰** (Keep It Simple)
```
✅ 好的目录结构:
project/
├── src/           # 源代码
├── docs/          # 文档
├── tests/         # 测试
└── scripts/       # 脚本

❌ 糟糕的目录结构:
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
避免"杂物抽屉"式的目录（misc/, other/, stuff/）
```

**示例**:
```
✅ 正确分类:
docs/
├── api/          # API文档
├── guides/       # 使用指南
└── tutorials/    # 教程

❌ 模糊分类:
docs/
├── files/        # 什么文件？
├── stuff/        # 什么东西？
└── others/       # 太模糊了
```

#### 3. 🏗️ **结构稳定** (Stable Structure)
```
目录结构应该相对稳定
避免频繁创建、删除、重命名顶层目录
新需求优先使用现有目录的子目录
```

---

## 🏠 根目录管理原则

### 什么是根目录？

**项目根目录** = 项目的最顶层目录，通常包含 `.git/` 文件夹的目录

### ✅ 根目录应该包含什么

#### 1. **必需的配置文件**
```
.gitignore          # Git忽略规则
README.md           # 项目说明
LICENSE             # 许可证（如适用）
```

#### 2. **项目管理文件**（可选）
```
.editorconfig       # 编辑器配置
.prettierrc         # 代码格式化配置
pyproject.toml      # Python项目配置
package.json        # Node.js项目配置
Cargo.toml          # Rust项目配置
pom.xml            # Java Maven配置
```

#### 3. **主要目录**
```
根据 project-config.md 定义的目录结构
通常包括:
├── [代码主目录]/
├── [文档主目录]/
├── 知识库/                  ⭐ 只读参考（标配）
├── [测试目录]/
├── [脚本目录]/
└── .windsurfrules/
```

**知识库目录** 🔒:
- 所有项目的标准配置目录
- 存放源参考文件、技术文档、学习资料
- 只读属性 - 只允许添加新文件，不允许修改、删除已有文件
- 详见 project-config.md 中的知识库规则

### ❌ 根目录严格禁止

#### 1. **禁止文档文件堆积**
```
❌ 错误:
/
├── README.md               ✅ 允许
├── 功能说明.md             ❌ 禁止
├── 部署指南.md             ❌ 禁止
├── API文档.md              ❌ 禁止
└── 开发笔记.md             ❌ 禁止

✅ 正确:
/
├── README.md               ✅ 项目总说明
└── docs/                   ✅ 文档目录
    ├── 功能说明.md
    ├── 部署指南.md
    ├── API文档.md
    └── 开发笔记.md
```

#### 2. **禁止临时文件**
```
❌ 禁止:
├── 临时笔记.txt
├── TODO.md
├── test.py
├── 新建文档.md
├── backup_20251125.zip
└── output.log

✅ 应该:
- 临时文件放在 .gitignore 的目录中
- 或者及时清理
- 或者放在专门的临时目录
```

#### 3. **禁止数据文件**
```
❌ 禁止:
├── data.json
├── users.csv
├── database.sqlite
└── export_results.xlsx

✅ 应该:
- 示例数据 → [代码目录]/data/
- 测试数据 → tests/fixtures/
- 实际数据 → 添加到 .gitignore
```

#### 4. **禁止构建产物**
```
❌ 禁止:
├── dist/
├── build/
├── *.pyc
├── node_modules/
└── target/

✅ 应该:
- 添加到 .gitignore
- 或者在 CI/CD 中生成
```

#### 5. **禁止随意创建顶层目录**
```
❌ 禁止:
├── my_scripts/       # 已有 scripts/
├── documents/        # 已有 docs/
├── temporary/        # 应该 .gitignore
├── backup/           # 应该 .gitignore
└── old_code/         # 应该删除或归档

✅ 原则:
- 新目录必须有充分理由
- 优先使用现有目录的子目录
- 参考 project-config.md 定义
```

### 📊 根目录清洁度检查

```markdown
根目录清洁度评分:

- 📁 只有 README.md + 配置文件 + 主要目录 = ⭐⭐⭐⭐⭐ (100分)
- 📁 有少量临时文件 (1-2个) = ⭐⭐⭐⭐ (80分)
- 📁 有多个文档文件 (3-5个) = ⭐⭐⭐ (60分)
- 📁 文件杂乱 (>10个文件) = ⭐⭐ (40分)
- 📁 完全混乱 (>20个文件) = ⭐ (20分)

目标: 保持 ⭐⭐⭐⭐⭐ (100分)
```

---

## 🗂️ 目录分类方法

### 按功能分类

#### **代码类目录**
```
src/ 或 app/ 或 [项目名]/
├── components/      # 组件
├── services/        # 服务
├── utils/          # 工具函数
├── models/         # 数据模型
└── config/         # 配置
```

#### **文档类目录**
```
docs/ 或 文档/ 或 项目记录/
├── api/            # API文档
├── guides/         # 指南
├── tutorials/      # 教程
└── references/     # 参考资料
```

#### **测试类目录**
```
tests/ 或 __tests__/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/           # 端到端测试
└── fixtures/       # 测试数据
```

#### **工具类目录**
```
scripts/ 或 tools/
├── build/          # 构建脚本
├── deploy/         # 部署脚本
└── maintenance/    # 维护脚本
```

### 按时间分类（适用于文档）

```
docs/
├── archive/        # 归档（过时内容）
├── current/        # 当前有效
└── drafts/         # 草稿（未发布）
```

或使用编号:
```
项目记录/
├── 1-归档/
├── 2-参考资料/
├── 3-功能说明/
└── 8-聊天记录/
```

### 按模块/业务分类（适用于代码）

```
src/
├── auth/           # 认证模块
├── user/           # 用户模块
├── product/        # 产品模块
└── order/          # 订单模块
```

---

## 🏷️ 目录命名规范

### 命名风格选择

#### **代码目录** - 推荐小写字母 + 下划线/连字符

```
✅ 推荐:
src/
├── user_service/
├── data-access/
├── api_routes/
└── common_utils/

⚠️ 可接受 (根据语言习惯):
src/
├── UserService/      # Java/C# 风格
├── user-service/     # kebab-case
├── user_service/     # snake_case
└── userService/      # camelCase (不推荐用于目录)
```

#### **文档目录** - 推荐中文或英文清晰命名

```
✅ 推荐:
docs/
├── api/              # 英文简洁
├── tutorials/        # 英文标准
├── 部署指南/         # 中文清晰
└── 功能说明/         # 中文明确

或使用编号:
项目记录/
├── 1-归档/
├── 2-源参考对照/
├── 3-功能说明/
└── 4-部署运维/
```

### ✅ 好的目录名称

**特征**:
- 🎯 **清晰明确** - 一看就知道是什么
- 📏 **简短适中** - 2-3个单词
- 🔤 **统一风格** - 全小写或全中文
- 🚫 **无特殊字符** - 避免空格、@、#等

**示例**:
```
✅ 优秀:
- api/
- docs/
- tests/
- scripts/
- components/
- 功能说明/
- 部署运维/

✅ 良好:
- user-service/
- api_routes/
- test_reports/
- auto_generated/
```

### ❌ 不好的目录名称

**问题**:
- ❌ **模糊不清**
- ❌ **包含空格**
- ❌ **过长过短**
- ❌ **临时命名**
- ❌ **特殊字符**

**示例**:
```
❌ 避免:
- misc/                    # 太模糊
- stuff/                   # 太模糊
- 我的 文件/               # 包含空格
- 临时文件夹/              # 临时命名
- a/                       # 太短
- this_is_a_very_long_directory_name_that_nobody_wants_to_type/  # 太长
- files@2025/              # 特殊字符
- new_folder/              # 未重命名
```

### 📝 命名检查清单

创建新目录前检查:
- [ ] 名称是否清晰表达目录用途？
- [ ] 名称是否简短（< 20个字符）？
- [ ] 是否避免了空格和特殊字符？
- [ ] 是否与现有目录风格一致？
- [ ] 是否避免了"临时"、"新建"等字眼？

---

## 📊 目录层级控制

### 推荐的层级深度

```
✅ 理想深度: 2-3层
⚠️ 可接受: 4层
❌ 避免: 5层以上
```

### 层级示例

#### ✅ **良好的层级** (3层)
```
project/
├── src/                    # 第1层
│   ├── components/         # 第2层
│   │   ├── Button/        # 第3层
│   │   └── Input/         # 第3层
│   └── services/          # 第2层
│       ├── api/           # 第3层
│       └── auth/          # 第3层
└── docs/                  # 第1层
    └── guides/            # 第2层
        └── getting-started.md  # 第3层
```

#### ⚠️ **可接受的层级** (4层)
```
project/
├── src/                    # 第1层
│   ├── modules/            # 第2层
│   │   ├── user/          # 第3层
│   │   │   ├── components/  # 第4层
│   │   │   └── services/    # 第4层
```

#### ❌ **过深的层级** (5层+)
```
❌ 避免:
project/
├── src/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── feature/
│   │   │   │   ├── components/
│   │   │   │   │   ├── shared/
│   │   │   │   │   │   └── Button.tsx  # 第7层！太深了！
```

### 深层目录的替代方案

**问题**: 目录嵌套太深 (>4层)

**解决方案**:

#### 方案1: 扁平化结构
```
❌ 深层嵌套:
src/modules/user/components/forms/

✅ 扁平化:
src/user-forms/
```

#### 方案2: 分拆目录
```
❌ 单一深层:
docs/guides/tutorials/beginner/basics/

✅ 分拆:
docs/
├── tutorials-beginner/
└── tutorials-advanced/
```

#### 方案3: 使用命名空间
```
❌ 多层目录:
src/app/modules/user/profile/components/

✅ 命名文件:
src/components/
├── UserProfileAvatar.tsx
├── UserProfileSettings.tsx
└── UserProfileForm.tsx
```

---

## 🚫 禁止的目录操作

### 1. ❌ **禁止在根目录随意创建顶层目录**

**错误操作**:
```bash
# 未经规划就创建
mkdir 新建文件夹
mkdir temp
mkdir backup
mkdir files
```

**正确操作**:
```bash
# 1. 先检查 project-config.md
# 2. 确认是否需要新顶层目录
# 3. 优先使用现有目录的子目录
mkdir docs/new-section/
```

**决策流程**:
```
需要创建目录
│
├─ 问题1: 是顶层目录还是子目录？
│  ├─ 顶层目录 → 是否在 project-config.md 中定义？
│  │  ├─ 是 → ✅ 可以创建
│  │  └─ 否 → ❌ 禁止创建，使用子目录
│  │
│  └─ 子目录 → ✅ 可以创建（遵循命名规范）
```

### 2. ❌ **禁止创建功能重复的目录**

**错误示例**:
```
project/
├── scripts/          # 已有脚本目录
├── tools/            # ❌ 重复！
├── utilities/        # ❌ 重复！
└── my_scripts/       # ❌ 重复！
```

**正确做法**:
```
project/
└── scripts/          # 统一的脚本目录
    ├── build/
    ├── deploy/
    └── maintenance/
```

### 3. ❌ **禁止创建"杂物抽屉"式目录**

**错误示例**:
```
❌ 避免:
├── misc/             # 杂项
├── other/            # 其他
├── stuff/            # 东西
├── files/            # 文件
├── temp/             # 临时（如果不清理）
└── old/              # 旧的
```

**原因**: 这些目录会变成垃圾收集器，难以维护

**正确做法**:
```
✅ 明确分类:
├── archive/          # 明确的归档目录
│   └── 2024/
├── drafts/           # 明确的草稿目录
└── legacy/           # 明确的遗留代码
    └── v1/
```

### 4. ❌ **禁止创建空目录长期存在**

**问题**:
```
project/
├── future_features/   # 空目录，一直没用
├── maybe_needed/      # 空目录，不确定
└── planned/           # 空目录，计划中
```

**原则**:
```
✅ 需要时创建，不要提前创建空目录
✅ 空目录超过1个月未使用 → 删除
✅ Git 不追踪空目录（除非有 .gitkeep）
```

### 5. ❌ **禁止频繁重命名顶层目录**

**问题**:
```
# 第1天
mkdir project-docs/

# 第2天
mv project-docs/ docs/

# 第3天
mv docs/ documentation/

# 第4天
mv documentation/ project-documents/
```

**影响**:
- 破坏Git历史
- 破坏文档链接
- 破坏代码引用
- 团队成员困惑

**原则**:
```
✅ 创建前仔细规划命名
✅ 顶层目录应该稳定
✅ 如需重命名，一次性完成并通知团队
```

---

## 💡 目录结构最佳实践

### 最佳实践 1: **使用标准目录名**

**原因**: 易于理解，符合社区习惯

**推荐的标准名称**:

```
代码目录:
✅ src/          - 源代码 (Source)
✅ lib/          - 库文件 (Library)
✅ app/          - 应用代码
✅ components/   - 组件
✅ services/     - 服务
✅ utils/        - 工具函数
✅ config/       - 配置

文档目录:
✅ docs/         - 文档 (Documentation)
✅ guides/       - 指南
✅ tutorials/    - 教程
✅ examples/     - 示例

测试目录:
✅ tests/        - 测试
✅ __tests__/    - 测试 (Jest风格)
✅ spec/         - 规范测试

其他:
✅ scripts/      - 脚本
✅ tools/        - 工具
✅ assets/       - 资源文件
✅ public/       - 公共文件
✅ dist/         - 构建输出
✅ build/        - 构建输出
```

### 最佳实践 2: **使用 README.md 说明目录用途**

**每个重要目录都应该有 README.md**

```
project/
├── src/
│   └── README.md          # 说明源代码组织
├── docs/
│   └── README.md          # 文档索引
├── tests/
│   └── README.md          # 测试说明
└── scripts/
    └── README.md          # 脚本使用说明
```

**README.md 示例**:
```markdown
# 📁 src/ - 源代码目录

## 📋 目录结构

- `components/` - React组件
- `services/` - 业务服务
- `utils/` - 工具函数
- `types/` - TypeScript类型定义

## 🔧 组织原则

- 按功能模块组织
- 每个模块独立目录
- 共享代码放在 common/
```

### 最佳实践 3: **使用 .gitkeep 保持空目录**

**问题**: Git 不追踪空目录

**解决**:
```bash
# 创建目录并保持追踪
mkdir -p logs/
touch logs/.gitkeep
git add logs/.gitkeep
```

**适用场景**:
```
✅ logs/          - 日志目录（运行时生成）
✅ uploads/       - 上传目录
✅ cache/         - 缓存目录
✅ tmp/           - 临时目录
```

### 最佳实践 4: **按项目阶段演进目录结构**

#### 阶段1: 项目初期（简单结构）
```
project/
├── src/
├── tests/
└── README.md
```

#### 阶段2: 项目成长（适度复杂）
```
project/
├── src/
│   ├── components/
│   ├── services/
│   └── utils/
├── tests/
├── docs/
└── README.md
```

#### 阶段3: 项目成熟（完整结构）
```
project/
├── src/
│   ├── modules/
│   │   ├── auth/
│   │   ├── user/
│   │   └── product/
│   ├── shared/
│   └── config/
├── tests/
├── docs/
├── scripts/
└── README.md
```

**原则**: 不要过早优化，根据需要演进

---

## 🛠️ 目录维护指南

### 定期清理检查清单

#### 每周检查
- [ ] 🗑️ 删除临时文件和目录
- [ ] 📁 检查是否有空目录
- [ ] 📝 更新各目录的 README.md
- [ ] 🔍 查找重复功能的目录

#### 每月检查
- [ ] 📊 统计目录层级深度
- [ ] 🏗️ 评估目录结构是否合理
- [ ] 📦 归档过时内容
- [ ] 🔄 重构过深的目录

#### 重大更新后检查
- [ ] 📋 更新 project-config.md
- [ ] 🗂️ 整理新增的目录
- [ ] 📖 更新文档中的目录引用
- [ ] ✅ 运行目录规范检查脚本

### 目录重构指南

**何时重构**:
- ❌ 目录层级超过4层
- ❌ 功能重复的目录
- ❌ "杂物抽屉"式目录堆积
- ❌ 难以找到文件

**如何重构**:

#### 步骤1: 规划新结构
```markdown
## 当前结构问题
- src/app/modules/user/profile/components/  # 太深

## 目标结构
- src/user-profile/  # 扁平化
```

#### 步骤2: 创建迁移计划
```bash
# 1. 创建新目录
mkdir -p src/user-profile/

# 2. 移动文件
mv src/app/modules/user/profile/* src/user-profile/

# 3. 更新引用
# 使用 IDE 批量重命名

# 4. 删除旧目录
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

## ✅ 目录管理检查清单

### 创建新目录前

- [ ] 📋 是否查看了 project-config.md？
- [ ] 🔍 是否检查了现有目录？
- [ ] 🎯 是否有明确的目录用途？
- [ ] 📏 目录名称是否清晰简短？
- [ ] 🏗️ 是否考虑了目录层级？
- [ ] 📝 是否准备创建 README.md？

### 目录结构健康检查

- [ ] ✅ 根目录清洁（无杂乱文件）
- [ ] ✅ 顶层目录数量合理（< 10个）
- [ ] ✅ 目录层级控制在4层以内
- [ ] ✅ 无功能重复的目录
- [ ] ✅ 无"杂物抽屉"式目录
- [ ] ✅ 无长期存在的空目录
- [ ] ✅ 目录命名统一规范
- [ ] ✅ 重要目录都有 README.md

---

**规则维护**: AI开发规范系统  
**最后更新**: 2025-11-26  
**规则版本**: v1.0.0  
**适用项目**: 所有软件开发项目  

---

## 🔗 相关规则

- 📄 [01-file-operations.md](01-file-operations.md) - 文件操作强制规则
- 🏷️ [03-naming-convention.md](03-naming-convention.md) - 文件命名规范
- ⚙️ [project-config.md](project-config.md) - 项目配置（目录结构定义）
