import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogIn, AlertCircle } from 'lucide-react'
import FormInput from '../components/forms/FormInput'

export default function Login() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // TODO: 实现实际的登录API调用
      // const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(formData)
      // })
      
      // 模拟登录
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 简单验证（实际应该调用API）
      if (formData.username && formData.password) {
        // 存储token（模拟）
        localStorage.setItem('token', 'demo-token-' + Date.now())
        localStorage.setItem('user', JSON.stringify({
          username: formData.username,
          role: 'Admin'
        }))
        
        // 跳转到仪表板
        navigate('/dashboard')
      } else {
        setError('请输入用户名和密码')
      }
    } catch (err) {
      setError('登录失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">owlRD 智慧养老</h1>
          <p className="text-gray-600">智能监测系统</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Login Form */}
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
            label="密码"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="请输入密码"
            required
            disabled={loading}
          />

          <div className="flex items-center justify-between mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-600">记住我</span>
            </label>
            <a href="#" className="text-sm text-blue-600 hover:text-blue-800">
              忘记密码？
            </a>
          </div>

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
                <span>登录中...</span>
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>登录</span>
              </>
            )}
          </button>
        </form>

        {/* Register Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            还没有账号？
            <a href="/register" className="text-blue-600 hover:text-blue-800 ml-1">
              立即注册
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
