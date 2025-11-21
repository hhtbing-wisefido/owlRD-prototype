"""
认证API端点
提供用户认证、注册和token管理
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import jwt
import bcrypt
from uuid import UUID

from app.services.storage import StorageService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 存储服务
user_storage = StorageService[User]("users")


# ============================================================================
# Pydantic模型
# ============================================================================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., min_length=6, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    phone: Optional[str] = Field(None, description="手机号")
    role: str = Field(default="Nurse", description="角色")
    tenant_id: UUID = Field(..., description="租户ID")


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


# ============================================================================
# 辅助函数
# ============================================================================

def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    # 从存储中获取用户
    user = user_storage.find_by_id("user_id", user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


# ============================================================================
# API端点
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    用户登录
    
    **功能**：
    - 验证用户名/邮箱和密码
    - 生成JWT access token
    - 返回用户信息
    
    **注意**：
    - username可以是用户名或邮箱
    - 密码使用bcrypt加密存储
    """
    # 查找用户（支持用户名或邮箱登录）
    users = user_storage.find_all(
        lambda u: u.get("username") == login_data.username or 
                  u.get("email") == login_data.username
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    user = users[0]
    
    # 验证密码
    if not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户状态
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建token
    access_token = create_access_token(
        data={
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "tenant_id": user.get("tenant_id"),
            "role": user.get("role")
        }
    )
    
    # 返回响应
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "role": user.get("role"),
            "tenant_id": user.get("tenant_id")
        }
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest):
    """
    用户注册
    
    **功能**：
    - 创建新用户账号
    - 自动生成JWT token
    - 返回用户信息
    
    **验证**：
    - 用户名唯一性
    - 邮箱唯一性
    - 密码强度（最少6位）
    """
    # 检查用户名是否已存在
    existing_username = user_storage.find_all(
        lambda u: u.get("username") == register_data.username
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = user_storage.find_all(
        lambda u: u.get("email") == register_data.email
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    from app.models.base import generate_uuid
    user_id = str(generate_uuid())
    
    new_user = {
        "user_id": user_id,
        "tenant_id": str(register_data.tenant_id),
        "username": register_data.username,
        "email": register_data.email,
        "phone": register_data.phone,
        "role": register_data.role,
        "password_hash": hash_password(register_data.password),
        "is_active": True,
        "alert_levels": ["L1", "L2"],
        "alert_channels": ["WEB", "APP"],
        "alert_scope": "ASSIGNED_ONLY",
        "tags": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    user_storage.create(new_user)
    
    # 创建token
    access_token = create_access_token(
        data={
            "user_id": user_id,
            "username": register_data.username,
            "tenant_id": str(register_data.tenant_id),
            "role": register_data.role
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "user_id": user_id,
            "username": register_data.username,
            "email": register_data.email,
            "phone": register_data.phone,
            "role": register_data.role,
            "tenant_id": str(register_data.tenant_id)
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    **需要认证**：Bearer Token
    """
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "role": current_user.get("role"),
        "tenant_id": current_user.get("tenant_id"),
        "alert_levels": current_user.get("alert_levels", []),
        "alert_channels": current_user.get("alert_channels", []),
        "alert_scope": current_user.get("alert_scope"),
        "tags": current_user.get("tags", [])
    }


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    修改密码
    
    **需要认证**：Bearer Token
    
    **步骤**：
    1. 验证旧密码
    2. 更新为新密码
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    user_storage.update(
        "user_id",
        current_user.get("user_id"),
        {
            "password_hash": hash_password(password_data.new_password),
            "updated_at": datetime.now().isoformat()
        }
    )
    
    return {"message": "密码修改成功"}


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    刷新token
    
    **需要认证**：Bearer Token
    
    **功能**：生成新的access token，延长有效期
    """
    # 创建新token
    access_token = create_access_token(
        data={
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "tenant_id": current_user.get("tenant_id"),
            "role": current_user.get("role")
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "email": current_user.get("email"),
            "role": current_user.get("role"),
            "tenant_id": current_user.get("tenant_id")
        }
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    登出
    
    **需要认证**：Bearer Token
    
    **注意**：由于使用JWT，实际的token失效需要客户端删除token
    """
    return {"message": "登出成功"}
