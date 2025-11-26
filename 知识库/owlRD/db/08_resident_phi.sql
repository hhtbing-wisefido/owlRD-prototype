-- 住户 PHI 表 (resident_phi) - 存放可选的个人健康信息，物理上与 residents 分离
-- 注意：仅在需要存储 PHI 的部署中启用，默认前端不暴露这些字段
-- DB层面加密存储，不存储明文


CREATE TABLE IF NOT EXISTS resident_phi (
    phi_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,

    -- Basic PHI
    first_name      VARCHAR(100),        -- 名字 (Given Name)，可空
    last_name       VARCHAR(100),        -- 姓氏 (Surname)，可空
    gender          VARCHAR(10),         -- 性别：Male/Female/Other/Unknown 等
    date_of_birth   DATE,                -- 出生日期
    resident_phone  VARCHAR(25),         -- 住户个人电话
    resident_email  VARCHAR(255),        -- 住户个人邮箱

    -- Biometric PHI（身高/体重）
    weight_lb   DECIMAL(5, 2),           -- 体重 (lb)
    height_ft   DECIMAL(5, 2),           -- 身高：feet
    height_in   DECIMAL(5, 2),           -- 身高：inches

    -- Functional Mobility（功能性活动能力）
    mobility_level INTEGER,              -- 0: 无行动能力 ~ 5: 完全独立（可选，视业务是否视为 PHI）

    -- Functional Health（功能性健康状态）
    tremor_status    VARCHAR(20),        -- 颤抖状态：None/Mild/Severe
    mobility_aid     VARCHAR(20),        -- 行走辅助：Cane/Wheelchair/None
    adl_assistance   VARCHAR(20),        -- 日常活动协助：Independent/NeedsHelp
    comm_status      VARCHAR(20),        -- 沟通状态：Normal/SpeechDifficulty

    -- Chronic Conditions / Medical History（老年常见慢病与病史）
    -- 说明：
    --   1) 这些字段均为可选，仅在明确启用 PHI 场景下使用（如 ToC 增值服务 / 机构选择承担 HIPAA 成本）
    --   2) 对应常见慢病，可在规则引擎中用于风险分层与告警阈值调整
    has_hypertension    BOOLEAN,         -- 高血压（Hypertension）
    has_hyperlipaemia   BOOLEAN,         -- 高血脂（Hyperlipaemia）
    has_hyperglycaemia  BOOLEAN,         -- 高血糖 / 糖尿病（Hyperglycaemia / Diabetes）
    has_stroke_history  BOOLEAN,         -- 既往脑卒中史（Stroke）
    has_paralysis       BOOLEAN,         -- 肢体瘫痪/偏瘫（Paralysis）
    has_alzheimer       BOOLEAN,         -- 阿尔茨海默病 / 痴呆（Alzheimer's disease / Dementia）

    medical_history     TEXT,            -- 其他病史说明（自由文本或半结构化描述）

    -- ========== 外部 HIS（医院信息系统）同步字段（包含 PII）==========
    -- 用于与外部 HIS 系统进行数据关联和同步
    -- 注意：这些字段包含 PII 或敏感信息，存储在 PHI 表中以符合 HIPAA 要求
    HIS_resident_name VARCHAR(100),             -- HIS 系统中的住户姓名（真实姓名，PII）
    HIS_resident_admission_date DATE,            -- HIS 系统中的入院日期（可能识别个人）
    HIS_resident_discharge_date DATE,           -- HIS 系统中的出院日期（可能识别个人）
    HIS_resident_metadata JSONB,                -- HIS 系统中的其他元数据（可能包含 PII）

    -- ========== 家庭地址信息（PHI，仅用于 HomeCare 场景）==========
    -- 注意：
    --   1) 机构场景（Institutional）的地址信息存储在 locations 表中（building, floor, area_id, door_number），不属于 PHI
    --   2) HomeCare 场景的所有地址信息（包含 PHI）必须存储在此表中（加密），符合 HIPAA 要求
    --   3) locations 表不存储任何 HomeCare 场景的地址信息（如 city, state_province, postal_code, latitude, longitude）
    --      - 这样可以消除 HIPAA 风险（locations 表不加密）
    --      - 所有 PHI 都存储在加密的 resident_phi 表中
    --   4) 设计原则：
    --      - HomeCare 场景的真实地址存储在 resident_phi 表中（与姓名关联，加密存储）
    --      - locations 表仅存储逻辑位置信息（location_name, location_tag），不存储任何 PHI
    --      - 通过加密存储和应用层访问控制保护 PHI
    --      - 符合 HIPAA 最小必要原则：所有 PHI 集中存储在加密表中
    --
    -- 关联方式：
    --   1) residents.location_id → locations（获取逻辑位置信息，如 location_name, location_tag，不包含真实地址和姓名）
    --   2) residents.resident_id → resident_phi（获取姓名和真实家庭地址，需要权限和加密）
    --   3) 查询示例（姓名+地址，需要权限，从加密表获取）：
    --      SELECT rp.first_name, rp.last_name, rp.home_address_street, rp.home_address_city
    --      FROM residents r
    --      JOIN resident_phi rp ON r.resident_id = rp.resident_id
    --      WHERE r.resident_id = ? AND r.location_id IN (
    --        SELECT location_id FROM locations WHERE location_type = 'HomeCare'
    --      );
    --   4) 查询示例（仅逻辑位置，无姓名和真实地址）：
    --      SELECT l.location_name, l.location_tag
    --      FROM residents r
    --      JOIN locations l ON r.location_id = l.location_id
    --      WHERE r.resident_id = ?;
    home_address_street VARCHAR(255),           -- 街道地址（可选冗余）
    home_address_city VARCHAR(100),             -- 城市（可选冗余）
    home_address_state VARCHAR(50),             -- 州/省（可选冗余）
    home_address_postal_code VARCHAR(20),        -- 邮编（可选冗余）
    plus_code VARCHAR(32),                      -- Google Plus Code 或类似全球编码（真实值）
    

    -- Emergency Contacts / Caregivers 建议使用独立表，避免此表过宽

    -- 每个住户在一个租户下最多一条 PHI 记录
    UNIQUE(tenant_id, resident_id)
);

CREATE INDEX IF NOT EXISTS idx_resident_phi_tenant ON resident_phi(tenant_id);
CREATE INDEX IF NOT EXISTS idx_resident_phi_resident ON resident_phi(resident_id);


