-- 设备表 (devices)
-- 对应权限表中的 Device 定义
-- 业务规则：
--   1) 设备在安装并投入使用时，应绑定到某个 Room（可通过 Default Room 实现“有房必有设备”）
--   2) 绑定路径：Location → Room → Bed/Device
--   3) 当 Location/Room 结构细分时，应在业务层迁移 BoundRoomID/BoundBedID，避免直接指向 Default Room

CREATE TABLE IF NOT EXISTS devices (
    -- Primary / SaaS
    device_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- Identity / Asset
    device_name           VARCHAR(100) NOT NULL,
    device_model   VARCHAR(50)  NOT NULL,  -- 型号（例如 WF-RADAR-60G-V2）

    -- 设备类型 / 分类：如 Radar / SleepPad / VibrationSensor / Gateway 等
    device_type    VARCHAR(50)  NOT NULL,

    -- 序列号 / UID：不同厂家可能同时提供 SN 和 UID，由应用层控制两者至少填一个
    -- 规则：serial_number 与 uid 至少填一个（由应用层校验），两者在各自租户内各自唯一
    serial_number  VARCHAR(100),          -- 厂家出厂序列号（可空）
    uid            VARCHAR(50),           -- 厂家或平台提供的唯一 UID（可空）
    imei          VARCHAR(50),             -- 4G 设备 IMEI，可空

    -- Technical Specs
    comm_mode        VARCHAR(20) NOT NULL,  -- 通讯方式（WiFi / LTE / Zigbee 等）
    firmware_version VARCHAR(50) NOT NULL,  -- 主业务固件版本（由应用层定义）
    mcu_model        VARCHAR(50),           -- MCU/主控型号（可选，如 STM32F4、ESP32 等）

    -- Location Binding
    location_id  UUID REFERENCES locations(location_id) ON DELETE SET NULL,
    bound_room_id UUID REFERENCES rooms(room_id)       ON DELETE SET NULL,
    bound_bed_id  UUID REFERENCES beds(bed_id)         ON DELETE SET NULL,

    -- Status / Maintenance
    status            VARCHAR(20) NOT NULL,            -- 实时状态快照（online/offline/error等）
    installed         BOOLEAN     NOT NULL DEFAULT TRUE,  -- 设备是否已安装（物理存在，避免重装/拆）
    business_access    BOOLEAN     NOT NULL DEFAULT FALSE, -- 是否允许设备接入系统（管理员审批）
    monitoring_enabled BOOLEAN    NOT NULL DEFAULT FALSE, -- 是否启用监护功能（业务状态）
    -- 字段说明：
    --   installed: 设备物理状态（TRUE=设备已安装，FALSE=设备已移除）
    --   business_access: 业务接入权限（TRUE=允许接入系统，FALSE=待审批/已拒绝）
    --   monitoring_enabled: 监护业务状态（TRUE=激活监护，FALSE=Dormant模式/待分配）
    -- 状态组合：
    --   - installed=TRUE, business_access=FALSE, monitoring_enabled=FALSE: 新设备加入，待管理员审批
    --   - installed=TRUE, business_access=TRUE, monitoring_enabled=FALSE: 设备已安装但未启用监护（待分配、Dormant模式）
    --   - installed=TRUE, business_access=TRUE, monitoring_enabled=TRUE: 设备已安装且激活监护（正常监护状态）
    --   - installed=FALSE, business_access=FALSE, monitoring_enabled=FALSE: 设备已移除（物理拆除）
    -- 业务规则：
    --   - 新设备加入时：installed=TRUE, business_access=FALSE, monitoring_enabled=FALSE（待管理员审批）
    --   - 管理员审批通过后：business_access=TRUE（允许接入系统）
    --   - 设备安装后：installed=TRUE, business_access=TRUE, monitoring_enabled=FALSE（待分配）
    --   - 住户入住后：monitoring_enabled=TRUE（激活监护）
    --   - 住户出院后：monitoring_enabled=FALSE（Dormant模式，涉及监护义务和生理数据授权），installed=TRUE（设备仍在）
    --   - 设备拆除时：installed=FALSE, business_access=FALSE, monitoring_enabled=FALSE
    installation_date_utc TIMESTAMPTZ NOT NULL,        -- 设备安装日期 (UTC)

    -- 其他扩展配置 / 标签：
    --   - 对于 IoT 设备，可在此存储 vue_radar 中的 IotDeviceProperties / RadarSpecificProperties 快照
    --   - 示例（雷达）：
    --     {
    --       "iot": {
    --         "deviceId": "Radar01",
    --         "radar": {
    --           "installModel": "wall",
    --           "workModel": "vital-sign",
    --           "rotation": 0,
    --           "hfov": 140,
    --           "vfov": 120,
    --           "boundary": { "leftH": 300, "rightH": 300, "frontV": 400, "rearV": 0 },
    --           "signalRadius": 500,
    --           "showBoundary": true,
    --           "showSignal": false
    --         }
    --       }
    --     }
    metadata JSONB,

    -- Tenant-Scope 唯一：设备序列号 / UID 各自唯一（允许 NULL）
    UNIQUE(tenant_id, serial_number),
    UNIQUE(tenant_id, uid)
);

CREATE INDEX IF NOT EXISTS idx_devices_tenant_id ON devices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(tenant_id, serial_number);
CREATE INDEX IF NOT EXISTS idx_devices_location_id ON devices(tenant_id, location_id);
CREATE INDEX IF NOT EXISTS idx_devices_room_id ON devices(tenant_id, bound_room_id);
CREATE INDEX IF NOT EXISTS idx_devices_bed_id ON devices(tenant_id, bound_bed_id);
CREATE INDEX IF NOT EXISTS idx_devices_business_access ON devices(tenant_id, business_access) WHERE business_access = FALSE;
CREATE INDEX IF NOT EXISTS idx_devices_monitoring ON devices(tenant_id, monitoring_enabled) WHERE monitoring_enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_devices_installed_monitoring ON devices(tenant_id, installed, monitoring_enabled) WHERE installed = TRUE AND monitoring_enabled = TRUE;
