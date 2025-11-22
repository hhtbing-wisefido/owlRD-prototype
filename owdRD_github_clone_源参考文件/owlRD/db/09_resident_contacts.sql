-- 住户紧急联系人 / 家属账号表 (resident_contacts)
-- 说明：
--   1) 为避免不必要的 PHI 暴露，姓名/电话/邮箱均为可选字段
--   2) 默认前端不开放姓名/电话/邮箱，仅在 ToC / 非 HIPAA 场景（如 tenant_id = 0）下，由用户自愿填写
--   3) 家属/联系人通过 contact_resident_id 关联到 residents 表（家属本身也是住户）
--   4) 默认开放的槽位为 A/B/C：供住户自行开启/关闭，并需显式选择 relationship / can_view_status / can_receive_alert
--   5) 槽位 D/E 为扩展账号，一般由机构管理员创建（例如子女同时查看 2 位老人的状态）
--   6) 登录方式：家属通过 residents 表的账号登录；手机号/邮箱仅用于验证和找回密码，
--      系统只保存 phone_hash/email_hash（加密校验值），不保存明文手机号/邮箱

CREATE TABLE IF NOT EXISTS resident_contacts (
    contact_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),

 
    tenant_id    UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    resident_id  UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    slot         VARCHAR(1) NOT NULL,  -- 'A','B','C','D','E'

    -- 关联的家属/联系人（可选）：指向 residents.resident_id（家属本身也是住户）
    -- 子女可同时查看 family_member 组里的父母
    contact_resident_id UUID REFERENCES residents(resident_id) ON DELETE SET NULL,

    -- 授权设置：是否允许访问住户状态 / 接收告警
    can_view_status   BOOLEAN NOT NULL DEFAULT TRUE,
    can_receive_alert BOOLEAN NOT NULL DEFAULT TRUE,

    -- 关系（非必填）：如 Child/Spouse/Friend/Caregiver
    relationship      VARCHAR(50),

    -- 可选的 PHI（姓名 / 联系方式），仅在特定场景下由用户自愿填写
    contact_first_name VARCHAR(100),
    contact_last_name  VARCHAR(100),
    contact_phone      VARCHAR(25),
    contact_email      VARCHAR(255),
    contact_sms        BOOLEAN DEFAULT FALSE,  -- 是否接收短信

    -- 登录/重置用的联系方式哈希（推荐使用 SHA-256 等单向哈希，后端校验）
    -- 用法示例：
    --   - 住户在前端输入手机号/邮箱 → 后端计算 hash(phone/email) → 与此处字段比对
    --   - 匹配成功后，可向用户刚刚输入的手机号/邮箱发送一次性验证码或重置链接
    phone_hash   BYTEA,
    email_hash   BYTEA,

    is_active     BOOLEAN NOT NULL DEFAULT TRUE,

    -- 约束：
    --   1) 同一住户在同一槽位（A/B/C/D/E）最多一个联系人
    --   2) 一个 contact_resident_id 可以绑定多个 resident（例如子女看两个老人）
    UNIQUE (tenant_id, resident_id, slot)
);

CREATE INDEX IF NOT EXISTS idx_resident_contacts_tenant_resident
    ON resident_contacts(tenant_id, resident_id);

CREATE INDEX IF NOT EXISTS idx_resident_contacts_contact_resident
    ON resident_contacts(contact_resident_id) WHERE contact_resident_id IS NOT NULL;


