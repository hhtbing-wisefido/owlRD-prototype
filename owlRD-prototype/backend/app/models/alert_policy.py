"""
告警策略模型（简化版）
Alert Policy Model (Simplified)

对应源参考文件：
- db/14_cloud_alert_policies.sql
- docs/TDPv2-0916.md (DangerLevel定义)

简化说明：
原SQL文件包含20+个告警类型字段，本模型采用更灵活的JSONB方式存储，
便于扩展和维护。核心功能保持不变。

DangerLevel定义：
- L1 (EMERGENCY): 紧急，高风险，高置信
- L2 (ALERT): 警报，高危事件
- DISABLE: 关闭该类报警

告警类型分类：
- Common: OfflineAlarm, LowBattery, DeviceFailure
- SleepMonitor: LeftBed, SitUp, ApneaHypopnea, AbnormalHeartRate等
- Radar: AbnormalHeartRate, AbnormalRespiratoryRate, Fall, SuspectedFall等
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class DangerLevel(str, Enum):
    """危险等级枚举"""
    DISABLE = "DISABLE"  # 禁用
    L1 = "L1"           # 紧急
    L2 = "L2"           # 警报

class AlertCategory(str, Enum):
    """告警类别"""
    COMMON = "Common"              # 通用告警
    SLEEP_MONITOR = "SleepMonitor" # 睡眠监测
    RADAR = "Radar"                # 雷达监测
    CUSTOM = "Custom"              # 自定义

class AlertTypeConfig(BaseModel):
    """单个告警类型配置"""
    alert_type: str = Field(..., description="告警类型名称")
    danger_level: DangerLevel = Field(..., description="危险等级")
    category: AlertCategory = Field(..., description="告警类别")
    enabled: bool = Field(True, description="是否启用")
    
    # 条件配置（如心率阈值）
    conditions: Optional[Dict[str, Any]] = Field(None, description="触发条件")
    
    # 通知规则
    notification_rules: Optional[Dict[str, Any]] = Field(None, description="通知规则")
    
    class Config:
        use_enum_values = True

class VitalSignThreshold(BaseModel):
    """生理指标阈值配置"""
    vital_type: str = Field(..., description="生理指标类型: heart_rate/respiratory_rate")
    
    # L1级别阈值
    l1_ranges: List[Dict[str, Optional[float]]] = Field(
        ...,
        description="L1级别范围: [{'min': 0, 'max': 44}, {'min': 116, 'max': null}]"
    )
    l1_duration_sec: int = Field(60, description="L1持续时间（秒）")
    
    # L2级别阈值
    l2_ranges: List[Dict[str, Optional[float]]] = Field(
        ...,
        description="L2级别范围"
    )
    l2_duration_sec: int = Field(300, description="L2持续时间（秒）")
    
    # 正常范围
    normal_ranges: List[Dict[str, Optional[float]]] = Field(
        ...,
        description="正常范围"
    )

class NotificationChannel(str, Enum):
    """通知渠道"""
    WEB = "WEB"
    APP = "APP"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    SMS = "SMS"

class NotificationRule(BaseModel):
    """通知规则配置"""
    level: DangerLevel = Field(..., description="危险等级")
    channels: List[NotificationChannel] = Field(..., description="通知渠道")
    immediate: bool = Field(True, description="是否立即发送")
    repeat_interval_sec: int = Field(300, description="重复发送间隔（秒）")

class EscalationRule(BaseModel):
    """升级规则"""
    enabled: bool = Field(False, description="是否启用")
    escalate_after_sec: int = Field(300, description="升级等待时间（秒）")
    escalate_to_level: DangerLevel = Field(DangerLevel.L1, description="升级到的等级")

class SuppressionRule(BaseModel):
    """抑制规则"""
    enabled: bool = Field(True, description="是否启用")
    suppress_duplicate_sec: int = Field(60, description="重复告警抑制时间（秒）")
    max_alerts_per_hour: int = Field(10, description="每小时最大告警数")

class SilenceRule(BaseModel):
    """静默规则"""
    enabled: bool = Field(False, description="是否启用")
    silence_hours: List[int] = Field(
        default_factory=list,
        description="静默小时: [22, 23, 0, 1, 2, 3, 4, 5, 6]"
    )
    silence_days: List[str] = Field(
        default_factory=list,
        description="静默日期: ['Saturday', 'Sunday']"
    )

class AlertPolicyBase(BaseModel):
    """告警策略基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    
    # 告警类型配置（JSONB存储）
    alert_types: Dict[str, AlertTypeConfig] = Field(
        default_factory=dict,
        description="告警类型配置映射"
    )
    
    # 生理指标阈值配置
    vital_thresholds: Dict[str, VitalSignThreshold] = Field(
        default_factory=dict,
        description="生理指标阈值配置"
    )
    
    # 通知规则配置
    notification_rules: List[NotificationRule] = Field(
        default_factory=list,
        description="通知规则列表"
    )
    
    # 升级规则
    escalation: Optional[EscalationRule] = Field(None, description="升级规则")
    
    # 抑制规则
    suppression: Optional[SuppressionRule] = Field(None, description="抑制规则")
    
    # 静默规则
    silence: Optional[SilenceRule] = Field(None, description="静默规则")
    
    # 状态
    is_active: bool = Field(True, description="是否激活")
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="扩展元数据")

class AlertPolicyCreate(AlertPolicyBase):
    """创建告警策略"""
    pass

