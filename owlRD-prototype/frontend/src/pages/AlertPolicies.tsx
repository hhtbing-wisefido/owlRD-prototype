import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Plus, Edit2, Trash2, ToggleLeft, ToggleRight, AlertTriangle } from 'lucide-react'
import api from '../services/api'
import { API_CONFIG } from '../config/api'

interface AlertPolicy {
  policy_id: string
  tenant_id: string
  policy_name: string
  alert_type: string
  severity_threshold: string
  is_enabled: boolean
  conditions: any
  actions: any
  created_at: string
  updated_at: string
}

export default function AlertPolicies() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedPolicy, setSelectedPolicy] = useState<AlertPolicy | null>(null)
  const queryClient = useQueryClient()
  const TENANT_ID = API_CONFIG.DEFAULT_TENANT_ID

  // 获取告警策略列表
  const { data: policies, isLoading } = useQuery<AlertPolicy[]>({
    queryKey: ['alert-policies', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/alert-policies/?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 启用/禁用策略
  const togglePolicyMutation = useMutation({
    mutationFn: async ({ policyId, enabled }: { policyId: string; enabled: boolean }) => {
      await api.put(`/api/v1/alert-policies/${policyId}`, { is_enabled: enabled })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-policies'] })
    },
  })

  // 删除策略
  const deletePolicyMutation = useMutation({
    mutationFn: async (policyId: string) => {
      await api.delete(`/api/v1/alert-policies/${policyId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-policies'] })
    },
  })

  // 获取严重程度样式
  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'L1':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'L2':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'L3':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'L5':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            告警规则配置
          </h1>
          <p className="text-gray-600 mt-1">配置告警触发条件和响应策略</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="h-5 w-5" />
          创建策略
        </button>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">总策略数</p>
          <p className="text-2xl font-bold text-gray-900">{policies?.length || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">已启用</p>
          <p className="text-2xl font-bold text-green-600">
            {policies?.filter((p) => p.is_enabled).length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">已禁用</p>
          <p className="text-2xl font-bold text-gray-600">
            {policies?.filter((p) => !p.is_enabled).length || 0}
          </p>
        </div>
      </div>

      {/* 策略列表 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">策略列表</h2>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <Shield className="h-8 w-8 animate-pulse mx-auto mb-2" />
            <p>加载中...</p>
          </div>
        ) : policies && policies.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {policies.map((policy) => (
              <div key={policy.policy_id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* 策略头部 */}
                    <div className="flex items-center gap-3 mb-3">
                      <Shield className="h-6 w-6 text-blue-600" />
                      <span className="font-semibold text-gray-900 text-lg">
                        {policy.policy_name}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityStyle(
                          policy.severity_threshold
                        )}`}
                      >
                        {policy.severity_threshold}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          policy.is_enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {policy.is_enabled ? '已启用' : '已禁用'}
                      </span>
                    </div>

                    {/* 策略信息 */}
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <AlertTriangle className="h-4 w-4" />
                        <span>告警类型: {policy.alert_type}</span>
                      </div>

                      {policy.conditions && (
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">触发条件: </span>
                          <span className="text-gray-700">
                            {JSON.stringify(policy.conditions, null, 2).substring(0, 100)}...
                          </span>
                        </div>
                      )}

                      {policy.actions && (
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">响应动作: </span>
                          <span className="text-gray-700">
                            {Array.isArray(policy.actions)
                              ? policy.actions.join(', ')
                              : JSON.stringify(policy.actions)}
                          </span>
                        </div>
                      )}

                      <div className="text-xs text-gray-500 mt-2">
                        创建时间: {new Date(policy.created_at).toLocaleString('zh-CN')}
                      </div>
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => setSelectedPolicy(policy)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="编辑"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() =>
                        togglePolicyMutation.mutate({
                          policyId: policy.policy_id,
                          enabled: !policy.is_enabled,
                        })
                      }
                      className={`p-2 rounded transition-colors ${
                        policy.is_enabled
                          ? 'text-orange-600 hover:bg-orange-50'
                          : 'text-green-600 hover:bg-green-50'
                      }`}
                      title={policy.is_enabled ? '禁用' : '启用'}
                    >
                      {policy.is_enabled ? (
                        <ToggleRight className="h-5 w-5" />
                      ) : (
                        <ToggleLeft className="h-5 w-5" />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        if (confirm('确定要删除这个策略吗？')) {
                          deletePolicyMutation.mutate(policy.policy_id)
                        }
                      }}
                      className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                      title="删除"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <Shield className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium">暂无告警策略</p>
            <p className="text-sm mt-1">点击右上角"创建策略"按钮开始</p>
          </div>
        )}
      </div>

      {/* 策略编辑/创建弹窗 */}
      {(showCreateModal || selectedPolicy) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  {selectedPolicy ? '编辑策略' : '创建策略'}
                </h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setSelectedPolicy(null)
                  }}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <Plus className="h-5 w-5 rotate-45" />
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="text-center py-8">
                <Shield className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">策略配置表单</h3>
                <p className="text-gray-600 mb-6">
                  策略创建和编辑表单需要配合完整的表单组件实现。
                  <br />
                  当前版本请使用API直接创建或通过系统自动创建。
                </p>
                <div className="space-y-2 text-left bg-gray-50 p-4 rounded">
                  <p className="text-sm font-medium text-gray-700">策略字段说明：</p>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                    <li>policy_name: 策略名称</li>
                    <li>alert_type: 告警类型 (vital_signs, fall, etc.)</li>
                    <li>severity_threshold: 严重程度 (L1/L2/L3/L5)</li>
                    <li>conditions: 触发条件 (JSON格式)</li>
                    <li>actions: 响应动作 (notify, escalate, etc.)</li>
                    <li>is_enabled: 是否启用</li>
                  </ul>
                </div>
                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setSelectedPolicy(null)
                  }}
                  className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 底部说明 */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">策略说明</p>
            <ul className="mt-2 space-y-1 list-disc list-inside">
              <li>L1(紧急): 心率&lt;44或&gt;116，呼吸率&lt;7或&gt;27 - 立即通知所有人</li>
              <li>L2(警报): 心率45-54或96-115，呼吸率8-9或24-26 - 通知相关人员</li>
              <li>L3(严重): 需要关注的异常值 - 记录并监控</li>
              <li>L5(警告): 预警信息 - 可选通知</li>
              <li>策略按优先级顺序评估，匹配到第一个有效策略即停止</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
