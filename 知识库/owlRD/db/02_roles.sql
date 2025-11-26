-- 角色表 (roles) - 由各租户自行扩展角色列表

CREATE TABLE IF NOT EXISTS roles (
    role_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id    UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- 角色编码：用于程序/DDL 中引用，如 Director / NurseManager / Nurse / ITSupport/Caregiver/SocialWorker/等
    role_code    VARCHAR(50) NOT NULL,

    -- 角色展示名称：用于前端显示，可多语言
    display_name VARCHAR(100) NOT NULL,

    -- 描述：该角色的大致职责说明
    description  TEXT,

    -- 是否系统预置：true 表示平台内置角色，租户不可删除，仅可启用/停用
    is_system    BOOLEAN DEFAULT FALSE,

    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- 同一租户内 role_code 唯一
    UNIQUE(tenant_id, role_code)
);

CREATE INDEX IF NOT EXISTS idx_roles_tenant_id ON roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_roles_active ON roles(tenant_id, is_active);


