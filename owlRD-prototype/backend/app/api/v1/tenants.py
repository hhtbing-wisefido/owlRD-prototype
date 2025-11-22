"""
租户管理API - 完整CRUD实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import UUID
import uuid
from loguru import logger

from app.models.tenant import Tenant, TenantCreate, TenantUpdate
from app.services.storage import StorageService

router = APIRouter()
tenant_storage = StorageService[Tenant]("tenants")


@router.get("/", response_model=List[Tenant], summary="获取租户列表")
async def list_tenants(
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取所有租户列表"""
    try:
        tenants = tenant_storage.find_all(lambda _: True)
        return tenants[:limit]
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tenant_id}", response_model=Tenant, summary="获取租户详情")
async def get_tenant(tenant_id: UUID):
    """获取单个租户详情"""
    try:
        tenant = tenant_storage.get(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return tenant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Tenant, status_code=201, summary="创建租户")
async def create_tenant(tenant: TenantCreate):
    """创建新租户"""
    try:
        tenant_dict = tenant.model_dump()
        tenant_dict["tenant_id"] = str(uuid.uuid4())
        result = tenant_storage.create(tenant_dict)
        logger.info(f"Created tenant: {result.get('tenant_id')}")
        return result
    except Exception as e:
        logger.error(f"Error creating tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{tenant_id}", response_model=Tenant, summary="更新租户")
async def update_tenant(tenant_id: UUID, tenant: TenantUpdate):
    """更新租户信息"""
    try:
        result = tenant_storage.update(tenant_id, tenant.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Tenant not found")
        logger.info(f"Updated tenant: {tenant_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{tenant_id}", summary="删除租户")
async def delete_tenant(tenant_id: UUID):
    """删除租户"""
    try:
        success = tenant_storage.delete(tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tenant not found")
        logger.info(f"Deleted tenant: {tenant_id}")
        return {"status": "success", "tenant_id": str(tenant_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))
