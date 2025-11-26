# 05 - 变更同步规则

**规则类别**: 强制执行  
**适用范围**: 所有文件修改、删除、重命名操作  
**优先级**: 🔴 高  
**版本**: v1.0  
**创建日期**: 2025-11-26  

---

## 📋 目录

- [核心原则](#核心原则)
- [适用场景](#适用场景)
- [修改文件后的同步要求](#修改文件后的同步要求)
- [删除文件后的同步要求](#删除文件后的同步要求)
- [重命名文件后的同步要求](#重命名文件后的同步要求)
- [检查清单](#检查清单)
- [严格禁止](#严格禁止)

---

## 🎯 核心原则

### 变更必须同步

```
代码变更 → 文档同步 → 索引更新 → 团队通知
```

**核心理念**:
- 💡 **文档是代码的一部分** - 修改代码=修改文档
- 🔄 **保持一致性** - 任何变更都要保持系统一致
- 📢 **透明沟通** - 修改要让团队知道
- ✅ **完整性检查** - 确认所有相关内容已更新

---

## 📚 适用场景

### 何时需要同步更新？

| 操作类型 | 需要同步 | 原因 |
|---------|---------|------|
| ✏️ 修改文件内容 | ✅ 必须 | 功能改变需要更新文档 |
| ❌ 删除文件 | ✅ 必须 | 索引需要移除 |
| 📝 重命名文件 | ✅ 必须 | 所有引用需要更新 |
| 📁 移动文件 | ✅ 必须 | 路径变更需要同步 |
| 🆕 添加新功能 | ✅ 必须 | README需要说明 |
| 🐛 修复Bug | ⚠️ 视情况 | 如影响使用需更新 |
| ♻️ 重构代码 | ⚠️ 视情况 | 如API改变需更新 |
| 💄 样式调整 | ❌ 通常不需要 | 不影响功能 |

---

## ✏️ 修改文件后的同步要求

### 场景1: 修改功能代码

**触发条件**:
- 修改了函数签名
- 修改了API接口
- 修改了配置格式
- 修改了使用方式

**必须更新**:

#### 1. 代码注释
```python
# 旧注释（需要更新）
def process_data(data):
    """处理数据"""
    
# 新注释（已更新）
def process_data(data, format="json"):
    """
    处理数据
    
    Args:
        data: 输入数据
        format: 输出格式，支持 'json' 或 'xml'（新增参数）
    """
```

#### 2. README.md
```markdown
# 旧README（需要更新）
## 使用方法
process_data(data)

# 新README（已更新）
## 使用方法
process_data(data, format="json")  # 新增format参数
```

#### 3. API文档
- 更新参数说明
- 更新示例代码
- 更新返回值说明

#### 4. CHANGELOG.md
```markdown
## [Unreleased]
### Changed
- `process_data()` 新增 `format` 参数，支持JSON和XML输出
```

---

### 场景2: 修改配置文件

**触发条件**:
- 修改了配置项
- 修改了默认值
- 添加了新配置

**必须更新**:

#### 1. 配置文档
```markdown
# config.md

## 配置项

### database.host (已更新)
- 类型: string
- 默认值: "localhost" → "127.0.0.1" (已修改)
- 说明: 数据库地址
```

#### 2. 配置示例
```yaml
# config.example.yml
database:
  host: "127.0.0.1"  # 已更新默认值
```

#### 3. README.md
- 更新配置说明部分
- 更新快速开始指南

---

### 场景3: 修改文档内容

**触发条件**:
- 修改了技术说明
- 修正了错误信息
- 更新了操作步骤

**必须更新**:

#### 1. 父目录README索引
```markdown
# 旧索引
- [部署指南](deployment.md) - 如何部署应用

# 新索引（如果修改了文档主题）
- [部署指南](deployment.md) - Docker和K8s部署方法（已更新）
```

#### 2. 相关引用
- 检查其他文档中的链接
- 检查代码注释中的引用
- 检查issue/PR中的引用

---

## ❌ 删除文件后的同步要求

### 必须执行的操作

#### 1. 从README索引中移除 ✅

```markdown
# 删除前
- [旧功能说明](old-feature.md)
- [新功能说明](new-feature.md)

# 删除后
- [新功能说明](new-feature.md)  # 已移除旧功能
```

#### 2. 检查并更新所有引用 ✅

**搜索命令**:
```bash
# 搜索文档引用
grep -r "old-feature" .

# 搜索代码引用
grep -r "old_feature" src/
```

**更新引用**:
- 移除失效链接
- 添加替代说明（如有）
- 或添加"已废弃"标记

#### 3. 更新相关文档 ✅

如果删除的文件是某个流程的一部分：
```markdown
# 流程文档需要更新

旧流程:
1. 配置环境
2. 运行old-feature  ← 需要删除
3. 验证结果

新流程:
1. 配置环境
2. 验证结果  ← 流程简化
```

#### 4. 添加删除说明 ✅

在CHANGELOG.md中记录:
```markdown
## [Unreleased]
### Removed
- 移除 `old-feature.md` - 功能已合并到 `new-feature.md`
```

---

## 📝 重命名文件后的同步要求

### 必须执行的操作

#### 1. 使用Git rename保留历史 ✅

```bash
# 正确做法
git mv old-name.md new-name.md

# 错误做法（会丢失历史）
rm old-name.md
create new-name.md
```

#### 2. 全局搜索更新引用 ✅

**文档引用**:
```bash
# 搜索Markdown链接
grep -r "old-name.md" .

# 批量替换
find . -name "*.md" -exec sed -i 's/old-name\.md/new-name.md/g' {} +
```

**代码引用**:
```bash
# 搜索import语句
grep -r "from old_module" src/

# 搜索文档链接
grep -r "old-name" docs/
```

#### 3. 更新README索引 ✅

```markdown
# 旧索引
- [旧名称](old-name.md)

# 新索引
- [新名称](new-name.md)  # 已重命名
```

#### 4. 更新项目配置 ✅

如果文件在配置中被引用：
```json
{
  "docs": [
    "old-name.md"  → "new-name.md"
  ]
}
```

#### 5. 通知团队 ✅

在PR或commit message中说明：
```
refactor: rename old-name.md to new-name.md

重命名原因: 更准确反映内容

影响:
- 更新了所有文档链接
- 更新了README索引
- 更新了项目配置
```

---

## ✅ 检查清单

### 修改文件后的检查清单

**代码修改**:
- [ ] 代码注释已更新
- [ ] README.md已更新
- [ ] API文档已更新（如适用）
- [ ] 示例代码已更新
- [ ] CHANGELOG.md已更新
- [ ] 单元测试已更新（如需要）

**配置修改**:
- [ ] 配置文档已更新
- [ ] 配置示例已更新
- [ ] 默认值说明已更新
- [ ] README配置章节已更新

**文档修改**:
- [ ] 索引已更新（如标题改变）
- [ ] 相关引用已检查
- [ ] 过时链接已移除

---

### 删除文件后的检查清单

- [ ] README索引已移除该文件
- [ ] 搜索并移除所有引用
- [ ] 相关流程文档已更新
- [ ] CHANGELOG.md已记录删除
- [ ] 替代方案已说明（如有）

---

### 重命名文件后的检查清单

- [ ] 使用git mv保留历史
- [ ] 全局搜索并更新文档引用
- [ ] 全局搜索并更新代码引用
- [ ] README索引已更新
- [ ] 项目配置已更新
- [ ] CHANGELOG.md已记录重命名
- [ ] 团队已通知

---

## 🚫 严格禁止

### 绝对不允许的操作

#### 1. ❌ 修改代码但不更新文档

**错误示例**:
```python
# 修改了代码
def process(data, format="json"):  # 新增参数
    pass

# 但README还是旧的
README.md: "使用 process(data)"  ❌ 未更新
```

**后果**:
- 用户困惑
- 浪费时间调试
- 技术债务累积

---

#### 2. ❌ 删除文件但不移除引用

**错误示例**:
```bash
# 删除了文件
rm old-feature.md

# 但README还在引用
README.md: "查看 [旧功能](old-feature.md)"  ❌ 失效链接
```

**后果**:
- 404链接
- 用户体验差
- 项目显得不专业

---

#### 3. ❌ 重命名文件但不更新引用

**错误示例**:
```bash
# 重命名了文件
git mv api.md api-reference.md

# 但其他文档还在用旧名
guide.md: "参考 [API文档](api.md)"  ❌ 失效链接
```

**后果**:
- 文档破碎
- 信息孤岛
- 维护困难

---

#### 4. ❌ 修改配置但不更新示例

**错误示例**:
```yaml
# config.yml 改了
database:
  host: "127.0.0.1"  # 改了默认值

# 但 config.example.yml 没改
database:
  host: "localhost"  ❌ 不一致
```

**后果**:
- 配置错误
- 部署失败
- 用户困惑

---

## 🔄 同步更新流程

### 标准流程

```
1. 进行修改
    ↓
2. 检查影响范围
    ├─ 代码注释
    ├─ README.md
    ├─ API文档
    ├─ 配置文档
    └─ CHANGELOG.md
    ↓
3. 逐一更新
    ├─ 更新注释
    ├─ 更新README
    ├─ 更新API文档
    ├─ 更新配置示例
    └─ 更新CHANGELOG
    ↓
4. 全局搜索验证
    ├─ grep 检查引用
    ├─ 检查链接有效性
    └─ 确认没有遗漏
    ↓
5. 提交更改
    ├─ 详细的commit message
    ├─ 说明修改内容和影响
    └─ 列出更新的文档
    ↓
6. 通知团队
    ├─ PR中说明变更
    ├─ 重要变更发通知
    └─ 更新团队文档
```

---

## 📊 实际示例

### 示例1: 修改API接口

**场景**: 为 `create_user()` 添加 `role` 参数

**需要更新**:

#### 1. 代码注释
```python
# 旧代码
def create_user(username, email):
    """创建用户"""

# 新代码
def create_user(username, email, role="user"):
    """
    创建用户
    
    Args:
        username: 用户名
        email: 邮箱
        role: 用户角色，默认为 "user"（新增）
    """
```

#### 2. API文档
```markdown
# api.md

## POST /api/users

### 参数
- username (string, 必需)
- email (string, 必需)
- role (string, 可选) - 用户角色，默认 "user" ⭐ 新增
```

#### 3. README.md
```markdown
# README.md

## 创建用户

python
user = create_user(
    username="john",
    email="john@example.com",
    role="admin"  # 可选，默认为 "user" ⭐ 新增
)
```

#### 4. CHANGELOG.md
```markdown
## [Unreleased]
### Added
- `create_user()` 新增 `role` 参数，支持创建不同角色的用户
```

---

### 示例2: 删除废弃功能

**场景**: 删除 `legacy-auth.md` 文档

**需要执行**:

#### 1. 删除文件
```bash
git rm docs/legacy-auth.md
```

#### 2. 从README移除
```markdown
# docs/README.md

# 旧索引
- [认证系统](auth.md)
- [旧版认证](legacy-auth.md) ← 删除这行
- [权限管理](permissions.md)

# 新索引
- [认证系统](auth.md)
- [权限管理](permissions.md)
```

#### 3. 搜索引用
```bash
grep -r "legacy-auth" .
```

#### 4. 更新相关文档
```markdown
# migration-guide.md

## 认证系统升级

旧版认证系统已废弃，请参考 [新版认证](auth.md)
```

#### 5. 记录CHANGELOG
```markdown
## [Unreleased]
### Removed
- 移除 `legacy-auth.md` - 旧版认证已完全废弃
- 所有项目应使用新版认证系统
```

---

## 🎯 最佳实践

### 1. 原子性变更

**一次提交包含**:
- ✅ 代码修改
- ✅ 文档更新
- ✅ 测试更新
- ✅ CHANGELOG更新

**优点**:
- 保持一致性
- 易于回滚
- 清晰的变更历史

---

### 2. 使用工具辅助

**检查链接有效性**:
```bash
# markdown-link-check
npx markdown-link-check docs/**/*.md
```

**搜索引用**:
```bash
# 搜索文件引用
rg "filename" --type md

# 搜索函数引用
rg "function_name" --type py
```

---

### 3. Code Review检查

**Review时确认**:
- [ ] 所有文档已更新
- [ ] 没有失效链接
- [ ] CHANGELOG已更新
- [ ] 示例代码可运行

---

## ❓ 常见问题

### Q1: 小修改也要更新文档吗？

**A**: 看影响范围

**需要更新**:
- ✅ API接口改变
- ✅ 配置格式改变
- ✅ 使用方式改变
- ✅ 参数含义改变

**可以不更新**:
- ✅ 内部实现优化
- ✅ 代码格式调整
- ✅ 性能优化（不影响使用）

---

### Q2: 如何确保没有遗漏？

**A**: 使用检查清单

1. ✅ 运行全局搜索
2. ✅ 检查README索引
3. ✅ 检查链接有效性
4. ✅ Code Review确认

---

### Q3: CHANGELOG必须每次都更新吗？

**A**: 重要变更必须更新

**必须更新**:
- ✅ 新功能
- ✅ Breaking Changes
- ✅ 重要Bug修复
- ✅ API变更

**可以不更新**:
- ✅ 文档修正
- ✅ 小的Bug修复
- ✅ 内部重构

---

## 📚 相关规则

- **00-core-principles.md** - 核心工作原则
- **01-file-operations.md** - 文件创建规则
- **03-naming-convention.md** - 文件重命名规范
- **04-git-workflow.md** - Git提交规范

---

**规则版本**: v1.0  
**最后更新**: 2025-11-26  
**维护状态**: ✅ 活跃维护中
