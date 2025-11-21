"""
角色管理API端点
对应 roles 表 (02_roles.sql)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.models.user import Role, RoleCreate, RoleUpdate
from app.services.storage import StorageService

router = APIRouter()
storage = StorageService()


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
    all_roles = await storage.read_all("roles", Role)
    
    # 按租户过滤
    roles = [r for r in all_roles if r.tenant_id == tenant_id]
    
    # 按启用状态过滤
    if is_active is not None:
        roles = [r for r in roles if r.is_active == is_active]
    
    # 按角色编码过滤
    if role_code:
        roles = [r for r in roles if r.role_code == role_code]
    
    return roles


@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: UUID):
    """
    获取单个角色详情
    
    - **role_id**: 角色ID
    """
    role = await storage.read_by_id("roles", role_id, Role)
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
    existing_roles = await storage.read_all("roles", Role)
    for existing in existing_roles:
        if existing.tenant_id == role_data.tenant_id and existing.role_code == role_data.role_code:
            raise HTTPException(
                status_code=400, 
                detail=f"Role code '{role_data.role_code}' already exists for this tenant"
            )
    
    # 创建角色
    role = Role(**role_data.model_dump())
    await storage.create("roles", role.role_id, role)
    return role


@router.put("/{role_id}", response_model=Role)
async def update_role(role_id: UUID, role_data: RoleUpdate):
    """
    更新角色信息
    
    注意：
    - 系统预置角色（is_system=True）的 role_code 和 is_system 字段不可修改
    - 只能更新 display_name, description, is_active
    """
    # 读取现有角色
    existing_role = await storage.read_by_id("roles", role_id, Role)
    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色限制检查
    if existing_role.is_system:
        if role_data.display_name is None and role_data.description is None and role_data.is_active is None:
            raise HTTPException(
                status_code=400,
                detail="System roles can only update display_name, description, or is_active"
            )
    
    # 更新字段
    update_data = role_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_role, key, value)
    
    # 保存更新
    await storage.update("roles", role_id, existing_role)
    return existing_role


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: UUID):
    """
    删除角色
    
    注意：
    - 系统预置角色（is_system=True）不可删除
    - 删除前应确保没有用户正在使用该角色
    """
    # 读取角色
    role = await storage.read_by_id("roles", role_id, Role)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 系统角色不可删除
    if role.is_system:
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be deleted"
        )
    
    # 检查是否有用户使用该角色
    from app.models.user import User
    all_users = await storage.read_all("users", User)
    users_with_role = [u for u in all_users if u.role == role.role_code]
    
    if users_with_role:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {len(users_with_role)} user(s) are currently assigned this role"
        )
    
    # 删除角色
    await storage.delete("roles", role_id)
    return None
