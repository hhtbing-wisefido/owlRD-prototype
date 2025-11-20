"""
用户管理API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users():
    """获取用户列表"""
    return []
