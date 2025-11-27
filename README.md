# owlRD 原型项目

> **WiseFido智慧养老IoT监测系统** - 完整功能原型实现  
> 基于 [sady37/owlRD](https://github.com/sady37/owlRD) 源项目的Python Web实现

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev/)

---

## 📋 项目简�?
owlRD是一�?*专业级智慧养老IoT监测系统**，为老年护理机构（Elder Care）和高级生活社区（Senior Living）提供：

- 🚨 **跌倒监�?*: 基于雷达轨迹的多级确认机�?- 💓 **生命体征**: 非接触式呼吸�?心率监测
- 🏥 **护理质量**: 空间智能分析与团队绩效评�?- 🔔 **智能预警**: 5级报警系统（L1-L8�?- 🏷�?**医疗标准**: SNOMED CT + HL7 FHIR集成
- 🔐 **隐私保护**: HIPAA合规，完全匿名化

### 与源项目的关�?
- **源参�?*: `owdRD_github_clone_源参考文�?` - GitHub源代码（PostgreSQL版本�?- **本项�?*: Python + JSON实现，保�?00%功能等价�?- **校验机制**: 自动检测源文件更新并生成差异报�?
---

## 🏗�?系统架构

### 技术栈

#### 后端
- **FastAPI** - 异步Web框架，自动OpenAPI文档
- **Pydantic** - 数据验证与序列化
- **aiofiles** - 异步文件IO
- **Protobuf** - TDPv2协议实现
- **pytest** - 测试框架

#### 前端
- **React 18 + TypeScript** - 现代化UI框架
- **TailwindCSS** - 实用优先的CSS框架
- **shadcn/ui** - 高质量UI组件
- **Recharts** - 数据可视�?- **React Query** - 数据获取与缓�?
#### 存储方案
- **JSON文件** - 替代PostgreSQL，易于版本管�?- **内存缓存** - LRU缓存提升性能
- **分片存储** - 时序数据轮转机制

---

## 🎯 核心功能

### 1. 实时监测系统

#### 跌倒检�?- 多传感器融合（雷�?+ 压力板）
- Person Matrix 实时跟踪
- 5级置信度判断
- 前后3秒点云存�?
#### 生命体征监测
- **心率(HR)**: 正常[55-95] / L3[55-89�?0-95] / L2[45-54�?6-115] / L1[0-44�?16+]
- **呼吸�?RR)**: 正常[10-23] / L3[10-12�?3-23] / L2[8-9�?4-26] / L1[0-7�?7+]
- 持续时间阈值：L1�?分钟，L2/L3�?分钟

#### 行为识别
- 上床/离床/坐起
- 姿态变化检测（SNOMED CT编码�?- 运动状态分析（静止/移动/异常步态）

### 2. 护理质量评估

#### 空间智能分析
- 护工-住户实时距离计算
- 有效护理区域定义（默�?.2米）
- 护理时长统计（总时�?有效时长/占比�?
#### 团队级报告（完全匿名�?- 房间覆盖�?- 响应时间达标�?- 无效走动比例
- 班次效率对比
- 7�?30天趋势分�?
#### 住户健康基线
- 睡眠质量（总卧床时长、离床次数）
- 日间活动能力（移动距离、坐站频次）
- 生活规律性（起床时间稳定性）
- 异常预警（活动下降、睡眠紊乱）

### 3. 多级报警系统

| 级别 | 名称 | 触发条件 | 响应方式 | CoAP |
|------|------|---------|---------|------|
| **L1** | EMERGENCY | 高风�?高置�?| 立即报警，所有终端，警号响起，必须手工取�?| CON |
| **L2** | ALERT | 高危事件 | 网页显示，App/Watch选择发送，警号响起 | CON |
| **L3** | CRITICAL | 严重事件 | 网页显示，App/Watch选择发送，不响警号 | CON |
| **L5** | WARNING | 高风�?低置�?| 30秒本地确�?120秒二次确认，Server�?0秒内取消 | CON |
| **L8** | DEBUG | 内部记录 | AI训练数据，不对外报警 | - |
| **L9** | CANCEL | 取消警报 | 清除所有计时器和通知 | CON |

