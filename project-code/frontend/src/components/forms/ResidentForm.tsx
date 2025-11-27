import { useState } from 'react'
import FormInput from './FormInput'
import FormSelect from './FormSelect'

interface ResidentFormData {
  last_name: string
  first_name: string
  gender: string
  date_of_birth: string
  admission_date: string
  status: string
  room_preference?: string
  dietary_restrictions?: string
  mobility_level?: string
  cognitive_level?: string
}

interface ResidentFormProps {
  initialData?: Partial<ResidentFormData>
  onSubmit: (data: ResidentFormData) => Promise<void>
  onCancel: () => void
  isEdit?: boolean
}

export default function ResidentForm({
  initialData,
  onSubmit,
  onCancel,
  isEdit = false
}: ResidentFormProps) {
  const [formData, setFormData] = useState<ResidentFormData>({
    last_name: initialData?.last_name || '',
    first_name: initialData?.first_name || '',
    gender: initialData?.gender || 'Male',
    date_of_birth: initialData?.date_of_birth || '',
    admission_date: initialData?.admission_date || new Date().toISOString().split('T')[0],
    status: initialData?.status || 'active',
    room_preference: initialData?.room_preference || '',
    dietary_restrictions: initialData?.dietary_restrictions || '',
    mobility_level: initialData?.mobility_level || 'independent',
    cognitive_level: initialData?.cognitive_level || 'normal'
  })
  
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const genderOptions = [
    { value: 'Male', label: '男' },
    { value: 'Female', label: '女' },
    { value: 'Other', label: '其他' }
  ]

  const statusOptions = [
    { value: 'active', label: '在院' },
    { value: 'discharged', label: '出院' },
    { value: 'suspended', label: '暂停' }
  ]

  const mobilityOptions = [
    { value: 'independent', label: '独立活动' },
    { value: 'assisted', label: '辅助活动' },
    { value: 'wheelchair', label: '轮椅' },
    { value: 'bedridden', label: '卧床' }
  ]

  const cognitiveOptions = [
    { value: 'normal', label: '正常' },
    { value: 'mild_impairment', label: '轻度障碍' },
    { value: 'moderate_impairment', label: '中度障碍' },
    { value: 'severe_impairment', label: '重度障碍' }
  ]

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: '' })
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.last_name.trim()) {
      newErrors.last_name = '姓氏不能为空'
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = '名字不能为空'
    }

    if (!formData.date_of_birth) {
      newErrors.date_of_birth = '出生日期不能为空'
    } else {
      const birthDate = new Date(formData.date_of_birth)
      const today = new Date()
      if (birthDate > today) {
        newErrors.date_of_birth = '出生日期不能晚于今天'
      }
    }

    if (!formData.admission_date) {
      newErrors.admission_date = '入住日期不能为空'
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
      <div className="grid grid-cols-2 gap-4">
        <FormInput
          label="姓氏"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          error={errors.last_name}
          required
          disabled={loading}
        />

        <FormInput
          label="名字"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          error={errors.first_name}
          required
          disabled={loading}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormSelect
          label="性别"
          name="gender"
          value={formData.gender}
          onChange={handleChange}
          options={genderOptions}
          required
          disabled={loading}
        />

        <FormInput
          label="出生日期"
          name="date_of_birth"
          type="date"
          value={formData.date_of_birth}
          onChange={handleChange}
          error={errors.date_of_birth}
          required
          disabled={loading}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormInput
          label="入住日期"
          name="admission_date"
          type="date"
          value={formData.admission_date}
          onChange={handleChange}
          error={errors.admission_date}
          required
          disabled={loading}
        />

        <FormSelect
          label="状态"
          name="status"
          value={formData.status}
          onChange={handleChange}
          options={statusOptions}
          required
          disabled={loading}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormSelect
          label="活动能力"
          name="mobility_level"
          value={formData.mobility_level || ''}
          onChange={handleChange}
          options={mobilityOptions}
          disabled={loading}
        />

        <FormSelect
          label="认知能力"
          name="cognitive_level"
          value={formData.cognitive_level || ''}
          onChange={handleChange}
          options={cognitiveOptions}
          disabled={loading}
        />
      </div>

      <FormInput
        label="房间偏好"
        name="room_preference"
        value={formData.room_preference || ''}
        onChange={handleChange}
        disabled={loading}
        helperText="如：朝南、靠窗等"
      />

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          饮食限制
        </label>
        <textarea
          name="dietary_restrictions"
          value={formData.dietary_restrictions || ''}
          onChange={handleChange}
          disabled={loading}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="如：无糖、低盐、过敏食物等"
        />
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
