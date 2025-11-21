"""
创建示例PHI数据
注意：这仅用于开发测试，生产环境中PHI数据必须加密存储
"""

import asyncio
import uuid
from datetime import datetime, date
from app.services.storage import StorageService

# 使用与init_sample_data.py相同的住户ID
SAMPLE_TENANT_ID = "10000000-0000-0000-0000-000000000001"
SAMPLE_RESIDENT_ID = "60000000-0000-0000-0000-000000000001"
SAMPLE_RESIDENT_ID_2 = "60000000-0000-0000-0000-000000000002"


async def create_sample_phi():
    """创建示例PHI数据"""
    print("🔐 Creating sample PHI data...")
    print("⚠️  WARNING: This is for development only!")
    print("⚠️  In production, PHI must be encrypted!")
    print()
    
    storage = StorageService("resident_phi")
    
    # PHI数据应该加密存储，这里为了演示使用明文
    phi_records = [
        {
            "phi_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            # 真实身份信息（生产环境必须加密）
            "real_first_name": "明华",  # 演示数据，非真实
            "real_last_name": "王",
            "date_of_birth": "1945-03-15",
            "ssn_last_4": "1234",  # 社保号后4位
            # 联系方式
            "phone_number": "+86-138-1111-1111",
            "email": "resident001@example.com",
            # 紧急联系人
            "emergency_contact_name": "小明王",
            "emergency_contact_phone": "+86-139-2222-2222",
            "emergency_contact_relationship": "儿子",
            # 医疗信息
            "medical_history": "高血压、糖尿病（2型）、既往心脏病史",
            "medications": "降压药（每日1次）、二甲双胍（每日2次）",
            "allergies": "青霉素过敏",
            "blood_type": "A+",
            # 医保信息
            "insurance_provider": "中国人寿医疗保险",
            "insurance_policy_number": "CL2023001234",
            # 其他
            "metadata": {
                "created_by": "admin",
                "notes": "定期检查血压和血糖"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "phi_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "real_first_name": "秀英",
            "real_last_name": "李",
            "date_of_birth": "1950-08-20",
            "ssn_last_4": "5678",
            "phone_number": "+86-138-2222-2222",
            "email": "resident002@example.com",
            "emergency_contact_name": "小红李",
            "emergency_contact_phone": "+86-139-3333-3333",
            "emergency_contact_relationship": "女儿",
            "medical_history": "骨质疏松、轻度认知障碍",
            "medications": "钙片（每日1次）、维生素D（每日1次）",
            "allergies": "无已知过敏",
            "blood_type": "O+",
            "insurance_provider": "城镇职工医疗保险",
            "insurance_policy_number": "BJ2023005678",
            "metadata": {
                "created_by": "admin",
                "notes": "需要协助行动，防跌倒"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for phi in phi_records:
        storage.create(phi)
        print(f"✅ Created PHI for resident: {phi['real_last_name']}{phi['real_first_name']}")
    
    print()
    print("=" * 70)
    print("✅ PHI data creation completed!")
    print("=" * 70)
    print()
    print("📋 Created PHI records:")
    print(f"  - Total: {len(phi_records)}")
    print(f"  - Resident 1: 王明华")
    print(f"  - Resident 2: 李秀英")
    print()
    print("🔐 Security Notes:")
    print("  ⚠️  These are UNENCRYPTED demo records")
    print("  ⚠️  Production systems MUST encrypt PHI data")
    print("  ⚠️  Access requires strict HIPAA compliance")
    print("  ⚠️  All access must be audited")
    print()
    print("🌐 Test API:")
    print("  GET /api/v1/resident_phi?tenant_id=10000000-0000-0000-0000-000000000001")
    print(f"  GET /api/v1/residents/{SAMPLE_RESIDENT_ID}/phi")
    print()


if __name__ == "__main__":
    asyncio.run(create_sample_phi())
