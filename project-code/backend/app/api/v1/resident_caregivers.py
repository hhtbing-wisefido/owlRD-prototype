"""
住户-护理人员关联API端点
对应 resident_caregivers 表 (10_resident_caregivers.sql)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.models.resident import (
    ResidentCaregiver,
    ResidentCaregiverCreate,
    ResidentCaregiverUpdate
)
from app.services.storage import StorageService

router = APIRouter(prefix="/resident_caregivers", tags=["Resident Caregivers"])
caregiver_storage = StorageService(collection="resident_caregivers")


@router.get("", response_model=List[ResidentCaregiver])
async def list_caregiver_assignments(
    tenant_id: UUID = Query(..., description="租户ID"),
    resident_id: Optional[UUID] = Query(None, description="住户ID（可选）"),
    caregiver_id: Optional[UUID] = Query(None, description="护理人员ID（可选）")
):
    """
    获取护理人员分配列表
    
    - **tenant_id**: 必需，租户ID
    - **resident_id**: 可选，查看指定住户的护理人员
    - **caregiver_id**: 可选，查看指定护理人员负责的住户
    """
    assignments = caregiver_storage.find_all(
        lambda a: str(a.get("tenant_id")) == str(tenant_id)
    )
    
    if resident_id:
        assignments = [a for a in assignments if str(a.get("resident_id")) == str(resident_id)]
    
    if caregiver_id:
        # 检查5个caregiver_id字段
        assignments = [
            a for a in assignments
            if str(caregiver_id) in [
                str(a.get("caregiver_id1")),
                str(a.get("caregiver_id2")),
                str(a.get("caregiver_id3")),
                str(a.get("caregiver_id4")),
                str(a.get("caregiver_id5"))
            ]
        ]
    
    return assignments


@router.get("/{assignment_id}", response_model=ResidentCaregiver)
async def get_assignment(assignment_id: UUID):
    """获取指定分配详情"""
    assignment = caregiver_storage.find_by_id(assignment_id, "id")
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post("", response_model=ResidentCaregiver, status_code=201)
async def create_assignment(assignment: ResidentCaregiverCreate):
    """创建护理人员分配"""
    assignment_dict = assignment.model_dump()
    
    # 检查是否已存在该住户的分配
    existing = caregiver_storage.find_all(
        lambda a: (
            str(a.get("tenant_id")) == str(assignment.tenant_id) and
            str(a.get("resident_id")) == str(assignment.resident_id)
        )
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Caregiver assignment already exists for this resident. Use PUT to update."
        )
    
    return caregiver_storage.create(assignment_dict)


@router.put("/{assignment_id}", response_model=ResidentCaregiver)
async def update_assignment(assignment_id: UUID, assignment_update: ResidentCaregiverUpdate):
    """更新护理人员分配"""
    existing = caregiver_storage.find_by_id(assignment_id, "id")
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    update_dict = assignment_update.model_dump(exclude_unset=True)
    return caregiver_storage.update(assignment_id, update_dict, id_field="id")


@router.delete("/{assignment_id}", status_code=204)
async def delete_assignment(assignment_id: UUID):
    """删除护理人员分配"""
    existing = caregiver_storage.find_by_id(assignment_id, "id")
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    caregiver_storage.delete(assignment_id, id_field="id")
    return None
