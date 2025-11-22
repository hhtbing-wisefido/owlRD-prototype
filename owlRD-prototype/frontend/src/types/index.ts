// Tenant types
export interface Tenant {
  tenant_id: string
  tenant_name: string
  domain?: string
  status: string
  created_at: string
  updated_at: string
  metadata?: {
    license_type?: string
    max_users?: number
    max_residents?: number
    features_enabled?: string[]
    contact_email?: string
    contact_phone?: string
    address?: string
    [key: string]: any
  }
}

// Role types
export interface Role {
  role_id: string;
  tenant_id: string;
  role_code: string;
  display_name: string;
  description?: string;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// CloudAlertPolicy types
export interface CloudAlertPolicy {
  tenant_id: string;
  // Common alerts
  OfflineAlarm?: string;
  LowBattery?: string;
  DeviceFailure?: string;
  // SleepMonitor alerts
  SleepPad_LeftBed?: string;
  SleepPad_SitUp?: string;
  SleepPad_ApneaHypopnea?: string;
  SleepPad_AbnormalHeartRate?: string;
  SleepPad_AbnormalRespiratoryRate?: string;
  SleepPad_AbnormalBodyMovement?: string;
  SleepPad_InBed?: string;
  // Radar alerts
  Radar_AbnormalHeartRate?: string;
  Radar_AbnormalRespiratoryRate?: string;
  SuspectedFall?: string;
  Fall?: string;
  VitalsWeak?: string;
  Radar_LeftBed?: string;
  Stay?: string;
  NoActivity24h?: string;
  AngleException?: string;
  // Custom alerts
  CustomAlert1?: string;
  CustomAlert2?: string;
  CustomAlert3?: string;
  // Configurations
  conditions?: Record<string, any>;
  notification_rules?: Record<string, any>;
  is_active: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// User types
export interface User {
  user_id: string
  tenant_id: string
  username?: string
  email?: string
  phone?: string
  role: string
  status: string
  alert_levels?: string[]
  alert_channels?: string[]
  alert_scope?: string
  tags?: {
    department?: string
    nurse_group?: string
    shift?: string
    certifications?: string[]
    [key: string]: any
  }
  last_login_at?: string
  created_at: string
  updated_at: string
}

// Resident PHI types (对齐 08_resident_phi.sql)
export interface ResidentPHI {
  phi_id: string
  tenant_id: string
  resident_id: string
  
  // 基本PHI
  first_name?: string  // 真实名字
  last_name?: string  // 真实姓氏
  gender?: string  // Male/Female/Other/Unknown
  date_of_birth?: string  // YYYY-MM-DD
  resident_phone?: string  // 住户个人电话
  resident_email?: string  // 住户个人邮箱
  
  // 生物特征PHI
  weight_lb?: number  // 体重（磅）
  height_ft?: number  // 身高（英尺）
  height_in?: number  // 身高（英寸）
  
  // 功能性活动能力
  mobility_level?: number  // 0无行动能力 ~ 5完全独立
  
  // 功能性健康状态
  tremor_status?: string  // None/Mild/Severe
  mobility_aid?: string  // Cane/Wheelchair/None
  adl_assistance?: string  // Independent/NeedsHelp
  comm_status?: string  // Normal/SpeechDifficulty
  
  // 慢性病史
  has_hypertension?: boolean  // 高血压
  has_hyperlipaemia?: boolean  // 高血脂
  has_hyperglycaemia?: boolean  // 高血糖/糖尿病
  has_stroke_history?: boolean  // 既往脑卒中史
  has_paralysis?: boolean  // 肢体瘾痪/偏瘾
  has_alzheimer?: boolean  // 阿尔茨海默病/痴呆
  medical_history?: string  // 其他病史说明
  
  // HIS系统同步字段（包含PII）
  HIS_resident_name?: string  // HIS系统真实姓名
  HIS_resident_admission_date?: string  // HIS入院日期
  HIS_resident_discharge_date?: string  // HIS出院日期
  HIS_resident_metadata?: Record<string, any>  // HIS其他元数据
  
