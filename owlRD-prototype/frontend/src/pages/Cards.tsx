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
  bed_id?: string
  location_id?: string
  card_type: 'ActiveBed' | 'Location'
  card_name?: string
  card_address?: string
  is_active: boolean
  is_public_space?: boolean
  routing_alert_user_ids?: string[]
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
  const [typeFilter, setTypeFilter] = useState<string>('all')

  const queryClient = useQueryClient()
  const TENANT_ID = API_CONFIG.DEFAULT_TENANT_ID

  // 获取卡片列表
  const { data: cards, isLoading } = useQuery<Card[]>({
    queryKey: ['cards', TENANT_ID, statusFilter, typeFilter],
    queryFn: async () => {
      let url = `/api/v1/cards/?tenant_id=${TENANT_ID}`
      if (statusFilter === 'active') {
        url += `&is_active=true`
      } else if (statusFilter === 'inactive') {
        url += `&is_active=false`
      }
      if (typeFilter !== 'all') {
        url += `&card_type=${typeFilter}`
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

  // 创建卡片
  const createCardMutation = useMutation({
    mutationFn: async (cardData: any) => {
      await api.post('/api/v1/cards/', cardData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] })
      setShowCreateModal(false)
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

  // 获取住户姓名
  const getResidentName = (residentId?: string) => {
    if (!residentId || !residents) return '--'
    const resident = residents.find((r: any) => r.resident_id === residentId)
    return resident ? resident.last_name : residentId.substring(0, 8)
  }

  // 获取位置名称
  const getLocationName = (locationId?: string) => {
    if (!locationId) return '--'
    if (!locations) return locationId.substring(0, 8)
    const location = locations.find((l: any) => l.location_id === locationId)
    return location?.location_name || locationId.substring(0, 8)
  }

  // 获取床位名称
  const getBedName = (bedId?: string) => {
    if (!bedId) return '--'
    return bedId.substring(0, 8)
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
            {cards?.filter((c) => c.is_active).length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">床位卡片</p>
          <p className="text-2xl font-bold text-blue-600">
            {cards?.filter((c) => c.card_type === 'ActiveBed').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">位置卡片</p>
          <p className="text-2xl font-bold text-purple-600">
            {cards?.filter((c) => c.card_type === 'Location').length || 0}
          </p>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">状态筛选:</label>
            <div className="flex gap-2">
              {['all', 'active', 'inactive'].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    statusFilter === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status === 'all' ? '全部' : status === 'active' ? '活跃' : '停用'}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700">类型筛选:</label>
            <div className="flex gap-2">
              {['all', 'ActiveBed', 'Location'].map((type) => (
                <button
                  key={type}
                  onClick={() => setTypeFilter(type)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    typeFilter === type
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {type === 'all' ? '全部' : type === 'ActiveBed' ? '床位' : '位置'}
                </button>
              ))}
            </div>
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
                        {card.card_name || `卡片 #${card.card_id.substring(0, 8)}`}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium border ${
                          card.card_type === 'ActiveBed'
                            ? 'bg-blue-50 text-blue-700 border-blue-200'
                            : 'bg-purple-50 text-purple-700 border-purple-200'
                        }`}
                      >
                        {card.card_type === 'ActiveBed' ? '床位卡片' : '位置卡片'}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium border ${
                          card.is_active
                            ? 'bg-green-50 text-green-700 border-green-200'
                            : 'bg-gray-50 text-gray-700 border-gray-200'
                        }`}
                      >
                        {card.is_active ? '活跃' : '停用'}
                      </span>
                      {card.is_public_space !== undefined && (
                        <span className="px-2 py-1 bg-yellow-50 border border-yellow-200 rounded text-xs font-medium text-yellow-700">
                          {card.is_public_space ? '公共空间' : '私人空间'}
                        </span>
                      )}
                    </div>

                    {/* 卡片信息 */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {card.card_address && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <MapPin className="h-4 w-4" />
                          <span>地址: {card.card_address}</span>
                        </div>
                      )}
                      {card.resident_id && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <User className="h-4 w-4" />
                          <span>住户: {getResidentName(card.resident_id)}</span>
                        </div>
                      )}
                      {card.bed_id && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Radio className="h-4 w-4" />
                          <span>床位: {getBedName(card.bed_id)}</span>
                        </div>
                      )}
                      {card.location_id && (
                        <div className="flex items-center gap-2 text-gray-600">
                          <MapPin className="h-4 w-4" />
                          <span>位置ID: {getLocationName(card.location_id)}</span>
                        </div>
                      )}
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
                    {card.is_active ? (
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

      {/* 创建卡片表单 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">创建卡片</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault()
                const formData = new FormData(e.currentTarget)
                const cardData = {
                  tenant_id: TENANT_ID,
                  resident_id: formData.get('resident_id') || undefined,
                  device_id: formData.get('device_id'),
                  location_id: formData.get('location_id'),
                  card_type: formData.get('card_type'),
                  priority: Number(formData.get('priority')),
                  status: 'active',
                }
                createCardMutation.mutate(cardData)
              }}
              className="p-6 space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  卡片类型 *
                </label>
                <select
                  name="card_type"
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">请选择</option>
                  <option value="private">私人卡片</option>
                  <option value="public">公共卡片</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  住户 (私人卡片必填)
                </label>
                <select
                  name="resident_id"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">无</option>
                  {residents?.map((resident: any) => (
                    <option key={resident.resident_id} value={resident.resident_id}>
                      {resident.last_name} ({resident.resident_account})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  设备 *
                </label>
                <select
                  name="device_id"
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">请选择</option>
                  {devices?.map((device: any) => (
                    <option key={device.device_id} value={device.device_id}>
                      {device.device_name || device.device_id}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  位置 *
                </label>
                <select
                  name="location_id"
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">请选择</option>
                  {locations?.map((location: any) => (
                    <option key={location.location_id} value={location.location_id}>
                      {location.location_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  优先级 *
                </label>
                <input
                  type="number"
                  name="priority"
                  defaultValue={1}
                  min={1}
                  max={100}
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="数字越小优先级越高"
                />
                <p className="text-xs text-gray-500 mt-1">
                  优先级决定告警路由顺序，数字越小优先级越高
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded transition-colors hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={createCardMutation.isPending}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50"
                >
                  {createCardMutation.isPending ? '创建中...' : '创建卡片'}
                </button>
              </div>
            </form>
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
