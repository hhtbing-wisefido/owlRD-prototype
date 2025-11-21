# 自动化对齐验证报告

**生成时间**: 1763702848.0713024

```
================================================================================
🔍 数据对齐验证报告
================================================================================

📊 总体统计:
  - 总表数: 18
  - 完美对齐: 1 (5.6%)
  - 平均对齐度: 28.5%

❌ roles - 0.0%
  SQL文件: 02_roles.sql
  Model文件: role
  SQL字段数: 7
  Model字段数: 0
  ❌ Model缺少字段: is_system, description, role_code, is_active, created_at, updated_at, display_name

❌ rooms - 0.0%
  SQL文件: 05_rooms.sql
  Model文件: room
  SQL字段数: 4
  Model字段数: 0
  ❌ Model缺少字段: layout_config, is_default, is_active, room_name

❌ beds - 0.0%
  SQL文件: 06_beds.sql
  Model文件: bed
  SQL字段数: 6
  Model字段数: 0
  ❌ Model缺少字段: mattress_thickness, bound_device_count, bed_type, is_active, bed_name, mattress_material

❌ resident_phi - 0.0%
  SQL文件: 08_resident_phi.sql
  Model文件: resident_phi
  SQL字段数: 25
  Model字段数: 0
  ❌ Model缺少字段: has_stroke_history, mobility_aid, resident_phone, has_paralysis, HIS_resident_name, weight_lb, has_hyperglycaemia, tremor_status, mobility_level, HIS_resident_discharge_date, gender, comm_status, has_hyperlipaemia, has_hypertension, last_name, height_in, HIS_resident_metadata, has_alzheimer, height_ft, date_of_birth, adl_assistance, medical_history, HIS_resident_admission_date, first_name, resident_email

❌ resident_contacts - 0.0%
  SQL文件: 09_resident_contacts.sql
  Model文件: resident_contact
  SQL字段数: 12
  Model字段数: 0
  ❌ Model缺少字段: can_view_status, contact_phone, contact_first_name, can_receive_alert, contact_last_name, email_hash, phone_hash, slot, contact_sms, is_active, contact_email, relationship

❌ resident_caregivers - 0.0%
  SQL文件: 10_resident_caregivers.sql
  Model文件: resident_caregiver
  SQL字段数: 1
  Model字段数: 0
  ❌ Model缺少字段: caregivers_tags

❌ posture_mapping - 0.0%
  SQL文件: 16_mapping_tables.sql
  Model文件: mapping
  SQL字段数: 9
  Model字段数: 0
  ❌ Model缺少字段: snomed_display, description, category, loinc_code, snomed_code, firmware_version, is_active, created_at, updated_at

❌ event_mapping - 0.0%
  SQL文件: 16_mapping_tables.sql
  Model文件: mapping
  SQL字段数: 9
  Model字段数: 0
  ❌ Model缺少字段: snomed_display, description, category, loinc_code, snomed_code, firmware_version, is_active, created_at, updated_at

❌ cloud_alert_policies - 10.7%
  SQL文件: 14_cloud_alert_policies.sql
  Model文件: alert
  SQL字段数: 28
  Model字段数: 29
  ⚠️  Model多余字段: tenant_id
  ⚠️  类型不匹配:
      Radar_LeftBed: SQL=str, Model=Union
      Radar_AbnormalRespiratoryRate: SQL=str, Model=Union
      LowBattery: SQL=str, Model=Union
      SleepPad_AbnormalHeartRate: SQL=str, Model=Union
      SleepPad_InBed: SQL=str, Model=Union
      OfflineAlarm: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union
      SleepPad_AbnormalRespiratoryRate: SQL=str, Model=Union
      notification_rules: SQL=dict, Model=Union
      SleepPad_SitUp: SQL=str, Model=Union
      CustomAlert3: SQL=str, Model=Union
      SleepPad_AbnormalBodyMovement: SQL=str, Model=Union
      SleepPad_LeftBed: SQL=str, Model=Union
      SuspectedFall: SQL=str, Model=Union
      Fall: SQL=str, Model=Union
      VitalsWeak: SQL=str, Model=Union
      AngleException: SQL=str, Model=Union
      CustomAlert1: SQL=str, Model=Union
      SleepPad_ApneaHypopnea: SQL=str, Model=Union
      conditions: SQL=dict, Model=Union
      DeviceFailure: SQL=str, Model=Union
      Radar_AbnormalHeartRate: SQL=str, Model=Union
      Stay: SQL=str, Model=Union
      CustomAlert2: SQL=str, Model=Union
      NoActivity24h: SQL=str, Model=Union

❌ users - 14.3%
  SQL文件: 03_users.sql
  Model文件: user
  SQL字段数: 14
  Model字段数: 18
  ⚠️  Model多余字段: tenant_id, user_id, updated_at, created_at
  ⚠️  类型不匹配:
      alert_channels: SQL=str, Model=Union
      tags: SQL=dict, Model=Union
      email_hash: SQL=bytes, Model=Union
      password_hash: SQL=bytes, Model=Union
      alert_scope: SQL=str, Model=Union
      phone_hash: SQL=bytes, Model=Union
      phone: SQL=str, Model=Union
      alert_levels: SQL=str, Model=Union
      last_login_at: SQL=datetime, Model=Union
      email: SQL=str, Model=Union
      username: SQL=str, Model=Union
      pin_hash: SQL=bytes, Model=Union

❌ residents - 35.3%
  SQL文件: 07_residents.sql
  Model文件: resident
  SQL字段数: 17
  Model字段数: 20
  ❌ Model缺少字段: WHERE
  ⚠️  Model多余字段: tenant_id, resident_id, bed_id, location_id
  ⚠️  类型不匹配:
      family_tag: SQL=str, Model=Union
      admission_date: SQL=datetime, Model=date
      HIS_resident_bed_id: SQL=str, Model=Union
      HIS_resident_id: SQL=str, Model=Union
      email_hash: SQL=bytes, Model=Union
      phone_hash: SQL=bytes, Model=Union
      family_member_account_1: SQL=str, Model=Union
      HIS_resident_status: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union
      first_name: SQL=str, Model=Union

❌ iot_timeseries - 39.1%
  SQL文件: 12_iot_timeseries.sql
  Model文件: iot_data
  SQL字段数: 23
  Model字段数: 27
  ⚠️  Model多余字段: tenant_id, device_id, room_id, location_id
  ⚠️  类型不匹配:
      event_display: SQL=str, Model=Union
      sleep_state_snomed_code: SQL=str, Model=Union
      posture_snomed_code: SQL=str, Model=Union
      tdp_tag_category: SQL=str, Model=Union
      heart_rate: SQL=int, Model=Union
      confidence: SQL=int, Model=Union
      sleep_state_display: SQL=str, Model=Union
      event_type: SQL=str, Model=Union
      raw_compression: SQL=str, Model=Union
      respiratory_rate: SQL=int, Model=Union
      tracking_id: SQL=int, Model=Union
      remaining_time: SQL=int, Model=Union
      posture_display: SQL=str, Model=Union
      area_id: SQL=int, Model=Union

❌ cards - 42.9%
  SQL文件: 18_cards.sql
  Model文件: card
  SQL字段数: 7
  Model字段数: 12
  ⚠️  Model多余字段: resident_id, card_id, tenant_id, location_id, bed_id
  ⚠️  类型不匹配:
      card_type: SQL=str, Model=CardType
      is_public_space: SQL=bool, Model=Union
      routing_alert_user_ids: SQL=UUID, Model=Union
      routing_alert_tags: SQL=str, Model=Union

❌ locations - 53.3%
  SQL文件: 04_locations.sql
  Model文件: location
  SQL字段数: 15
  Model字段数: 17
  ⚠️  Model多余字段: tenant_id, primary_resident_id
  ⚠️  类型不匹配:
      location_tag: SQL=str, Model=Union
      layout_config: SQL=dict, Model=Union
      building: SQL=str, Model=Union
      floor: SQL=str, Model=Union
      area_id: SQL=str, Model=Union
      alert_user_ids: SQL=UUID, Model=Union
      alert_tags: SQL=str, Model=Union

❌ devices - 66.7%
  SQL文件: 11_devices.sql
  Model文件: device
  SQL字段数: 15
  Model字段数: 20
  ⚠️  Model多余字段: bound_bed_id, tenant_id, bound_room_id, location_id, device_id
  ⚠️  类型不匹配:
      serial_number: SQL=str, Model=Union
      uid: SQL=str, Model=Union
      imei: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union
      mcu_model: SQL=str, Model=Union

❌ config_versions - 71.4%
  SQL文件: 15_config_versions.sql
  Model文件: config_version
  SQL字段数: 7
  Model字段数: 11
  ⚠️  Model多余字段: tenant_id, updated_at, version_id, created_at
  ⚠️  类型不匹配:
      current_entity_id: SQL=UUID, Model=Union
      valid_to: SQL=datetime, Model=Union

⚠️ tenants - 80.0%
  SQL文件: 01_tenants.sql
  Model文件: tenant
  SQL字段数: 5
  Model字段数: 7
  ⚠️  Model多余字段: tenant_id, domain
  ⚠️  类型不匹配:
      metadata: SQL=dict, Model=Union

✅ iot_monitor_alerts - 100.0%
  SQL文件: 13_iot_monitor_alerts.sql
  Model文件: iot_data
  SQL字段数: 4
  Model字段数: 7
  ⚠️  Model多余字段: tenant_id, alert_config_id, device_id

================================================================================
```
