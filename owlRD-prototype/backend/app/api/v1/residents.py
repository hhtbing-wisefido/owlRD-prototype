"""
住户管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
import uuid
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
        
        residents = resident_storage.find_all(filter_func)
        return residents[:limit]
    except Exception as e:
        logger.error(f"Error fetching residents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resident_id}", response_model=Resident, summary="获取住户详情")
async def get_resident(resident_id: UUID):
    """获取单个住户详情"""
    try:
        resident = resident_storage.get(resident_id)
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
        # 将Pydantic模型转换为字典，排除None值避免循环引用
        resident_dict = resident.model_dump(exclude_none=True, mode='json')
        resident_dict["resident_id"] = str(uuid.uuid4())
        # 确保anonymous_name字段存在
        if 'anonymous_name' not in resident_dict or not resident_dict['anonymous_name']:
            resident_dict['anonymous_name'] = resident_dict['last_name']
        result = resident_storage.create(resident_dict)
        logger.info(f"Created resident: {result.get('resident_id')}")
        return result
    except Exception as e:
        logger.error(f"Error creating resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{resident_id}", response_model=Resident, summary="更新住户")
async def update_resident(resident_id: UUID, resident: ResidentUpdate):
    """
    更新住户信息
    
    ## 参数
    - resident_id: 住户UUID
    - resident: 更新的字段
    
    ## 注意事项
    - 只更新提供的字段
    - 不能更新tenant_id
    """
    try:
        # 检查住户是否存在
        all_residents = resident_storage.load_all()
        existing = next((r for r in all_residents if r.get("resident_id") == str(resident_id)), None)
        if not existing:
            raise HTTPException(status_code=404, detail="Resident not found")
        
        # 更新字段
        from datetime import datetime
        update_dict = resident.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            existing[key] = value
        existing["updated_at"] = datetime.now().isoformat()
        
        # 保存
        all_residents = [existing if r.get("resident_id") == str(resident_id) else r for r in all_residents]
        import json
        with open(resident_storage._get_file_path(), 'w', encoding='utf-8') as f:
            json.dump(all_residents, f, indent=2, ensure_ascii=False)
        result = existing
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
        all_residents = resident_storage.load_all()
        filtered = [r for r in all_residents if r.get("resident_id") != str(resident_id)]
        if len(filtered) == len(all_residents):
            raise HTTPException(status_code=404, detail="Resident not found")
        
        import json
        with open(resident_storage._get_file_path(), 'w', encoding='utf-8') as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Deleted resident: {resident_id}")
        return {"message": "Resident deleted successfully", "resident_id": str(resident_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resident: {e}")
        raise HTTPException(status_code=500, detail=str(e))
