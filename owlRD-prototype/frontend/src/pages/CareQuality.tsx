import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Users, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1']

export default function CareQuality() {
  // Fetch care quality report
  const { data: report, isLoading } = useQuery({
    queryKey: ['care-quality'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/care-quality/report?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  // Mock data for demonstration
  const qualityScore = report?.quality_score || 85
  const responseData = [
    { name: '周一', 响应时间: 45, 达标率: 92 },
    { name: '周二', 响应时间: 38, 达标率: 95 },
    { name: '周三', 响应时间: 52, 达标率: 88 },
    { name: '周四', 响应时间: 42, 达标率: 93 },
    { name: '周五', 响应时间: 48, 达标率: 90 },
    { name: '周六', 响应时间: 55, 达标率: 85 },
    { name: '周日', 响应时间: 50, 达标率: 87 },
  ]

  const coverageData = [
    { name: '有效护理', value: 75 },
    { name: '无效走动', value: 15 },
    { name: '休息时间', value: 10 },
  ]

  const teamPerformance = [
    { shift: '早班', 覆盖率: 85, 响应率: 92, 质量分: 88 },
    { shift: '中班', 覆盖率: 78, 响应率: 88, 质量分: 82 },
    { shift: '晚班', 覆盖率: 82, 响应率: 90, 质量分: 86 },
  ]

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 90) return <CheckCircle className="w-8 h-8 text-green-600" />
    if (score >= 70) return <AlertTriangle className="w-8 h-8 text-yellow-600" />
    return <XCircle className="w-8 h-8 text-red-600" />
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">护理质量评估</h1>

      {/* Quality Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">总体质量评分</h3>
            {getScoreIcon(qualityScore)}
          </div>
          <div className={`text-3xl font-bold ${getScoreColor(qualityScore)}`}>
            {qualityScore}分
          </div>
          <p className="text-xs text-gray-500 mt-2">较上周 +3.2%</p>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">平均响应时间</h3>
            <Clock className="w-8 h-8 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">45秒</div>
          <p className="text-xs text-gray-500 mt-2">目标: &lt;60秒</p>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">房间覆盖率</h3>
            <Users className="w-8 h-8 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">92%</div>
          <p className="text-xs text-gray-500 mt-2">58/63 房间</p>
        </div>

        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">告警处理率</h3>
            <TrendingUp className="w-8 h-8 text-purple-600" />
          </div>
          <div className="text-3xl font-bold text-gray-900">96%</div>
          <p className="text-xs text-gray-500 mt-2">153/159 处理</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Response Time Trend */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">响应时间趋势</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={responseData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" label={{ value: '秒', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: '%', angle: 90, position: 'insideRight' }} />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="响应时间" stroke="#3b82f6" strokeWidth={2} />
              <Line yAxisId="right" type="monotone" dataKey="达标率" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Coverage Distribution */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">护理时间分布</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={coverageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {coverageData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Team Performance */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">班次效率对比</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={teamPerformance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="shift" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="覆盖率" fill="#3b82f6" />
            <Bar dataKey="响应率" fill="#10b981" />
            <Bar dataKey="质量分" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Improvement Suggestions */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">改进建议</h3>
        <ul className="space-y-3">
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 mt-2 bg-blue-600 rounded-full"></div>
            </div>
            <p className="ml-3 text-sm text-gray-700">
              <strong>周末覆盖不足：</strong>建议增加周末护理人员配置，提高房间覆盖率
            </p>
          </li>
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 mt-2 bg-green-600 rounded-full"></div>
            </div>
            <p className="ml-3 text-sm text-gray-700">
              <strong>响应时间优化：</strong>平均响应时间已达标，继续保持当前服务水平
            </p>
          </li>
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 mt-2 bg-yellow-600 rounded-full"></div>
            </div>
            <p className="ml-3 text-sm text-gray-700">
              <strong>中班效率提升：</strong>中班质量评分偏低，建议加强培训和支持
            </p>
          </li>
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 mt-2 bg-purple-600 rounded-full"></div>
            </div>
            <p className="ml-3 text-sm text-gray-700">
              <strong>减少无效走动：</strong>优化护理路线规划，减少15%的无效走动时间
            </p>
          </li>
        </ul>
      </div>
    </div>
  )
}
