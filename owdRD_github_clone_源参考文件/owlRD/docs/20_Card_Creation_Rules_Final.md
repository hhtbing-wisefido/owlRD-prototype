# 卡片创建规则（最终版）

## 场景说明

### Institutional 场景（机构场景）
- **适用场景**：养老院、护理院等机构
- **地址信息**：存储在 `locations` 表中（`building`, `floor`, `area_id`, `door_number`），不属于 PHI
- **住户关联**：住户通过床位（`bed`）关联到位置
- **Location 字段**：
  - `is_public_space`：标识公共空间（如大厅、走廊、电梯等），默认为 FALSE
  - `is_multi_person_room`：标识多人房间（设备属于公共，不能让个人所见），默认为 FALSE
  - `primary_resident_id`：单间或夫妻套房必须设置（第一位入住者），用于 Location 卡片名称显示
  - `alert_user_ids` / `alert_tags`：警报通报组，用于告警路由和权限控制
- **支持场景**：
  - **公共空间**：`is_public_space = TRUE`，`primary_resident_id` 可为 NULL
  - **多人房间**：`is_multi_person_room = TRUE`，`primary_resident_id` 可为 NULL
  - **单人房间/夫妻套房**：`is_multi_person_room = FALSE`，必须设置 `primary_resident_id`

### HomeCare 场景（家庭场景）
- **适用场景**：家庭护理场景
- **地址信息**：
  - 真实地址信息存储在 `resident_phi` 表中（加密，PHI）
  - `locations` 表仅存储逻辑位置信息（`location_name`, `location_tag`），不存储 PHI
- **住户关联**：住户直接通过 `residents.location_id` 关联到位置
- **Location 字段**：
  - `is_public_space`：始终为 FALSE（个人住所）
  - `is_multi_person_room`：始终为 FALSE（不考虑多人合租）
  - `primary_resident_id`：必须设置（绑定用户时，必须处理该值不为空），用于 Location 卡片名称显示
  - `alert_user_ids` / `alert_tags`：警报通报组，用于告警路由和权限控制
- **支持场景**：
  - **单人居住**：一个 location 对应一个住户
  - **夫妻同住**：一个 location 对应两个住户，使用相同的 `family_tag`，可以互相查看 Location 卡片
- **不支持场景**：多人合租（不同 `family_tag` 的多人合租）

## 规则 1：ActiveBed 判断条件 ✅ 已确认

### ActiveBed 判断条件（动态判断，不依赖 bed_type）

ActiveBed 必须同时满足：
1. ✅ `beds.resident_id IS NOT NULL`（有住户）
2. ✅ `beds.bound_device_count > 0`（有激活监护的监控设备）
3. ✅ `beds.is_active = TRUE`（床位激活，由 `bound_device_count > 0` 自动计算）
4. 同一Bed下，只能绑定1*radar+sleepad, 禁止绑2个同类呼吸/心率设备

**注意**：
- **不需要检查 `beds.bed_type = 'ActiveBed'`**
- 根据条件动态判断，避免数据不一致

---

## 规则 2：卡片创建场景 ✅ 已确认
//创建location卡片时，必须检查alter_tag

### 场景 A：门牌下只有 1 个 ActiveBed

**条件**：
- 门牌号下有且仅有 1 个 ActiveBed（`bound_device_count > 0` 且 `resident_id IS NOT NULL`）

**操作**：
1. **创建 1 个 ActiveBed 卡片**（ActiveBed 本身就有绑床的设备，所以必须创建）
2. 该卡片绑定该门牌内**所有 monitoring_enabled = TRUE 的设备**：
   - 该 ActiveBed 绑定的设备：`devices.bound_bed_id = bed_id` 且 `monitoring_enabled = TRUE`（至少1个）
   - 该 location 下未绑床的设备：`devices.location_id = location_id` 且 `devices.bound_bed_id IS NULL` 且 `monitoring_enabled = TRUE`

