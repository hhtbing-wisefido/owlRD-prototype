# 项目工具脚本

本目录包含项目自动化工具脚本。

---

## 📝 脚本列表

### 1. `update_project_status.py`

**功能**: 自动更新项目状态文件

**作用**:
- 扫描后端代码统计行数
- 扫描前端代码统计行数
- 统计文档行数
- 获取Git提交次数
- 检测服务运行状态
- 更新`../项目记录/项目状态.json`

**使用**:
```bash
cd scripts
python update_project_status.py
```

**自动运行**: 
- 每次`git commit`时自动运行（通过Git Hook）

---

### 2. `update_status.bat`

**功能**: Windows快捷启动脚本

**作用**:
- 双击运行`update_project_status.py`
- 显示友好的界面
- 运行后暂停查看结果

**使用**:
- 双击`update_status.bat`文件

---

### 3. `check_directory_standards.py` ⭐

**功能**: 项目记录目录规范检查

**作用**:
- 检查顶层目录完整性（1-8编号）
- 检查子目录结构（如2-源参考对照的1-5子目录）
- 检查根目录文件规范
- 检测临时文件和需要归档的文件
- 检查聊天记录完整性
- 生成检查报告JSON

**使用**:
```bash
# 命令行运行
python scripts/check_directory_standards.py

# 或使用批处理文件
scripts\check_standards.bat
```

**检查项**:
- ✅ 目录编号是否连续
- ✅ 必需目录是否存在
- ✅ 根目录是否有不规范文件
- ✅ 是否有临时文件需要清理
- ✅ 聊天记录是否完整

**输出**:
- 控制台：详细检查结果
- 文件：`项目记录/directory_check_report.json`

---

### 4. `check_standards.bat`

**功能**: Windows目录规范检查快捷脚本

**作用**:
- 双击运行`check_directory_standards.py`
- 显示检查结果
- 等待查看后关闭

**使用**:
- 双击`check_standards.bat`文件

---

## 🔧 维护

### 添加新脚本

1. 在此目录创建脚本文件
2. 添加执行权限（Linux/Mac）
3. 更新本README说明

### 修改现有脚本

编辑脚本文件后：
- 测试运行确保正常
- 更新相关文档

---

## 📚 相关文档

- [状态自动更新说明](../项目记录/状态自动更新说明.md) - 详细使用指南
- [项目状态](../项目记录/项目状态.json) - 自动更新的状态文件

---

**创建时间**: 2025-11-20  
**最后更新**: 2025-11-22  
**维护者**: 项目团队  
**状态**: ✅ 自动化运行中
