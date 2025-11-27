"""
设备数据模型
对应 devices 表 (11_devices.sql)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


class DeviceBase(BaseModel):
    """设备基础模型"""
    
    # 设备标识
    device_name: str = Field(..., max_length=100, description="设备名称")
    device_model: str = Field(..., max_length=50, description="设备型号（如WF-RADAR-60G-V2）")
    device_type: str = Field(..., max_length=50, description="设备类型：Radar/SleepPad/VibrationSensor/Gateway等")
    
    # 序列号/UID（至少填一个）
    serial_number: Optional[str] = Field(None, max_length=100, description="厂家序列号")
    uid: Optional[str] = Field(None, max_length=50, description="厂家或平台提供的唯一UID")
    imei: Optional[str] = Field(None, max_length=50, description="4G设备IMEI")
    
    # 技术规格
    comm_mode: str = Field(..., max_length=20, description="通讯方式：WiFi/LTE/Zigbee等")
    firmware_version: str = Field(..., max_length=50, description="主业务固件版本")
    mcu_model: Optional[str] = Field(None, max_length=50, description="MCU/主控型号（如STM32F4、ESP32）")
    
    # 位置绑定
    location_id: Optional[UUID] = Field(None, description="绑定位置ID")
    bound_room_id: Optional[UUID] = Field(None, description="绑定房间ID")
    bound_bed_id: Optional[UUID] = Field(None, description="绑定床位ID")
    
    # 状态/维护
    status: str = Field(..., max_length=20, description="实时状态：online/offline/error等")
    installed: bool = Field(default=True, description="设备是否已安装（物理存在）")
    business_access: bool = Field(default=False, description="是否允许接入系统（管理员审批）")
    monitoring_enabled: bool = Field(default=False, description="是否启用监护功能")
    installation_date_utc: datetime = Field(..., description="设备安装日期（UTC）")
    
    # 扩展配置/标签
    metadata: Optional[Dict[str, Any]] = Field(None, description="设备元数据（如vue_radar的IoT配置）")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["online", "offline", "error", "dormant", "maintenance"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v
    
    @field_validator("comm_mode")
    @classmethod
    def validate_comm_mode(cls, v: str) -> str:
        allowed = ["WiFi", "LTE", "Zigbee", "Ethernet", "LoRa"]
        if v not in allowed:
            raise ValueError(f"comm_mode must be one of {allowed}")
        return v


class DeviceCreate(DeviceBase):
    """创建设备请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    
    @field_validator("serial_number", "uid")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        """至少需要serial_number或uid其中之一"""
        values = info.data
        if not any([v, values.get("serial_number"), values.get("uid")]):
            raise ValueError("Must provide at least one of: serial_number or uid")
        return v


class DeviceUpdate(BaseModel):
    """更新设备请求模型"""
    
    device_name: Optional[str] = Field(None, max_length=100)
    device_model: Optional[str] = Field(None, max_length=50)
    device_type: Optional[str] = Field(None, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=100)
    uid: Optional[str] = Field(None, max_length=50)
    imei: Optional[str] = Field(None, max_length=50)
    comm_mode: Optional[str] = Field(None, max_length=20)
    firmware_version: Optional[str] = Field(None, max_length=50)
    mcu_model: Optional[str] = Field(None, max_length=50)
    location_id: Optional[UUID] = None
    bound_room_id: Optional[UUID] = None
    bound_bed_id: Optional[UUID] = None
    status: Optional[str] = Field(None, max_length=20)
    installed: Optional[bool] = None
    business_access: Optional[bool] = None
    monitoring_enabled: Optional[bool] = None
    installation_date_utc: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Device(DeviceBase):
    """设备完整模型"""
    
    device_id: UUID = Field(default_factory=generate_uuid, description="设备唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "550e8400-e29b-41d4-a716-446655440030",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "device_name": "Radar-E203-001",
                "device_model": "WF-RADAR-60G-V2",
                "device_type": "Radar",
                "serial_number": "SN20250001",
                "uid": "F59D3E873F8F",
                "imei": None,
                "comm_mode": "WiFi",
                "firmware_version": "2.3.1",
                "mcu_model": "ESP32-P4",
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "bound_room_id": "550e8400-e29b-41d4-a716-446655440011",
                "bound_bed_id": "550e8400-e29b-41d4-a716-446655440012",
                "status": "online",
                "installed": True,
                "business_access": True,
                "monitoring_enabled": True,
                "installation_date_utc": "2025-01-01T00:00:00Z",
                "metadata": {
                    "iot": {
                        "deviceId": "Radar01",
                        "radar": {
                            "installModel": "wall",
                            "workModel": "vital-sign",
                            "rotation": 0,
                            "hfov": 140,
                            "vfov": 120,
                            "boundary": {"leftH": 300, "rightH": 300, "frontV": 400, "rearV": 0},
                            "signalRadius": 500
                        }
                    }
                }
            }
        }
