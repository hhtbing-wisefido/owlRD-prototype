/**
 * 批量为前端页面添加权限控制的工具脚本
 * 注意：这是辅助脚本，实际需要手动应用更改
 */

// 通用权限导入模板
export const PERMISSION_IMPORTS = `
import { usePermissions } from '../hooks/usePermissions'
import PermissionGuard from '../components/PermissionGuard'
`.trim()

// 通用Hook使用模板  
export const PERMISSION_HOOK_USAGE = (permissions) => `
  const { ${permissions.join(', ')} } = usePermissions()
`.trim()

// 页面特定配置
export const PAGE_CONFIGS = {
  'Locations.tsx': {
    permissions: ['canManageLocations', 'isAdmin'],
    buttons: [
      { selector: 'handleCreate', guard: 'canManageLocations' },
      { selector: 'handleEdit', guard: 'canManageLocations' },
      { selector: 'handleDelete', guard: 'isAdmin' }
    ]
  },
  'Residents.tsx': {
    permissions: ['canManageResidents', 'isAdmin'],
    buttons: [
      { selector: 'handleCreate', guard: 'canManageResidents' },
      { selector: 'handleEdit', guard: 'canManageResidents' },
      { selector: 'handleDelete', guard: 'isAdmin' }
    ]
  },
  'Alerts.tsx': {
    permissions: ['canViewAlerts'],
    buttons: [
      { selector: 'acknowledge', guard: 'canViewAlerts' },
      { selector: 'resolve', guard: 'canViewAlerts' }
    ]
  },
  'AlertPolicies.tsx': {
    permissions: ['canManageAlertPolicies', 'isAdmin'],
    buttons: [
      { selector: 'create', guard: 'canManageAlertPolicies' },
      { selector: 'edit', guard: 'canManageAlertPolicies' },
      { selector: 'delete', guard: 'isAdmin' }
    ]
  },
  'Roles.tsx': {
    permissions: ['isAdmin'],
    buttons: [
      { selector: 'create', guard: 'isAdmin' },
      { selector: 'edit', guard: 'isAdmin' },
      { selector: 'delete', guard: 'isAdmin' }
    ]
  }
}

// 通用权限守卫模板
export const PERMISSION_GUARD_TEMPLATES = {
  button: (guard, content) => `
    <PermissionGuard requires={(p) => p.${guard}}>
      ${content}
    </PermissionGuard>
  `.trim(),
  
  simpleButton: (guard, content) => `
    <PermissionGuard requires="${guard}">
      ${content}  
    </PermissionGuard>
  `.trim(),

  conditional: (guard, content, fallback = '') => `
    <PermissionGuard 
      requires={(p) => p.${guard}}
      ${fallback ? `fallback={${fallback}}` : ''}
    >
      ${content}
    </PermissionGuard>
  `.trim()
}

// 常用权限检查函数
export const PERMISSION_CHECKS = {
  canManageDevices: '(p) => p.isAdmin || p.isDirector || p.isNurseManager',
  canManageLocations: '(p) => p.isAdmin || p.isDirector',
  canManageResidents: '(p) => p.isAdmin || p.isDirector || p.isNurseManager',
  canViewAlerts: '(p) => true', // 所有人都可以查看告警
  canManageAlertPolicies: '(p) => p.isAdmin || p.isDirector',
  canManageUsers: '(p) => p.isAdmin || p.isDirector',
  canManageRoles: '(p) => p.isAdmin',
  canDeleteAny: '(p) => p.isAdmin'
}

console.log('权限控制配置已加载完成')
