-- 床位表 (beds)
-- 对应权限表中的 Bed 定义
-- 业务规则：
--   1) Bed 必须绑定到 Room（RoomID NOT NULL），绑定路径：Location → Room → Bed
--   2) 当客户从 Default Room 迁移到细分 Room 时，应先在业务层迁移 Bed，再限制 Default Room 接受新绑定
--   3) 若夫妻同床但使用 2 套独立监测设备，可在同一物理床上建 2 个护理床位（BedA/BedB），分别绑定各自设备和住户
--      若仅有 1 套监测设备，则视为 1 个护理床位（单一 Bed），避免多个 active 住户共享同一 BedID

CREATE TABLE IF NOT EXISTS beds (
    -- Primary / SaaS
    bed_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- Structure
    room_id     UUID NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
    location_id UUID NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE, -- 冗余，加速查询

    -- Configuration
    -- 床位名称：建议使用 A/B/C... 或 Bed1/Bed2 等技术编号，前端应提示“示例：A, B, C，不要填写住户姓名”
    bed_name           VARCHAR(50) NOT NULL,
    -- 床位类型：由应用层根据绑定状态计算，不在 DB 中自动推导
    -- 规则示例：
    --   ActiveBed    = 同时绑定 Resident（有人） + 至少一个监控设备（如雷达/睡眠板）
    --                  + 设备 monitoring_enabled = TRUE（监护已激活）
    --   NonActiveBed = 其他情况（仅有人 / 仅设备 / 暂未启用监控 / 监护未激活）
    -- 注意：住户出院后，设备应进入 Dormant 模式（monitoring_enabled = FALSE），
    --       此时床位类型应更新为 NonActiveBed，避免监护义务和生理数据授权风险
    bed_type           VARCHAR(20) NOT NULL,  -- ActiveBed / NonActiveBed
    -- 床垫材质 / 类型：可选，用于压力床垫等需要精细配置的场景
    mattress_material  VARCHAR(50),
    -- 床垫厚度：在部分场景需要（如压力床垫），否则可为空
    mattress_thickness VARCHAR(20),           -- 可选：'< 7in', '7-10in', '11-14in', '14in+'

    -- Resident Link
    resident_id UUID REFERENCES residents(resident_id) ON DELETE SET NULL,

    -- 绑定的激活监护设备数量（自动维护）
    -- 规则：只计算 monitoring_enabled = TRUE 的监控设备（Radar、SleepPad）
    -- 当设备绑定/解绑床位，或 monitoring_enabled 状态变化时，自动更新此计数器
    bound_device_count INTEGER NOT NULL DEFAULT 0,
    
    -- 床位是否激活（计算字段，基于 bound_device_count）
    -- bound_device_count > 0 时，is_active = TRUE
    is_active BOOLEAN GENERATED ALWAYS AS (bound_device_count > 0) STORED,

    -- 复合唯一性：同一租户 + 房间内，床名唯一
    UNIQUE(tenant_id, room_id, bed_name)
);

CREATE INDEX IF NOT EXISTS idx_beds_tenant_id ON beds(tenant_id);
CREATE INDEX IF NOT EXISTS idx_beds_room_id ON beds(tenant_id, room_id);
CREATE INDEX IF NOT EXISTS idx_beds_location_id ON beds(tenant_id, location_id);
CREATE INDEX IF NOT EXISTS idx_beds_resident_id ON beds(tenant_id, resident_id);
CREATE INDEX IF NOT EXISTS idx_beds_device_count ON beds(tenant_id, bound_device_count) WHERE bound_device_count > 0;
CREATE INDEX IF NOT EXISTS idx_beds_active ON beds(tenant_id, is_active) WHERE is_active = TRUE;

-- ============================================================================
-- 触发器：自动维护 beds.bound_device_count
-- ============================================================================
-- 功能：当设备绑定/解绑床位，或 monitoring_enabled 状态变化时，自动更新床位设备计数器
-- 规则：只计算 monitoring_enabled = TRUE 的监控设备（Radar、SleepPad）

-- 函数：更新床位的设备计数器
CREATE OR REPLACE FUNCTION update_bed_device_count()
RETURNS TRIGGER AS $$
DECLARE
    v_bed_id UUID;
