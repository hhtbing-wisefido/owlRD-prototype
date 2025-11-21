# 前端类型对齐验证报告

**生成时间**: 1763704459.3813689

```
================================================================================
🔍 前端类型对齐验证报告
================================================================================

📊 总体统计:
  - 总类型数: 13
  - 完美对齐: 5 (38.5%)
  - 良好对齐: 2 (15.4%)
  - 部分对齐: 2 (15.4%)
  - 严重不对齐: 2 (15.4%)
  - 平均对齐度: 85.5%

❌ Python Model Alert 不存在 Alert - 0.0%
  TypeScript: 14 fields
  Python Model: 0 fields

❌ 严重不对齐 User - 55.6%
  TypeScript: 15 fields
  Python Model: 18 fields
  ⚠️  TS缺少字段: last_login_at, phone_hash, pin_hash, password_hash, email_hash
  ⚠️  Python缺少字段: shift, nurse_group, department, certifications
  ⚠️  类型不匹配:
      tags: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 部分对齐 Card - 83.3%
  TypeScript: 12 fields
  Python Model: 12 fields
  ⚠️  TS缺少字段: routing_alert_tags
  ⚠️  Python缺少字段: created_at
  ⚠️  类型不匹配:
      card_type: TS=string, Py=<enum 'CardType'>

⚠️ 部分对齐 Tenant - 85.7%
  TypeScript: 14 fields
  Python Model: 7 fields
  ⚠️  Python缺少字段: license_type, contact_phone, address, max_users, features_enabled
      ... 等共7个
  ⚠️  类型不匹配:
      metadata: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 良好对齐 Resident - 90.0%
  TypeScript: 19 fields
  Python Model: 20 fields
  ⚠️  TS缺少字段: phone_hash, email_hash
  ⚠️  Python缺少字段: created_at

⚠️ 良好对齐 IoTData - 96.3%
  TypeScript: 27 fields
  Python Model: 27 fields
  ⚠️  类型不匹配:
      raw_original: TS=string, Py=<class 'bytes'>

✅ 完美对齐 Role - 100.0%
  TypeScript: 9 fields
  Python Model: 9 fields

✅ 完美对齐 ResidentPHI - 100.0%
  TypeScript: 33 fields
  Python Model: 33 fields

⚠️ 良好对齐 Device - 100.0%
  TypeScript: 21 fields
  Python Model: 20 fields
  ⚠️  Python缺少字段: created_at

✅ 完美对齐 CloudAlertPolicy - 100.0%
  TypeScript: 29 fields
  Python Model: 29 fields

⚠️ 良好对齐 ConfigVersion - 100.0%
  TypeScript: 13 fields
  Python Model: 11 fields
  ⚠️  Python缺少字段: created_by, metadata

✅ 完美对齐 PostureMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

✅ 完美对齐 EventMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

================================================================================
```
