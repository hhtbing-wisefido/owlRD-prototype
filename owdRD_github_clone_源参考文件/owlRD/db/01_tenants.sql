-- 租户表 (tenants)
-- 业务规则：
--   1) 跨租户登录支持：同一个 email/phone 可以在多个租户下创建不同的用户记录（users 表）
--   2) 登录流程（前端控制）：
--        - 用户输入 user_account/email/phone
--        - 后端计算 hash(phone/email)，统一查询 users 和 residents 表：
--          SELECT * FROM users WHERE email_hash = ? OR phone_hash = ?
--          UNION ALL
--          SELECT * FROM residents WHERE email_hash = ? OR phone_hash = ?
--        - 如果匹配到多个机构/身份，前端展示选择界面
--        - 用户选择：身份（角色，如客户/staff）+ 机构名（tenant_name）
--        - 如果只有一个机构/身份，自动进入，无需选择
--        - 注意：users 表同时存明文和 hash，residents 表只存 hash（降低 PII 风险）
--   3) 设计原则：平台不管理跨租户关联，完全由用户登录时自行选择，避免客户疑问

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_name VARCHAR(255) NOT NULL,
    domain      VARCHAR(255) UNIQUE,  -- 租户域名
    status      VARCHAR(50)  DEFAULT 'active',  -- active, suspended, deleted
    created_at  TIMESTAMPTZ  DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ  DEFAULT CURRENT_TIMESTAMP,
    metadata    JSONB        -- 扩展配置信息
);

CREATE INDEX IF NOT EXISTS idx_tenants_domain ON tenants(domain);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);


