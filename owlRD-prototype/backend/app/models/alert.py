"""
告警数据模型

对齐源参考：
1. TDPv2-0916.md - 协议定义（DangerLevel枚举：L1/L2/L3/L5/L8/L9）
2. 25_Alarm_Notification_Flow.md - 告警流程和级别说明
3. 14_cloud_alert_policies.sql - 云端告警策略表（CloudAlertPolicy）

注意：
- Alert模型是协议扩展实现，源SQL中没有对应表定义
- 告警级别使用 L1/L2/L3/L5/L8/L9/DISABLE（对齐TDPv2协议）
- 时间字段使用 timestamp（对齐协议中的alert_timestamp）
- 状态字段使用 pending/acknowledged/resolved/dismissed

包含：
1. Alert - 告警实例记录（协议扩展）
2. CloudAlertPolicy - 云端告警策略配置（对齐14_cloud_alert_policies.sql）
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import Field, field_validator

from app.models.base import BaseModel


# ============================================================================
# Enums (枚举类型)
# ============================================================================

class AlertLevel(str, Enum):
    """告警级别（基于TDPv2协议）"""
    EMERGENCY = "L1"      # 紧急，高风险，高置信
    ALERT = "L2"          # 警报，高危事件
    CRITICAL = "L3"       # 严重（较少使用）
    WARNING = "L5"        # 警告（较少使用）
    DEBUG = "L8"          # 调试（较少使用）
    CANCEL = "L9"         # 取消
    DISABLE = "DISABLE"   # 关闭


class AlertStatus(str, Enum):
    """告警状态"""
    PENDING = "pending"           # 待处理
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"          # 已解决
    DISMISSED = "dismissed"        # 已忽略


class AlertScope(str, Enum):
    """告警接收范围"""
    ALL = "ALL"                       # 全机构
    LOCATION_TAG = "LOCATION-TAG"     # 按地点标签
    ASSIGNED_ONLY = "ASSIGNED_ONLY"   # 仅负责的住户


class DangerLevel(str, Enum):
    """危险等级（用于CloudAlertPolicy字段值）"""
    L1 = "L1"             # EMERGENCY
    L2 = "L2"             # ALERT
    DISABLE = "DISABLE"   # 关闭


# ============================================================================
# Alert Models (告警实例记录)
# ============================================================================

class AlertBase(BaseModel):
    """告警实例基础模型"""
    alert_level: str = Field(..., description="告警级别: L1/L2/L3/L5")
    alert_type: str = Field(..., description="告警类型: FALL/LEAVE/HEART_RATE等")
    message: str = Field(..., description="告警消息")
    resident_id: Optional[UUID] = Field(None, description="关联住户ID")
    device_id: Optional[UUID] = Field(None, description="关联设备ID")
    location_id: Optional[UUID] = Field(None, description="关联位置ID")
    status: str = Field(default="pending", description="告警状态: pending/acknowledged/resolved")
    acknowledged_by: Optional[UUID] = Field(None, description="确认人ID")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    resolved_by: Optional[UUID] = Field(None, description="解决人ID")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    
    # 告警升级/抑制机制（25_Alarm_Notification_Flow.md）
    escalation_level: Optional[int] = Field(None, ge=0, le=3, description="升级级别: 0=初始, 1-3=升级次数")
    escalated_at: Optional[datetime] = Field(None, description="最后升级时间")
    suppressed_until: Optional[datetime] = Field(None, description="抑制到期时间（静默期）")
    auto_escalate: bool = Field(default=True, description="是否启用自动升级")


class AlertCreate(AlertBase):
    """创建告警请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class AlertUpdate(BaseModel):
    """更新告警请求模型"""
    status: Optional[str] = Field(None, description="告警状态")
    acknowledged_by: Optional[UUID] = Field(None, description="确认人ID")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    resolved_by: Optional[UUID] = Field(None, description="解决人ID")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    note: Optional[str] = Field(None, description="备注")
    resolution: Optional[str] = Field(None, description="解决说明")


class Alert(AlertBase):
    """告警完整模型（对齐前端Alert接口）"""
    alert_id: UUID = Field(..., description="告警ID")
    tenant_id: UUID = Field(..., description="所属租户ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="告警发生时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "alert_level": "L1",
                "alert_type": "FALL",
                "message": "检测到住户张三疑似跌倒",
                "timestamp": "2025-11-22T10:30:00Z",
                "status": "pending",
                "resident_id": "660e8400-e29b-41d4-a716-446655440001",
                "device_id": "770e8400-e29b-41d4-a716-446655440002",
                "location_id": "880e8400-e29b-41d4-a716-446655440003"
            }
        }


# ============================================================================
# CloudAlertPolicy Models (云端告警策略)
# ============================================================================

