"""
角色管理API端点
对应 roles 表 (02_roles.sql)
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.models.user import Role, RoleCreate, RoleUpdate
from app.services.storage import StorageService

router = APIRouter()
role_storage = StorageService[Role]("roles")


@router.get("", response_model=List[Role])
async def get_roles(
    tenant_id: UUID = Query(..., description="租户ID"),
    is_active: Optional[bool] = Query(None, description="筛选启用状态"),
    role_code: Optional[str] = Query(None, description="按角色编码筛选")
):
    """
    获取角色列表
    
    - **tenant_id**: 必须，租户ID
    - **is_active**: 可选，筛选启用/禁用的角色
    - **role_code**: 可选，按角色编码筛选（如 Director, Nurse）
    """
    roles_data = await role_storage.find_all(
        lambda r: str(r.get("tenant_id")) == str(tenant_id)
    )
    
    # 额外过滤
    if is_active is not None:
        roles_data = [r for r in roles_data if r.get("is_active") == is_active]
    
    if role_code:
        roles_data = [r for r in roles_data if r.get("role_code") == role_code]
    
    return roles_data


@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: UUID):
    """
    获取单个角色详情
    
    - **role_id**: 角色ID
    """
    role = await role_storage.find_by_id("role_id", role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("", response_model=Role, status_code=201)
async def create_role(role_data: RoleCreate):
    """
    创建新角色
    
    - **role_code**: 角色编码（如 Director, NurseManager, Nurse, Caregiver）
    - **display_name**: 角色显示名称
    - **description**: 角色职责说明（可选）
    - **is_system**: 是否系统预置角色（系统角色不可删除）
    - **is_active**: 是否启用
    """
    # 检查角色编码是否已存在
    existing_roles = await role_storage.find_all(lambda _: True)
    for existing in existing_roles:
        if str(existing.get("tenant_id")) == str(role_data.tenant_id) and existing.get("role_code") == role_data.role_code:
            raise HTTPException(
                status_code=400, 
                detail=f"Role code '{role_data.role_code}' already exists for this tenant"
            )
    
    # 创建角色
    from app.models.base import generate_uuid
    role_dict = role_data.model_dump()
    role_dict["role_id"] = str(generate_uuid())
    role_dict["created_at"] = role_dict.get("created_at") or datetime.now().isoformat()
    role_dict["updated_at"] = datetime.now().isoformat()
    
    await role_storage.create(role_dict)
    return role_dict


@router.put("/{role_id}", response_model=Role)
async def update_role(role_id: UUID, role_data: RoleUpdate):
    """
    更新角色信息
    
    注意：
    - 系统预置角色（is_system=True）的 role_code 和 is_system 字段不可修改
    - 只能更新 display_name, description, is_active
    """
    # 读取现有角色
    existing_role = await role_storage.find_by_id("role_id", role_id)
    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色限制检查
    if existing_role.get("is_system"):
        if role_data.display_name is None and role_data.description is None and role_data.is_active is None:
            raise HTTPException(
                status_code=400,
                detail="System roles can only update display_name, description, or is_active"
            )
    
    # 更新字段
    update_data = role_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    # 保存更新
    updated = await role_storage.update("role_id", role_id, update_data)
    return updated


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: UUID):
    """
    删除角色
    
    注意：
    - 系统预置角色（is_system=True）不可删除
    - 删除前应确保没有用户正在使用该角色
    """
    # 读取角色
    role = await role_storage.find_by_id("role_id", role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色不可删除
    if role.get("is_system"):
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be deleted"
        )
    
    # 检查是否有用户使用该角色
    user_storage = StorageService("users")
    all_users = await user_storage.find_all(lambda _: True)
    users_with_role = [u for u in all_users if u.get("role") == role.get("role_code")]
    
    if users_with_role:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {len(users_with_role)} user(s) are currently assigned this role"
        )
    
    # 删除角色
    await role_storage.delete("role_id", role_id)
    return None
