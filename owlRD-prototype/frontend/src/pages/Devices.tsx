import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Radio, Plus, Edit2, Trash2, Circle } from 'lucide-react'
import { API_CONFIG, API_ENDPOINTS } from '../config/api'
import DeviceModal from '../components/modals/DeviceModal'
import { Device } from '../types'

export default function Devices() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedDevice, setSelectedDevice] = useState<Device | undefined>()

  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices', API_CONFIG.DEFAULT_TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DEVICES}?tenant_id=${API_CONFIG.DEFAULT_TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch devices')
      return response.json() as Promise<Device[]>
    }
  })

  const createMutation = useMutation({
    mutationFn: async (deviceData: Partial<Device>) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DEVICES}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deviceData)
      })
      if (!response.ok) throw new Error('Failed to create device')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] })
      setIsModalOpen(false)
      setSelectedDevice(undefined)
    }
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Device> }) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DEVICES}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to update device')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] })
      setIsModalOpen(false)
      setSelectedDevice(undefined)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (deviceId: string) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DEVICES}/${deviceId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete device')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] })
    }
  })

  const handleCreate = () => {
    setSelectedDevice(undefined)
    setIsModalOpen(true)
  }

  const handleEdit = (device: Device) => {
    setSelectedDevice(device)
    setIsModalOpen(true)
  }

  const handleDelete = async (deviceId: string) => {
    if (window.confirm('确定要删除这个设备吗？')) {
      deleteMutation.mutate(deviceId)
    }
  }

  const handleSave = (deviceData: Partial<Device>) => {
    if (selectedDevice) {
      updateMutation.mutate({ id: selectedDevice.device_id, data: deviceData })
    } else {
      createMutation.mutate(deviceData)
    }
  }

  const statusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'text-green-500'
      case 'offline': return 'text-gray-400'
      case 'fault': return 'text-red-500'
      default: return 'text-yellow-500'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'offline': return 'bg-gray-100 text-gray-800'
      case 'fault': return 'bg-red-100 text-red-800'
      default: return 'bg-yellow-100 text-yellow-800'
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
            <Radio className="w-8 h-8" />
            设备管理
          </h1>
          <p className="text-gray-600 mt-2">管理IoT监测设备和呼叫设备</p>
        </div>
        <button onClick={handleCreate} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus className="w-5 h-5" />
          添加设备
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-900">{devices?.length || 0}</div>
          <div className="text-gray-600 text-sm mt-1">总设备数</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-green-600">
            {devices?.filter(d => d.status?.toLowerCase() === 'active').length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">运行中</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-600">
            {devices?.filter(d => d.status?.toLowerCase() === 'offline').length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">离线</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-red-600">
            {devices?.filter(d => d.status?.toLowerCase() === 'fault').length || 0}
          </div>
          <div className="text-gray-600 text-sm mt-1">故障</div>
        </div>
      </div>

      {/* Device Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices?.map((device) => (
          <div key={device.device_id} className="bg-white p-6 rounded-lg shadow border border-gray-200 hover:shadow-md transition">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Radio className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {device.device_name || device.device_type}
                  </h3>
                  <p className="text-sm text-gray-500">{device.device_id.slice(0, 8)}</p>
                </div>
              </div>
              <Circle className={`w-4 h-4 ${statusColor(device.status)} fill-current`} />
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">类型</span>
                <span className="text-gray-900">{device.device_type}</span>
              </div>
              {device.device_model && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">型号</span>
                  <span className="text-gray-900">{device.device_model}</span>
                </div>
              )}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">状态</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(device.status)}`}>
                  {device.status}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-4 border-t">
              <button onClick={() => handleEdit(device)} className="p-2 text-gray-400 hover:text-blue-600 transition" title="编辑">
                <Edit2 className="w-4 h-4" />
              </button>
              <button onClick={() => handleDelete(device.device_id)} className="p-2 text-gray-400 hover:text-red-600 transition" title="删除">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {(!devices || devices.length === 0) && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Radio className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">暂无设备数据</p>
          <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            添加第一个设备
          </button>
        </div>
      )}

      {/* Device Modal */}
      <DeviceModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedDevice(undefined)
        }}
        onSave={handleSave}
        device={selectedDevice}
        tenantId={API_CONFIG.DEFAULT_TENANT_ID}
      />
    </div>
  )
}
