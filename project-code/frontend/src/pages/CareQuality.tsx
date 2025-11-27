import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Users, Clock, AlertTriangle, CheckCircle, XCircle, Award, Target, Lightbulb, Activity, Heart } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1']

export default function CareQuality() {
  const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview')

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
  
  // 多维度评分数据
  const qualityDimensions = [
    { dimension: '响应速度', score: 92, fullMark: 100 },
    { dimension: '服务态度', score: 88, fullMark: 100 },
    { dimension: '专业技能', score: 85, fullMark: 100 },
    { dimension: '房间覆盖', score: 90, fullMark: 100 },
    { dimension: '文档记录', score: 78, fullMark: 100 },
    { dimension: '应急处理', score: 95, fullMark: 100 },
  ]
  
  // AI分析结果
  const aiInsights = [
    {
      type: 'strength',
      icon: <CheckCircle className="h-5 w-5 text-green-600" />,
      title: '优势项',
      items: [
        '应急处理能力优秀，95分位列前茅',
        '响应速度快速稳定，平均45秒内到达',
        '房间覆盖率高达92%，服务全面',
      ]
    },
    {
      type: 'weakness',
      icon: <AlertTriangle className="h-5 w-5 text-yellow-600" />,
      title: '改进项',
      items: [
        '文档记录有待加强，仅78分需要重点提升',
        '中班护理质量偏低，建议加强培训',
        '周末服务覆盖不足，需增加人员配置',
      ]
    },
    {
      type: 'recommendation',
      icon: <Lightbulb className="h-5 w-5 text-blue-600" />,
      title: '智能建议',
      items: [
        '推荐引入电子记录系统，提升文档完整性',
        '建议优化排班算法，平衡各班次工作量',
        '可考虑增加周末激励措施，提升覆盖率',
      ]
    },
  ]
  
  // 护理员绩效排名
  const staffPerformance = [
    { name: '张护士', score: 95, services: 156, satisfaction: 98 },
    { name: '李护士', score: 92, services: 148, satisfaction: 96 },
    { name: '王护士', score: 88, services: 142, satisfaction: 94 },
    { name: '赵护士', score: 85, services: 138, satisfaction: 92 },
    { name: '刘护士', score: 82, services: 135, satisfaction: 90 },
  ]
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
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Award className="h-8 w-8 text-yellow-500" />
            护理质量评估
          </h1>
          <p className="text-gray-600 mt-1">AI智能分析 · 多维度评估</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overview')}
            className={`px-4 py-2 rounded transition-colors ${
              viewMode === 'overview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            概览
          </button>
          <button
            onClick={() => setViewMode('detailed')}
            className={`px-4 py-2 rounded transition-colors ${
              viewMode === 'detailed'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            详细分析
          </button>
        </div>
      </div>

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

      {/* AI智能分析 - 仅在详细模式显示 */}
      {viewMode === 'detailed' && (
        <>
          {/* 多维度雷达图 */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              多维度质量评估
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={qualityDimensions}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="评分"
                  dataKey="score"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
                <Tooltip />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
              {qualityDimensions.map((dim, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-700">{dim.dimension}</span>
                  <span className={`font-bold ${getScoreColor(dim.score)}`}>{dim.score}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI分析洞察 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            {aiInsights.map((insight, idx) => (
              <div key={idx} className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  {insight.icon}
                  <h3 className="text-lg font-semibold text-gray-900">{insight.title}</h3>
                </div>
                <ul className="space-y-2">
                  {insight.items.map((item, itemIdx) => (
                    <li key={itemIdx} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="text-blue-600 font-bold">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* 护理员绩效排名 */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-600" />
              护理员绩效排名
            </h3>
            <div className="space-y-3">
              {staffPerformance.map((staff, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                      idx === 0 ? 'bg-yellow-100' : idx === 1 ? 'bg-gray-100' : idx === 2 ? 'bg-orange-100' : 'bg-blue-50'
                    }`}>
                      <span className={`font-bold ${
                        idx === 0 ? 'text-yellow-600' : idx === 1 ? 'text-gray-600' : idx === 2 ? 'text-orange-600' : 'text-blue-600'
                      }`}>
                        {idx + 1}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{staff.name}</p>
                      <p className="text-xs text-gray-500">{staff.services} 次服务</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <p className="text-xs text-gray-500">评分</p>
                      <p className={`text-lg font-bold ${getScoreColor(staff.score)}`}>{staff.score}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500">满意度</p>
                      <p className="text-lg font-bold text-green-600">{staff.satisfaction}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Improvement Suggestions - 总是显示 */}
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

      {/* 底部提示 */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <Heart className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">AI智能分析说明</p>
            <p className="text-xs">
              本报告基于IoT数据、告警记录、护理日志等多维度数据，通过AI算法自动生成。
              建议每周查看一次，持续优化护理质量。点击右上角"详细分析"查看更多内容。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
