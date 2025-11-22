-- 住户-护士关联表 (resident_caregivers)
-- 用途：
--   1) 表示哪些护理人员/staff 主要负责某位住户（护理分配关系）
--   2) 替代原始设计中 Resident 表里的 Caregiver1ID..15 等多列结构
--   3) 不存任何住户 PHI，仅存关联与角色信息
--   4） 如果不指定护理人员，默认使用location_id关联的警报通报组

CREATE TABLE IF NOT EXISTS resident_caregivers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,

    -- 护理人员账号（caregiver），来自 users 表，最多5个护理人员可同时护理一个住户
    caregiver_id1 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    caregiver_id2 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    caregiver_id3 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    caregiver_id4 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    caregiver_id5 UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- 护士组标签，如 "NightShift", "Group.A", "FallsExpert" 等
    caregivers_tags       JSONB,



    -- 约束：
    --   1) 同一住户 + 护理人员 + 角色 的组合唯一
    UNIQUE (tenant_id, resident_id, caregiver_id, caregiver_role)
);

CREATE INDEX IF NOT EXISTS idx_resident_caregivers_tenant_resident
    ON resident_caregivers(tenant_id, resident_id);

CREATE INDEX IF NOT EXISTS idx_resident_caregivers_staff
    ON resident_caregivers(tenant_id, caregiver_id);


