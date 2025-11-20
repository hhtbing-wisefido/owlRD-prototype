"""
用户管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from loguru import logger

from app.models.user import User, UserCreate, UserUpdate
from app.services.storage import StorageService

router = APIRouter()
user_storage = StorageService[User]("users")


@router.get("/", response_model=List[User])
async def list_users(
    tenant_id: UUID = Query(..., description="租户ID"),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取用户列表"""
    try:
        users = await user_storage.find_all(
            lambda u: str(u.get("tenant_id")) == str(tenant_id)
        )
        return users[:limit]
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID):
    """获取用户详情"""
    try:
        user = await user_storage.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """创建用户"""
    try:
        result = await user_storage.create(user)
        return result
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: UUID, user: UserUpdate):
    """更新用户"""
    try:
        result = await user_storage.update(user_id, user.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: UUID):
    """删除用户"""
    try:
        success = await user_storage.delete(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "user_id": str(user_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
