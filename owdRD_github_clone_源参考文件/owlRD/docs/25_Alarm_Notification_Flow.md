# 警报通知流程和分布

## 概述

本文档详细说明 owlRD 系统中警报通知的完整流程，包括告警路由机制、告警级别、用户配置和通知分发规则。

---

## 1. 告警路由机制

告警路由根据设备位置、住户分配和位置特征（公共空间/多人房间/个人空间）来决定告警接收者。

### 1.1 路由规则

#### 规则 1：ActiveBed 卡片路由

**路径**：`设备 → 床 → 住户 → 指定的护士`

**说明**：
- ActiveBed 卡片关联到具体的床位和住户
- 告警通过 `resident_caregivers` 表查找该住户的负责护士
- 最多支持 5 个护理人员同时负责一个住户（`caregiver_id1` ~ `caregiver_id5`）

**查询逻辑**：
```sql
-- 获取 ActiveBed 卡片的告警接收者
SELECT DISTINCT u.user_id, u.username, u.alert_levels, u.alert_channels, u.alert_scope
FROM cards c
JOIN beds b ON c.bed_id = b.bed_id
JOIN resident_caregivers rc ON b.resident_id = rc.resident_id
JOIN users u ON (
    u.user_id = rc.caregiver_id1 
    OR u.user_id = rc.caregiver_id2 
    OR u.user_id = rc.caregiver_id3 
    OR u.user_id = rc.caregiver_id4 
    OR u.user_id = rc.caregiver_id5
)
WHERE c.card_id = ?
  AND c.card_type = 'ActiveBed'
  AND u.status = 'active'
  AND u.user_id IS NOT NULL
```

**注意**：
- `resident_caregivers` 表中每个记录包含 5 个护理人员ID（`caregiver_id1` ~ `caregiver_id5`），都是必填字段
- 一个住户可以有多个 `resident_caregivers` 记录，每个记录包含 5 个护理人员
- 查询时需要检查 `user_id IS NOT NULL`，因为某些位置可能没有分配护理人员

#### 规则 2：Location 卡片路由（公共空间/多人房间）

**路径**：`设备 → location → 警报通报组（alert_user_ids + alert_tags）`

**条件**：
- `locations.is_public_space = TRUE`（公共空间，如大厅、走廊、电梯等）
- 或 `locations.is_multi_person_room = TRUE`（多人房间，设备属于公共）

**说明**：
- 使用 `locations.alert_user_ids` 和 `locations.alert_tags` 进行路由
- 如果 `cards.routing_alert_user_ids` 或 `cards.routing_alert_tags` 有值，则覆盖 `locations` 表的配置
- 查询规则：
  1. 如果指定了 `alert_user_ids`，直接包含这些用户
  2. 如果指定了 `alert_tags`，匹配 `users.tags` 中包含这些标签的用户
  3. 两者可以同时使用，取并集

**查询逻辑**：
```sql
-- 获取 Location 卡片（公共空间/多人房间）的告警接收者
SELECT DISTINCT u.user_id, u.username, u.alert_levels, u.alert_channels, u.alert_scope
FROM cards c
JOIN locations l ON c.location_id = l.location_id
JOIN users u ON (
    -- 直接指定的用户ID
    (COALESCE(c.routing_alert_user_ids, l.alert_user_ids) IS NOT NULL 
     AND u.user_id = ANY(COALESCE(c.routing_alert_user_ids, l.alert_user_ids)))
    OR
    -- 标签匹配的用户
    (COALESCE(c.routing_alert_tags, l.alert_tags) IS NOT NULL 
     AND u.tags ?| COALESCE(c.routing_alert_tags, l.alert_tags))
)
WHERE c.card_id = ?
  AND c.card_type = 'Location'
  AND (l.is_public_space = TRUE OR l.is_multi_person_room = TRUE)
  AND u.status = 'active'
```

#### 规则 3：Location 卡片路由（个人空间，单人/伴侣房）

**路径**：`设备 → location → 该房间所有住户的护士（通过 resident_caregivers 表）或 警报通报组`

**条件**：
- `locations.is_public_space = FALSE` 且 `locations.is_multi_person_room = FALSE`
- 单人房间或夫妻套房