#### 多级确认机制
1. **第一级（本地确认�?*: 30秒倒计时，语音询问"Are you OK?"
2. **第二级（床头主机�?*: 150秒倒计时，闪烁+语音提示
3. **权威决策**: Server可在50秒内发�?假报�?否决

### 4. IoT设备管理

#### TDPv2协议 (Telemetry Data Protocol v2)
- 基于Protobuf的高效二进制协议
- 支持LITE/FULL两种数据报模�?- CodeableConcept支持多编码系�?- 张量负载支持压缩（RLE/LZ4/GZIP�?
#### Person Matrix (人员矩阵)
```c
{
  "producer_id": "device_id(48bit) + tracking_id(16bit)",
  "pos_x, pos_y, pos_z": "三维坐标(cm)",
  "vel_x, vel_y, vel_z": "三维速度(cm/s)",
  "height": "身高(cm)",
  "posture": {"category": "Posture", "code": "102538003"},  // SNOMED CT
  "motion_state": {"category": "MotionState", "code": "129006008"},
  "health_score": {"category": "HealthCondition", "code": "49049000"},
  "confidence": 95
}
```

#### Object Matrix (物体矩阵)
- 床、轮椅、沙发等物体识别
- 危险区域标注（高�?60cm的区域）
- 房间布局（雷达坐标转房间坐标�?
### 5. 卡片系统

#### 两种卡片类型
- **ActiveBed卡片**: 床位级监控，路由到resident_caregivers指定护士
- **Location卡片**: 位置级监控，区分公共空间/个人空间

#### 自动生成规则
- SQL函数驱动的自动化创建
- 基于设备绑定关系动态生�?- 支持卡片权限继承和覆�?
#### 告警路由
```
设备触发告警 �?确定卡片类型
  ├─ ActiveBed �?resident_caregivers查找负责护士
  └─ Location
      ├─ 公共空间/多人房间 �?警报通报�?alert_user_ids + alert_tags)
      └─ 个人空间 �?住户护士 �?警报通报�?```

### 6. 医疗标准集成

#### SNOMED CT编码
- **姿态编�?*: STANDING(102538003), SITTING(102491009), LYING_SUPINE(40199007)
- **运动编码**: WALKING(129006008), ABNORMAL_GAIT(22325002), SHUFFLING_GAIT(249911004)
- **健康编码**: PARKINSONS_DISEASE(49049000), FALL_EVENT(161898004), FALL_RISK(129839007)

#### HL7 FHIR
- Patient资源映射（匿名化�?- Observation资源（生命体征）
- Condition资源（健康状况）
- 与EHR系统对接

---

## 📂 项目结构

