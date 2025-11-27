"""
租户数据模型
对应 tenants 表 (01_tenants.sql)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


class TenantBase(BaseModel):
    """租户基础模型"""
    
    tenant_name: str = Field(..., max_length=255, description="租户名称")
    domain: Optional[str] = Field(None, max_length=255, description="租户域名（唯一）")
    status: str = Field(default="active", max_length=50, description="状态: active, suspended, deleted")
    metadata: Optional[Dict[str, Any]] = Field(None, description="扩展配置信息（JSONB）")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["active", "suspended", "deleted"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class TenantCreate(TenantBase):
    """创建租户请求模型"""
    pass


class TenantUpdate(BaseModel):
    """更新租户请求模型"""
    
    tenant_name: Optional[str] = Field(None, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["active", "suspended", "deleted"]
            if v not in allowed:
                raise ValueError(f"status must be one of {allowed}")
        return v


class Tenant(TenantBase):
    """租户完整模型（含系统字段）"""
    
    tenant_id: UUID = Field(default_factory=generate_uuid, description="租户唯一标识")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_name": "Sunrise Senior Living",
                "domain": "sunrise.owlrd.com",
                "status": "active",
                "metadata": {
                    "address": "123 Main St",
                    "contact_email": "admin@sunrise.com",
                    "timezone": "America/New_York"
                },
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
