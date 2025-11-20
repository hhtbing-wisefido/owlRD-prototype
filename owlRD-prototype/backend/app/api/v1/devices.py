"""
设备管理API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_devices():
    """获取设备列表"""
    return []
