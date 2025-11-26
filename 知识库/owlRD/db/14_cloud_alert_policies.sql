-- 云端告警策略表 (cloud_alert_policies)
-- 
-- 【核心功能】
-- 每个租户可以配置每种报警类型的报警级别（DangerLevel）和发送模式
-- 每个报警类型是一个独立字段，字段值存储对应的 DangerLevel
-- 
-- 【使用场景】
-- 例如：租户A想设置"心率异常"的报警规则：
--   - 级别：AbnormalHeartRate_level = 'L1' 或 'L2'
--   - 阈值：在 conditions JSONB 中配置心率阈值范围
--   - 发送：在 notification_rules JSONB 中配置发送模式
-- 
-- 【配置说明】
-- 1. 每个租户（tenant_id）只有一条配置记录（PRIMARY KEY tenant_id）
-- 2. 每个报警类型对应一个字段，字段值存储 DangerLevel（'DISABLE', 'L1', 'L2'）
-- 3. 如果字段值为 NULL，表示使用系统默认级别
-- 4. 创建新租户时，需要初始化所有字段的默认值
-- 
-- 【DangerLevel 定义（参考 TDPv2-0916.md）】
--   L1 (EMERGENCY): 紧急，高风险，高置信
--   L2 (ALERT): 警报，高危事件
--   DISABLE: 关闭该类报警
--   当前仅建议使用 ['DISABLE','L1','L2']
-- 
-- 【与其他表的关系】
--   - 与 iot_monitor_alerts（IoT设备本地报警）取合集，最终报警级别 = max(云端级别, IoT级别)
--   - 与 users.alert_levels/alert_channels/alert_scope 一起决定实际路由行为

