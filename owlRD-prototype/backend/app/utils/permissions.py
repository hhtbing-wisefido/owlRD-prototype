"""
权限控制工具
提供基于角色的访问控制（RBAC）
"""

from typing import List, Optional
from fastapi import HTTPException, status, Depends
from app.api.v1.auth import get_current_user


# ============================================================================
# 角色定义
# ============================================================================

class Role:
    """角色枚举"""
    DIRECTOR = "Director"              # 院长/主管
    NURSE_MANAGER = "NurseManager"     # 护士长
    NURSE = "Nurse"                    # 护士
    CAREGIVER = "Caregiver"           # 护理员
    DOCTOR = "Doctor"                  # 医生
    FAMILY_MEMBER = "FamilyMember"     # 家属
    
    # 角色层级（数字越小权限越高）
    HIERARCHY = {
        DIRECTOR: 1,
        NURSE_MANAGER: 2,
        DOCTOR: 2,
        NURSE: 3,
        CAREGIVER: 4,
        FAMILY_MEMBER: 5
    }


# ============================================================================
# 权限检查函数
# ============================================================================

def check_permission(
    current_user: dict,
    required_roles: Optional[List[str]] = None,
    min_role_level: Optional[int] = None
) -> bool:
    """
    检查用户权限
    
    Args:
        current_user: 当前用户信息
        required_roles: 允许的角色列表
        min_role_level: 最小角色层级（数字越小权限越高）
    
    Returns:
        是否有权限
    """
    user_role = current_user.get("role")
    
    # 检查角色列表
    if required_roles:
        if user_role not in required_roles:
            return False
    
    # 检查角色层级
    if min_role_level is not None:
        user_level = Role.HIERARCHY.get(user_role, 99)
        if user_level > min_role_level:
            return False
    
    return True


# ============================================================================
# 权限装饰器依赖
# ============================================================================

class RequireRole:
    """
    要求特定角色的依赖
    
    用法：
        @router.get("/admin-only")
        async def admin_endpoint(user: dict = Depends(RequireRole([Role.DIRECTOR]))):
            return {"message": "Admin access"}
    """
    
    def __init__(self, roles: List[str]):
        self.roles = roles
    
    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        if not check_permission(current_user, required_roles=self.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(self.roles)}"
            )
        return current_user


class RequireMinRole:
    """
    要求最小角色层级的依赖
    
    用法：
        @router.get("/management")
        async def management_endpoint(user: dict = Depends(RequireMinRole(Role.NURSE_MANAGER))):
            return {"message": "Management access"}
    """
    
    def __init__(self, role: str):
        self.min_level = Role.HIERARCHY.get(role, 99)
        self.role_name = role
    
    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        if not check_permission(current_user, min_role_level=self.min_level):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要{self.role_name}及以上角色"
            )
        return current_user


# ============================================================================
# 便捷权限依赖
# ============================================================================

# 管理员权限（Director）
RequireDirector = RequireRole([Role.DIRECTOR])

# 管理层权限（Director, NurseManager, Doctor）
RequireManagement = RequireRole([Role.DIRECTOR, Role.NURSE_MANAGER, Role.DOCTOR])

# 医护人员权限（Director, NurseManager, Doctor, Nurse）
RequireMedicalStaff = RequireRole([
    Role.DIRECTOR, 
    Role.NURSE_MANAGER, 
    Role.DOCTOR, 
    Role.NURSE
])

# 所有员工权限（不包括家属）
RequireStaff = RequireRole([
    Role.DIRECTOR,
    Role.NURSE_MANAGER,
    Role.DOCTOR,
    Role.NURSE,
    Role.CAREGIVER
])


# ============================================================================
# 数据访问权限检查
# ============================================================================

def check_tenant_access(current_user: dict, resource_tenant_id: str) -> bool:
    """
    检查用户是否可以访问指定租户的资源
    
    Args:
        current_user: 当前用户
        resource_tenant_id: 资源所属租户ID
    
    Returns:
        是否有权限访问
    """
    user_tenant_id = current_user.get("tenant_id")
    return str(user_tenant_id) == str(resource_tenant_id)


def check_resident_access(current_user: dict, resident_id: str, assigned_caregivers: List[str]) -> bool:
    """
    检查用户是否可以访问指定住户的数据
    
    Args:
        current_user: 当前用户
        resident_id: 住户ID
        assigned_caregivers: 分配的护理人员ID列表
    
    Returns:
        是否有权限访问
    """
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Director和NurseManager可以访问所有住户
    if user_role in [Role.DIRECTOR, Role.NURSE_MANAGER]:
        return True
    
    # 其他角色只能访问分配给自己的住户
    return str(user_id) in [str(cg_id) for cg_id in assigned_caregivers]


# ============================================================================
# 权限辅助函数
# ============================================================================

def get_user_permissions(role: str) -> dict:
    """
    获取角色的权限列表
    
    Returns:
        权限字典
    """
    permissions = {
        Role.DIRECTOR: {
            "can_manage_users": True,
            "can_manage_roles": True,
            "can_manage_locations": True,
            "can_manage_residents": True,
            "can_manage_devices": True,
            "can_view_phi": True,
            "can_manage_alerts": True,
            "can_view_all_residents": True,
            "can_export_data": True
        },
        Role.NURSE_MANAGER: {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_locations": True,
            "can_manage_residents": True,
            "can_manage_devices": True,
            "can_view_phi": True,
            "can_manage_alerts": True,
            "can_view_all_residents": True,
            "can_export_data": True
        },
        Role.DOCTOR: {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_locations": False,
            "can_manage_residents": False,
            "can_manage_devices": False,
            "can_view_phi": True,
            "can_manage_alerts": False,
            "can_view_all_residents": True,
            "can_export_data": False
        },
        Role.NURSE: {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_locations": False,
            "can_manage_residents": False,
            "can_manage_devices": False,
            "can_view_phi": True,
            "can_manage_alerts": False,
            "can_view_all_residents": False,
            "can_export_data": False
        },
        Role.CAREGIVER: {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_locations": False,
            "can_manage_residents": False,
            "can_manage_devices": False,
            "can_view_phi": False,
            "can_manage_alerts": False,
            "can_view_all_residents": False,
            "can_export_data": False
        },
        Role.FAMILY_MEMBER: {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_locations": False,
            "can_manage_residents": False,
            "can_manage_devices": False,
            "can_view_phi": False,
            "can_manage_alerts": False,
            "can_view_all_residents": False,
            "can_export_data": False
        }
    }
    
    return permissions.get(role, {})
