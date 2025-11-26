# 卡片权限设计

## 概述

卡片权限采用**动态计算**方式，不在卡片表中存储权限信息。权限根据用户类型（Staff/Resident/Family）和相应的权限规则动态计算。

**用户类型**：
- **Staff（员工）**：根据角色、`alert_scope`、`tags` 和 `resident_caregivers` 表动态计算
- **Resident（住户）**：只能看到自己的卡片（自己所在的床位/门牌号）
- **Family（家属）**：根据 `resident_contacts` 表关联，只能看到关联住户的卡片

## 权限设计原则

### 1. 不在卡片表中存储权限

**原因**：
- 权限是动态的，可能随时变化（用户角色变化、住户分配变化等）
- 如果存储在卡片表中，需要频繁更新，维护成本高
- 权限计算逻辑复杂，涉及多个表（users、locations、resident_caregivers）

**方案**：
- 卡片表只存储卡片的基本信息（名称、地址、关联的住户和设备）
- 权限通过 `get_user_cards()` 函数动态计算

### 2. 权限计算逻辑

权限基于以下信息动态计算：

1. **用户角色**（`users.role`）：
   - **Admin**：在 tenant 下，可以看到该 tenant 下的所有卡片（所有园区）
     - 例如：MonirStar tenant 下有 LDV9、Litton、Spring 三个园区，Admin 可以看到所有园区的卡片
   - **Director / NurseManager**：分园区的，在同一个 tenant 下，根据 `alert_scope` 决定可见范围 
     - 每个园区各有 Director/NurseManager（如 LDV9 园区的 Director、Litton 园区的 Director）location_tag
   - **Staff**：根据 `alert_scope` 决定

2. **用户告警范围**（`users.alert_scope`）：
   - `ALL`：可以看到该 tenant 下的所有卡片
     - Director/NurseManager 也是分园区的，需要设置 `alert_scope = 'ALL'` 才能看到该 tenant 下的所有卡片
   - `LOCATION`：根据 `locations.location_tag` 匹配 `users.tags`
     - tenant 下面可以有多个园区，用 location_tag 区分
     - 如果用户设置了 tags，则匹配 location_tag；否则根据其他规则
   - `ASSIGNED_ONLY`：根据 `resident_caregivers` 表，只看到自己负责的住户的卡片

3. **位置标签**（`locations.location_tag`）：
   - 用于匹配用户的 `tags`，决定用户可以看到哪些 location 的卡片
   - 例如：location_tag = "A 院区主楼"，用户的 tags 中包含 "A 院区主楼"，则可以看见该 location 的卡片

4. **住户分配**（`resident_caregivers` 表）：
   - 用于 `ASSIGNED_ONLY` 权限，确定用户负责哪些住户

## 权限查询函数

### `get_user_cards(p_user_id)`

根据用户 ID 返回该用户可见的卡片列表。

**权限规则**：

1. **Admin 角色权限**（同一 tenant 下）：
   ```sql
   WHERE users.role = 'Admin' AND cards.tenant_id = users.tenant_id
   ```
   - Admin 在 tenant 下，可以看到该 tenant 下的所有卡片（所有园区）
   - 例如：MonirStar tenant 下有 LDV9、Litton、Spring 三个园区，Admin 可以看到所有园区的卡片

2. **ALL 权限**（同一 tenant 下）：
   ```sql
   WHERE users.alert_scope = 'ALL' AND cards.tenant_id = users.tenant_id
   ```
   - 返回该 tenant 下的所有卡片
   - Director/NurseManager 也是分园区的，需要设置 `alert_scope = 'ALL'` 才能看到该 tenant 下的所有卡片

3. **LOCATION 权限**（同一 tenant 下）：
   ```sql
   WHERE users.alert_scope = 'LOCATION'
     AND locations.location_tag = ANY(users.tags)  -- location_tag 在用户的 tags 中
   ```
   - 返回用户标签中包含 location_tag 的卡片
   - 例如：location_tag = "A 院区主楼"，用户的 tags 中包含 "A 院区主楼"，则可以看见该 location 的卡片

4. **ASSIGNED_ONLY 权限**：
   ```sql
   WHERE users.alert_scope = 'ASSIGNED_ONLY'
     AND (
       -- ActiveBed 卡片：住户分配给该用户
       (card_type = 'ActiveBed' AND resident_id IN (
         SELECT resident_id FROM resident_caregivers 
         WHERE caregiver_id = user_id
       ))
       OR
       -- Location 卡片：有住户分配给该用户
       (card_type = 'Location' AND location_id IN (
         SELECT DISTINCT r.location_id 
         FROM residents r
         JOIN resident_caregivers rc ON r.resident_id = rc.resident_id
         WHERE rc.caregiver_id = user_id
       ))
     )
   ```
   - 返回用户负责的住户相关的卡片

---

## 住户和家属权限

### 住户权限（Resident）

**权限规则**：
- 住户只能看到自己的卡片（自己所在的床位/门牌号）
- 不涉及 `alert_scope` 或 `location_tag` 匹配

**可见卡片**：
1. **ActiveBed 卡片**：住户自己的床位卡片
   - 条件：`card_type = 'ActiveBed'` 且 `bed_id = resident.bed_id` 且 `primary_resident_id = resident_id`
2. **Location 卡片**：住户所在的门牌号卡片
   - 条件：`card_type = 'Location'` 且 `location_id = resident.location_id` 且住户在 `card_residents` 关联表中
   - **权限规则**：
     - **情况1（单人居住）**：该 `location_id` 下住户唯一且为该住户
     - **情况2（夫妻同住）**：该 `location_id` 下的所有住户都使用相同的 `family_tag`（夫妻可以互相查看 Location 卡片）
   - **注意**：不考虑多人合租场景（不同 `family_tag` 的多人合租，设备属于公共，不能让个人所见）
   - **卡片名称规则**：
     - 当住户唯一时，卡片名称显示该住户的 LastName
     - 当有多个住户（夫妻同住）时，卡片名称显示 `location_name`

