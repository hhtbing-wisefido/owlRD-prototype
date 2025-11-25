# owlRD Backend API

智慧养老IoT监测系统 - Python FastAPI后端服务

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 下载Swagger UI（首次运行）

```bash
python scripts/download_swagger_ui.py
```

### 3. 初始化示例数据（可选）

```bash
python scripts/init_sample_data.py
```

### 4. 启动服务器

```bash
# 方法1: 智能启动脚本（推荐 ⭐ - 自动检查端口冲突）
python start_with_check.py

# 方法2: 手动uvicorn启动（仅当确认端口未被占用）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方法3: Python直接运行
python -m app.main
```

**为什么推荐使用 `start_with_check.py`**:
- ✅ 自动检测端口8000是否被占用
- ✅ 提供交互式进程清理选项
- ✅ 避免端口冲突错误
- ✅ 友好的启动提示信息

### 5. 访问API文档

**推荐使用本地版（完全离线）：**
```
http://localhost:8000/docs-local
```

**所有文档地址：**
- 本地Swagger: http://localhost:8000/docs-local （⭐ 推荐 - 完全离线）
- 国内CDN: http://localhost:8000/docs-cn （需联网）
- 默认版本: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI规范: http://localhost:8000/api/openapi.json

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
├── scripts/                 # 后端维护工具
├── start_with_check.py      # 启动脚本（带端口检查）
├── requirements.txt         # Python依赖
└── .env.example            # 环境变量示例

注意：所有测试文件已迁移至 ../tests/ 目录
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
**代码量**: ~9,500行（含注释和文档）  
**字段映射**: 100%（未简化任何SQL字段）  
**API端点**: 68个完整实现  
**示例数据**: 19/19表完整覆盖（~100条记录） ⭐  
**最后更新**: 2025-11-22

## 测试

所有测试已统一迁移至 `../tests/` 目录。

```bash
# 运行完整系统测试（推荐）
cd ../tests
python full_system_test.py

# 运行后端API测试
python full_system_test.py --backend

# 运行CRUD测试
python test_crud_all.py
python test_crud_all_v2.py
```

详细测试文档请参考: `../tests/README.md`

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

## 🌐 局域网访问

### 获取本机IP

**Windows:**
```bash
ipconfig
# 查找 "IPv4 地址"
```

**Linux/Mac:**
```bash
ifconfig  # 或 ip addr show
```

### 局域网访问地址

假设你的IP是 `192.168.2.6`：

**API文档（推荐使用本地版）：**
```
http://192.168.2.6:8000/docs-local
```

**其他端点：**
- API文档（国内CDN）: http://192.168.2.6:8000/docs-cn
- 健康检查: http://192.168.2.6:8000/health
- WebSocket: ws://192.168.2.6:8000/api/v1/realtime/ws/{tenant_id}

### 防火墙配置

**Windows（管理员权限）：**
```powershell
netsh advfirewall firewall add rule name="owlRD API" dir=in action=allow protocol=TCP localport=8000
```

**Linux：**
```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

### 测试局域网访问

```bash
# 从其他设备测试
curl http://192.168.2.6:8000/health