**示例**：
```
门牌号：201（Building: BuildA, Floor: 1F, DoorNumber: 201, location_name: E203）
ActiveBed：BedA（住户：Smith）
设备：
  - Radar01（绑 BedA，monitoring_enabled=TRUE）
  - SleepPad01（绑 BedA，monitoring_enabled=TRUE）
  - Radar02（绑门牌号，未绑床，monitoring_enabled=TRUE）

结果：
  1 个 ActiveBed 卡片（BedA）
    - 卡片名称：Smith
    - 卡片地址：A 院区主楼-E203-BedA
    - 绑定设备：Radar01（绑床）、SleepPad01（绑床）、Radar02（未绑床）
```

### 场景 B：门牌下有多个 ActiveBed（≥2）

**条件**：
- 门牌号下有 2 个或更多 ActiveBed

**操作**：
1. 为每个 ActiveBed 创建 **1 个 ActiveBed 卡片**（共 N 个）
   - 卡片名称：该床位的住户 LastName
   - 卡片地址：`location_tag + "-" + location_name + "-" + BedName`（如果 location_tag 不为 NULL）或 `location_name + "-" + BedName`（如果 location_tag 为 NULL）
   - 绑定设备：该床位的设备（`devices.bound_bed_id = bed_id` 且 `monitoring_enabled = TRUE`）
2. **创建 Location 卡片**（仅当该 location 下可监控且未绑床的设备数量 > 0 时创建）
   - 创建条件：`COUNT(devices WHERE devices.location_id = location_id AND devices.bound_bed_id IS NULL AND devices.monitoring_enabled = TRUE) > 0`
   - 卡片名称：按照 Location 卡片名称规则（规则3）计算，使用 `is_public_space`、`is_multi_person_room`、`primary_resident_id` 等字段
   - 卡片地址：`location_tag + "-" + location_name`（如果 location_tag 不为 NULL）或 `location_name`（如果 location_tag 为 NULL）
   - 绑定设备：该 location 下未绑床的设备（`devices.location_id = location_id` 且 `devices.bound_bed_id IS NULL` 且 `monitoring_enabled = TRUE`）



**示例**：
```
门牌号：201（Building: BuildA, Floor: 1F, DoorNumber: 201, location_name: E203）
Location 配置：
  - is_multi_person_room = TRUE（多人房间，设备属于公共）
  - is_public_space = FALSE
  - primary_resident_id = NULL（多人房间可为 NULL）
ActiveBed：
  - BedA（住户：Smith）
  - BedB（住户：Johnson）
设备：
  - Radar01（绑 BedA，monitoring_enabled=TRUE）
  - SleepPad01（绑 BedA，monitoring_enabled=TRUE）
  - Radar02（绑 BedB，monitoring_enabled=TRUE）
  - Radar03（绑门牌号，未绑床，monitoring_enabled=TRUE）
  - VibrationSensor01（绑门牌号，未绑床，monitoring_enabled=TRUE）

结果：
  2 个 ActiveBed 卡片：
    - BedA 卡片：
      - 卡片名称：Smith
      - 卡片地址：A 院区主楼-E203-BedA
      - 绑定设备：Radar01（绑床）、SleepPad01（绑床）
    - BedB 卡片：
      - 卡片名称：Johnson
      - 卡片地址：A 院区主楼-E203-BedB
      - 绑定设备：Radar02（绑床）
  1 个 Location 卡片：
    - 卡片名称：E203（is_multi_person_room = TRUE，显示 location_name）
    - 卡片地址：A 院区主楼-E203（location_tag + location_name）
    - 绑定设备：Radar03（未绑床）、VibrationSensor01（未绑床）
```

### 场景 C：门牌下无 ActiveBed

**条件**：
- 门牌号下没有 ActiveBed（只有 NABed 或没有床）

**操作**：
- **创建 Location 卡片**（仅当该 location 下可监控且未绑床的设备数量 > 0 时创建）
  - 创建条件：`COUNT(devices WHERE devices.location_id = location_id AND devices.bound_bed_id IS NULL AND devices.monitoring_enabled = TRUE) > 0`
  - 卡片名称：按照 Location 卡片名称规则（规则3）计算，使用 `is_public_space`、`is_multi_person_room`、`primary_resident_id` 等字段
  - 卡片地址：`location_tag + "-" + location_name`（如果 location_tag 不为 NULL）或 `location_name`（如果 location_tag 为 NULL）
  - 绑定设备：该 location 下未绑床的设备（`devices.location_id = location_id` 且 `devices.bound_bed_id IS NULL` 且 `monitoring_enabled = TRUE`）

