# 卡片自动生成函数使用说明

## 概述

本文档说明如何使用卡片自动生成函数和触发器，实现卡片的自动创建和维护。

## 核心函数

### 1. `regenerate_cards_for_location(p_location_id, p_actor_id, p_actor_type)`

为指定 location 重新生成所有卡片。

**参数**：
- `p_location_id` (UUID)：location ID
- `p_actor_id` (UUID, 可选)：操作者 ID，默认为系统
- `p_actor_type` (VARCHAR, 可选)：操作者类型，默认为 'System'

**功能**：
- 删除该 location 下的所有旧卡片
- 根据卡片创建规则重新生成卡片：
  - 场景 A：门牌下只有 1 个 ActiveBed → 创建 1 个 ActiveBed 卡片
  - 场景 B：门牌下有多个 ActiveBed → 创建 N 个 ActiveBed 卡片 + 0 或 1 个 Location 卡片
  - 场景 C：门牌下无 ActiveBed → 创建 0 或 1 个 Location 卡片

**示例**：
```sql
-- 为指定 location 重新生成卡片
SELECT regenerate_cards_for_location(
    '123e4567-e89b-12d3-a456-426614174000'::UUID,
    '987fcdeb-51a2-43d7-8f9e-123456789abc'::UUID,
    'Staff'
);
```

### 2. `regenerate_all_cards(p_actor_id, p_actor_type)`

为所有 location 重新生成所有卡片。

**参数**：
- `p_actor_id` (UUID, 可选)：操作者 ID，默认为系统
- `p_actor_type` (VARCHAR, 可选)：操作者类型，默认为 'System'

**功能**：
- 遍历所有活跃的 location
- 为每个 location 调用 `regenerate_cards_for_location`

**示例**：
```sql
-- 为所有 location 重新生成卡片（初始化或批量更新）
SELECT regenerate_all_cards();
```

### 3. `is_activebed(p_bed_id)`

判断指定床位是否为 ActiveBed。

**参数**：
- `p_bed_id` (UUID)：床位 ID

**返回值**：
- `BOOLEAN`：是否为 ActiveBed

**判断条件**：
- `resident_id IS NOT NULL`（有住户）
- `bound_device_count > 0`（有激活监护的监控设备）

**示例**：
```sql
-- 判断床位是否为 ActiveBed
SELECT is_activebed('123e4567-e89b-12d3-a456-426614174000'::UUID);
```

### 4. `calculate_activebed_address(p_location_tag, p_location_name, p_bed_name)`

计算 ActiveBed 卡片地址。

**参数**：
- `p_location_tag` (VARCHAR)：位置标签
- `p_location_name` (VARCHAR)：位置名称
- `p_bed_name` (VARCHAR)：床位名称

**返回值**：
- `VARCHAR`：卡片地址

**规则**：
- 如果 `location_tag` 不为 NULL：`location_tag + "-" + location_name + "-" + BedName`
- 如果 `location_tag` 为 NULL：`location_name + "-" + BedName`

**示例**：
```sql
-- 计算 ActiveBed 卡片地址
SELECT calculate_activebed_address('A 院区主楼', 'E203', 'BedA');
-- 返回：'A 院区主楼-E203-BedA'
```

### 5. `calculate_location_address(p_location_tag, p_location_name)`

计算 Location 卡片地址。

**参数**：
- `p_location_tag` (VARCHAR)：位置标签
- `p_location_name` (VARCHAR)：位置名称

**返回值**：
- `VARCHAR`：卡片地址

**规则**：
- 如果 `location_tag` 不为 NULL：`location_tag + "-" + location_name`
- 如果 `location_tag` 为 NULL：`location_name`

**示例**：
```sql
-- 计算 Location 卡片地址
SELECT calculate_location_address('A 院区主楼', 'E203');
-- 返回：'A 院区主楼-E203'
```

---

## 自动触发器

系统已配置以下触发器，当相关表变化时自动重新生成卡片：

### 1. `trigger_regenerate_cards_on_bed_change`

**触发表**：`beds`

**触发时机**：`INSERT`、`UPDATE`、`DELETE`

**功能**：当床位信息变化时（如住户绑定/解绑、床位激活状态变化），自动重新生成该 location 的卡片

### 2. `trigger_regenerate_cards_on_resident_change`

**触发表**：`residents`

**触发时机**：`INSERT`、`UPDATE`、`DELETE`

**功能**：当住户信息变化时（如住户绑定/解绑 location、住户状态变化），自动重新生成该 location 的卡片

### 3. `trigger_regenerate_cards_on_device_change`

**触发表**：`devices`

**触发时机**：`INSERT`、`UPDATE`、`DELETE`

**功能**：当设备信息变化时（如设备绑定/解绑床位/location、设备监护状态变化），自动重新生成该 location 的卡片

### 4. `trigger_regenerate_cards_on_location_change`

**触发表**：`locations`

**触发时机**：`UPDATE`

**触发条件**：`location_name` 或 `location_tag` 变化

**功能**：当 location 名称或标签变化时，自动重新生成该 location 的卡片

---

## 使用场景

### 场景 1：初始化卡片（系统部署后）

```sql
-- 为所有 location 生成卡片
SELECT regenerate_all_cards();
```

### 场景 2：手动触发卡片更新（应用层调用）

```sql
-- 当住户入住时，手动触发卡片更新
SELECT regenerate_cards_for_location(
    p_location_id := '123e4567-e89b-12d3-a456-426614174000'::UUID,
    p_actor_id := current_user_id(),
    p_actor_type := 'Staff'
);
```

### 场景 3：批量更新（数据迁移后）

```sql
-- 数据迁移后，重新生成所有卡片
SELECT regenerate_all_cards(
    p_actor_id := '00000000-0000-0000-0000-000000000000'::UUID,
    p_actor_type := 'System'
);
```

---

## 注意事项

### 1. 性能考虑

- **触发器自动更新**：实时更新，适合卡片变化少的场景
- **批量更新**：如果大量数据变化，建议先禁用触发器，批量更新后再启用

### 2. 事务保证

- 所有函数都在事务中执行
- 删除旧卡片和创建新卡片是原子操作

### 3. 历史记录

- **不保留历史记录**：删除旧卡片时直接 `DELETE`，不使用软删除
- 如果需要历史记录，建议在应用层实现

### 4. 错误处理

- 如果 location 不存在，函数会抛出异常
- 建议在应用层捕获异常并处理

---

## 测试示例

### 测试场景 A：门牌下只有 1 个 ActiveBed

```sql
-- 1. 创建 location
INSERT INTO locations (...) VALUES (...);

-- 2. 创建床位并绑定住户
INSERT INTO beds (..., resident_id, ...) VALUES (...);

-- 3. 绑定设备
INSERT INTO devices (..., bound_bed_id, monitoring_enabled, ...) VALUES (...);

-- 4. 触发器自动创建卡片，或手动触发
SELECT regenerate_cards_for_location(location_id);
```

### 测试场景 B：门牌下有多个 ActiveBed

```sql
-- 1. 创建多个床位并绑定住户
INSERT INTO beds (...) VALUES (...), (...);

-- 2. 绑定设备
INSERT INTO devices (...) VALUES (...);

-- 3. 触发器自动创建卡片
-- 结果：N 个 ActiveBed 卡片 + 0 或 1 个 Location 卡片
```

---

## 相关文档

- 卡片创建规则：`docs/20_Card_Creation_Rules_Final.md`
- 卡片表结构：`db/18_cards.sql`
- 卡片函数实现：`db/19_card_functions.sql`

