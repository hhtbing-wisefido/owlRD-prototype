-- 卡片表 (cards)
-- 用途：
--   1) 存储计算好的卡片信息，供前端 Vue 直接调用，避免每次查询时重新计算
--   2) 卡片类型：ActiveBed（床位卡片）或 Location（门牌号卡片）
--   3) 卡片创建规则：参见 docs/17_Card_Creation_Rules.md
-- 维护策略：
--   - 当床位/住户/设备绑定关系变化时，触发卡片重新计算（通过应用层或触发器）
--   - 建议使用应用层维护，确保数据一致性

CREATE TABLE IF NOT EXISTS cards (
    -- Primary / SaaS
    card_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id  UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- Card Type & Binding
    -- 卡片类型：ActiveBed（床位卡片）或 Location（门牌号卡片）
    card_type  VARCHAR(20) NOT NULL,  -- 'ActiveBed' / 'Location'
    
    -- 关联对象（根据 card_type 决定使用哪个字段）
    -- ActiveBed 卡片：bed_id 不为 NULL，location_id 可为 NULL（冗余，加速查询）
    -- Location 卡片：location_id 不为 NULL，bed_id 为 NULL
    bed_id     UUID REFERENCES beds(bed_id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(location_id) ON DELETE CASCADE,
    
    -- 卡片显示信息（计算好的，直接供前端使用）
    card_name  VARCHAR(255) NOT NULL,  -- 卡片名称（如 "Smith" 或 "201"）
    card_address VARCHAR(255) NOT NULL, -- 卡片地址（如 "BuildA-1F-201-Bedroom-BedA"）
    
    -- 关联的住户（用于 ActiveBed 卡片，冗余存储，加速查询）
    -- 注意：Location 卡片可能关联多个住户，此字段为 NULL，通过 card_residents 关联表查询
    resident_id UUID REFERENCES residents(resident_id) ON DELETE SET NULL,
    
    -- ========== 报警路由配置 ==========
    -- 路由规则：
    --   1) ActiveBed 卡片：设备 → 床 → 住户 → 指定的护士（通过 resident_caregivers 表）
    --   2) Location 卡片（公共空间/多人房间）：设备 → location → 警报通报组（alert_user_ids + alert_tags）
    --   3) Location 卡片（个人空间，单人/伴侣房）：设备 → location → 该房间所有住户的护士（通过 resident_caregivers 表）或 警报通报组
    -- 
    -- 路由判断逻辑（基于 locations 表）：
    --   - 如果 locations.is_public_space = TRUE 或 locations.is_multi_person_room = TRUE：
    --     使用警报通报组进行路由（通过 locations.alert_user_ids/alert_tags 或 cards.routing_alert_user_ids/routing_alert_tags）
    --   - 如果 locations.is_public_space = FALSE 且 locations.is_multi_person_room = FALSE：
    --     使用该房间所有住户的护士进行路由（通过 resident_caregivers 表查找），或使用警报通报组（如果配置了）
    -- 
    -- 此字段用于覆盖 locations 表的配置（可选）：
    --   - TRUE：强制使用警报通报组路由（公共空间/多人房间）
    --   - FALSE：使用住户的护士路由（个人空间）
    --   - NULL：自动判断（根据 locations.is_public_space 或 locations.is_multi_person_room）
    is_public_space BOOLEAN,  -- TRUE=使用警报通报组路由，FALSE=使用住户的护士路由，NULL=自动判断
    
    -- 警报通报组路由（当 is_public_space = TRUE 或 locations.is_multi_person_room = TRUE 时使用）
    -- 用于公共空间/多人房间的设备，覆盖 locations 表的配置
    -- 如果为 NULL，则使用 locations.alert_user_ids 和 locations.alert_tags
    -- 查询规则：
    --   1) 如果指定了 routing_alert_user_ids，直接包含这些用户
    --   2) 如果指定了 routing_alert_tags，匹配 users.tags 中包含这些标签的用户
    --   3) 两者可以同时使用，取并集
    routing_alert_user_ids UUID[],   -- 警报接收者用户ID列表（直接指定，覆盖 locations.alert_user_ids）
    routing_alert_tags VARCHAR[],    -- 警报接收者标签组（匹配 users.tags，覆盖 locations.alert_tags）
    
    -- Status
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 约束：确保卡片类型与关联对象的一致性
    CONSTRAINT chk_card_type_binding CHECK (
        (card_type = 'ActiveBed' AND bed_id IS NOT NULL) OR
        (card_type = 'Location' AND location_id IS NOT NULL AND bed_id IS NULL)
    ),
    
    -- 同一租户内，ActiveBed 卡片与床位一一对应
    -- Location 卡片：同一门牌号在同一时间只能有一个活跃卡片
    UNIQUE(tenant_id, bed_id) WHERE card_type = 'ActiveBed' AND bed_id IS NOT NULL,
    UNIQUE(tenant_id, location_id) WHERE card_type = 'Location' AND location_id IS NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cards_tenant_id ON cards(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(tenant_id, card_type);
CREATE INDEX IF NOT EXISTS idx_cards_bed_id ON cards(tenant_id, bed_id) WHERE bed_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_location_id ON cards(tenant_id, location_id) WHERE location_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_resident_id ON cards(tenant_id, resident_id) WHERE resident_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_active ON cards(tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_cards_public_space ON cards(tenant_id, is_public_space) WHERE is_public_space IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_routing_alert_user_ids ON cards USING GIN (routing_alert_user_ids) WHERE routing_alert_user_ids IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cards_routing_alert_tags ON cards USING GIN (routing_alert_tags) WHERE routing_alert_tags IS NOT NULL;

-- 卡片-设备关联表 (card_devices)
-- 用途：存储卡片绑定的设备列表
-- 注意：一个设备可以绑定到多个卡片（如门牌卡片和床位卡片），但通常一个设备只绑定一个卡片

CREATE TABLE IF NOT EXISTS card_devices (
    card_device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    
    card_id       UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    device_id     UUID NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    
    -- 绑定类型：用于区分设备是直接绑定还是间接绑定
    -- 'direct'：设备直接绑定到卡片对应的对象（如设备绑床，卡片是ActiveBed）
    -- 'indirect'：设备间接绑定（如门牌卡片绑定该门牌下所有未绑床的设备）
    binding_type  VARCHAR(20) NOT NULL DEFAULT 'direct',  -- 'direct' / 'indirect'
    
    -- 同一卡片不能重复绑定同一设备
    UNIQUE(card_id, device_id)
);

CREATE INDEX IF NOT EXISTS idx_card_devices_card_id ON card_devices(card_id);
CREATE INDEX IF NOT EXISTS idx_card_devices_device_id ON card_devices(device_id);
CREATE INDEX IF NOT EXISTS idx_card_devices_tenant ON card_devices(tenant_id);

-- 卡片-住户关联表 (card_residents)
-- 用途：存储 Location 卡片关联的多个住户（ActiveBed 卡片通过 cards.resident_id 直接关联）
-- 注意：Location 卡片可能关联多个住户（当门牌号下有多个住户时）

CREATE TABLE IF NOT EXISTS card_residents (
    card_resident_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    
    card_id         UUID NOT NULL REFERENCES cards(card_id) ON DELETE CASCADE,
    resident_id     UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    
    -- 同一卡片不能重复关联同一住户
    UNIQUE(card_id, resident_id)
);

CREATE INDEX IF NOT EXISTS idx_card_residents_card_id ON card_residents(card_id);
CREATE INDEX IF NOT EXISTS idx_card_residents_resident_id ON card_residents(resident_id);
CREATE INDEX IF NOT EXISTS idx_card_residents_tenant ON card_residents(tenant_id);

-- 视图：卡片完整信息视图（供前端直接查询）
-- 包含卡片基本信息、绑定的设备列表、关联的住户列表
-- 注意：设备列表和住户列表使用子查询，避免 JSON 聚合的复杂性

CREATE OR REPLACE VIEW v_cards_full AS
SELECT 
    c.card_id,
    c.tenant_id,
    c.card_type,
    c.bed_id,
    c.location_id,
    c.card_name,
    c.card_address,
    c.resident_id AS primary_resident_id,
    c.is_active,
    
    -- 绑定的设备列表（JSON 数组）
    (
        SELECT COALESCE(json_agg(
            jsonb_build_object(
                'device_id', d.device_id,
                'device_name', d.name,
                'device_type', d.device_type,
                'device_model', d.device_model,
                'binding_type', cd.binding_type
            ) ORDER BY d.name
        ), '[]'::json)
        FROM card_devices cd
        JOIN devices d ON cd.device_id = d.device_id
        WHERE cd.card_id = c.card_id 
          AND d.installed = TRUE
    ) AS devices,
    
    -- 关联的住户列表（JSON 数组）
    (
        SELECT COALESCE(json_agg(
            jsonb_build_object(
                'resident_id', r.resident_id,
                'last_name', r.last_name,
                'first_name', r.first_name,
                'anonymous_name', r.anonymous_name
            ) ORDER BY r.last_name, r.first_name
        ), '[]'::json)
        FROM (
            -- ActiveBed 卡片：从 cards.resident_id 获取
            SELECT r.resident_id, r.last_name, r.first_name, r.anonymous_name
            FROM residents r
            WHERE r.resident_id = c.resident_id 
              AND c.card_type = 'ActiveBed'
              AND r.status = 'active'
            UNION
            -- Location 卡片：从 card_residents 关联表获取
            SELECT r.resident_id, r.last_name, r.first_name, r.anonymous_name
            FROM card_residents cr
            JOIN residents r ON cr.resident_id = r.resident_id
            WHERE cr.card_id = c.card_id 
              AND c.card_type = 'Location'
              AND r.status = 'active'
        ) r
    ) AS residents,
    
    -- 设备数量（用于排序和统计）
    (
        SELECT COUNT(*)
        FROM card_devices cd
        JOIN devices d ON cd.device_id = d.device_id
        WHERE cd.card_id = c.card_id 
          AND d.installed = TRUE
    ) AS device_count,
    
    -- 住户数量（用于排序和统计）
    (
        SELECT COUNT(*)
        FROM (
            SELECT r.resident_id
            FROM residents r
            WHERE r.resident_id = c.resident_id 
              AND c.card_type = 'ActiveBed'
              AND r.status = 'active'
            UNION
            SELECT r.resident_id
            FROM card_residents cr
            JOIN residents r ON cr.resident_id = r.resident_id
            WHERE cr.card_id = c.card_id 
              AND c.card_type = 'Location'
              AND r.status = 'active'
        ) r
    ) AS resident_count

FROM cards c
WHERE c.is_active = TRUE;

-- 注释
COMMENT ON TABLE cards IS '卡片表：存储计算好的卡片信息，供前端直接调用';
COMMENT ON COLUMN cards.card_type IS '卡片类型：ActiveBed（床位卡片）或 Location（门牌号卡片）';
COMMENT ON COLUMN cards.card_name IS '卡片名称：ActiveBed卡片显示住户姓名，Location卡片显示门牌号或唯一住户姓名';
COMMENT ON COLUMN cards.card_address IS '卡片地址：完整地址格式，如 BuildA-1F-201-Bedroom-BedA';
COMMENT ON TABLE card_devices IS '卡片-设备关联表：存储卡片绑定的设备列表';
COMMENT ON TABLE card_residents IS '卡片-住户关联表：存储Location卡片关联的多个住户（ActiveBed卡片通过cards.resident_id直接关联）';
COMMENT ON VIEW v_cards_full IS '卡片完整信息视图：包含卡片基本信息、绑定的设备列表、关联的住户列表，供前端直接查询';

-- ============================================================================
-- 卡片维护说明
-- ============================================================================
-- 
-- 卡片表需要在以下场景下重新计算和维护：
-- 
-- 1. 床位绑定关系变化时：
--    - 住户绑定/解绑床位（beds.resident_id 变化）
--    - 设备绑定/解绑床位（devices.bound_bed_id 变化）
--    - 床位类型变化（ActiveBed ↔ NonActiveBed）
--    → 触发：重新计算该床位的 ActiveBed 卡片，或创建/删除卡片
-- 
-- 2. 门牌号下住户变化时：
--    - 住户绑定/解绑门牌号（residents.location_id 变化）
--    - 住户状态变化（residents.status 变化）
--    → 触发：重新计算该门牌号的 Location 卡片（卡片名称可能变化）
-- 
-- 3. 设备绑定关系变化时：
--    - 设备绑定/解绑门牌号/房间/床位（devices.location_id/bound_room_id/bound_bed_id 变化）
--    → 触发：重新计算相关卡片（ActiveBed 卡片或 Location 卡片）的设备列表
-- 
-- 4. 地址信息变化时：
--    - 门牌号/房间/床位名称变化（locations/rooms/beds 名称变化）
--    → 触发：更新相关卡片的 card_address
-- 
-- 维护策略建议：
-- 
-- 方案 A：应用层维护（推荐）
--   - 在业务逻辑层（API/Service）维护卡片表
--   - 当绑定关系变化时，调用卡片计算函数
--   - 优点：逻辑清晰，易于调试和维护
--   - 缺点：需要确保所有变更路径都调用维护函数
-- 
-- 方案 B：数据库触发器维护
--   - 在 beds/residents/devices 表上创建触发器
--   - 当相关字段变化时，自动触发卡片重新计算
--   - 优点：自动维护，不会遗漏
--   - 缺点：触发器逻辑复杂，调试困难，可能影响性能
-- 
-- 方案 C：定时任务维护
--   - 使用定时任务（如 cron job）定期重新计算所有卡片
--   - 优点：简单，不需要复杂的触发逻辑
--   - 缺点：数据可能短暂不一致，需要权衡更新频率
-- 
-- 推荐使用方案 A（应用层维护），结合方案 C（定时任务兜底，如每小时全量刷新一次）
-- 
-- 卡片计算函数示例（伪代码）：
-- 
-- FUNCTION recalculate_cards_for_location(location_id):
--   1. 查询该门牌号下的所有 ActiveBed
--   2. 查询该门牌号下的所有设备（按绑定类型分组）
--   3. 根据卡片创建规则（docs/17_Card_Creation_Rules.md）创建/更新卡片
--   4. 更新 card_devices 和 card_residents 关联表
-- 
-- FUNCTION recalculate_cards_for_bed(bed_id):
--   1. 判断床位类型（ActiveBed / NonActiveBed）
--   2. 如果是 ActiveBed，创建/更新 ActiveBed 卡片
--   3. 更新 card_devices 关联表
--   4. 触发相关门牌号的 Location 卡片重新计算（如果设备绑定关系变化）
--

-- ============================================================================
-- 用户权限过滤：根据用户权限返回可见的卡片列表
-- ============================================================================
-- 
-- 权限规则：
--   1. Admin 角色：在 tenant 下，可以看到该 tenant 下的所有卡片（所有园区）
--      例如：MonirStar tenant 下有 LDV9、Litton、Spring 三个园区，Admin 可以看到所有园区的卡片
--   2. alert_scope = 'ALL'：可以看到该 tenant 下的所有卡片（所有园区）
--      - Director/NurseManager 也是分园区的，需要设置 alert_scope = 'ALL' 才能看到该 tenant 下的所有卡片
--   3. alert_scope = 'LOCATION'：根据 locations.location_tag 匹配 users.tags
--      - tenant 下面可以有多个园区，用 location_tag 区分（如 LDV9、Litton、Spring）
--      - 每个园区各有 Director/NurseManager
--      - 如果用户设置了 tags，则匹配 location_tag；否则根据其他规则
--   4. alert_scope = 'ASSIGNED_ONLY'：根据 resident_caregivers 表，只看到自己负责的住户的卡片
-- 
-- 使用方式：
--   SELECT * FROM get_user_cards('user_id_here');
--   或
--   SELECT * FROM v_user_cards WHERE user_id = 'user_id_here';

-- 函数：根据用户ID获取可见的卡片列表
CREATE OR REPLACE FUNCTION get_user_cards(p_user_id UUID)
RETURNS TABLE (
    card_id UUID,
    tenant_id UUID,
    card_type VARCHAR,
    bed_id UUID,
    location_id UUID,
    card_name VARCHAR,
    card_address VARCHAR,
    primary_resident_id UUID,
    is_active BOOLEAN,
    devices JSON,
    residents JSON,
    device_count BIGINT,
    resident_count BIGINT
) AS $$
DECLARE
    v_user_tenant_id UUID;
    v_user_alert_scope VARCHAR(20);
    v_user_role VARCHAR(50);
    v_user_tags JSONB;
BEGIN
    -- 获取用户信息
    SELECT u.tenant_id, u.alert_scope, u.role, u.tags
    INTO v_user_tenant_id, v_user_alert_scope, v_user_role, v_user_tags
    FROM users u
    WHERE u.user_id = p_user_id
      AND u.status = 'active';
    
    IF v_user_tenant_id IS NULL THEN
        RAISE EXCEPTION 'User not found or inactive: %', p_user_id;
    END IF;
    
    -- 返回查询结果
    RETURN QUERY
    SELECT 
        vcf.card_id,
        vcf.tenant_id,
        vcf.card_type,
        vcf.bed_id,
        vcf.location_id,
        vcf.card_name,
        vcf.card_address,
        vcf.primary_resident_id,
        vcf.is_active,
        vcf.devices,
        vcf.residents,
        vcf.device_count,
        vcf.resident_count
    FROM v_cards_full vcf
    WHERE vcf.tenant_id = v_user_tenant_id
      AND (
        -- 权限规则 1：Admin 角色 - 在 tenant 下，可以看到该 tenant 下的所有卡片（所有园区）
        -- 例如：MonirStar tenant 下有 LDV9、Litton、Spring 三个园区，Admin 可以看到所有园区的卡片
        v_user_role = 'Admin'
        OR
        -- 权限规则 2：ALL - 可以看到该 tenant 下的所有卡片（所有园区）
        -- Director/NurseManager 也是分园区的，需要设置 alert_scope = 'ALL' 才能看到该 tenant 下的所有卡片
        v_user_alert_scope = 'ALL'
        OR
        -- 权限规则 3：LOCATION - 根据 locations.location_tag 匹配
        -- tenant 下面可以有多个园区，用 location_tag 区分（如 LDV9、Litton、Spring）
        -- 如果用户设置了 tags，则匹配 location_tag；否则根据其他规则
        (
          v_user_alert_scope = 'LOCATION'
          AND EXISTS (
            SELECT 1
            FROM locations l
            WHERE l.location_id = vcf.location_id
              AND (
                -- 如果用户有 tags，检查 location_tag 是否在用户的 tags 中
                (v_user_tags IS NOT NULL 
                 AND l.location_tag IS NOT NULL
                 AND l.location_tag = ANY(ARRAY(
                   SELECT jsonb_array_elements_text(v_user_tags)
                 )))
                OR
                -- 如果 location 没有 location_tag，则所有 LOCATION 权限用户都可见
                (l.location_tag IS NULL)
              )
          )
        )
        OR
        -- 权限规则 4：ASSIGNED_ONLY - 根据 resident_caregivers 表，只看到自己负责的住户的卡片
        (
          v_user_alert_scope = 'ASSIGNED_ONLY'
          AND (
            -- ActiveBed 卡片：检查住户是否分配给该用户
            (
              vcf.card_type = 'ActiveBed'
              AND vcf.primary_resident_id IS NOT NULL
              AND EXISTS (
                SELECT 1
                FROM resident_caregivers rc
                WHERE rc.resident_id = vcf.primary_resident_id
                  AND rc.caregiver_id = p_user_id
                  AND rc.is_active = TRUE
              )
            )
            OR
            -- Location 卡片：检查是否有任何关联的住户分配给该用户
            (
              vcf.card_type = 'Location'
              AND EXISTS (
                SELECT 1
                FROM card_residents cr
                JOIN resident_caregivers rc ON cr.resident_id = rc.resident_id
                WHERE cr.card_id = vcf.card_id
                  AND rc.caregiver_id = p_user_id
                  AND rc.is_active = TRUE
              )
            )
          )
        )
      )
    ORDER BY vcf.card_type, vcf.card_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 视图：用户可见的卡片列表（供前端直接查询）
-- 注意：此视图需要传入 user_id，建议使用函数 get_user_cards() 或应用层过滤
CREATE OR REPLACE VIEW v_user_cards AS
SELECT 
    u.user_id,
    vcf.*
FROM users u
CROSS JOIN v_cards_full vcf
WHERE u.status = 'active'
  AND vcf.tenant_id = u.tenant_id
  AND (
    -- 权限规则 1：Admin 角色 - 在 tenant 下，可以看到该 tenant 下的所有卡片（所有园区）
    u.role = 'Admin'
    OR
    -- 权限规则 2：ALL - 可以看到该 tenant 下的所有卡片（所有园区）
    u.alert_scope = 'ALL'
    OR
    -- 权限规则 3：LOCATION
        (
          u.alert_scope = 'LOCATION'
          AND EXISTS (
            SELECT 1
            FROM locations l
            WHERE l.location_id = vcf.location_id
              AND (
                -- 如果用户有 tags，检查 location_tag 是否在用户的 tags 中
                (u.tags IS NOT NULL 
                 AND l.location_tag IS NOT NULL
                 AND l.location_tag = ANY(ARRAY(
                   SELECT jsonb_array_elements_text(u.tags)
                 )))
                OR
                -- 如果 location 没有 location_tag，则所有 LOCATION 权限用户都可见
                (l.location_tag IS NULL)
              )
          )
        )
        OR
        -- 权限规则 4：ASSIGNED_ONLY
        (
          u.alert_scope = 'ASSIGNED_ONLY'
          AND (
        (
          vcf.card_type = 'ActiveBed'
          AND vcf.primary_resident_id IS NOT NULL
          AND EXISTS (
            SELECT 1
            FROM resident_caregivers rc
            WHERE rc.resident_id = vcf.primary_resident_id
              AND rc.caregiver_id = u.user_id
              AND rc.is_active = TRUE
          )
        )
        OR
        (
          vcf.card_type = 'Location'
          AND EXISTS (
            SELECT 1
            FROM card_residents cr
            JOIN resident_caregivers rc ON cr.resident_id = rc.resident_id
            WHERE cr.card_id = vcf.card_id
              AND rc.caregiver_id = u.user_id
              AND rc.is_active = TRUE
          )
          )
        )
      );

-- 注释
COMMENT ON FUNCTION get_user_cards(UUID) IS '根据用户ID获取可见的卡片列表，自动应用权限过滤规则';
COMMENT ON VIEW v_user_cards IS '用户可见的卡片列表视图（需要应用层按user_id过滤，或使用get_user_cards函数）';

-- ============================================================================
-- 住户和家属卡片查询：根据住户ID或家属用户ID获取可见的卡片列表
-- ============================================================================
-- 
-- 权限规则：
--   1. 住户（resident）：只能看到自己的卡片（自己所在的床位/门牌号）
--   2. 家属（family/contact）：根据 resident_contacts 表关联，只能看到关联住户的卡片
--      - 需要 can_view_status = TRUE
--      - 一个家属可以关联多个住户（例如子女看两个老人）
-- 
-- 使用方式：
--   -- 住户登录后
--   SELECT * FROM get_resident_cards('resident_id_here');
--   
--   -- 家属登录后（通过contact_id，家属通过 resident_contacts 表登录，不使用 users 表）
--   SELECT * FROM get_family_cards('contact_id_here');

-- 函数：根据住户ID获取可见的卡片列表（住户自己）
CREATE OR REPLACE FUNCTION get_resident_cards(p_resident_id UUID)
RETURNS TABLE (
    card_id UUID,
    tenant_id UUID,
    card_type VARCHAR,
    bed_id UUID,
    location_id UUID,
    card_name VARCHAR,
    card_address VARCHAR,
    primary_resident_id UUID,
    is_active BOOLEAN,
    devices JSON,
    residents JSON,
    device_count BIGINT,
    resident_count BIGINT
) AS $$
DECLARE
    v_resident_tenant_id UUID;
    v_resident_bed_id UUID;
    v_resident_location_id UUID;
    v_resident_family_tag VARCHAR(100);
BEGIN
    -- 获取住户信息（包括 family_tag）
    SELECT r.tenant_id, r.bed_id, r.location_id, r.family_tag
    INTO v_resident_tenant_id, v_resident_bed_id, v_resident_location_id, v_resident_family_tag
    FROM residents r
    WHERE r.resident_id = p_resident_id
      AND r.status = 'active';
    
    IF v_resident_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Resident not found or inactive: %', p_resident_id;
    END IF;
    
    -- 返回查询结果：住户只能看到自己的卡片
    RETURN QUERY
    SELECT 
        vcf.card_id,
        vcf.tenant_id,
        vcf.card_type,
        vcf.bed_id,
        vcf.location_id,
        vcf.card_name,
        vcf.card_address,
        vcf.primary_resident_id,
        vcf.is_active,
        vcf.devices,
        vcf.residents,
        vcf.device_count,
        vcf.resident_count
    FROM v_cards_full vcf
    WHERE vcf.tenant_id = v_resident_tenant_id
      AND (
        -- 规则 1：ActiveBed 卡片 - 住户自己的床位
        (
          vcf.card_type = 'ActiveBed'
          AND vcf.bed_id = v_resident_bed_id
          AND vcf.primary_resident_id = p_resident_id
        )
        OR
        -- 规则 2：Location 卡片 - 住户所在的门牌号
        -- 权限规则：
        --   - 该 location_id 下住户唯一且为该住户（单人居住）
        --   - 或者该 location_id 下的所有住户都使用相同的 family_tag（夫妻同住，可以互相查看）
        -- 注意：不考虑多人合租场景（不同 family_tag 的多人合租）
        (
          vcf.card_type = 'Location'
          AND vcf.location_id = v_resident_location_id
          AND EXISTS (
            SELECT 1
            FROM card_residents cr
            WHERE cr.card_id = vcf.card_id
              AND cr.resident_id = p_resident_id
          )
          AND (
            -- 情况1：该 location 下只有1个住户（单人居住）
            (
              SELECT COUNT(*)
              FROM card_residents cr2
              WHERE cr2.card_id = vcf.card_id
            ) = 1
            OR
            -- 情况2：该 location 下的所有住户都使用相同的 family_tag（夫妻同住）
            (
              v_resident_family_tag IS NOT NULL
              AND NOT EXISTS (
                SELECT 1
                FROM card_residents cr3
                JOIN residents r3 ON cr3.resident_id = r3.resident_id
                WHERE cr3.card_id = vcf.card_id
                  AND r3.status = 'active'
                  AND (r3.family_tag IS NULL OR r3.family_tag != v_resident_family_tag)
              )
            )
          )
        )
      )
    ORDER BY vcf.card_type, vcf.card_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 函数：根据家属联系人ID获取可见的卡片列表（家属）
-- 注意：家属通过 resident_contacts 表登录，不使用 users 表
CREATE OR REPLACE FUNCTION get_family_cards(p_contact_id UUID)
RETURNS TABLE (
    card_id UUID,
    tenant_id UUID,
    card_type VARCHAR,
    bed_id UUID,
    location_id UUID,
    card_name VARCHAR,
    card_address VARCHAR,
    primary_resident_id UUID,
    is_active BOOLEAN,
    devices JSON,
    residents JSON,
    device_count BIGINT,
    resident_count BIGINT
) AS $$
DECLARE
    v_contact_tenant_id UUID;
BEGIN
    -- 获取家属联系人信息（家属通过 resident_contacts 表登录，不使用 users 表）
    SELECT rc.tenant_id
    INTO v_contact_tenant_id
    FROM resident_contacts rc
    WHERE rc.contact_id = p_contact_id
      AND rc.can_view_status = TRUE
      AND rc.is_active = TRUE;
    
    IF v_contact_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found, inactive, or no view permission: %', p_contact_id;
    END IF;
    
    -- 返回查询结果：家属只能看到关联住户的卡片（can_view_status = TRUE）
    -- 权限逻辑与住户相同：家属看到的内容和住户看到的内容相同
    -- 如果不开通家属账号（resident_contacts 表中没有关联），家属就不可见
    RETURN QUERY
    SELECT DISTINCT
        vcf.card_id,
        vcf.tenant_id,
        vcf.card_type,
        vcf.bed_id,
        vcf.location_id,
        vcf.card_name,
        vcf.card_address,
        vcf.primary_resident_id,
        vcf.is_active,
        vcf.devices,
        vcf.residents,
        vcf.device_count,
        vcf.resident_count
    FROM v_cards_full vcf
    JOIN resident_contacts rc ON rc.contact_id = p_contact_id
      AND rc.can_view_status = TRUE
      AND rc.is_active = TRUE
    JOIN residents r ON r.resident_id = rc.resident_id
      AND r.status = 'active'
      AND r.tenant_id = v_contact_tenant_id
    WHERE vcf.tenant_id = v_contact_tenant_id
      AND (
        -- 规则 1：ActiveBed 卡片 - 关联住户的床位（与住户权限相同）
        (
          vcf.card_type = 'ActiveBed'
          AND vcf.bed_id = r.bed_id
          AND vcf.primary_resident_id = r.resident_id
        )
        OR
        -- 规则 2：Location 卡片 - 关联住户所在的门牌号（与住户权限相同）
        -- 权限规则：
        --   - 该 location_id 下住户唯一且为该住户（单人居住）
        --   - 或者该 location_id 下的所有住户都使用相同的 family_tag（夫妻同住，可以互相查看）
        -- 注意：不考虑多人合租场景（不同 family_tag 的多人合租）
        (
          vcf.card_type = 'Location'
          AND vcf.location_id = r.location_id
          AND EXISTS (
            SELECT 1
            FROM card_residents cr
            WHERE cr.card_id = vcf.card_id
              AND cr.resident_id = r.resident_id
          )
          AND (
            -- 情况1：该 location 下只有1个住户（单人居住）
            (
              SELECT COUNT(*)
              FROM card_residents cr2
              WHERE cr2.card_id = vcf.card_id
            ) = 1
            OR
            -- 情况2：该 location 下的所有住户都使用相同的 family_tag（夫妻同住）
            (
              r.family_tag IS NOT NULL
              AND NOT EXISTS (
                SELECT 1
                FROM card_residents cr3
                JOIN residents r3 ON cr3.resident_id = r3.resident_id
                WHERE cr3.card_id = vcf.card_id
                  AND r3.status = 'active'
                  AND (r3.family_tag IS NULL OR r3.family_tag != r.family_tag)
              )
            )
          )
        )
      )
    ORDER BY vcf.card_type, vcf.card_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 视图：住户可见的卡片列表（供前端直接查询）
CREATE OR REPLACE VIEW v_resident_cards AS
SELECT 
    r.resident_id,
    vcf.*
FROM residents r
CROSS JOIN v_cards_full vcf
WHERE r.status = 'active'
  AND vcf.tenant_id = r.tenant_id
  AND (
    -- ActiveBed 卡片：住户自己的床位
    (
      vcf.card_type = 'ActiveBed'
      AND vcf.bed_id = r.bed_id
      AND vcf.primary_resident_id = r.resident_id
    )
    OR
    -- Location 卡片：住户所在的门牌号
    -- 权限规则：
    --   - 该 location_id 下住户唯一且为该住户（单人居住）
    --   - 或者该 location_id 下的所有住户都使用相同的 family_tag（夫妻同住，可以互相查看）
    -- 注意：不考虑多人合租场景（不同 family_tag 的多人合租）
    (
      vcf.card_type = 'Location'
      AND vcf.location_id = r.location_id
      AND EXISTS (
        SELECT 1
        FROM card_residents cr
        WHERE cr.card_id = vcf.card_id
          AND cr.resident_id = r.resident_id
      )
      AND (
        -- 情况1：该 location 下只有1个住户（单人居住）
        (
          SELECT COUNT(*)
          FROM card_residents cr2
          WHERE cr2.card_id = vcf.card_id
        ) = 1
        OR
        -- 情况2：该 location 下的所有住户都使用相同的 family_tag（夫妻同住）
        (
          r.family_tag IS NOT NULL
          AND NOT EXISTS (
            SELECT 1
            FROM card_residents cr3
            JOIN residents r3 ON cr3.resident_id = r3.resident_id
            WHERE cr3.card_id = vcf.card_id
              AND r3.status = 'active'
              AND (r3.family_tag IS NULL OR r3.family_tag != r.family_tag)
          )
        )
      )
    )
  );

-- 视图：家属可见的卡片列表（供前端直接查询）
-- 权限逻辑与住户相同：家属看到的内容和住户看到的内容相同
-- 如果不开通家属账号（resident_contacts 表中没有关联），家属就不可见
-- 注意：家属通过 resident_contacts 表登录，不使用 users 表
CREATE OR REPLACE VIEW v_family_cards AS
SELECT DISTINCT
    rc.contact_id,
    vcf.*
FROM resident_contacts rc
JOIN residents r ON r.resident_id = rc.resident_id
  AND r.status = 'active'
  AND r.tenant_id = rc.tenant_id
CROSS JOIN v_cards_full vcf
WHERE rc.can_view_status = TRUE
  AND rc.is_active = TRUE
  AND vcf.tenant_id = rc.tenant_id
  AND (
    -- 规则 1：ActiveBed 卡片 - 关联住户的床位（与住户权限相同）
    (
      vcf.card_type = 'ActiveBed'
      AND vcf.bed_id = r.bed_id
      AND vcf.primary_resident_id = r.resident_id
    )
    OR
    -- 规则 2：Location 卡片 - 关联住户所在的门牌号（与住户权限相同）
    -- 限制：该 location_id 下住户唯一且为该住户
    -- （多人情况下，location下的设备属于公共，不能让个人所见）
    (
      vcf.card_type = 'Location'
      AND vcf.location_id = r.location_id
      AND EXISTS (
        SELECT 1
        FROM card_residents cr
        WHERE cr.card_id = vcf.card_id
          AND cr.resident_id = r.resident_id
      )
      -- 确保该 location_id 下住户唯一且为该住户
      AND (
        SELECT COUNT(*)
        FROM card_residents cr2
        WHERE cr2.card_id = vcf.card_id
      ) = 1
    )
  );

-- 注释
COMMENT ON FUNCTION get_resident_cards(UUID) IS '根据住户ID获取可见的卡片列表（住户自己），只能看到自己的床位/门牌号卡片';
COMMENT ON FUNCTION get_family_cards(UUID) IS '根据家属联系人ID获取可见的卡片列表（家属），只能看到关联住户的卡片（can_view_status = TRUE）。注意：家属通过 resident_contacts 表登录，不使用 users 表';
COMMENT ON VIEW v_resident_cards IS '住户可见的卡片列表视图（需要应用层按resident_id过滤，或使用get_resident_cards函数）';
COMMENT ON VIEW v_family_cards IS '家属可见的卡片列表视图（需要应用层按contact_id过滤，或使用get_family_cards函数）。注意：家属通过 resident_contacts 表登录，不使用 users 表';