**示例**：
```
门牌号：201（Building: BuildA, Floor: 1F, DoorNumber: 201, location_name: E203）
Location 配置：
  - is_public_space = TRUE（公共空间，如大厅）
  - is_multi_person_room = FALSE
  - primary_resident_id = NULL（公共空间可为 NULL）
ActiveBed：无
设备：
  - Radar01（绑门牌号，未绑床，monitoring_enabled=TRUE）
  - VibrationSensor01（绑门牌号，未绑床，monitoring_enabled=TRUE）

结果：
  1 个 Location 卡片：
    - 卡片名称：E203（is_public_space = TRUE，显示 location_name）
    - 卡片地址：A 院区主楼-E203（location_tag + location_name）
    - 绑定设备：Radar01（未绑床）、VibrationSensor01（未绑床）
```

---

## 规则 3：卡片名称计算 ✅ 已确认

### ActiveBed 卡片名称

```
卡片名称 = 该床位上绑定的住户的 LastName
```

**说明**：
- 使用 `residents.last_name`（与 `anonymous_name` 相同）
- 不显示 FirstName（即使有 FirstName，也只显示 LastName）

**示例**：
- 住户 LastName = "Smith" → 卡片名称：`Smith`
- 住户 LastName = "钟表匠" → 卡片名称：`钟表匠`

### Location 卡片名称

```
如果 is_public_space = TRUE：
  卡片名称 = location_name（Institutional 公共空间，如 "大厅"、"走廊"）

如果 is_multi_person_room = TRUE：
  卡片名称 = location_name（Institutional 多人房间，设备属于公共，如 "E203"）

如果 location_type = 'HomeCare' 且 primary_resident_id IS NOT NULL：
  卡片名称 = primary_resident_id 对应的住户的 LastName（HomeCare 场景）

如果 is_multi_person_room = FALSE（Institutional 单人房间/夫妻套房）：
  卡片名称 = primary_resident_id 对应的住户的 LastName（第一位入住者）
  注意：必须设置 primary_resident_id（绑定用户时，必须处理该值不为空）
```

**说明**：
- **优先级1**：`is_public_space = TRUE` → 显示 `location_name`（Institutional 公共空间，如大厅、走廊、电梯等）
- **优先级2**：`is_multi_person_room = TRUE` → 显示 `location_name`（Institutional 多人房间，设备属于公共，不能让个人所见）
- **优先级3**：`location_type = 'HomeCare'` 且 `primary_resident_id IS NOT NULL` → 显示 `primary_resident_id` 对应的住户的 LastName（HomeCare 场景，直接使用主要住户的匿名名称）
- **优先级4**：`is_multi_person_room = FALSE`（Institutional 单人房间/夫妻套房）：
  - 必须设置 `primary_resident_id`（绑定用户时，必须处理该值不为空）
  - 显示 `primary_resident_id` 对应的住户的 LastName（第一位入住者）
 

**场景说明**：
- **Institutional 场景**：
  - 公共空间（`is_public_space = TRUE`）：显示 `location_name`（如 "大厅"），`primary_resident_id` 可为 NULL
  - 多人房间（`is_multi_person_room = TRUE`）：显示 `location_name`（如 "E203"），`primary_resident_id` 可为 NULL
  - 单人房间/夫妻套房（`is_public_space = FALSE` 且 `is_multi_person_room = FALSE`）：
    - **必须设置 `primary_resident_id`**（绑定用户时，必须处理该值不为空）
    - 显示第一位入住者的 LastName（如 "Smith"）
