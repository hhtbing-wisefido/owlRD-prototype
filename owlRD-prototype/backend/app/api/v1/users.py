"""
用户管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any
from uuid import UUID
import uuid
from loguru import logger

from app.models.user import User, UserCreate, UserUpdate
from app.services.storage import StorageService
from app.dependencies.auth import get_current_user_from_token, require_role

router = APIRouter()
user_storage = StorageService[User]("users")


@router.get("/", response_model=List[User])
async def list_users(
    tenant_id: UUID = Query(..., description="租户ID"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """获取用户列表（需要管理员或Director权限）"""
    try:
        # 权限检查
        if str(current_user.get("tenant_id")) != str(tenant_id):
            raise HTTPException(status_code=403, detail="无权访问其他租户的数据")
        
        user_role = current_user.get("role")
        if user_role not in ["Admin", "Director"]:
            raise HTTPException(status_code=403, detail="需要Admin或Director权限")
        
        users = user_storage.find_all(
            lambda u: str(u.get("tenant_id")) == str(tenant_id)
        )
        return users[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """获取用户详情（可查看自己或同租户的用户）"""
    try:
        user = user_storage.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 权限检查：只能查看自己或同租户的用户
        if str(current_user.get("user_id")) != str(user_id):
            if str(current_user.get("tenant_id")) != str(user.get("tenant_id")):
                raise HTTPException(status_code=403, detail="无权访问其他租户的用户")
            if current_user.get("role") not in ["Admin", "Director"]:
                raise HTTPException(status_code=403, detail="需要Admin或Director权限")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=User, status_code=201)
async def create_user(
    user: UserCreate,
    current_user: Dict[str, Any] = Depends(require_role(["Admin", "Director"]))
):
    """创建用户（需要Admin或Director权限）"""
    try:
        # 验证租户权限
        if str(current_user.get("tenant_id")) != str(user.tenant_id):
            raise HTTPException(status_code=403, detail="只能在自己的租户下创建用户")
        
        user_data = user.model_dump()
        user_data["user_id"] = str(uuid.uuid4())
        result = user_storage.create(user_data)
        logger.info(f"User {current_user.get('username')} created user {result.get('user_id')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID, 
    user: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """更新用户（可更新自己或同租户的用户）"""
    try:
        existing_user = user_storage.get(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 权限检查
        if str(current_user.get("user_id")) != str(user_id):
            # 不是更新自己，需要管理员权限
            if str(current_user.get("tenant_id")) != str(existing_user.get("tenant_id")):
                raise HTTPException(status_code=403, detail="无权更新其他租户的用户")
            if current_user.get("role") not in ["Admin", "Director"]:
                raise HTTPException(status_code=403, detail="需要Admin或Director权限")
        
        result = user_storage.update("user_id", user_id, user.model_dump(exclude_unset=True))
        logger.info(f"User {current_user.get('username')} updated user {user_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(require_role(["Admin"]))
):
    """删除用户（仅Admin权限）"""
    try:
        existing_user = user_storage.get(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 验证租户权限
        if str(current_user.get("tenant_id")) != str(existing_user.get("tenant_id")):
            raise HTTPException(status_code=403, detail="无权删除其他租户的用户")
        
        success = user_storage.delete("user_id", user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "user_id": str(user_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
