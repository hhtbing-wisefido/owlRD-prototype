"""
数据导出API - 完整实现
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.services.storage import StorageService
from app.utils.export import (
    export_to_csv, export_to_json, export_to_excel,
    generate_filename, filter_columns, get_export_columns
)
from app.api.v1.auth import get_current_user
from app.utils.permissions import RequireStaff

router = APIRouter()


@router.get("/users")
async def export_users(
    format: str = Query("csv"),
    tenant_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(RequireStaff)
):
    """导出用户数据"""
    storage = StorageService("users")
    users = storage.find_all(
        lambda u: not tenant_id or str(u.get("tenant_id")) == str(tenant_id)
    )
    
    columns = get_export_columns("users")
    data = filter_columns(users, include=columns)
    
    if format == "csv":
        content = export_to_csv(data, columns)
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('users', 'csv')}"}
        )
    elif format == "json":
        content = export_to_json(data)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('users', 'json')}"}
        )
    elif format == "excel":
        content = export_to_excel(data, columns)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('users', 'xlsx')}"}
        )


@router.get("/residents")
async def export_residents(
    format: str = Query("csv"),
    tenant_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(RequireStaff)
):
    """导出住户数据"""
    storage = StorageService("residents")
    residents = storage.find_all(
        lambda r: not tenant_id or str(r.get("tenant_id")) == str(tenant_id)
    )
    
    columns = get_export_columns("residents")
    data = filter_columns(residents, include=columns)
    
    if format == "csv":
        content = export_to_csv(data, columns)
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('residents', 'csv')}"}
        )
    elif format == "json":
        content = export_to_json(data)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('residents', 'json')}"}
        )
    elif format == "excel":
        content = export_to_excel(data, columns)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={generate_filename('residents', 'xlsx')}"}
        )
