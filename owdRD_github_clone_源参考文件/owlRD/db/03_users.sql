-- 用户表 (users) - 租户内登录账号，由各租户自行维护

CREATE TABLE IF NOT EXISTS users (
    user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 所属机构（租户）：账号由各租户在自己的作用域内创建和管理
    tenant_id     UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- 内部账号（可选，用作显示名或内部标识，不必是真实姓名）
    username      VARCHAR(255),

    -- 登录凭证 & 联系方式：邮箱 / 手机号，用于登录和双因子认证
    -- 注意：同时存储明文和哈希，明文用于工作联系，哈希用于统一登录匹配（与 residents 表一致）
    email         VARCHAR(255),
    phone         VARCHAR(50),
    
    -- 登录/重置用的联系方式哈希（推荐使用 SHA-256 等单向哈希，后端校验）
    -- 用途：
    --   1) 统一登录流程：users 和 residents 都可以用 email/phone 登录，通过 hash 匹配
    --   2) 降低 PII 风险：即使明文字段泄露，hash 字段仍可用于验证
    --   3) 与 residents 表设计一致：residents 只存 hash，users 同时存明文和 hash
    -- 用法示例：
    --   - 用户在前端输入手机号/邮箱 → 后端计算 hash(phone/email) → 与 users/residents 表的 hash 字段比对
    --   - 匹配成功后，可向用户刚刚输入的手机号/邮箱发送一次性验证码或重置链接
    email_hash    BYTEA,
    phone_hash    BYTEA,

    -- 密码哈希（可空）：建议使用应用层计算的 bcrypt/argon2 哈希，不存明文密码
    password_hash BYTEA,

    -- PIN 码哈希（可空）：仅存哈希，不存明文 PIN
    pin_hash      BYTEA,

    -- 在该机构内的角色：如 Director / NurseManager / Nurse / ITSupport /Caregiver/SocialWorker/等
    -- 实际可选值在 roles 表中配置，这里建议与 roles.role_code 对应
    role          VARCHAR(50) NOT NULL,

    -- 账号状态：active（在职/可登录）、disabled（停用）、left（离职，保留审计记录）
    status        VARCHAR(50) DEFAULT 'active',

    -- 告警接收配置（通常用于管理层：Director / NurseManager / Admin 等）
    --   alert_levels：用户愿意接收的告警级别集合，如 ["L1","L2","L3"]；为空表示使用系统默认
    --   alert_channels：用户愿意接收的通道，如 ["APP","EMAIL"]；短信等需在应用层结合策略控制
    --   alert_scope：接收范围，例如 'ALL'（全机构）、'LOCATION-TAG'（按地点标签）、'ASSIGNED_ONLY'（仅自己负责的住户）
    alert_levels   VARCHAR[],
    alert_channels VARCHAR[],
    alert_scope    VARCHAR(20),

    last_login_at TIMESTAMPTZ,  -- 业务字段：最后登录时间（用于会话管理）

    -- 员工标签：如 ["NightShift", "Group.A", "FallsExpert"]
    tags          JSONB,

    -- 约束：用户名在租户内唯一；email / phone 可重复（由应用层在登录时处理多匹配场景）
    UNIQUE(tenant_id, username)
);

CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(tenant_id, role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_users_email_hash ON users(email_hash) WHERE email_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_phone_hash ON users(phone_hash) WHERE phone_hash IS NOT NULL;


