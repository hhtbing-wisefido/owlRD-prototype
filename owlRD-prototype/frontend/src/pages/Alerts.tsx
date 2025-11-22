import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle, Clock, Check, X, Eye, Filter } from 'lucide-react'
import api from '../services/api'
import type { Alert } from '../types'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Alerts() {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const queryClient = useQueryClient()

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', statusFilter],
    queryFn: async () => {
      let url = `/api/v1/alerts?tenant_id=${TENANT_ID}`
      if (statusFilter !== 'all') {
        url += `&status=${statusFilter}`
      }
      const { data } = await api.get<Alert[]>(url)
      return data
    },
    refetchInterval: 10000, // 每10秒自动刷新
  })

  const { data: stats } = useQuery({
    queryKey: ['alert-stats'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/alerts/statistics/summary?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 确认告警
  const acknowledgeMutation = useMutation({
    mutationFn: async (alertId: string) => {
      await api.post(`/api/v1/alerts/${alertId}/acknowledge`, {})
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
    },
  })

  // 解决告警
  const resolveMutation = useMutation({
    mutationFn: async (alertId: string) => {
      await api.post(`/api/v1/alerts/${alertId}/resolve`, {})
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      queryClient.invalidateQueries({ queryKey: ['alert-stats'] })
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
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            告警中心
          </h1>
          <p className="text-gray-600 mt-1">实时告警监控与处理</p>
        </div>
      </div>

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

      {/* 筛选器 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-gray-600" />
          <label className="text-sm font-medium text-gray-700">状态筛选:</label>
          <div className="flex gap-2">
            {['all', 'pending', 'acknowledged', 'resolved'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all'
                  ? '全部'
                  : status === 'pending'
                  ? '待处理'
                  : status === 'acknowledged'
                  ? '已确认'
                  : '已解决'}
              </button>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4 animate-pulse text-blue-500" />
            <span>自动刷新中</span>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            告警列表 ({alerts?.length || 0})
          </h2>
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
                
                {/* 操作按钮 */}
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => setSelectedAlert(alert)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="查看详情"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  {alert.status === 'pending' && (
                    <button
                      onClick={() => acknowledgeMutation.mutate(alert.alert_id)}
                      disabled={acknowledgeMutation.isPending}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors disabled:opacity-50 flex items-center gap-1"
                      title="确认告警"
                    >
                      <Check className="h-3 w-3" />
                      确认
                    </button>
                  )}
                  {(alert.status === 'pending' || alert.status === 'acknowledged') && (
                    <button
                      onClick={() => resolveMutation.mutate(alert.alert_id)}
                      disabled={resolveMutation.isPending}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors disabled:opacity-50 flex items-center gap-1"
                      title="解决告警"
                    >
                      <CheckCircle className="h-3 w-3" />
                      解决
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {(!alerts || alerts.length === 0) && (
          <div className="text-center py-12 text-gray-500">
            <AlertTriangle className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium">暂无告警数据</p>
            <p className="text-sm mt-1">系统运行正常</p>
          </div>
        )}
      </div>

      {/* 告警详情弹窗 */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">告警详情</h2>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-600">告警级别</label>
                <div className="mt-1">
                  <span className={`px-3 py-1 text-sm font-medium rounded border ${levelColor(selectedAlert.alert_level)}`}>
                    {selectedAlert.alert_level}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">告警类型</label>
                <p className="mt-1 text-gray-900">{selectedAlert.alert_type}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">状态</label>
                <div className="mt-1">{statusBadge(selectedAlert.status)}</div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">告警消息</label>
                <p className="mt-1 text-gray-900">{selectedAlert.message}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">触发时间</label>
                <p className="mt-1 text-gray-900">
                  {new Date(selectedAlert.timestamp).toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </p>
              </div>

              {selectedAlert.device_id && (
                <div>
                  <label className="text-sm font-medium text-gray-600">设备ID</label>
                  <p className="mt-1 text-gray-900 font-mono text-sm">{selectedAlert.device_id}</p>
                </div>
              )}

              {selectedAlert.resident_id && (
                <div>
                  <label className="text-sm font-medium text-gray-600">住户ID</label>
                  <p className="mt-1 text-gray-900 font-mono text-sm">{selectedAlert.resident_id}</p>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                {selectedAlert.status === 'pending' && (
                  <button
                    onClick={() => {
                      acknowledgeMutation.mutate(selectedAlert.alert_id)
                      setSelectedAlert(null)
                    }}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center justify-center gap-2"
                  >
                    <Check className="h-4 w-4" />
                    确认告警
                  </button>
                )}
                {(selectedAlert.status === 'pending' || selectedAlert.status === 'acknowledged') && (
                  <button
                    onClick={() => {
                      resolveMutation.mutate(selectedAlert.alert_id)
                      setSelectedAlert(null)
                    }}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    解决告警
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
