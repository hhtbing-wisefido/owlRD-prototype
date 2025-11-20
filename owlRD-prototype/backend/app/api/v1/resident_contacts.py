"""
住户联系人API端点
对应 resident_contacts 表 (09_resident_contacts.sql)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.models.resident import (
    ResidentContact,
    ResidentContactCreate,
    ResidentContactUpdate
)
from app.services.storage import StorageService

router = APIRouter(prefix="/resident_contacts", tags=["Resident Contacts"])
contact_storage = StorageService(collection="resident_contacts")


@router.get("", response_model=List[ResidentContact])
async def list_contacts(
    tenant_id: UUID = Query(..., description="租户ID"),
    resident_id: Optional[UUID] = Query(None, description="住户ID（可选）")
):
    """
    获取住户联系人列表
    
    - **tenant_id**: 必需，租户ID
    - **resident_id**: 可选，指定住户的联系人
    """
    contacts = contact_storage.find_all(
        lambda c: str(c.get("tenant_id")) == str(tenant_id)
    )
    
    if resident_id:
        contacts = [c for c in contacts if str(c.get("resident_id")) == str(resident_id)]
    
    return contacts


@router.get("/{contact_id}", response_model=ResidentContact)
async def get_contact(contact_id: UUID):
    """获取指定联系人详情"""
    contact = contact_storage.find_by_id(contact_id, "contact_id")
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("", response_model=ResidentContact, status_code=201)
async def create_contact(contact: ResidentContactCreate):
    """创建住户联系人"""
    contact_dict = contact.model_dump()
    
    # 检查slot是否已被占用
    existing = contact_storage.find_all(
        lambda c: (
            str(c.get("tenant_id")) == str(contact.tenant_id) and
            str(c.get("resident_id")) == str(contact.resident_id) and
            c.get("slot") == contact.slot
        )
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Slot {contact.slot} already occupied for this resident"
        )
    
    return contact_storage.create(contact_dict)


@router.put("/{contact_id}", response_model=ResidentContact)
async def update_contact(contact_id: UUID, contact_update: ResidentContactUpdate):
    """更新联系人信息"""
    existing = contact_storage.find_by_id(contact_id, "contact_id")
    if not existing:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_dict = contact_update.model_dump(exclude_unset=True)
    return contact_storage.update(contact_id, update_dict, id_field="contact_id")


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: UUID):
    """删除联系人"""
    existing = contact_storage.find_by_id(contact_id, "contact_id")
    if not existing:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact_storage.delete(contact_id, id_field="contact_id")
    return None
