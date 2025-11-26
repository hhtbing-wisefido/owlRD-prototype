-- IoT 设备时间序列数据表 (iot_timeseries) - TimescaleDB 超表
-- 存储 Radar、SleepPad 等多种 IoT 设备的实时时间序列数据（轨迹、事件、生命体征等）
-- 设计：标准值 + 原始记录双存储
-- 用途：
--   1) 存储实时数据（轨迹、姿态、生命体征等），用于回放、分析和 AI 训练
--   2) 标准值（主要存储）：用于业务查询、规则引擎、AI 分析
--   3) 原始记录（审计追溯）：存储厂家发送的完整原始数据，用于前端参考、审计追溯和重新解析
-- 保留策略：
--   - 热数据：最近 3 个月保留在 TimescaleDB（用于实时查询、回放和分析）
--   - 冷数据：3 个月以上的数据自动归档到离线备份（S3 Glacier / Azure Archive）
--   - 永久保存：所有数据一直保存，不删除，用于未来 AI 训练和模型优化

CREATE TABLE IF NOT EXISTS iot_timeseries (
    id         BIGSERIAL,
    
    -- ========== 设备索引 ==========
    tenant_id  UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    device_id  UUID NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    -- 注意：device_SN 和 device_uid 通过 device_id JOIN devices 表查询，不冗余存储
    
    -- ========== 时间戳 ==========
    timestamp  TIMESTAMPTZ NOT NULL,  -- 数据时间戳（NTP 同步）
    
    -- ========== TDP Tag Category（用于快速分类查询）==========
    -- 对应 06_FHIR_Simple_Conversion_Guide.md 中的分类：
    --   Physiological: 生命体征测量和异常（基于数值阈值判断）
    --                   - 基础测量：心率（Heart Rate, HR）、呼吸频率（Respiratory Rate, RR）
    --                   - 异常状态：心动过速、心动过缓、呼吸急促、呼吸缓慢、呼吸暂停（Apnea）
    --   Behavioral: 行为观测（如床上坐起、在床/不在床等）
    --   Posture: 姿态观测（站立/坐位/卧位/床上坐姿等）
    --   MotionState: 运动状态（行走/静止/异常步态等）
    --   SleepState: 睡眠状态（清醒、浅睡眠、深睡眠）
    --                - 注意：睡眠状态是从 HR/RR 数据推导出来的，总是与生命体征数据一同推送
    --                - 当有 HR/RR 数据时，通常也会有对应的睡眠状态数据
    --   Safety: 安全告警（事件型告警，不依赖数值阈值）
    --            - 跌倒、疑似跌倒、在地面
    --            - 身体抽畜（ABM）
    --            - 长时间滞留、24H无人
    --   HealthCondition: 健康风险（暂时空）
    --   DeviceError: 设备故障状态 + 告警
    -- 分类原则：
    --   - Physiological：基于数值阈值判断的生命体征测量和异常（如心率 ≥ 116、呼吸率 < 5）
    --   - SleepState：从 HR/RR 数据推导的睡眠状态（清醒、浅睡眠、深睡眠），总是与生命体征数据一同推送
    --   - Safety：事件型告警，不依赖数值阈值（如跌倒、长时间滞留）
    tdp_tag_category VARCHAR(50),  -- TDP Tag Category，用于快速分类查询

    -- ========== 标准值（主要存储，用于查询和处理）==========
    -- 轨迹数据
    tracking_id   INTEGER,           -- 目标ID（0-7，NULL 表示无人，来自原始值 88 的映射）
    radar_pos_x   INTEGER NOT NULL,  -- 雷达坐标 X（厘米，雷达坐标系）
    radar_pos_y   INTEGER NOT NULL,  -- 雷达坐标 Y（厘米，雷达坐标系）
    radar_pos_z   INTEGER NOT NULL,  -- 雷达坐标 Z（厘米，雷达坐标系）

    -- 姿态/运动状态（标准编码值，用于查询和规则引擎）
    -- 注意：分类信息可通过 JOIN posture_mapping 表查询，无需冗余存储
    posture_snomed_code VARCHAR(50),   -- SNOMED CT 编码（如 "383370001" 表示 Standing position）
    posture_display     VARCHAR(100),  -- 显示名称（如 "Standing position"）

    -- 事件（标准事件类型）
    -- 注意：分类信息可通过 JOIN event_mapping 表查询，无需冗余存储
    -- 事件类型示例：
    --   - 基础行为：ENTER_ROOM, LEAVE_ROOM, ENTER_AREA, LEAVE_AREA
    --   - 床相关（Radar/SleepPad通用）：LEFT_BED, ENTER_BED, BED_SIT_UP
    --   - 生理指标异常：APNEA_CONFIRMED（呼吸暂停）
    --   - 健康风险：NO_TURNING_2H, NO_BODY_MOVEMENT_2H
    --   - 安全告警：FALL, FALL_SUSPECTED, PROLONGED_STAY, NO_ACTIVITY_24H
    event_type      VARCHAR(50),   -- 标准事件类型（如 "ENTER_ROOM", "LEFT_BED", "NO_TURNING_2H"）
    event_display   VARCHAR(100),  -- 事件显示名称（如 "进入房间", "离床", "超2H未翻身"）
    area_id         INTEGER,       -- 区域 ID（当 event_type 为 ENTER_AREA/LEAVE_AREA 时有效）

    -- 生命体征（标准值，统一单位）
    -- 注意：Apnea（呼吸暂停）可通过 respiratory_rate < 5 持续10秒计算得出
    --       当检测到 Apnea 时，应在 event_type 字段中记录 'APNEA_CONFIRMED'
    -- SNOMED CT 编码：
    --   - 心率（Heart Rate, HR）：364075005 (Heart rate)
    --   - 呼吸频率（Respiratory Rate, RR）：86290005 (Respiratory rate)
    heart_rate       INTEGER,        -- 心率（bpm，次/分钟），SNOMED: 364075005 (Heart rate)
    respiratory_rate INTEGER,        -- 呼吸率（次/分钟），SNOMED: 86290005 (Respiratory rate)
    
    -- 睡眠状态（从 HR/RR 数据推导，总是与生命体征数据一同推送）
    -- 注意：
    --   1) 睡眠状态是从呼吸/心率数据推送出来的，总是跟随 HR/RR 一同进入系统
    --   2) 当有 HR/RR 数据时，通常也会有对应的睡眠状态数据
    --   3) 睡眠状态分类：清醒（Awake）、浅睡眠（Light sleep）、深睡眠（Deep sleep）
    --   4) SNOMED CT 编码：
    --      - 清醒：248220002 (Awake)
    --      - 浅睡眠：248232005 (Light sleep)
    --      - 深睡眠：248233000 (Deep sleep)
    sleep_state_snomed_code VARCHAR(50),   -- 睡眠状态 SNOMED CT 编码（如 "248220002" 表示 Awake）
    sleep_state_display      VARCHAR(100),  -- 睡眠状态显示名称（如 "Awake", "Light sleep", "Deep sleep"）

    -- ========== 位置信息（用于查询同门牌号下的所有 IoT 设备数据）==========
    location_id  UUID REFERENCES locations(location_id) ON DELETE SET NULL,  -- 门牌号/地址（冗余，加速查询）
    room_id      UUID REFERENCES rooms(room_id) ON DELETE SET NULL,          -- 房间ID（冗余，加速查询）

    -- ========== 其他字段 ==========
    confidence     INTEGER,        -- 置信度（0-100）
    remaining_time INTEGER,        -- 剩余时间（0-60 秒，仅自动测量边界时使用）

    -- ========== 原始记录存储（供前端参考和审计追溯）==========
    -- 原始记录：厂家发送的完整数据，非解析，可能压缩
    -- 用途：
    --   1) 前端参考：vue_radar 等前端需要参考厂家设计（如 areaID），因为没有标准
    --   2) 审计追溯：合规审计和数据追溯
    --   3) 重新解析：硬件升级时，从原始记录重新解析并映射
    raw_original   BYTEA      NOT NULL,  -- 原始记录（厂家发送的完整数据，非解析，可能压缩）
    raw_format     VARCHAR(50) NOT NULL, -- 原始数据格式（"json", "binary", "xml", "string" 等）
    raw_compression VARCHAR(50),         -- 压缩方式（"gzip", "deflate", NULL = 未压缩）

    -- ========== 元数据（扩展信息）==========
    -- 注意：版本信息（固件版本、映射版本、解析器版本等）不在此存储，应通过以下方式获取：
    --   1) firmware_version: 从 devices 表获取（当前版本）或从 config_versions 表查询历史版本
    --   2) mapping_version / parser_version: 从 config_versions 表查询（config_type = 'device_config'）
    --   3) 查询示例：
    --      SELECT d.firmware_version, cv.config_data->>'mapping_version', cv.config_data->>'parser_version'
    --      FROM iot_timeseries ts
    --      JOIN devices d ON ts.device_id = d.device_id
    --      LEFT JOIN config_versions cv ON cv.config_type = 'device_config' 
    --        AND cv.entity_id = ts.device_id 
    --        AND cv.valid_from <= ts.timestamp 
    --        AND (cv.valid_to IS NULL OR cv.valid_to > ts.timestamp)
    --      WHERE ts.id = ?;
    -- metadata 字段仅用于存储其他非版本相关的扩展信息（如临时标记、调试信息等）
    metadata   JSONB DEFAULT '{}'::JSONB

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 如已安装 TimescaleDB，可在部署时执行以下语句创建 hypertable：
-- SELECT create_hypertable('iot_timeseries', 'timestamp', if_not_exists => TRUE);

