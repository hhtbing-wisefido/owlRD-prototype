import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface VitalSignsChartProps {
  data: Array<{
    timestamp: string
    heart_rate?: number
    respiratory_rate?: number
  }>
  dataType: 'heart_rate' | 'respiratory_rate' | 'both'
}

export default function VitalSignsChart({ data, dataType }: VitalSignsChartProps) {
  // 处理数据，格式化时间戳
  const chartData = data.map((item) => ({
    ...item,
    time: new Date(item.timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    }),
  }))

  // 根据数据类型获取颜色和名称
  const getChartConfig = () => {
    if (dataType === 'heart_rate') {
      return {
        lines: [
          { dataKey: 'heart_rate', stroke: '#ef4444', name: '心率 (bpm)' },
        ],
      }
    } else if (dataType === 'respiratory_rate') {
      return {
        lines: [
          { dataKey: 'respiratory_rate', stroke: '#3b82f6', name: '呼吸率 (/min)' },
        ],
      }
    } else {
      return {
        lines: [
          { dataKey: 'heart_rate', stroke: '#ef4444', name: '心率 (bpm)' },
          { dataKey: 'respiratory_rate', stroke: '#3b82f6', name: '呼吸率 (/min)' },
        ],
      }
    }
  }

  const config = getChartConfig()

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="time"
          style={{ fontSize: '12px' }}
        />
        <YAxis style={{ fontSize: '12px' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
        />
        <Legend />
        {config.lines.map((line) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            stroke={line.stroke}
            name={line.name}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