  // HomeCare场景家庭地址（PHI）
  home_address_street?: string  // 街道地址
  home_address_city?: string  // 城市
  home_address_state?: string  // 州/省
  home_address_postal_code?: string  // 邮编
  plus_code?: string  // Google Plus Code
}

// Config Version types
export interface ConfigVersion {
  version_id: string
  tenant_id: string
  config_type: string
  entity_id?: string
  current_entity_id?: string
  config_data: Record<string, any>
  valid_from: string
  valid_to?: string | null
  is_active: boolean
  created_by?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

// Posture Mapping types (对齐 16_mapping_tables.sql - posture_mapping)
export interface PostureMapping {
  mapping_id: string
  tenant_id: string
  
  // 分类
  category: string  // Posture/MotionState/SleepState
  
  // 厂家代码
  vendor_code: string  // 厂家原始代码
  firmware_version: string  // 固件版本（如 '1.4.0'）
  
  // SNOMED CT编码
  snomed_code?: string  // SNOMED CT编码
  snomed_display?: string  // SNOMED CT显示名称
  
  // LOINC编码
  loinc_code?: string  // LOINC编码（可选）
  
  // 描述
  description?: string  // 映射说明
  
  // 是否启用
  is_active: boolean  // 是否启用该映射
  
  created_at: string
  updated_at: string
}

// Event Mapping types (对齐 16_mapping_tables.sql - event_mapping)
export interface EventMapping {
  mapping_id: string
  tenant_id: string
  
  // 分类
  category: string  // RoomEvent/BedEvent/SafetyEvent
  
  // 厂家代码
  vendor_code: string  // 厂家原始代码
  firmware_version: string  // 固件版本（如 '1.4.0'）
  
  // SNOMED CT编码
  snomed_code?: string  // SNOMED CT编码
  snomed_display?: string  // SNOMED CT显示名称
  
  // LOINC编码
  loinc_code?: string  // LOINC编码（可选）
  
  // 描述
  description?: string  // 映射说明
  
  // 是否启用
  is_active: boolean  // 是否启用该映射
  
  created_at: string
  updated_at: string
}

// Resident types
export interface Resident {
  resident_id: string
  tenant_id: string
  HIS_resident_id?: string
  HIS_resident_bed_id?: string
  HIS_resident_status?: string
  resident_account: string
  first_name?: string
  last_name: string
  anonymous_name: string
  is_institutional: boolean
  location_id?: string
  bed_id?: string
  admission_date?: string
  status: string
  metadata?: any
  family_tag?: string
  family_member_account_1?: string
  can_view_status: boolean
  created_at: string
}

// Device types
export interface Device {
  device_id: string
  tenant_id: string
  device_name: string
  device_model: string
  device_type: string
  serial_number?: string
  uid?: string
  imei?: string
  comm_mode: string
  firmware_version?: string
  mcu_model?: string
  location_id?: string
  bound_room_id?: string
  bound_bed_id?: string
  status: string
  installed: boolean
  business_access: boolean
  monitoring_enabled: boolean
  installation_date_utc?: string
  metadata?: any
  created_at: string
}

// Alert types
export interface Alert {
  alert_id: string
  tenant_id: string
  alert_level: string
  alert_type: string
  message: string
  timestamp: string
  status: string
  resident_id?: string
  device_id?: string
  location_id?: string
  acknowledged_by?: string
  acknowledged_at?: string
  resolved_by?: string
  resolved_at?: string
  
  // 告警升级/抑制机制
  escalation_level?: number  // 0=初始, 1-3=升级次数
  escalated_at?: string
  suppressed_until?: string  // 抑制到期时间
  auto_escalate?: boolean    // 是否启用自动升级
}

// IoT Data types (对齐 12_iot_timeseries.sql)
export interface IoTData {
  // 主键和索引
  id: number  // BIGSERIAL in SQL
  tenant_id: string
  device_id: string
  
  // 时间戳
  timestamp: string
  
  // TDP Tag Category
  tdp_tag_category?: string  // Physiological/Behavioral/Posture/MotionState/SleepState/Safety/HealthCondition/DeviceError
  
  // 轨迹数据（必需）
  tracking_id?: number  // 0-7, null表示无人
  radar_pos_x: number  // 厘米
  radar_pos_y: number  // 厘米
  radar_pos_z: number  // 厘米
  
  // 姿态/运动状态
  posture_snomed_code?: string  // SNOMED CT编码
  posture_display?: string
  
  // 事件
  event_type?: string  // ENTER_ROOM, LEFT_BED等
  event_display?: string
  area_id?: number
  
  // 生命体征
  heart_rate?: number  // bpm
  respiratory_rate?: number  // 次/分钟（修正拼写）
  
