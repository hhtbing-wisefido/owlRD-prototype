"""
角色数据模型
对应 roles (02_roles.sql) 表
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# Role Models (角色模型)
# ============================================================================

class RoleBase(BaseModel):
    """角色基础模型"""
    
    # 角色编码（如 Director, NurseManager, Nurse）
    role_code: str = Field(..., max_length=50, description="角色编码（程序引用，如Director）")
    
    # 角色展示名称
    display_name: str = Field(..., max_length=100, description="角色展示名称（可多语言）")
    
    # 描述
    description: Optional[str] = Field(None, description="角色职责说明")
    
    # 是否系统预置
    is_system: bool = Field(default=False, description="是否系统预置角色（不可删除）")
    
    # 是否启用
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("role_code")
    @classmethod
    def validate_role_code(cls, v: str) -> str:
        # 角色编码必须是字母数字下划线
        if not v.replace('_', '').isalnum():
            raise ValueError("role_code must contain only letters, numbers, and underscores")
        return v


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Role(RoleBase):
    """角色完整模型"""
    
    role_id: UUID = Field(default_factory=generate_uuid, description="角色唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "550e8400-e29b-41d4-a716-446655440030",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "role_code": "Director",
                "display_name": "主任/院长",
                "description": "机构主任或院长，拥有最高权限",
                "is_system": True,
                "is_active": True,
                "created_at": "2025-11-20T14:00:00Z",
                "updated_at": "2025-11-20T14:00:00Z"
            }
        }
