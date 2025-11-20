// Tenant types
export interface Tenant {
  tenant_id: string
  tenant_name: string
  tenant_code: string
  contact_email?: string
  contact_phone?: string
  address?: string
  license_type: string
  max_users: number
  max_residents: number
  features_enabled: string[]
  is_active: boolean
  created_at: string
}

// User types
export interface User {
  user_id: string
  tenant_id: string
  username: string
  full_name: string
  email?: string
  phone?: string
  role: string
  department?: string
  nurse_group_tag?: string
  is_active: boolean
  created_at: string
}

// Resident types
export interface Resident {
  resident_id: string
  tenant_id: string
  resident_account: string
  last_name: string
  is_institutional: boolean
  location_id?: string
  bed_id?: string
  admission_date?: string
  status: string
  can_view_status: boolean
  primary_contact_name?: string
  primary_contact_phone?: string
  primary_contact_relation?: string
  anonymous_display_name?: string
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
  comm_mode: string
  firmware_version?: string
  location_id?: string
  status: string
  installed: boolean
  business_access: boolean
  monitoring_enabled: boolean
  installation_date_utc?: string
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

// Care Quality types
export interface CareQualityMetrics {
  tenant_id: string
  time_range: string
  coverage_rate: number
  avg_response_time: number
  avg_care_duration: number
  total_interactions: number
}
