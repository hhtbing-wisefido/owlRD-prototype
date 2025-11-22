"""
位置相关数据模型

对齐源参考：
- 04_locations.sql - 位置表定义
- 05_rooms.sql - 房间表定义
- 06_beds.sql - 床位表定义
- 25_Alarm_Notification_Flow.md - Location卡片告警路由规则
  * alert_user_ids: 直接指定的告警接收者
  * alert_tags: 标签匹配的告警接收者（如NightShift, TeamA）
  * 用于公共空间/多人房间的告警路由
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# Location Models (位置模型)
# ============================================================================

class LocationBase(BaseModel):
    """位置基础模型"""
    
    # 位置标签和名称
    location_tag: Optional[str] = Field(None, max_length=255, description="位置标签（如 'A院区主楼'、'Spring区域组SP'）")
    location_name: str = Field(..., max_length=255, description="位置名称（如 'E203'、'201'、'Home-001'）")
    
    # Institutional场景地址字段
    building: Optional[str] = Field(None, max_length=50, description="楼栋（机构场景，如 'Building A'、'主楼'）")
    floor: Optional[str] = Field(None, max_length=50, description="楼层（机构场景，如 '1F'、'2F'）")
    area_id: Optional[str] = Field(None, max_length=100, description="区域ID（机构场景，如 'Area A'、'Memory Care Unit'）")
    door_number: str = Field(..., max_length=255, description="门牌号/房间号（机构场景，如 '201'、'E203'）")
    
    # 布局配置
    layout_config: Optional[Dict[str, Any]] = Field(None, description="房间布局配置（JSON，vue_radar canvasData格式）")
    
    # 场景类型
    location_type: str = Field(..., max_length=20, description="场景类型：Institutional / HomeCare")
    
    # 主要关联住户
    primary_resident_id: Optional[UUID] = Field(None, description="主要关联住户ID（HomeCare/单间/夫妻套房必须设置）")
    
    # 空间属性
    is_public_space: bool = Field(default=False, description="是否为公共空间（大厅、走廊、电梯等）")
    is_multi_person_room: bool = Field(default=False, description="是否多人房间（仅Institutional场景）")
    
    # 路由和状态
    timezone: str = Field(..., max_length=50, description="IANA时区格式（如 'America/Los_Angeles'）")
    alert_user_ids: Optional[List[UUID]] = Field(None, description="警报接收者用户ID列表（直接指定）")
    alert_tags: Optional[List[str]] = Field(None, description="警报接收者标签组（匹配users.tags）")
    is_active: bool = Field(default=True, description="是否启用监控")
    
    @field_validator("location_type")
    @classmethod
    def validate_location_type(cls, v: str) -> str:
        allowed = ["Institutional", "HomeCare"]
        if v not in allowed:
            raise ValueError(f"location_type must be one of {allowed}")
        return v


class LocationCreate(LocationBase):
    """创建位置请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class LocationUpdate(BaseModel):
    """更新位置请求模型"""
    
    location_tag: Optional[str] = Field(None, max_length=255)
    location_name: Optional[str] = Field(None, max_length=255)
    building: Optional[str] = Field(None, max_length=50)
    floor: Optional[str] = Field(None, max_length=50)
    area_id: Optional[str] = Field(None, max_length=100)
    door_number: Optional[str] = Field(None, max_length=255)
    layout_config: Optional[Dict[str, Any]] = None
    location_type: Optional[str] = Field(None, max_length=20)
    primary_resident_id: Optional[UUID] = None
    is_public_space: Optional[bool] = None
    is_multi_person_room: Optional[bool] = None
    timezone: Optional[str] = Field(None, max_length=50)
    alert_user_ids: Optional[List[UUID]] = None
    alert_tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Location(LocationBase):
    """位置完整模型"""
    
    location_id: UUID = Field(default_factory=generate_uuid, description="位置唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_tag": "Spring区域组SP",
                "location_name": "E203",
                "building": "Building A",
                "floor": "2F",
                "area_id": "Memory Care Unit",
                "door_number": "E203",
                "layout_config": {
                    "params": {"width": 1000, "height": 800},
                    "objects": [],
                    "timestamp": "2025-11-20T14:00:00Z"
                },
                "location_type": "Institutional",
                "primary_resident_id": None,
                "is_public_space": False,
                "is_multi_person_room": False,
                "timezone": "America/Los_Angeles",
                "alert_user_ids": [],
                "alert_tags": ["NightShift", "TeamA"],
                "is_active": True
            }
        }


