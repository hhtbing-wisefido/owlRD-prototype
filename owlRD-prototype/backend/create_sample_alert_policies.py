"""
创建示例告警策略数据
为示例租户初始化默认告警配置
"""

import asyncio
import uuid
from datetime import datetime
from app.services.storage import StorageService

# 使用与init_sample_data.py相同的租户ID
SAMPLE_TENANT_ID = "10000000-0000-0000-0000-000000000001"


async def create_sample_alert_policies():
    """创建示例告警策略数据"""
    print("⚡ Creating sample alert policies...")
    print()

    storage = StorageService("cloud_alert_policies")

    # 创建默认告警策略（基于vue_radar标准）
    policy = {
        "tenant_id": SAMPLE_TENANT_ID,
        # Common报警
        "OfflineAlarm": "L2",
        "LowBattery": "L2",
        "DeviceFailure": "L1",
        # SleepMonitor报警
        "SleepPad_LeftBed": "L2",
        "SleepPad_SitUp": "L2",
        "SleepPad_ApneaHypopnea": "L1",
        "SleepPad_AbnormalHeartRate": "L1",
        "SleepPad_AbnormalRespiratoryRate": "L1",
        "SleepPad_AbnormalBodyMovement": "L2",
        "SleepPad_InBed": "DISABLE",
        # Radar报警
        "Radar_AbnormalHeartRate": "L1",
        "Radar_AbnormalRespiratoryRate": "L1",
        "SuspectedFall": "L2",
        "Fall": "L1",
        "VitalsWeak": "L2",
        "Radar_LeftBed": "L2",
        "Stay": "L2",
        "NoActivity24h": "L1",
        "AngleException": "L2",
        # 自定义报警（未启用）
        "CustomAlert1": None,
        "CustomAlert2": None,
        "CustomAlert3": None,
        # 默认阈值（基于vue_radar项目标准）
        "conditions": {
            "heart_rate": {
                "L1": {
                    "ranges": [{"min": 0, "max": 44}, {"min": 116, "max": None}],
                    "duration_sec": 60
                },
                "L2": {
                    "ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}],
                    "duration_sec": 300
                },
                "Normal": {
                    "ranges": [{"min": 55, "max": 95}],
                    "duration_sec": 0
                }
            },
            "respiratory_rate": {
                "L1": {
                    "ranges": [{"min": 0, "max": 7}, {"min": 27, "max": None}],
                    "duration_sec": 60
                },
                "L2": {
                    "ranges": [{"min": 8, "max": 9}, {"min": 24, "max": 26}],
                    "duration_sec": 300
                },
                "Normal": {
                    "ranges": [{"min": 10, "max": 23}],
                    "duration_sec": 0
                }
            }
        },
        # 默认通知规则
        "notification_rules": {
            "L1": {
                "channels": ["WEB", "APP", "PHONE", "EMAIL"],
                "immediate": True,
                "repeat_interval_sec": 300
            },
            "L2": {
                "channels": ["WEB", "APP"],
                "immediate": False,
                "repeat_interval_sec": 600
            },
            "escalation": {
                "enabled": True,
                "escalate_after_sec": 300,
                "escalate_to_level": "L1"
            },
            "suppression": {
                "enabled": True,
                "suppress_duplicate_sec": 60,
                "max_alerts_per_hour": 10
            }
        },
        "is_active": True,
        "metadata": {
            "initialized_by": "script",
            "initialization_date": datetime.now().isoformat(),
            "notes": "示例配置，基于vue_radar项目标准"
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    storage.create(policy)
    print(f"✅ Created alert policy for tenant: {SAMPLE_TENANT_ID}")

    print()
    print("=" * 70)
    print("✅ Alert policy creation completed!")
    print("=" * 70)
    print()
    print("📋 Configuration summary:")
    print(f"  - Tenant ID: {SAMPLE_TENANT_ID}")
    print()
    print("  📌 Common alerts:")
    print(f"     • OfflineAlarm: L2")
    print(f"     • LowBattery: L2")
    print(f"     • DeviceFailure: L1")
    print()
    print("  🛌 SleepMonitor alerts:")
    print(f"     • LeftBed: L2, SitUp: L2")
    print(f"     • ApneaHypopnea: L1 (呼吸暂停)")
    print(f"     • AbnormalHeartRate: L1 (心率异常)")
    print(f"     • AbnormalRespiratoryRate: L1 (呼吸率异常)")
    print(f"     • InBed: DISABLE (不报警)")
    print()
    print("  📡 Radar alerts:")
    print(f"     • Fall: L1 (跌倒)")
    print(f"     • SuspectedFall: L2 (疑似跌倒)")
    print(f"     • NoActivity24h: L1 (24小时无活动)")
    print(f"     • AbnormalHeartRate/RespiratoryRate: L1")
    print()
    print("  📊 Thresholds (vue_radar standard):")
    print("     • Heart Rate:")
    print("       - L1: <44 or >116 bpm (持续60秒)")
    print("       - L2: 45-54 or 96-115 bpm (持续300秒)")
    print("       - Normal: 55-95 bpm")
    print("     • Respiratory Rate:")
    print("       - L1: <7 or >27 breaths/min (持续60秒)")
    print("       - L2: 8-9 or 24-26 breaths/min (持续300秒)")
    print("       - Normal: 10-23 breaths/min")
    print()
    print("  🔔 Notification rules:")
    print("     • L1: WEB/APP/PHONE/EMAIL, 立即发送, 300秒重复")
    print("     • L2: WEB/APP, 延迟发送, 600秒重复")
    print("     • Escalation: L2持续300秒升级为L1")
    print("     • Suppression: 60秒内重复只发一次")
    print()
    print("🌐 Test API:")
    print(f"  GET /api/v1/alert_policies/{SAMPLE_TENANT_ID}")
    print()


if __name__ == "__main__":
    asyncio.run(create_sample_alert_policies())