```
owlRD-原型项目/                        �?主项目目�?= Git仓库根目�?├── owdRD_github_clone_源参考文�?     # GitHub源代码（参考）
├── 项目聊天记录/                      # 开发过程记�?├── owlRD-prototype/                  # 代码子目�?�?  ├── backend/                      # Python后端
�?  �?  ├── app/
�?  �?  �?  ├── main.py              # FastAPI入口
�?  �?  �?  ├── models/              # Pydantic数据模型
�?  �?  �?  �?  ├── base.py          # 基础模型
�?  �?  �?  �?  ├── tenant.py        # 租户模型
�?  �?  �?  �?  ├── user.py          # 用户/角色模型
�?  �?  �?  �?  ├── location.py      # 位置/房间/床位
�?  �?  �?  �?  ├── resident.py      # 住户（匿名化�?�?  �?  �?  �?  ├── device.py        # IoT设备
�?  �?  �?  �?  ├── iot_data.py      # 时序数据
�?  �?  �?  �?  ├── alert.py         # 报警策略
�?  �?  �?  �?  ├── card.py          # 卡片系统
�?  �?  �?  �?  ├── tdp.py           # TDPv2协议
�?  �?  �?  �?  └── snomed.py        # SNOMED CT编码
�?  �?  �?  ├── services/            # 业务逻辑
�?  �?  �?  �?  ├── storage.py       # JSON存储引擎
�?  �?  �?  �?  ├── alert_engine.py  # 报警引擎
�?  �?  �?  �?  ├── care_quality.py  # 护理质量评估
�?  �?  �?  �?  ├── baseline.py      # 健康基线建模
�?  �?  �?  �?  ├── card_manager.py  # 卡片管理
�?  �?  �?  �?  ├── tdp_processor.py # TDP数据处理
�?  �?  �?  �?  └── matrix.py        # Person/Object Matrix
�?  �?  �?  ├── api/                 # API路由
�?  �?  �?  �?  ├── v1/
�?  �?  �?  �?  �?  ├── tenants.py
�?  �?  �?  �?  �?  ├── users.py
�?  �?  �?  �?  �?  ├── residents.py
�?  �?  �?  �?  �?  ├── devices.py
�?  �?  �?  �?  �?  ├── alerts.py
�?  �?  �?  �?  �?  ├── cards.py
�?  �?  �?  �?  �?  ├── care_quality.py
�?  �?  �?  �?  �?  └── realtime.py  # WebSocket
�?  �?  �?  └── data/                # JSON数据存储
�?  �?  �?      ├── tenants.json
�?  �?  �?      ├── users.json
�?  �?  �?      ├── locations.json
�?  �?  �?      ├── residents.json
�?  �?  �?      ├── devices.json
�?  �?  �?      ├── iot_timeseries/  # 分片存储
�?  �?  �?      ├── alerts.json
�?  �?  �?      └── cards.json
�?  �?  ├── requirements.txt
�?  �?  └── README.md
�?  ├── frontend/                     # React前端
�?  �?  ├── src/
�?  �?  �?  ├── components/          # UI组件
�?  �?  �?  ├── pages/               # 页面
�?  �?  �?  ├── hooks/               # React Hooks
�?  �?  �?  ├── services/            # API调用
�?  �?  �?  └── types/               # TypeScript类型
�?  �?  ├── package.json
�?  �?  └── README.md
�?  ├── scripts/                      # 工具脚本
�?  �?  ├── sync_validator.py        # 源文件校�?�?  �?  ├── sql_parser.py            # SQL解析�?�?  �?  └── data_migrator.py         # 数据迁移
�?  ├── tests/                        # 测试框架�?8个测试，100%通过）✅
�?  �?  ├── full_system_test.py      # 主测试脚本（统一入口�?�?  �?  ├── test_frontend_unit.py    # 前端单元测试
�?  �?  ├── test_e2e.py              # E2E端到端测�?�?  �?  ├── test_api_integration.py  # API集成测试
�?  �?  ├── test_security.py         # 安全测试
�?  �?  ├── locustfile.py            # 性能测试配置
�?  �?  ├── test_reports/            # 测试报告
�?  �?  �?  └── test_report_*.json
�?  �?  └── README.md                # 测试文档
�?  └── docs/                         # 项目文档
�?      ├── API.md                    # API文档
�?      ├── DATA_MODEL.md             # 数据模型
�?      ├── TDP_PROTOCOL.md           # TDP协议说明
�?      └── DEPLOYMENT.md             # 部署指南
├── .validation_config.json           # 校验配置
└── README.md                         # 本文�?```

---

## 🚀 快速开�?
### 环境要求
- Python 3.11+
- Node.js 18+
- npm/yarn
- 端口8000�?000未被占用

### 安装与运�?
#### 1. 后端启动
```bash
cd owlRD-prototype/backend

# 安装依赖
pip install -r requirements.txt

# 首次运行：下载Swagger UI（用于局域网访问�?python scripts/download_swagger_ui.py

# 启动服务（推�?- 自动检查端口冲突）
python start_with_check.py
```

**访问地址**:
- 本机: http://localhost:8000/docs-local
- 局域网: http://192.168.2.6:8000/docs-local

#### 2. 初始化示例数�?```bash
cd owlRD-prototype/backend
python init_sample_data.py
```

#### 3. 前端启动
```bash
cd owlRD-prototype/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器（支持局域网访问�?npm run dev
```

**访问地址**:
- 本机: http://localhost:3000
- 局域网: http://192.168.2.6:3000

### 常见问题

**端口被占�?*:
```bash
# Windows - 查找并结束进�?netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

**没有数据显示**: 运行 `python init_sample_data.py` 初始化数�?
**局域网白屏**: 使用本地Swagger `/docs-local` 而不�?`/docs`

**详细配置**: 查看 [局域网访问指南](项目文档/4-部署运维/局域网访问指南.md)

