import { useState, useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import toast from 'react-hot-toast'
import type { WebSocketMessage, AlertMessage } from '@types'

interface UseWebSocketOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onMessage?: (message: WebSocketMessage) => void
  onAlert?: (alert: AlertMessage) => void
  onDeviceUpdate?: (device: any) => void
  onConnectionChange?: (connected: boolean) => void
}

interface WebSocketState {
  connected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastMessage: WebSocketMessage | null
  error: string | null
}

const DEFAULT_OPTIONS: Required<UseWebSocketOptions> = {
  autoReconnect: true,
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
  onMessage: () => {},
  onAlert: () => {},
  onDeviceUpdate: () => {},
  onConnectionChange: () => {}
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    connectionStatus: 'disconnected',
    lastMessage: null,
    error: null
  })
  
  const socketRef = useRef<Socket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimerRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    try {
      setState(prev => ({ ...prev, connectionStatus: 'connecting', error: null }))

      // In development, simulate WebSocket connection
      if (import.meta.env.DEV) {
        setTimeout(() => {
          setState(prev => ({
            ...prev,
            connected: true,
            connectionStatus: 'connected'
          }))
          opts.onConnectionChange(true)
          
          // Simulate periodic updates
          const interval = setInterval(() => {
            const mockMessage: WebSocketMessage = {
              type: 'device_update',
              deviceId: ['filament-001', 'conveyor-001', 'qc-001'][Math.floor(Math.random() * 3)],
              timestamp: new Date(),
              payload: {
                data: {
                  // Mock data based on device type
                }
              }
            }
            
            setState(prev => ({ ...prev, lastMessage: mockMessage }))
            opts.onMessage(mockMessage)
            
            // Emit custom events for device updates
            if (mockMessage.type === 'device_update') {
              const deviceType = mockMessage.deviceId.includes('filament') ? 'filament' :
                               mockMessage.deviceId.includes('conveyor') ? 'conveyor' : 'qc'
              
              window.dispatchEvent(new CustomEvent('device_update', {
                detail: {
                  deviceType,
                  deviceData: mockMessage.payload
                }
              }))
            }
            
            // Random alert simulation
            if (Math.random() > 0.95) {
              const mockAlert: AlertMessage = {
                id: `alert_${Date.now()}`,
                deviceId: mockMessage.deviceId,
                deviceName: `Device ${mockMessage.deviceId}`,
                severity: Math.random() > 0.7 ? 'critical' : 'warning',
                title: 'Test Alert',
                message: 'This is a test alert for development',
                timestamp: new Date(),
                acknowledged: false
              }
              
              opts.onAlert(mockAlert)
              window.dispatchEvent(new CustomEvent('alert', { detail: mockAlert }))
              
              if (mockAlert.severity === 'critical') {
                toast.error(`🚨 ${mockAlert.title}: ${mockAlert.message}`)
              } else {
                toast(`⚠️ ${mockAlert.title}: ${mockAlert.message}`)
              }
            }
          }, Math.random() * 10000 + 5000) // 5-15 seconds

          return () => clearInterval(interval)
        }, 1000)
        return
      }

      // Production WebSocket connection
      socketRef.current = io('ws://localhost:5000', {
        transports: ['websocket', 'polling'],
        timeout: 10000,
        forceNew: true
      })

      socketRef.current.on('connect', () => {
        setState(prev => ({
          ...prev,
          connected: true,
          connectionStatus: 'connected',
          error: null
        }))
        opts.onConnectionChange(true)
        reconnectAttemptsRef.current = 0
        
        toast.success('🔗 Conectado ao servidor')
      })

      socketRef.current.on('disconnect', () => {
        setState(prev => ({
          ...prev,
          connected: false,
          connectionStatus: 'disconnected'
        }))
        opts.onConnectionChange(false)
        
        if (reconnectAttemptsRef.current === 0) {
          toast.error('🔌 Conexão perdida com o servidor')
        }
      })

      socketRef.current.on('connect_error', (error) => {
        setState(prev => ({
          ...prev,
          connected: false,
          connectionStatus: 'error',
          error: error.message
        }))
        opts.onConnectionChange(false)
        console.error('WebSocket connection error:', error)
      })

      socketRef.current.on('device_update', (data) => {
        const message: WebSocketMessage = {
          type: 'device_update',
          deviceId: data.deviceId,
          timestamp: new Date(data.timestamp),
          payload: data.payload
        }
        
        setState(prev => ({ ...prev, lastMessage: message }))
        opts.onMessage(message)
        opts.onDeviceUpdate(data)
        
        // Emit custom events
        window.dispatchEvent(new CustomEvent('device_update', {
          detail: {
            deviceType: data.deviceType,
            deviceData: data
          }
        }))
      })

      socketRef.current.on('alert', (alert: AlertMessage) => {
        opts.onAlert(alert)
        
        // Emit custom events
        window.dispatchEvent(new CustomEvent('alert', { detail: alert }))
        
        // Show toast notifications
        if (alert.severity === 'critical') {
          toast.error(`🚨 ${alert.title}: ${alert.message}`)
        } else {
          toast(`⚠️ ${alert.title}: ${alert.message}`)
        }
      })

      socketRef.current.on('command_response', (response) => {
        if (response.success) {
          toast.success(`✅ ${response.message}`)
        } else {
          toast.error(`❌ ${response.message}`)
        }
      })

    } catch (error) {
      setState(prev => ({
        ...prev,
        connected: false,
        connectionStatus: 'error',
        error: error instanceof Error ? error.message : 'Connection failed'
      }))
      opts.onConnectionChange(false)
    }
  }, [opts])

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current)
    }
    
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
    }
    
    setState(prev => ({
      ...prev,
      connected: false,
      connectionStatus: 'disconnected'
    }))
    opts.onConnectionChange(false)
  }, [opts])

  const sendMessage = useCallback((message: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('message', message)
    } else {
      console.warn('Cannot send message: WebSocket not connected')
    }
  }, [])

  // Auto-reconnect logic
  useEffect(() => {
    if (opts.autoReconnect && state.connectionStatus === 'disconnected' && reconnectAttemptsRef.current < opts.maxReconnectAttempts) {
      reconnectTimerRef.current = setTimeout(() => {
        reconnectAttemptsRef.current++
        console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${opts.maxReconnectAttempts})`)
        connect()
      }, opts.reconnectInterval * reconnectAttemptsRef.current) // Exponential backoff
    }
  }, [state.connectionStatus, opts.autoReconnect, opts.reconnectInterval, opts.maxReconnectAttempts, connect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  // Initial connection
  useEffect(() => {
    connect()
  }, [connect])

  return {
    ...state,
    connect,
    disconnect,
    sendMessage
  }
}