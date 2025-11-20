"""
示例数据初始化脚本

功能：
- 创建示例租户、用户、住户、设备
- 生成示例IoT数据
- 创建示例卡片
- 便于系统演示和测试
"""

import asyncio
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from app.services.storage import StorageService


# 示例数据
SAMPLE_TENANT_ID = "10000000-0000-0000-0000-000000000001"
SAMPLE_USER_ID = "20000000-0000-0000-0000-000000000001"
SAMPLE_LOCATION_ID = "30000000-0000-0000-0000-000000000001"
SAMPLE_ROOM_ID = "40000000-0000-0000-0000-000000000001"
SAMPLE_BED_ID = "50000000-0000-0000-0000-000000000001"
SAMPLE_RESIDENT_ID = "60000000-0000-0000-0000-000000000001"
SAMPLE_DEVICE_ID = "70000000-0000-0000-0000-000000000001"


async def init_tenants():
    """初始化租户"""
    print("🏢 Creating sample tenant...")
    storage = StorageService("tenants")
    
    tenant = {
        "tenant_id": SAMPLE_TENANT_ID,
        "tenant_name": "示例养老院",
        "tenant_code": "DEMO001",
        "contact_email": "admin@demo-facility.com",
        "contact_phone": "+86-138-0000-0001",
        "address": "北京市朝阳区示例路123号",
        "license_type": "ENTERPRISE",
        "max_users": 100,
        "max_residents": 200,
        "features_enabled": ["IOT", "ALERTS", "CARE_QUALITY", "CARDS"],
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    storage.create(tenant)
    print(f"✅ Created tenant: {tenant['tenant_name']}")


async def init_users():
    """初始化用户"""
    print("\n👤 Creating sample users...")
    storage = StorageService("users")
    
    users = [
        {
            "user_id": SAMPLE_USER_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "admin",
            "full_name": "管理员",
            "email": "admin@demo.com",
            "phone": "+86-138-0000-0001",
            "role": "ADMIN",
            "department": "管理部",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "user_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "nurse01",
            "full_name": "护士张三",
            "email": "nurse01@demo.com",
            "phone": "+86-138-0000-0002",
            "role": "NURSE",
            "department": "护理部",
            "nurse_group_tag": "A组",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "user_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "nurse02",
            "full_name": "护士李四",
            "email": "nurse02@demo.com",
            "phone": "+86-138-0000-0003",
            "role": "NURSE",
            "department": "护理部",
            "nurse_group_tag": "A组",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for user in users:
        storage.create(user)
        print(f"✅ Created user: {user['full_name']}")


async def init_locations():
    """初始化位置"""
    print("\n📍 Creating sample locations...")
    location_storage = StorageService("locations")
    room_storage = StorageService("rooms")
    bed_storage = StorageService("beds")
    
    # 创建位置
    location = {
        "location_id": SAMPLE_LOCATION_ID,
        "tenant_id": SAMPLE_TENANT_ID,
        "location_name": "A楼",
        "location_type": "BUILDING",
        "door_number": "A",
        "floor": 1,
        "is_public_space": False,
        "alert_user_ids": [SAMPLE_USER_ID],
        "created_at": datetime.now().isoformat()
    }
    location_storage.create(location)
    print(f"✅ Created location: {location['location_name']}")
    
    # 创建房间
    room = {
        "room_id": SAMPLE_ROOM_ID,
        "tenant_id": SAMPLE_TENANT_ID,
        "location_id": SAMPLE_LOCATION_ID,
        "room_name": "101房间",
        "room_number": "101",
        "room_type": "DOUBLE",
        "max_beds": 2,
        "created_at": datetime.now().isoformat()
    }
    room_storage.create(room)
    print(f"✅ Created room: {room['room_name']}")
    
    # 创建床位
    bed = {
        "bed_id": SAMPLE_BED_ID,
        "tenant_id": SAMPLE_TENANT_ID,
        "room_id": SAMPLE_ROOM_ID,
        "location_id": SAMPLE_LOCATION_ID,
        "bed_name": "1号床",
        "bed_number": "101-1",
        "is_occupied": True,
        "resident_id": SAMPLE_RESIDENT_ID,
        "created_at": datetime.now().isoformat()
    }
    bed_storage.create(bed)
    print(f"✅ Created bed: {bed['bed_name']}")


async def init_residents():
    """初始化住户"""
    print("\n🧓 Creating sample residents...")
    storage = StorageService("residents")
    
    residents = [
        {
            "resident_id": SAMPLE_RESIDENT_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_account": "R001",
            "last_name": "王老先生",
            "is_institutional": True,
            "location_id": SAMPLE_LOCATION_ID,
            "bed_id": SAMPLE_BED_ID,
            "admission_date": (datetime.now() - timedelta(days=180)).date().isoformat(),
            "status": "active",
            "can_view_status": True,
            "primary_contact_name": "王小明",
            "primary_contact_phone": "+86-138-1111-1111",
            "primary_contact_relation": "儿子",
            "anonymous_name": "活力老人",
            "created_at": datetime.now().isoformat()
        },
        {
            "resident_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_account": "R002",
            "last_name": "李老太太",
            "is_institutional": True,
            "location_id": SAMPLE_LOCATION_ID,
            "admission_date": (datetime.now() - timedelta(days=90)).date().isoformat(),
            "status": "active",
            "can_view_status": True,
            "primary_contact_name": "李小红",
            "primary_contact_phone": "+86-138-2222-2222",
            "primary_contact_relation": "女儿",
            "anonymous_name": "温和老人",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for resident in residents:
        storage.create(resident)
        print(f"✅ Created resident: {resident['last_name']}")


async def init_devices():
    """初始化设备"""
    print("\n📱 Creating sample devices...")
    storage = StorageService("devices")
    
    devices = [
        {
            "device_id": SAMPLE_DEVICE_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "device_name": "A楼1层雷达",
            "device_model": "TDP-V2-Pro",
            "device_type": "RADAR",
            "serial_number": "TDP20231001001",
            "uid": "TDP-RADAR-001",
            "comm_mode": "WiFi",
            "firmware_version": "2.1.0",
            "location_id": SAMPLE_LOCATION_ID,
            "status": "online",
            "installed": True,
            "business_access": True,
            "monitoring_enabled": True,
            "installation_date_utc": (datetime.now() - timedelta(days=30)).isoformat(),
            "created_at": datetime.now().isoformat()
        },
        {
            "device_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "device_name": "101房间传感器",
            "device_model": "SENSOR-V1",
            "device_type": "SENSOR",
            "serial_number": "SEN20231001002",
            "uid": "SENSOR-001",
            "comm_mode": "Zigbee",
            "firmware_version": "1.5.0",
            "location_id": SAMPLE_LOCATION_ID,
            "status": "online",
            "installed": True,
            "business_access": True,
            "monitoring_enabled": True,
            "installation_date_utc": (datetime.now() - timedelta(days=25)).isoformat(),
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for device in devices:
        storage.create(device)
        print(f"✅ Created device: {device['device_name']}")


async def init_iot_data():
    """初始化IoT数据"""
    print("\n📊 Creating sample IoT data...")
    storage = StorageService("iot_timeseries")
    
    # 生成最近24小时的数据
    now = datetime.now()
    count = 0
    
    for i in range(24):  # 每小时生成数据
        timestamp = now - timedelta(hours=i)
        
        # 生成正常数据
        iot_data = {
            "id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "device_id": SAMPLE_DEVICE_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            "bed_id": SAMPLE_BED_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "timestamp": timestamp.isoformat(),
            "heart_rate": random.randint(60, 80),
            "respiration_rate": random.randint(12, 18),
            "motion_intensity": round(random.uniform(0.1, 0.5), 2),
            "presence": True,
            "in_bed": True,
            "alert_triggered": False,
            "data_source": "TDP",
            "created_at": timestamp.isoformat()
        }
        storage.create(iot_data)
        count += 1
    
    # 生成一条告警数据
    alert_data = {
        "id": str(uuid4()),
        "tenant_id": SAMPLE_TENANT_ID,
        "device_id": SAMPLE_DEVICE_ID,
        "resident_id": SAMPLE_RESIDENT_ID,
        "bed_id": SAMPLE_BED_ID,
        "location_id": SAMPLE_LOCATION_ID,
        "timestamp": (now - timedelta(hours=2)).isoformat(),
        "heart_rate": 120,
        "respiration_rate": 25,
        "motion_intensity": 0.8,
        "presence": True,
        "in_bed": True,
        "alert_triggered": True,
        "alert_type": "HEART_RATE_HIGH",
        "alert_level": "L3",
        "data_source": "TDP",
        "created_at": (now - timedelta(hours=2)).isoformat()
    }
    storage.create(alert_data)
    count += 1
    
    print(f"✅ Created {count} IoT data records")


async def init_cards():
    """初始化卡片"""
    print("\n🎴 Creating sample cards...")
    storage = StorageService("cards")
    
    cards = [
        {
            "card_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "card_type": "ActiveBed",
            "bed_id": SAMPLE_BED_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "card_name": "王老先生",
            "card_address": "A楼 > 101房间 > 1号床",
            "resident_id": SAMPLE_RESIDENT_ID,
            "is_public_space": False,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "card_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "card_type": "Location",
            "location_id": SAMPLE_LOCATION_ID,
            "card_name": "A楼公共区域",
            "card_address": "A楼",
            "is_public_space": True,
            "routing_alert_user_ids": [SAMPLE_USER_ID],
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for card in cards:
        storage.create(card)
        print(f"✅ Created card: {card['card_name']}")


async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 owlRD Sample Data Initialization")
    print("=" * 60)
    
    try:
        await init_tenants()
        await init_users()
        await init_locations()
        await init_residents()
        await init_devices()
        await init_iot_data()
        await init_cards()
        
        print("\n" + "=" * 60)
        print("✅ Sample data initialization completed!")
        print("=" * 60)
        print("\n📋 Summary:")
        print(f"  - Tenant ID: {SAMPLE_TENANT_ID}")
        print(f"  - User ID: {SAMPLE_USER_ID}")
        print(f"  - Resident ID: {SAMPLE_RESIDENT_ID}")
        print(f"  - Device ID: {SAMPLE_DEVICE_ID}")
        print("\n🌐 You can now access the API at:")
        print("  - http://localhost:8000/docs")
        print("  - http://192.168.2.6:8000/docs")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
