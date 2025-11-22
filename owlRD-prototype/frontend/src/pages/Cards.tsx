import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CreditCard,
  Plus,
  Edit2,
  Trash2,
  Check,
  X,
  Radio,
  User,
  MapPin,
  AlertCircle,
} from 'lucide-react'
import api from '../services/api'
import { API_CONFIG } from '../config/api'

interface Card {
  card_id: string
  tenant_id: string
  resident_id?: string
  device_id: string
  location_id: string
  card_type: 'private' | 'public'
  status: 'active' | 'inactive' | 'suspended'
  priority: number
  tags?: Record<string, any>
  created_at: string
  updated_at: string
}

interface CardFunction {
  function_id: string
  card_id: string
  function_name: string
  function_type: string
  is_enabled: boolean
  created_at: string
}

export default function Cards() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedCard, setSelectedCard] = useState<Card | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const queryClient = useQueryClient()
  const TENANT_ID = API_CONFIG.DEFAULT_TENANT_ID

  // 获取卡片列表
  const { data: cards, isLoading } = useQuery<Card[]>({
    queryKey: ['cards', TENANT_ID, statusFilter],
    queryFn: async () => {
      let url = `/api/v1/cards/?tenant_id=${TENANT_ID}`
      if (statusFilter !== 'all') {
        url += `&status=${statusFilter}`
      }
      const { data } = await api.get(url)
      return data
    },
  })

  // 获取住户列表
  const { data: residents } = useQuery({
    queryKey: ['residents', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/residents/?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 获取设备列表
  const { data: devices } = useQuery({
    queryKey: ['devices', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/devices/?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 获取位置列表
  const { data: locations } = useQuery({
    queryKey: ['locations', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/locations/?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 获取选中卡片的功能列表
  const { data: cardFunctions } = useQuery<CardFunction[]>({
    queryKey: ['card-functions', selectedCard?.card_id],
    queryFn: async () => {
      if (!selectedCard) return []
      const { data } = await api.get(`/api/v1/card-functions/?card_id=${selectedCard.card_id}`)
      return data
    },
    enabled: !!selectedCard,
  })

  // 删除卡片
  const deleteCardMutation = useMutation({
    mutationFn: async (cardId: string) => {
      await api.delete(`/api/v1/cards/${cardId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] })
    },
  })

  // 更新卡片状态
  const updateCardStatusMutation = useMutation({
    mutationFn: async ({ cardId, status }: { cardId: string; status: string }) => {
      await api.put(`/api/v1/cards/${cardId}`, { status })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] })
    },
  })

  // 执行卡片功能
  const executeFunctionMutation = useMutation({
    mutationFn: async ({ functionId, payload }: { functionId: string; payload?: any }) => {
      await api.post(`/api/v1/card-functions/${functionId}/execute`, payload || {})
    },
    onSuccess: () => {
      alert('功能执行成功')
    },
  })

  // 获取卡片类型标签样式
  const getCardTypeStyle = (type: string) => {
    return type === 'private'
      ? 'bg-blue-100 text-blue-800 border-blue-300'
      : 'bg-green-100 text-green-800 border-green-300'
  }

  // 获取状态标签样式
  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'inactive':
        return 'bg-gray-100 text-gray-800 border-gray-300'
      case 'suspended':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  // 获取住户姓名
  const getResidentName = (residentId?: string) => {
    if (!residentId || !residents) return '--'
    const resident = residents.find((r: any) => r.resident_id === residentId)
    return resident ? resident.last_name : residentId.substring(0, 8)
  }

  // 获取设备名称
  const getDeviceName = (deviceId: string) => {
    if (!devices) return deviceId.substring(0, 8)
    const device = devices.find((d: any) => d.device_id === deviceId)
    return device?.device_name || deviceId.substring(0, 8)
  }

  // 获取位置名称
  const getLocationName = (locationId: string) => {
    if (!locations) return locationId.substring(0, 8)
    const location = locations.find((l: any) => l.location_id === locationId)
    return location?.location_name || locationId.substring(0, 8)
  }

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <CreditCard className="h-8 w-8 text-blue-600" />
            卡片管理
          </h1>
          <p className="text-gray-600 mt-1">设备绑定与告警路由配置</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="h-5 w-5" />
          创建卡片
        </button>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">总卡片数</p>
          <p className="text-2xl font-bold text-gray-900">{cards?.length || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">活跃卡片</p>
          <p className="text-2xl font-bold text-green-600">
            {cards?.filter((c) => c.status === 'active').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">私人卡片</p>
          <p className="text-2xl font-bold text-blue-600">
            {cards?.filter((c) => c.card_type === 'private').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">公共卡片</p>
          <p className="text-2xl font-bold text-purple-600">
            {cards?.filter((c) => c.card_type === 'public').length || 0}
          </p>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">状态筛选:</label>
          <div className="flex gap-2">
            {['all', 'active', 'inactive', 'suspended'].map((status) => (
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
                  : status === 'active'
                  ? '活跃'
                  : status === 'inactive'
                  ? '停用'
                  : '暂停'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 卡片列表 */}
      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <CreditCard className="h-8 w-8 animate-pulse mx-auto mb-2" />
            <p>加载中...</p>
          </div>
        ) : cards && cards.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {cards.map((card) => (
              <div key={card.card_id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* 卡片头部 */}
                    <div className="flex items-center gap-3 mb-3">
                      <CreditCard className="h-6 w-6 text-blue-600" />
                      <span className="font-semibold text-gray-900">
                        卡片 #{card.card_id.substring(0, 8)}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium border ${getCardTypeStyle(
                          card.card_type
                        )}`}
                      >
                        {card.card_type === 'private' ? '私人' : '公共'}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium border ${getStatusStyle(
                          card.status
                        )}`}
                      >
                        {card.status === 'active'
                          ? '活跃'
                          : card.status === 'inactive'
                          ? '停用'
                          : '暂停'}
                      </span>
                      <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium text-gray-700">
                        优先级: {card.priority}
                      </span>
                    </div>

                    {/* 卡片信息 */}
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <User className="h-4 w-4" />
                        <span>住户: {getResidentName(card.resident_id)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Radio className="h-4 w-4" />
                        <span>设备: {getDeviceName(card.device_id)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin className="h-4 w-4" />
                        <span>位置: {getLocationName(card.location_id)}</span>
                      </div>
                    </div>

                    {/* 创建时间 */}
                    <div className="mt-2 text-xs text-gray-500">
                      创建时间: {new Date(card.created_at).toLocaleString('zh-CN')}
                    </div>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => setSelectedCard(card)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="查看功能"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    {card.status === 'active' ? (
                      <button
                        onClick={() =>
                          updateCardStatusMutation.mutate({
                            cardId: card.card_id,
                            status: 'inactive',
                          })
                        }
                        className="p-2 text-orange-600 hover:bg-orange-50 rounded transition-colors"
                        title="停用"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    ) : (
                      <button
                        onClick={() =>
                          updateCardStatusMutation.mutate({
                            cardId: card.card_id,
                            status: 'active',
                          })
                        }
                        className="p-2 text-green-600 hover:bg-green-50 rounded transition-colors"
                        title="启用"
                      >
                        <Check className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => {
                        if (confirm('确定要删除这张卡片吗？')) {
                          deleteCardMutation.mutate(card.card_id)
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
            <CreditCard className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium">暂无卡片</p>
            <p className="text-sm mt-1">点击右上角"创建卡片"按钮开始</p>
          </div>
        )}
      </div>

      {/* 卡片功能面板 */}
      {selectedCard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  卡片功能 - {selectedCard.card_id.substring(0, 8)}
                </h2>
                <button
                  onClick={() => setSelectedCard(null)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="p-6">
              {cardFunctions && cardFunctions.length > 0 ? (
                <div className="space-y-3">
                  {cardFunctions.map((func) => (
                    <div
                      key={func.function_id}
                      className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{func.function_name}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            类型: {func.function_type}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            创建于: {new Date(func.created_at).toLocaleString('zh-CN')}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              func.is_enabled
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {func.is_enabled ? '已启用' : '已禁用'}
                          </span>
                          {func.is_enabled && (
                            <button
                              onClick={() =>
                                executeFunctionMutation.mutate({
                                  functionId: func.function_id,
                                })
                              }
                              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                            >
                              执行
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <AlertCircle className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p>此卡片暂无功能</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 创建卡片提示 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">创建卡片</h2>
              <p className="text-gray-600 mb-6">
                卡片创建功能需要配合完整的表单实现。
                <br />
                当前版本请使用API直接创建或通过系统自动创建。
              </p>
              <button
                onClick={() => setShowCreateModal(false)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 底部说明 */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">卡片说明</p>
            <ul className="mt-2 space-y-1 list-disc list-inside">
              <li>私人卡片: 绑定特定住户，接收该住户的所有告警</li>
              <li>公共卡片: 绑定公共空间设备，接收区域告警</li>
              <li>优先级决定告警路由顺序，数字越小优先级越高</li>
              <li>卡片功能可以定制特定操作（如确认、升级、转发等）</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
