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

// Resident PHI types
export interface ResidentPHI {
  phi_id: string
  resident_id: string
  tenant_id: string
  encrypted_medical_history?: string
  encrypted_medications?: string
  encrypted_allergies?: string
  encrypted_conditions?: string
  encrypted_notes?: string
  encryption_method?: string
  last_updated_by?: string
  created_at: string
  updated_at: string
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

// Posture Mapping types
export interface PostureMapping {
  mapping_id: string
  tenant_id: string
  raw_posture: string
  snomed_code?: string
  snomed_display?: string
  loinc_code?: string
  loinc_display?: string
  risk_level?: string
  description?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

// Event Mapping types
export interface EventMapping {
  mapping_id: string
  tenant_id: string
  event_type: string
  event_subtype?: string
  snomed_code?: string
  snomed_display?: string
  loinc_code?: string
  loinc_display?: string
  severity?: string
  description?: string
  metadata?: Record<string, any>
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
}

// IoT Data types
export interface IoTData {
  id: string
  tenant_id: string
  device_id: string
  resident_id?: string
  bed_id?: string
  location_id?: string
  timestamp: string
  heart_rate?: number
  respiration_rate?: number
  motion_intensity?: number
  presence: boolean
  in_bed?: boolean
  alert_triggered: boolean
  alert_type?: string
  alert_level?: string
  data_source: string
  created_at: string
}

// Card types
export interface Card {
  card_id: string
  tenant_id: string
  card_type: string
  bed_id?: string
  location_id?: string
  card_name: string
  card_address: string
  resident_id?: string
  is_public_space: boolean
  routing_alert_user_ids?: string[]
  is_active: boolean
  created_at: string
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