---

## 🧪 系统测试

### 全自动测试框�?
**测试结果**: �?**48个测试，100%通过** 🎉

**运行完整系统测试**:
```bash
# 方法1: 使用便捷脚本（Windows�?cd owlRD-prototype/scripts
run_tests.bat

# 方法2: 直接运行（推荐）
cd owlRD-prototype
python tests/full_system_test.py --all

# 方法3: 分类运行
python tests/full_system_test.py --backend    # 后端API测试�?7个）
python tests/full_system_test.py --frontend   # 前端测试�?个）
python tests/full_system_test.py --integration # 集成测试�?个）

# 查看测试报告
python tests/full_system_test.py --report
```

**前提条件**: 后端服务必须已启动（`http://localhost:8000`�?
### 测试覆盖详情

#### 后端API测试�?7个）�?- **健康检�?*: 2�?- 系统状态、根路径
- **API文档**: 3�?- Swagger UI、OpenAPI规范
- **租户管理**: 3�?- 列表、创建、查�?- **用户管理**: 3�?- 列表、创建�?*删除** �?- **位置管理**: 3�?- 列表、创建�?*删除** �?- **住户管理**: 5�?- 列表、创建�?*删除** ⭐、联系人、护理关�?- **设备管理**: 3�?- 列表、创建�?*删除** �?- **IoT数据**: 2�?- 查询、统�?- **告警管理**: 3�?- 列表、统计、策�?- **卡片管理**: 1�?- 列表
- **护理质量**: 2�?- 报告、评�?- **数据完整�?*: 6�?- 各实体数据存在性检�?
#### 前端测试�?个）�?- **编译构建**: TypeScript编译、构建输�?- **代码质量**: ESLint检查（0错误�?警告�?- **组件检�?*: 20个组件�?4个页面�?个服�?- **功能组件**: 5个表单（新建/编辑）�?6个模态框（删除）�?
#### 集成测试�?个）�?- **E2E测试**: 用户/住户/设备 完整CRUD流程测试框架
- **API集成**: 后端连通性测�?
### 测试报告

**报告位置**: `tests/test_reports/test_report_YYYYMMDD_HHMMSS.json`

**报告内容**:
- 测试统计（总数、通过、失败、通过率）
- 详细测试结果（每个测试的状态和详情�?- 执行时间�?
**详细文档**: 
- 📖 [完整测试指南](owlRD-prototype/tests/README.md)
- 📝 [测试框架完善报告](项目文档/7-过程记录/2025-11-22_1940_测试框架完善完成报告.md)

---

## 📊 数据模型

### 核心实体�?9个）

1. **tenants** - 租户（多租户隔离�?2. **roles** - 角色（RBAC权限�?3. **users** - 用户
4. **locations** - 位置/地址
5. **rooms** - 房间
6. **beds** - 床位
7. **residents** - 住户（完全匿名化，使�?00个匿名代称）
8. **resident_phi** - 住户健康信息（加密存储）
9. **resident_contacts** - 住户联系�?10. **resident_caregivers** - 护理人员关系
11. **devices** - IoT设备
12. **iot_timeseries** - IoT时序数据
13. **iot_monitor_alerts** - IoT监控警报
14. **cloud_alert_policies** - 云端警报策略
15. **config_versions** - 配置版本
16. **mapping_tables** - 映射�?17. **cards** - 卡片
18. **anonymous_name_pool** - 匿名代称池（300个）
19. **card_functions** - 卡片自动生成函数

### Location-�?设备绑定关系
```
Location (位置/地址)
  ├── Room (房间)
  �?    ├── Bed (床位)
  �?    �?    ├── Resident (住户) �?residents.bed_id
  �?    �?    └── Device (设备) �?devices.bound_bed_id
  �?    └── Device (设备) �?devices.bound_room_id
  ├── Resident (住户) �?residents.location_id (HomeCare/单人�?夫妻套房)
  └── Device (设备) �?devices.location_id (未绑床设�?
```

---

