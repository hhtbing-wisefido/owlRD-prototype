import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import api from '../services/api'
import type { Alert } from '../types'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Alerts() {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const { data } = await api.get<Alert[]>(`/api/v1/alerts?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  const { data: stats } = useQuery({
    queryKey: ['alert-stats'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/alerts/statistics/summary?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">加载中...</div>
  }

  const levelColor = (level: string) => {
    switch (level) {
      case 'L1': return 'bg-red-100 text-red-800 border-red-200'
      case 'L2': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'L3': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'L5': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const statusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">待处理</span>
      case 'acknowledged':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">已确认</span>
      case 'resolved':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">已解决</span>
      default:
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">{status}</span>
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">告警中心</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center">
            <AlertTriangle className="w-8 h-8 text-red-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">总告警数</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-orange-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">待处理</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.by_status?.pending || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">已解决</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.by_status?.resolved || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">告警列表</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {alerts?.map((alert) => (
            <div
              key={alert.alert_id}
              className="px-6 py-4 hover:bg-gray-50"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded border ${levelColor(alert.alert_level)}`}>
                      {alert.alert_level}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{alert.alert_type}</span>
                    {statusBadge(alert.status)}
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                  <p className="text-xs text-gray-500">
                    时间: {new Date(alert.timestamp).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {(!alerts || alerts.length === 0) && (
          <div className="text-center py-12 text-gray-500">
            暂无告警数据
          </div>
        )}
      </div>
    </div>
  )
}
