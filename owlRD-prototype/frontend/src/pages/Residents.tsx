import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { UserCircle, Plus, Edit2, Trash2, Tag, Heart, Activity } from 'lucide-react'
import { API_CONFIG, API_ENDPOINTS } from '../config/api'
import ResidentModal from '../components/modals/ResidentModal'
import type { Resident } from '../types'

export default function Residents() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedResident, setSelectedResident] = useState<Resident | undefined>()

  const { data: residents, isLoading } = useQuery({
    queryKey: ['residents', API_CONFIG.DEFAULT_TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.RESIDENTS}?tenant_id=${API_CONFIG.DEFAULT_TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch residents')
      return response.json() as Promise<Resident[]>
    }
  })

  const createMutation = useMutation({
    mutationFn: async (residentData: Partial<Resident>) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.RESIDENTS}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(residentData)
      })
      if (!response.ok) throw new Error('Failed to create resident')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['residents'] })
      setIsModalOpen(false)
      setSelectedResident(undefined)
    }
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Resident> }) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.RESIDENTS}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to update resident')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['residents'] })
      setIsModalOpen(false)
      setSelectedResident(undefined)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (residentId: string) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.RESIDENTS}/${residentId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete resident')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['residents'] })
    }
  })

  const handleCreate = () => {
    setSelectedResident(undefined)
    setIsModalOpen(true)
  }

  const handleEdit = (resident: Resident) => {
    setSelectedResident(resident)
    setIsModalOpen(true)
  }

  const handleDelete = async (residentId: string) => {
    if (window.confirm('确定要删除这个住户吗？')) {
      deleteMutation.mutate(residentId)
    }
  }

  const handleSave = (residentData: Partial<Resident>) => {
    if (selectedResident) {
      updateMutation.mutate({ id: selectedResident.resident_id, data: residentData })
    } else {
      createMutation.mutate(residentData)
    }
  }

  if (isLoading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <UserCircle className="w-8 h-8" />
            住户管理
          </h1>
          <p className="text-gray-600 mt-2">管理住户信息和护理记录</p>
        </div>
        <button onClick={handleCreate} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus className="w-5 h-5" />
          添加住户
        </button>
      </div>

      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            住户列表 ({residents?.length || 0})
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  住户信息
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  账号
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  健康标签
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  联系人
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  入住日期
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {residents?.map((resident) => (
                <tr key={resident.resident_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <UserCircle className="h-6 w-6 text-gray-500" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {resident.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          匿名代称: {resident.last_name}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{resident.resident_account}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`
                      px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                      ${resident.status === 'active' ? 'bg-green-100 text-green-800' : ''}
                      ${resident.status === 'discharged' ? 'bg-gray-100 text-gray-800' : ''}
                    `}>
                      {resident.status === 'active' ? '在院' : '已出院'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {(resident as any).health_tags && (resident as any).health_tags.length > 0 ? (
                        (resident as any).health_tags.map((tag: string, index: number) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-300"
                          >
                            <Tag className="h-3 w-3 mr-1" />
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm text-gray-400 flex items-center gap-1">
                          <Activity className="h-4 w-4" />
                          无标签
                        </span>
                      )}
                    </div>
                    {(resident as any).snomed_codes && (resident as any).snomed_codes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {(resident as any).snomed_codes.slice(0, 2).map((code: any, index: number) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-300"
                            title={code.display || code.code}
                          >
                            <Heart className="h-3 w-3 mr-1" />
                            SNOMED: {code.code}
                          </span>
                        ))}
                        {(resident as any).snomed_codes.length > 2 && (
                          <span className="text-xs text-gray-500">
                            +{(resident as any).snomed_codes.length - 2} 更多
                          </span>
                        )}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {resident.family_tag || '-'}
                    </div>
                    <div className="text-sm text-gray-500">
                      {resident.HIS_resident_id || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {resident.admission_date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => handleEdit(resident)} className="text-blue-600 hover:text-blue-900 transition" title="编辑">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(resident.resident_id)} className="text-red-600 hover:text-red-900 transition" title="删除">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {(!residents || residents.length === 0) && (
          <div className="text-center py-12 text-gray-500">
            暂无住户数据
          </div>
        )}
      </div>

      {/* Resident Modal */}
      <ResidentModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedResident(undefined)
        }}
        onSave={handleSave}
        resident={selectedResident}
        tenantId={API_CONFIG.DEFAULT_TENANT_ID}
      />
    </div>
  )
}
