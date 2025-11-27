"""
房间管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
from loguru import logger

from app.models.location import Room, RoomCreate, RoomUpdate
from app.services.storage import StorageService

router = APIRouter()
room_storage = StorageService[Room]("rooms")


@router.get("/", response_model=List[Room], summary="获取房间列表")
async def list_rooms(
    location_id: UUID = Query(None, description="位置ID"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取房间列表"""
    try:
        if location_id:
            rooms = room_storage.find_all(
                lambda room: room["location_id"] == str(location_id)
            )
        else:
            rooms = room_storage.find_all(lambda _: True)
        return rooms[:limit]
    except Exception as e:
        logger.error(f"Error listing rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}", response_model=Room, summary="获取房间详情")
async def get_room(room_id: UUID):
    """获取指定房间详情"""
    try:
        room = room_storage.find_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Room, summary="创建房间", status_code=201)
async def create_room(room_data: RoomCreate):
    """创建新房间"""
    try:
        room_dict = room_data.model_dump()
        room = room_storage.create(room_dict)
        return room
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{room_id}", response_model=Room, summary="更新房间")
async def update_room(room_id: UUID, room_data: RoomUpdate):
    """更新房间信息"""
    try:
        existing = room_storage.find_by_id(room_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Room not found")
        
        update_dict = room_data.model_dump(exclude_unset=True)
        updated = room_storage.update(room_id, update_dict)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{room_id}", status_code=204, summary="删除房间")
async def delete_room(room_id: UUID):
    """删除房间"""
    try:
        existing = room_storage.find_by_id(room_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Room not found")
        
        room_storage.delete(room_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room {room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
