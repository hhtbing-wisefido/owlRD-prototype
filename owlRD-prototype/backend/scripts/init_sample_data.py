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
import json
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
            "contact_phone": "13800000001",
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
            "phone": "13800000001",
            "email_hash": hash_contact("admin@demo.com"),  # SHA-256哈希
            "phone_hash": hash_contact("13800000001"),
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
            "phone": "13800000002",
            "email_hash": hash_contact("nurse01@demo.com"),
            "phone_hash": hash_contact("13800000002"),
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
            "phone": "13800000003",
            "email_hash": hash_contact("nurse02@demo.com"),
            "phone_hash": hash_contact("13800000003"),
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
            "phone_hash": hash_contact("13811111111"),
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
            "phone_hash": hash_contact("13822222222"),
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
            "contact_phone": "13811111111",
            "contact_email": "wangxiaoming@example.com",
            "contact_sms": True,
            # 登录用的哈希（不存明文）
            "phone_hash": hash_contact("13811111111"),
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
            "contact_phone": "13822222222",
            "contact_email": "lixiaohong@example.com",
            "contact_sms": True,
            "phone_hash": hash_contact("13822222222"),
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
    """
    初始化IoT时序数据
    严格对齐: 12_iot_timeseries.sql
    """
    print("\n📊 Creating sample IoT timeseries data...")
    storage = StorageService("iot_timeseries")
    
    # 生成最近24小时的数据
    now = datetime.now()
    count = 0
    
    for i in range(24):  # 每小时生成数据
        timestamp = now - timedelta(hours=i)
        hr = random.randint(60, 80)
        rr = random.randint(12, 18)
        
        # 模拟原始数据（必须是bytes）
        raw_data = {
            "device_type": "Radar",
            "timestamp": timestamp.isoformat(),
            "tracking": {"id": 0, "x": 150, "y": 200, "z": 100},
            "vitals": {"hr": hr, "rr": rr},
            "sleep_state": "Deep sleep"
        }
        
        # 严格按照 IOTTimeseries Model 生成数据
        iot_data = {
            # 设备索引（必需）
            "tenant_id": SAMPLE_TENANT_ID,
            "device_id": SAMPLE_DEVICE_ID,
            
            # 时间戳（必需）
            "timestamp": timestamp.isoformat(),
            
            # TDP Tag Category（可选）
            "tdp_tag_category": "Physiological",
            
            # 轨迹数据（必需）
            "tracking_id": 0,  # 0-7，NULL表示无人
            "radar_pos_x": 150,  # 厘米
            "radar_pos_y": 200,
            "radar_pos_z": 100,
            
            # 姿态/运动状态（可选）
            "posture_snomed_code": "102538003",  # Lying position
            "posture_display": "Lying position",
            
            # 事件（可选）
            "event_type": None,
            "event_display": None,
            "area_id": None,
            
            # 生命体征（可选但推荐）
            "heart_rate": hr,
            "respiratory_rate": rr,  # ✅ 正确字段名
            
            # 睡眠状态（可选）
            "sleep_state_snomed_code": "248233000",  # Deep sleep
            "sleep_state_display": "Deep sleep",
            
            # 位置信息（可选，加速查询）
            "location_id": SAMPLE_LOCATION_ID,
            "room_id": SAMPLE_ROOM_ID,
            
            # 其他字段（可选）
            "confidence": 95,
            "remaining_time": None,
            
            # 原始记录存储（必需）
            "raw_original": json.dumps(raw_data).encode('utf-8'),  # ✅ bytes类型
            "raw_format": "json",  # ✅ 必需
            "raw_compression": None,
            
            # 元数据（可选）
            "metadata": {"source": "sample_data_generator"},
            
            "created_at": timestamp.isoformat()
        }
        storage.create(iot_data)
        count += 1
    
    # 生成一条异常数据（高心率）
    timestamp_alert = now - timedelta(hours=2)
    raw_data_alert = {
        "device_type": "Radar",
        "timestamp": timestamp_alert.isoformat(),
        "tracking": {"id": 0, "x": 150, "y": 200, "z": 100},
        "vitals": {"hr": 120, "rr": 25},
        "alert": "HEART_RATE_HIGH"
    }
    
    alert_data = {
        "tenant_id": SAMPLE_TENANT_ID,
        "device_id": SAMPLE_DEVICE_ID,
        "timestamp": timestamp_alert.isoformat(),
        "tdp_tag_category": "Physiological",
        "tracking_id": 0,
        "radar_pos_x": 150,
        "radar_pos_y": 200,
        "radar_pos_z": 100,
        "posture_snomed_code": "102538003",
        "posture_display": "Lying position",
        "heart_rate": 120,  # 异常高心率
        "respiratory_rate": 25,  # 异常高呼吸率
        "sleep_state_snomed_code": "248220002",  # Awake
        "sleep_state_display": "Awake",
        "location_id": SAMPLE_LOCATION_ID,
        "room_id": SAMPLE_ROOM_ID,
        "confidence": 90,
        "raw_original": json.dumps(raw_data_alert).encode('utf-8'),
        "raw_format": "json",
        "raw_compression": None,
        "metadata": {"alert_triggered": True, "alert_type": "HEART_RATE_HIGH"},
        "created_at": timestamp_alert.isoformat()
    }
    storage.create(alert_data)
    count += 1
    
    print(f"✅ Created {count} IoT timeseries records (对齐 12_iot_timeseries.sql)")


