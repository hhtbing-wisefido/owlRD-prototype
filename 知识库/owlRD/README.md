# WiseFido

## 项目概述

WiseFido 是一家专注于老人跌倒及紧急生理监测的 SaaS 服务商，为老年护理机构（Elder Care）和高级生活社区（Senior Living）提供 IoT 设备及云端服务。

### 核心服务

- **跌倒监测**：实时监测老人跌倒事件，提供多级报警机制
- **生理监测**：非接触式监测呼吸率、心率等生命体征
- **行为分析**：基于雷达轨迹分析日常活动模式，评估护理质量
- **智能预警**：基于 SNOMED CT 标准的健康风险评估与预警

### 目标客户

- 老年护理机构（Elder Care Facilities）
- 高级生活社区（Senior Living Communities）
- 居家养老服务机构



### 前端

- **管理看板**：Web 管理界面（支持 PC/移动端）
- **实时监控**：WebSocket 实时推送
- **数据可视化**：图表展示、趋势分析

### 标准与规范

- **医疗编码**：SNOMED CT（姿态、运动状态、健康状况）
- **数据交换**：HL7 FHIR（与电子病历系统对接）
- **协议标准**：TDPv2（Telemetry Data Protocol v2）

---

## 核心功能

### 1. 实时监测

- **跌倒检测**：基于雷达轨迹和高度变化，多级确认机制
- **生命体征**：非接触式监测呼吸率、心率
- **行为识别**：识别上床、离床、坐起等行为

### 2. 护理质量评估

- **空间智能分析**：基于护工-住户距离计算有效护理时长
- **团队级报告**：按护士组聚合指标，完全匿名
- **趋势分析**：7 天/30 天趋势跟踪

### 3. 健康基线建模

- **个人基线**：基于过去 7 天数据建立动态健康基线
- **异常检测**：识别睡眠异常、活动下降等风险信号
- **预警机制**：结合护理质量与住户状态，提供智能预警

### 4. 多级报警系统

- **L1（紧急）**：高风险、高置信，立即报警，所有终端接收
- **L2（高风险）**：高置信，网页显示，App/Watch 选择发送
- **L3（严重）**：需关注，网页显示，不响警号
- **L5（警告）**：低置信，本地确认 + Server 计算确认
- **L8（调试）**：内部记录，主要用于 AI 标识与训练

### 5. AI 训练与持续学习

> **注**：由于采用货架成熟产品，设备固件无法修改，无法直接获取原始 RAW 数据。所有 AI 训练在云端基于设备标准化输出进行。

- **数据采集**：
  - IoT 设备上传标准化数据（跌倒报警、心率、呼吸率、轨迹等）
  - 高频数据（心率、呼吸、轨迹）持续上传
  - 事件触发时上传设备判断结果和上下文信息
- **云端数据增强**：
  - **多源数据融合**：结合雷达轨迹、压力板事件、房间布局等多维度数据
  - **时序特征提取**：
    - 从轨迹数据提取：速度、加速度、位移、方向变化
    - 从生命体征提取：心率变异性、呼吸模式、异常持续时间
    - 从行为模式提取：活动频率、静止时长、姿态变化
  - **上下文关联**：
    - 房间布局信息（床位置、危险区域）
    - 历史行为基线（个人正常活动模式）
    - 时间上下文（睡眠时段、护理时段）
  - **特征工程**：构建高维特征向量，用于模型训练
- **标签生成**：
  - **人工反馈**：本地确认、Server 确认、取消等操作作为训练标签
  - **IoT 反馈**：设备本地判断结果作为初始标签
  - **事件序列追踪**：通过 `producer_id + sequence_number` 追踪完整事件链
  - **多源验证**：结合人工确认和设备判断，生成高质量训练标签
- **模型训练**：
  - 基于增强后的特征数据进行模型训练
  - 实时数据作为模型输入
  - 反馈数据作为监督学习标签
  - 持续优化跌倒检测、风险判断等模型
  - 提升住户风险判断准确率
- **数据流**：
  ```
  IoT 设备（标准化输出）
      ↓
  云端数据接收 → 数据增强（特征提取、多源融合）
      ↓
  实时风险判断 → 人工/IoT 反馈 → 标签生成
      ↓
  AI 模型训练 → 模型优化 → 部署更新
  ```
- **后续优化方向**：
  - 探索与设备厂商合作，获取原始数据接口（如 SDK 支持）
  - 研究基于有限数据的迁移学习方案
  - 建立多设备协同的增强学习框架

---

## 数据模型

### 人员矩阵 (Person Matrix)

跟踪和描述动态的人体目标，包含：
- 空间位置（pos_x, pos_y, pos_z）
- 速度信息（vel_x, vel_y, vel_z）
- 姿态状态（posture）
- 运动状态（motion_state）
- 健康状况（health_score）

