import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Users, Radio, Activity } from 'lucide-react'
import api from '../services/api'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Dashboard() {
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

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">仪表板</h1>

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
          {alerts?.slice(0, 5).map((alert: any) => (
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
          {(!alerts || alerts.length === 0) && (
            <p className="text-center text-gray-500 py-8">暂无告警数据</p>
          )}
        </div>
      </div>
    </div>
  )
}
