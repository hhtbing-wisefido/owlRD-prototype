"""
住户管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from loguru import logger

from app.models.resident import Resident, ResidentCreate, ResidentUpdate
from app.services.storage import StorageService

router = APIRouter()
resident_storage = StorageService[Resident]("residents")


@router.get("/", response_model=List[Resident], summary="获取住户列表")
async def list_residents(
    tenant_id: UUID = Query(..., description="租户ID"),
    location_id: Optional[UUID] = Query(None, description="位置ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    获取住户列表
    
    ## 筛选条件
    - **tenant_id**: 租户ID（必填）
    - **location_id**: 按位置筛选（可选）
    - **status**: 按状态筛选（active/discharged/transferred）
    - **limit**: 返回数量限制
    """
    try:
        def filter_func(r):
            if str(r.get("tenant_id")) != str(tenant_id):
                return False
            if location_id and str(r.get("location_id")) != str(location_id):
                return False
            if status and r.get("status") != status:
                return False
            return True
        
        residents = await resident_storage.find_all(filter_func)
        return residents[:limit]
    except Exception as e:
        logger.error(f"Error listing residents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resident_id}", response_model=Resident, summary="获取住户详情")
async def get_resident(resident_id: UUID):
    """获取单个住户详情"""
    try:
        resident = await resident_storage.get(resident_id)
        if not resident:
            raise HTTPException(status_code=404, detail="Resident not found")
        return resident
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Resident, status_code=201, summary="创建住户")
async def create_resident(resident: ResidentCreate):
    """
    创建新住户
    
    ## 注意事项
    - PHI数据会自动加密
    - 自动生成匿名代称
    - 验证必填字段
    """
    try:
        result = await resident_storage.create(resident)
        logger.info(f"Created resident: {result.get('resident_id')}")
        return result
    except Exception as e:
        logger.error(f"Error creating resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{resident_id}", response_model=Resident, summary="更新住户")
async def update_resident(resident_id: UUID, resident: ResidentUpdate):
    """
    更新住户信息
    
    ## 可更新字段
    - 基础信息（姓名、状态等）
    - 位置和床位
    - 联系人信息
    - 护理人员
    """
    try:
        result = await resident_storage.update(
            resident_id, 
            resident.model_dump(exclude_unset=True)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Resident not found")
        logger.info(f"Updated resident: {resident_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{resident_id}", summary="删除住户")
async def delete_resident(resident_id: UUID):
    """
    删除住户
    
    ## 注意
    - 这是软删除，可以恢复
    - 相关数据不会被删除
    """
    try:
        success = await resident_storage.delete(resident_id)
        if not success:
            raise HTTPException(status_code=404, detail="Resident not found")
        logger.info(f"Deleted resident: {resident_id}")
        return {"status": "success", "resident_id": str(resident_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))