class AlertPolicyUpdate(BaseModel):
    """更新告警策略"""
    alert_types: Optional[Dict[str, AlertTypeConfig]] = None
    vital_thresholds: Optional[Dict[str, VitalSignThreshold]] = None
    notification_rules: Optional[List[NotificationRule]] = None
    escalation: Optional[EscalationRule] = None
    suppression: Optional[SuppressionRule] = None
    silence: Optional[SilenceRule] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertPolicy(AlertPolicyBase):
    """告警策略完整模型"""
    policy_id: UUID = Field(default_factory=uuid4, description="策略ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "policy_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "alert_types": {
                    "OfflineAlarm": {
                        "alert_type": "OfflineAlarm",
                        "danger_level": "L2",
                        "category": "Common",
                        "enabled": True
                    },
                    "Fall": {
                        "alert_type": "Fall",
                        "danger_level": "L1",
                        "category": "Radar",
                        "enabled": True
                    }
                },
                "vital_thresholds": {
                    "heart_rate": {
                        "vital_type": "heart_rate",
                        "l1_ranges": [{"min": 0, "max": 44}, {"min": 116, "max": None}],
                        "l1_duration_sec": 60,
                        "l2_ranges": [{"min": 45, "max": 54}, {"min": 96, "max": 115}],
                        "l2_duration_sec": 300,
                        "normal_ranges": [{"min": 55, "max": 95}]
                    }
                },
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def get_alert_type_level(self, alert_type: str) -> Optional[DangerLevel]:
        """获取指定告警类型的危险等级"""
        if alert_type in self.alert_types:
            return self.alert_types[alert_type].danger_level
        return None

    def is_alert_type_enabled(self, alert_type: str) -> bool:
        """检查告警类型是否启用"""
        if alert_type in self.alert_types:
            config = self.alert_types[alert_type]
            return config.enabled and config.danger_level != DangerLevel.DISABLE
        return False

    def get_notification_channels_for_level(self, level: DangerLevel) -> List[NotificationChannel]:
        """获取指定危险等级的通知渠道"""
        for rule in self.notification_rules:
            if rule.level == level:
                return rule.channels
        return []

class AlertPolicySummary(BaseModel):
    """告警策略摘要"""
    policy_id: UUID
    tenant_id: UUID
    total_alert_types: int = Field(0, description="总告警类型数")
    enabled_alert_types: int = Field(0, description="启用的告警类型数")
    l1_alert_types: int = Field(0, description="L1级别告警数")
    l2_alert_types: int = Field(0, description="L2级别告警数")
    is_active: bool
    
    class Config:
        from_attributes = True

# 默认配置生成器
class DefaultAlertPolicyFactory:
    """默认告警策略工厂"""
    
    @staticmethod
    def create_default_policy(tenant_id: UUID) -> AlertPolicyCreate:
        """创建默认告警策略"""
        return AlertPolicyCreate(
            tenant_id=tenant_id,
            alert_types={
                # Common alerts
                "OfflineAlarm": AlertTypeConfig(
                    alert_type="OfflineAlarm",
                    danger_level=DangerLevel.L2,
                    category=AlertCategory.COMMON,
                    enabled=True
                ),
                "LowBattery": AlertTypeConfig(
                    alert_type="LowBattery",
                    danger_level=DangerLevel.L2,
                    category=AlertCategory.COMMON,
                    enabled=True
                ),
                "DeviceFailure": AlertTypeConfig(
                    alert_type="DeviceFailure",
                    danger_level=DangerLevel.L1,
                    category=AlertCategory.COMMON,
                    enabled=True
                ),
                # Radar alerts
                "Fall": AlertTypeConfig(
                    alert_type="Fall",
                    danger_level=DangerLevel.L1,
                    category=AlertCategory.RADAR,
                    enabled=True
                ),
                "SuspectedFall": AlertTypeConfig(
                    alert_type="SuspectedFall",
                    danger_level=DangerLevel.L2,
                    category=AlertCategory.RADAR,
                    enabled=True
                )
            },
            vital_thresholds={
                "heart_rate": VitalSignThreshold(
                    vital_type="heart_rate",
                    l1_ranges=[{"min": 0, "max": 44}, {"min": 116, "max": None}],
                    l1_duration_sec=60,
                    l2_ranges=[{"min": 45, "max": 54}, {"min": 96, "max": 115}],
                    l2_duration_sec=300,
                    normal_ranges=[{"min": 55, "max": 95}]
                ),
                "respiratory_rate": VitalSignThreshold(
                    vital_type="respiratory_rate",
                    l1_ranges=[{"min": 0, "max": 7}, {"min": 27, "max": None}],
                    l1_duration_sec=60,
                    l2_ranges=[{"min": 8, "max": 9}, {"min": 24, "max": 26}],
                    l2_duration_sec=300,
                    normal_ranges=[{"min": 10, "max": 23}]
                )
            },
            notification_rules=[
                NotificationRule(
                    level=DangerLevel.L1,
                    channels=[
                        NotificationChannel.WEB,
                        NotificationChannel.APP,
                        NotificationChannel.PHONE
                    ],
                    immediate=True,
                    repeat_interval_sec=300
                ),
                NotificationRule(
                    level=DangerLevel.L2,
                    channels=[
                        NotificationChannel.WEB,
                        NotificationChannel.APP
                    ],
                    immediate=False,
                    repeat_interval_sec=600
                )
            ],
            is_active=True
        )
