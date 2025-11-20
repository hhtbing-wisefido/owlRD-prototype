"""
住户管理API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_residents():
    """获取住户列表"""
    return []
