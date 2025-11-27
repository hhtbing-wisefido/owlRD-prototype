---
title: "README Management Standard"
description: "README.md文件管理和目录树维护规范"
trigger: always_on
---

# README.md 管理规范

**规则类型**: 🔴 强制规则  
**强制级别**: 🔴 严格执行  
**适用范围**: 项目中所有包含README.md的目录

---

## 📋 核心规则

### 规则1: README.md 自动更新机制 🔴

**强制要求**：
当README.md所在的根目录及其所有子目录有任何文件变动时，**必须立即更新该README.md**。

**文件变动包括**：
- ✅ 新增文件或目录
- ✅ 删除文件或目录
- ✅ 重命名文件或目录
- ✅ 移动文件或目录
- ✅ 修改文件结构

**更新时机**：
`
文件变动  立即更新README.md  提交代码
`

**禁止行为**：
- ❌ 修改了目录结构但不更新README.md
- ❌ 添加了新文件但README.md中没有说明
- ❌ 删除了文件但目录树仍显示该文件
- ❌ README.md与实际目录结构不一致

---

### 规则2: 目录树必需内容 🔴

**每个README.md必须包含以下部分**：

#### 1. 目录树结构
`markdown
## 📁 目录结构

\\\
目录名/
 file1.ext               文件说明
 file2.ext               文件说明
 subdirectory/           子目录说明
    subfile1.ext        文件说明
    subfile2.ext        文件说明
 README.md               本文件
\\\
`

#### 2. 目录树详解注释

**每个文件和目录必须有注释**：
`
✅ 正确示例：
 main.py               FastAPI应用入口
 config.py             配置管理
 models/               数据模型目录
    user.py           用户模型
    tenant.py         租户模型

❌ 错误示例：
 main.py
 config.py
 models/
`

**注释要求**：
- 🔴 **必须**：每个项目都要有注释
- 🔴 **清晰**：说明文件/目录的用途
- 🔴 **简洁**：一句话概括，不超过20个字
- 🔴 **一致**：使用   作为注释符号

---

## 🎯 执行流程

### AI执行检查清单

**每次修改文件系统时，必须执行以下步骤**：

#### Step 1: 检测变动
`
检查是否修改了：
- 文件：新增/删除/重命名/移动
- 目录：新增/删除/重命名/移动
`

#### Step 2: 定位README.md
`
找到需要更新的README.md：
- 变动所在目录的README.md
- 如果不存在，向上查找父目录的README.md
`

#### Step 3: 更新目录树
`
1. 使用工具扫描实际目录结构
2. 生成新的目录树
3. 更新README.md中的目录树部分
4. 确保所有项目都有注释
`

#### Step 4: 验证完整性
`
检查：
✅ 目录树与实际结构一致
✅ 所有文件都有注释
✅ 所有目录都有注释
✅ 注释清晰明确
`

#### Step 5: 提交更改
`
git add README.md
git commit -m "docs: 更新README.md目录树"
`

---

## 📐 目录树格式标准

### 基本格式

**使用ASCII树形字符**：
`
目录/
 文件1
 文件2
 子目录/
    子文件1
    子文件2
 最后一个文件
`

**字符说明**：
- \\ - 中间项
- \\ - 最后一项
- \\ - 垂直连接线
- \/\ - 目录标识

### 注释格式

**使用箭头注释**：
`
文件名                文件说明（简洁明确）
`

**注释位置**：
- 使用 \ \ 分隔文件名和注释
- 注释对齐（可选，但推荐）
- 每个项目都必须有注释

### 完整示例

\\\markdown
## 📁 目录结构

\\\
backend/
 app/
    main.py               FastAPI应用入口
    config.py             配置管理
    models/               Pydantic数据模型
       user.py           用户模型
       tenant.py         租户模型
       __init__.py       模块初始化
    services/             业务逻辑服务
       auth.py           认证服务
       storage.py        数据存储服务
    api/                  API路由
        v1/               API版本1
            users.py      用户路由
            tenants.py    租户路由
 tests/                    测试文件
    test_api.py           API测试
    test_models.py        模型测试
 requirements.txt          Python依赖
 README.md                 本文件（项目说明）
\\\
\\\

---

## 🔍 特殊情况处理

### 情况1: 目录过深（超过5层）

**处理方式**：
`
方案A: 折叠显示深层目录
 deep/
    nested/
        ...（省略深层内容）

方案B: 只显示重要目录
 deep/
    （包含多个子目录，详见子目录README）
`

### 情况2: 文件过多（超过30个）

**处理方式**：
`
方案A: 分组显示
 api/                      API路由（20个文件）
    users.py              用户相关API
    tenants.py            租户相关API
    ...（其他18个文件）

方案B: 分类汇总
 models/                   数据模型目录
    user/                 用户模型（5个文件）
    tenant/               租户模型（3个文件）
    ...（其他模型）
`

### 情况3: 临时文件/缓存文件

**排除规则**：
`
不要在目录树中包含：
❌ __pycache__/
❌ node_modules/
❌ .git/
❌ *.pyc
❌ .DS_Store
❌ .vscode/（除非项目配置）
`

### 情况4: 新创建的目录

