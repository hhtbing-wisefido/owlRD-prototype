# 自动化对齐验证报告

**生成时间**: 1763703801.9416003

```
================================================================================
🔍 数据对齐验证报告
================================================================================

📊 总体统计:
  - 总表数: 18
  - 完美对齐: 1 (5.6%)
  - 平均对齐度: 49.3%

❌ resident_phi - 0.0%
  SQL文件: 08_resident_phi.sql
  Model文件: resident
  SQL字段数: 25
  Model字段数: 33
  ⚠️  Model多余字段: tenant_id, home_address_state, resident_id, home_address_postal_code, plus_code, phi_id, home_address_street, home_address_city
  ⚠️  类型不匹配:
      tremor_status: SQL=str, Model=Union
      comm_status: SQL=str, Model=Union
      resident_email: SQL=str, Model=Union
      resident_phone: SQL=str, Model=Union
      has_hyperglycaemia: SQL=bool, Model=Union
      weight_lb: SQL=float, Model=Union
      last_name: SQL=str, Model=Union
      has_hypertension: SQL=bool, Model=Union
      HIS_resident_name: SQL=str, Model=Union
      has_hyperlipaemia: SQL=bool, Model=Union
      medical_history: SQL=str, Model=Union
      height_ft: SQL=float, Model=Union
      HIS_resident_metadata: SQL=dict, Model=Union
      mobility_aid: SQL=str, Model=Union
      adl_assistance: SQL=str, Model=Union
      has_paralysis: SQL=bool, Model=Union
      has_stroke_history: SQL=bool, Model=Union
      first_name: SQL=str, Model=Union
      date_of_birth: SQL=datetime, Model=Union
      HIS_resident_admission_date: SQL=datetime, Model=Union
      has_alzheimer: SQL=bool, Model=Union
      mobility_level: SQL=int, Model=Union
      gender: SQL=str, Model=Union
      height_in: SQL=float, Model=Union
      HIS_resident_discharge_date: SQL=datetime, Model=Union

❌ resident_caregivers - 0.0%
  SQL文件: 10_resident_caregivers.sql
  Model文件: resident
  SQL字段数: 1
  Model字段数: 9
  ⚠️  Model多余字段: id, tenant_id, caregiver_id2, caregiver_id1, caregiver_id4, caregiver_id5, caregiver_id3, resident_id
  ⚠️  类型不匹配:
      caregivers_tags: SQL=dict, Model=Union

❌ cloud_alert_policies - 10.7%
  SQL文件: 14_cloud_alert_policies.sql
  Model文件: alert
  SQL字段数: 28
  Model字段数: 29
  ⚠️  Model多余字段: tenant_id
  ⚠️  类型不匹配:
      Stay: SQL=str, Model=Union
      notification_rules: SQL=dict, Model=Union
      SleepPad_InBed: SQL=str, Model=Union
      SleepPad_SitUp: SQL=str, Model=Union
      Radar_LeftBed: SQL=str, Model=Union
      Radar_AbnormalHeartRate: SQL=str, Model=Union
      SleepPad_AbnormalRespiratoryRate: SQL=str, Model=Union
      conditions: SQL=dict, Model=Union
      SleepPad_AbnormalBodyMovement: SQL=str, Model=Union
      OfflineAlarm: SQL=str, Model=Union
      AngleException: SQL=str, Model=Union
      Fall: SQL=str, Model=Union
      CustomAlert2: SQL=str, Model=Union
      SleepPad_LeftBed: SQL=str, Model=Union
      SuspectedFall: SQL=str, Model=Union
      LowBattery: SQL=str, Model=Union
      NoActivity24h: SQL=str, Model=Union
      SleepPad_AbnormalHeartRate: SQL=str, Model=Union
      CustomAlert1: SQL=str, Model=Union
      CustomAlert3: SQL=str, Model=Union
      VitalsWeak: SQL=str, Model=Union
      DeviceFailure: SQL=str, Model=Union
      SleepPad_ApneaHypopnea: SQL=str, Model=Union
      Radar_AbnormalRespiratoryRate: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union

❌ users - 14.3%
  SQL文件: 03_users.sql
  Model文件: user
  SQL字段数: 14
  Model字段数: 18
  ⚠️  Model多余字段: tenant_id, updated_at, created_at, user_id
  ⚠️  类型不匹配:
      email: SQL=str, Model=Union
      email_hash: SQL=bytes, Model=Union
      last_login_at: SQL=datetime, Model=Union
      pin_hash: SQL=bytes, Model=Union
      phone: SQL=str, Model=Union
      alert_scope: SQL=str, Model=Union
      alert_levels: SQL=str, Model=Union
      username: SQL=str, Model=Union
      password_hash: SQL=bytes, Model=Union
      phone_hash: SQL=bytes, Model=Union
      alert_channels: SQL=str, Model=Union
      tags: SQL=dict, Model=Union

❌ residents - 29.4%
  SQL文件: 07_residents.sql
  Model文件: resident
  SQL字段数: 17
  Model字段数: 20
  ❌ Model缺少字段: WHERE
  ⚠️  Model多余字段: tenant_id, location_id, resident_id, bed_id
  ⚠️  类型不匹配:
      anonymous_name: SQL=str, Model=Union
      email_hash: SQL=bytes, Model=Union
      admission_date: SQL=datetime, Model=date
      HIS_resident_bed_id: SQL=str, Model=Union
      family_tag: SQL=str, Model=Union
      first_name: SQL=str, Model=Union
      HIS_resident_status: SQL=str, Model=Union
      HIS_resident_id: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union
      phone_hash: SQL=bytes, Model=Union
      family_member_account_1: SQL=str, Model=Union

❌ iot_timeseries - 39.1%
  SQL文件: 12_iot_timeseries.sql
  Model文件: iot_data
  SQL字段数: 23
  Model字段数: 27
  ⚠️  Model多余字段: tenant_id, device_id, room_id, location_id
  ⚠️  类型不匹配:
      tracking_id: SQL=int, Model=Union
      heart_rate: SQL=int, Model=Union
      sleep_state_display: SQL=str, Model=Union
      posture_display: SQL=str, Model=Union
      confidence: SQL=int, Model=Union
      respiratory_rate: SQL=int, Model=Union
      remaining_time: SQL=int, Model=Union
      tdp_tag_category: SQL=str, Model=Union
      area_id: SQL=int, Model=Union
      raw_compression: SQL=str, Model=Union
      event_type: SQL=str, Model=Union
      posture_snomed_code: SQL=str, Model=Union
      event_display: SQL=str, Model=Union
      sleep_state_snomed_code: SQL=str, Model=Union

❌ resident_contacts - 41.7%
  SQL文件: 09_resident_contacts.sql
  Model文件: resident
  SQL字段数: 12
  Model字段数: 16
  ⚠️  Model多余字段: tenant_id, contact_id, contact_resident_id, resident_id
  ⚠️  类型不匹配:
      email_hash: SQL=bytes, Model=Union
      contact_first_name: SQL=str, Model=Union
      contact_last_name: SQL=str, Model=Union
      relationship: SQL=str, Model=Union
      contact_phone: SQL=str, Model=Union
      contact_email: SQL=str, Model=Union
      phone_hash: SQL=bytes, Model=Union

❌ cards - 42.9%
  SQL文件: 18_cards.sql
  Model文件: card
  SQL字段数: 7
  Model字段数: 12
  ⚠️  Model多余字段: tenant_id, bed_id, resident_id, location_id, card_id
  ⚠️  类型不匹配:
      routing_alert_tags: SQL=str, Model=Union
      routing_alert_user_ids: SQL=UUID, Model=Union
      card_type: SQL=str, Model=CardType
      is_public_space: SQL=bool, Model=Union

❌ locations - 53.3%
  SQL文件: 04_locations.sql
  Model文件: location
  SQL字段数: 15
  Model字段数: 17
  ⚠️  Model多余字段: tenant_id, primary_resident_id
  ⚠️  类型不匹配:
      floor: SQL=str, Model=Union
      location_tag: SQL=str, Model=Union
      building: SQL=str, Model=Union
      alert_tags: SQL=str, Model=Union
      alert_user_ids: SQL=UUID, Model=Union
      area_id: SQL=str, Model=Union
      layout_config: SQL=dict, Model=Union

❌ posture_mapping - 55.6%
  SQL文件: 16_mapping_tables.sql
  Model文件: mapping
  SQL字段数: 9
  Model字段数: 12
  ⚠️  Model多余字段: vendor_code, tenant_id, mapping_id
  ⚠️  类型不匹配:
      snomed_code: SQL=str, Model=Union
      loinc_code: SQL=str, Model=Union
      snomed_display: SQL=str, Model=Union
      description: SQL=str, Model=Union

❌ event_mapping - 55.6%
  SQL文件: 16_mapping_tables.sql
  Model文件: mapping
  SQL字段数: 9
  Model字段数: 12
  ⚠️  Model多余字段: vendor_code, tenant_id, mapping_id
  ⚠️  类型不匹配:
      snomed_code: SQL=str, Model=Union
      loinc_code: SQL=str, Model=Union
      snomed_display: SQL=str, Model=Union
      description: SQL=str, Model=Union

❌ beds - 66.7%
  SQL文件: 06_beds.sql
  Model文件: location
  SQL字段数: 6
  Model字段数: 11
  ⚠️  Model多余字段: tenant_id, room_id, location_id, resident_id, bed_id
  ⚠️  类型不匹配:
      mattress_thickness: SQL=str, Model=Union
      mattress_material: SQL=str, Model=Union

❌ devices - 66.7%
  SQL文件: 11_devices.sql
  Model文件: device
  SQL字段数: 15
  Model字段数: 20
  ⚠️  Model多余字段: tenant_id, device_id, bound_bed_id, bound_room_id, location_id
  ⚠️  类型不匹配:
      uid: SQL=str, Model=Union
      mcu_model: SQL=str, Model=Union
      serial_number: SQL=str, Model=Union
      imei: SQL=str, Model=Union
      metadata: SQL=dict, Model=Union

❌ config_versions - 71.4%
  SQL文件: 15_config_versions.sql
  Model文件: config_version
  SQL字段数: 7
  Model字段数: 11
  ⚠️  Model多余字段: tenant_id, updated_at, created_at, version_id
  ⚠️  类型不匹配:
      current_entity_id: SQL=UUID, Model=Union
      valid_to: SQL=datetime, Model=Union

❌ rooms - 75.0%
  SQL文件: 05_rooms.sql
  Model文件: location
  SQL字段数: 4
  Model字段数: 7
  ⚠️  Model多余字段: tenant_id, room_id, location_id
  ⚠️  类型不匹配:
      layout_config: SQL=dict, Model=Union

⚠️ tenants - 80.0%
  SQL文件: 01_tenants.sql
  Model文件: tenant
  SQL字段数: 5
  Model字段数: 7
  ⚠️  Model多余字段: domain, tenant_id
  ⚠️  类型不匹配:
      metadata: SQL=dict, Model=Union

⚠️ roles - 85.7%
  SQL文件: 02_roles.sql
  Model文件: role
  SQL字段数: 7
  Model字段数: 9
  ⚠️  Model多余字段: tenant_id, role_id
  ⚠️  类型不匹配:
      description: SQL=str, Model=Union

✅ iot_monitor_alerts - 100.0%
  SQL文件: 13_iot_monitor_alerts.sql
  Model文件: iot_data
  SQL字段数: 4
  Model字段数: 7
  ⚠️  Model多余字段: tenant_id, device_id, alert_config_id

================================================================================
```
