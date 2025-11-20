"""
护理质量评估API
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/report")
async def get_care_quality_report():
    """获取护理质量报告"""
    return {"status": "coming soon"}