- **HomeCare 场景**：
  - **必须设置 `primary_resident_id`**（绑定用户时，必须处理该值不为空）
  - 直接使用 `primary_resident_id` 对应的住户的 LastName（如 "Smith"）
  - 无论单人居住还是夫妻同住，都使用主要住户的匿名名称

**示例**：
- Institutional 公共空间（`is_public_space = TRUE`）→ 卡片名称：`大厅`
- Institutional 多人房间（`is_multi_person_room = TRUE`）→ 卡片名称：`E203`
- Institutional 单人房间（`primary_resident_id` 指向 Smith）→ 卡片名称：`Smith`
- Institutional 夫妻套房（`primary_resident_id` 指向 Smith）→ 卡片名称：`Smith`
- HomeCare 场景（`primary_resident_id` 指向 Smith）→ 卡片名称：`Smith`

---

## 规则 4：卡片地址计算 ✅ 已确认

### ActiveBed 卡片地址

**规则**：
```
如果 location_tag 不为 NULL：
  卡片地址 = location_tag + "-" + location_name + "-" + BedName
  示例：A 院区主楼-E203-BedA

如果 location_tag 为 NULL：
  卡片地址 = location_name + "-" + BedName
  示例：E203-BedA
```

**说明**：
- 优先使用 `location_tag + location_name + BedName` 组合
- 如果 `location_tag` 为空，则只使用 `location_name + BedName`
- 不使用 Building、Floor、DoorNumber、RoomName
- 向后兼容：如果 location_tag 为 NULL，仍使用 location_name

**示例**：
- location_tag = "A 院区主楼", location_name = "E203", bed_name = "BedA" → 卡片地址：`A 院区主楼-E203-BedA`
- location_tag = NULL, location_name = "E203", bed_name = "BedA" → 卡片地址：`E203-BedA`
- location_tag = "Spring 区域组", location_name = "201", bed_name = "BedB" → 卡片地址：`Spring 区域组-201-BedB`

### Location 卡片地址

**规则**：
```
如果 location_tag 不为 NULL：
  卡片地址 = location_tag + "-" + location_name
  示例：A 院区主楼-E203

如果 location_tag 为 NULL：
  卡片地址 = location_name
  示例：E203
```

**说明**：
- 优先使用 `location_tag + location_name` 组合，提供更多上下文信息
- 如果 `location_tag` 为空，则只使用 `location_name`
- 不使用 Building、Floor、DoorNumber

**示例**：
- location_tag = "A 院区主楼", location_name = "E203" → 卡片地址：`A 院区主楼-E203`
- location_tag = NULL, location_name = "E203" → 卡片地址：`E203`
- location_tag = "Spring 区域组", location_name = "201" → 卡片地址：`Spring 区域组-201`



## 规则 5：设备绑定规则 ✅ 已确认

### 5.1 设备绑定优先级

**规则**：
- **按最小地址优先原则**：床 > 房间 > 门牌号
- 如果设备同时绑定床和门牌号，优先归属到床

**说明**：
- 床属于最小地址单位
- 设备绑定关系由 `devices` 表的 `bound_bed_id`、`bound_room_id`、`location_id` 字段确定

### 5.2 ActiveBed 卡片设备绑定

**规则**：
- 绑床的设备：`devices.bound_bed_id = bed_id` 且 `monitoring_enabled = TRUE`（`binding_type = 'direct'`）
- 未绑床的设备：`devices.bound_bed_id IS NULL` 且 `monitoring_enabled = TRUE`（`binding_type = 'indirect'`，仅当门牌下只有 1 个 ActiveBed 时）

**说明**：
- "未绑床的设备"：指 `bound_bed_id IS NULL`（未绑定任何床）
- 必须满足 `monitoring_enabled = TRUE`（监护已激活）

### 5.3 Location 卡片设备绑定

**规则**：
- 绑定设备：`devices.bound_bed_id IS NULL` 且 `monitoring_enabled = TRUE`（`binding_type = 'indirect'`）

**说明**：
- "未与床绑定"：指 `bound_bed_id IS NULL`（未绑定任何床）
- 必须满足 `monitoring_enabled = TRUE`（监护已激活）

---

## 规则 6：设备类型过滤 ✅ 已确认