BEGIN
    -- 确定需要更新的床位ID
    IF TG_OP = 'DELETE' THEN
        v_bed_id := OLD.bound_bed_id;
    ELSIF TG_OP = 'INSERT' THEN
        v_bed_id := NEW.bound_bed_id;
    ELSIF TG_OP = 'UPDATE' THEN
        -- UPDATE 时，可能需要更新两个床位（旧床位和新床位）
        -- 先更新旧床位（如果存在且与新床位不同）
        IF OLD.bound_bed_id IS NOT NULL AND OLD.bound_bed_id IS DISTINCT FROM NEW.bound_bed_id THEN
            UPDATE beds
            SET bound_device_count = (
                SELECT COUNT(*)
                FROM devices d
                WHERE d.bound_bed_id = OLD.bound_bed_id
                  AND d.installed = TRUE
                  AND d.monitoring_enabled = TRUE
                  AND d.device_type IN ('Radar', 'SleepPad')
            )
            WHERE bed_id = OLD.bound_bed_id;
        END IF;
        -- 再更新新床位
        v_bed_id := NEW.bound_bed_id;
    END IF;
    
    -- 更新床位设备计数器
    IF v_bed_id IS NOT NULL THEN
        UPDATE beds
        SET bound_device_count = (
            SELECT COUNT(*)
            FROM devices d
            WHERE d.bound_bed_id = v_bed_id
              AND d.installed = TRUE
              AND d.monitoring_enabled = TRUE
              AND d.device_type IN ('Radar', 'SleepPad')
        )
        WHERE bed_id = v_bed_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 触发器：设备绑定/解绑床位时，更新床位设备计数器
CREATE TRIGGER trigger_update_bed_device_count_on_bind
    AFTER INSERT OR UPDATE OF bound_bed_id OR DELETE
    ON devices
    FOR EACH ROW
    WHEN (
        -- 只处理监控设备（Radar、SleepPad）
        (COALESCE(NEW.device_type, OLD.device_type) IN ('Radar', 'SleepPad'))
        -- 只处理激活监护的设备（INSERT/UPDATE 时检查 NEW，DELETE 时检查 OLD）
        AND (
            (NEW.monitoring_enabled = TRUE AND NEW.installed = TRUE)
            OR (OLD.monitoring_enabled = TRUE AND OLD.installed = TRUE)
        )
    )
    EXECUTE FUNCTION update_bed_device_count();

-- 触发器：设备 monitoring_enabled 状态变化时，更新床位设备计数器
CREATE TRIGGER trigger_update_bed_device_count_on_monitoring
    AFTER UPDATE OF monitoring_enabled
    ON devices
    FOR EACH ROW
    WHEN (
        -- 只处理监控设备（Radar、SleepPad）
        NEW.device_type IN ('Radar', 'SleepPad')
        -- 设备绑定到床位
        AND (NEW.bound_bed_id IS NOT NULL OR OLD.bound_bed_id IS NOT NULL)
        -- monitoring_enabled 状态发生变化
        AND (NEW.monitoring_enabled IS DISTINCT FROM OLD.monitoring_enabled)
        -- 设备已安装
        AND NEW.installed = TRUE
    )
    EXECUTE FUNCTION update_bed_device_count();

-- 触发器：设备 installed 状态变化时，更新床位设备计数器
CREATE TRIGGER trigger_update_bed_device_count_on_installed
    AFTER UPDATE OF installed
    ON devices
    FOR EACH ROW
    WHEN (
        -- 只处理监控设备（Radar、SleepPad）
        NEW.device_type IN ('Radar', 'SleepPad')
        -- 设备绑定到床位
        AND (NEW.bound_bed_id IS NOT NULL OR OLD.bound_bed_id IS NOT NULL)
        -- installed 状态发生变化
        AND (NEW.installed IS DISTINCT FROM OLD.installed)
        -- 监护已激活
        AND NEW.monitoring_enabled = TRUE
    )
    EXECUTE FUNCTION update_bed_device_count();

-- 函数：初始化所有床位的设备计数器（用于数据迁移或修复）
CREATE OR REPLACE FUNCTION initialize_bed_device_count()
RETURNS void AS $$
BEGIN
    UPDATE beds b
    SET bound_device_count = (
        SELECT COUNT(*)
        FROM devices d
        WHERE d.bound_bed_id = b.bed_id
          AND d.installed = TRUE
          AND d.monitoring_enabled = TRUE
          AND d.device_type IN ('Radar', 'SleepPad')
    );
END;
$$ LANGUAGE plpgsql;

-- 注释
COMMENT ON COLUMN beds.bound_device_count IS '绑定的激活监护设备数量（自动维护），只计算 monitoring_enabled=TRUE 的监控设备（Radar、SleepPad）';
COMMENT ON COLUMN beds.is_active IS '床位是否激活（计算字段），bound_device_count > 0 时自动为 TRUE';
COMMENT ON FUNCTION update_bed_device_count() IS '更新床位设备计数器的触发器函数，当设备绑定/解绑床位或 monitoring_enabled 状态变化时自动调用';
COMMENT ON FUNCTION initialize_bed_device_count() IS '初始化所有床位的设备计数器（用于数据迁移或修复），执行一次即可初始化所有床位的 bound_device_count';