**说明**：
- 优先使用该房间所有住户的护士进行路由（通过 `resident_caregivers` 表查找）
- 如果配置了警报通报组（`locations.alert_user_ids` 或 `locations.alert_tags`），也可以使用警报通报组
- 如果 `cards.routing_alert_user_ids` 或 `cards.routing_alert_tags` 有值，则覆盖 `locations` 表的配置

**查询逻辑**：
```sql
-- 获取 Location 卡片（个人空间）的告警接收者
-- 方式1：通过住户的护士
SELECT DISTINCT u.user_id, u.username, u.alert_levels, u.alert_channels, u.alert_scope
FROM cards c
JOIN locations l ON c.location_id = l.location_id
JOIN residents r ON r.location_id = l.location_id AND r.status = 'active'
JOIN resident_caregivers rc ON r.resident_id = rc.resident_id
JOIN users u ON (
    u.user_id = rc.caregiver_id1 
    OR u.user_id = rc.caregiver_id2 
    OR u.user_id = rc.caregiver_id3 
    OR u.user_id = rc.caregiver_id4 
    OR u.user_id = rc.caregiver_id5
)
WHERE c.card_id = ?
  AND c.card_type = 'Location'
  AND l.is_public_space = FALSE
  AND l.is_multi_person_room = FALSE
  AND u.status = 'active'
  AND u.user_id IS NOT NULL

UNION

-- 方式2：通过警报通报组（如果配置了）
SELECT DISTINCT u.user_id, u.username, u.alert_levels, u.alert_channels, u.alert_scope
FROM cards c
JOIN locations l ON c.location_id = l.location_id
JOIN users u ON (
    (COALESCE(c.routing_alert_user_ids, l.alert_user_ids) IS NOT NULL 
     AND u.user_id = ANY(COALESCE(c.routing_alert_user_ids, l.alert_user_ids)))
    OR
    (COALESCE(c.routing_alert_tags, l.alert_tags) IS NOT NULL 
     AND u.tags ?| COALESCE(c.routing_alert_tags, l.alert_tags))
)
WHERE c.card_id = ?
  AND c.card_type = 'Location'
  AND l.is_public_space = FALSE
  AND l.is_multi_person_room = FALSE
  AND u.status = 'active'
```

---

## 2. 告警级别（DangerLevel）

### 2.1 级别定义

| 级别 | 名称 | 说明 | 使用场景 |
|------|------|------|----------|
| **L1** | EMERGENCY | 紧急，高风险，高置信 | 无论何处发出，立即报警，所有终端均收到；警号立即响起，L1红色，本地二次确认，必须手工取消 |
| **L2** | ALERT | 警报，高危事件 | 网页显示，app/watch选择发送；警号立即响起，L2橙色 |
| **L3** | CRITICAL | 严重 | 网页显示，app/watch选择发送；不响警号 |
| **L5** | WARNING | 高风险，低置信 | 触发警示灯（30秒+120秒）计时器报警，确认方式=本地人工确认或Server计算确认危险 |
| **DISABLE** | - | 关闭该类报警 | 不发送告警 |

**注意**：当前仅建议使用 `['DISABLE','L1','L2']`

### 2.2 告警级别确定规则

**最终报警级别 = max(云端级别, IoT级别)**

1. **云端级别**：从 `cloud_alert_policies` 表获取（租户级别的全局配置）
2. **IoT级别**：从 `iot_monitor_alerts` 表获取（设备本地报警配置）
3. **取最大值**：如果云端级别为 L2，IoT级别为 L1，则最终级别为 L1（更紧急）

---

## 3. 用户告警配置

### 3.1 用户告警接收配置（`users` 表）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `alert_levels` | VARCHAR[] | 用户愿意接收的告警级别集合 | `["L1","L2","L3"]`，为空表示使用系统默认 |
| `alert_channels` | VARCHAR[] | 用户愿意接收的通道 | `["APP","EMAIL"]`，短信等需在应用层结合策略控制 |
| `alert_scope` | VARCHAR(20) | 接收范围 | `'ALL'`（全机构）、`'LOCATION-TAG'`（按地点标签）、`'ASSIGNED_ONLY'`（仅自己负责的住户） |

### 3.2 告警范围（`alert_scope`）

