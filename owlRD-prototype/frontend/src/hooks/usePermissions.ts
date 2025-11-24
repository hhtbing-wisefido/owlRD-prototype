/**
 * 权限Hook
 * 提供基于角色和alert_scope的权限判断
 */

import { useMemo } from 'react'

export interface User {
  user_id: string
  tenant_id: string
  username: string
  email: string
  role: string
  alert_scope?: 'ALL' | 'LOCATION' | 'ASSIGNED_ONLY'
  tags?: Record<string, any>
  is_active?: boolean
}

export interface PermissionResult {
  // 角色权限
  isAdmin: boolean
  isDirector: boolean
  isNurseManager: boolean
  isNurse: boolean
  isCaregiver: boolean
  
  // 数据查看权限
  canViewAllCards: boolean
  canViewLocationCards: boolean
  canViewAssignedCards: boolean
  
  // 操作权限
  canCreateCard: boolean
  canEditCard: boolean
  canDeleteCard: boolean
  canManageUsers: boolean
  canManageRoles: boolean
  canManageDevices: boolean
  canManageLocations: boolean
  canManageResidents: boolean
  canViewAlerts: boolean
  canManageAlertPolicies: boolean
  
  // 原始用户信息
  user: User | null
  alertScope: string
}

/**
 * 获取当前用户
 */
function getCurrentUser(): User | null {
  try {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    return JSON.parse(userStr) as User
  } catch {
    return null
  }
}

/**
 * 权限Hook
 * 
 * @returns PermissionResult 权限判断结果
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { canViewAllCards, isAdmin, canEditCard } = usePermissions()
 *   
 *   return (
 *     <div>
 *       {canViewAllCards && <AllCardsView />}
 *       {canEditCard && <EditButton />}
 *     </div>
 *   )
 * }
 * ```
 */
export function usePermissions(): PermissionResult {
  const user = getCurrentUser()
  
  const permissions = useMemo(() => {
    if (!user) {
      return {
        isAdmin: false,
        isDirector: false,
        isNurseManager: false,
        isNurse: false,
        isCaregiver: false,
        canViewAllCards: false,
        canViewLocationCards: false,
        canViewAssignedCards: false,
        canCreateCard: false,
        canEditCard: false,
        canDeleteCard: false,
        canManageUsers: false,
        canManageRoles: false,
        canManageDevices: false,
        canManageLocations: false,
        canManageResidents: false,
        canViewAlerts: false,
        canManageAlertPolicies: false,
        user: null,
        alertScope: 'ASSIGNED_ONLY'
      }
    }
    
    const role = user.role || ''
    const alertScope = user.alert_scope || 'ASSIGNED_ONLY'
    
    // 角色判断
    const isAdmin = role === 'Admin'
    const isDirector = role === 'Director'
    const isNurseManager = role === 'NurseManager'
    const isNurse = role === 'Nurse'
    const isCaregiver = role === 'Caregiver'
    
    // 数据查看权限（基于alert_scope）
    const canViewAllCards = isAdmin || alertScope === 'ALL'
    const canViewLocationCards = alertScope === 'LOCATION'
    const canViewAssignedCards = alertScope === 'ASSIGNED_ONLY'
    
    // 操作权限（基于角色）
    const canCreateCard = isAdmin || isDirector || isNurseManager
    const canEditCard = isAdmin || isDirector || isNurseManager
    const canDeleteCard = isAdmin
    const canManageUsers = isAdmin || isDirector
    const canManageRoles = isAdmin
    const canManageDevices = isAdmin || isDirector || isNurseManager
    const canManageLocations = isAdmin || isDirector
    const canManageResidents = isAdmin || isDirector || isNurseManager
    const canViewAlerts = true // 所有角色都能查看告警
    const canManageAlertPolicies = isAdmin || isDirector || isNurseManager
    
    return {
      isAdmin,
      isDirector,
      isNurseManager,
      isNurse,
      isCaregiver,
      canViewAllCards,
      canViewLocationCards,
      canViewAssignedCards,
      canCreateCard,
      canEditCard,
      canDeleteCard,
      canManageUsers,
      canManageRoles,
      canManageDevices,
      canManageLocations,
      canManageResidents,
      canViewAlerts,
      canManageAlertPolicies,
      user,
      alertScope
    }
  }, [user])
  
  return permissions
}

/**
 * 获取用户令牌
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('token')
}

/**
 * 获取当前用户ID
 */
export function getCurrentUserId(): string | null {
  const user = getCurrentUser()
  return user?.user_id || null
}

/**
 * 获取当前租户ID
 */
export function getCurrentTenantId(): string | null {
  const user = getCurrentUser()
  return user?.tenant_id || null
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken() && !!getCurrentUser()
}
