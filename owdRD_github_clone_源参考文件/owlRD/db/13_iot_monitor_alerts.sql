-- IoT 设备实时报警配置表 (iot_monitor_alerts)
-- 用途：
--   1) 存储 IoT 设备本地报警阈值配置（厂家原始格式，用于上传/下发到设备）
--   2) IoT 设备使用指定阈值，触发后通过 MQTT 主动上报事件或统计信息
--   3) 作为“兜底保护”，厂家报警条件可能更严格（如心率 < 45 至少 20 分钟才报警）
--   4) 与 cloud_alert_policies（云端计算策略）取合集：
--        - IoT 侧：设备本地阈值触发后上报事件
--        - 云端侧：cloud_alert_policies 接收事件报警并自行计算，定义报警级别
--        - 最终报警级别 = max(IoT 级别, 云端级别)
--        - 示例：默认 bed_situp 为 L2 或不报警，但如果 IoT 上设置了 L1，则最终为 L1
--   5) 配置存储：使用厂家原始 JSON 格式，便于直接上传/下发到设备
--   6) 历史版本：通过 iot_monitor_alerts_versions 表记录配置变更历史（用于回放/审计）

CREATE TABLE IF NOT EXISTS iot_monitor_alerts (
    alert_config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    device_id   UUID NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,

    -- 报警类型：如 LeftBed, ApneaHypopnea, AbnormalHeartRate, Fall 等
    alert_type  VARCHAR(50) NOT NULL,

    -- IoT 设备报警级别：通常为 'L1'（设备本地报警），部分厂家可能支持 L2
    -- 注意：IoT 设备报警更多是“兜底设置”，条件可能比云端更严格
    -- 前端 UI 说明：当前端打勾启用该报警类型时，默认 iot_level = 'L1'
    iot_level   VARCHAR(10) NOT NULL,  -- 'L1' / 'L2' / 'DISABLE'

    -- 厂家原始阈值配置（JSON）：直接存储厂家格式，便于上传/下发
    -- 示例（Sleepad）：
    --   { "heart_rate_low": { "threshold": 45, "duration_min": 20 },
    --     "apnea": { "duration_sec": 10 } }
    -- 示例（Radar）：
    --   { "hr_below": 44, "hr_above": 116, "duration_sec": 60 }
    vendor_config JSONB NOT NULL,

    -- 是否启用该报警类型
    is_enabled  BOOLEAN NOT NULL DEFAULT TRUE,

    -- 同一设备 + 报警类型唯一
    UNIQUE (tenant_id, device_id, alert_type)
);

CREATE INDEX IF NOT EXISTS idx_iot_monitor_alerts_device
    ON iot_monitor_alerts(tenant_id, device_id);

CREATE INDEX IF NOT EXISTS idx_iot_monitor_alerts_type
    ON iot_monitor_alerts(tenant_id, alert_type, is_enabled);

