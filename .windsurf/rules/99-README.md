---
title: "Rules System Overview"
description: "规则系统总览"
trigger: manual
---

# Windsurf 规则系统总览

## 规则分类

### 🔴 核心强制规则（Always On）
1. **00-core-principles** - 核心工作原则（最高优先级）
2. **01-file-operations** - 文件操作规范
3. **02-directory-management** - 目录管理规范
4. **03-naming-convention** - 文件命名规范
5. **04-git-workflow** - Git工作流规范
6. **05-change-synchronization** - 变更同步规则
7. **05-test-organization** - 测试组织规范
8. **07-strict-directory-control** - 严格目录控制
9. **08-rule-self-enforcement** - 规则自我执行机制

### 🟡 智能决策规则（Model Decision）
- **06-directory-architecture-template** - 目录架构模板
- **09-project-config** - 项目特定配置

### 📖 参考文档（Manual）
- **10-architecture-guide** - 架构模板使用指南
- **11-rule-sync-guide** - 规则同步说明
- **12-migration-checklist** - 规则移植检查清单
- **13-project-config-example** - 项目配置示例
- **99-README** - 本文档

## 规则优先级

```
最高优先级：00 核心原则
高优先级：  01-05, 07-08 强制规则
中优先级：  06, 09 智能决策
低优先级：  10-13, 99 参考文档
```

## 激活模式说明

- **Always On** - 自动应用，无需@mention
- **Model Decision** - AI根据上下文决定
- **Manual** - 需要@mention激活

## 快速开始

1. **查看核心规则**：`@00-core-principles`
2. **检查项目结构**：运行 `check_project_structure.py`
3. **移植到新项目**：参考 `@12-migration-checklist`

## 规则文件要求

- 格式：Markdown (.md)
- 大小：≤12,000字符
- 命名：`NN-descriptive-name.md`
- frontmatter：必须包含title, description, trigger

## 工具脚本

位置：`.windsurf/scripts/`

主要脚本：
- `check_project_structure.py` - 项目结构检查
- `check_directory_standards.py` - 目录标准检查
- `update_config_rules.py` - 更新配置

## 版本信息

- **当前版本**: v2.0.0
- **规则数量**: 16个（9个强制 + 2个智能 + 5个参考）
- **最后更新**: 2025-11-26
