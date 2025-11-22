import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { Location } from '@/types'

interface LocationModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (location: Partial<Location>) => void
  location?: Location
  tenantId: string
}

export default function LocationModal({ isOpen, onClose, onSave, location, tenantId }: LocationModalProps) {
  const [formData, setFormData] = useState<Partial<Location>>({
    tenant_id: tenantId,
    location_name: '',
    door_number: '',
    location_type: 'HomeCare',
    is_public_space: false,
    is_multi_person_room: false,
    timezone: 'Asia/Shanghai',
    is_active: true
  })

  useEffect(() => {
    if (location) {
      setFormData(location)
    } else {
      setFormData({
        tenant_id: tenantId,
        location_name: '',
        door_number: '',
        location_type: 'HomeCare',
        is_public_space: false,
        is_multi_person_room: false,
        timezone: 'Asia/Shanghai',
        is_active: true
      })
    }
  }, [location, tenantId])

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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold">{location ? '编辑位置' : '创建位置'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">位置名称</label>
              <input
                type="text"
                name="location_name"
                value={formData.location_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">门牌号</label>
              <input
                type="text"
                name="door_number"
                value={formData.door_number || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">建筑</label>
              <input
                type="text"
                name="building"
                value={formData.building || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">楼层</label>
              <input
                type="text"
                name="floor"
                value={formData.floor || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">位置类型</label>
              <select
                name="location_type"
                value={formData.location_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="HomeCare">居家</option>
                <option value="Facility">机构</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">标签</label>
              <input
                type="text"
                name="location_tag"
                value={formData.location_tag || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="col-span-2 flex gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_public_space"
                  checked={formData.is_public_space}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">公共空间</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_multi_person_room"
                  checked={formData.is_multi_person_room}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">多人房间</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">激活</span>
              </label>
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
              {location ? '保存' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