## 🔐 隐私与合�?
### HIPAA合规
- �?完全匿名化（无PII存储在主表）
- �?PHI数据加密（resident_phi表）
- �?访问审计日志
- �?最小权限原�?
### 匿名代称系统�?00个）
- **职业类（50个）**: 锅匠、钟表匠、邮差、渔�?..
- **影视角色�?0个）**: 哆啦A梦、小王子、E.T....
- **动物类（100个）**: 水豚、猫头鹰、考拉...
- **生活物品�?00个）**: 茶壶、雨伞、藤�?..

---

## 🧪 测试

```bash
# 单元测试
pytest tests/unit -v

# 集成测试
pytest tests/integration -v

# E2E测试
pytest tests/e2e -v

# 覆盖�?pytest --cov=app tests/
```

---

## 📈 项目状�?
**当前状�?*: �?95%完成 - 生产就绪

> 💡 **实时数据**: 查看 [`项目文档/项目状�?json`](项目文档/项目状�?json) 获取自动更新的准确统�?>
> 该文件定期更新，包含�?> - 实时代码行数统计�?8,000+行）
> - Git提交次数�?7次）
> - 服务运行状�?> - Phase完成情况
> - 完成度检查完成度（Schema 100% + 文档 88% = 总体 95%�?> - 最近里程碑记录

---

## 🔄 校验机制

### 自动校验流程
```bash
python scripts/sync_validator.py
```

### 校验内容
1. SQL表结�?vs JSON Schema对比
2. 字段类型、约束、索引一致性检�?3. 业务逻辑完整性验�?4. 文档更新检�?5. 生成差异报告

---

## 📚 文档

- [API文档](docs/API.md) - RESTful API接口说明
- [数据模型](docs/DATA_MODEL.md) - 完整数据模型文档
- [TDP协议](docs/TDP_PROTOCOL.md) - TDPv2协议实现
- [部署指南](docs/DEPLOYMENT.md) - 生产环境部署

---

## 🤝 贡献

本项目为原型实现，基于源参考项目保�?00%功能等价性�?
---

## 📄 许可�?
MIT License

---

## 📞 联系方式

- **源项�?*: https://github.com/sady37/owlRD
- **项目文档**: �?`docs/` 目录
- **问题反馈**: 通过Issue提交

---

## 📊 项目进展

### 项目完成�?�?
**扫描时间**: 2025-11-22 (最终版)

| 项目 | 完成�?| 代码行数 | 文件�?| 状�?|
|------|--------|---------|--------|------|
| **后端** | 92% | 9,500+�?| 57个Python文件 | �?优秀 |
| **前端** | 95% | 10,700+�?| 40个TypeScript文件 | �?卓越 �?|
| **文档** | 100% | 8,000+�?| 35个文档文�?| �?完善 |
| **总计** | **95%** | **28,200+�?* | - | **🎉 生产就绪** |

**核心组件**:
- �?数据模型: 19�?(Tenant, User, Resident, Device, Alert, Card, etc.)
- �?业务服务: 7�?(Storage, SNOMED, TDP, AlertEngine, CareQuality, etc.)
- �?API端点: 68个端点（完整RESTful API�?- �?前端页面: 12�?(Dashboard, Residents, Devices, Alerts, AlertPolicies �? CareQuality, Cards �? IoTData �? Users, Locations, Roles, Login)
- �?WebSocket: 实时数据推�?- �?数据可视�? 10+个图表组�?�?- �?示例数据: 19/19表完整覆�?�?- �?源参考对�? Schema 100% + 文档理解 88% = 总体 95% �?
> 📊 **查看详细统计**: 运行 `scripts\update_status.bat` 或查�?`项目文档/项目状�?json`

### 🎯 快速开�?
#### 后端启动
```bash
cd owlRD-prototype/backend

# 首次运行：下载Swagger UI
python scripts/download_swagger_ui.py

# 启动服务（推�?- 自动检查端口冲突）
python start_with_check.py
```

**访问地址**:
- 本机: http://localhost:8000/docs-local
- 局域网: http://192.168.2.6:8000/docs-local