-- 索引：设备索引（通过 device_id 关联到 devices 表，可查询 device_SN 和 device_uid）
-- 注意：device_SN 和 device_uid 存储在 devices 表中，通过 JOIN 查询，不冗余存储

-- 索引：TDP Tag Category（用于快速分类查询）
CREATE INDEX IF NOT EXISTS idx_trajectories_tdp_tag_category
    ON iot_timeseries(tenant_id, device_id, tdp_tag_category, timestamp DESC);

-- 索引：标准值（主要索引，用于查询和规则引擎）
CREATE INDEX IF NOT EXISTS idx_trajectories_posture_snomed
    ON iot_timeseries(tenant_id, device_id, posture_snomed_code, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_trajectories_event_type
    ON iot_timeseries(tenant_id, device_id, event_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_trajectories_tracking_id
    ON iot_timeseries(tenant_id, device_id, tracking_id, timestamp DESC);

-- 注意：如需按姿态/事件分类查询，可通过 JOIN posture_mapping/event_mapping 表的 category 字段
-- 或直接使用 tdp_tag_category 进行顶层分类查询

-- 索引：时间范围查询
CREATE INDEX IF NOT EXISTS idx_trajectories_timestamp
    ON iot_timeseries(tenant_id, device_id, timestamp DESC);

-- 索引：位置查询（用于查询同门牌号下的所有 IoT 设备数据）
CREATE INDEX IF NOT EXISTS idx_trajectories_location
    ON iot_timeseries(tenant_id, location_id, timestamp DESC)
    WHERE location_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trajectories_room
    ON iot_timeseries(tenant_id, room_id, timestamp DESC)
    WHERE room_id IS NOT NULL;

-- 注意：计算两个 tracking_id 之间的距离时，查询方式为：
--   SELECT tracking_id, radar_pos_x, radar_pos_y, radar_pos_z
--   FROM iot_timeseries
--   WHERE tenant_id = 'xxx' AND device_id = 'xxx' AND timestamp = '...'
--   然后直接在应用层计算距离：SQRT((radar_pos_x1-radar_pos_x2)^2 + (radar_pos_y1-radar_pos_y2)^2)
--   此查询主要使用 device_id + timestamp，已有 idx_trajectories_timestamp 索引支持，无需 radar_pos_x/y 索引

-- 索引：生命体征查询（用于规则引擎和 AI 分析）
CREATE INDEX IF NOT EXISTS idx_trajectories_vital_signs
    ON iot_timeseries(tenant_id, device_id, heart_rate, respiratory_rate, timestamp DESC)
    WHERE heart_rate IS NOT NULL OR respiratory_rate IS NOT NULL;

-- 索引：睡眠状态查询（用于睡眠质量分析和 AI 训练）
-- 注意：睡眠状态总是与 HR/RR 数据一同推送，可通过此索引快速查询睡眠状态变化
CREATE INDEX IF NOT EXISTS idx_trajectories_sleep_state
    ON iot_timeseries(tenant_id, device_id, sleep_state_snomed_code, timestamp DESC)
    WHERE sleep_state_snomed_code IS NOT NULL;


