import { useQuery } from '@tanstack/react-query'
import { Radio, Circle } from 'lucide-react'
import api from '../services/api'
import type { Device } from '../types'

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Devices() {
  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      const { data } = await api.get<Device[]>(`/api/v1/devices?tenant_id=${TENANT_ID}`)
      return data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">加载中...</div>
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500'
      case 'offline': return 'text-gray-400'
      case 'error': return 'text-red-500'
      default: return 'text-gray-400'
    }
  }

  const statusText = (status: string) => {
    switch (status) {
      case 'online': return '在线'
      case 'offline': return '离线'
      case 'error': return '错误'
      case 'maintenance': return '维护中'
      default: return status
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">设备管理</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices?.map((device) => (
          <div
            key={device.device_id}
            className="bg-white rounded-lg shadow border border-gray-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="bg-blue-100 rounded-lg p-3 mr-3">
                  <Radio className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {device.device_name}
                  </h3>
                  <p className="text-sm text-gray-500">{device.device_model}</p>
                </div>
              </div>
              <Circle className={`w-3 h-3 fill-current ${statusColor(device.status)}`} />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">类型:</span>
                <span className="text-gray-900 font-medium">{device.device_type}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">状态:</span>
                <span className={`font-medium ${statusColor(device.status)}`}>
                  {statusText(device.status)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">序列号:</span>
                <span className="text-gray-900 font-mono text-xs">
                  {device.serial_number || '-'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">固件版本:</span>
                <span className="text-gray-900">{device.firmware_version || '-'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">通信方式:</span>
                <span className="text-gray-900">{device.comm_mode}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>已安装: {device.installed ? '是' : '否'}</span>
                <span>监控: {device.monitoring_enabled ? '开启' : '关闭'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {(!devices || devices.length === 0) && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-12 text-center text-gray-500">
          暂无设备数据
        </div>
      )}
    </div>
  )
}
