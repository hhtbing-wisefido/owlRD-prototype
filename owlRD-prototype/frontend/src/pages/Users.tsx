import { useQuery } from '@tanstack/react-query'
import { UserCircle, UserPlus, Edit2, Trash2, Shield } from 'lucide-react'

interface User {
  user_id: string
  tenant_id: string
  username?: string
  email?: string
  phone?: string
  role: string
  alert_levels?: string[]
  alert_channels?: string[]
  alert_scope?: string
  tags?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

// 模拟租户ID（实际应从上下文获取）
const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Users() {
  const { data: users, isLoading } = useQuery({
    queryKey: ['users', TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/users?tenant_id=${TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch users')
      return response.json() as Promise<User[]>
    }
  })

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      'Director': 'bg-purple-100 text-purple-800',
      'NurseManager': 'bg-blue-100 text-blue-800',
      'Nurse': 'bg-green-100 text-green-800',
      'Caregiver': 'bg-yellow-100 text-yellow-800',
      'Doctor': 'bg-red-100 text-red-800',
      'FamilyMember': 'bg-pink-100 text-pink-800'
    }
    return colors[role] || 'bg-gray-100 text-gray-800'
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <UserCircle className="w-8 h-8" />
            用户管理
          </h1>
          <p className="text-gray-600 mt-2">管理系统用户和权限配置</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <UserPlus className="w-5 h-5" />
          添加用户
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-900">{users?.length || 0}</div>
          <div className="text-gray-600 text-sm mt-1">总用户数</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-green-600">
            {users?.filter(u => u.is_active).length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">活跃用户</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-blue-600">
            {users?.filter(u => u.role === 'Nurse').length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">护士</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-purple-600">
            {users?.filter(u => u.role === 'Doctor').length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">医生</div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  用户
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  角色
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  告警设置
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  标签
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users?.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <UserCircle className="w-6 h-6 text-blue-600" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username || user.email || user.phone || '未命名用户'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {user.email || user.phone || 'ID: ' + user.user_id.substring(0, 8)}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {user.alert_levels?.join(', ') || '未设置'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {user.alert_scope || 'ALL'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {user.tags?.slice(0, 2).map((tag, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          {tag}
                        </span>
                      ))}
                      {(user.tags?.length || 0) > 2 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          +{(user.tags?.length || 0) - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.is_active ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        活跃
                      </span>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        禁用
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button className="text-blue-600 hover:text-blue-900 transition">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button className="text-purple-600 hover:text-purple-900 transition">
                        <Shield className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900 transition">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {users?.length === 0 && (
        <div className="text-center py-12">
          <UserCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">暂无用户数据</p>
        </div>
      )}
    </div>
  )
}
