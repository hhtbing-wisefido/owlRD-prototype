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
            # 基本PHI（符合模型字段名）
            "first_name": "明华",  # 演示数据，非真实
            "last_name": "王",
            "gender": "Male",
            "date_of_birth": "1945-03-15",
            "resident_phone": "+86-138-1111-1111",
            "resident_email": "wang.minghua@example.com",
            # 生物特征
            "weight_lb": "154.0",  # 70kg ≈ 154磅
            "height_ft": "5.0",
            "height_in": "7.0",  # 5英尺7英寸 ≈ 170cm
            # 功能性活动能力
            "mobility_level": 3,  # 需要部分协助
            "tremor_status": "Mild",
            "mobility_aid": "Cane",
            "adl_assistance": "NeedsHelp",
            "comm_status": "Normal",
            # 慢性病史
            "has_hypertension": True,
            "has_hyperglycaemia": True,
            "has_stroke_history": False,
            "has_paralysis": False,
            "has_alzheimer": False,
            "has_hyperlipaemia": False,
            "medical_history": "高血压病史10年，糖尿病5年，控制良好",
            # HIS系统同步字段
            "HIS_resident_name": "王明华",
            "HIS_resident_admission_date": "2023-01-15",
            "HIS_resident_metadata": {
                "medical_record_number": "MR-2023-001",
                "primary_physician": "张医生"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "phi_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            # 基本PHI
            "first_name": "秀英",
            "last_name": "李",
            "gender": "Female",
            "date_of_birth": "1950-08-20",
            "resident_phone": "+86-138-2222-2222",
            "resident_email": "li.xiuying@example.com",
            # 生物特征
            "weight_lb": "121.0",  # 55kg ≈ 121磅
            "height_ft": "5.0",
            "height_in": "3.0",  # 5英尺3英寸 ≈ 160cm
            # 功能性活动能力
            "mobility_level": 2,  # 需要较多协助
            "tremor_status": "None",
            "mobility_aid": "Wheelchair",
            "adl_assistance": "NeedsHelp",
            "comm_status": "Normal",
            # 慢性病史
            "has_hypertension": False,
            "has_hyperglycaemia": False,
            "has_stroke_history": False,
            "has_paralysis": False,
            "has_alzheimer": True,
            "has_hyperlipaemia": False,
            "medical_history": "轻度认知障碍，骨质疏松",
            # HIS系统同步字段
            "HIS_resident_name": "李秀英",
            "HIS_resident_admission_date": "2023-02-20",
            "HIS_resident_metadata": {
                "medical_record_number": "MR-2023-002",
                "primary_physician": "李医生"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for phi in phi_records:
        storage.create(phi)
        print(f"✅ Created PHI for resident: {phi['last_name']}{phi['first_name']}")
    
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