**使用方式**：
```sql
-- 获取住户可见的卡片列表
SELECT * FROM get_resident_cards('resident_id_here');
-- 或使用视图
SELECT * FROM v_resident_cards WHERE resident_id = 'resident_id_here';
```

### 家属权限（Family/Contact）

**权限规则**：
- **权限逻辑与住户相同**：家属看到的内容和住户看到的内容相同
- 家属根据 `resident_contacts` 表关联到住户，然后应用和住户相同的权限逻辑
- 需要满足：`can_view_status = TRUE` 且 `is_active = TRUE`
- **如果不开通家属账号**（`resident_contacts` 表中没有关联），家属就不可见任何卡片
- 一个家属可以关联多个住户（例如子女看两个老人），可以看到所有关联住户的卡片

**可见卡片**（与住户权限相同）：
1. **ActiveBed 卡片**：关联住户的床位卡片
   - 条件：`card_type = 'ActiveBed'` 且 `bed_id = resident.bed_id` 且 `primary_resident_id = resident_id`
   - 与住户看到的 ActiveBed 卡片逻辑相同
2. **Location 卡片**：关联住户所在的门牌号卡片
   - 条件：`card_type = 'Location'` 且 `location_id = resident.location_id` 且住户在 `card_residents` 关联表中
   - 与住户看到的 Location 卡片逻辑相同
   - **权限规则**（与住户权限相同）：
     - **情况1（单人居住）**：该 `location_id` 下住户唯一且为该住户
     - **情况2（夫妻同住）**：该 `location_id` 下的所有住户都使用相同的 `family_tag`（夫妻可以互相查看 Location 卡片）
   - **注意**：不考虑多人合租场景（不同 `family_tag` 的多人合租，设备属于公共，不能让个人所见）
   - **卡片名称规则**：
     - 当住户唯一时，卡片名称显示该住户的 LastName
     - 当有多个住户（夫妻同住）时，卡片名称显示 `location_name`

**使用方式**：
```sql
-- 获取家属可见的卡片列表（家属通过 resident_contacts 表登录，使用 contact_id）
SELECT * FROM get_family_cards('contact_id_here');
-- 或使用视图
SELECT * FROM v_family_cards WHERE contact_id = 'contact_id_here';
```

**重要说明**：
- 家属**不使用 users 表**，家属通过 `resident_contacts` 表登录
- 家属登录时使用 `phone_hash`/`email_hash` 匹配 `resident_contacts` 表
- 登录成功后，使用 `contact_id` 来查询可见的卡片

---

## 使用方式

### 方式 1：使用函数

```sql
-- 获取用户（Staff）可见的卡片列表
SELECT * FROM get_user_cards('user_id_here');

-- 获取住户可见的卡片列表
SELECT * FROM get_resident_cards('resident_id_here');

-- 获取家属可见的卡片列表（使用 contact_id）
SELECT * FROM get_family_cards('contact_id_here');
```

### 方式 2：使用视图

```sql
-- 使用视图（需要先设置用户上下文）
SELECT * FROM v_user_cards WHERE user_id = 'user_id_here';
SELECT * FROM v_resident_cards WHERE resident_id = 'resident_id_here';
SELECT * FROM v_family_cards WHERE contact_id = 'contact_id_here';
```

### 方式 3：应用层查询

```sql
-- 应用层可以根据用户权限动态构建查询
SELECT c.*
FROM cards c
JOIN users u ON c.tenant_id = u.tenant_id
WHERE u.user_id = 'user_id_here'
  AND (
    u.role = 'Admin'
    OR u.alert_scope = 'ALL'
    OR (u.alert_scope = 'LOCATION' AND ...)
    OR (u.alert_scope = 'ASSIGNED_ONLY' AND ...)
  );
```

## 权限表结构

### 相关表

1. **users 表**：
   - `alert_scope`：告警范围（ALL / LOCATION / ASSIGNED_ONLY）
   - `tags`：用户标签（JSONB 数组）
   - `role`：用户角色

2. **locations 表**：
   - `location_tag`：位置标签（VARCHAR），用于匹配用户的 tags

3. **resident_caregivers 表**：
   - `caregiver_id`：护理人员 ID
   - `resident_id`：住户 ID
   - `is_active`：是否激活

### 不需要单独建权限表

**原因**：
- 权限信息已经分散在多个表中（users、locations、resident_caregivers）
- 权限是动态计算的，不需要冗余存储
- 如果单独建权限表，需要维护数据一致性，增加复杂度

## 性能优化

### 索引

已创建的索引：
- `idx_cards_tenant_id`：按租户查询
- `idx_cards_location_id`：按位置查询
- `idx_cards_resident_id`：按住户查询
- `idx_resident_caregivers_caregiver_id`：按护理人员查询

### 缓存建议

应用层可以缓存用户的可见卡片列表：
- 缓存键：`user_cards:{user_id}`
- 缓存失效：当用户权限变化、住户分配变化、卡片变化时

## 总结

1. **权限不存储在卡片表中**：卡片表只存储卡片的基本信息
2. **权限动态计算**：通过 `get_user_cards()` 函数根据用户信息动态计算
3. **不需要单独建权限表**：权限信息已经分散在 users、locations、resident_caregivers 表中
4. **应用层调用**：应用层在查询卡片时调用权限过滤函数