  // 睡眠状态
  sleep_state_snomed_code?: string
  sleep_state_display?: string
  
  // 睡眠时段（TDPv2 SleepPeriod）
  sleep_period_start?: string  // HH:MM
  sleep_period_end?: string    // HH:MM
  
  // 位置信息
  location_id?: string
  room_id?: string
  
  // 其他字段
  confidence?: number  // 0-100
  remaining_time?: number  // 0-60秒
  
  // 原始记录（base64编码的字符串）
  raw_original: string  // bytes转为base64
  raw_format: string  // json/binary/xml/string
  raw_compression?: string  // gzip/deflate/null
  
  // 元数据
  metadata?: Record<string, any>
  
  created_at: string
}

// Card types
export interface Card {
  card_id: string
  tenant_id: string
  card_type: string  // 'ActiveBed' | 'Location'
  bed_id?: string
  location_id?: string
  card_name: string
  card_address: string
  resident_id?: string
  is_public_space: boolean
  routing_alert_user_ids?: string[]
  routing_alert_tags?: string[]  // 警报路由标签（新增）
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Location types
export interface Location {
  location_id: string
  tenant_id: string
  // 位置标签和名称
  location_tag?: string  // 位置标签（如 'A院区主楼'、'Spring区域组SP'）
  location_name: string  // 位置名称（如 'E203'、'201'、'Home-001'）
  // Institutional场景地址字段
  building?: string  // 楼栋（如 'Building A'、'主楼'）
  floor?: string  // 楼层（如 '1F'、'2F'）
  area_id?: string  // 区域ID（如 'Area A'、'Memory Care Unit'）
  door_number: string  // 门牌号/房间号（如 '201'、'E203'）
  // 布局和场景
  layout_config?: Record<string, any>  // 房间布局配置（vue_radar canvasData格式）
  location_type: string  // 场景类型：Institutional / HomeCare
  primary_resident_id?: string  // 主要关联住户ID
  // 空间属性
  is_public_space: boolean  // 是否为公共空间（大厅、走廊等）
  is_multi_person_room: boolean  // 是否多人房间
  // 路由和状态
  timezone: string  // IANA时区格式（如 'America/Los_Angeles'）
  alert_user_ids?: string[]  // 警报接收者用户ID列表
  alert_tags?: string[]  // 警报接收者标签组
  is_active: boolean  // 是否启用监控
  created_at: string
  updated_at: string
}

// Room types
export interface Room {
  room_id: string
  tenant_id: string
  location_id: string
  is_default: boolean  // 是否默认房间（创建Location时自动生成）
  room_name: string  // 房间名称（如 'Bedroom'、'Bathroom'）
  is_active: boolean  // 是否启用
  layout_config?: Record<string, any>  // 房间级独立布局配置
  created_at: string
  updated_at: string
}

// Bed types
export interface Bed {
  bed_id: string
  tenant_id: string
  location_id: string
  room_id: string
  bed_name: string  // 床位名称（如 'A'、'B'、'Bed1'）
  bed_type: string  // 床位类型：ActiveBed / NonActiveBed
  mattress_material?: string  // 床垫材质/类型
  mattress_thickness?: string  // 床垫厚度（如 '< 7in'、'7-10in'）
  resident_id?: string  // 绑定的住户ID
  created_at: string
  updated_at: string
}

// Care Quality types
export interface CareQualityMetrics {
  tenant_id: string
  time_range: string
  coverage_rate: number
  avg_response_time: number
  avg_care_duration: number
  total_interactions: number
}

// Resident Contact types (09_resident_contacts.sql)
export interface ResidentContact {
  contact_id: string
  tenant_id: string
  resident_id: string
  slot: string // A/B/C/D/E
  contact_resident_id?: string
  can_view_status: boolean
  can_receive_alert: boolean
  relationship?: string
  contact_first_name?: string
  contact_last_name?: string
  contact_phone?: string
  contact_email?: string
  contact_sms: boolean
  is_active: boolean
  created_at: string
}

// Resident Caregiver types (10_resident_caregivers.sql)
export interface ResidentCaregiver {
  id: string
  tenant_id: string
  resident_id: string
  caregiver_id1: string
  caregiver_id2?: string
  caregiver_id3?: string
  caregiver_id4?: string
  caregiver_id5?: string
  nurse_group_tags?: string[]
  created_at: string
}
