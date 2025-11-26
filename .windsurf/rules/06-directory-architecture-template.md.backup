---
title: "Directory Architecture Template"
description: "通用项目目录架构标准"
trigger: model_decision
---

# 📐 项目目录架构模板 - 通用标准

**模板名称**: 全栈项目标准架构  
**适用场景**: 前后端分离全栈项�?/ 纯后端API项目  
**版本**: v1.0.0  
**创建日期**: 2025-11-26  
**参考项�?*: owlRD-原型项目

---

## 🎯 架构特点

这是一�?*通用的标准项目架�?*，适用于多种项目类型：

### �?完全适用
- **全栈项目**: FastAPI + React / Django + Vue / Flask + Angular
- **纯后端API**: FastAPI / Django / Flask
- **微服务项�?*: 多个独立服务
- **原型开�?*: 快速搭建和迭代

### 🎨 核心优势
- �?前后端完全分离（如需要）
- �?规范的文档管理（8大分类）
- �?知识库参考系统（只读�?
- �?完整的测试覆�?
- �?规则系统集成

---

## 📁 完整目录结构

```plaintext
项目根目�?
�?
├── 📄 README.md                          # 项目总说�?
├── 📄 .gitignore                         # Git忽略规则
�?
├── 🔧 .git/                              # Git版本控制
├── 🔧 .vscode/                           # VS Code配置
├── 🔧 .windsurf/                    # AI规则系统 �?
�?  ├── README.md                         # 规则系统说明
�?  ├── 00-core-principles.md             # 核心原则
�?  ├── 01-file-operations.md             # 文件操作规范
�?  ├── 02-directory-management.md        # 目录管理规则
�?  ├── 03-naming-convention.md           # 命名约定
�?  ├── 04-git-workflow.md                # Git工作�?
�?  ├── 05-change-synchronization.md      # 变更同步
�?  ├── 06-directory-architecture-template.md  # 本架构模�?
�?  ├── config.json                       # 规则配置
�?  ├── project-config.md                 # 项目配置
�?  ├── project-config.example.md         # 配置模板
�?  └── scripts/                          # 规则工具脚本
�?      ├── check_project_structure.py    # 结构检�?
�?      ├── verify_portability.py         # 移植性验�?
�?      └── ...
�?
├── 📦 {项目名}-prototype/                 # 代码主目录（使用实际项目名）
�?  �?
�?  ├── 🐍 backend/                       # 后端代码
�?  �?  ├── app/                          # FastAPI应用
�?  �?  �?  ├── main.py                   # 应用入口
�?  �?  �?  ├── config.py                 # 配置管理
�?  �?  �?  ├── database.py               # 数据库连�?
�?  �?  �?  ├── models/                   # SQLAlchemy模型
�?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  ├── user.py
�?  �?  �?  �?  ├── device.py
�?  �?  �?  �?  └── ...
�?  �?  �?  ├── schemas/                  # Pydantic schemas
�?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  ├── user.py
�?  �?  �?  �?  └── ...
�?  �?  �?  ├── api/                      # API路由
�?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  ├── v1/
�?  �?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  �?  ├── users.py
�?  �?  �?  �?  �?  ├── devices.py
�?  �?  �?  �?  �?  └── ...
�?  �?  �?  �?  └── deps.py               # 依赖注入
�?  �?  �?  ├── crud/                     # CRUD操作
�?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  ├── user.py
�?  �?  �?  �?  └── ...
�?  �?  �?  ├── services/                 # 业务逻辑�?
�?  �?  �?  �?  ├── __init__.py
�?  �?  �?  �?  └── ...
�?  �?  �?  ├── core/                     # 核心功能
�?  �?  �?  �?  ├── security.py           # 安全相关
�?  �?  �?  �?  └── ...
�?  �?  �?  ├── data/                     # 示例/初始数据
�?  �?  �?  �?  └── sample_data.json
�?  �?  �?  └── static/                   # 静态文�?
�?  �?  �?      └── ...
�?  �?  �?
�?  �?  ├── scripts/                      # 后端脚本
�?  �?  �?  ├── init_db.py                # 数据库初始化
�?  �?  �?  ├── load_sample_data.py       # 加载示例数据
�?  �?  �?  └── ...
�?  �?  �?
�?  �?  ├── logs/                         # 日志文件（gitignored�?
�?  �?  ├── venv/                         # Python虚拟环境（gitignored�?
�?  �?  �?
�?  �?  ├── requirements.txt              # Python依赖
�?  �?  ├── pytest.ini                    # Pytest配置
�?  �?  ├── .env.example                  # 环境变量示例
�?  �?  ├── .gitignore                    # 后端Git忽略
�?  �?  ├── README.md                     # 后端文档
�?  �?  ├── start_server.bat              # Windows启动脚本
�?  �?  ├── start_server.sh               # Linux/Mac启动脚本
�?  �?  └── start_with_check.py           # 带检查的启动脚本
�?  �?
�?  ├── ⚛️ frontend/                      # 前端代码
�?  �?  ├── src/                          # 源代�?
�?  �?  �?  ├── App.tsx                   # 主应用组�?
�?  �?  �?  ├── main.tsx                  # 应用入口
�?  �?  �?  ├── vite-env.d.ts             # Vite类型定义
�?  �?  �?  �?
�?  �?  �?  ├── components/               # React组件
�?  �?  �?  �?  ├── common/               # 通用组件
�?  �?  �?  �?  �?  ├── Button.tsx
�?  �?  �?  �?  �?  ├── Input.tsx
�?  �?  �?  �?  �?  └── ...
�?  �?  �?  �?  ├── layout/               # 布局组件
�?  �?  �?  �?  �?  ├── Header.tsx
�?  �?  �?  �?  �?  ├── Sidebar.tsx
�?  �?  �?  �?  �?  └── ...
�?  �?  �?  �?  └── features/             # 功能组件
�?  �?  �?  �?      └── ...
�?  �?  �?  �?
�?  �?  �?  ├── pages/                    # 页面组件
�?  �?  �?  �?  ├── Dashboard.tsx
�?  �?  �?  �?  ├── Users.tsx
�?  �?  �?  �?  └── ...
�?  �?  �?  �?
�?  �?  �?  ├── services/                 # API服务
�?  �?  �?  �?  ├── api.ts                # API客户�?
�?  �?  �?  �?  ├── auth.ts               # 认证服务
�?  �?  �?  �?  └── ...
�?  �?  �?  �?
�?  �?  �?  ├── hooks/                    # 自定义Hooks
�?  �?  �?  �?  ├── useAuth.ts
�?  �?  �?  �?  ├── useWebSocket.ts
�?  �?  �?  �?  └── ...
�?  �?  �?  �?
�?  �?  �?  ├── types/                    # TypeScript类型
�?  �?  �?  �?  ├── index.ts
�?  �?  �?  �?  ├── user.ts
�?  �?  �?  �?  └── ...
�?  �?  �?  �?
�?  �?  �?  ├── utils/                    # 工具函数
�?  �?  �?  �?  ├── format.ts
�?  �?  �?  �?  └── ...
�?  �?  �?  �?
�?  �?  �?  ├── styles/                   # 样式文件
�?  �?  �?  �?  └── global.css
�?  �?  �?  �?
�?  �?  �?  └── assets/                   # 静态资�?
�?  �?  �?      ├── images/
�?  �?  �?      └── fonts/
�?  �?  �?
�?  �?  ├── public/                       # 公共资源
�?  �?  �?  └── favicon.ico
�?  �?  �?
�?  �?  ├── scripts/                      # 前端脚本
�?  �?  �?  └── ...
�?  �?  �?
�?  �?  ├── dist/                         # 构建输出（gitignored�?
�?  �?  ├── node_modules/                 # npm依赖（gitignored�?
�?  �?  �?
�?  �?  ├── package.json                  # npm配置
�?  �?  ├── package-lock.json             # npm锁文�?
�?  �?  ├── tsconfig.json                 # TypeScript配置
�?  �?  ├── tsconfig.node.json            # Node TypeScript配置
�?  �?  ├── vite.config.ts                # Vite配置
�?  �?  ├── tailwind.config.js            # TailwindCSS配置
�?  �?  ├── postcss.config.js             # PostCSS配置
�?  �?  ├── .env.example                  # 环境变量示例
�?  �?  ├── .gitignore                    # 前端Git忽略
�?  �?  ├── README.md                     # 前端文档
�?  �?  ├── index.html                    # HTML模板
�?  �?  ├── start_lan.bat                 # 局域网启动（Windows�?
�?  �?  ├── start_lan.sh                  # 局域网启动（Linux/Mac�?
�?  �?  └── check-port.js                 # 端口检查脚�?
�?  �?
�?  └── 🧪 tests/                         # 测试文件
�?      ├── backend/                      # 后端测试
�?      �?  ├── test_api.py
�?      �?  ├── test_models.py
�?      �?  └── ...
�?      ├── frontend/                     # 前端测试
�?      �?  ├── unit/                     # 单元测试
�?      �?  └── e2e/                      # 端到端测�?
�?      ├── integration/                  # 集成测试
�?      ├── test_reports/                 # 测试报告（gitignored�?
�?      └── README.md                     # 测试文档
�?
├── 📚 项目记录/                           # 项目文档�?大分类）�?
�?  ├── README.md                         # 文档索引
�?  ├── 项目状�?json                      # 项目状态（自动生成�?
�?  �?
�?  ├── 1-归档/                           # 过时文档归档
�?  �?  ├── README.md                     # 归档说明
�?  �?  └── [过时的文�?..]
�?  �?
�?  ├── 2-源参考对�?                     # 源项目对�?
�?  �?  ├── README.md
�?  �?  ├── 1-数据库Schema对照/
�?  �?  ├── 2-技术文档理�?
�?  �?  ├── 3-自动化验�?
�?  �?  ├── 4-完成度报�?
�?  �?  └── 5-版本历史/
�?  �?
�?  ├── 3-功能说明/                       # 功能详细说明
�?  �?  ├── API接口说明.md
�?  �?  ├── CRUD功能说明.md
�?  �?  └── [其他功能说明...]
�?  �?
�?  ├── 4-部署运维/                       # 部署和运�?
�?  �?  ├── 局域网访问指南.md
�?  �?  ├── 演示账号说明.md
�?  �?  └── [运维文档...]
�?  �?
�?  ├── 6-开发规�?                       # 开发规�?
�?  �?  ├── 文件操作强制检查清�?md
�?  �?  ├── 项目根目录管理规�?md
�?  �?  └── [规范文档...]
�?  �?
�?  ├── 7-过程记录/                       # 开发过程记�?
�?  �?  └── YYYY-MM-DD_[描述].md
�?  �?
�?  └── 8-聊天记录/                       # AI对话记录
�?      └── YYYY-MM-DD_完整对话记录.md
�?
├── 📚 知识�?                             # 只读参考库 �?
�?  ├── README.md                         # 知识库说�?
�?  └── {参考项目名}/                     # 源参考项目（如：sourceProject/�?
�?      └── [参考文�?..]
�?
├── 📄 test_git_hook.bat                  # Git Hook测试脚本
├── 📄 vscode-tasks-example.json          # VS Code任务示例
├── 📄 启动文件监控.bat                    # 文件监控启动
└── 📄 检查项目结�?bat                    # 结构检查快捷方�?
```

