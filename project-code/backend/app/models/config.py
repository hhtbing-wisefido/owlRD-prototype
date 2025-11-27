"""
配置和映射表数据模型
对应 config_versions (15_config_versions.sql), mapping_tables (16_mapping_tables.sql) 表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# ConfigVersion Models (统一配置历史)
# ============================================================================

class ConfigVersionBase(BaseModel):
    """配置版本基础模型"""
    
    config_type: str = Field(
        ...,
        max_length=50,
        description="配置类型：room_layout/device_config/cloud_alert_policy/iot_monitor_alert/device_installation"
    )
    entity_id: UUID = Field(..., description="实体ID（根据config_type指向不同表的ID）")
    current_entity_id: Optional[UUID] = Field(None, description="当前实体ID（可为NULL，表示实体已删除）")
    config_data: Dict[str, Any] = Field(..., description="配置数据快照（JSONB）")
    valid_from: datetime = Field(..., description="配置开始生效时间")
    valid_to: Optional[datetime] = Field(None, description="配置失效时间（NULL表示当前仍生效）")
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("config_type")
    @classmethod
    def validate_config_type(cls, v: str) -> str:
        allowed = [
            "room_layout",
            "device_config",
            "cloud_alert_policy",
            "iot_monitor_alert",
            "device_installation"
        ]
        if v not in allowed:
            raise ValueError(f"config_type must be one of {allowed}")
        return v


class ConfigVersionCreate(ConfigVersionBase):
    """创建配置版本请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class ConfigVersionUpdate(BaseModel):
    """更新配置版本请求模型"""
    
    config_data: Optional[Dict[str, Any]] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class ConfigVersion(ConfigVersionBase):
    """配置版本完整模型"""
    
    version_id: UUID = Field(default_factory=generate_uuid, description="版本唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_by: Optional[str] = Field(None, description="创建人ID或用户名")
    metadata: Optional[Dict[str, Any]] = Field(None, description="扩展信息")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version_id": "550e8400-e29b-41d4-a716-446655440060",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "config_type": "room_layout",
                "entity_id": "550e8400-e29b-41d4-a716-446655440011",
                "current_entity_id": "550e8400-e29b-41d4-a716-446655440011",
                "config_data": {
                    "layout": {},
                    "params": {"width": 1000, "height": 800},
                    "objects": []
                },
                "valid_from": "2025-01-01T00:00:00Z",
                "valid_to": None,
                "is_active": True
            }
        }


# ============================================================================
# PostureMapping Models (姿态映射表)
# ============================================================================

class PostureMappingBase(BaseModel):
    """姿态映射基础模型"""
    
    raw_posture: int = Field(..., ge=0, le=11, description="原始姿态值（0-11）")
    snomed_code: Optional[str] = Field(None, max_length=50, description="SNOMED CT编码")
    snomed_display: str = Field(..., max_length=100, description="SNOMED显示名称")
    category: str = Field(..., max_length=50, description="分类：Posture/MotionState/Safety")
    loinc_code: Optional[str] = Field(None, max_length=50, description="LOINC编码（用于FHIR）")
    description: Optional[str] = Field(None, description="描述")
    firmware_version: Optional[str] = Field(None, max_length=50, description="需要的固件版本")
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["Posture", "MotionState", "Safety"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class PostureMappingCreate(PostureMappingBase):
    """创建姿态映射请求模型"""
    pass


class PostureMappingUpdate(BaseModel):
    """更新姿态映射请求模型"""
    
    snomed_code: Optional[str] = Field(None, max_length=50)
    snomed_display: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    loinc_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    firmware_version: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class PostureMapping(PostureMappingBase):
    """姿态映射完整模型"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_posture": 4,
                "snomed_code": "383370001",
                "snomed_display": "Standing position",
                "category": "Posture",
                "loinc_code": "56903-8",
                "description": "站立",
                "firmware_version": None,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }


# ============================================================================
# EventMapping Models (事件映射表)
# ============================================================================

class EventMappingBase(BaseModel):
    """事件映射基础模型"""
    
    event_type: str = Field(..., max_length=50, description="标准事件类型（如ENTER_ROOM, LEFT_BED）")
    event_display: str = Field(..., max_length=100, description="事件显示名称（中文）")
    category: str = Field(..., max_length=50, description="分类：Behavioral/Safety/HealthCondition/Physiological")
    snomed_code: Optional[str] = Field(None, max_length=50, description="SNOMED CT编码")
    snomed_display: Optional[str] = Field(None, max_length=100, description="SNOMED显示名称")
    description: Optional[str] = Field(None, description="描述")
    duration_threshold_minutes: Optional[int] = Field(None, description="持续时间阈值（分钟）")
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["Behavioral", "Safety", "HealthCondition", "Physiological"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class EventMappingCreate(EventMappingBase):
    """创建事件映射请求模型"""
    pass


class EventMappingUpdate(BaseModel):
    """更新事件映射请求模型"""
    
    event_display: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    snomed_code: Optional[str] = Field(None, max_length=50)
    snomed_display: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    duration_threshold_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class EventMapping(EventMappingBase):
    """事件映射完整模型"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "LEFT_BED",
                "event_display": "离床",
                "category": "Behavioral",
                "snomed_code": "248570008",
                "snomed_display": "Not in bed",
                "description": "离开床位（从卧床状态转为非卧床状态）",
                "duration_threshold_minutes": None,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
