"""
用户和角色数据模型
对应 roles 表 (02_roles.sql) 和 users 表 (03_users.sql)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field, EmailStr, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# Role Models (角色模型)
# ============================================================================

class RoleBase(BaseModel):
    """角色基础模型"""
    
    role_code: str = Field(..., max_length=50, description="角色编码（如 Director, NurseManager, Nurse）")
    display_name: str = Field(..., max_length=100, description="角色展示名称（多语言）")
    description: Optional[str] = Field(None, description="角色职责说明")
    is_system: bool = Field(default=False, description="是否系统预置角色（不可删除）")
    is_active: bool = Field(default=True, description="是否启用")


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "550e8400-e29b-41d4-a716-446655440001",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "role_code": "NurseManager",
                "display_name": "Nurse Manager",
                "description": "Manages nursing team and oversees care quality",
                "is_system": True,
                "is_active": True
            }
        }


# ============================================================================
# User Models (用户模型)
# ============================================================================

class UserBase(BaseModel):
    """用户基础模型"""
    
    username: Optional[str] = Field(None, max_length=255, description="内部账号（显示名）")
    email: Optional[EmailStr] = Field(None, description="邮箱（明文，用于工作联系）")
    phone: Optional[str] = Field(None, max_length=50, description="手机号（明文，用于工作联系）")
    role: str = Field(..., max_length=50, description="角色编码（对应roles.role_code）")
    status: str = Field(default="active", max_length=50, description="账号状态: active, disabled, left")
    alert_levels: Optional[List[str]] = Field(None, description="接收的告警级别 ['L1', 'L2', 'L3']")
    alert_channels: Optional[List[str]] = Field(None, description="接收的通道 ['APP', 'EMAIL']")
    alert_scope: Optional[str] = Field(None, max_length=20, description="接收范围: ALL, LOCATION-TAG, ASSIGNED_ONLY")
    tags: Optional[Dict[str, Any]] = Field(None, description="员工标签（如班次、分组）")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["active", "disabled", "left"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v
    
    @field_validator("alert_scope")
    @classmethod
    def validate_alert_scope(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["ALL", "LOCATION-TAG", "ASSIGNED_ONLY"]
            if v not in allowed:
                raise ValueError(f"alert_scope must be one of {allowed}")
        return v


class UserCreate(UserBase):
    """创建用户请求模型"""
    
    tenant_id: UUID = Field(..., description="所属租户ID")
    password: Optional[str] = Field(None, min_length=8, description="密码（明文，将被哈希）")
    pin: Optional[str] = Field(None, min_length=4, max_length=6, description="PIN码（明文，将被哈希）")


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    
    username: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    alert_levels: Optional[List[str]] = None
    alert_channels: Optional[List[str]] = None
    alert_scope: Optional[str] = Field(None, max_length=20)
    tags: Optional[Dict[str, Any]] = None
    password: Optional[str] = Field(None, min_length=8, description="新密码（将被哈希）")
    pin: Optional[str] = Field(None, min_length=4, max_length=6, description="新PIN码（将被哈希）")


class User(UserBase):
    """用户完整模型（不含敏感字段）"""
    
    user_id: UUID = Field(default_factory=generate_uuid, description="用户唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    
    # 哈希字段（仅用于内部验证，不对外暴露原始值）
    email_hash: Optional[bytes] = Field(None, description="邮箱哈希（用于登录匹配）", exclude=True)
    phone_hash: Optional[bytes] = Field(None, description="手机号哈希（用于登录匹配）", exclude=True)
    password_hash: Optional[bytes] = Field(None, description="密码哈希（bcrypt）", exclude=True)
    pin_hash: Optional[bytes] = Field(None, description="PIN码哈希", exclude=True)
    
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440002",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "jane.smith",
                "email": "jane.smith@sunrise.com",
                "phone": "+1-555-1234",
                "role": "NurseManager",
                "status": "active",
                "alert_levels": ["L1", "L2", "L3"],
                "alert_channels": ["APP", "EMAIL"],
                "alert_scope": "ALL",
                "tags": {
                    "shift": "DayShift",
                    "group": "TeamA",
                    "expertise": ["Falls", "Dementia"]
                },
                "last_login_at": "2025-11-20T08:30:00Z"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求模型"""
    
    # 支持多种登录方式
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    
    # 认证方式（二选一）
    password: Optional[str] = Field(None, description="密码")
    pin: Optional[str] = Field(None, description="PIN码")
    
    # 可选：租户ID（如果用户在多个租户下有账号）
    tenant_id: Optional[UUID] = Field(None, description="指定租户ID")
    
    @field_validator("username", "email", "phone")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        """至少需要一种标识符"""
        values = info.data
        if not any([v, values.get("username"), values.get("email"), values.get("phone")]):
            raise ValueError("Must provide at least one of: username, email, or phone")
        return v


class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    
    access_token: str = Field(..., description="访问令牌（JWT）")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: User = Field(..., description="用户信息")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
