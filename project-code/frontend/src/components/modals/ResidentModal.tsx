import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { Resident } from '@/types'

interface ResidentModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (resident: Partial<Resident>) => void
  resident?: Resident
  tenantId: string
}

export default function ResidentModal({ isOpen, onClose, onSave, resident, tenantId }: ResidentModalProps) {
  const [formData, setFormData] = useState<Partial<Resident>>({
    tenant_id: tenantId,
    is_institutional: true,
    anonymous_name: '',
    last_name: '',
    resident_account: '',
    status: 'active',
    can_view_status: true
  })

  useEffect(() => {
    if (resident) {
      setFormData(resident)
    } else {
      setFormData({
        tenant_id: tenantId,
        is_institutional: true,
        anonymous_name: '',
        last_name: '',
        resident_account: '',
        status: 'active',
        can_view_status: true
      })
    }
  }, [resident, tenantId])

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
          <h2 className="text-2xl font-bold">{resident ? '编辑住户' : '创建住户'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">匿名名称</label>
              <input
                type="text"
                name="anonymous_name"
                value={formData.anonymous_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">住户账号</label>
              <input
                type="text"
                name="resident_account"
                value={formData.resident_account || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">姓</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">名</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="col-span-2 flex gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_institutional"
                  checked={formData.is_institutional}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">机构照护</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="can_view_status"
                  checked={formData.can_view_status}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">可查看状态</span>
              </label>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
                <select
                  name="status"
                  value={formData.status || 'active'}
                  onChange={handleChange}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="active">活跃</option>
                  <option value="discharged">出院</option>
                  <option value="transferred">转院</option>
                </select>
              </div>
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
              {resident ? '保存' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