CREATE TABLE IF NOT EXISTS cloud_alert_policies (
    -- 主键：租户ID，每个租户只有一条配置记录
    tenant_id   UUID PRIMARY KEY REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- ========== Common 报警类型 ==========
    OfflineAlarm      VARCHAR(10),  -- DangerLevel: 'DISABLE', 'L1', 'L2', NULL=系统默认
    LowBattery        VARCHAR(10),
    DeviceFailure     VARCHAR(10),

    -- ========== SleepMonitor 报警类型 ==========
    SleepPad_LeftBed           VARCHAR(10),
    SleepPad_SitUp             VARCHAR(10),
    SleepPad_ApneaHypopnea     VARCHAR(10),
    SleepPad_AbnormalHeartRate VARCHAR(10),  -- 心率异常（Heart Rate, HR）
    SleepPad_AbnormalRespiratoryRate VARCHAR(10),  -- 呼吸频率异常（Respiratory Rate, RR）
    SleepPad_AbnormalBodyMovement VARCHAR(10),
    SleepPad_InBed             VARCHAR(10),

    -- ========== Radar 报警类型 ==========
    -- 注意：Radar 和 SleepMonitor 有重复的报警类型（ApneaHypopnea, AbnormalHeartRate, AbnormalRespiratoryRate, LeftBed）
    -- 这里使用 Radar 前缀区分，或者可以共用同一个字段（根据实际需求）
    Radar_AbnormalHeartRate VARCHAR(10),  -- 心率异常（Heart Rate, HR）
    Radar_AbnormalRespiratoryRate VARCHAR(10),  -- 呼吸频率异常（Respiratory Rate, RR）
    SuspectedFall           VARCHAR(10),
    Fall                    VARCHAR(10),
    VitalsWeak              VARCHAR(10),
    Radar_LeftBed           VARCHAR(10),
    Stay                    VARCHAR(10),
    NoActivity24h           VARCHAR(10),
    AngleException          VARCHAR(10),

    -- ========== 自定义报警类型（预留扩展）==========
    CustomAlert1           VARCHAR(10),  -- 自定义报警1级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认
    CustomAlert2           VARCHAR(10),  -- 自定义报警2级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认
    CustomAlert3           VARCHAR(10),  -- 自定义报警3级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认

    -- 【报警阈值配置】
    -- 用于生理指标类报警（如心率 Heart Rate, HR、呼吸频率 Respiratory Rate, RR），定义什么数值范围触发什么级别
    -- 如果为 NULL，则使用系统默认阈值（vue_radar 项目标准）
    -- 
    -- 示例：心率异常阈值（Heart Rate, HR）
    --   {
    --     "heart_rate": {
    --       "L1": { "ranges": [{"min": 0, "max": 44}, {"min": 116, "max": null}], "duration_sec": 60 },
    --       "L2": { "ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}], "duration_sec": 300 },
    --       "Normal": { "ranges": [{"min": 55, "max": 95}], "duration_sec": 0 }
    --     }
    --   }
    -- 
    -- 示例：呼吸频率异常阈值（Respiratory Rate, RR）
    --   {
    --     "respiratory_rate": {
    --       "L1": { "ranges": [{"min": 0, "max": 7}, {"min": 27, "max": null}], "duration_sec": 60 },
    --       "L2": { "ranges": [{"min": 8, "max": 9}, {"min": 24, "max": 26}], "duration_sec": 300 },
    --       "Normal": { "ranges": [{"min": 10, "max": 23}], "duration_sec": 0 }
    --     }
    --   }
    conditions  JSONB,

    -- 【发送模式配置】
    -- 包含通知通道、发送方式、升级规则、抑制规则、静默规则等完整配置
    -- 如果为 NULL，表示使用用户/系统默认配置
    -- 
    -- 示例：
    --   {
    --     "notification_rules": {
    --       "L1": {
    --         "channels": ["WEB", "APP", "PHONE", "EMAIL"],
    --         "immediate": true,
    --         "repeat_interval_sec": 300
    --       },
    --       "L2": {
    --         "channels": ["WEB", "APP"],
    --         "immediate": false,
    --         "repeat_interval_sec": 600
    --       }
    --     },
    --     "escalation": {
    --       "enabled": true,
    --       "escalate_after_sec": 300,
    --       "escalate_to_level": "L1"
    --     },
    --     "suppression": {
    --       "enabled": true,
    --       "suppress_duplicate_sec": 60,
    --       "max_alerts_per_hour": 10
    --     },
    --     "silence": {
    --       "enabled": false,
    --       "silence_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6],
    --       "silence_days": ["Saturday", "Sunday"]
    --     }
    --   }
    -- 
    -- 说明：
    --   - channels: 通知通道数组，如 ["WEB","APP","PHONE","EMAIL"]，为空则使用用户/系统默认
    --   - immediate: 是否立即发送（true=立即，false=延迟/批量）
    --   - repeat_interval_sec: 重复发送间隔（秒）
    --   - escalation: 升级规则（如 L2 持续 5 分钟后升级为 L1）
    --   - suppression: 抑制规则（如 1 分钟内重复报警只发一次）
    --   - silence: 静默规则（如夜间 22:00-6:00 不发送）
    notification_rules JSONB,

    -- 状态
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,

    -- 时间戳
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 元数据：扩展信息
    metadata    JSONB
);

-- ============================================================================
-- 初始化函数：为新租户创建所有报警类型的默认配置
-- ============================================================================
CREATE OR REPLACE FUNCTION initialize_tenant_alert_policies(p_tenant_id UUID)
RETURNS void AS $$
DECLARE
    v_default_conditions JSONB;
BEGIN
    -- 设置默认阈值（仅生理指标类报警）
    v_default_conditions := '{
        "heart_rate": {
            "L1": { "ranges": [{"min": 0, "max": 44}, {"min": 116, "max": null}], "duration_sec": 60 },
            "L2": { "ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}], "duration_sec": 300 },
            "Normal": { "ranges": [{"min": 55, "max": 95}], "duration_sec": 0 }
        },
        "respiratory_rate": {
            "L1": { "ranges": [{"min": 0, "max": 7}, {"min": 27, "max": null}], "duration_sec": 60 },
            "L2": { "ranges": [{"min": 8, "max": 9}, {"min": 24, "max": 26}], "duration_sec": 300 },
            "Normal": { "ranges": [{"min": 10, "max": 23}], "duration_sec": 0 }
        }
    }'::jsonb;

    -- 插入默认配置
    INSERT INTO cloud_alert_policies (
        tenant_id,
        -- Common
        OfflineAlarm, LowBattery, DeviceFailure,
        -- SleepMonitor
        SleepPad_LeftBed, SleepPad_SitUp, SleepPad_ApneaHypopnea,
        SleepPad_AbnormalHeartRate, SleepPad_AbnormalRespiratoryRate, SleepPad_AbnormalBodyMovement, SleepPad_InBed,
        -- Radar
        Radar_ApneaHypopnea, Radar_AbnormalHeartRate, Radar_AbnormalRespiratoryRate,
        SuspectedFall, Fall, VitalsWeak, Radar_LeftBed,
        Stay, NoActivity24h, AngleException,
        -- 自定义报警
        CustomAlert1, CustomAlert2, CustomAlert3,
        conditions
    ) VALUES (
        p_tenant_id,
        -- Common: 默认 L2, L2, L1
        'L2', 'L2', 'L1',
        -- SleepMonitor: 默认 L2, L2, L1, L1+L2, L1+L2, L2, 不报警
        'L2', 'L2', 'L1', 'L1', 'L1', 'L2', 'DISABLE',
        -- Radar: 默认 L1, L1, L1, L2, L1, L2, L2, L2, L1, L2
        'L1', 'L1', 'L1', 'L2', 'L1', 'L2', 'L2', 'L2', 'L1', 'L2',
        -- 自定义报警：默认 NULL（未启用）
        NULL, NULL, NULL,
        v_default_conditions
    )
    ON CONFLICT (tenant_id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION initialize_tenant_alert_policies IS '为新租户初始化所有报警类型的默认配置，创建租户时必须调用此函数';

-- 注释
COMMENT ON TABLE cloud_alert_policies IS '云端告警策略表：租户级别的全局配置，每个报警类型是一个字段，字段值存储 DangerLevel';
COMMENT ON COLUMN cloud_alert_policies.tenant_id IS '租户ID：主键，每个租户只有一条配置记录';
COMMENT ON COLUMN cloud_alert_policies.OfflineAlarm IS '设备离线报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.LowBattery IS '低电量报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.DeviceFailure IS '设备故障报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_LeftBed IS '离床报警级别（SleepPad）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_SitUp IS '坐起报警级别（SleepPad）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_ApneaHypopnea IS '呼吸暂停报警级别（SleepPad）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_AbnormalHeartRate IS '心率异常报警级别（SleepPad，Heart Rate, HR）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_AbnormalRespiratoryRate IS '呼吸频率异常报警级别（SleepPad，Respiratory Rate, RR）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_AbnormalBodyMovement IS '异常体动报警级别（SleepPad）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SleepPad_InBed IS '上床报警级别（SleepPad）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Radar_ApneaHypopnea IS '呼吸暂停报警级别（Radar）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Radar_AbnormalHeartRate IS '心率异常报警级别（Radar，Heart Rate, HR）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Radar_AbnormalRespiratoryRate IS '呼吸频率异常报警级别（Radar，Respiratory Rate, RR）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.SuspectedFall IS '疑似跌倒报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Fall IS '跌倒报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.VitalsWeak IS '生命体征微弱报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Radar_LeftBed IS '离床报警级别（Radar）：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.Stay IS '长时间滞留报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.NoActivity24h IS '24小时无活动报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.AngleException IS '角度异常报警级别：DangerLevel (DISABLE/L1/L2)，NULL=系统默认';
COMMENT ON COLUMN cloud_alert_policies.CustomAlert1 IS '自定义报警1级别：DangerLevel (DISABLE/L1/L2)，NULL=未启用，预留扩展';
COMMENT ON COLUMN cloud_alert_policies.CustomAlert2 IS '自定义报警2级别：DangerLevel (DISABLE/L1/L2)，NULL=未启用，预留扩展';
COMMENT ON COLUMN cloud_alert_policies.CustomAlert3 IS '自定义报警3级别：DangerLevel (DISABLE/L1/L2)，NULL=未启用，预留扩展';
COMMENT ON COLUMN cloud_alert_policies.conditions IS '条件/阈值配置（JSONB）：包含阈值范围、持续时长等，为空则使用系统默认（vue_radar 标准）';
COMMENT ON COLUMN cloud_alert_policies.notification_rules IS '通知规则（JSONB）：完整的发送模式配置，包含通知通道（channels）、立即发送（immediate）、重复间隔（repeat_interval_sec）、升级规则（escalation）、抑制规则（suppression）、静默规则（silence）等，为空则使用用户/系统默认配置';
COMMENT ON COLUMN cloud_alert_policies.created_at IS '创建时间：用于查看配置的创建时间';
COMMENT ON COLUMN cloud_alert_policies.updated_at IS '更新时间：用于查看配置的最后修改时间';
COMMENT ON COLUMN cloud_alert_policies.metadata IS '元数据（JSONB）：扩展信息';