---

## 📂 目录详细说明

### 1️⃣ 代码主目�?`{项目名}-prototype/`

**命名规则**: 使用实际项目名称，后缀 `-prototype`（原型项目）或其他合适后缀

**特点**:
- �?前后端完全分�?
- �?独立的测试目�?
- �?各自的配置和依赖

---

### 2️⃣ 后端目录 `backend/`

**技术栈**: FastAPI + SQLAlchemy + Pydantic

**核心结构**:
```
backend/
├── app/                    # 应用代码
�?  ├── main.py            # FastAPI应用入口
�?  ├── models/            # 数据模型（数据库表）
�?  ├── schemas/           # 数据验证（API输入输出�?
�?  ├── api/               # API路由
�?  �?  └── v1/            # API版本控制
�?  ├── crud/              # 数据库操�?
�?  └── services/          # 业务逻辑
�?
├── scripts/               # 维护脚本
├── requirements.txt       # Python依赖
└── README.md             # 后端文档
```

**设计原则**:
- 🔷 **models** - 数据库表结构（ORM�?
- 🔷 **schemas** - API数据验证（Pydantic�?
- 🔷 **api** - 路由定义，按版本组织
- 🔷 **crud** - 数据库CRUD操作
- 🔷 **services** - 复杂业务逻辑