class CloudAlertPolicyBase(BaseModel):
    """云端告警策略基础模型"""
    
    # ========== Common 报警类型 ==========
    OfflineAlarm: Optional[str] = Field(None, max_length=10, description="离线告警级别：DISABLE/L1/L2/NULL")
    LowBattery: Optional[str] = Field(None, max_length=10, description="低电量告警级别")
    DeviceFailure: Optional[str] = Field(None, max_length=10, description="设备故障告警级别")
    
    # ========== SleepMonitor 报警类型 ==========
    SleepPad_LeftBed: Optional[str] = Field(None, max_length=10, description="睡眠板离床告警级别")
    SleepPad_SitUp: Optional[str] = Field(None, max_length=10, description="睡眠板坐起告警级别")
    SleepPad_ApneaHypopnea: Optional[str] = Field(None, max_length=10, description="睡眠板呼吸暂停告警级别")
    SleepPad_AbnormalHeartRate: Optional[str] = Field(None, max_length=10, description="睡眠板心率异常告警级别")
    SleepPad_AbnormalRespiratoryRate: Optional[str] = Field(None, max_length=10, description="睡眠板呼吸率异常告警级别")
    SleepPad_AbnormalBodyMovement: Optional[str] = Field(None, max_length=10, description="睡眠板异常体动告警级别")
    SleepPad_InBed: Optional[str] = Field(None, max_length=10, description="睡眠板在床告警级别")
    
    # ========== Radar 报警类型 ==========
    Radar_AbnormalHeartRate: Optional[str] = Field(None, max_length=10, description="雷达心率异常告警级别")
    Radar_AbnormalRespiratoryRate: Optional[str] = Field(None, max_length=10, description="雷达呼吸率异常告警级别")
    SuspectedFall: Optional[str] = Field(None, max_length=10, description="疑似跌倒告警级别")
    Fall: Optional[str] = Field(None, max_length=10, description="跌倒告警级别")
    VitalsWeak: Optional[str] = Field(None, max_length=10, description="生命体征微弱告警级别")
    Radar_LeftBed: Optional[str] = Field(None, max_length=10, description="雷达离床告警级别")
    Stay: Optional[str] = Field(None, max_length=10, description="长时间滞留告警级别")
    NoActivity24h: Optional[str] = Field(None, max_length=10, description="24小时无活动告警级别")
    AngleException: Optional[str] = Field(None, max_length=10, description="角度异常告警级别")
    
    # ========== 自定义报警类型（预留扩展）==========
    CustomAlert1: Optional[str] = Field(None, max_length=10, description="自定义报警1级别")
    CustomAlert2: Optional[str] = Field(None, max_length=10, description="自定义报警2级别")
    CustomAlert3: Optional[str] = Field(None, max_length=10, description="自定义报警3级别")
    
    # ========== 报警阈值配置 ==========
    conditions: Optional[Dict[str, Any]] = Field(
        None,
        description="报警阈值配置（心率/呼吸率等生理指标）"
    )
    
    # ========== 发送模式配置 ==========
    notification_rules: Optional[Dict[str, Any]] = Field(
        None,
        description="发送模式配置（通知通道、发送方式、升级规则、抑制规则、静默规则）"
    )
    
    # 状态
    is_active: bool = Field(default=True, description="是否启用")
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="扩展信息")
    
    @field_validator(
        "OfflineAlarm", "LowBattery", "DeviceFailure",
        "SleepPad_LeftBed", "SleepPad_SitUp", "SleepPad_ApneaHypopnea",
        "SleepPad_AbnormalHeartRate", "SleepPad_AbnormalRespiratoryRate",
        "SleepPad_AbnormalBodyMovement", "SleepPad_InBed",
        "Radar_AbnormalHeartRate", "Radar_AbnormalRespiratoryRate",
        "SuspectedFall", "Fall", "VitalsWeak", "Radar_LeftBed",
        "Stay", "NoActivity24h", "AngleException",
        "CustomAlert1", "CustomAlert2", "CustomAlert3"
    )
    @classmethod
    def validate_danger_level(cls, v: Optional[str]) -> Optional[str]:
        """验证DangerLevel字段值"""
        if v is not None:
            allowed = ["DISABLE", "L1", "L2"]
            if v not in allowed:
                raise ValueError(f"DangerLevel must be one of {allowed}")
        return v


class CloudAlertPolicyCreate(CloudAlertPolicyBase):
    """创建云端告警策略请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class CloudAlertPolicyUpdate(CloudAlertPolicyBase):
    """更新云端告警策略请求模型"""
    pass


class CloudAlertPolicy(CloudAlertPolicyBase):
    """云端告警策略完整模型"""
    
    tenant_id: UUID = Field(..., description="所属租户ID（主键）")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "OfflineAlarm": "L2",
                "LowBattery": "L2",
                "DeviceFailure": "L1",
                "SleepPad_LeftBed": "L2",
                "SleepPad_ApneaHypopnea": "L1",
                "SleepPad_AbnormalHeartRate": "L1",
                "SleepPad_AbnormalRespiratoryRate": "L1",
                "Radar_AbnormalHeartRate": "L1",
                "Fall": "L1",
                "SuspectedFall": "L2",
                "NoActivity24h": "L2",
                "conditions": {
                    "heart_rate": {
                        "L1": {
                            "ranges": [{"min": 0, "max": 44}, {"min": 116, "max": None}],
                            "duration_sec": 60
                        },
                        "L2": {
                            "ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}],
                            "duration_sec": 300
                        }
                    },
                    "respiratory_rate": {
                        "L1": {
                            "ranges": [{"min": 0, "max": 7}, {"min": 27, "max": None}],
                            "duration_sec": 60
                        }
                    }
                },
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
                    }
                },
                "is_active": True,
                "metadata": {}
            }
        }
