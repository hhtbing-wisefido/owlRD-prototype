"""
租户管理API
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from app.models.tenant import Tenant, TenantCreate, TenantUpdate

router = APIRouter()


@router.get("/", response_model=List[Tenant])
async def list_tenants():
    """获取租户列表"""
    # TODO: 从存储服务获取
    return []


@router.post("/", response_model=Tenant, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant: TenantCreate):
    """创建租户"""
    # TODO: 实现创建逻辑
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: UUID):
    """获取租户详情"""
    # TODO: 实现获取逻辑
    raise HTTPException(status_code=404, detail="Tenant not found")


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: UUID, tenant: TenantUpdate):
    """更新租户"""
    # TODO: 实现更新逻辑
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: UUID):
    """删除租户"""
    # TODO: 实现删除逻辑
    raise HTTPException(status_code=501, detail="Not implemented yet")
