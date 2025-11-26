-- 位置表 (locations)
-- 对应权限表 Excel 中的 Location sheet

CREATE TABLE IF NOT EXISTS locations (
    -- Primary / SaaS
    location_id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,


    -- 位置标签：例如 "A 院区主楼"、"Spring 区域组SP"、"Denver-East  DVE"（用于分组、路由等）
    location_tag    VARCHAR(255),
    
    -- 位置名称：例如 "E203"、"201"、"Home-001"（便于护士记录的名字，可以重复，因为每组不同）
    -- 用于卡片显示和日常记录，同一租户内可以重复
    -- 注意：
    --   - Institutional 场景：房间名称（如 "E203"）
    --   - HomeCare 场景：逻辑名称（如 "Home-001"），真实地址存放在 resident_phi 表中
    location_name   VARCHAR(255) NOT NULL,

    -- ========== Institutional 场景地址字段（机构如 elder care）==========
    -- 机构场景使用以下字段标识位置：
    --   - building: 楼栋（如 "Building A"、"主楼"）
    --   - floor: 楼层（如 "1F"、"2F"）
    --   - area_id: 区域ID（如 "Area A"、"Memory Care Unit"）
    --   - door_number: 门牌号/房间号（如 "201"、"E203"）
    -- 注意：
    --   - 这些字段仅用于机构场景（location_type = 'Institutional'），不属于 PHI
    --   - 机构地址通常不需要城市、州省、邮编等完整地址信息
    --   - HomeCare 场景的所有地址信息（包含 PHI）必须存储在加密的 resident_phi 表中
    --   - locations 表不存储任何 PHI，符合 HIPAA 要求
    building        VARCHAR(50),    -- 楼栋（机构场景）
    floor           VARCHAR(50),    -- 楼层（机构场景）
    area_id         VARCHAR(100),   -- 区域ID（机构场景，如 "Area A"、"Memory Care Unit"）
    door_number     VARCHAR(255) NOT NULL,  -- 门牌号/房间号（机构场景：如 "201"、"E203"）
    

    layout_config JSONB,



    -- Address Structure (optional)
    
    -- Institutional / HomeCare 等场景类型（具体枚举由应用层控制）
    location_type   VARCHAR(20)  NOT NULL,

    -- 主要关联住户（用于 HomeCare 和 Institutional 场景）
    -- 注意：
    --   - HomeCare 场景：一个 location 可以对应一个或两个住户（单人居住或夫妻同住）
    --     此字段关联主要住户（通常是第一个入住的住户），第二个住户（夫妻）通过 residents.location_id 关联
    --     必须设置此字段（绑定用户时，必须处理该值不为空）
    --   - Institutional 场景：单间或夫妻套房（is_multi_person_room = FALSE）必须设置此字段（第一位入住者）
    --     用于 Location 卡片名称显示，优先使用第一位入住者的 LastName
    --     必须设置此字段（绑定用户时，必须处理该值不为空）
    --   - 多人房间（is_multi_person_room = TRUE）或公共空间（is_public_space = TRUE）：此字段可为 NULL
    --   - 此字段用于统一地址管理，录入住户时可在地址管理中选择关联住户
    --   - 设备/床位/住户都通过 location_id 关联，保证统一管理
    --   - 夫妻同住：两个住户使用相同的 family_tag，可以互相查看 Location 卡片
    primary_resident_id UUID REFERENCES residents(resident_id) ON DELETE SET NULL,

    -- 公共空间：用于标识公共空间，如大厅、走廊、电梯等
    -- 注意：HomeCare 场景默认为 FALSE（个人住所），无需选择
    is_public_space BOOLEAN NOT NULL DEFAULT FALSE, -- 是否为公共空间
   
    -- 多人房间：多人共享，设备属于公共，不能让个人所见（仅用于 Institutional 场景）
    -- 注意：
    --   - HomeCare 场景：
    --     * 始终为 FALSE（默认），不考虑多人合租场景
    --     * 单人居住或夫妻同住时，都使用 FALSE（夫妻通过相同 family_tag 可以互相查看）
    --   - Institutional 场景：
    --     * 单人房间：is_multi_person_room = FALSE
    --     * 多人房间：is_multi_person_room = TRUE（设备属于公共，不能让个人所见）
    is_multi_person_room BOOLEAN NOT NULL DEFAULT FALSE, 

    -- Routing & Status
    timezone        VARCHAR(50)  NOT NULL,      -- IANA 格式，例如 "America/Los_Angeles"
    
    -- 警报通报组：用于指定告警接收者（告警路由和权限控制）
    --   alert_user_ids: 具体指定的用户ID列表（直接指定接收者）
    --   alert_tags: 标签组，用于匹配 users.tags（通过标签匹配接收者）
    -- 查询规则：
    --   1) 如果指定了 alert_user_ids，直接包含这些用户
    --   2) 如果指定了 alert_tags，匹配 users.tags 中包含这些标签的用户
    --   3) 两者可以同时使用，取并集
    -- 注意：在绑定用户后，alert_user_ids 和 alert_tags 不能同时为空,至少指定一个，公共区域必须指定
    alert_user_ids  UUID[],                     -- 警报接收者用户ID列表（直接指定）
    alert_tags      VARCHAR[],                  -- 警报接收者标签组（匹配 users.tags）
    
    --房间是否启用监控，默认启用
    --如果房间没有住户，则不启用监控，由应用层控制，且不能删除该房间，且同步把绑定的设备 is_monitoring_enabled 设置为 FALSE
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,

    -- 复合主键：LocationID + TenantID
    PRIMARY KEY (location_id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_locations_tenant ON locations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_locations_door_number ON locations(tenant_id, door_number);
CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(tenant_id, location_name);
CREATE INDEX IF NOT EXISTS idx_locations_building ON locations(tenant_id, building) WHERE building IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_floor ON locations(tenant_id, floor) WHERE floor IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_area_id ON locations(tenant_id, area_id) WHERE area_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_tag ON locations(tenant_id, location_tag) WHERE location_tag IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_alert_user_ids ON locations USING GIN (alert_user_ids) WHERE alert_user_ids IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_alert_tags ON locations USING GIN (alert_tags) WHERE alert_tags IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_primary_resident ON locations(primary_resident_id) WHERE primary_resident_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_locations_public_space ON locations(tenant_id, is_public_space) WHERE is_public_space = TRUE;
CREATE INDEX IF NOT EXISTS idx_locations_multi_person ON locations(tenant_id, is_multi_person_room) WHERE is_multi_person_room = TRUE;

-- 唯一性约束：同一租户内，location_tag + location_name 组合唯一
-- 如果 location_tag 不为 NULL：使用 (tenant_id, location_tag, location_name) 唯一
-- 如果 location_tag 为 NULL：使用 (tenant_id, location_name) 唯一
CREATE UNIQUE INDEX idx_locations_unique_with_tag 
    ON locations(tenant_id, location_tag, location_name) 
    WHERE location_tag IS NOT NULL;
CREATE UNIQUE INDEX idx_locations_unique_without_tag 
    ON locations(tenant_id, location_name) 
    WHERE location_tag IS NULL;

-- 额外唯一约束：支持其他表通过 location_id 建立外键
ALTER TABLE locations
    ADD CONSTRAINT uq_locations_location_id UNIQUE (location_id);