#### 前端启动
```bash
cd owlRD-prototype/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

**访问地址**:
- 本机: http://localhost:3000
- 局域网: http://192.168.2.6:3000

#### 🌐 局域网访问配置

**前后端均已配置局域网访问�?*

- 后端: 已配�?`host=0.0.0.0` �?CORS
- 前端: 已配�?`vite --host`
- 局域网IP: `192.168.2.6`

详见: [局域网访问指南](项目文档/局域网访问指南.md)

### Phase 3 - 核心业务逻辑详情

#### 已实现的7个核心服�?
1. **StorageService (231�?** - 通用存储服务
   - 泛型设计，支持所有模型类�?   - 完整CRUD操作
   - Lambda表达式高级查�?   - 自动序列化（datetime, UUID, bytes, BaseModel�?
2. **SnomedService (302�?** - SNOMED CT编码服务
   - 64个医疗编码，7个分�?   - 生命体征自动评估算法
   - 危险等级自动判定
   - 原始姿态值转SNOMED编码

3. **TDPProcessor (337�?** - TDP协议处理�?   - Person/Object Matrix完整解析
   - IoT时序数据自动生成
   - Tag智能分类（Physiological, SleepState, Posture等）
   - 实时告警检测集�?
4. **AlertEngine (140�?** - 多级告警引擎
   - L1/L2/L3三级告警支持
   - 智能路由决策（基于接收范围和用户标签�?   - 多通道发送（WEB, APP, PHONE, EMAIL�?   - 告警历史记录

5. **CardManager (130�?** - 卡片管理�?   - ActiveBed/Location卡片自动生成
   - 层级地址生成（Location > Room > Bed�?   - 匿名代称集成
   - 告警路由配置

6. **CareQualityService (560�?** - 护理质量评估服务
   - 空间覆盖分析（基于实际IoT数据�?   - 团队质量报告生成（响应时间、告警率�?   - 100分制评分系统
   - 护理改进建议生成
   - 住户行为模式分析（每小时活动规律�?   - 基线对比分析

7. **BaselineService (700�?** - 健康基线服务
   - 个性化健康基线建立�?4天观察期�?   - 5类完整基线：
     - 生命体征基线（心率、呼吸率统计分析�?     - 活动基线（日常活动量、活跃时段识别）
     - 睡眠基线（睡眠周期分析、入�?起床时间、睡眠质量评分）
     - 姿态分布基线（姿态时间占比统计）
     - 位置活动基线（位置分布、移动性评分）
   - 行为模式识别（规律性评分、习惯识别）
   - 异常检测算法（生命体征、活动、睡眠异常）
   - 增量基线更新机制

**最后扫�?*: 2025-11-22 14:50 (最终版)  
**项目状�?*: �?95%完成 - 生产就绪 🚀  
**代码质量**: 100%类型注解�?错误0警告  
**Git提交**: 27�? 
**部署就绪**: �? 
**源参考对�?*: 95% (Schema 100% + 文档理解 88%) �?
### 🎊 2025-11-22 重大更新

**4小时持续开发，前端�?9%提升�?5% (+66%)�?*

**新增功能**:
- �?IoTData.tsx (360�? - IoT数据列表+图表可视�?- �?Cards.tsx (520�? - 卡片管理+创建表单
- �?AlertPolicies.tsx (330�? - 告警规则配置
- �?VitalSignsChart组件 - 心率/呼吸率趋势图
- �?CareQuality增强 - AI深度分析+6维雷达图
- �?Alerts增强 - 确认/解决功能
- �?Residents增强 - SNOMED标签显示
- �?Dashboard增强 - IoT数据概览
- �?示例数据补充 - 19/19表完整覆盖（~100条记录）

---

## 📁 项目文档

### 开发过程记�?- [项目启动与需求确认](项目文档/6-过程记录/2025-11-20_1333_项目启动与需求确�?md)
- [Phase 1-3 完成报告](项目文档/6-过程记录/) - 后端核心开�?- [后端开发完成报告](项目文档/6-过程记录/2025-11-20_1615_后端开发完成报�?md)
- [前端开发完成报告](项目文档/6-过程记录/2025-11-20_1827_前端开发完成报�?md)

### 技术文�?- [后端README](owlRD-prototype/backend/README.md)
- [前端README](owlRD-prototype/frontend/README.md)
- [前端开发总结](owlRD-prototype/frontend/DEVELOPMENT_SUMMARY.md)

### 聊天记录
- [完整对话记录](项目文档/7-聊天记录/2025-11-20_完整对话记录.md)
