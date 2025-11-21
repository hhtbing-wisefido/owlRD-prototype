import { useQuery } from '@tanstack/react-query'
import { Shield, UserCheck, AlertCircle, Edit2, Trash2, Plus } from 'lucide-react'

interface Role {
  role_id: string
  tenant_id: string
  role_code: string
  display_name: string
  description?: string
  is_system: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Roles() {
  const { data: roles, isLoading } = useQuery({
    queryKey: ['roles', TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/roles?tenant_id=${TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch roles')
      return response.json() as Promise<Role[]>
    }
  })

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
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
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
                    <button className="p-2 text-gray-400 hover:text-blue-600 transition">
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
                      <button className="p-2 text-gray-400 hover:text-blue-600 transition">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-red-600 transition">
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
    </div>
  )
}