---

### 3️⃣ 前端目录 `frontend/`

**技术栈**: React + TypeScript + Vite + TailwindCSS

**核心结构**:
```
frontend/
├── src/
�?  ├── components/        # React组件
�?  �?  ├── common/        # 通用组件（Button, Input等）
�?  �?  ├── layout/        # 布局组件（Header, Sidebar等）
�?  �?  └── features/      # 功能组件
�?  �?
�?  ├── pages/             # 页面组件
�?  ├── services/          # API调用
�?  ├── hooks/             # 自定义Hooks
�?  ├── types/             # TypeScript类型定义
�?  └── utils/             # 工具函数
�?
├── public/                # 静态资�?
├── package.json           # npm配置
└── vite.config.ts         # Vite配置
```

**设计原则**:
- 🔷 **components** - 按用途分类（common/layout/features�?
- 🔷 **pages** - 页面级组件，对应路由
- 🔷 **services** - API调用封装
- 🔷 **hooks** - 自定义React Hooks
- 🔷 **types** - 统一的类型定�?

---

### 4️⃣ 测试目录 `tests/`

**特点**: 前后端测试统一管理

**结构**:
```
tests/
├── backend/               # 后端测试
�?  ├── test_api.py       # API测试
�?  └── test_models.py    # 模型测试
�?
├── frontend/              # 前端测试
�?  ├── unit/             # 单元测试（Vitest�?
�?  └── e2e/              # E2E测试（Playwright�?
�?
├── integration/           # 集成测试
└── test_reports/         # 测试报告（gitignored�?
```