# ============================================================================
# Room Models (房间模型)
# ============================================================================

class RoomBase(BaseModel):
    """房间基础模型"""
    
    is_default: bool = Field(default=False, description="是否默认房间（创建Location时自动生成）")
    room_name: str = Field(..., max_length=100, description="房间名称（如 'Bedroom'、'Bathroom'）")
    is_active: bool = Field(default=True, description="是否启用")
    layout_config: Optional[Dict[str, Any]] = Field(None, description="房间级独立布局配置（JSON）")


class RoomCreate(RoomBase):
    """创建房间请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    location_id: UUID = Field(..., description="所属位置ID")


class RoomUpdate(BaseModel):
    """更新房间请求模型"""
    
    room_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    layout_config: Optional[Dict[str, Any]] = None


class Room(RoomBase):
    """房间完整模型"""
    
    room_id: UUID = Field(default_factory=generate_uuid, description="房间唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    location_id: UUID = Field(..., description="所属位置ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "room_id": "550e8400-e29b-41d4-a716-446655440011",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "is_default": True,
                "room_name": "E203",
                "is_active": True,
                "layout_config": None
            }
        }


# ============================================================================
# Bed Models (床位模型)
# ============================================================================

class BedBase(BaseModel):
    """床位基础模型"""
    
    bed_name: str = Field(..., max_length=50, description="床位名称（如 'A'、'B'、'Bed1'）")
    bed_type: str = Field(..., max_length=20, description="床位类型：ActiveBed / NonActiveBed")
    mattress_material: Optional[str] = Field(None, max_length=50, description="床垫材质/类型（可选）")
    mattress_thickness: Optional[str] = Field(None, max_length=20, description="床垫厚度（如 '< 7in'、'7-10in'）")
    resident_id: Optional[UUID] = Field(None, description="绑定的住户ID")
    
    @field_validator("bed_type")
    @classmethod
    def validate_bed_type(cls, v: str) -> str:
        allowed = ["ActiveBed", "NonActiveBed"]
        if v not in allowed:
            raise ValueError(f"bed_type must be one of {allowed}")
        return v
    
    @field_validator("mattress_thickness")
    @classmethod
    def validate_mattress_thickness(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["< 7in", "7-10in", "11-14in", "14in+"]
            if v not in allowed:
                raise ValueError(f"mattress_thickness must be one of {allowed}")
        return v


class BedCreate(BedBase):
    """创建床位请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    room_id: UUID = Field(..., description="所属房间ID")
    location_id: UUID = Field(..., description="所属位置ID（冗余，加速查询）")


class BedUpdate(BaseModel):
    """更新床位请求模型"""
    
    bed_name: Optional[str] = Field(None, max_length=50)
    bed_type: Optional[str] = Field(None, max_length=20)
    mattress_material: Optional[str] = Field(None, max_length=50)
    mattress_thickness: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[UUID] = None


class Bed(BedBase):
    """床位完整模型"""
    
    bed_id: UUID = Field(default_factory=generate_uuid, description="床位唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    room_id: UUID = Field(..., description="所属房间ID")
    location_id: UUID = Field(..., description="所属位置ID")
    
    # 自动维护字段
    bound_device_count: int = Field(default=0, description="绑定的激活监护设备数量（自动维护）")
    is_active: bool = Field(default=False, description="床位是否激活（计算字段，bound_device_count > 0）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bed_id": "550e8400-e29b-41d4-a716-446655440012",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "room_id": "550e8400-e29b-41d4-a716-446655440011",
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "bed_name": "A",
                "bed_type": "ActiveBed",
                "mattress_material": "Memory Foam",
                "mattress_thickness": "7-10in",
                "resident_id": "550e8400-e29b-41d4-a716-446655440020",
                "bound_device_count": 2,
                "is_active": True
            }
        }
