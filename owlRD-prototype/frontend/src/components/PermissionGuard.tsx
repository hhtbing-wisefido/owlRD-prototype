/**
 * 权限守卫组件
 * 只在用户有权限时渲染子组件
 */

import type { ReactNode } from 'react'
import { usePermissions, type PermissionResult } from '../hooks/usePermissions'

interface PermissionGuardProps {
  requires: keyof PermissionResult | ((permissions: PermissionResult) => boolean)
  fallback?: ReactNode
  children: ReactNode
}

/**
 * 权限组件包装器
 * 只在用户有权限时渲染子组件
 * 
 * @example
 * ```tsx
 * <PermissionGuard requires="canEditCard" fallback={<div>无权限</div>}>
 *   <EditButton />
 * </PermissionGuard>
 * ```
 */
export function PermissionGuard({ requires, fallback = null, children }: PermissionGuardProps) {
  const permissions = usePermissions()
  
  let hasPermission = false
  
  if (typeof requires === 'function') {
    hasPermission = requires(permissions)
  } else {
    hasPermission = Boolean(permissions[requires])
  }
  
  if (!hasPermission) {
    return <>{fallback}</>
  }
  
  return <>{children}</>
}

export default PermissionGuard
