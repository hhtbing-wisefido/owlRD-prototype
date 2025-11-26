---
title: "Git Workflow"
description: "Git工作流规范"
trigger: always
---

# 🔀 Git工作流规�?

**规则类型**: 通用规则 �? 
**强制级别**: 🟡 强烈建议  
**适用场景**: Git操作和版本控�? 
**版本**: v1.0.0  

---

## 📋 目录

- [核心原则](#核心原则)
- [Commit消息规范](#commit消息规范)
- [分支管理策略](#分支管理策略)
- [提交前检查清单](#提交前检查清�?
- [代码审查要求](#代码审查要求)
- [Git最佳实践](#git最佳实�?
- [常见问题处理](#常见问题处理)

---

## 🎯 核心原则

### 四大核心原则

#### 1. 📝 **清晰的提交历�?* (Clear History)
```
�?好的提交历史:
feat: 添加用户认证功能
fix: 修复登录页面样式问题
docs: 更新API文档
refactor: 重构数据库访问层

�?糟糕的提交历�?
修改了一些东�?
update
fix bug
临时提交
今天的工�?
```

**原则**: 每个commit都应该清晰说明做了什�?

#### 2. 🎯 **原子性提�?* (Atomic Commits)
```
�?原子�?
commit 1: feat: 添加用户注册功能
commit 2: feat: 添加邮件验证功能
commit 3: test: 添加注册功能测试

�?大杂�?
commit 1: 添加用户注册、修复登录bug、更新文档、重构代�?
```

**原则**: 一个commit只做一件事，便于回滚和review

#### 3. 🔄 **频繁提交** (Frequent Commits)
```
�?频繁提交:
- 完成一个功�?�?commit
- 修复一个bug �?commit
- 重构一段代�?�?commit
- 更新一个文�?�?commit

�?累积提交:
- 工作了一整天 �?晚上一次性commit
- 完成整个模块 �?最后commit
```

**原则**: 小步快跑，降低风�?

#### 4. 🛡�?**保护主分�?* (Protect Main Branch)
```
�?正确流程:
main (受保�?
  �?
  merge (经过review)
  �?
develop
  �?
  合并 feature
  �?
feature/user-auth

�?错误做法:
直接�?main 上开�?�?
跳过 review 直接合并 �?
```

**原则**: main/master分支应该始终是稳定可发布�?

---

## 💬 Commit消息规范

### 基本格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

**必须使用以下类型之一**:

| Type | Emoji | 说明 | 示例 |
|------|-------|------|------|
| `feat` | �?| 新功�?| feat: 添加用户登录功能 |
| `fix` | 🐛 | Bug修复 | fix: 修复登录验证错误 |
| `docs` | 📝 | 文档更新 | docs: 更新API文档 |
| `style` | 🎨 | 代码格式�?| style: 格式化用户模块代�?|
| `refactor` | ♻️ | 重构 | refactor: 重构数据库访问层 |
| `perf` | �?| 性能优化 | perf: 优化查询性能 |
| `test` | �?| 测试相关 | test: 添加用户服务测试 |
| `build` | 🔧 | 构建系统 | build: 更新webpack配置 |
| `ci` | 👷 | CI配置 | ci: 添加自动化测�?|
| `chore` | 🔨 | 其他杂务 | chore: 更新依赖�?|
| `revert` | �?| 回滚 | revert: 回滚commit abc123 |

### Scope 范围（可选）

**指明改动的范�?*:

```
feat(auth): 添加登录功能
fix(ui): 修复按钮样式
docs(api): 更新用户接口文档
test(user): 添加用户服务测试
```

**常见scope**:
- 模块�? `auth`, `user`, `order`, `product`
- 层级�? `api`, `ui`, `db`, `service`
- 文件�? `README`, `package.json`
- 功能�? `login`, `register`, `payment`

### Subject 主题

**规则**:
- �?使用祈使句（"添加"而非"添加�?�?
- �?不要大写首字母（中文不影响）
- �?结尾不要加句�?
- �?不超�?0个字�?

**示例**:
```
�?正确:
feat: 添加用户认证功能
fix: 修复登录页面错误
docs: 更新部署指南

�?错误:
feat: 添加了用户认证功�?       # "添加�?改为"添加"
Fix: 修复登录页面错误           # 不要大写首字�?
docs: 更新部署指南�?           # 不要句号
feat: 这是一个非常非常长的提交消息超过了五十个字符的限制  # 太长
```

### Body 正文（可选）

**详细说明改动**:

```
feat: 添加用户认证功能

- 实现JWT token生成和验�?
- 添加登录、注册、登出接�?
- 集成邮箱验证功能
- 添加密码加密存储

相关issue: #123
```

**规则**:
- 解释"为什�?改动，而非"怎么"改动
- 可以分点列出多个改动
- 与subject之间空一�?

### Footer 页脚（可选）

**关联issue或重大变�?*:

```
feat: 重构API响应格式

BREAKING CHANGE: API响应格式�?{data} 改为 {success, data, message}

Closes #123
Closes #456
```

**常用标记**:
- `BREAKING CHANGE:` - 破坏性变�?
- `Closes #123` - 关闭issue
- `Fixes #123` - 修复issue
- `Refs #123` - 引用issue

### 完整示例

#### 示例1: 简单提�?
```
feat: 添加用户注册功能
```

#### 示例2: 带scope
```
fix(auth): 修复JWT token过期时间错误
```

#### 示例3: 完整格式
```
feat(user): 添加用户头像上传功能

- 支持上传jpg、png格式图片
- 限制文件大小不超�?MB
- 自动压缩和裁剪图�?
- 存储到云存储服务

Closes #234
```

#### 示例4: 破坏性变�?
```
refactor(api): 重构API响应格式

BREAKING CHANGE: 
所有API响应格式�?{data} 改为 {success, data, message}
前端需要相应调�?

Closes #456
```

### 使用Gitmoji（可选）

**在commit消息中添加emoji**:

```
�?feat: 添加用户认证功能
🐛 fix: 修复登录验证错误
📝 docs: 更新API文档
🎨 style: 格式化代�?
♻️ refactor: 重构数据库层
�?perf: 优化查询性能
�?test: 添加单元测试
🔧 build: 更新构建配置
```

**参�?*: https://gitmoji.dev/

---

## 🌿 分支管理策略

### Git Flow 分支模型

```
main (生产分支)
  �?
  ├─── develop (开发分�?
  �?     �?
  �?     ├─── feature/user-auth (功能分支)
  �?     ├─── feature/payment (功能分支)
  �?     └─── feature/dashboard (功能分支)
  �?
  ├─── release/v1.2.0 (发布分支)
  �?
  └─── hotfix/login-bug (热修复分�?
```

### 分支类型

#### 1. 📍 **main / master** (主分�?
```
用�? 生产环境代码
规则:
  - �?始终可发�?
  - �?每次合并都是一个新版本
  - �?不直接在此分支开�?
  - �?只接受来�?release �?hotfix 的合�?
```

#### 2. 🔄 **develop** (开发分�?
```
用�? 日常开发主分支
规则:
  - �?包含最新开发的功能
  - �?接受来自 feature 分支的合�?
  - �?不直接在此分支开发（除非很小的改动）
  - ⚠️ 应该始终是可运行的（虽然可能有bug�?
```

#### 3. �?**feature/** (功能分支)
```
命名: feature/功能�?
示例:
  - feature/user-auth
  - feature/payment-gateway
  - feature/email-notification

流程:
  1. �?develop 创建
  2. 开发功�?
  3. 提交�?develop
  4. 删除分支

命令:
  git checkout develop
  git checkout -b feature/user-auth
  # 开�?..
  git checkout develop
  git merge feature/user-auth
  git branch -d feature/user-auth
```

#### 4. 🐛 **bugfix/** (Bug修复分支)
```
命名: bugfix/bug描述
示例:
  - bugfix/login-error
  - bugfix/ui-layout-issue

流程: �?feature 分支相同
  1. �?develop 创建
  2. 修复bug
  3. 提交�?develop
  4. 删除分支
```

#### 5. 🚀 **release/** (发布分支)
```
命名: release/版本�?
示例:
  - release/v1.0.0
  - release/v1.2.0

流程:
  1. �?develop 创建
  2. 测试、修复小bug、更新版本号
  3. 合并�?main �?develop
  4. 打tag
  5. 删除分支

命令:
  git checkout develop
  git checkout -b release/v1.0.0
  # 测试和修�?..
  git checkout main
  git merge release/v1.0.0
  git tag -a v1.0.0 -m "Version 1.0.0"
  git checkout develop
  git merge release/v1.0.0
  git branch -d release/v1.0.0
```

#### 6. 🔥 **hotfix/** (热修复分�?
```
命名: hotfix/问题描述
示例:
  - hotfix/critical-security-bug
  - hotfix/payment-failure

用�? 修复生产环境的紧急bug

流程:
  1. �?main 创建
  2. 快速修�?
  3. 合并�?main �?develop
  4. 打tag
  5. 删除分支

命令:
  git checkout main
  git checkout -b hotfix/login-bug
  # 修复...
  git checkout main
  git merge hotfix/login-bug
  git tag -a v1.0.1 -m "Hotfix 1.0.1"
  git checkout develop
  git merge hotfix/login-bug
  git branch -d hotfix/login-bug
```

### 简化分支模型（小团�?个人项目�?

```
main
  �?
  ├─── feature/功能�?
  ├─── bugfix/bug描述
  └─── hotfix/紧急修�?

规则:
  - 所有分支从 main 创建
  - 完成后合并回 main
  - 删除已合并的分支
```

---

## �?提交前检查清�?

### 自动检查（Git Hook�?

**�?`.git/hooks/pre-commit` 中添加检�?*:

```bash
#!/bin/bash

echo "🔍 运行提交前检�?.."

# 1. 代码格式�?
echo "📝 检查代码格�?.."
npm run lint  # �?flake8, eslint�?
if [ $? -ne 0 ]; then
  echo "�?代码格式检查失�?
  exit 1
fi

# 2. 运行测试
echo "�?运行测试..."
npm test  # �?pytest, jest�?
if [ $? -ne 0 ]; then
  echo "�?测试失败"
  exit 1
fi

# 3. 检查目录规�?
echo "📁 检查目录规�?.."
python scripts/check_directory_standards.py
if [ $? -ne 0 ]; then
  echo "�?目录规范检查失�?
  exit 1
fi

echo "�?所有检查通过，可以提�?
exit 0
```

### 手动检查清�?

**每次提交前检�?*:

- [ ] 📝 **代码质量**
  - [ ] 代码已格式化（Prettier/Black/等）
  - [ ] 无lint错误和警�?
  - [ ] 无console.log/print调试语句
  - [ ] 无注释掉的代码块

- [ ] �?**测试**
  - [ ] 相关测试已通过
  - [ ] 新功能有对应测试
  - [ ] 测试覆盖率未降低

- [ ] 📄 **文档**
  - [ ] README已更新（如需要）
  - [ ] API文档已更新（如需要）
  - [ ] 注释清晰完整
  - [ ] Changelog已更新（如需要）

- [ ] 🔧 **配置和依�?*
  - [ ] 依赖已添加到配置文件
  - [ ] 环境变量已说�?
  - [ ] 配置示例已更�?

- [ ] 🚫 **禁止提交**
  - [ ] 无敏感信息（密码、token等）
  - [ ] 无大文件�?100MB�?
  - [ ] 无编译产物（dist/, build/等）
  - [ ] 无临时文件（.tmp, .log等）

- [ ] 📋 **Commit消息**
  - [ ] 使用了正确的type
  - [ ] subject清晰简�?
  - [ ] 包含必要的说�?

---

## 👥 代码审查要求

### Pull Request 规范

#### PR标题格式

```
<type>: <简要描�?

示例:
feat: 添加用户认证功能
fix: 修复登录页面样式问题
docs: 更新部署文档
```

#### PR描述模板

```markdown
## 📝 改动说明

简要描述这个PR的目的和主要改动

## 🎯 改动类型

- [ ] �?新功�?(feature)
- [ ] 🐛 Bug修复 (bugfix)
- [ ] 📝 文档更新 (docs)
- [ ] 🎨 代码格式�?(style)
- [ ] ♻️ 重构 (refactor)
- [ ] �?性能优化 (perf)
- [ ] �?测试 (test)
- [ ] 🔧 构建/工具 (build/chore)

## �?检查清�?

- [ ] 代码已格式化
- [ ] 测试已通过
- [ ] 文档已更�?
- [ ] 无调试代�?
- [ ] 已自我审�?

## 📸 截图（如适用�?

（添加UI变更的截图）

## 🔗 相关Issue

Closes #123
Refs #456

## 📋 测试说明

说明如何测试这个改动

## 💬 备注

（其他需要说明的内容�?
```

### Review检查要�?

**审查者应该检�?*:

#### 1. 📝 **代码质量**
- [ ] 代码逻辑正确
- [ ] 无明显bug
- [ ] 无代码重�?
- [ ] 变量命名清晰
- [ ] 注释充分

#### 2. 🏗�?**架构和设�?*
- [ ] 符合项目架构
- [ ] 模块划分合理
- [ ] 依赖关系清晰
- [ ] 无过度设�?

#### 3. �?**测试**
- [ ] 有对应测�?
- [ ] 测试覆盖充分
- [ ] 测试用例合理

#### 4. 📖 **文档**
- [ ] 代码有必要注�?
- [ ] 复杂逻辑有说�?
- [ ] API有文�?
- [ ] README已更�?

#### 5. �?**性能和安�?*
- [ ] 无明显性能问题
- [ ] 无安全漏�?
- [ ] 输入已验�?
- [ ] 错误已处�?

### Review反馈规范

**给出建设性的反馈**:

```markdown
�?好的反馈:
💡 建议: 这里可以使用Map代替循环查找，性能更好
⚠️ 问题: 这个函数太长了，建议拆分成几个小函数
�?疑问: 这里为什么要用setTimeout？有什么特殊原因吗�?

�?不好的反�?
这代码写得太烂了
你这样写不对
重写�?
```

**反馈优先�?*:

```
🔴 必须修复 (MUST):
  - 明显的bug
  - 安全问题
  - 破坏性变�?

🟡 建议修复 (SHOULD):
  - 性能问题
  - 代码质量
  - 设计改进

🟢 可选优�?(COULD):
  - 命名优化
  - 注释补充
  - 代码风格
```

---

## 💡 Git最佳实�?

### 1. 🔄 **频繁拉取更新**

```bash
# 每天开始工作前
git checkout develop
git pull origin develop

# 长期功能分支定期同步
git checkout feature/my-feature
git merge develop  # �?git rebase develop
```

### 2. 📦 **提交前整理commits**

**使用 interactive rebase**:

```bash
# 查看最�?个commits
git log --oneline -5

# 整理最�?个commits
git rebase -i HEAD~3

# 在编辑器�?
# pick abc123 feat: 添加功能A
# squash def456 fix: 修复功能A的bug
# squash ghi789 docs: 更新功能A文档

# 结果: 3个commits合并�?�?
```

**常用操作**:
- `pick` - 保留commit
- `squash` - 合并到前一个commit
- `reword` - 修改commit消息
- `drop` - 删除commit

### 3. 🎯 **清晰的commit粒度**

```
�?好的粒度:
commit 1: feat: 添加User模型
commit 2: feat: 添加User API路由
commit 3: feat: 添加User前端界面
commit 4: test: 添加User功能测试
commit 5: docs: 更新User功能文档

�?粒度太大:
commit 1: feat: 实现完整的用户管理功�?

�?粒度太小:
commit 1: feat: 添加user变量
commit 2: feat: 添加userId变量
commit 3: feat: 添加userName变量
```

### 4. 📝 **使用 .gitignore**

**重要规则**:

```gitignore
# 依赖
node_modules/
venv/
__pycache__/

# 构建产物
dist/
build/
*.pyc

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# 日志
*.log
logs/

# 临时文件
*.tmp
*.temp
temp/

# OS
.DS_Store
Thumbs.db
```

### 5. 🔖 **使用标签管理版本**

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标�?
git push origin v1.0.0

# 推送所有标�?
git push origin --tags

# 查看标签
git tag -l

# 删除标签
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### 6. 🛡�?**保护分支**

**在GitHub/GitLab中设�?*:

```
main 分支保护:
  �?需要PR才能合并
  �?需要至�?人review
  �?CI/CD必须通过
  �?禁止强制推�?
  �?禁止删除分支
```

---

## 🚨 常见问题处理

### 问题1: commit消息写错�?

**未推送的最近commit**:
```bash
# 修改最近一次commit消息
git commit --amend -m "正确的commit消息"
```

**已推送的commit**:
```bash
# ⚠️ 慎用！会改变历史
git commit --amend
git push --force-with-lease

# 或者添加新的commit来纠�?
git commit -m "docs: 修正上个commit的说�?
```

### 问题2: 提交了不该提交的文件

**未推�?*:
```bash
# 取消文件暂存
git reset HEAD <file>

# 或移除文件并重新commit
git rm --cached <file>
git commit --amend
```

**已推�?*:
```bash
# 添加�?.gitignore
echo "secret.txt" >> .gitignore

# 从Git移除但保留本地文�?
git rm --cached secret.txt
git commit -m "chore: 移除敏感文件"
git push
```

### 问题3: 需要回滚代�?

**回滚最近commit（不删除历史�?*:
```bash
# 创建反向commit
git revert HEAD
git push
```

**回滚到指定版本（危险�?*:
```bash
# ⚠️ 会删除历史！
git reset --hard <commit-hash>
git push --force-with-lease
```

### 问题4: 分支合并冲突

```bash
# 1. 尝试合并
git merge feature-branch

# 2. 解决冲突
# 编辑冲突文件，保留需要的代码

# 3. 标记为已解决
git add <resolved-files>

# 4. 完成合并
git commit

# 5. 推�?
git push
```

### 问题5: 误删分支

**恢复最近删除的分支**:
```bash
# 查找最近的commit
git reflog

# 从commit恢复分支
git checkout -b recovered-branch <commit-hash>
```

---

## �?Git工作流检查清�?

### 日常开�?

- [ ] 🌅 每天开始前拉取最新代�?
- [ ] 🌿 从正确的分支创建feature分支
- [ ] 📝 频繁提交，小步快�?
- [ ] �?提交前运行测�?
- [ ] 💬 使用规范的commit消息
- [ ] 🔄 定期同步主分�?
- [ ] 📤 推送到远程仓库备份
- [ ] 👥 创建PR等待review
- [ ] 🧹 合并后删除feature分支

### 发布流程

- [ ] 🌿 创建release分支
- [ ] 🧪 完整测试
- [ ] 📝 更新Changelog
- [ ] 📊 更新版本�?
- [ ] 🔀 合并到main
- [ ] 🔖 创建版本标签
- [ ] 🚀 部署到生产环�?
- [ ] 🔄 同步回develop分支
- [ ] 🧹 删除release分支

---

**规则维护**: AI开发规范系�? 
**最后更�?*: 2025-11-26  
**规则版本**: v1.0.0  
**适用项目**: 所有软件开发项�? 

---

## 🔗 相关资源

- 📖 [Gitmoji](https://gitmoji.dev/) - Git commit emoji规范
- 📖 [Conventional Commits](https://www.conventionalcommits.org/) - commit消息规范
- 📖 [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) - 分支管理模型
- 📖 [GitHub Flow](https://guides.github.com/introduction/flow/) - 简化的工作�?

## 🔗 相关规则

- 📄 [01-file-operations.md](01-file-operations.md) - 文件操作强制规则
- 📁 [02-directory-management.md](02-directory-management.md) - 目录管理规范
- 🏷�?[03-naming-convention.md](03-naming-convention.md) - 文件命名规范
- ⚙️ [project-config.md](project-config.md) - 项目配置
