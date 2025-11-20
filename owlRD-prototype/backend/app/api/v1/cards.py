"""
卡片管理API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_cards():
    """获取卡片列表"""
    return []
