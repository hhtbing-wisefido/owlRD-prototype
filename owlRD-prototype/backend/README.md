# owlRD Backend

Python FastAPI后端服务

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 启动服务

```bash
# 开发模式（自动重载）
python -m uvicorn app.main:app --reload --port 8000

# 或直接运行
python app/main.py
```

### 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # Pydantic数据模型
│   ├── services/            # 业务逻辑服务
│   ├── api/v1/              # API路由
│   └── data/                # JSON数据存储
├── tests/                   # 测试文件
├── requirements.txt         # Python依赖
└── .env.example            # 环境变量示例
```

## 开发进度

- ✅ **Phase 1: 项目基础设施搭建** (已完成)
  - ✅ 目录结构
  - ✅ 配置文件
  - ✅ FastAPI应用框架
  - ✅ 基础模型（Tenant, User, Role）
  - ✅ API路由存根
  - ✅ 存储服务框架

- ✅ **Phase 2: 数据模型完整实现** (已完成 - 100%)
  - ✅ Tenant模型（完成 - 100%）
  - ✅ User/Role模型（完成 - 100%）
  - ✅ Location/Room/Bed模型（完成 - 100%）
  - ✅ Resident系列模型（完成 - 100%）
    - ✅ Resident（完全匿名化）
    - ✅ ResidentPHI（加密存储）
    - ✅ ResidentContact（家属账号）
    - ✅ ResidentCaregiver（护士关联）
    - ✅ AnonymousNamePool（300个匿名代称）
  - ✅ Device模型（完成 - 100%）
  - ✅ IoT数据模型（完成 - 100%）
    - ✅ IOTTimeseries（TimescaleDB超表）
    - ✅ IOTMonitorAlert（设备报警配置）
  - ✅ Alert模型（完成 - 100%）
    - ✅ CloudAlertPolicy（20+报警类型）
  - ✅ Card模型（完成 - 100%）
    - ✅ Card（ActiveBed/Location卡片）
    - ✅ CardDevice（卡片-设备关联）
  - ✅ Config模型（完成 - 100%）
    - ✅ ConfigVersion（统一配置历史）
    - ✅ PostureMapping（姿态映射）
    - ✅ EventMapping（事件映射）
  - ✅ TDP协议模型（完成 - 100%）
    - ✅ PersonMatrix（人员矩阵）
    - ✅ ObjectMatrix（物体矩阵）
    - ✅ TDPEvent（TDP事件）
    - ✅ LiteEventHeader / ExtendEventHeader
  - ✅ SNOMED CT编码（完成 - 100%）
    - ✅ PostureCode（15个编码）
    - ✅ MotionStateCode（12个编码）
    - ✅ HealthConditionCode（12个编码）
    - ✅ SleepStateCode（4个编码）
    - ✅ VitalSignsCode（5个编码）
    - ✅ AbnormalVitalSignsCode（10个编码）
    - ✅ SafetyEventCode（6个编码）

- ⏳ **Phase 3-10**: 其他阶段（规划中）

**已完成**: 19/19个模型 (100%)  
**代码量**: ~3500行（含注释和文档）  
**字段映射**: 100%（未简化任何SQL字段）

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_models.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## API端点

当前可用端点：

- `GET /` - 健康检查
- `GET /health` - 详细健康检查
- `GET /docs` - Swagger UI文档
- `GET /api/v1/tenants` - 租户列表（存根）
- `GET /api/v1/users` - 用户列表（存根）
- `GET /api/v1/residents` - 住户列表（存根）
- `GET /api/v1/devices` - 设备列表（存根）
- `GET /api/v1/alerts` - 告警列表（存根）
- `GET /api/v1/cards` - 卡片列表（存根）
- `GET /api/v1/care-quality/report` - 护理质量报告（存根）
- `WS /api/v1/realtime/ws` - WebSocket实时数据（存根）

## 下一步计划

1. 完成19个数据模型的完整实现
2. 实现存储服务的CRUD操作
3. 实现SNOMED CT编码系统
4. 实现TDPv2协议处理
5. 实现Person/Object Matrix
6. 实现多级报警系统
7. 实现护理质量评估算法
8. 实现健康基线建模
9. 实现卡片自动生成逻辑
10. 完善WebSocket实时推送