**立即处理**：
`
1. 创建目录时立即创建README.md
2. 如果是空目录，说明目录用途
3. 添加占位内容（待添加文件时更新）
`

---

## ✅ 更新README.md的标准流程

### 自动化命令（推荐）

**使用tree命令生成目录树**：
\\\ash
# Linux/Mac
tree -L 3 -I 'node_modules|__pycache__|.git' > temp_tree.txt

# Windows PowerShell
tree /F /A > temp_tree.txt
\\\

**然后**：
1. 复制tree输出
2. 添加注释（\ \）
3. 更新README.md

### 手动更新流程

**步骤**：
1. 列出当前目录所有文件和子目录
2. 绘制ASCII树形结构
3. 为每个项目添加注释
4. 验证与实际结构一致
5. 更新README.md

---

## 🎯 验证检查清单

**更新README.md后必须验证**：

- [ ] 目录树与实际文件系统一致
- [ ] 所有文件都有注释
- [ ] 所有目录都有注释
- [ ] 注释清晰明确（不超过20字）
- [ ] 使用标准ASCII树形字符
- [ ] 使用 \ \ 作为注释分隔符
- [ ] 排除了临时文件和缓存目录
- [ ] 格式美观整洁
- [ ] 没有拼写错误

---


## ⚠️ 例外情况

**以下README.md不需要包含目录树**：

### 1. 系统说明文档
- **.windsurf/README.md** - 规则系统使用指南
  - ✅ 此文件描述规则系统本身
  - ✅ 不描述 .windsurf/ 目录的文件结构
  - ✅ 内容是：如何使用规则、激活模式、FAQ等
  - ❌ 不需要列出 .windsurf/rules/ 的规则文件

### 2. 项目总览文档
- **项目根目录的 README.md**（特殊情况）
  - 如果是项目介绍、使用说明等总览性质
  - 可以不包含详细目录树
  - 但建议至少说明主要目录的用途

### 3. 纯说明性文档
- 纯教程类README（如：	utorial/README.md）
- 纯FAQ类README
- 纯链接索引类README

**判断标准**：
`
需要目录树：README描述"这个目录包含什么文件"
不需要目录树：README描述"如何使用某个系统/功能"
`

**示例对比**：
`
✅ 需要目录树：
   backend/README.md - "Backend API项目结构说明"
    应该列出 app/, tests/, scripts/ 等

❌ 不需要目录树：
   .windsurf/README.md - "规则系统使用指南"
    描述如何使用规则系统，不是目录内容
`

---
## 📊 监控范围

**以下目录的README.md必须遵守此规范**：

### 项目级README
- \/README.md\ - 项目根目录

### 模块级README
- \/backend/README.md\
- \/frontend/README.md\
- \/tests/README.md\
- \/docs/README.md\

### 子模块README
- \/backend/app/README.md\
- \/backend/services/README.md\
- \/frontend/src/README.md\
- 等等...

**规则**：
- 🔴 有README.md的目录必须维护目录树
- 🔴 修改目录结构必须更新README.md
- 🔴 不允许README.md与实际不符

---

## 💡 最佳实践

### 1. 实时更新
`
每次修改文件系统  立即更新README.md
不要积累多次修改后才更新
`

### 2. 清晰注释
`
✅ 好的注释：
 auth.py               用户认证和权限管理

❌ 差的注释：
 auth.py               认证
`

### 3. 合理层级
`
✅ 显示3-4层：
backend/
 app/
    models/
       user.py

❌ 显示太深（7层+）：
backend/app/models/schemas/users/base/common/user.py
`

### 4. 分组组织
`
✅ 按功能分组：
models/
 用户模型（5个文件）
 设备模型（3个文件）
 IoT模型（8个文件）

❌ 平铺所有文件（16个）
`

---

## 🚫 禁止行为

### 严格禁止

1. ❌ **忽略更新** - 修改了目录但不更新README
2. ❌ **手动不一致** - README.md与实际目录不符
3. ❌ **缺少注释** - 文件/目录没有说明
4. ❌ **注释模糊** - 说明不清楚或过于简略
5. ❌ **格式混乱** - 不使用标准ASCII树形字符

### 警告行为

1. ⚠️ **延迟更新** - 修改后拖延更新（应立即更新）
2. ⚠️ **注释过长** - 超过20个字（应简洁）
3. ⚠️ **层级过深** - 显示超过5层（应折叠）

---

## 🔄 执行优先级

**优先级顺序**：
1. 🔴 **最高** - 项目根目录 README.md
2. 🔴 **高** - 主要模块 README.md (backend, frontend, tests)
3. 🟡 **中** - 子模块 README.md
4. 🟢 **低** - 深层子目录 README.md

---

## ✅ 自检要求

**AI在每次操作后必须自检**：

1. **检查文件变动**
   - 是否创建/删除/移动了文件或目录？

2. **定位README.md**
   - 找到需要更新的README.md

3. **更新目录树**
   - 扫描实际结构
   - 更新目录树
   - 添加/更新注释

4. **验证一致性**
   - README.md与实际结构一致
   - 所有项目都有注释

5. **报告完成**
   - 告知用户已更新README.md
   - 说明更新了哪些内容

---

**遵守此规范，保持README.md始终与项目结构同步！**