---

### 5️⃣ 项目记录 `项目记录/`

**特点**: 8大分类文档管�?�?

**核心规则**:
- �?必须使用编号前缀�?-�?-�?
- �?编号必须连续
- �?根目录只放README.md和项目状�?json

**8大分�?*:

| 编号 | 目录�?| 用�?|
|------|--------|------|
| 1 | 1-归档/ | 过时文档归档 |
| 2 | 2-源参考对�? | 源项目对照分�?|
| 3 | 3-功能说明/ | 功能详细说明 |
| 4 | 4-部署运维/ | 部署运维文档 |
| 6 | 6-开发规�? | 开发规范和检查清�?|
| 7 | 7-过程记录/ | 开发过程记�?|
| 8 | 8-聊天记录/ | AI对话记录 |

**注意**: 原有5-问题分析已删除归�?

---

### 6️⃣ 知识�?`知识�?`

**特点**: 只读参�?🔒

**规则**:
- �?**允许**: 读取、引用、参�?
- �?**允许**: 添加新的参考文�?
- �?**禁止**: 修改已有文件
- �?**禁止**: 删除、重命名已有文件

**用�?*:
- 存放源项目代码（如：referenceProject/、sourceCode/ 等）
- 存放技术文�?
- 存放参考资�?

---

### 7️⃣ 规则系统 `.windsurf/`

**特点**: 完全可移植的AI规则系统 �?

**核心文件**:
- `00-core-principles.md` - 5大核心原�?
- `01-file-operations.md` - 文件操作5步检�?
- `02-directory-management.md` - 目录管理规则
- `03-naming-convention.md` - 命名规范
- `04-git-workflow.md` - Git工作�?
- `05-change-synchronization.md` - 变更同步规则
- `06-directory-architecture-template.md` - 本架构模�?

**工具脚本**:
- `check_project_structure.py` - 项目结构检�?
- `verify_portability.py` - 移植性验�?
- `install_git_hooks.py` - Git Hook安装
- �?..

---

## 🎯 架构变体

本架构模板提�?*标准结构**，可根据项目类型灵活调整�?

