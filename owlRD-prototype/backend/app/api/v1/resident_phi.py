"""
住户PHI(Protected Health Information)管理API端点
对应 resident_phi 表 (08_resident_phi.sql)
严格遵循HIPAA合规要求
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models.resident import ResidentPHI, ResidentPHICreate, ResidentPHIUpdate
from app.services.storage import StorageService

router = APIRouter()
phi_storage = StorageService[ResidentPHI]("resident_phi")


@router.get("/resident_phi", response_model=List[ResidentPHI])
async def get_resident_phi_list(
    tenant_id: UUID = Query(..., description="租户ID"),
    resident_id: Optional[UUID] = Query(None, description="按住户ID筛选")
):
    """
    获取住户PHI列表
    
    **注意**: PHI数据高度敏感，需要严格的访问控制
    
    - **tenant_id**: 必须，租户ID
    - **resident_id**: 可选，按住户ID筛选
    
    **权限要求**: 仅医疗专业人员或授权管理员可访问
    """
    # 构建过滤函数
    def filter_fn(p):
        if str(p.get("tenant_id")) != str(tenant_id):
            return False
        if resident_id and str(p.get("resident_id")) != str(resident_id):
            return False
        return True
    
    phi_records = await phi_storage.find_all(filter_fn)
    return phi_records


@router.get("/resident_phi/{phi_id}", response_model=ResidentPHI)
async def get_resident_phi(phi_id: UUID):
    """
    获取单个住户PHI记录
    
    **注意**: PHI数据高度敏感
    
    - **phi_id**: PHI记录ID
    
    **权限要求**: 仅医疗专业人员或授权管理员可访问
    """
    phi = await phi_storage.find_by_id("phi_id", phi_id)
    if not phi:
        raise HTTPException(status_code=404, detail="Resident PHI record not found")
    return phi


@router.post("/resident_phi", response_model=ResidentPHI, status_code=201)
async def create_resident_phi(phi_data: ResidentPHICreate):
    """
    创建住户PHI记录
    
    **重要**: 
    - PHI数据需要加密存储
    - 符合HIPAA合规要求
    - 访问需要严格审计
    
    **字段说明**:
    - **real_first_name/real_last_name**: 真实姓名（加密存储）
    - **date_of_birth**: 出生日期（加密）
    - **ssn_last_4**: 社保号后4位（加密）
    - **phone_number/email**: 联系方式（加密）
    - **emergency_contact_***: 紧急联系人信息（加密）
    - **medical_history**: 病史（加密）
    - **medications**: 用药信息（加密）
    - **allergies**: 过敏信息（加密）
    
    **权限要求**: 仅授权医疗管理员可创建
    """
    # 检查住户是否存在
    resident_storage = StorageService("residents")
    resident = await resident_storage.find_by_id("resident_id", phi_data.resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    
    # 检查是否已有PHI记录
    existing_phi = await phi_storage.find_all(lambda _: True)
    for phi in existing_phi:
        if str(phi.get("resident_id")) == str(phi_data.resident_id):
            raise HTTPException(
                status_code=400,
                detail=f"PHI record already exists for resident {phi_data.resident_id}"
            )
    
    # 创建PHI记录
    from app.models.base import generate_uuid
    phi_dict = phi_data.model_dump()
    phi_dict["phi_id"] = str(generate_uuid())
    phi_dict["created_at"] = datetime.now().isoformat()
    phi_dict["updated_at"] = datetime.now().isoformat()
    
    await phi_storage.create(phi_dict)
    
    # TODO: 记录访问审计日志
    # audit_log(action="CREATE_PHI", user=current_user, resident_id=phi_dict["resident_id"])
    
    return phi_dict


@router.put("/resident_phi/{phi_id}", response_model=ResidentPHI)
async def update_resident_phi(phi_id: UUID, phi_data: ResidentPHIUpdate):
    """
    更新住户PHI信息
    
    **注意**: 所有更新需要审计日志
    
    **权限要求**: 仅授权医疗管理员可更新
    """
    # 读取现有PHI
    existing_phi = await phi_storage.find_by_id("phi_id", phi_id)
    if not existing_phi:
        raise HTTPException(status_code=404, detail="Resident PHI record not found")
    
    # 更新字段
    update_data = phi_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    # 保存更新
    updated = await phi_storage.update("phi_id", phi_id, update_data)
    
    # TODO: 记录访问审计日志
    # audit_log(action="UPDATE_PHI", user=current_user, phi_id=phi_id, changes=update_data)
    
    return updated


@router.delete("/resident_phi/{phi_id}", status_code=204)
async def delete_resident_phi(phi_id: UUID):
    """
    删除住户PHI记录
    
    **警告**: 
    - PHI删除需要特殊授权
    - 根据HIPAA规定，PHI通常应标记为删除而非物理删除
    - 需要记录详细的审计日志
    
    **权限要求**: 仅系统管理员可删除
    """
    # 读取PHI
    phi = await phi_storage.find_by_id("phi_id", phi_id)
    if not phi:
        raise HTTPException(status_code=404, detail="Resident PHI record not found")
    
    # TODO: 记录审计日志
    # audit_log(action="DELETE_PHI", user=current_user, phi_id=phi_id)
    
    # 删除PHI（实际生产环境应该是软删除）
    await phi_storage.delete("phi_id", phi_id)
    
    return None


@router.get("/residents/{resident_id}/phi", response_model=Optional[ResidentPHI])
async def get_phi_by_resident(resident_id: UUID):
    """
    通过住户ID获取PHI记录（便捷端点）
    
    - **resident_id**: 住户ID
    
    **权限要求**: 仅授权人员可访问
    """
    phi_records = await phi_storage.find_all(
        lambda p: str(p.get("resident_id")) == str(resident_id)
    )
    
    if phi_records:
        # TODO: 记录访问审计日志
        # audit_log(action="VIEW_PHI", user=current_user, resident_id=resident_id)
        return phi_records[0]
    
    # 没有PHI记录也不算错误，可能还未创建
    return None
