# 前端类型对齐验证报告

**生成时间**: 1763704459.3813689

```
================================================================================
🔍 前端类型对齐验证报告
================================================================================

📊 总体统计:
  - 总类型数: 13
  - 完美对齐: 6 (46.2%)
  - 良好对齐: 3 (23.1%)
  - 部分对齐: 1 (7.7%)
  - 严重不对齐: 1 (7.7%)
  - 平均对齐度: 93.8%

❌ 严重不对齐 User - 55.6%
  TypeScript: 15 fields
  Python Model: 18 fields
  ⚠️  TS缺少字段: phone_hash, email_hash, last_login_at, password_hash, pin_hash
  ⚠️  Python缺少字段: certifications, shift, department, nurse_group
  ⚠️  类型不匹配:
      tags: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 部分对齐 Tenant - 85.7%
  TypeScript: 14 fields
  Python Model: 7 fields
  ⚠️  Python缺少字段: max_users, address, license_type, contact_email, contact_phone
      ... 等共7个
  ⚠️  类型不匹配:
      metadata: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 良好对齐 Resident - 90.0%
  TypeScript: 19 fields
  Python Model: 20 fields
  ⚠️  TS缺少字段: phone_hash, email_hash
  ⚠️  Python缺少字段: created_at

⚠️ 良好对齐 Card - 91.7%
  TypeScript: 14 fields
  Python Model: 12 fields
  ⚠️  Python缺少字段: updated_at, created_at
  ⚠️  类型不匹配:
      card_type: TS=string, Py=<enum 'CardType'>

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

✅ 完美对齐 Alert - 100.0%
  TypeScript: 14 fields
  Python Model: 14 fields

✅ 完美对齐 CloudAlertPolicy - 100.0%
  TypeScript: 29 fields
  Python Model: 29 fields

⚠️ 良好对齐 ConfigVersion - 100.0%
  TypeScript: 13 fields
  Python Model: 11 fields
  ⚠️  Python缺少字段: metadata, created_by

✅ 完美对齐 PostureMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

✅ 完美对齐 EventMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

================================================================================
```
