import { useEffect, useRef, useState } from 'react'

interface WebSocketMessage {
  type: string
  data?: any
  message?: string
  timestamp: string
}

interface UseRealtimeDataOptions {
  url?: string
  topics?: string[]
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Event) => void
  autoReconnect?: boolean
  reconnectInterval?: number
}

export default function useRealtimeData({
  url = 'ws://localhost:8000/api/v1/realtime/ws',
  topics = [],
  onMessage,
  onError,
  autoReconnect = true,
  reconnectInterval = 5000
}: UseRealtimeDataOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const subscribedTopicsRef = useRef<Set<string>>(new Set())

  const connect = () => {
    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)

        // 订阅主题
        topics.forEach(topic => {
          subscribe(topic)
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          
          if (onMessage) {
            onMessage(message)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        if (onError) {
          onError(error)
        }
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null

        // 自动重连
        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...')
            connect()
          }, reconnectInterval)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Error creating WebSocket:', error)
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    setIsConnected(false)
  }

  const send = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  const subscribe = (topic: string) => {
    if (!subscribedTopicsRef.current.has(topic)) {
      send({
        type: 'subscribe',
        topic
      })
      subscribedTopicsRef.current.add(topic)
    }
  }

  const unsubscribe = (topic: string) => {
    if (subscribedTopicsRef.current.has(topic)) {
      send({
        type: 'unsubscribe',
        topic
      })
      subscribedTopicsRef.current.delete(topic)
    }
  }

  const ping = () => {
    send({ type: 'ping' })
  }

  useEffect(() => {
    connect()

    // 心跳检测
    const heartbeatInterval = setInterval(() => {
      if (isConnected) {
        ping()
      }
    }, 30000) // 每30秒发送一次心跳

    return () => {
      clearInterval(heartbeatInterval)
      disconnect()
    }
  }, [])

  return {
    isConnected,
    lastMessage,
    send,
    subscribe,
    unsubscribe,
    ping,
    disconnect
  }
}