**规则**：
- 不需要特别说明设备类型过滤规则
- 设备绑定关系已在 `devices` 表中通过 `bound_bed_id`、`bound_room_id`、`location_id` 字段明确
- 床属于最小地址单位，设备绑定到床即属于该床位的卡片

---

## 规则 7：卡片更新触发条件 ✅ 已确认

**规则**：
- **实时更新**：当关系变化时立即重新计算卡片
- 卡片变化很少，主要在以下场景：
  - 住户入住/出院（床位绑定关系变化）
  - 设备安装/移除（设备绑定关系变化）

**触发场景**：
1. 床位绑定关系变化：
   - 住户绑定/解绑床位（`beds.resident_id` 变化）
   - 设备绑定/解绑床位（`devices.bound_bed_id` 变化）
   - 床位激活状态变化（`beds.is_active` 变化）
2. 门牌号下住户变化：
   - 住户绑定/解绑门牌号（`residents.location_id` 变化）
   - 住户状态变化（`residents.status` 变化）
3. 设备绑定关系变化：
   - 设备绑定/解绑门牌号/房间/床位
   - 设备监护状态变化（`devices.monitoring_enabled` 变化）
4. 地址信息变化：
   - 门牌号/房间/床位名称变化（`locations.location_name`、`rooms.room_name`、`beds.bed_name` 变化）
   - 位置标签变化（`locations.location_tag` 变化）

**实现建议**：
- 使用数据库触发器或应用层事件监听
- 当上述字段变化时，立即触发卡片重新计算

---

## 规则 8：卡片去重规则 ✅ 已确认

**规则**：
- **删除旧卡片，创建新卡片**
- **不保留历史记录**：直接删除旧卡片，不标记为 inactive

**场景示例**：
- 门牌下从多个 ActiveBed 变为 1 个 ActiveBed：
  - 删除 Location 卡片
  - 创建 ActiveBed 卡片
- 门牌下从 1 个 ActiveBed 变为多个 ActiveBed：
  - 删除 ActiveBed 卡片
  - 创建 N 个 ActiveBed 卡片 + 1 个 Location 卡片（如果有未绑床的设备）

**实现建议**：
- 使用事务确保原子性：先删除旧卡片，再创建新卡片
- 使用 `DELETE` 语句直接删除，不使用软删除（`is_active = FALSE`）

---

## 规则总结（完整版）

### 关键点

1. **ActiveBed 判断**：动态判断，不依赖 `bed_type`
2. **卡片创建**：
   - 场景 A：只要有 ActiveBed 就创建，绑定所有 monitoring_enabled 设备
   - 场景 B：N 个 ActiveBed 卡片 + 0 或 1 个 Location 卡片（仅当有未绑床的 monitoring_enabled 设备时创建 Location 卡片）
   - 场景 C：仅当有未绑床的 monitoring_enabled 设备时创建 Location 卡片
3. **卡片名称**：
   - ActiveBed：使用 `residents.last_name`
   - Location：按照优先级规则计算（规则3）：
     - 优先级1：`is_public_space = TRUE` → `location_name`
     - 优先级2：`is_multi_person_room = TRUE` → `location_name`
     - 优先级3：`location_type = 'HomeCare'` 且 `primary_resident_id IS NOT NULL` → `primary_resident_id` 对应的住户 LastName
     - 优先级4：`is_multi_person_room = FALSE` → `primary_resident_id` 对应的住户 LastName（必须设置）
4. **卡片地址**：
   - ActiveBed：`location_tag + "-" + location_name + "-" + BedName`（如果 location_tag 不为 NULL）或 `location_name + "-" + BedName`（如果 location_tag 为 NULL）
   - Location：`location_tag + "-" + location_name`（如果 location_tag 不为 NULL）或 `location_name`（如果 location_tag 为 NULL）
5. **设备绑定**：按最小地址优先原则（床 > 房间 > 门牌号）
6. **卡片更新**：实时更新，关系变化时立即重新计算
7. **卡片去重**：删除旧卡片，创建新卡片，不保留历史记录
