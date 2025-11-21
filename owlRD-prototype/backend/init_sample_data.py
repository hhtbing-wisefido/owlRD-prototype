"""
示例数据初始化脚本 - 严格对齐源参考版本

功能：
- 严格按照 owdRD_github_clone_源参考文件/db/*.sql 的表结构生成数据
- 包含所有源参考中定义的字段
- 实现多表关联（resident_contacts, resident_caregivers）
- 使用哈希字段（phone_hash, email_hash）
- 便于系统演示和测试

对齐的表结构：
- 01_tenants.sql
- 03_users.sql
- 07_residents.sql
- 09_resident_contacts.sql
- 10_resident_caregivers.sql
- 11_devices.sql
"""

import asyncio
import uuid
from uuid import uuid4
from datetime import datetime, timedelta
import hashlib
import random
from app.services.storage import StorageService


def hash_contact(value: str) -> str:
    """生成联系方式的SHA-256哈希（模拟）"""
    if not value:
        return None
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


# 示例数据 ID
SAMPLE_TENANT_ID = "10000000-0000-0000-0000-000000000001"
SAMPLE_USER_ID = "20000000-0000-0000-0000-000000000001"
SAMPLE_USER_ID_2 = "20000000-0000-0000-0000-000000000002"
SAMPLE_USER_ID_3 = "20000000-0000-0000-0000-000000000003"
SAMPLE_LOCATION_ID = "30000000-0000-0000-0000-000000000001"
SAMPLE_ROOM_ID = "40000000-0000-0000-0000-000000000001"
SAMPLE_BED_ID = "50000000-0000-0000-0000-000000000001"
SAMPLE_BED_ID_2 = "50000000-0000-0000-0000-000000000002"
SAMPLE_RESIDENT_ID = "60000000-0000-0000-0000-000000000001"
SAMPLE_RESIDENT_ID_2 = "60000000-0000-0000-0000-000000000002"
SAMPLE_DEVICE_ID = "70000000-0000-0000-0000-000000000001"


async def init_tenants():
    """
    初始化租户
    对齐: 01_tenants.sql
    """
    print("🏢 Creating sample tenant...")
    storage = StorageService("tenants")
    
    # 严格按照源参考 01_tenants.sql 的字段
    tenant = {
        "tenant_id": SAMPLE_TENANT_ID,
        "tenant_name": "示例养老院",
        "domain": "demo-facility.owlrd.com",  # 租户域名
        "status": "active",  # active, suspended, deleted
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "metadata": {  # 扩展配置信息
            "license_type": "ENTERPRISE",
            "max_users": 100,
            "max_residents": 200,
            "features_enabled": ["IOT", "ALERTS", "CARE_QUALITY", "CARDS"],
            "contact_email": "admin@demo-facility.com",
            "contact_phone": "+86-138-0000-0001",
            "address": "北京市朝阳区示例路123号"
        }
    }
    
    storage.create(tenant)
    print(f"✅ Created tenant: {tenant['tenant_name']}")


