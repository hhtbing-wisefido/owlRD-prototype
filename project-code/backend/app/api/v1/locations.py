"""
位置管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any
from uuid import UUID
import uuid
from loguru import logger

from app.models.location import Location, LocationCreate, LocationUpdate
from app.services.storage import StorageService
from app.dependencies.auth import get_current_user_from_token, require_role
from app.middleware.permissions import check_tenant_access

router = APIRouter()
location_storage = StorageService[Location]("locations")


@router.get("/", response_model=List[Location], summary="获取位置列表")
async def list_locations(
    tenant_id: UUID = Query(..., description="租户ID"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """获取位置列表（需要认证）"""
    try:
        check_tenant_access(current_user, tenant_id)
        
        locations = location_storage.find_all(
            lambda loc: loc["tenant_id"] == str(tenant_id)
        )
        return locations[:limit]
    except Exception as e:
        logger.error(f"Error listing locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=Location, summary="获取位置详情")
async def get_location(
    location_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """获取指定位置详情（需要认证）"""
    try:
        location = location_storage.find_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        check_tenant_access(current_user, location.get("tenant_id"))
        
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Location, summary="创建位置", status_code=201)
async def create_location(
    location_data: LocationCreate,
    current_user: Dict[str, Any] = Depends(require_role(["Admin", "Director"]))
):
    """创建新位置（需要Admin/Director权限）"""
    try:
        check_tenant_access(current_user, location_data.tenant_id)
        
        location_dict = location_data.model_dump()
        location_dict["location_id"] = str(uuid.uuid4())
        location = location_storage.create(location_dict)
        logger.info(f"User {current_user.get('username')} created location {location.get('location_id')}")
        return location
    except Exception as e:
        logger.error(f"Error creating location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{location_id}", response_model=Location, summary="更新位置")
async def update_location(
    location_id: UUID, 
    location_data: LocationUpdate,
    current_user: Dict[str, Any] = Depends(require_role(["Admin", "Director"]))
):
    """更新位置信息（需要Admin/Director权限）"""
    try:
        existing = location_storage.find_by_id("location_id", location_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Location not found")
        
        check_tenant_access(current_user, existing.get("tenant_id"))
        
        update_dict = location_data.model_dump(exclude_unset=True)
        updated = location_storage.update("location_id", location_id, update_dict)
        logger.info(f"User {current_user.get('username')} updated location {location_id}")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}", status_code=204, summary="删除位置")
async def delete_location(
    location_id: UUID,
    current_user: Dict[str, Any] = Depends(require_role(["Admin"]))
):
    """删除位置"""
    try:
        existing = location_storage.find_by_id("location_id", location_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location_storage.delete("location_id", location_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting location {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
