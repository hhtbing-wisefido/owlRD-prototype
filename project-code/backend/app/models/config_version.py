"""
配置版本历史数据模型
对应 config_versions (15_config_versions.sql) 表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


class ConfigVersionBase(BaseModel):
    """配置版本基础模型"""
    
    # 配置类型
    config_type: str = Field(..., max_length=50, description="配置类型：room_layout/device_config/cloud_alert_policy/iot_monitor_alert/device_installation")
    
    # 实体关联
    entity_id: UUID = Field(..., description="关联的实体ID")
    current_entity_id: Optional[UUID] = Field(None, description="当前实体ID（可能已删除）")
    
    # 配置数据快照
    config_data: Dict[str, Any] = Field(..., description="配置内容快照（JSONB）")
    
    # 版本生效时间区间
    valid_from: datetime = Field(..., description="配置开始生效时间")
    valid_to: Optional[datetime] = Field(None, description="配置失效时间（NULL表示当前仍生效）")
    
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("config_type")
    @classmethod
    def validate_config_type(cls, v: str) -> str:
        """验证配置类型"""
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
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version_id": "550e8400-e29b-41d4-a716-446655440030",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "config_type": "room_layout",
                "entity_id": "550e8400-e29b-41d4-a716-446655440011",
                "current_entity_id": "550e8400-e29b-41d4-a716-446655440011",
                "config_data": {
                    "layout": {
                        "width": 800,
                        "height": 600,
                        "objects": [
                            {"type": "bed", "x": 100, "y": 100, "width": 200, "height": 100}
                        ]
                    },
                    "params": {
                        "radar_position": {"x": 400, "y": 50}
                    }
                },
                "valid_from": "2025-01-01T00:00:00Z",
                "valid_to": None,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
