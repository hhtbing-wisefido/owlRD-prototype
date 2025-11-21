import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { User } from '@/types'

interface UserModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (user: Partial<User>) => void
  user?: User
  tenantId: string
}

export default function UserModal({ isOpen, onClose, onSave, user, tenantId }: UserModalProps) {
  const [formData, setFormData] = useState<Partial<User>>({
    tenant_id: tenantId,
    username: '',
    email: '',
    phone: '',
    role: 'Nurse',
    alert_scope: 'ALL',
    is_active: true
  })

  useEffect(() => {
    if (user) {
      setFormData(user)
    } else {
      setFormData({
        tenant_id: tenantId,
        username: '',
        email: '',
        phone: '',
        role: 'Nurse',
        alert_scope: 'ALL',
        is_active: true
      })
    }
  }, [user, tenantId])

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
          <h2 className="text-2xl font-bold">{user ? '编辑用户' : '创建用户'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                用户名
              </label>
              <input
                type="text"
                name="username"
                value={formData.username || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                角色
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="Director">Director</option>
                <option value="NurseManager">NurseManager</option>
                <option value="Nurse">Nurse</option>
                <option value="Caregiver">Caregiver</option>
                <option value="Doctor">Doctor</option>
                <option value="FamilyMember">FamilyMember</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                邮箱
              </label>
              <input
                type="email"
                name="email"
                value={formData.email || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                电话
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                告警范围
              </label>
              <select
                name="alert_scope"
                value={formData.alert_scope}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ALL">全部</option>
                <option value="LOCATION-TAG">位置标签</option>
                <option value="ASSIGNED_ONLY">仅分配</option>
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
              <label className="ml-2 text-sm font-medium text-gray-700">
                激活状态
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
              {user ? '保存' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
