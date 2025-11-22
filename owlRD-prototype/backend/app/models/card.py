"""
卡片数据模型
对应 cards (18_cards.sql) 表
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import Field

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# Enums (枚举类型)
# ============================================================================

class CardType(str, Enum):
    """卡片类型"""
    ACTIVE_BED = "ActiveBed"    # 床位卡片
    LOCATION = "Location"        # 门牌号卡片


class BindingType(str, Enum):
    """设备绑定类型"""
    DIRECT = "direct"      # 直接绑定
    INDIRECT = "indirect"  # 间接绑定


# ============================================================================
# Card Models (卡片模型)
# ============================================================================

class CardBase(BaseModel):
    """卡片基础模型"""
    
    card_type: CardType = Field(..., description="卡片类型：ActiveBed/Location")
    
    # 关联对象（根据card_type决定使用哪个字段）
    bed_id: Optional[UUID] = Field(None, description="关联床位ID（ActiveBed卡片必填）")
    location_id: Optional[UUID] = Field(None, description="关联位置ID（Location卡片必填）")
    
    # 卡片显示信息
    card_name: str = Field(..., max_length=255, description="卡片名称（如Smith或201）")
    card_address: str = Field(..., max_length=255, description="卡片地址（如BuildA-1F-201-Bedroom-BedA）")
    
    # 关联住户（仅ActiveBed卡片）
    resident_id: Optional[UUID] = Field(None, description="关联住户ID（仅ActiveBed卡片）")
    
    # 报警路由配置
    is_public_space: Optional[bool] = Field(
        None,
        description="是否使用警报通报组路由：TRUE=警报通报组，FALSE=住户护士，NULL=自动判断"
    )
    routing_alert_user_ids: Optional[List[UUID]] = Field(None, description="警报接收者用户ID列表")
    routing_alert_tags: Optional[List[str]] = Field(None, description="警报接收者标签组")
    
    # 状态
    is_active: bool = Field(default=True, description="是否启用")


class CardCreate(CardBase):
    """创建卡片请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class CardUpdate(BaseModel):
    """更新卡片请求模型"""
    
    card_name: Optional[str] = Field(None, max_length=255)
    card_address: Optional[str] = Field(None, max_length=255)
    resident_id: Optional[UUID] = None
    is_public_space: Optional[bool] = None
    routing_alert_user_ids: Optional[List[UUID]] = None
    routing_alert_tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Card(CardBase):
    """卡片完整模型"""
    
    card_id: UUID = Field(default_factory=generate_uuid, description="卡片唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "550e8400-e29b-41d4-a716-446655440050",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "card_type": "ActiveBed",
                "bed_id": "550e8400-e29b-41d4-a716-446655440012",
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "card_name": "锅匠",
                "card_address": "BuildA-2F-E203-Bedroom-BedA",
                "resident_id": "550e8400-e29b-41d4-a716-446655440020",
                "is_public_space": False,
                "routing_alert_user_ids": None,
                "routing_alert_tags": None,
                "is_active": True
            }
        }


# ============================================================================
# CardDevice Models (卡片-设备关联)
# ============================================================================

class CardDeviceBase(BaseModel):
    """卡片-设备关联基础模型"""
    
    binding_type: BindingType = Field(default=BindingType.DIRECT, description="绑定类型：direct/indirect")


class CardDeviceCreate(CardDeviceBase):
    """创建卡片-设备关联请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    card_id: UUID = Field(..., description="卡片ID")
    device_id: UUID = Field(..., description="设备ID")


class CardDevice(CardDeviceBase):
    """卡片-设备关联完整模型"""
    
    card_device_id: UUID = Field(default_factory=generate_uuid, description="关联唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    card_id: UUID = Field(..., description="卡片ID")
    device_id: UUID = Field(..., description="设备ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_device_id": "550e8400-e29b-41d4-a716-446655440051",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "card_id": "550e8400-e29b-41d4-a716-446655440050",
                "device_id": "550e8400-e29b-41d4-a716-446655440030",
                "binding_type": "direct"
            }
        }