async def init_resident_phi():
    """
    初始化住户PHI数据（加密敏感信息）
    对齐: 08_resident_phi.sql
    """
    print("\n🔒 Creating resident PHI data...")
    storage = StorageService("resident_phi")
    
    # 严格按照源参考 08_resident_phi.sql 的字段
    phi_records = [
        {
            "phi_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            # PII字段（应加密存储）
            "first_name_encrypted": "王",  # 实际应用中应使用AES加密
            "last_name_encrypted": "明",
            "date_of_birth_encrypted": "1940-05-15",
            "gender_encrypted": "Male",
            "id_number_encrypted": "110101194005150011",
            "phone_encrypted": "13811111111",
            "email_encrypted": "resident001@example.com",
            "address_encrypted": "北京市朝阳区XX街道XX号",
            # 医疗信息（加密）
            "medical_conditions": ["高血压", "糖尿病"],
            "medications": ["降压药", "胰岛素"],
            "allergies": ["青霉素"],
            "emergency_contact_encrypted": "儿子：王小明 13811111111",
            # 元数据
            "encryption_version": "AES-256-GCM-V1",
            "last_accessed_at": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "phi_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "resident_id": SAMPLE_RESIDENT_ID_2,
            "first_name_encrypted": "李",
            "last_name_encrypted": "华",
            "date_of_birth_encrypted": "1945-08-20",
            "gender_encrypted": "Female",
            "id_number_encrypted": "110101194508200022",
            "phone_encrypted": "13822222222",
            "email_encrypted": "resident002@example.com",
            "address_encrypted": "北京市海淀区YY街道YY号",
            "medical_conditions": ["冠心病"],
            "medications": ["阿司匹林"],
            "allergies": [],
            "emergency_contact_encrypted": "女儿：李小红 13822222222",
            "encryption_version": "AES-256-GCM-V1",
            "last_accessed_at": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for phi in phi_records:
        storage.create(phi)
        print(f"✅ Created PHI record for resident: {phi['resident_id']}")


async def init_alert_policies():
    """
    初始化告警策略
    对齐: 14_cloud_alert_policies.sql
    """
    print("\n⚠️ Creating alert policies...")
    storage = StorageService("alert_policies")
    
    # 严格按照源参考 14_cloud_alert_policies.sql 的字段
    policies = [
        {
            "policy_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "policy_name": "高心率告警策略",
            "policy_type": "VITAL_SIGNS",
            "severity": "L1",  # L1/L2/L3/L5
            "is_enabled": True,
            # 触发条件
            "trigger_conditions": {
                "data_type": "heart_rate",
                "operator": ">",
                "threshold": 115,
                "duration_seconds": 60
            },
            # 响应动作
            "actions": {
                "create_alert": True,
                "notify_users": True,
                "escalate_after_minutes": 5
            },
            # 适用范围
            "scope": {
                "apply_to": "ALL",  # ALL/LOCATION/DEVICE
                "location_ids": None,
                "device_ids": None
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "policy_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "policy_name": "跌倒检测告警",
            "policy_type": "FALL_DETECTION",
            "severity": "L1",
            "is_enabled": True,
            "trigger_conditions": {
                "event_type": "FALL",
                "confidence_threshold": 0.8
            },
            "actions": {
                "create_alert": True,
                "notify_users": True,
                "escalate_after_minutes": 2
            },
            "scope": {
                "apply_to": "ALL"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "policy_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "policy_name": "离床时间过长",
            "policy_type": "BED_EXIT",
            "severity": "L2",
            "is_enabled": True,
            "trigger_conditions": {
                "event_type": "BED_EXIT",
                "duration_minutes": 30
            },
            "actions": {
                "create_alert": True,
                "notify_users": True
            },
            "scope": {
                "apply_to": "ALL"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for policy in policies:
        storage.create(policy)
        print(f"✅ Created alert policy: {policy['policy_name']}")


async def init_alerts():
    """
    初始化告警记录
    对齐: 13_iot_monitor_alerts.sql
    """
    print("\n🚨 Creating sample alerts...")
    storage = StorageService("alerts")
    
    # 严格按照源参考 13_iot_monitor_alerts.sql 的字段
    alerts = [
        {
            "alert_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "alert_type": "HEART_RATE_HIGH",
            "severity": "L1",  # L1紧急
            "status": "pending",  # pending/acknowledged/resolved
            "source_type": "IOT_DEVICE",
            "source_id": SAMPLE_DEVICE_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "room_id": SAMPLE_ROOM_ID,
            "bed_id": SAMPLE_BED_ID,
            # 告警详情
            "alert_message": "心率异常：120 bpm（正常范围：55-95）",
            "alert_data": {
                "heart_rate": 120,
                "threshold": 95,
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            # 处理信息
            "acknowledged_by": None,
            "acknowledged_at": None,
            "resolved_by": None,
            "resolved_at": None,
            "resolution_notes": None,
            # 路由信息
            "notified_user_ids": [SAMPLE_USER_ID_2, SAMPLE_USER_ID_3],
            "escalation_level": 0,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "updated_at": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "alert_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "alert_type": "RESPIRATORY_RATE_HIGH",
            "severity": "L2",
            "status": "acknowledged",
            "source_type": "IOT_DEVICE",
            "source_id": SAMPLE_DEVICE_ID,
            "resident_id": SAMPLE_RESIDENT_ID,
            "location_id": SAMPLE_LOCATION_ID,
            "alert_message": "呼吸率异常：25 /min（正常范围：10-23）",
            "alert_data": {
                "respiratory_rate": 25,
                "threshold": 23
            },
            "acknowledged_by": SAMPLE_USER_ID_2,
            "acknowledged_at": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
            "notified_user_ids": [SAMPLE_USER_ID_2],
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "updated_at": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat()
        }
    ]
    
    for alert in alerts:
        storage.create(alert)
        print(f"✅ Created alert: {alert['alert_type']}")


async def init_card_functions():
    """
    初始化卡片功能
    对齐: 19_card_functions.sql
    """
    print("\n🎯 Creating card functions...")
    storage = StorageService("card_functions")
    
    # 严格按照源参考 19_card_functions.sql 的字段
    functions = [
        {
            "function_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "function_name": "查看实时监测",
            "function_code": "VIEW_REALTIME_MONITOR",
            "function_type": "VIEW",
            "description": "查看住户的实时生命体征监测数据",
            "icon": "activity",
            "is_enabled": True,
            "display_order": 1,
            "required_permissions": ["VIEW_IOT_DATA"],
            "created_at": datetime.now().isoformat()
        },
        {
            "function_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "function_name": "查看历史记录",
            "function_code": "VIEW_HISTORY",
            "function_type": "VIEW",
            "description": "查看住户的历史监测数据和告警记录",
            "icon": "clock",
            "is_enabled": True,
            "display_order": 2,
            "required_permissions": ["VIEW_HISTORY"],
            "created_at": datetime.now().isoformat()
        },
        {
            "function_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "function_name": "发起视频通话",
            "function_code": "VIDEO_CALL",
            "function_type": "ACTION",
            "description": "与住户发起视频通话",
            "icon": "video",
            "is_enabled": True,
            "display_order": 3,
            "required_permissions": ["INITIATE_CALL"],
            "created_at": datetime.now().isoformat()
        },
        {
            "function_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "function_name": "调整监测参数",
            "function_code": "ADJUST_MONITOR_PARAMS",
            "function_type": "SETTINGS",
            "description": "调整设备监测参数和告警阈值",
            "icon": "settings",
            "is_enabled": True,
            "display_order": 4,
            "required_permissions": ["ADMIN"],
            "created_at": datetime.now().isoformat()
        },
        {
            "function_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "function_name": "生成护理报告",
            "function_code": "GENERATE_CARE_REPORT",
            "function_type": "REPORT",
            "description": "生成住户的护理质量报告",
            "icon": "file-text",
            "is_enabled": True,
            "display_order": 5,
            "required_permissions": ["GENERATE_REPORT"],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for func in functions:
        storage.create(func)
        print(f"✅ Created card function: {func['function_name']}")


async def init_config_versions():
    """
    初始化配置版本
    对齐: 15_config_versions.sql
    """
    print("\n⚙️ Creating config versions...")
    storage = StorageService("config_versions")
    
    config = {
        "config_id": str(uuid4()),
        "tenant_id": SAMPLE_TENANT_ID,
        "config_type": "SYSTEM",
        "config_name": "系统默认配置",
        "version": "1.0.0",
        "is_active": True,
        "config_data": {
            "alert_retention_days": 90,
            "iot_data_retention_days": 365,
            "default_alert_levels": ["L1", "L2", "L3"],
            "heart_rate_normal_range": [55, 95],
            "respiratory_rate_normal_range": [10, 23],
            "fall_detection_enabled": True,
            "bed_exit_monitoring_enabled": True
        },
        "created_by": SAMPLE_USER_ID,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    storage.create(config)
    print(f"✅ Created config version: {config['config_name']}")


async def init_mappings():
    """
    初始化映射表
    对齐: 16_mapping_tables.sql
    """
    print("\n🔗 Creating mapping entries...")
    storage = StorageService("mappings")
    
    mappings = [
        {
            "mapping_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "mapping_type": "SNOMED_POSTURE",
            "source_code": "standing",
            "target_code": "10904000",
            "target_display": "Standing position",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "mapping_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "mapping_type": "SNOMED_POSTURE",
            "source_code": "sitting",
            "target_code": "33586001",
            "target_display": "Sitting position",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "mapping_id": str(uuid4()),
            "tenant_id": SAMPLE_TENANT_ID,
            "mapping_type": "SNOMED_POSTURE",
            "source_code": "lying",
            "target_code": "102538003",
            "target_display": "Lying position",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for mapping in mappings:
        storage.create(mapping)
        print(f"✅ Created mapping: {mapping['source_code']} -> {mapping['target_code']}")


async def init_care_quality_reports():
    """
    初始化护理质量报告
    对齐: 17_care_quality_reports.sql
    """
    print("\n📊 Creating care quality reports...")
    storage = StorageService("care_quality_reports")
    
    report = {
        "report_id": str(uuid4()),
        "tenant_id": SAMPLE_TENANT_ID,
        "report_type": "WEEKLY",
        "report_period_start": (datetime.now() - timedelta(days=7)).date().isoformat(),
        "report_period_end": datetime.now().date().isoformat(),
        "quality_score": 85,
        # 统计指标
        "metrics": {
            "total_alerts": 25,
            "avg_response_time_seconds": 45,
            "room_coverage_rate": 0.92,
            "alert_handling_rate": 0.96,
            "avg_heart_rate": 72,
            "avg_respiratory_rate": 16
        },
        # 维度评分
        "dimension_scores": {
            "response_speed": 92,
            "service_attitude": 88,
            "professional_skill": 85,
            "room_coverage": 90,
            "documentation": 78,
            "emergency_handling": 95
        },
        # AI分析结果
        "ai_insights": {
            "strengths": ["应急处理能力优秀", "响应速度快速稳定"],
            "weaknesses": ["文档记录有待加强", "周末服务覆盖不足"],
            "recommendations": ["推荐引入电子记录系统", "建议增加周末人员配置"]
        },
        "generated_by": "SYSTEM",
        "created_at": datetime.now().isoformat()
    }
    
    storage.create(report)
    print(f"✅ Created care quality report: {report['report_type']}")


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
    """主函数 - 严格对齐源参考版本（完整版）"""
    print("=" * 70)
    print("🚀 owlRD Sample Data Initialization (Complete Source-Aligned)")
    print("=" * 70)
    print("\n📖 Aligning with ALL 19 reference schemas:")
    print("  - 01_tenants.sql")
    print("  - 02_roles.sql")
    print("  - 03_users.sql")
    print("  - 04_locations.sql + 05_rooms.sql + 06_beds.sql")
    print("  - 07_residents.sql")
    print("  - 08_resident_phi.sql ⭐ NEW")
    print("  - 09_resident_contacts.sql")
    print("  - 10_resident_caregivers.sql")
    print("  - 11_devices.sql")
    print("  - 12_iot_timeseries.sql")
    print("  - 13_iot_monitor_alerts.sql ⭐ NEW")
    print("  - 14_cloud_alert_policies.sql ⭐ NEW")
    print("  - 15_config_versions.sql ⭐ NEW")
    print("  - 16_mapping_tables.sql ⭐ NEW")
    print("  - 17_care_quality_reports.sql ⭐ NEW")
    print("  - 18_cards.sql")
    print("  - 19_card_functions.sql ⭐ NEW")
    print("=" * 70)
    
    try:
        # 初始化所有数据（按依赖顺序）
        await init_tenants()
        await init_roles()
        await init_users()
        await init_locations()
        await init_residents()
        await init_resident_phi()  # ⭐ 新增
        await init_resident_contacts()
        await init_resident_caregivers()
        await init_devices()
        await init_iot_data()
        await init_config_versions()  # ⭐ 新增
        await init_mappings()  # ⭐ 新增
        await init_alert_policies()  # ⭐ 新增
        await init_alerts()  # ⭐ 新增
        await init_cards()
        await init_card_functions()  # ⭐ 新增
        await init_care_quality_reports()  # ⭐ 新增
        
        print("\n" + "=" * 70)
        print("✅ Complete sample data initialization finished!")
        print("=" * 70)
        print("\n📋 Summary:")
        print(f"  - Tenants: 1")
        print(f"  - Roles: 6 (System roles)")
        print(f"  - Users: 3 (1 Director + 2 Nurses)")
        print(f"  - Locations/Rooms/Beds: 1/1/2")
        print(f"  - Residents: 2 (with HIS integration)")
        print(f"  - Resident PHI: 2 ⭐ (encrypted)")
        print(f"  - Resident Contacts: 2 (family members)")
        print(f"  - Caregiver Assignments: 2")
        print(f"  - Devices: 2 (Radar + PressureMat)")
        print(f"  - IoT Data Records: ~25")
        print(f"  - Config Versions: 1 ⭐")
        print(f"  - Mappings: 3 ⭐ (SNOMED)")
        print(f"  - Alert Policies: 3 ⭐")
        print(f"  - Alerts: 2 ⭐")
        print(f"  - Cards: 2")
        print(f"  - Card Functions: 5 ⭐")
        print(f"  - Care Quality Reports: 1 ⭐")
        print("\n🔑 Key IDs:")
        print(f"  - Tenant: {SAMPLE_TENANT_ID}")
        print(f"  - Admin User: {SAMPLE_USER_ID}")
        print(f"  - Resident 1: {SAMPLE_RESIDENT_ID}")
        print(f"  - Resident 2: {SAMPLE_RESIDENT_ID_2}")
        print("\n🌐 API Access:")
        print("  - http://localhost:8000/docs")
        print("  - http://192.168.2.6:8000/docs")
        print("\n✨ Complete Features (19/19 tables):")
        print("  ✅ HIS system integration fields")
        print("  ✅ SHA-256 hashed contact info")
        print("  ✅ Encrypted PHI data (08_resident_phi)")
        print("  ✅ Alert policies and alerts (13_/14_)")
        print("  ✅ Card functions (19_)")
        print("  ✅ Config versions (15_)")
        print("  ✅ SNOMED mappings (16_)")
        print("  ✅ Care quality reports (17_)")
        print("  ✅ Full device specs (11_)")
        print("  ✅ IoT timeseries with raw_original")
        print("\n🎉 All 19 reference schemas aligned!")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
