import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Activity, Radio, Heart, Wind, AlertTriangle, TrendingUp } from 'lucide-react'
import api from '../services/api'
import { API_CONFIG } from '../config/api'

interface IOTTimeseries {
  iot_id: string
  tenant_id: string
  device_id: string
  resident_id?: string
  location_id?: string
  timestamp: string
  data_type: string
  value: number
  unit?: string
  danger_level?: string
  tag_category?: string
  tag_code?: string
  snomed_code?: string
  created_at: string
}

export default function IoTData() {
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState(24) // 默认24小时

  const TENANT_ID = API_CONFIG.DEFAULT_TENANT_ID

  // 获取设备列表
  const { data: devices } = useQuery({
    queryKey: ['devices', TENANT_ID],
    queryFn: async () => {
      const { data } = await api.get(`/api/v1/devices/?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  // 获取IoT统计信息
  const { data: statistics } = useQuery({
    queryKey: ['iot-statistics', TENANT_ID, timeRange],
    queryFn: async () => {
      const { data } = await api.get(
        `/api/v1/iot-data/statistics?tenant_id=${TENANT_ID}&hours=${timeRange}`
      )
      return data
    },
  })

  // 获取最新IoT数据列表
  const { data: iotDataList, isLoading } = useQuery<IOTTimeseries[]>({
    queryKey: ['iot-data-list', TENANT_ID, selectedDevice, timeRange],
    queryFn: async () => {
      let url = `/api/v1/iot-data/query?tenant_id=${TENANT_ID}&limit=50`
      if (selectedDevice) {
        url += `&device_id=${selectedDevice}`
      }
      const { data } = await api.get(url)
      return data
    },
    refetchInterval: 5000, // 每5秒自动刷新
  })

  // 获取危险等级的样式
  const getDangerLevelStyle = (level?: string) => {
    switch (level) {
      case 'L1':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'L2':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'L3':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'L5':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  // 获取数据类型图标
  const getDataTypeIcon = (dataType: string) => {
    switch (dataType) {
      case 'heart_rate':
        return <Heart className="h-4 w-4" />
      case 'respiratory_rate':
        return <Wind className="h-4 w-4" />
      case 'vital_signs':
        return <Activity className="h-4 w-4" />
      default:
        return <Radio className="h-4 w-4" />
    }
  }

  // 格式化时间
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Radio className="h-8 w-8 text-blue-600" />
          IoT数据监控
        </h1>
        <p className="text-gray-600 mt-1">实时设备数据与生命体征监测</p>
      </div>

      {/* 统计卡片 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总数据量</p>
                <p className="text-2xl font-bold text-gray-900">
                  {statistics.total_records || 0}
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">在线设备</p>
                <p className="text-2xl font-bold text-green-600">
                  {statistics.active_devices || 0}
                </p>
              </div>
              <Radio className="h-8 w-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">平均心率</p>
                <p className="text-2xl font-bold text-pink-600">
                  {statistics.avg_heart_rate?.toFixed(0) || '--'} bpm
                </p>
              </div>
              <Heart className="h-8 w-8 text-pink-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">平均呼吸率</p>
                <p className="text-2xl font-bold text-cyan-600">
                  {statistics.avg_respiratory_rate?.toFixed(0) || '--'} /min
                </p>
              </div>
              <Wind className="h-8 w-8 text-cyan-500" />
            </div>
          </div>
        </div>
      )}

      {/* 筛选器 */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">设备筛选:</label>
            <select
              value={selectedDevice || ''}
              onChange={(e) => setSelectedDevice(e.target.value || null)}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部设备</option>
              {devices?.map((device: any) => (
                <option key={device.device_id} value={device.device_id}>
                  {device.device_name || device.device_id}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">时间范围:</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>最近1小时</option>
              <option value={6}>最近6小时</option>
              <option value={24}>最近24小时</option>
              <option value={168}>最近7天</option>
            </select>
          </div>

          <div className="ml-auto flex items-center gap-2 text-sm text-gray-600">
            <Activity className="h-4 w-4 animate-pulse text-green-500" />
            <span>自动刷新中</span>
          </div>
        </div>
      </div>

      {/* IoT数据列表 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">实时数据流</h2>
          <p className="text-sm text-gray-600 mt-1">
            {iotDataList?.length || 0} 条记录 (最近{timeRange}小时)
          </p>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-2" />
            <p>加载数据中...</p>
          </div>
        ) : iotDataList && iotDataList.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {iotDataList.map((data) => (
              <div
                key={data.iot_id}
                className="p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {/* 数据类型图标 */}
                    <div className="mt-1">{getDataTypeIcon(data.data_type)}</div>

                    {/* 主要信息 */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {data.data_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className="text-2xl font-bold text-blue-600">
                          {data.value}
                        </span>
                        {data.unit && (
                          <span className="text-sm text-gray-600">{data.unit}</span>
                        )}
                      </div>

                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span>设备: {data.device_id.substring(0, 8)}...</span>
                        {data.resident_id && (
                          <span>住户: {data.resident_id.substring(0, 8)}...</span>
                        )}
                        <span>{formatTime(data.timestamp)}</span>
                      </div>

                      {/* SNOMED编码和标签 */}
                      <div className="flex items-center gap-2 mt-2">
                        {data.snomed_code && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-300">
                            SNOMED: {data.snomed_code}
                          </span>
                        )}
                        {data.tag_category && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-300">
                            {data.tag_category}: {data.tag_code}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* 危险等级标识 */}
                  {data.danger_level && (
                    <div
                      className={`flex items-center gap-1 px-3 py-1 rounded border ${getDangerLevelStyle(
                        data.danger_level
                      )}`}
                    >
                      <AlertTriangle className="h-4 w-4" />
                      <span className="text-sm font-medium">{data.danger_level}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <Radio className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium">暂无IoT数据</p>
            <p className="text-sm mt-1">等待设备发送数据...</p>
          </div>
        )}
      </div>

      {/* 底部提示 */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">数据说明</p>
            <ul className="mt-2 space-y-1 list-disc list-inside">
              <li>L1(紧急): 心率&lt;44或&gt;116，呼吸率&lt;7或&gt;27</li>
              <li>L2(警报): 心率45-54或96-115，呼吸率8-9或24-26</li>
              <li>L3(严重): 需要关注的异常值</li>
              <li>数据每5秒自动刷新</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
