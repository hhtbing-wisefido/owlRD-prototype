import { useState } from 'react'
import FormInput from './FormInput'
import FormSelect from './FormSelect'

interface UserFormData {
  username: string
  email: string
  phone?: string
  role: string
  alert_levels: string[]
  alert_channels: string[]
}

interface UserFormProps {
  initialData?: Partial<UserFormData>
  onSubmit: (data: UserFormData) => Promise<void>
  onCancel: () => void
  isEdit?: boolean
}

export default function UserForm({
  initialData,
  onSubmit,
  onCancel,
  isEdit = false
}: UserFormProps) {
  const [formData, setFormData] = useState<UserFormData>({
    username: initialData?.username || '',
    email: initialData?.email || '',
    phone: initialData?.phone || '',
    role: initialData?.role || 'Nurse',
    alert_levels: initialData?.alert_levels || ['L1', 'L2'],
    alert_channels: initialData?.alert_channels || ['WEB', 'APP']
  })
  
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const roleOptions = [
    { value: 'Director', label: '院长/主管' },
    { value: 'NurseManager', label: '护士长' },
    { value: 'Nurse', label: '护士' },
    { value: 'Caregiver', label: '护理员' },
    { value: 'Doctor', label: '医生' },
    { value: 'FamilyMember', label: '家属' }
  ]

  const alertLevelOptions = [
    { value: 'L1', label: '一级告警' },
    { value: 'L2', label: '二级告警' }
  ]

  const alertChannelOptions = [
    { value: 'WEB', label: 'Web端' },
    { value: 'APP', label: '移动端' },
    { value: 'SMS', label: '短信' },
    { value: 'WECHAT', label: '微信' }
  ]

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // 清除该字段的错误
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' })
    }
  }

  const handleMultiSelectChange = (field: string, value: string) => {
    const currentValues = formData[field as keyof UserFormData] as string[]
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value]
    
    setFormData({
      ...formData,
      [field]: newValues
    })
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.username.trim()) {
      newErrors.username = '用户名不能为空'
    } else if (formData.username.length < 3) {
      newErrors.username = '用户名至少3个字符'
    }

    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确'
    }

    if (formData.phone && !/^1[3-9]\d{9}$/.test(formData.phone)) {
      newErrors.phone = '手机号格式不正确'
    }

    if (formData.alert_levels.length === 0) {
      newErrors.alert_levels = '至少选择一个告警级别'
    }

    if (formData.alert_channels.length === 0) {
      newErrors.alert_channels = '至少选择一个告警渠道'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validate()) {
      return
    }

    setLoading(true)
    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormInput
        label="用户名"
        name="username"
        value={formData.username}
        onChange={handleChange}
        error={errors.username}
        required
        disabled={loading || isEdit}
        helperText={isEdit ? "用户名不可修改" : undefined}
      />

      <FormInput
        label="邮箱"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
        required
        disabled={loading}
      />

      <FormInput
        label="手机号"
        name="phone"
        type="tel"
        value={formData.phone || ''}
        onChange={handleChange}
        error={errors.phone}
        disabled={loading}
        helperText="可选，用于接收告警短信"
      />

      <FormSelect
        label="角色"
        name="role"
        value={formData.role}
        onChange={handleChange}
        options={roleOptions}
        required
        disabled={loading}
      />

      {/* Alert Levels Multi-Select */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          告警级别 <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {alertLevelOptions.map(option => (
            <label key={option.value} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.alert_levels.includes(option.value)}
                onChange={() => handleMultiSelectChange('alert_levels', option.value)}
                disabled={loading}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">{option.label}</span>
            </label>
          ))}
        </div>
        {errors.alert_levels && (
          <p className="mt-1 text-sm text-red-600">{errors.alert_levels}</p>
        )}
      </div>

      {/* Alert Channels Multi-Select */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          告警渠道 <span className="text-red-500">*</span>
        </label>
        <div className="space-y-2">
          {alertChannelOptions.map(option => (
            <label key={option.value} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.alert_channels.includes(option.value)}
                onChange={() => handleMultiSelectChange('alert_channels', option.value)}
                disabled={loading}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">{option.label}</span>
            </label>
          ))}
        </div>
        {errors.alert_channels && (
          <p className="mt-1 text-sm text-red-600">{errors.alert_channels}</p>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
        >
          取消
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
        >
          {loading && (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          )}
          <span>{isEdit ? '更新' : '创建'}</span>
        </button>
      </div>
    </form>
  )
}
