"""
IoT数据模型
对应 iot_timeseries (12_iot_timeseries.sql), iot_monitor_alerts (13_iot_monitor_alerts.sql) 表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# IOTTimeseries Models (IoT时序数据 - TimescaleDB超表)
# ============================================================================

class IOTTimeseriesBase(BaseModel):
    """IoT时序数据基础模型"""
    
    # 时间戳
    timestamp: datetime = Field(..., description="数据时间戳（NTP同步）")
    
    # TDP Tag Category（快速分类查询）
    tdp_tag_category: Optional[str] = Field(
        None, 
        max_length=50,
        description="TDP Tag分类：Physiological/Behavioral/Posture/MotionState/SleepState/Safety/HealthCondition/DeviceError"
    )
    
    # 轨迹数据
    tracking_id: Optional[int] = Field(None, description="目标ID（0-7，NULL表示无人）")
    radar_pos_x: int = Field(..., description="雷达坐标X（厘米）")
    radar_pos_y: int = Field(..., description="雷达坐标Y（厘米）")
    radar_pos_z: int = Field(..., description="雷达坐标Z（厘米）")
    
    # 姿态/运动状态（SNOMED CT编码）
    posture_snomed_code: Optional[str] = Field(None, max_length=50, description="SNOMED CT姿态编码（如383370001）")
    posture_display: Optional[str] = Field(None, max_length=100, description="姿态显示名称（如Standing position）")
    
    # 事件
    event_type: Optional[str] = Field(None, max_length=50, description="标准事件类型（如ENTER_ROOM, LEFT_BED）")
    event_display: Optional[str] = Field(None, max_length=100, description="事件显示名称")
    area_id: Optional[int] = Field(None, description="区域ID（ENTER_AREA/LEAVE_AREA时有效）")
    
    # 生命体征（标准值）
    heart_rate: Optional[int] = Field(None, description="心率（bpm），SNOMED: 364075005")
    respiratory_rate: Optional[int] = Field(None, description="呼吸率（次/分钟），SNOMED: 86290005")
    
    # 睡眠状态（从HR/RR推导）
    sleep_state_snomed_code: Optional[str] = Field(None, max_length=50, description="睡眠状态SNOMED CT编码")
    sleep_state_display: Optional[str] = Field(None, max_length=100, description="睡眠状态显示名称")
    
    # 位置信息（冗余，加速查询）
    location_id: Optional[UUID] = Field(None, description="门牌号/地址")
    room_id: Optional[UUID] = Field(None, description="房间ID")
    
    # 其他字段
    confidence: Optional[int] = Field(None, ge=0, le=100, description="置信度（0-100）")
    remaining_time: Optional[int] = Field(None, ge=0, le=60, description="剩余时间（0-60秒）")
    
    # 原始记录存储
    raw_original: bytes = Field(..., description="原始记录（厂家数据，可能压缩）")
    raw_format: str = Field(..., max_length=50, description="原始数据格式：json/binary/xml/string")
    raw_compression: Optional[str] = Field(None, max_length=50, description="压缩方式：gzip/deflate/NULL")
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="扩展信息")
    
    @field_validator("tdp_tag_category")
    @classmethod
    def validate_tdp_tag_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = [
                "Physiological", "Behavioral", "Posture", "MotionState",
                "SleepState", "Safety", "HealthCondition", "DeviceError"
            ]
            if v not in allowed:
                raise ValueError(f"tdp_tag_category must be one of {allowed}")
        return v
    
    @field_validator("raw_format")
    @classmethod
    def validate_raw_format(cls, v: str) -> str:
        allowed = ["json", "binary", "xml", "string"]
        if v not in allowed:
            raise ValueError(f"raw_format must be one of {allowed}")
        return v
    
    @field_validator("raw_compression")
    @classmethod
    def validate_raw_compression(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["gzip", "deflate"]
            if v not in allowed:
                raise ValueError(f"raw_compression must be one of {allowed}")
        return v


class IOTTimeseriesCreate(IOTTimeseriesBase):
    """创建IoT时序数据请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    device_id: UUID = Field(..., description="设备ID")


class IOTTimeseries(IOTTimeseriesBase):
    """IoT时序数据完整模型"""
    
    id: int = Field(..., description="自增ID（BIGSERIAL）")
    tenant_id: UUID = Field(..., description="所属租户ID")
    device_id: UUID = Field(..., description="设备ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123456789,
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "device_id": "550e8400-e29b-41d4-a716-446655440030",
                "timestamp": "2025-11-20T14:30:00Z",
                "tdp_tag_category": "Physiological",
                "tracking_id": 0,
                "radar_pos_x": 150,
                "radar_pos_y": 200,
                "radar_pos_z": 100,
                "posture_snomed_code": "102538003",
                "posture_display": "Lying position",
                "event_type": None,
                "event_display": None,
                "area_id": None,
                "heart_rate": 72,
                "respiratory_rate": 16,
                "sleep_state_snomed_code": "248233000",
                "sleep_state_display": "Deep sleep",
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "room_id": "550e8400-e29b-41d4-a716-446655440011",
                "confidence": 95,
                "remaining_time": None,
                "raw_format": "json",
                "raw_compression": None,
                "metadata": {}
            }
        }


# ============================================================================
# IOTMonitorAlert Models (IoT设备实时报警配置)
# ============================================================================

class IOTMonitorAlertBase(BaseModel):
    """IoT设备报警配置基础模型"""
    
    alert_type: str = Field(..., max_length=50, description="报警类型：LeftBed/ApneaHypopnea/AbnormalHeartRate/Fall等")
    iot_level: str = Field(..., max_length=10, description="IoT设备报警级别：L1/L2/DISABLE")
    vendor_config: Dict[str, Any] = Field(..., description="厂家原始阈值配置（JSON）")
    is_enabled: bool = Field(default=True, description="是否启用该报警类型")
    
    @field_validator("iot_level")
    @classmethod
    def validate_iot_level(cls, v: str) -> str:
        allowed = ["L1", "L2", "DISABLE"]
        if v not in allowed:
            raise ValueError(f"iot_level must be one of {allowed}")
        return v


class IOTMonitorAlertCreate(IOTMonitorAlertBase):
    """创建IoT报警配置请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    device_id: UUID = Field(..., description="设备ID")


class IOTMonitorAlertUpdate(BaseModel):
    """更新IoT报警配置请求模型"""
    
    iot_level: Optional[str] = Field(None, max_length=10)
    vendor_config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class IOTMonitorAlert(IOTMonitorAlertBase):
    """IoT设备报警配置完整模型"""
    
    alert_config_id: UUID = Field(default_factory=generate_uuid, description="报警配置唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    device_id: UUID = Field(..., description="设备ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_config_id": "550e8400-e29b-41d4-a716-446655440040",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "device_id": "550e8400-e29b-41d4-a716-446655440030",
                "alert_type": "AbnormalHeartRate",
                "iot_level": "L1",
                "vendor_config": {
                    "hr_below": 44,
                    "hr_above": 116,
                    "duration_sec": 60
                },
                "is_enabled": True
            }
        }
