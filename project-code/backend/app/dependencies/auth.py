"""
认证依赖项
用于FastAPI端点的用户认证和授权
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from uuid import UUID
import jwt

from app.services.storage import StorageService
from app.api.v1.auth import SECRET_KEY, ALGORITHM


async def get_current_user_from_token(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    从Authorization header中获取当前用户
    
    参数:
        authorization: Authorization header (Bearer token)
        
    返回:
        Dict: 用户信息
        
    异常:
        HTTPException: 401 未授权
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 提取token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证方案",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Authorization header格式",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 解码token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户信息
    user_storage = StorageService("users")
    users = user_storage.find_all(
        lambda u: str(u.get("user_id")) == str(user_id)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users[0]
    
    # 检查用户是否激活
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """
    获取当前用户（可选）
    如果未提供token或token无效，返回None
    
    参数:
        authorization: Authorization header (Bearer token)
        
    返回:
        Optional[Dict]: 用户信息或None
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user_from_token(authorization)
    except HTTPException:
        return None


def require_role(allowed_roles: list[str]):
    """
    装饰器工厂：要求特定角色
    
    参数:
        allowed_roles: 允许的角色列表
        
    返回:
        依赖函数
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user_from_token)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_admin():
    """要求Admin角色的依赖"""
    return require_role(["Admin"])
