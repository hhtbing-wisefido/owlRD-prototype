"""
云端告警策略管理API端点

对齐源参考：
- 14_cloud_alert_policies.sql - 云端告警策略表定义
- TDPv2-0916.md - DangerLevel定义（L1/L2/DISABLE）
- 25_Alarm_Notification_Flow.md - 告警策略配置说明

字段说明：
- DangerLevel字段：DISABLE/L1/L2（每个报警类型对应一个危险等级）
- notification_rules: 通知规则配置（通道、升级、抑制、静默）
- conditions: 报警阈值配置（心率、呼吸率等生理指标）
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.models.alert import CloudAlertPolicy, CloudAlertPolicyCreate, CloudAlertPolicyUpdate
from app.services.storage import StorageService

router = APIRouter()
policy_storage = StorageService[CloudAlertPolicy]("cloud_alert_policies")


@router.get("/", response_model=list[CloudAlertPolicy])
async def list_alert_policies(
    tenant_id: Optional[UUID] = Query(None, description="租户ID筛选")
):
    """
    获取告警策略列表
    
    Args:
        tenant_id: 可选的租户ID筛选
    
    Returns:
        告警策略列表
    """
    if tenant_id:
        policy = policy_storage.find_by_id("tenant_id", str(tenant_id))
        return [policy] if policy else []
    else:
        policies = policy_storage.find_all()
        return policies


@router.get("/{tenant_id}", response_model=CloudAlertPolicy)
async def get_alert_policy(tenant_id: UUID):
    """
    获取租户的告警策略配置
    
    每个租户只有一条配置记录
    - **tenant_id**: 租户ID（主键）
    """
    policy = policy_storage.find_by_id("tenant_id", tenant_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Alert policy not found for this tenant")
    return policy


@router.post("", response_model=CloudAlertPolicy, status_code=201)
async def create_alert_policy(policy_data: CloudAlertPolicyCreate):
    """
    为租户创建告警策略配置
    
    **注意**：
    - 每个租户只能有一条配置记录
    - 创建新租户时应该同时初始化告警策略
    - 所有报警类型字段值必须是 'DISABLE', 'L1', 'L2' 或 NULL
    
    **默认值建议**：
    - OfflineAlarm: L2
    - LowBattery: L2
    - DeviceFailure: L1
    - SleepPad_LeftBed: L2
    - SleepPad_ApneaHypopnea: L1
    - Fall: L1
    - SuspectedFall: L2
    
    **阈值配置示例** (conditions):
    ```json
    {
      "heart_rate": {
        "L1": { "ranges": [{"min": 0, "max": 44}, {"min": 116, "max": null}], "duration_sec": 60 },
        "L2": { "ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}], "duration_sec": 300 }
      },
      "respiratory_rate": {
        "L1": { "ranges": [{"min": 0, "max": 7}, {"min": 27, "max": null}], "duration_sec": 60 },
        "L2": { "ranges": [{"min": 8, "max": 9}, {"min": 24, "max": 26}], "duration_sec": 300 }
      }
    }
    ```
    
    **通知规则示例** (notification_rules):
    ```json
    {
      "L1": {
        "channels": ["WEB", "APP", "PHONE", "EMAIL"],
        "immediate": true,
        "repeat_interval_sec": 300
      },
      "L2": {
        "channels": ["WEB", "APP"],
        "immediate": false,
        "repeat_interval_sec": 600
      },
      "escalation": {
        "enabled": true,
        "escalate_after_sec": 300,
        "escalate_to_level": "L1"
      },
      "suppression": {
        "enabled": true,
        "suppress_duplicate_sec": 60,
        "max_alerts_per_hour": 10
      },
      "silence": {
        "enabled": false,
        "silence_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6],
        "silence_days": ["Saturday", "Sunday"]
      }
    }
    ```
    """
    # 检查租户是否已有配置
    existing_policy = policy_storage.find_by_id("tenant_id", policy_data.tenant_id)
    if existing_policy:
        raise HTTPException(
            status_code=400,
            detail=f"Alert policy already exists for tenant {policy_data.tenant_id}"
        )
    
    # 创建策略
    from app.models.base import generate_uuid
    policy_dict = policy_data.model_dump()
    policy_dict["created_at"] = datetime.now().isoformat()
    policy_dict["updated_at"] = datetime.now().isoformat()
    
    # 如果未提供conditions，使用默认阈值（基于vue_radar标准）
    if not policy_dict.get("conditions"):
        policy_dict["conditions"] = {
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
        }
    
    policy_storage.create(policy_dict)
    return policy_dict


@router.put("/{tenant_id}", response_model=CloudAlertPolicy)
async def update_alert_policy(tenant_id: UUID, policy_data: CloudAlertPolicyUpdate):
    """
    更新租户的告警策略配置
    
    可以单独更新任何字段，未提供的字段保持不变
    - **tenant_id**: 租户ID
    
    **常见更新场景**：
    1. 调整某个告警类型的级别：如将Fall从L1改为L2
    2. 修改阈值配置：如调整心率异常的范围
    3. 更新通知规则：如修改通知通道或重复间隔
    4. 启用/禁用静默规则：如夜间不发送告警
    """
    # 读取现有策略
    existing_policy = policy_storage.find_by_id("tenant_id", tenant_id)
    if not existing_policy:
        raise HTTPException(status_code=404, detail="Alert policy not found for this tenant")
    
    # 更新字段
    update_data = policy_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    # 保存更新
    updated = policy_storage.update("tenant_id", tenant_id, update_data)
    return updated


@router.delete("/{tenant_id}", status_code=204)
async def delete_alert_policy(tenant_id: UUID):
    """
    删除租户的告警策略配置
    
    **警告**：删除后租户将没有告警配置，建议谨慎操作
    - **tenant_id**: 租户ID
    """
    # 读取策略
    policy = policy_storage.find_by_id("tenant_id", tenant_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Alert policy not found for this tenant")
    
    # 删除策略
    policy_storage.delete("tenant_id", tenant_id)
    return None


@router.post("/{tenant_id}/initialize", response_model=CloudAlertPolicy, status_code=201)
async def initialize_tenant_alert_policy(tenant_id: UUID):
    """
    为新租户初始化默认告警策略
    
    **使用场景**：创建新租户时自动调用
    
    **默认配置**：
    - Common: OfflineAlarm=L2, LowBattery=L2, DeviceFailure=L1
    - SleepMonitor: LeftBed=L2, SitUp=L2, ApneaHypopnea=L1, HR/RR=L1, BodyMovement=L2, InBed=DISABLE
    - Radar: HR/RR=L1, SuspectedFall=L2, Fall=L1, VitalsWeak=L2, LeftBed=L2, Stay=L2, NoActivity=L1, AngleException=L2
    - 自定义报警: 全部NULL（未启用）
    - 阈值: 基于vue_radar项目的老年群体优化标准
    """
    # 检查是否已有配置
    existing_policy = policy_storage.find_by_id("tenant_id", tenant_id)
    if existing_policy:
        raise HTTPException(
            status_code=400,
            detail=f"Alert policy already exists for tenant {tenant_id}, use PUT to update"
        )
    
    # 创建默认配置
    default_policy = {
        "tenant_id": str(tenant_id),
        # Common
        "OfflineAlarm": "L2",
        "LowBattery": "L2",
        "DeviceFailure": "L1",
        # SleepMonitor
        "SleepPad_LeftBed": "L2",
        "SleepPad_SitUp": "L2",
        "SleepPad_ApneaHypopnea": "L1",
        "SleepPad_AbnormalHeartRate": "L1",
        "SleepPad_AbnormalRespiratoryRate": "L1",
        "SleepPad_AbnormalBodyMovement": "L2",
        "SleepPad_InBed": "DISABLE",
        # Radar
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
        # 默认阈值（基于vue_radar标准）
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
            "initialized_by": "system",
            "initialization_date": datetime.now().isoformat()
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    policy_storage.create(default_policy)
    return default_policy
