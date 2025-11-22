-- 映射表（posture_mapping 和 event_mapping）
-- 用于将原始设备数据映射到标准 SNOMED CT 编码和事件类型

-- ========== 姿态映射表 (posture_mapping) ==========
-- 原始姿态值到标准编码的映射表
CREATE TABLE IF NOT EXISTS posture_mapping (
    raw_posture INTEGER PRIMARY KEY CHECK (raw_posture >= 0 AND raw_posture <= 11),
    snomed_code VARCHAR(50),  -- SNOMED CT编码（可为NULL，如初始化状态）
    snomed_display VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- Posture, MotionState, Safety
    loinc_code VARCHAR(50),  -- LOINC编码（用于FHIR，可选）
    description TEXT,
    firmware_version VARCHAR(50),  -- 需要的固件版本（如"202406"）
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 插入姿态映射数据（基于雷达设备原始值 0-11）
INSERT INTO posture_mapping (raw_posture, snomed_code, snomed_display, category, loinc_code, description, firmware_version) VALUES
(0, NULL, '初始化', 'Posture', NULL, '初始状态', NULL),
(1, '129006008', 'Walking', 'MotionState', '68461-1', '行走', NULL),
(2, '129839007', 'At risk for falls', 'Safety', NULL, '疑似跌倒', NULL),
(3, '402120000', 'Sitting position', 'Posture', '56903-8', '蹲坐', NULL),
(4, '383370001', 'Standing position', 'Posture', '56903-8', '站立', NULL),
(5, '161898004', 'Fall', 'Safety', NULL, '跌倒确认', NULL),
(6, '109030009', 'Lying position', 'Posture', '56903-8', '卧床', '202406'),
(7, '129839007', 'At risk for falls', 'Safety', NULL, '疑似坐地', '202407'),
(8, '161898004', 'Fall', 'Safety', NULL, '确认坐地', '202407'),
(9, '109030009', 'Lying position', 'Posture', '56903-8', '普通床上坐起', '202501'),
(10, '129839007', 'At risk for falls', 'Safety', NULL, '疑似床上坐起', '202501'),
(11, '161898004', 'Fall', 'Safety', NULL, '确认床上坐起', '202501')
ON CONFLICT (raw_posture) DO UPDATE SET
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    category = EXCLUDED.category,
    loinc_code = EXCLUDED.loinc_code,
    description = EXCLUDED.description,
    firmware_version = EXCLUDED.firmware_version,
    updated_at = CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_posture_mapping_category ON posture_mapping(category, is_active);
CREATE INDEX IF NOT EXISTS idx_posture_mapping_snomed ON posture_mapping(snomed_code) WHERE snomed_code IS NOT NULL;

-- ========== 事件映射表 (event_mapping) ==========
-- 原始事件值到标准事件类型的映射表
CREATE TABLE IF NOT EXISTS event_mapping (
    event_type VARCHAR(50) PRIMARY KEY,  -- 标准事件类型（如 "ENTER_ROOM", "LEFT_BED"）
    event_display VARCHAR(100) NOT NULL,  -- 事件显示名称（中文）
    category VARCHAR(50) NOT NULL,  -- Behavioral, Safety, HealthCondition
    snomed_code VARCHAR(50),  -- SNOMED CT编码（可选）
    snomed_display VARCHAR(100),  -- SNOMED显示名称（可选）
    description TEXT,
    duration_threshold_minutes INTEGER,  -- 持续时间阈值（分钟），用于长时间事件判断
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 插入事件映射数据
-- 基础行为事件
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description) VALUES
('NO_EVENT', '无事件', 'Behavioral', NULL, NULL, '无事件'),
('ENTER_ROOM', '进入房间', 'Behavioral', NULL, NULL, '进入房间'),
('LEAVE_ROOM', '离开房间', 'Behavioral', NULL, NULL, '离开房间'),
('ENTER_AREA', '进入区域', 'Behavioral', NULL, NULL, '进入区域（需结合区域ID）'),
('LEAVE_AREA', '离开区域', 'Behavioral', NULL, NULL, '离开区域（需结合区域ID）')
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- 床相关事件（Radar/SleepPad 通用）
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description, duration_threshold_minutes) VALUES
('LEFT_BED', '离床', 'Behavioral', '248570008', 'Not in bed', '离开床位（从卧床状态转为非卧床状态）', NULL),
('ENTER_BED', '上床', 'Behavioral', '248569007', 'In bed', '进入床位（从非卧床状态转为卧床状态）', NULL),
('BED_SIT_UP', '床上坐起', 'Behavioral', '40199007', 'Bed sitting position', '床上坐起（从卧位转为坐位）', NULL),
('NO_TURNING_2H', '超2H未翻身', 'HealthCondition', '248527007', 'Lack of change in body position', '超过2小时未翻身（防床褥/压疮预防）', 120),
('NO_BODY_MOVEMENT_2H', '2H无体动', 'HealthCondition', '260413007', 'No movement', '2小时无体动（人体睡觉时会有体动，完全无动作可能异常）', 120)
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- 生理指标测量项目（Physiological - 基础测量）
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description, duration_threshold_minutes) VALUES
('HEART_RATE', '心率（Heart Rate, HR）', 'Physiological', '364075005', 'Heart rate', '心率测量项目（基础观测值）', NULL),
('RESPIRATORY_RATE', '呼吸频率（Respiratory Rate, RR）', 'Physiological', '86290005', 'Respiratory rate', '呼吸频率测量项目（基础观测值）', NULL)
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- 生理指标异常事件（Physiological - 异常状态）
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description, duration_threshold_minutes) VALUES
('APNEA_CONFIRMED', '呼吸暂停', 'Physiological', '28436001', 'Apnea', '确诊呼吸暂停（呼吸率 < 5 持续10秒）', NULL)
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- 睡眠状态事件（SleepState）
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description, duration_threshold_minutes) VALUES
('AWAKE', '清醒', 'SleepState', '248220002', 'Awake', '清醒状态（Awake）', NULL),
('LIGHT_SLEEP', '浅睡眠', 'SleepState', '248232005', 'Light sleep', '浅睡眠（非快速眼动睡眠 N1 + N2）', NULL),
('DEEP_SLEEP', '深睡眠', 'SleepState', '248233000', 'Deep sleep', '深睡眠（非快速眼动睡眠 N3）', NULL)
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- 安全告警事件
INSERT INTO event_mapping (event_type, event_display, category, snomed_code, snomed_display, description) VALUES
('FALL', '跌倒', 'Safety', '161898004', 'Fall', '跌倒确认'),
('FALL_SUSPECTED', '疑似跌倒', 'Safety', '129839007', 'At risk for falls', '疑似跌倒（风险预警）'),
('ON_FLOOR', '在地面', 'Safety', '161898004', 'Fall', '坐地检测'),
('PROLONGED_STAY', '长时间滞留', 'Safety', '77605003', 'Prolonged stay', '长时间滞留（如卫生间）'),
('NO_ACTIVITY_24H', '24H无人', 'Safety', '373147003', '24-hour Inactivity', '整个房间24小时无人员活动')
ON CONFLICT (event_type) DO UPDATE SET
    event_display = EXCLUDED.event_display,
    category = EXCLUDED.category,
    snomed_code = EXCLUDED.snomed_code,
    snomed_display = EXCLUDED.snomed_display,
    description = EXCLUDED.description,
    duration_threshold_minutes = EXCLUDED.duration_threshold_minutes,
    updated_at = CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_event_mapping_category ON event_mapping(category, is_active);
CREATE INDEX IF NOT EXISTS idx_event_mapping_snomed ON event_mapping(snomed_code) WHERE snomed_code IS NOT NULL;

