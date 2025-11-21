"""
标准编码映射数据模型
对应 posture_mapping, event_mapping (16_mapping_tables.sql) 表
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# PostureMapping Models (姿态映射模型)
# ============================================================================

class PostureMappingBase(BaseModel):
    """姿态映射基础模型"""
    
    # 分类
    category: str = Field(..., max_length=50, description="分类：Posture/MotionState/SleepState")
    
    # 厂家代码
    vendor_code: str = Field(..., max_length=50, description="厂家原始代码")
    firmware_version: str = Field(..., max_length=50, description="固件版本（如 '1.4.0'）")
    
    # SNOMED CT编码
    snomed_code: Optional[str] = Field(None, max_length=50, description="SNOMED CT编码（如 '102538003'）")
    snomed_display: Optional[str] = Field(None, max_length=100, description="SNOMED CT显示名称")
    
    # LOINC编码
    loinc_code: Optional[str] = Field(None, max_length=50, description="LOINC编码（可选）")
    
    # 描述
    description: Optional[str] = Field(None, description="映射说明")
    
    # 是否启用
    is_active: bool = Field(default=True, description="是否启用该映射")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["Posture", "MotionState", "SleepState"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class PostureMappingCreate(PostureMappingBase):
    """创建姿态映射请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class PostureMappingUpdate(BaseModel):
    """更新姿态映射请求模型"""
    
    snomed_code: Optional[str] = Field(None, max_length=50)
    snomed_display: Optional[str] = Field(None, max_length=100)
    loinc_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PostureMapping(PostureMappingBase):
    """姿态映射完整模型"""
    
    mapping_id: UUID = Field(default_factory=generate_uuid, description="映射唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mapping_id": "550e8400-e29b-41d4-a716-446655440040",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "category": "Posture",
                "vendor_code": "Standing",
                "firmware_version": "1.4.0",
                "snomed_code": "10904000",
                "snomed_display": "Orthostatic body position",
                "loinc_code": None,
                "description": "站立姿态",
                "is_active": True,
                "created_at": "2025-11-20T14:00:00Z",
                "updated_at": "2025-11-20T14:00:00Z"
            }
        }


# ============================================================================
# EventMapping Models (事件映射模型)
# ============================================================================

class EventMappingBase(BaseModel):
    """事件映射基础模型"""
    
    # 分类
    category: str = Field(..., max_length=50, description="分类：RoomEvent/BedEvent/SafetyEvent")
    
    # 厂家代码
    vendor_code: str = Field(..., max_length=50, description="厂家原始代码")
    firmware_version: str = Field(..., max_length=50, description="固件版本（如 '1.4.0'）")
    
    # SNOMED CT编码
    snomed_code: Optional[str] = Field(None, max_length=50, description="SNOMED CT编码")
    snomed_display: Optional[str] = Field(None, max_length=100, description="SNOMED CT显示名称")
    
    # LOINC编码
    loinc_code: Optional[str] = Field(None, max_length=50, description="LOINC编码（可选）")
    
    # 描述
    description: Optional[str] = Field(None, description="映射说明")
    
    # 是否启用
    is_active: bool = Field(default=True, description="是否启用该映射")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["RoomEvent", "BedEvent", "SafetyEvent"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class EventMappingCreate(EventMappingBase):
    """创建事件映射请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class EventMappingUpdate(BaseModel):
    """更新事件映射请求模型"""
    
    snomed_code: Optional[str] = Field(None, max_length=50)
    snomed_display: Optional[str] = Field(None, max_length=100)
    loinc_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EventMapping(EventMappingBase):
    """事件映射完整模型"""
    
    mapping_id: UUID = Field(default_factory=generate_uuid, description="映射唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mapping_id": "550e8400-e29b-41d4-a716-446655440041",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "category": "BedEvent",
                "vendor_code": "LeftBed",
                "firmware_version": "1.4.0",
                "snomed_code": "281100009",
                "snomed_display": "Left bed",
                "loinc_code": None,
                "description": "离床事件",
                "is_active": True,
                "created_at": "2025-11-20T14:00:00Z",
                "updated_at": "2025-11-20T14:00:00Z"
            }
        }
