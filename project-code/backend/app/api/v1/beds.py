"""
床位管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from loguru import logger

from app.models.location import Bed, BedCreate, BedUpdate
from app.services.storage import StorageService

router = APIRouter()
bed_storage = StorageService[Bed]("beds")


@router.get("/", response_model=List[Bed], summary="获取床位列表")
async def list_beds(
    room_id: UUID = Query(None, description="房间ID"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取床位列表"""
    try:
        if room_id:
            beds = bed_storage.find_all(
                lambda bed: bed["room_id"] == str(room_id)
            )
        else:
            beds = bed_storage.find_all(lambda _: True)
        return beds[:limit]
    except Exception as e:
        logger.error(f"Error listing beds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{bed_id}", response_model=Bed, summary="获取床位详情")
async def get_bed(bed_id: UUID):
    """获取指定床位详情"""
    try:
        bed = bed_storage.find_by_id(bed_id)
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        return bed
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bed {bed_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Bed, summary="创建床位", status_code=201)
async def create_bed(bed_data: BedCreate):
    """创建新床位"""
    try:
        bed_dict = bed_data.model_dump()
        bed = bed_storage.create(bed_dict)
        return bed
    except Exception as e:
        logger.error(f"Error creating bed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{bed_id}", response_model=Bed, summary="更新床位")
async def update_bed(bed_id: UUID, bed_data: BedUpdate):
    """更新床位信息"""
    try:
        existing = bed_storage.find_by_id(bed_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        update_dict = bed_data.model_dump(exclude_unset=True)
        updated = bed_storage.update(bed_id, update_dict)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bed {bed_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{bed_id}", status_code=204, summary="删除床位")
async def delete_bed(bed_id: UUID):
    """删除床位"""
    try:
        existing = bed_storage.find_by_id(bed_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        bed_storage.delete(bed_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bed {bed_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
