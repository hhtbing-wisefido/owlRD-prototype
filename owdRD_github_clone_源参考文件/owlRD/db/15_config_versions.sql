-- 统一配置历史表 (config_versions)
-- 用途：
--   1) 按时间保存所有配置类型的快照，用于历史回放和审计
--   2) 支持的配置类型：
--        - 'room_layout': 房间布局（关联 room_id）
--        - 'device_config': 设备技术配置（关联 device_id）
--        - 'cloud_alert_policy': 云端告警策略（关联 policy_id，scope_type/scope_id）
--        - 'iot_monitor_alert': IoT 设备报警配置（关联 alert_config_id，device_id）
--        - 'device_installation': 设备安装/绑定（关联 device_id，location_id/room_id/bed_id）
--   3) 当前生效配置同时写入对应的主表，方便实时查询
--   4) 支持回放：查询某个时间点的任意配置，用于分析历史数据

CREATE TABLE IF NOT EXISTS config_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- 配置类型：用于区分不同的配置实体
    config_type VARCHAR(50) NOT NULL,  -- 'room_layout' / 'device_config' / 'cloud_alert_policy' / 'iot_monitor_alert' / 'device_installation'

    -- 实体关联：
    --   - room_layout: entity_id = room_id
    --   - device_config: entity_id = device_id
    --   - cloud_alert_policy: entity_id = policy_id
    --   - iot_monitor_alert: entity_id = alert_config_id
    --   - device_installation: entity_id = device_id
    entity_id UUID NOT NULL,

    -- 关联到当前实体表的ID（可选，用于已删除的实体）
    --   - room_layout: current_entity_id = room_id (FK to rooms)
    --   - device_config: current_entity_id = device_id (FK to devices)
    --   - cloud_alert_policy: current_entity_id = policy_id (FK to cloud_alert_policies)
    --   - iot_monitor_alert: current_entity_id = alert_config_id (FK to iot_monitor_alerts)
    --   - device_installation: current_entity_id = device_id (FK to devices)
    current_entity_id UUID,  -- 可为 NULL，表示关联的实体已删除

    -- 配置数据快照（JSONB）：存储完整的配置内容
    --   不同 config_type 的 JSONB 结构不同，由应用层解析
    --   示例：
    --     room_layout: { "layout": {...}, "params": {...}, "objects": [...] }
    --     device_config: { "config": {...} }
    --     cloud_alert_policy: { "scope_type": "...", "scope_id": "...", "alert_type": "...", ... }
    --     iot_monitor_alert: { "alert_type": "...", "iot_level": "...", "vendor_config": {...} }
    --     device_installation: { "location_id": "...", "bound_room_id": "...", "bound_bed_id": "...", "installation_status": "..." }
    config_data JSONB NOT NULL,

    -- 版本生效时间区间：[valid_from, valid_to)
    valid_from TIMESTAMPTZ NOT NULL,   -- 配置开始生效时间
    valid_to   TIMESTAMPTZ,            -- 配置失效时间（NULL 表示当前仍生效）

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- 约束：同一配置类型 + 实体在任一时间点仅有一个生效版本（由应用层控制 valid_from/valid_to 不重叠）
    UNIQUE (tenant_id, config_type, entity_id, valid_from)
);

-- 索引：按配置类型和实体查询
CREATE INDEX IF NOT EXISTS idx_config_versions_tenant_type_entity
    ON config_versions(tenant_id, config_type, entity_id);

-- 索引：时间区间查询（用于回放）
CREATE INDEX IF NOT EXISTS idx_config_versions_valid
    ON config_versions(tenant_id, config_type, entity_id, valid_from, valid_to);

-- 索引：关联到当前实体（用于查询当前生效配置）
CREATE INDEX IF NOT EXISTS idx_config_versions_current_entity
    ON config_versions(current_entity_id) WHERE current_entity_id IS NOT NULL;

-- 索引：按配置类型查询（用于统计/审计）
CREATE INDEX IF NOT EXISTS idx_config_versions_type
    ON config_versions(tenant_id, config_type, valid_from DESC);

-- 索引：JSONB 查询优化（GIN 索引，用于复杂查询）
CREATE INDEX IF NOT EXISTS idx_config_versions_config_data
    ON config_versions USING GIN (config_data);

-- 注释：使用示例
-- 查询某个房间在某个时间点的布局：
--   SELECT config_data FROM config_versions
--   WHERE tenant_id = ? AND config_type = 'room_layout' AND entity_id = ?
--     AND valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)
--   ORDER BY valid_from DESC LIMIT 1;
--
-- 查询某个设备的所有配置历史：
--   SELECT * FROM config_versions
--   WHERE tenant_id = ? AND config_type = 'device_config' AND entity_id = ?
--   ORDER BY valid_from DESC;