#### ALL（全机构）
- 用户可以看到该租户下的所有卡片
- 通常用于 Director、NurseManager、Admin 等管理层角色

#### LOCATION-TAG（按地点标签）
- 用户只能看到 `location_tag` 在用户的 `tags` 中的卡片
- 例如：`location_tag = "A 院区主楼"`，用户的 `tags` 中包含 `"A 院区主楼"`，则可以看见该 location 的卡片

#### ASSIGNED_ONLY（仅自己负责的住户）
- 用户只能看到自己负责的住户相关的卡片
- ActiveBed 卡片：住户分配给该用户（通过 `resident_caregivers` 表）
- Location 卡片：有住户分配给该用户

---

## 4. 告警策略配置

### 4.1 云端告警策略（`cloud_alert_policies`）

**用途**：租户级别的全局配置，每个报警类型是一个字段，字段值存储 DangerLevel

**配置说明**：
1. 每个租户（`tenant_id`）只有一条配置记录（PRIMARY KEY `tenant_id`）
2. 每个报警类型对应一个字段，字段值存储 DangerLevel（`'DISABLE'`, `'L1'`, `'L2'`）
3. 如果字段值为 NULL，表示使用系统默认级别
4. 创建新租户时，需要初始化所有字段的默认值（调用 `initialize_tenant_alert_policies()` 函数）

**报警类型示例**：
- Common：`OfflineAlarm`, `LowBattery`, `DeviceFailure`
- SleepMonitor：`SleepPad_LeftBed`, `SleepPad_ApneaHypopnea`, `SleepPad_AbnormalHeartRate`, `SleepPad_AbnormalRespiratoryRate` 等
- Radar：`Radar_AbnormalHeartRate`, `Radar_AbnormalRespiratoryRate`, `SuspectedFall`, `Fall`, `VitalsWeak` 等

**阈值配置**（`conditions` JSONB）：
- 用于生理指标类报警（如心率、呼吸频率），定义什么数值范围触发什么级别
- 如果为 NULL，则使用系统默认阈值（vue_radar 项目标准）

**通知规则配置**（`notification_rules` JSONB）：
- 包含通知通道、发送方式、升级规则、抑制规则、静默规则等完整配置
- 如果为 NULL，表示使用用户/系统默认配置

### 4.2 IoT设备本地报警配置（`iot_monitor_alerts`）

**用途**：IoT设备本地报警配置，更多是"兜底设置"，条件可能比云端更严格

**配置说明**：
- 每个设备（`device_id`）可以配置多种报警类型
- 每个报警类型对应一个 `iot_level`（`'L1'` / `'L2'` / `'DISABLE'`）
- 前端 UI 说明：当前端打勾启用该报警类型时，默认 `iot_level = 'L1'`
- 厂家原始阈值配置存储在 `vendor_config` JSONB 字段中

---

## 5. 告警通知流程

### 5.1 完整流程

```
1. 设备触发告警
   ↓
2. 确定告警类型和级别
   - 查询 cloud_alert_policies（云端级别）
   - 查询 iot_monitor_alerts（IoT级别）
   - 最终级别 = max(云端级别, IoT级别)
   ↓
3. 确定告警路由（根据卡片类型和位置特征）
   - ActiveBed 卡片 → 通过 resident_caregivers 查找护士
   - Location 卡片（公共空间/多人房间）→ 通过 alert_user_ids/alert_tags 查找用户
   - Location 卡片（个人空间）→ 通过 resident_caregivers 或 alert_user_ids/alert_tags 查找用户
   ↓
4. 过滤用户（根据用户配置）
   - 检查 alert_levels：用户是否愿意接收该级别的告警
   - 检查 alert_scope：用户是否有权限看到该卡片
   - 检查 alert_channels：用户愿意接收的通道
   ↓
5. 应用通知规则（从 cloud_alert_policies.notification_rules）
   - 检查升级规则（escalation）
   - 检查抑制规则（suppression）
   - 检查静默规则（silence）
   ↓
6. 发送通知
   - 根据 alert_channels 发送到不同通道（WEB, APP, PHONE, EMAIL等）
   - 根据 immediate 标志决定是否立即发送
   - 根据 repeat_interval_sec 决定重复发送间隔
```

