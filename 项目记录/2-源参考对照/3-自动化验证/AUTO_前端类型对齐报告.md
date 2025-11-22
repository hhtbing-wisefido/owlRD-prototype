# 前端类型对齐验证报告

**生成时间**: 1763781132.173281

```
================================================================================
🔍 前端类型对齐验证报告
================================================================================

📊 总体统计:
  - 总类型数: 13
  - 完美对齐: 8 (61.5%)
  - 良好对齐: 3 (23.1%)
  - 部分对齐: 1 (7.7%)
  - 严重不对齐: 1 (7.7%)
  - 平均对齐度: 93.9%

❌ 严重不对齐 User - 55.6%
  TypeScript: 15 fields
  Python Model: 18 fields
  ⚠️  TS缺少字段: pin_hash, last_login_at, email_hash, password_hash, phone_hash
  ⚠️  Python缺少字段: nurse_group, shift, department, certifications
  ⚠️  类型不匹配:
      tags: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 部分对齐 Tenant - 85.7%
  TypeScript: 14 fields
  Python Model: 7 fields
  ⚠️  Python缺少字段: max_residents, contact_phone, contact_email, address, max_users
      ... 等共7个
  ⚠️  类型不匹配:
      metadata: TS={, Py=typing.Optional[typing.Dict[str, typing.Any]]

⚠️ 良好对齐 Resident - 90.5%
  TypeScript: 19 fields
  Python Model: 21 fields
  ⚠️  TS缺少字段: email_hash, phone_hash

⚠️ 良好对齐 Card - 92.9%
  TypeScript: 14 fields
  Python Model: 14 fields
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

✅ 完美对齐 Device - 100.0%
  TypeScript: 21 fields
  Python Model: 21 fields

✅ 完美对齐 Alert - 100.0%
  TypeScript: 14 fields
  Python Model: 14 fields

✅ 完美对齐 CloudAlertPolicy - 100.0%
  TypeScript: 29 fields
  Python Model: 29 fields

✅ 完美对齐 ConfigVersion - 100.0%
  TypeScript: 13 fields
  Python Model: 13 fields

✅ 完美对齐 PostureMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

✅ 完美对齐 EventMapping - 100.0%
  TypeScript: 12 fields
  Python Model: 12 fields

================================================================================
```
