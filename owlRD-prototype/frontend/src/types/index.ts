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
  role_id: string
  tenant_id: string
  role_code: string
  display_name: string
  description?: string
  is_system: boolean
  is_active: boolean
  created_at: string
  updated_at: string
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
  location_name: string
  address?: string
  is_public_space: boolean
  is_multi_person_room: boolean
  alert_user_ids?: string[]
  alert_tags?: string[]
  metadata?: any
  created_at: string
}

// Room types
export interface Room {
  room_id: string
  tenant_id: string
  location_id: string
  room_number: string
  room_type?: string
  capacity?: number
  floor?: number
  is_occupied: boolean
  metadata?: any
  created_at: string
}

// Bed types
export interface Bed {
  bed_id: string
  tenant_id: string
  room_id: string
  bed_number: string
  resident_id?: string
  is_occupied: boolean
  metadata?: any
  created_at: string
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
