import { useQuery } from '@tanstack/react-query'
import { User } from 'lucide-react'
import api from '../services/api'
import type { Resident } from '../types'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Residents() {
  const { data: residents, isLoading } = useQuery({
    queryKey: ['residents'],
    queryFn: async () => {
      const { data } = await api.get<Resident[]>(`/api/v1/residents?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">住户管理</h1>

      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              住户列表 ({residents?.length || 0})
            </h2>
          </div>
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
                  联系人
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  入住日期
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {residents?.map((resident) => (
                <tr key={resident.resident_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <User className="h-6 w-6 text-gray-500" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {resident.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {resident.anonymous_display_name}
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
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{resident.primary_contact_name}</div>
                    <div className="text-sm text-gray-500">{resident.primary_contact_phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {resident.admission_date}
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
    </div>
  )
}