### 5.2 通知通道

- **WEB**：网页端显示
- **APP**：移动应用推送
- **PHONE**：电话通知
- **EMAIL**：邮件通知
- **SMS**：短信通知（需在应用层结合策略控制）

### 5.3 通知规则示例

```json
{
  "notification_rules": {
    "L1": {
      "channels": ["WEB", "APP", "PHONE", "EMAIL"],
      "immediate": true,
      "repeat_interval_sec": 300
    },
    "L2": {
      "channels": ["WEB", "APP"],
      "immediate": false,
      "repeat_interval_sec": 600
    }
  },
  "escalation": {
    "enabled": true,
    "escalate_after_sec": 300,
    "escalate_to_level": "L1"
  },
  "suppression": {
    "enabled": true,
    "suppress_duplicate_sec": 60,
    "max_alerts_per_hour": 10
  },
  "silence": {
    "enabled": false,
    "silence_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6],
    "silence_days": ["Saturday", "Sunday"]
  }
}
```

---

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

---

## 7. 配置示例

### 7.1 机构场景配置示例

**场景**：养老院，A 院区主楼，E203 房间（单人房间），住户 Smith，负责护士 Alice 和 Bob

**配置**：
```sql
-- locations 表
location_id = 'xxx'
location_tag = 'A 院区主楼'
location_name = 'E203'
is_public_space = FALSE
is_multi_person_room = FALSE
alert_user_ids = NULL  -- 个人空间，不使用警报通报组
alert_tags = NULL

-- resident_caregivers 表
resident_id = 'smith-resident-id'
caregiver_id1 = 'alice-user-id'
caregiver_id2 = 'bob-user-id'

-- users 表（Alice）
user_id = 'alice-user-id'
alert_levels = ['L1', 'L2']
alert_channels = ['APP', 'EMAIL']
alert_scope = 'ASSIGNED_ONLY'

-- users 表（Bob）
user_id = 'bob-user-id'
alert_levels = ['L1', 'L2']
alert_channels = ['APP']
alert_scope = 'ASSIGNED_ONLY'
```

**告警路由结果**：
- 设备触发告警 → ActiveBed 卡片 → 查找 Smith 的负责护士 → Alice 和 Bob
- 如果告警级别为 L1 或 L2，Alice 和 Bob 都会收到通知
- Alice 通过 APP 和 EMAIL 接收，Bob 通过 APP 接收

### 7.2 公共空间配置示例

**场景**：养老院，A 院区主楼，大厅（公共空间），配置了夜班护士组

**配置**：
```sql
-- locations 表
location_id = 'xxx'
location_tag = 'A 院区主楼'
location_name = '大厅'
is_public_space = TRUE
is_multi_person_room = FALSE
alert_user_ids = NULL
alert_tags = ['NightShift']  -- 夜班护士组标签

-- users 表（夜班护士）
user_id = 'night-nurse-1'
tags = ['NightShift', 'Group.A']
alert_levels = ['L1', 'L2']
alert_channels = ['APP']
alert_scope = 'LOCATION-TAG'
```

**告警路由结果**：
- 设备触发告警 → Location 卡片（公共空间）→ 使用警报通报组路由
- 匹配 `tags` 中包含 `'NightShift'` 的用户 → 所有夜班护士
- 如果告警级别为 L1 或 L2，所有夜班护士都会收到通知

---

## 8. 总结

### 8.1 关键点

1. **路由机制**：根据卡片类型（ActiveBed/Location）和位置特征（公共空间/多人房间/个人空间）决定告警接收者
2. **告警级别**：最终级别 = max(云端级别, IoT级别)，确保最紧急的告警被优先处理
3. **用户过滤**：根据用户的 `alert_levels`、`alert_scope`、`alert_channels` 过滤接收者
4. **通知规则**：支持升级、抑制、静默等高级规则，避免告警疲劳

### 8.2 设计原则

1. **灵活性**：支持多种路由方式（护士分配、警报通报组、标签匹配）
2. **可扩展性**：支持自定义报警类型和通知规则
3. **可配置性**：租户级别、设备级别、用户级别多层级配置
4. **安全性**：通过 `alert_scope` 控制用户可见范围，符合权限管理要求

