import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

interface Device {
  device_id?: string
  tenant_id: string
  device_type: string
  device_tag?: string
  manufacturer?: string
  model?: string
  status: string
  is_active: boolean
}

interface DeviceModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (device: Partial<Device>) => void
  device?: Device
  tenantId: string
}

export default function DeviceModal({ isOpen, onClose, onSave, device, tenantId }: DeviceModalProps) {
  const [formData, setFormData] = useState<Partial<Device>>({
    tenant_id: tenantId,
    device_type: 'IoTMonitor',
    status: 'Active',
    is_active: true
  })

  useEffect(() => {
    if (device) {
      setFormData(device)
    } else {
      setFormData({
        tenant_id: tenantId,
        device_type: 'IoTMonitor',
        status: 'Active',
        is_active: true
      })
    }
  }, [device, tenantId])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold">{device ? '编辑设备' : '创建设备'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">设备类型</label>
              <select
                name="device_type"
                value={formData.device_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="IoTMonitor">IoT监测设备</option>
                <option value="CallButton">呼叫按钮</option>
                <option value="Card">卡片</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">设备标签</label>
              <input
                type="text"
                name="device_tag"
                value={formData.device_tag || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">制造商</label>
              <input
                type="text"
                name="manufacturer"
                value={formData.manufacturer || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">型号</label>
              <input
                type="text"
                name="model"
                value={formData.model || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="Active">运行中</option>
                <option value="Idle">空闲</option>
                <option value="Maintenance">维护中</option>
                <option value="Fault">故障</option>
                <option value="Offline">离线</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label className="ml-2 text-sm font-medium text-gray-700">激活状态</label>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              取消
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
            >
              {device ? '保存' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
