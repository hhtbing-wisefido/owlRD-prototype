---
title: "Git Workflow"
description: "Git工作流规范"
trigger: always
---

# Git工作流规范

## Commit规范

### 格式
```
<type>: <subject>

<body>
```

### Type类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具

### 示例
```
feat: 添加用户认证功能

- 实现JWT令牌验证
- 添加登录/注销接口
- 更新相关文档
```

## Pre-commit Hook

### 自动检查
- ✅ 项目结构检查
- ✅ 文件命名规范
- ✅ 目录清洁度
- ✅ 文档同步状态

### Hook位置
`.git/hooks/pre-commit`

## 提交前检查

每次提交前确认：
1. ✅ 代码通过测试
2. ✅ 文档已更新
3. ✅ 索引已同步
4. ✅ 无临时文件
5. ✅ 遵守命名规范
