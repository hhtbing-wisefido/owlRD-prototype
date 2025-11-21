"""
映射表管理API端点
对应 mapping_tables (16_mapping_tables.sql) 表
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.config import (
    PostureMapping, PostureMappingCreate, PostureMappingUpdate,
    EventMapping, EventMappingCreate, EventMappingUpdate
)
from app.services.storage import StorageService

router = APIRouter()
posture_storage = StorageService[PostureMapping]("posture_mappings")
event_storage = StorageService[EventMapping]("event_mappings")


# ============================================================================
# Posture Mapping Endpoints
# ============================================================================

@router.get("/postures", response_model=List[PostureMapping])
async def list_posture_mappings(
    category: Optional[str] = Query(None, description="分类过滤：Posture/MotionState/Safety"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    获取姿态映射列表
    
    **姿态值范围**：0-11
    **分类**：
    - Posture: 姿态（如站立、坐姿）
    - MotionState: 运动状态（如行走、静止）
    - Safety: 安全状态（如跌倒）
    """
    def filter_fn(pm):
        if category and pm.get("category") != category:
            return False
        if is_active is not None and pm.get("is_active") != is_active:
            return False
        return True
    
    mappings = posture_storage.find_all(filter_fn)
    return mappings[:limit]


@router.get("/postures/{raw_posture}", response_model=PostureMapping)
async def get_posture_mapping(raw_posture: int):
    """
    根据原始姿态值获取映射
    
    **参数**：
    - **raw_posture**: 原始姿态值（0-11）
    """
    if raw_posture < 0 or raw_posture > 11:
        raise HTTPException(status_code=400, detail="raw_posture must be between 0 and 11")
    
    # 在实际数据中查找
    mappings = posture_storage.find_all(lambda pm: pm.get("raw_posture") == raw_posture)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Posture mapping not found for raw_posture={raw_posture}")
    
    return mappings[0]


@router.post("/postures", response_model=PostureMapping, status_code=201)
async def create_posture_mapping(mapping_data: PostureMappingCreate):
    """
    创建姿态映射
    
    **注意**：确保raw_posture唯一
    """
    from datetime import datetime
    # 检查是否已存在
    existing = posture_storage.find_all(lambda pm: pm.get("raw_posture") == mapping_data.raw_posture)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Posture mapping already exists for raw_posture={mapping_data.raw_posture}"
        )
    
    mapping_dict = mapping_data.model_dump()
    mapping_dict["created_at"] = datetime.now().isoformat()
    mapping_dict["updated_at"] = datetime.now().isoformat()
    
    posture_storage.create(mapping_dict)
    return mapping_dict


@router.put("/postures/{raw_posture}", response_model=PostureMapping)
async def update_posture_mapping(raw_posture: int, mapping_data: PostureMappingUpdate):
    """
    更新姿态映射
    """
    from datetime import datetime
    if raw_posture < 0 or raw_posture > 11:
        raise HTTPException(status_code=400, detail="raw_posture must be between 0 and 11")
    
    # 查找现有映射
    mappings = posture_storage.find_all(lambda pm: pm.get("raw_posture") == raw_posture)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Posture mapping not found for raw_posture={raw_posture}")
    
    existing = mappings[0]
    update_data = mapping_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    # 使用raw_posture作为主键更新
    updated = posture_storage.update("raw_posture", raw_posture, update_data)
    return updated


@router.delete("/postures/{raw_posture}", status_code=204)
async def delete_posture_mapping(raw_posture: int):
    """
    删除姿态映射
    """
    if raw_posture < 0 or raw_posture > 11:
        raise HTTPException(status_code=400, detail="raw_posture must be between 0 and 11")
    
    mappings = posture_storage.find_all(lambda pm: pm.get("raw_posture") == raw_posture)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Posture mapping not found for raw_posture={raw_posture}")
    
    posture_storage.delete("raw_posture", raw_posture)
    return None


# ============================================================================
# Event Mapping Endpoints
# ============================================================================

@router.get("/events", response_model=List[EventMapping])
async def list_event_mappings(
    category: Optional[str] = Query(None, description="分类过滤：Behavioral/Safety/HealthCondition/Physiological"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    获取事件映射列表
    
    **分类**：
    - Behavioral: 行为事件（如进入房间、离床）
    - Safety: 安全事件（如跌倒、长时间无活动）
    - HealthCondition: 健康状况（如呼吸暂停）
    - Physiological: 生理指标（如心率异常）
    """
    def filter_fn(em):
        if category and em.get("category") != category:
            return False
        if is_active is not None and em.get("is_active") != is_active:
            return False
        return True
    
    mappings = event_storage.find_all(filter_fn)
    return mappings[:limit]


@router.get("/events/{event_type}", response_model=EventMapping)
async def get_event_mapping(event_type: str):
    """
    根据事件类型获取映射
    
    **参数**：
    - **event_type**: 标准事件类型（如 ENTER_ROOM, LEFT_BED）
    """
    mappings = event_storage.find_all(lambda em: em.get("event_type") == event_type)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Event mapping not found for event_type={event_type}")
    
    return mappings[0]


@router.post("/events", response_model=EventMapping, status_code=201)
async def create_event_mapping(mapping_data: EventMappingCreate):
    """
    创建事件映射
    
    **注意**：确保event_type唯一
    """
    from datetime import datetime
    # 检查是否已存在
    existing = event_storage.find_all(lambda em: em.get("event_type") == mapping_data.event_type)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Event mapping already exists for event_type={mapping_data.event_type}"
        )
    
    mapping_dict = mapping_data.model_dump()
    mapping_dict["created_at"] = datetime.now().isoformat()
    mapping_dict["updated_at"] = datetime.now().isoformat()
    
    event_storage.create(mapping_dict)
    return mapping_dict


@router.put("/events/{event_type}", response_model=EventMapping)
async def update_event_mapping(event_type: str, mapping_data: EventMappingUpdate):
    """
    更新事件映射
    """
    from datetime import datetime
    mappings = event_storage.find_all(lambda em: em.get("event_type") == event_type)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Event mapping not found for event_type={event_type}")
    
    update_data = mapping_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    updated = event_storage.update("event_type", event_type, update_data)
    return updated


@router.delete("/events/{event_type}", status_code=204)
async def delete_event_mapping(event_type: str):
    """
    删除事件映射
    """
    mappings = event_storage.find_all(lambda em: em.get("event_type") == event_type)
    if not mappings:
        raise HTTPException(status_code=404, detail=f"Event mapping not found for event_type={event_type}")
    
    event_storage.delete("event_type", event_type)
    return None
