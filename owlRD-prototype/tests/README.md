# owlRD 系统测试

本目录包含owlRD项目的所有系统级测试脚本。

---

## 📁 目录结构

```
tests/
├── README.md                    ← 本文件
├── full_system_test.py          ← 全自动系统测试
└── test_reports/                ← 测试报告输出目录（自动创建）
```

---

## 🚀 快速开始

### 运行全自动测试

#### 方法1: 使用便捷脚本（Windows）
```bash
# 在项目根目录
run_tests.bat
```

#### 方法2: 直接运行Python脚本
```bash
# 在项目根目录
python tests/full_system_test.py
```

### 前提条件

**必须先启动后端服务**:
```bash
cd owlRD-prototype/backend
python start_with_check.py
```

后端服务应该运行在: http://localhost:8000

---

## 📋 测试内容

### full_system_test.py - 全系统自动化测试

**测试覆盖**:
- ✅ 健康检查端点
- ✅ API文档可访问性
- ✅ 租户管理API
- ✅ 用户和角色管理API
- ✅ 位置管理API（Location/Room/Bed）
- ✅ 住户管理API
- ✅ 设备管理API
- ✅ IoT数据API
- ✅ 告警系统API
- ✅ 卡片系统API
- ✅ 护理质量API
- ✅ 标准编码API
- ✅ 数据完整性检查

**测试方法**:
- GET请求测试
- POST请求测试（创建操作）
- 响应状态码验证
- 响应数据格式验证
- 数据存在性检查

**输出**:
- 彩色终端输出（实时结果）
- JSON格式的详细报告（保存在test_reports/）
- 统计信息（总数、通过、失败、通过率）

---

## 📊 测试报告

测试报告自动保存在 `test_reports/` 目录下，文件名格式：
```
test_report_YYYYMMDD_HHMMSS.json
```

**报告内容**:
```json
{
  "timestamp": "2025-11-22T15:30:00",
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "pass_rate": 96.0
  },
  "tests": [
    {
      "test": "健康检查端点",
      "passed": true,
      "details": "状态码: 200",
      "timestamp": "2025-11-22T15:30:01"
    }
    // ... 更多测试结果
  ]
}
```

---

## 🎯 测试场景

### 场景1: 功能验证测试
验证所有API端点是否正常工作。

### 场景2: 数据完整性测试
检查示例数据是否已正确初始化。

### 场景3: 端到端测试
测试创建、读取操作的完整流程。

---

## 💡 使用建议

### 开发阶段
- 每次修改API后运行测试
- 确保所有测试通过后再提交代码
- 关注失败的测试，及时修复

### 演示前
- 运行完整测试确保系统正常
- 检查测试报告确认通过率
- 验证所有核心功能可用

### 部署前
- 必须运行完整测试
- 要求100%测试通过
- 检查数据完整性

---

## 🔧 扩展测试

### 添加新的测试
在 `full_system_test.py` 中添加新的测试函数：

```python
def test_new_feature_endpoints():
    """测试新功能API"""
    print_section("新功能API测试")
    
    test_api_endpoint(
        "GET", "/new-feature/",
        "获取新功能列表"
    )
```

然后在 `main()` 函数中调用：
```python
test_new_feature_endpoints()
```

### 创建新的测试脚本
可以创建针对特定模块的测试脚本：
- `test_performance.py` - 性能测试
- `test_security.py` - 安全测试
- `test_integration.py` - 集成测试

---

## 📚 相关文档

- [主README - 快速开始](../README.md#快速开始)
- [后端README](../owlRD-prototype/backend/README.md)
- [项目维护清单](../项目记录/6-开发规范/项目维护清单.md)

---

## ⚠️ 常见问题

### Q: 测试失败：连接被拒绝
**A**: 后端服务未启动。先启动后端:
```bash
cd owlRD-prototype/backend
python start_with_check.py
```

### Q: 部分测试失败
**A**: 检查：
1. 后端服务是否正常运行
2. 端口8000是否正确
3. 是否初始化了示例数据

### Q: 如何只测试特定模块？
**A**: 编辑 `full_system_test.py`，注释掉不需要的测试函数调用。

---

**创建时间**: 2025-11-22  
**维护者**: 项目团队  
**状态**: ✅ 可用
