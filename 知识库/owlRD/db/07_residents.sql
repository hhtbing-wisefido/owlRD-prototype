-- 住户表 (residents) - 完全匿名化，无 PII 存储

CREATE TABLE IF NOT EXISTS residents (
    resident_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- UUID 是随机生成的技术标识符，仅用于系统内部关联

    tenant_id    UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- ========== 外部 HIS（医院信息系统）同步字段 ==========
    -- 用于与外部 HIS 系统进行数据关联和同步
    -- 注意：这些字段仅用于系统间关联，不用于业务展示，符合匿名化要求
    -- 注意：包含 PII 的字段（如真实姓名、日期、元数据）已移至 resident_phi 表
    HIS_resident_id VARCHAR(100),              -- HIS 系统中的住户 ID（外部系统标识，非 PII）
    HIS_resident_bed_id VARCHAR(100),           -- HIS 系统中的床位 ID（外部系统标识，非 PII）
    HIS_resident_status VARCHAR(100),           -- HIS 系统中的住户状态（非 PII）

    -- 住户账号（机构内部唯一标识，不包含姓名，可用于绑定 Portal / 家属授权等）
    resident_account VARCHAR(100) NOT NULL,

    -- 虚拟姓名字段（last_name用匿名代称填充，不存储真实姓名，first_name可为空）
    first_name   VARCHAR(100),
    last_name    VARCHAR(100) NOT NULL,

    -- 匿名代称：用于展示和查询，与 last_name 相同
    anonymous_name VARCHAR(100) NOT NULL GENERATED ALWAYS AS (last_name) STORED,

    -- 机构或在家模式：机构模式或在家模式
    is_institutional BOOLEAN NOT NULL DEFAULT FALSE,
    -- is_homecare BOOLEAN NOT NULL DEFAULT FALSE,



    -- 位置信息 / 住院信息（不构成 PII）
    location_id  UUID REFERENCES locations(location_id) ON DELETE SET NULL, -- 当前地址 / 门牌号 (FK → locations)
    bed_id       UUID REFERENCES beds(bed_id) ON DELETE SET NULL,          -- 当前床位（必须唯一，其他设备可继续绑定 Location/Room）

    admission_date DATE NOT NULL,  -- 入住日期 / 服务开始日期

    status       VARCHAR(50) DEFAULT 'active',  -- active, discharged, transferred
    metadata     JSONB,  -- 仅包含非 PII 信息

    -- 登录/重置用的联系方式哈希（可选）：推荐使用 SHA-256 等单向哈希，后端校验
    -- 用法示例：
    --   - 住户在前端输入手机号/邮箱 → 后端计算 hash(phone/email) → 与此处字段比对
    --   - 匹配成功后，可向用户刚刚输入的手机号/邮箱发送一次性验证码或重置链接
    phone_hash   BYTEA,
    email_hash   BYTEA,


    -- 家庭标签（family_tag）：用于标识同一家庭的成员
    -- 同一 family_tag 下的住户可以互相查看 Location 卡片（当同一 location_id 下有多个住户时）
    -- 例如：夫妻同住一个门牌号，可以设置相同的 family_tag，互相查看状态
    family_tag   VARCHAR(100),  -- 家庭标识符（同一家庭的成员使用相同的 family_tag）
    -- 共同Family-Member的账号,必须由管理员在创建
    family_member_account_1 VARCHAR(100) ,


    --增加一个字段，是否允许家属查看状态
    can_view_status BOOLEAN NOT NULL DEFAULT TRUE,

    -- 同一租户内 HIS_resident_id 唯一（用于关联外部系统）
    UNIQUE(tenant_id, HIS_resident_id) WHERE HIS_resident_id IS NOT NULL,

    -- 同一租户内住户账号唯一（内部标识，用于授权，不包含 PII）
    UNIQUE(tenant_id, resident_account),

    -- 同一租户内匿名代称唯一（避免重名）
    UNIQUE(tenant_id, last_name),

    -- 同一床位在同一时间仅允许一个活跃住户
    UNIQUE(tenant_id, bed_id)
        WHERE status = 'active'
);

CREATE INDEX IF NOT EXISTS idx_residents_tenant_id ON residents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_residents_bed_id ON residents(bed_id);
CREATE INDEX IF NOT EXISTS idx_residents_last_name ON residents(tenant_id, last_name);
CREATE INDEX IF NOT EXISTS idx_residents_anonymous_name ON residents(tenant_id, anonymous_name);
CREATE INDEX IF NOT EXISTS idx_residents_status ON residents(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_residents_his_id ON residents(tenant_id, HIS_resident_id) WHERE HIS_resident_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_residents_his_bed_id ON residents(tenant_id, HIS_resident_bed_id) WHERE HIS_resident_bed_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_residents_family_tag ON residents(tenant_id, location_id, family_tag) WHERE family_tag IS NOT NULL;

-- 匿名代称分配表（anonymous_name_pool）

CREATE TABLE IF NOT EXISTS anonymous_name_pool (
    name_id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    anonymous_name          VARCHAR(100) NOT NULL,
    category                VARCHAR(50)  NOT NULL,  -- profession, character, animal, item
    is_assigned             BOOLEAN      DEFAULT false,
    assigned_to_resident_id UUID REFERENCES residents(resident_id) ON DELETE SET NULL,
    assigned_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ  DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(tenant_id, anonymous_name)
);

CREATE INDEX IF NOT EXISTS idx_name_pool_tenant
    ON anonymous_name_pool(tenant_id);

CREATE INDEX IF NOT EXISTS idx_name_pool_category
    ON anonymous_name_pool(tenant_id, category, is_assigned);

CREATE INDEX IF NOT EXISTS idx_name_pool_assigned
    ON anonymous_name_pool(assigned_to_resident_id)
    WHERE is_assigned = true;


