import { useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, Users, Radio, Activity, Wifi, WifiOff } from 'lucide-react'
import { useState } from 'react'
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'
const WS_URL = `ws://localhost:8000/api/v1/realtime/ws/${TENANT_ID}`

export default function Dashboard() {
  const queryClient = useQueryClient()
  const [realtimeAlerts, setRealtimeAlerts] = useState<any[]>([])
  
  // WebSocket connection
  const { isConnected } = useWebSocket(WS_URL, {
    onMessage: (message) => {
      if (message.type === 'alert') {
        // Add new alert to the top
        setRealtimeAlerts(prev => [message.data, ...prev].slice(0, 10))
        // Invalidate alerts query to refresh
        queryClient.invalidateQueries({ queryKey: ['alerts'] })
      } else if (message.type === 'device_status') {
        // Invalidate devices query to refresh
        queryClient.invalidateQueries({ queryKey: ['devices'] })
      }
    },
  })
  
  // Fetch residents count
  const { data: residents } = useQuery({
    queryKey: ['residents'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/residents?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // Fetch devices
  const { data: devices } = useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/devices?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // Fetch alerts
  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/alerts?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  const stats = [
    {
      name: '住户总数',
      value: residents?.length || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      name: '在线设备',
      value: devices?.filter((d: any) => d.status === 'online').length || 0,
      icon: Radio,
      color: 'bg-green-500',
    },
    {
      name: '未处理告警',
      value: alerts?.filter((a: any) => a.status === 'pending').length || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
    },
    {
      name: '护理质量',
      value: '85%',
      icon: Activity,
      color: 'bg-purple-500',
    },
  ]

  const displayAlerts = realtimeAlerts.length > 0 ? realtimeAlerts : alerts

  // Mock data for charts
  const deviceStatusData = [
    { name: '在线', value: devices?.filter((d: any) => d.status === 'online').length || 12 },
    { name: '离线', value: devices?.filter((d: any) => d.status === 'offline').length || 3 },
    { name: '维护中', value: devices?.filter((d: any) => d.status === 'maintenance').length || 2 },
  ]

  const COLORS = ['#10b981', '#ef4444', '#f59e0b']

  const alertTrendData = [
    { time: '00:00', 告警数: 2 },
    { time: '04:00', 告警数: 1 },
    { time: '08:00', 告警数: 5 },
    { time: '12:00', 告警数: 8 },
    { time: '16:00', 告警数: 12 },
    { time: '20:00', 告警数: 6 },
    { time: '23:59', 告警数: 3 },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">仪表板</h1>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <>
              <Wifi className="w-5 h-5 text-green-600" />
              <span className="text-sm text-green-600 font-medium">实时连接</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-400 font-medium">连接断开</span>
            </>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.name}
              className="bg-white rounded-lg shadow p-6 border border-gray-200"
            >
              <div className="flex items-center">
                <div className={`${stat.color} rounded-lg p-3 mr-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">最近告警</h2>
        </div>
        <div className="p-6">
          {displayAlerts?.slice(0, 5).map((alert: any) => (
            <div
              key={alert.alert_id}
              className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-red-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                  <p className="text-xs text-gray-500">{alert.timestamp}</p>
                </div>
              </div>
              <span className={`
                px-2 py-1 text-xs font-medium rounded-full
                ${alert.alert_level === 'L1' ? 'bg-red-100 text-red-800' : ''}
                ${alert.alert_level === 'L2' ? 'bg-orange-100 text-orange-800' : ''}
                ${alert.alert_level === 'L3' ? 'bg-yellow-100 text-yellow-800' : ''}
              `}>
                {alert.alert_level}
              </span>
            </div>
          ))}
          {(!displayAlerts || displayAlerts.length === 0) && (
            <p className="text-center text-gray-500 py-8">暂无告警数据</p>
          )}
          {isConnected && realtimeAlerts.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-green-600 text-center">
                <Activity className="w-3 h-3 inline mr-1" />
                实时更新中
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {/* Device Status Distribution */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">设备状态分布</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={deviceStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {deviceStatusData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 24h Alert Trend */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">24小时告警趋势</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={alertTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="告警数" stroke="#ef4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
