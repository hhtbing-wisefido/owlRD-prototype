import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Users, MapPin, Tag, Save, AlertCircle, CheckCircle } from 'lucide-react'
import api from '../services/api'
import { API_CONFIG } from '../config/api'
import { usePermissions } from '../hooks/usePermissions'
import PermissionGuard from '../components/PermissionGuard'

interface User {
  user_id: string
  username: string
  email: string
  role: string
  alert_scope?: 'ALL' | 'LOCATION' | 'ASSIGNED_ONLY'
  tags?: Record<string, any>
  is_active: boolean
}

export default function PermissionSettings() {
  const queryClient = useQueryClient()
  const { isAdmin, isDirector } = usePermissions()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [alertScope, setAlertScope] = useState<string>('')
  const [tagsInput, setTagsInput] = useState<string>('')
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const TENANT_ID = API_CONFIG.DEFAULT_TENANT_ID

  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['users', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/users/?tenant_id=${TENANT_ID}`)
      return data
    },
    enabled: isAdmin || isDirector
  })

  const updatePermissionMutation = useMutation({
    mutationFn: async ({ userId, data }: { userId: string, data: Partial<User> }) => {
      await api.put(`/api/v1/users/${userId}`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setMessage({ type: 'success', text: '权限更新成功！' })
      setTimeout(() => setMessage(null), 3000)
      setSelectedUser(null)
    },
    onError: (error: any) => {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || '权限更新失败' 
      })
      setTimeout(() => setMessage(null), 5000)
    }
  })

  const handleSelectUser = (user: User) => {
    setSelectedUser(user)
    setAlertScope(user.alert_scope || 'ASSIGNED_ONLY')
    setTagsInput(user.tags ? JSON.stringify(user.tags, null, 2) : '{}')
  }

  const handleSavePermissions = () => {
    if (!selectedUser) return

    try {
      const parsedTags = tagsInput.trim() ? JSON.parse(tagsInput) : {}
      
      updatePermissionMutation.mutate({
        userId: selectedUser.user_id,
        data: {
          alert_scope: alertScope as any,
          tags: parsedTags
        }
      })
    } catch (error) {
      setMessage({ type: 'error', text: 'Tags格式错误，请输入有效的JSON' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'Admin':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'Director':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'NurseManager':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'Nurse':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'Caregiver':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <PermissionGuard 
      requires={(p) => p.isAdmin || p.isDirector}
      fallback={
        <div className="p-8 text-center">
          <AlertCircle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">权限不足</h2>
          <p className="text-gray-600">您需要Admin或Director角色才能访问权限配置</p>
        </div>
      }
    >
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            权限配置
          </h1>
          <p className="text-gray-600 mt-1">配置用户的数据访问范围和权限标签</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg border flex items-center gap-3 ${
            message.type === 'success' 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5" />
            ) : (
              <AlertCircle className="h-5 w-5" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Users className="h-5 w-5 text-gray-600" />
                  用户列表
                </h2>
              </div>
              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {isLoading ? (
                  <div className="p-8 text-center text-gray-500">加载中...</div>
                ) : users && users.length > 0 ? (
                  users.map((user) => (
                    <button
                      key={user.user_id}
                      onClick={() => handleSelectUser(user)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                        selectedUser?.user_id === user.user_id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                    >
                      <div className="font-medium text-gray-900">{user.username}</div>
                      <div className="text-sm text-gray-600">{user.email}</div>
                      <div className="mt-2 flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getRoleBadgeColor(user.role)}`}>
                          {user.role}
                        </span>
                        {user.alert_scope && (
                          <span className="px-2 py-1 bg-gray-100 border border-gray-200 rounded text-xs font-medium text-gray-700">
                            {user.alert_scope}
                          </span>
                        )}
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">暂无用户</div>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {selectedUser ? (
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">
                    配置用户权限: {selectedUser.username}
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    角色: <span className="font-medium">{selectedUser.role}</span>
                  </p>
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      数据访问范围 (Alert Scope)
                    </label>
                    <div className="space-y-3">
                      {[
                        { value: 'ALL', label: '全部数据', desc: '可以查看租户下所有数据' },
                        { value: 'LOCATION', label: '位置数据', desc: '只能查看匹配location_tag的数据' },
                        { value: 'ASSIGNED_ONLY', label: '分配数据', desc: '只能查看分配给自己的住户数据' }
                      ].map((option) => (
                        <label
                          key={option.value}
                          className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                            alertScope === option.value 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          <input
                            type="radio"
                            name="alert_scope"
                            value={option.value}
                            checked={alertScope === option.value}
                            onChange={(e) => setAlertScope(e.target.value)}
                            className="mt-1"
                          />
                          <div className="ml-3 flex-1">
                            <div className="font-medium text-gray-900">{option.label}</div>
                            <div className="text-sm text-gray-600 mt-1">{option.desc}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
                      <Tag className="h-4 w-4" />
                      权限标签 (Tags)
                    </label>
                    <textarea
                      value={tagsInput}
                      onChange={(e) => setTagsInput(e.target.value)}
                      placeholder='{"region": "A院区主楼"}'
                      rows={6}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <button
                      onClick={() => setSelectedUser(null)}
                      className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      取消
                    </button>
                    <button
                      onClick={handleSavePermissions}
                      disabled={updatePermissionMutation.isPending}
                      className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Save className="h-4 w-4" />
                      {updatePermissionMutation.isPending ? '保存中...' : '保存权限'}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">选择用户</h3>
                <p className="text-gray-600">从左侧列表选择一个用户开始配置权限</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </PermissionGuard>
  )
}
