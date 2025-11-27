import { AlertCircle, XCircle } from 'lucide-react'

interface ErrorMessageProps {
  title?: string
  message: string
  type?: 'error' | 'warning'
  onRetry?: () => void
  className?: string
}

export default function ErrorMessage({
  title,
  message,
  type = 'error',
  onRetry,
  className = ''
}: ErrorMessageProps) {
  const Icon = type === 'error' ? XCircle : AlertCircle
  const bgColor = type === 'error' ? 'bg-red-50' : 'bg-yellow-50'
  const borderColor = type === 'error' ? 'border-red-200' : 'border-yellow-200'
  const textColor = type === 'error' ? 'text-red-800' : 'text-yellow-800'
  const iconColor = type === 'error' ? 'text-red-600' : 'text-yellow-600'

  return (
    <div className={`${bgColor} border ${borderColor} rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 ${iconColor} flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          {title && (
            <h3 className={`text-sm font-semibold ${textColor} mb-1`}>
              {title}
            </h3>
          )}
          <p className={`text-sm ${textColor}`}>
            {message}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-sm font-medium text-blue-600 hover:text-blue-800 transition"
            >
              重试
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
