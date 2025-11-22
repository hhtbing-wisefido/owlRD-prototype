import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Plus, Edit2, Trash2, UserCheck, AlertCircle } from 'lucide-react'
import { API_CONFIG, API_ENDPOINTS } from '../config/api'
import RoleModal from '../components/modals/RoleModal'
import { Role } from '../types'

export default function Roles() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | undefined>()

  const { data: roles, isLoading } = useQuery({
    queryKey: ['roles', API_CONFIG.DEFAULT_TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.ROLES}?tenant_id=${API_CONFIG.DEFAULT_TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch roles')
      return response.json() as Promise<Role[]>
    }
  })

  const createMutation = useMutation({
    mutationFn: async (roleData: Partial<Role>) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.ROLES}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roleData)
      })
      if (!response.ok) throw new Error('Failed to create role')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setIsModalOpen(false)
      setSelectedRole(undefined)
    }
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Role> }) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.ROLES}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to update role')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setIsModalOpen(false)
      setSelectedRole(undefined)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (roleId: string) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.ROLES}/${roleId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete role')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
    }
  })

  const handleCreate = () => {
    setSelectedRole(undefined)
    setIsModalOpen(true)
  }

  const handleEdit = (role: Role) => {
    setSelectedRole(role)
    setIsModalOpen(true)
  }

  const handleDelete = async (roleId: string) => {
    if (window.confirm('确定要删除这个角色吗？')) {
      deleteMutation.mutate(roleId)
    }
  }

  const handleSave = (roleData: Partial<Role>) => {
    if (selectedRole) {
      updateMutation.mutate({ id: selectedRole.role_id, data: roleData })
    } else {
      createMutation.mutate(roleData)
    }
  }

  const getRoleIcon = (roleCode: string) => {
    const icons: Record<string, string> = {
      'Director': '🏥',
      'NurseManager': '👨‍⚕️',
      'Nurse': '👩‍⚕️',
      'Caregiver': '🤝',
      'Doctor': '⚕️',
      'FamilyMember': '👨‍👩‍👧'
    }
    return icons[roleCode] || '👤'
  }

  const getRoleColor = (roleCode: string) => {
    const colors: Record<string, string> = {
      'Director': 'from-purple-500 to-purple-600',
      'NurseManager': 'from-blue-500 to-blue-600',
      'Nurse': 'from-green-500 to-green-600',
      'Caregiver': 'from-yellow-500 to-yellow-600',
      'Doctor': 'from-red-500 to-red-600',
      'FamilyMember': 'from-pink-500 to-pink-600'
    }
    return colors[roleCode] || 'from-gray-500 to-gray-600'
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const systemRoles = roles?.filter(r => r.is_system) || []
  const customRoles = roles?.filter(r => !r.is_system) || []

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="w-8 h-8" />
            角色管理
          </h1>
          <p className="text-gray-600 mt-2">管理系统角色和权限配置</p>
        </div>
        <button onClick={handleCreate} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus className="w-5 h-5" />
          创建角色
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-900">{roles?.length || 0}</div>
          <div className="text-gray-600 text-sm mt-1">总角色数</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-blue-600">{systemRoles.length}</div>
          <div className="text-gray-600 text-sm mt-1">系统角色</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-green-600">{customRoles.length}</div>
          <div className="text-gray-600 text-sm mt-1">自定义角色</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-purple-600">
            {roles?.filter(r => r.is_active).length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">启用角色</div>
        </div>
      </div>

      {/* System Roles Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <UserCheck className="w-6 h-6" />
          系统预置角色
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systemRoles.map((role) => (
            <div
              key={role.role_id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition"
            >
              <div className={`h-2 bg-gradient-to-r ${getRoleColor(role.role_code)}`}></div>
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">{getRoleIcon(role.role_code)}</div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{role.display_name}</h3>
                      <p className="text-sm text-gray-500">{role.role_code}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleEdit(role)} className="p-2 text-gray-400 hover:text-blue-600 transition" title="编辑">
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {role.description || '系统预置角色'}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full flex items-center gap-1">
                      <Shield className="w-3 h-3" />
                      系统角色
                    </span>
                    {role.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        启用
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                        禁用
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Custom Roles Section */}
      {customRoles.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6" />
            自定义角色
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {customRoles.map((role) => (
              <div
                key={role.role_id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition"
              >
                <div className="h-2 bg-gradient-to-r from-gray-400 to-gray-500"></div>
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="text-4xl">👤</div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{role.display_name}</h3>
                        <p className="text-sm text-gray-500">{role.role_code}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEdit(role)} className="p-2 text-gray-400 hover:text-blue-600 transition" title="编辑">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(role.role_id)} className="p-2 text-gray-400 hover:text-red-600 transition" title="删除">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {role.description || '自定义角色'}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                        自定义
                      </span>
                      {role.is_active ? (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          启用
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                          禁用
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {roles?.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">暂无角色数据</p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            创建第一个角色
          </button>
        </div>
      )}

      {/* Role Modal */}
      <RoleModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedRole(undefined)
        }}
        onSave={handleSave}
        role={selectedRole}
        tenantId={API_CONFIG.DEFAULT_TENANT_ID}
      />
    </div>
  )
}
