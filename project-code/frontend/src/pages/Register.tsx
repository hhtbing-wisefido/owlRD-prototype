import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UserPlus, AlertCircle } from 'lucide-react'
import FormInput from '../components/forms/FormInput'
import FormSelect from '../components/forms/FormSelect'
import { API_CONFIG, API_ENDPOINTS } from '../config/api'

const TENANT_ID = '10000000-0000-0000-0000-000000000001' // 示例租户ID

export default function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    role: 'Nurse'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // 验证密码匹配
    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    // 验证密码强度
    if (formData.password.length < 6) {
      setError('密码至少需要6位')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.REGISTER}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          phone: formData.phone || null,
          role: formData.role,
          tenant_id: TENANT_ID
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '注册失败')
      }

      const data = await response.json()

      // 存储token和用户信息
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      // 跳转到仪表板
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const roleOptions = [
    { value: 'Director', label: '院长/主管' },
    { value: 'NurseManager', label: '护士长' },
    { value: 'Nurse', label: '护士' },
    { value: 'Caregiver', label: '护理员' },
    { value: 'Doctor', label: '医生' },
    { value: 'FamilyMember', label: '家属' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">owlRD 智慧养老</h1>
          <p className="text-gray-600">创建新账号</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleSubmit}>
          <FormInput
            label="用户名"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="请输入用户名"
            required
            disabled={loading}
          />

          <FormInput
            label="邮箱"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="请输入邮箱"
            required
            disabled={loading}
          />

          <FormInput
            label="手机号"
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            placeholder="请输入手机号（可选）"
            disabled={loading}
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

          <FormInput
            label="密码"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="请输入密码（至少6位）"
            required
            disabled={loading}
          />

          <FormInput
            label="确认密码"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="请再次输入密码"
            required
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading}
            className={`
              w-full flex items-center justify-center gap-2 px-4 py-3 
              bg-blue-600 text-white rounded-lg font-medium
              transition duration-200
              ${loading 
                ? 'opacity-50 cursor-not-allowed' 
                : 'hover:bg-blue-700 active:scale-95'
              }
            `}
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>注册中...</span>
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                <span>注册</span>
              </>
            )}
          </button>
        </form>

        {/* Login Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            已有账号？
            <Link to="/login" className="text-blue-600 hover:text-blue-800 ml-1">
              立即登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
