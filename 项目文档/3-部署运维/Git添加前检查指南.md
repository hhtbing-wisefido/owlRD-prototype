# Git添加前检查指南

**创建时间**: 2025-11-27  
**目的**: 避免误提交临时文件、空文件和旧目录  

---

## 🎯 为什么需要检查？

### 常见问题

使用 `git add -A` 或 `git add .` 会**无差别添加所有文件**，可能导致：

1. ❌ 提交临时文件（test.py, temp.md等）
2. ❌ 提交空文件（0字节）
3. ❌ 提交旧目录（已重命名但未删除）
4. ❌ 提交不应该在Git中的文件

### 历史教训

**2025-11-27 发生的问题**：
- 误提交了 `.windsurfrules/`（旧目录）
- 误提交了 `add_frontmatter.py`（空文件）
- 误提交了 `simplify_remaining.py`（空文件）
- 误提交了 `项目记录/`（旧目录名）

---

## ✅ 推荐流程（3步检查法）

### 方法1：使用检查脚本（最安全）⭐

```powershell
# 步骤1: 运行预检查脚本
.\.windsurf\scripts\git_add_check.ps1

# 步骤2: 根据提示决定操作
#   - 如有可疑文件，先处理
#   - 如无问题，继续下一步

# 步骤3: 选择性添加文件
git add "项目文档/2-开发记录/2025-11-27_某某.md"
git add ".windsurf/rules/某规则.md"

# 步骤4: 提交前再次确认
git status
git diff --cached --name-only

# 步骤5: 提交
git commit -m "描述"
```

### 方法2：手动检查流程

```powershell
# 步骤1: 查看工作区状态
git status

# 步骤2: 仔细查看每个文件
#   - 新文件（??）：是否应该提交？
#   - 修改文件（M）：修改是否正确？
#   - 删除文件（D）：确认删除？

# 步骤3: 检查文件大小
Get-ChildItem -Recurse | Where-Object { $_.Length -eq 0 }

# 步骤4: 选择性添加
git add <文件路径>

# 步骤5: 再次确认
git status
git diff --cached

# 步骤6: 提交
git commit -m "描述"
```

### 方法3：分批添加（最谨慎）

```powershell
# 按目录分批添加

# 1. 添加文档
git add "项目文档/**/*.md"

# 2. 添加规则
git add ".windsurf/rules/**/*.md"

# 3. 添加代码（如需要）
git add "project-code/**/*.py"
git add "project-code/**/*.ts"

# 4. 检查暂存区
git status

# 5. 提交
git commit -m "描述"
```

---

## 🔍 检查脚本使用说明

### 基本用法

```powershell
# 运行检查
.\.windsurf\scripts\git_add_check.ps1

# 预览模式（不交互）
.\.windsurf\scripts\git_add_check.ps1 -DryRun
```

### 脚本输出说明

```
=== Git Add 预检查 ===

📋 工作区状态：
?? add_frontmatter.py
M  README.md

🔍 文件分析：
  📄 新文件: 1个
  ✏️ 修改文件: 1个
  🗑️ 删除文件: 0个

⚠️ 发现可疑文件：
  ❌ add_frontmatter.py  ← 匹配 temp/test 模式

📊 空文件检查：
  ⚠️ add_frontmatter.py (0字节)

📁 按目录分组：
  📂 根目录 (2个文件):
     - add_frontmatter.py
     - README.md

💡 建议操作：
  ⚠️ 发现问题文件，建议：
     1. 检查并删除临时文件/空文件
     2. 更新 .gitignore
     3. 使用选择性添加：git add <文件路径>
```

---

## 🚫 禁止的操作

### ❌ 绝对不要这样做

```powershell
# 1. 不检查就批量添加
git add -A  # 危险！
git add .   # 危险！

# 2. 不看git status就提交
git commit -m "update"  # 不知道提交了什么

# 3. 忽略警告信息
# 看到可疑文件警告，但仍然继续提交
```

---

## ✅ 推荐的操作

### ✅ 安全的做法