async def init_roles():
    """
    初始化角色
    对齐: 02_roles.sql - 系统预置角色
    """
    print("\n👔 Creating sample roles...")
    storage = StorageService("roles")
    
    # 严格按照源参考 02_roles.sql 的字段
    roles = [
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "Director",
            "display_name": "主任/院长",
            "description": "养老机构管理者，拥有全部权限",
            "is_system": True,  # 系统预置角色，不可删除
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "NurseManager",
            "display_name": "护士长",
            "description": "护理团队管理者，管理护士和护工",
            "is_system": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "Nurse",
            "display_name": "护士",
            "description": "专业护理人员，负责住户护理和健康监测",
            "is_system": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "Caregiver",
            "display_name": "护工",
            "description": "日常照护人员，协助住户生活起居",
            "is_system": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "Doctor",
            "display_name": "医生",
            "description": "医疗专业人员，提供医疗咨询和诊断",
            "is_system": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "role_id": str(uuid.uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "role_code": "FamilyMember",
            "display_name": "家属",
            "description": "住户家属，可查看关联住户的状态",
            "is_system": True,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for role in roles:
        storage.create(role)
        print(f"✅ Created role: {role['display_name']} ({role['role_code']})")


async def init_users():
    """
    初始化用户
    对齐: 03_users.sql
    """
    print("\n👤 Creating sample users...")
    storage = StorageService("users")
    
    # 严格按照源参考 03_users.sql 的字段
    users = [
        {
            "user_id": SAMPLE_USER_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "admin_user",
            "email": "admin@demo.com",
            "phone": "+86-138-0000-0001",
            "email_hash": hash_contact("admin@demo.com"),  # SHA-256哈希
            "phone_hash": hash_contact("+86-138-0000-0001"),
            "password_hash": None,  # 应该是bcrypt/argon2哈希
            "pin_hash": None,
            "role": "Director",  # Director / NurseManager / Nurse / ITSupport
            "status": "active",  # active, disabled, left
            "alert_levels": ["L1", "L2", "L3"],  # 接收的告警级别
            "alert_channels": ["APP", "EMAIL"],  # 接收通道
            "alert_scope": "ALL",  # ALL, LOCATION-TAG, ASSIGNED_ONLY
            "last_login_at": None,
            "tags": {"department": "管理部", "permissions": ["all"]},  # 员工标签
            "created_at": datetime.now().isoformat()
        },
        {
            "user_id": SAMPLE_USER_ID_2,
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "nurse_zhang",
            "email": "nurse01@demo.com",
            "phone": "+86-138-0000-0002",
            "email_hash": hash_contact("nurse01@demo.com"),
            "phone_hash": hash_contact("+86-138-0000-0002"),
            "password_hash": None,
            "pin_hash": None,
            "role": "Nurse",
            "status": "active",
            "alert_levels": ["L1", "L2"],  # 只接收高优先级告警
            "alert_channels": ["APP"],
            "alert_scope": "ASSIGNED_ONLY",  # 只接收分配给自己的住户告警
            "last_login_at": None,
            "tags": {
                "department": "护理部",
                "nurse_group": "A组",
                "shift": "DayShift",
                "certifications": ["FallsExpert"]
            },
            "created_at": datetime.now().isoformat()
        },
        {
            "user_id": SAMPLE_USER_ID_3,
            "tenant_id": SAMPLE_TENANT_ID,
            "username": "nurse_li",
            "email": "nurse02@demo.com",
            "phone": "+86-138-0000-0003",
            "email_hash": hash_contact("nurse02@demo.com"),
            "phone_hash": hash_contact("+86-138-0000-0003"),
            "password_hash": None,
            "pin_hash": None,
            "role": "Nurse",
            "status": "active",
            "alert_levels": ["L1", "L2", "L3"],
            "alert_channels": ["APP"],
            "alert_scope": "ASSIGNED_ONLY",
            "last_login_at": None,
            "tags": {
                "department": "护理部",
                "nurse_group": "A组",
                "shift": "NightShift"
            },
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for user in users:
        storage.create(user)
        print(f"✅ Created user: {user['username']}")


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
    beds = [
        {
            "bed_id": SAMPLE_BED_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "room_id": SAMPLE_ROOM_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "bed_name": "1号床",
            "bed_number": "101-1",
            "is_occupied": True,
            "resident_id": SAMPLE_RESIDENT_ID,
            "created_at": datetime.now().isoformat()
        },
        {
            "bed_id": SAMPLE_BED_ID_2,
            "tenant_id": SAMPLE_TENANT_ID,
            "room_id": SAMPLE_ROOM_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "bed_name": "2号床",
            "bed_number": "101-2",
            "is_occupied": True,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for bed in beds:
        bed_storage.create(bed)
        print(f"✅ Created bed: {bed['bed_name']}")


async def init_residents():
    """
    初始化住户
    对齐: 07_residents.sql - 完全匿名化，无PII存储
    """
    print("\n🧓 Creating sample residents...")
    storage = StorageService("residents")
    
    # 严格按照源参考 07_residents.sql 的字段
    residents = [
        {
            "resident_id": SAMPLE_RESIDENT_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            # HIS系统集成字段
            "HIS_resident_id": "HIS-R-2023-001",  # 外部HIS系统ID
            "HIS_resident_bed_id": "HIS-BED-101-1",
            "HIS_resident_status": "active",
            # 住户账号（机构内部唯一标识）
            "resident_account": "R001",
            # 虚拟姓名（匿名代称）
            "first_name": None,
            "last_name": "活力老人",  # 用匿名代称填充
            "anonymous_name": "活力老人",  # 与last_name相同
            # 机构或在家模式
            "is_institutional": True,
            # 位置信息
            "location_id": SAMPLE_LOCATION_ID,
            "bed_id": SAMPLE_BED_ID,
            "admission_date": (datetime.now() - timedelta(days=180)).date().isoformat(),
            "status": "active",  # active, discharged, transferred
            "metadata": {"notes": "演示住户1"},  # 仅包含非PII信息
            # 登录/重置用的联系方式哈希（不存明文）
            "phone_hash": hash_contact("+86-138-1111-1111"),
            "email_hash": hash_contact("resident001@example.com"),
            # 家庭标签
            "family_tag": "FAMILY-WANG",  # 家庭标识符
            "family_member_account_1": None,  # 共同家庭成员账号
            # 是否允许家属查看状态
            "can_view_status": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "tenant_id": SAMPLE_TENANT_ID,
            "HIS_resident_id": "HIS-R-2023-002",
            "HIS_resident_bed_id": "HIS-BED-101-2",
            "HIS_resident_status": "active",
            "resident_account": "R002",
            "first_name": None,
            "last_name": "温和老人",
            "anonymous_name": "温和老人",
            "is_institutional": True,
            "location_id": SAMPLE_LOCATION_ID,
            "bed_id": SAMPLE_BED_ID_2,
            "admission_date": (datetime.now() - timedelta(days=90)).date().isoformat(),
            "status": "active",
            "metadata": {"notes": "演示住户2"},
            "phone_hash": hash_contact("+86-138-2222-2222"),
            "email_hash": hash_contact("resident002@example.com"),
            "family_tag": "FAMILY-LI",
            "family_member_account_1": None,
            "can_view_status": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for resident in residents:
        storage.create(resident)
        print(f"✅ Created resident: {resident['anonymous_name']}")


async def init_resident_contacts():
    """
    初始化住户联系人（家属账号）
    对齐: 09_resident_contacts.sql
    """
    print("\n👨‍👩‍👧‍👦 Creating resident contacts...")
    storage = StorageService("resident_contacts")
    
    # 严格按照源参考 09_resident_contacts.sql 的字段
    contacts = [
        {
            "contact_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            "slot": "A",  # A/B/C/D/E
            "contact_resident_id": None,  # 可指向另一个residents记录
            "can_view_status": True,
            "can_receive_alert": True,
            "relationship": "Child",  # Child/Spouse/Friend/Caregiver
            # 可选的PHI（仅在特定场景下填写）
            "contact_first_name": "小明",
            "contact_last_name": "王",
            "contact_phone": "+86-138-1111-1111",
            "contact_email": "wangxiaoming@example.com",
            "contact_sms": True,
            # 登录用的哈希（不存明文）
            "phone_hash": hash_contact("+86-138-1111-1111"),
            "email_hash": hash_contact("wangxiaoming@example.com"),
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "contact_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "slot": "A",
            "contact_resident_id": None,
            "can_view_status": True,
            "can_receive_alert": True,
            "relationship": "Child",
            "contact_first_name": "小红",
            "contact_last_name": "李",
            "contact_phone": "+86-138-2222-2222",
            "contact_email": "lixiaohong@example.com",
            "contact_sms": True,
            "phone_hash": hash_contact("+86-138-2222-2222"),
            "email_hash": hash_contact("lixiaohong@example.com"),
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for contact in contacts:
        storage.create(contact)
        print(f"✅ Created contact: {contact['contact_first_name']}{contact['contact_last_name']} (Slot {contact['slot']})")


async def init_resident_caregivers():
    """
    初始化住户-护理人员关联
    对齐: 10_resident_caregivers.sql
    """
    print("\n👨‍⚕️ Creating resident-caregiver assignments...")
    storage = StorageService("resident_caregivers")
    
    # 严格按照源参考 10_resident_caregivers.sql 的字段
    # 注意：每个记录包含5个护理人员ID（caregiver_id1~5），都是必填
    caregivers = [
        {
            "id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            # 5个护理人员ID（都是必填）
            "caregiver_id1": SAMPLE_USER_ID_2,  # 护士张三
            "caregiver_id2": SAMPLE_USER_ID_3,  # 护士李四
            "caregiver_id3": SAMPLE_USER_ID_2,  # 可重复
            "caregiver_id4": SAMPLE_USER_ID_2,
            "caregiver_id5": SAMPLE_USER_ID_2,
            # 护士组标签
            "nurse_group_tags": ["A组", "DayShift", "FallsExpert"],
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "caregiver_id1": SAMPLE_USER_ID_3,  # 护士李四
            "caregiver_id2": SAMPLE_USER_ID_2,  # 护士张三
            "caregiver_id3": SAMPLE_USER_ID_3,
            "caregiver_id4": SAMPLE_USER_ID_3,
            "caregiver_id5": SAMPLE_USER_ID_3,
            "nurse_group_tags": ["A组", "NightShift"],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for caregiver in caregivers:
        storage.create(caregiver)
        print(f"✅ Created caregiver assignment for resident: {caregiver['resident_id']}")


async def init_devices():
    """
    初始化设备
    对齐: 11_devices.sql
    """
    print("\n📱 Creating sample devices...")
    storage = StorageService("devices")
    
    # 严格按照源参考 11_devices.sql 的字段
    devices = [
        {
            "device_id": SAMPLE_DEVICE_ID,
            "tenant_id": SAMPLE_TENANT_ID,
            "device_name": "A楼1层雷达",
            "device_model": "WF-RADAR-60G-V2",  # 型号
            "device_type": "Radar",  # Radar/SleepPad/VibrationSensor/Gateway
            "serial_number": "TDP20231001001",  # 厂家序列号
            "uid": "TDP-RADAR-001",  # 平台UID
            "imei": None,  # 4G设备IMEI
            "comm_mode": "WiFi",  # WiFi/LTE/Zigbee
            "firmware_version": "2.1.0",
            "mcu_model": "ESP32",  # MCU型号
            # Location Binding
            "location_id": SAMPLE_LOCATION_ID,
            "bound_room_id": SAMPLE_ROOM_ID,
            "bound_bed_id": SAMPLE_BED_ID,
            # Status
            "status": "online",  # online/offline/error
            "installed": True,  # 设备已安装
            "business_access": True,  # 允许接入系统
            "monitoring_enabled": True,  # 启用监护功能
            "installation_date_utc": (datetime.now() - timedelta(days=30)).isoformat(),
            "metadata": {"notes": "主雷达设备"},
            "created_at": datetime.now().isoformat()
        },
        {
            "device_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "device_name": "101房间压力板",
            "device_model": "PRESSURE-MAT-V1",
            "device_type": "PressureMat",
            "serial_number": "PM20231001002",
            "uid": "PM-001",
            "imei": None,
            "comm_mode": "Zigbee",
            "firmware_version": "1.5.0",
            "mcu_model": "STM32F4",
            "location_id": SAMPLE_LOCATION_ID,
            "bound_room_id": SAMPLE_ROOM_ID,
            "bound_bed_id": SAMPLE_BED_ID_2,
            "status": "online",
            "installed": True,
            "business_access": True,
            "monitoring_enabled": True,
            "installation_date_utc": (datetime.now() - timedelta(days=25)).isoformat(),
            "metadata": {"notes": "床垫传感器"},
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
    """主函数 - 严格对齐源参考版本"""
    print("=" * 70)
    print("🚀 owlRD Sample Data Initialization (Source-Aligned Version)")
    print("=" * 70)
    print("\n📖 Aligning with reference schemas:")
    print("  - 01_tenants.sql")
    print("  - 03_users.sql")
    print("  - 07_residents.sql")
    print("  - 09_resident_contacts.sql")
    print("  - 10_resident_caregivers.sql")
    print("  - 11_devices.sql")
    print("=" * 70)
    
    try:
        # 初始化所有数据
        await init_tenants()
        await init_roles()
        await init_users()
        await init_locations()
        await init_residents()
        await init_resident_contacts()  # 新增：联系人表
        await init_resident_caregivers()  # 新增：护理人员关联表
        await init_devices()
        await init_iot_data()
        await init_cards()
        
        print("\n" + "=" * 70)
        print("✅ Sample data initialization completed!")
        print("=" * 70)
        print("\n📋 Summary:")
        print(f"  ��� Tenants: 1")
        print(f"  - Users: 3 (1 Director + 2 Nurses)")
        print(f"  - Residents: 2 (with HIS integration fields)")
        print(f"  - Resident Contacts: 2 (family members)")
        print(f"  - Caregiver Assignments: 2")
        print(f"  - Devices: 2 (Radar + PressureMat)")
        print(f"  - IoT Data Records: ~25")
        print(f"  - Cards: 2")
        print("\n🔑 Key IDs:")
        print(f"  - Tenant: {SAMPLE_TENANT_ID}")
        print(f"  - Admin User: {SAMPLE_USER_ID}")
        print(f"  - Resident 1: {SAMPLE_RESIDENT_ID}")
        print(f"  - Resident 2: {SAMPLE_RESIDENT_ID_2}")
        print("\n🌐 API Access:")
        print("  - http://localhost:8000/docs")
        print("  - http://192.168.2.6:8000/docs")
        print("\n✨ Features:")
        print("  ✅ HIS system integration fields")
        print("  ✅ SHA-256 hashed contact info (phone/email)")
        print("  ✅ Family tags for multi-resident families")
        print("  ✅ Separate contact records (09_resident_contacts)")
        print("  ✅ Caregiver assignments (10_resident_caregivers)")
        print("  ✅ Full device specs (11_devices)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