### 变体1: 全栈项目（标准架构）

```
{项目名}-prototype/
├── backend/              # 后端：FastAPI/Django/Flask
├── frontend/             # 前端：React/Vue/Angular
└── tests/                # 测试
```

**适用**: Web应用、管理系统、SaaS产品

---

### 变体2: 纯后端API项目

```
{项目名}-prototype/
├── backend/              # 后端API
�?  ├── app/
�?  ├── scripts/
�?  └── requirements.txt
└── tests/                # 测试
```

**特点**: 删除frontend/目录  
**适用**: REST API、微服务、数据服�? 
**示例**: WiseFido_TDPv1_Coding_Dictionary

---

### 变体3: 纯前端项�?

```
{项目名}-prototype/
├── frontend/             # 前端应用
�?  ├── src/
�?  └── package.json
└── tests/                # 测试
```

**特点**: 删除backend/目录  
**适用**: 静态网站、Jamstack、纯前端应用

---

### 变体4: 微服务架�?

```
{项目名}-microservices/
├── service-user/         # 用户服务
�?  ├── app/
�?  └── requirements.txt
├── service-order/        # 订单服务
�?  ├── app/
�?  └── requirements.txt
├── api-gateway/          # API网关
└── tests/                # 集成测试
```

**特点**: 多个独立服务目录  
**适用**: 大型系统、分布式应用

---

### 变体5: 数据科学项目

```
{项目名}-prototype/
├── notebooks/            # Jupyter笔记�?
├── src/                  # 源代�?
�?  ├── data/            # 数据处理
�?  ├── models/          # 模型定义
�?  └── visualization/   # 可视�?
├── data/                 # 数据文件
└── tests/                # 测试
```

**特点**: 增加notebooks和data目录  
**适用**: 机器学习、数据分�?

---

### 🔧 如何选择变体�?

| 项目类型 | 推荐变体 | 保留目录 |
|---------|---------|---------|
| Web全栈应用 | 变体1 | backend/ + frontend/ |
| REST API服务 | 变体2 | backend/ �?|
| 单页应用(SPA) | 变体3 | frontend/ �?|
| 微服务系�?| 变体4 | 多个服务目录 |
| 数据分析 | 变体5 | notebooks/ + src/ |

**核心不变**: 无论哪种变体，都保留�?
- �?`项目记录/`�?大分类）
- �?`知识�?`（只读参考）
- �?`.windsurf/`（规则系统）

---

## 📝 目录命名规范

### 代码主目录命�?

```bash
# 格式
{项目名}-prototype/

# 示例
HealthMonitor-prototype/      # 健康监测项目
SmartHome-prototype/          # 智能家居项目
Ecommerce-api/                # 电商API项目
DataAnalysis-ml/              # 数据分析项目
```

### 项目记录编号规范

```bash
# 必须使用编号前缀
1-归档/
2-源参考对�?
3-功能说明/
4-部署运维/
6-开发规�?
7-过程记录/
8-聊天记录/

# �?错误：缺少编�?
归档/
功能说明/
```

---

## 🚀 快速启动新项目

### 方法1: 手动创建

```bash
# 1. 创建项目目录
mkdir MyProject
cd MyProject

# 2. 创建主要目录
mkdir MyProject-prototype
mkdir 项目记录
mkdir 知识�?

# 3. 创建前后端目�?
cd MyProject-prototype
mkdir backend frontend tests

# 4. 创建项目记录8大分�?
cd ../项目记录
mkdir 1-归档 2-源参考对�?3-功能说明 4-部署运维 6-开发规�?7-过程记录 8-聊天记录

# 5. 复制规则系统
xcopy path\to\.windsurf ..\.windsurf\ /E /I

# 6. 修改配置
# 编辑 .windsurf/project-config.md
# 编辑 .windsurf/scripts/check_project_structure.py
```

### 方法2: 从模板复�?

```bash
# 1. 复制整个项目结构
xcopy {源项目} MyProject /E /I /EXCLUDE:exclude.txt
# 示例: xcopy ReferenceProject MyHealthApp /E /I

# 2. 清理代码目录
# 删除 MyProject-prototype/backend/app/ 下的代码
# 删除 MyProject-prototype/frontend/src/ 下的代码

# 3. 修改配置
# 更新 .windsurf/project-config.md
# 更新 README.md
```

