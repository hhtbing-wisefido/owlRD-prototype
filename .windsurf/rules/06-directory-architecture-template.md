---
title: "Directory Architecture Template"
description: "通用项目目录架构标准"
trigger: model_decision
---

# 目录架构模板

## 标准目录结构

```
项目根目录/
├── 项目记录/              # 项目相关文档
│   ├── 1-归档/           # 历史文档归档
│   ├── 2-源参考对照/     # 源代码参考
│   ├── 3-功能说明/       # 功能文档
│   ├── 4-部署运维/       # 部署相关
│   ├── 6-开发规范/       # 开发规范
│   ├── 7-过程记录/       # 过程记录
│   └── 8-聊天记录/       # AI对话记录
├── 知识库/                # 只读参考资料
├── .windsurf/            # Windsurf配置
│   ├── rules/           # 规则文件
│   └── scripts/         # 工具脚本
├── tests/               # 测试文件
│   └── test_reports/    # 测试报告
├── [项目名]-prototype/   # 代码目录
│   ├── backend/         # 后端代码
│   ├── frontend/        # 前端代码
│   └── docs/            # 技术文档
└── README.md            # 项目说明
```

## 核心原则

### 1. 项目记录（必需）
8个编号目录，不得增减：
1. **1-归档** - 历史文档
2. **2-源参考对照** - 数据库/API对照
3. **3-功能说明** - 功能文档
4. **4-部署运维** - 部署指南
5. **6-开发规范** - 编码规范
6. **7-过程记录** - 临时文档
7. **8-聊天记录** - AI对话

### 2. 代码目录命名
- 格式：`[项目名]-[类型]`
- 示例：`myapp-prototype`, `myapp-backend`, `myapp-frontend`
- 允许类型：prototype, backend, frontend, api, ml

### 3. 禁止的目录
❌ 编号外的目录（如`5-xxx`）
❌ 无编号的顶层目录
❌ 临时/测试目录在根目录

## 使用建议

**新项目初始化**：
1. 创建8个项目记录目录
2. 创建代码目录
3. 复制规则系统
4. 创建README.md

**检查合规性**：
```bash
python .windsurf/scripts/check_project_structure.py
```