# 或运行测试脚本
python test_docs.py
```

## 📚 文档访问说明

本项目提供4种API文档访问方式：

| 端点 | CDN来源 | 推荐场景 | 特点 |
|------|---------|---------|------|
| `/docs-local` | 本地文件 | ⭐⭐⭐⭐⭐ 生产/离线 | 完全离线、最稳定、速度快 |
| `/docs-cn` | 国内CDN | ⭐⭐⭐⭐ 开发/局域网 | 需联网、国内访问快 |
| `/docs-offline` | FastAPI内置 | ⭐⭐⭐ 备用 | 使用Python包自带资源 |
| `/docs` | 国外CDN | ⭐⭐ 仅本机 | 局域网可能白屏 |

### 为什么需要本地部署？

**问题：** 局域网设备访问 `/docs` 出现白屏  
**原因：** Swagger UI默认从国外CDN加载资源，局域网无法访问  
**解决：** 下载Swagger UI到本地，完全离线可用

### 首次使用

团队成员克隆项目后，需运行一次：
```bash
python download_swagger_ui.py
```

这会自动下载约10MB的Swagger UI静态文件到 `app/static/swagger-ui/`。

## 📁 重要文件说明

```
backend/
├── app/
│   ├── main.py                  # FastAPI应用入口（已挂载静态文件）
│   ├── config.py                # 配置管理（host=0.0.0.0支持局域网）
│   ├── api/
│   │   ├── docs.py              # 国内CDN文档路由
│   │   ├── docs_local.py        # 本地文件文档路由
│   │   ├── docs_offline.py      # 离线文档路由
│   │   └── v1/                  # API路由
│   ├── static/
│   │   └── swagger-ui/          # Swagger UI本地文件（不提交到Git）
│   ├── models/                  # 数据模型
│   ├── services/                # 业务逻辑
│   └── data/                    # JSON数据存储
├── download_swagger_ui.py       # Swagger UI下载脚本
├── test_docs.py                 # 文档端点测试脚本
├── init_sample_data.py          # 示例数据初始化
├── start_server.bat/sh          # 启动脚本
└── requirements.txt             # Python依赖
```

## 🧪 测试

### 测试所有文档端点

```bash
python test_docs.py
```

预期输出：
```
🦉 owlRD API文档端点测试
==============================================================================
✅ /                        根路径健康检查                [200]
✅ /health                  详细健康检查                  [200]
✅ /docs-local              本地Swagger UI（推荐）        [200]
...
测试结果: 8/8 通过
🎉 所有端点测试通过！
```

### 运行单元测试

```bash
pytest
pytest --cov=app --cov-report=html
```

## ⚙️ 配置说明

### 环境变量

创建 `.env` 文件（可选）：
```bash
cp .env.example .env
```

主要配置项：
```bash
APP_NAME=owlRD Prototype
DEBUG=True
HOST=0.0.0.0              # 监听所有网络接口
PORT=8000
CORS_ORIGINS=["*"]         # 开发环境允许所有源
LOG_LEVEL=INFO
```

### CORS配置

生产环境建议修改 `app/config.py`：
```python
cors_origins = [
    "http://your-frontend-ip:3000",
    "http://another-allowed-ip:8080"
]
```

## 🐛 故障排查

### 问题1: 局域网白屏

**症状：** 局域网设备访问 `/docs` 白屏  
**原因：** 无法访问国外CDN  
**解决：** 使用本地版 `/docs-local`

### 问题2: /docs-local 显示404

**原因：** 静态文件未下载  
**解决：**
```bash
python download_swagger_ui.py
```

### 问题3: 端口被占用

**解决：** 修改端口
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 问题4: 防火墙阻止

**检查：**
```bash
# Windows
netstat -ano | findstr :8000

# Linux
ss -tuln | grep :8000
```

应该看到 `0.0.0.0:8000` 表示监听所有网络接口。

## 📊 项目进度

- ✅ Phase 1: 基础设施搭建（100%）
- ✅ Phase 2: 数据模型实现（19/19模型，100%）
- ✅ Phase 3: 本地Swagger UI部署（100%）
- ⏳ Phase 4-10: 业务逻辑实现（进行中）

**已完成：**
- 19个完整数据模型
- 完全匿名化系统
- SNOMED CT编码
- TDPv2协议模型
- 本地API文档部署
- 局域网访问支持

**代码量：** ~4500行（含注释和文档）

## 🔒 安全建议

### 开发环境
- ✅ CORS允许所有源
- ✅ DEBUG模式开启
- ✅ 详细日志记录

### 生产环境
- ⚠️ 配置具体CORS源
- ⚠️ 关闭DEBUG模式
- ⚠️ 启用HTTPS
- ⚠️ 添加认证中间件
- ⚠️ 配置防火墙规则
- ⚠️ 使用环境变量管理敏感信息

## 📞 支持

- 项目地址: https://github.com/hhtbing-wisefido/owlRD-prototype
- 源项目: https://github.com/sady37/owlRD
- 文档问题: 查看 `/docs-local` 获取完整API文档

---

**配置完成！现在可以在局域网内任何设备访问API了！** 🎉

推荐访问: `http://your-ip:8000/docs-local`
