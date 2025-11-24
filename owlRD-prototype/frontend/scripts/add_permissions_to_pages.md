# 前端页面权限控制批量更新指南

## 已完成页面
- ✅ Cards.tsx - 卡片管理（完整权限控制）
- ✅ Users.tsx - 用户管理（完整权限控制）
- ✅ PermissionSettings.tsx - 权限配置（Admin/Director专用）

## 需要更新的页面

### 1. Devices.tsx - 设备管理
**所需权限**: `canManageDevices`
**按钮权限**:
- 创建设备: canManageDevices
- 编辑设备: canManageDevices
- 删除设备: isAdmin

**更新步骤**:
```typescript
// 1. 导入
import { usePermissions } from '../hooks/usePermissions'
import PermissionGuard from '../components/PermissionGuard'

// 2. 使用Hook
const { canManageDevices, isAdmin } = usePermissions()

// 3. 包裹按钮
<PermissionGuard requires="canManageDevices">
  <button>创建设备</button>
</PermissionGuard>
```

### 2. Locations.tsx - 位置管理
**所需权限**: `canManageLocations`
**按钮权限**:
- 创建位置: canManageLocations
- 编辑位置: canManageLocations
- 删除位置: isAdmin

### 3. Residents.tsx - 住户管理
**所需权限**: `canManageResidents`
**按钮权限**:
- 创建住户: canManageResidents
- 编辑住户: canManageResidents
- 删除住户: isAdmin

### 4. Alerts.tsx - 告警管理
**所需权限**: `canViewAlerts`
**按钮权限**:
- 确认告警: canViewAlerts
- 解决告警: canViewAlerts
- 查看详情: canViewAlerts

### 5. AlertPolicies.tsx - 告警策略
**所需权限**: `canManageAlertPolicies`
**按钮权限**:
- 创建策略: canManageAlertPolicies
- 编辑策略: canManageAlertPolicies
- 删除策略: isAdmin

### 6. Dashboard.tsx - 仪表板
**所需权限**: 无（所有人可访问）
**特殊处理**:
- 根据权限显示不同的统计卡片
- 根据alert_scope过滤显示的数据

### 7. Roles.tsx - 角色管理
**所需权限**: `canManageRoles`
**按钮权限**:
- 创建角色: isAdmin
- 编辑角色: isAdmin
- 删除角色: isAdmin

## 通用权限控制模式

### 模式1: 简单按钮控制
```typescript
<PermissionGuard requires="canEdit">
  <button>编辑</button>
</PermissionGuard>
```

### 模式2: 复杂条件控制
```typescript
<PermissionGuard requires={(p) => p.isAdmin || p.isDirector}>
  <AdminPanel />
</PermissionGuard>
```

### 模式3: 带fallback的控制
```typescript
<PermissionGuard 
  requires="canDelete"
  fallback={<div>权限不足</div>}
>
  <DeleteButton />
</PermissionGuard>
```

## 权限Hook可用属性

```typescript
const {
  // 角色判断
  isAdmin,
  isDirector,
  isNurseManager,
  isNurse,
  isCaregiver,
  
  // 操作权限
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
  
  // 原始数据
  user,
  alertScope
} = usePermissions()
```

## 完成检查清单

- [ ] Devices.tsx - 权限控制添加完成
- [ ] Locations.tsx - 权限控制添加完成
- [ ] Residents.tsx - 权限控制添加完成
- [ ] Alerts.tsx - 权限控制添加完成
- [ ] AlertPolicies.tsx - 权限控制添加完成
- [ ] Dashboard.tsx - 权限控制添加完成
- [ ] Roles.tsx - 权限控制添加完成
- [ ] 所有页面测试通过
- [ ] 文档更新完成
