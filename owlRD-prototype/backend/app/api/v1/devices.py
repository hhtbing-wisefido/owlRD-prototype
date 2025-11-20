"""
设备管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from loguru import logger

from app.models.device import Device, DeviceCreate, DeviceUpdate
from app.services.storage import StorageService

router = APIRouter()
device_storage = StorageService[Device]("devices")


@router.get("/", response_model=List[Device], summary="获取设备列表")
async def list_devices(
    tenant_id: UUID = Query(..., description="租户ID"),
    location_id: Optional[UUID] = Query(None, description="位置ID筛选"),
    device_type: Optional[str] = Query(None, description="设备类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    获取设备列表
    
    ## 筛选条件
    - **tenant_id**: 租户ID（必填）
    - **location_id**: 按位置筛选（可选）
    - **device_type**: 按设备类型筛选（可选）
    - **status**: 按状态筛选（online/offline/error/dormant/maintenance）
    - **limit**: 返回数量限制
    """
    try:
        def filter_func(d):
            if str(d.get("tenant_id")) != str(tenant_id):
                return False
            if location_id and str(d.get("location_id")) != str(location_id):
                return False
            if device_type and d.get("device_type") != device_type:
                return False
            if status and d.get("status") != status:
                return False
            return True
        
        devices = await device_storage.find_all(filter_func)
        return devices[:limit]
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}", response_model=Device, summary="获取设备详情")
async def get_device(device_id: UUID):
    """获取单个设备详情"""
    try:
        device = await device_storage.get(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Device, status_code=201, summary="创建设备")
async def create_device(device: DeviceCreate):
    """
    创建新设备
    
    ## 必填字段
    - device_name: 设备名称
    - device_model: 设备型号
    - device_type: 设备类型
    - comm_mode: 通信方式
    - serial_number或uid: 至少一个
    """
    try:
        result = await device_storage.create(device)
        logger.info(f"Created device: {result.get('device_id')}")
        return result
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{device_id}", response_model=Device, summary="更新设备")
async def update_device(device_id: UUID, device: DeviceUpdate):
    """
    更新设备信息
    
    ## 可更新字段
    - 状态（online/offline/error等）
    - 位置绑定
    - 固件版本
    - 配置信息
    """
    try:
        result = await device_storage.update(
            device_id,
            device.model_dump(exclude_unset=True)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Device not found")
        logger.info(f"Updated device: {device_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{device_id}", summary="删除设备")
async def delete_device(device_id: UUID):
    """
    删除设备
    
    ## 注意
    - 删除前应确保设备已离线
    - 相关数据不会被删除
    """
    try:
        success = await device_storage.delete(device_id)
        if not success:
            raise HTTPException(status_code=404, detail="Device not found")
        logger.info(f"Deleted device: {device_id}")
        return {"status": "success", "device_id": str(device_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/status", summary="更新设备状态")
async def update_device_status(
    device_id: UUID,
    status: str = Query(..., description="新状态")
):
    """
    快速更新设备状态
    
    ## 状态值
    - online: 在线
    - offline: 离线
    - error: 错误
    - dormant: 休眠
    - maintenance: 维护中
    """
    try:
        device = await device_storage.get(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # 验证状态值
        valid_statuses = ["online", "offline", "error", "dormant", "maintenance"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        result = await device_storage.update(device_id, {"status": status})
        logger.info(f"Updated device status: {device_id} -> {status}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating device status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