### 物体矩阵 (Object Matrix)

描述静态或准静态的物体和环境特征：
- 床、轮椅、沙发等物体识别
- 危险区域标注
- 房间布局管理

---

## 开发状态

- ✅ IoT 设备选型（货架成熟产品）
- ✅ TDPv2 协议定义（标准化数据上传）
- ✅ SNOMED CT 编码集成
- 🚧 云端服务器开发（按 HIPAA 标准）
- 🚧 多租户数据隔离实现
- 🚧 权限管理系统
- 🚧 护理质量分析引擎
- 🚧 云端数据增强引擎（特征提取、多源融合）
- 🚧 AI 训练平台（基于增强数据的模型训练）

---

## 文档

### 核心设计文档

- [04_Data_Preparation_AI_Care.md](./docs/04_Data_Preparation_AI_Care.md) - AI 护理数据整理设计
- [06_FHIR_Simple_Conversion_Guide.md](./docs/06_FHIR_Simple_Conversion_Guide.md) - **FHIR/SNOMED CT 简化转换指南（IT人员专用）**
- [20_Card_Creation_Rules_Final.md](./docs/20_Card_Creation_Rules_Final.md) - **卡片创建规则（最终版）**
- [23_Card_Functions_Usage.md](./docs/23_Card_Functions_Usage.md) - **卡片自动生成函数使用说明**
- [24_Card_Permission_Design.md](./docs/24_Card_Permission_Design.md) - **卡片权限设计**

### 需求与规范文档

- [AI护理.md](./AI护理.md) - 智能护理质量评估系统功能清单
- [person_matrix_snomed_tags.md](./person_matrix_snomed_tags.md) - 人员矩阵 SNOMED CT 编码规范（包含高级编码如帕金森、中风、心梗等）
- [Radar本地报警机制-0916.md](./Radar本地报警机制-0916.md) - 雷达本地报警机制设计
- [TDPv2-0916.md](./TDPv2-0916.md) - TDPv2 协议定义（统一使用 vue_radar 生命体征阈值标准）

---

## 联系方式

如有技术问题或合作咨询，请联系项目团队。

---

*最后更新：2025年1月*

# owlRD

20251127
1.增加了呼吸RR/心率HR  sleepSatus  SNOME编码 

location-人/设备 绑定路径总结：

Location (位置/地址)
  ├── Room (房间)
  │     ├── Bed (床位)
  │     │     ├── Resident (住户) ← residents.bed_id
  │     │     └── Device (设备) ← devices.bound_bed_id
  │     └── Device (设备) ← devices.bound_room_id
  ├── Resident (住户) ← residents.location_id (HomeCare场景或Institutional的单人间or夫妻套房)
  └── Device (设备) ← devices.location_id (未绑床的设备)



告警路由机制：
ActiveBed 卡片路由（设备 → 床 → 住户 → 指定的护士）
Location 卡片路由（公共空间/多人房间）：使用警报通报组
Location 卡片路由（个人空间）：使用住户的护士或警报通报组

告警级别：
L1 (EMERGENCY)、L2 (ALERT)、L3 (CRITICAL)、L5 (WARNING)、DISABLE
最终级别 = max(云端级别, IoT级别)

用户告警配置：
alert_levels：用户愿意接收的告警级别集合 L1
alert_channels：用户愿意接收的通道（APP, EMAIL等）
alert_scope：接收范围（ALL, LOCATION-TAG, ASSIGNED_ONLY）

告警策略配置：
云端告警策略（cloud_alert_policies）：租户级别的全局配置
IoT设备本地报警配置（iot_monitor_alerts）：设备级别的兜底设置



## 6. 告警路由决策树

```
设备触发告警
  ↓
确定设备所属的卡片（ActiveBed 或 Location）
  ↓
如果是 ActiveBed 卡片
  ↓
  通过 resident_caregivers 查找该住户的负责护士
  ↓
  返回护士列表

如果是 Location 卡片
  ↓
  检查 locations.is_public_space 或 locations.is_multi_person_room
  ↓
  如果是 TRUE（公共空间/多人房间）
    ↓
    使用警报通报组路由（alert_user_ids + alert_tags）
    ↓
    如果 cards.routing_alert_user_ids 或 cards.routing_alert_tags 有值，则覆盖
    ↓
    返回用户列表
  ↓
  如果是 FALSE（个人空间）
    ↓
    方式1：通过 resident_caregivers 查找该房间所有住户的护士
    ↓
    方式2：如果配置了警报通报组，也包含警报通报组的用户
    ↓
    取并集，返回用户列表
  ↓
过滤用户（根据 alert_levels, alert_scope, alert_channels）
  ↓
应用通知规则（升级、抑制、静默）
  ↓
发送通知
```