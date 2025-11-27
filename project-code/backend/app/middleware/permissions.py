"""
权限中间件
提供常用的权限检查装饰器和辅助函数
"""

from typing import Dict, Any, Callable
from fastapi import HTTPException
from uuid import UUID


def check_tenant_access(current_user: Dict[str, Any], tenant_id: UUID) -> None:
    """
    检查用户是否有权访问指定租户的数据
    
    参数:
        current_user: 当前用户信息
        tenant_id: 要访问的租户ID
        
    异常:
        HTTPException: 403 无权访问
    """
    if str(current_user.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=403,
            detail="无权访问其他租户的数据"
        )


def check_role_permission(current_user: Dict[str, Any], allowed_roles: list[str]) -> None:
    """
    检查用户角色是否在允许的角色列表中
    
    参数:
        current_user: 当前用户信息
        allowed_roles: 允许的角色列表
        
    异常:
        HTTPException: 403 权限不足
    """
    user_role = current_user.get("role")
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"需要以下角色之一: {', '.join(allowed_roles)}"
        )


def check_manage_permission(current_user: Dict[str, Any]) -> None:
    """
    检查用户是否有管理权限（Admin, Director, NurseManager）
    
    参数:
        current_user: 当前用户信息
        
    异常:
        HTTPException: 403 权限不足
    """
    check_role_permission(current_user, ["Admin", "Director", "NurseManager"])


def check_admin_permission(current_user: Dict[str, Any]) -> None:
    """
    检查用户是否有Admin权限
    
    参数:
        current_user: 当前用户信息
        
    异常:
        HTTPException: 403 权限不足
    """
    check_role_permission(current_user, ["Admin"])


def verify_resource_access(
    current_user: Dict[str, Any],
    resource: Dict[str, Any],
    resource_name: str = "资源"
) -> None:
    """
    验证用户是否有权访问指定资源
    检查租户ID是否匹配
    
    参数:
        current_user: 当前用户信息
        resource: 资源数据（必须包含tenant_id字段）
        resource_name: 资源名称（用于错误消息）
        
    异常:
        HTTPException: 403 无权访问
    """
    resource_tenant_id = resource.get("tenant_id")
    if not resource_tenant_id:
        return  # 资源没有tenant_id，跳过检查
    
    if str(current_user.get("tenant_id")) != str(resource_tenant_id):
        raise HTTPException(
            status_code=403,
            detail=f"无权访问其他租户的{resource_name}"
        )
