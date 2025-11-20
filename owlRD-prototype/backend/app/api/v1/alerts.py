"""
告警管理API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_alerts():
    """获取告警列表"""
    return []
