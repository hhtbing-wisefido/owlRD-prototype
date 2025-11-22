# Backend Scripts

**目录**: `backend/scripts/`  
**用途**: 自动化验证和维护脚本

---

## 📋 脚本清单

### 1. validate_alignment.py (442行)

**功能**: 验证后端Pydantic Model与SQL定义的对齐度

**详细功能**:
- 从SQL文件提取字段定义（CREATE TABLE解析）
- 从Pydantic Model提取字段定义
- 对比字段名、类型、可空性
- 生成详细对齐报告

**用法**:
```bash
python scripts/validate_alignment.py
```

**输出**:
- 控制台：对齐度百分比
- 文件：`../../项目记录/AUTO_对齐验证报告.md`

**依赖**:
- Python 3.8+
- Pydantic Models in `app/models/`
- SQL files in `../../owdRD_github_clone_源参考文件/owlRD/db/`

---

### 2. sync_checklist.py (420行)

**功能**: 智能同步检查清单，自动更新对齐状态

**详细功能**:
- 运行`validate_alignment.py`获取验证结果
- 智能过滤合理差异（主键/外键/时间戳/Optional类型）
- 计算调整后的对齐分数
- 自动更新检查清单
- 生成优先级分级的TODO清单

**用法**:
```bash
python scripts/sync_checklist.py
```

**输出**:
- `../../项目记录/2-源参考对照/1-数据库Schema对照/检查清单.md` (更新)
- `../../项目记录/AUTO_TODO修复清单.md`

**智能过滤规则**:
```python
REASONABLE_EXTRA_FIELDS = {
    'tenant_id', 'created_at', 'updated_at',
    'device_id', 'user_id', 'resident_id',
    'location_id', 'room_id', 'bed_id',
    # ... 等主键/外键/时间戳字段
}
```

---

### 3. validate_frontend_types.py (400行)

**功能**: 验证前端TypeScript类型与后端Pydantic Model的对齐度

**详细功能**:
- 解析TypeScript接口定义（正则匹配）
- 从Python Model提取字段定义
- 智能类型匹配（string ↔ UUID/str/datetime）
- 对比前后端类型一致性
- 生成详细对齐报告

**用法**:
```bash
python scripts/validate_frontend_types.py
```

**输出**:
- 控制台：前端类型对齐度
- 文件：`../../项目记录/AUTO_前端类型对齐报告.md`

**类型映射规则**:
```python
TYPE_MAPPINGS = {
    'string': ['str', 'UUID', 'EmailStr', 'datetime', 'date'],
    'number': ['int', 'float', 'Decimal'],
    'boolean': ['bool'],
    'Record<string, any>': ['Dict', 'dict'],
}
```

---

## 🚀 典型工作流

### 修改Model后验证

```bash
# 1. 修改app/models/*.py

# 2. 验证后端对齐
python scripts/sync_checklist.py

# 3. 查看报告
cat ../../项目记录/AUTO_对齐验证报告.md
cat ../../项目记录/AUTO_TODO修复清单.md

# 4. 如果有问题，修复Model

# 5. 重新验证直到100%对齐
```

### 修改前端类型后验证

```bash
# 1. 修改../../frontend/src/types/index.ts

# 2. 验证前端对齐
python scripts/validate_frontend_types.py

# 3. 查看报告
cat ../../项目记录/AUTO_前端类型对齐报告.md

# 4. 修复类型定义直到对齐
```

### 一键全栈验证

```bash
# 验证所有
python scripts/sync_checklist.py && python scripts/validate_frontend_types.py

# 查看所有AUTO报告
ls ../../项目记录/AUTO_*.md
```

---

### 4. init_sample_data.py (1236行) ⭐

**功能**: 初始化完整示例数据（19/19表）

**详细功能**:
- 严格按照SQL Schema生成示例数据
- 覆盖所有19个表（Tenant/User/Resident/Device/IoT/Alert等）
- 包含加密PHI数据、告警策略、卡片功能等
- ~100条示例记录，可立即用于演示和测试

**用法**:
```bash
python scripts/init_sample_data.py
```

**输出**:
- 在`app/data/`目录下创建所有JSON数据文件
- 控制台显示详细初始化进度

**数据覆盖**:
- ✅ 基础数据：租户、角色、用户、位置
- ✅ 住户数据：住户、PHI、联系人、护理人员
- ✅ 设备数据：IoT设备、时序数据
- ✅ 告警数据：告警策略、告警记录
- ✅ 卡片数据：卡片、卡片功能
- ✅ 配置数据：配置版本、映射表
- ✅ 报告数据：护理质量报告

---

## 📊 当前对齐状态

| 维度 | 对齐度 | 状态 |
|------|--------|------|
| 后端Model ↔ SQL | 100% | ✅ |
| 前端Type ↔ 后端Model | 100% | ✅ ⭐ |
| 示例数据覆盖 | 100% (19/19表) | ✅ ⭐ |
| 全栈平均 | **100%** | 🎊 |

**更新时间**: 2025-11-22

---

## 💡 最佳实践

1. **每次修改Model后运行验证**
   ```bash
   python scripts/sync_checklist.py
   ```

2. **每次修改types/index.ts后运行验证**
   ```bash
   python scripts/validate_frontend_types.py
   ```

3. **CI集成（未来）**
   ```yaml
   # .github/workflows/validate.yml
   - name: Validate alignment
     run: |
       python backend/scripts/sync_checklist.py
       python backend/scripts/validate_frontend_types.py
   ```

4. **定期检查AUTO报告**
   - 发现技术债务
   - 优先修复核心功能

---

## 🔗 相关文档

- [自动化验证体系说明](../../项目记录/2-源参考对照/2-自动化验证/README.md)
- [检查清单](../../项目记录/2-源参考对照/1-数据库Schema对照/检查清单.md)
- [方案B执行总结](../../项目记录/3-功能说明/方案B执行总结.md)

---

**维护者**: Development Team  
**最后更新**: 2025-11-22  
**脚本数量**: 4个  
**总代码量**: ~2500行