```powershell
# 1. 先检查
.\.windsurf\scripts\git_add_check.ps1

# 2. 选择性添加（明确指定文件）
git add "项目文档/2-开发记录/2025-11-27_功能开发.md"
git add ".windsurf/rules/05-测试组织规范.md"

# 3. 提交前确认
git status
git diff --cached --name-only

# 4. 确认无误再提交
git commit -m "docs: 添加功能开发记录和测试规范"

# 5. 推送前最后检查
git log --oneline -3
git push origin main
```

---

## 📝 .gitignore 配置

### 已配置的忽略规则

```gitignore
# 临时文件
add_frontmatter.py
simplify_remaining.py
*_temp.py
*_test.py
*.tmp
*.log

# 旧目录
.windsurfrules/
项目记录/

# 自动生成的报告
项目文档/完成度报告_*.md
```

### 如何添加新的忽略规则

1. 编辑 `.gitignore` 文件
2. 添加要忽略的文件/目录模式
3. 提交 `.gitignore` 的更改

```powershell
# 示例
echo "new_temp_file.py" >> .gitignore
git add .gitignore
git commit -m "chore: 更新.gitignore"
```

---

## 🔧 常见场景

### 场景1：添加新的开发记录

```powershell
# ✅ 正确做法
git add "项目文档/2-开发记录/2025-11-27/2025-11-27_1430_功能完成.md"
git commit -m "docs: 添加功能完成记录"
```

### 场景2：添加新的规则文件

```powershell
# ✅ 正确做法
git add ".windsurf/rules/10-新规则.md"
git commit -m "feat: 添加新规则 v1.0"
```

### 场景3：修改多个文件

```powershell
# ✅ 正确做法
# 1. 先检查
git status

# 2. 逐个添加
git add "README.md"
git add "项目文档/README.md"

# 3. 确认
git status

# 4. 提交
git commit -m "docs: 更新README"
```

### 场景4：发现误添加

```powershell
# 如果不小心添加了错误的文件
git reset HEAD <文件>  # 从暂存区移除

# 或者重置所有
git reset HEAD .  # 移除所有暂存的文件
```

---

## 📊 检查清单

### 提交前必查项

- [ ] ✅ 运行了 `git_add_check.ps1` 脚本
- [ ] ✅ 检查了 `git status` 输出
- [ ] ✅ 确认没有可疑文件（temp, test, old等）
- [ ] ✅ 确认没有空文件（0字节）
- [ ] ✅ 确认没有误添加旧目录
- [ ] ✅ 使用了选择性添加（而非批量添加）
- [ ] ✅ 提交前查看了 `git diff --cached`
- [ ] ✅ 提交信息清晰明确

---

## 🎓 最佳实践总结

### 核心原则

1. **🔍 先检查，后添加** - 永远先看 `git status`
2. **✅ 选择性添加** - 明确指定每个文件
3. **📋 提交前确认** - 查看 `git diff --cached`
4. **🚫 避免批量操作** - 不用 `git add -A`
5. **📝 维护 .gitignore** - 及时添加忽略规则

### 养成的习惯

```powershell
# 每次提交前的标准流程
.\.windsurf\scripts\git_add_check.ps1  # 1. 检查
git add <文件>                          # 2. 选择性添加
git status                              # 3. 确认
git diff --cached                       # 4. 查看变更
git commit -m "描述"                    # 5. 提交
git push origin main                    # 6. 推送
```

---

## 🆘 紧急处理

### 如果已经误提交了

```powershell
# 方案1: 从Git中删除，但保留本地
git rm --cached <文件>
git commit -m "chore: 删除误提交的文件"
git push origin main

# 方案2: 回退提交（未推送的情况）
git reset HEAD~1  # 回退一个提交

# 方案3: 修改最后一次提交（未推送）
git reset HEAD~1
# 重新添加正确的文件
git add <正确的文件>
git commit -m "正确的描述"
```

---

## 📞 获取帮助

**遇到问题时**：
1. 查看本文档
2. 运行检查脚本查看提示
3. 执行 `git status` 了解状态
4. 如有疑问，先不要提交！

**参考资源**：
- `.windsurf/scripts/git_add_check.ps1` - 检查脚本
- `.gitignore` - 忽略规则
- 项目文档/3-部署运维/ - 其他运维文档

---

**记住：谨慎比速度更重要！** 🎯

**创建日期**: 2025-11-27  
**维护者**: Benson  
**状态**: ✅ 活跃维护