---

## 💡 最佳实�?

### 1. 保持前后端分�?

```bash
�?好的设计:
{项目名}-prototype/
├── backend/              # 独立的后�?
�?  ├── app/
�?  ├── requirements.txt
�?  └── venv/
└── frontend/             # 独立的前�?
    ├── src/
    ├── package.json
    └── node_modules/

�?不好的设�?
{项目名}-prototype/
├── app.py               # 后端代码混在一�?
├── index.html
└── static/
    └── js/
```

### 2. 使用版本化API

```python
# �?好的设计
backend/app/api/v1/users.py
backend/app/api/v1/devices.py

# �?不好的设�?
backend/app/api/users.py  # 没有版本控制
```

### 3. 组件按功能分�?

```typescript
// �?好的设计
frontend/src/components/
├── common/              # 通用组件
�?  ├── Button.tsx
�?  └── Input.tsx
├── layout/              # 布局组件
�?  └── Header.tsx
└── features/            # 功能组件
    └── UserProfile/

// �?不好的设�?
frontend/src/components/
├── Button.tsx           # 所有组件平�?
├── Input.tsx
└── UserProfile.tsx
```

### 4. 项目记录必须分类

```bash
�?好的设计:
项目记录/
├── 1-归档/
├── 2-源参考对�?
└── ...

�?不好的设�?
项目记录/
├── 文档1.md            # 文件堆积在根目录
├── 文档2.md
└── ...
```

---

## 🔍 关键检查点

### 根目录检�?

```bash
�?README.md 存在
�?.gitignore 配置正确
�?.windsurf/ 目录完整
�?{项目名}-prototype/ 命名正确（使用实际项目名�?
�?项目记录/ 8大分类完�?
�?知识�? 目录存在
```

### 代码目录检�?

```bash
�?backend/ �?frontend/ 完全分离
�?tests/ 目录独立存在
�?各自�?README.md 存在
�?各自�?.gitignore 配置
```

### 项目记录检�?

```bash
�?8个编号目录存在（1-,2-,3-,4-,6-,7-,8-�?
�?编号连续，无跳号
�?根目录只�?README.md �?项目状�?json
�?各分类目录有自己�?README.md
```

---

## 📚 参考文�?

### 规则系统

- `.windsurf/README.md` - 规则系统总览
- `.windsurf/00-core-principles.md` - 核心原则
- `.windsurf/02-directory-management.md` - 目录管理
- `.windsurf/project-config.md` - 项目配置

### 技术文�?

- `{项目名}-prototype/backend/README.md` - 后端文档
- `{项目名}-prototype/frontend/README.md` - 前端文档
- `{项目名}-prototype/tests/README.md` - 测试文档

---

## 🔄 架构演进

### v1.0.0 (2025-11-26)
- �?初始版本
- �?基于owlRD-原型项目提炼
- �?支持FastAPI + React全栈项目

### 未来计划
- [ ] 添加Docker容器化配�?
- [ ] 添加CI/CD pipeline模板
- [ ] 添加API文档生成工具

---

**创建日期**: 2025-11-26  
**维护�?*: Cascade AI  
**状�?*: �?稳定使用  
**适用项目**: FastAPI + React 全栈项目

---

## 💡 快速参�?

### 核心目录速查�?

| 目录 | 用�?| 必需 | 可修�?|
|------|------|------|--------|
| `{项目名}-prototype/` | 代码主目�?| �?| �?(改名) |
| `backend/` | 后端代码 | �?| �?|
| `frontend/` | 前端代码 | �?| �?|
| `tests/` | 测试文件 | �?| �?|
| `项目记录/` | 文档管理 | �?| ⚠️ (保持8大分�? |
| `知识�?` | 只读参�?| �?| 🔒 (只读) |
| `.windsurf/` | 规则系统 | �?| ⚠️ (谨慎) |

**图例**:
- �?必需
- �?强烈推荐
- ⚠️ 谨慎修改
- 🔒 只读
