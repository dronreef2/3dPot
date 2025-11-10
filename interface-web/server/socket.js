// Socket.IO handlers for real-time communication
import { logger } from './utils/logger.js'

export function setupSocketHandlers(io, deviceManager) {
  // Handle client connections
  io.on('connection', (socket) => {
    logger.logWebSocket('connected', socket.id, {
      ip: socket.handshake.address
    })

    // Join default room
    socket.join('dashboard')

    // Send initial connection confirmation
    socket.emit('connection_confirmed', {
      id: socket.id,
      timestamp: new Date().toISOString(),
      message: 'Conectado ao servidor 3dPot'
    })

    // Handle client requests for device status
    socket.on('request_device_status', async () => {
      try {
        if (deviceManager) {
          const deviceStatus = await deviceManager.getAllDevicesStatus()
          socket.emit('device_status', deviceStatus)
        } else {
          // Fallback para modo desenvolvimento
          const deviceStatus = {
            filament: {
              id: 'filament-001',
              status: 'online',
              data: {
                weight: Math.random() * 1000 + 100,
                temperature: Math.random() * 15 + 20,
                batteryLevel: Math.random() * 100
              }
            },
            conveyor: {
              id: 'conveyor-001', 
              status: 'online',
              data: {
                speed: Math.random() * 100,
                isRunning: Math.random() > 0.2,
                mode: Math.random() > 0.3 ? 'automatic' : 'manual'
              }
            },
            qc: {
              id: 'qc-001',
              status: 'online',
              data: {
                lastInspection: {
                  classification: ['A', 'B', 'C', 'D', 'F'][Math.floor(Math.random() * 5)],
                  confidence: Math.random() * 0.4 + 0.6
                }
              }
            }
          }
          
          socket.emit('device_status', deviceStatus)
        }
      } catch (error) {
        logger.error('Error getting device status', { error: error.message, socketId: socket.id })
        socket.emit('device_status_error', { error: 'Erro ao obter status dos dispositivos' })
      }
    })

    // Handle device control commands
    socket.on('device_control', async (data) => {
      const { deviceType, action, parameters } = data
      
      logger.logWebSocket('device_control', socket.id, { deviceType, action, parameters })
      
      try {
        if (deviceManager) {
          const result = await deviceManager.controlDevice(deviceType, action, parameters)
          
          socket.emit('command_response', {
            success: result.success,
            deviceType,
            action,
            result: result.result,
            error: result.error,
            timestamp: new Date().toISOString()
          })
          
          // Broadcast to other clients
          if (result.success) {
            socket.broadcast.to('dashboard').emit('device_update', {
              deviceId: `${deviceType}-001`,
              deviceType,
              action,
              timestamp: new Date().toISOString(),
              payload: {
                commandExecuted: action,
                success: true
              }
            })
          }
          
        } else {
          // Fallback para modo desenvolvimento
          const response = {
            success: true,
            deviceType,
            action,
            parameters,
            timestamp: new Date().toISOString(),
            message: `Comando ${action} executado com sucesso em ${deviceType} (modo desenvolvimento)`
          }
          
          socket.emit('command_response', response)
          
          // Broadcast to other clients
          socket.broadcast.to('dashboard').emit('device_update', {
            deviceId: `${deviceType}-001`,
            deviceType,
            action,
            timestamp: new Date().toISOString(),
            payload: {
              commandExecuted: action,
              success: true
            }
          })
        }
      } catch (error) {
        logger.error('Error controlling device', { 
          error: error.message, 
          deviceType, 
          action, 
          socketId: socket.id 
        })
        
        socket.emit('command_response', {
          success: false,
          deviceType,
          action,
          error: error.message,
          timestamp: new Date().toISOString()
        })
      }
    })

    // Handle alert acknowledgment
    socket.on('acknowledge_alert', (data) => {
      const { alertId } = data
      
      logger.logWebSocket('alert_acknowledged', socket.id, { alertId })
      
      // Broadcast acknowledgment to all clients
      io.emit('alert_acknowledged', {
        alertId,
        timestamp: new Date().toISOString(),
        acknowledgedBy: socket.id
      })
    })

    // Handle device-specific subscriptions
    socket.on('subscribe_device', (data) => {
      const { deviceType } = data
      const room = `device_${deviceType}`
      socket.join(room)
      logger.logWebSocket('subscribed', socket.id, { device: deviceType })
    })

    socket.on('unsubscribe_device', (data) => {
      const { deviceType } = data
      const room = `device_${deviceType}`
      socket.leave(room)
      logger.logWebSocket('unsubscribed', socket.id, { device: deviceType })
    })

    // Handle disconnection
    socket.on('disconnect', (reason) => {
      logger.logWebSocket('disconnected', socket.id, { reason })
    })
  })

  // Se deviceManager estiver disponível, configurar event listeners
  if (deviceManager) {
    // Device status updates
    deviceManager.on('deviceStatusUpdate', ({ deviceType, status }) => {
      io.to(`device_${deviceType}`).emit('device_status_update', {
        deviceType,
        status,
        timestamp: new Date().toISOString()
      })
    })

    // Device data updates
    deviceManager.on('deviceDataUpdate', ({ deviceType, data }) => {
      io.to(`device_${deviceType}`).emit('device_data_update', {
        deviceType,
        data,
        timestamp: new Date().toISOString()
      })
    })

    // Inspection results (QC)
    deviceManager.on('inspectionResult', (result) => {
      io.emit('inspection_result', {
        ...result,
        timestamp: new Date().toISOString()
      })
    })

    // Device alerts
    deviceManager.on('deviceAlert', (alert) => {
      io.emit('alert', {
        ...alert,
        timestamp: new Date().toISOString()
      })
    })

    // System alerts
    deviceManager.on('systemAlert', (alert) => {
      io.emit('system_alert', {
        ...alert,
        timestamp: new Date().toISOString()
      })
    })

    // Device connection events
    deviceManager.on('deviceConnected', ({ deviceType, status }) => {
      io.emit('device_connected', {
        deviceType,
        status,
        timestamp: new Date().toISOString()
      })
    })

    deviceManager.on('deviceDisconnected', ({ deviceType }) => {
      io.emit('device_disconnected', {
        deviceType,
        timestamp: new Date().toISOString()
      })
    })

    // Health check updates
    deviceManager.on('healthCheck', (healthStatus) => {
      io.to('dashboard').emit('health_check_update', {
        ...healthStatus,
        timestamp: new Date().toISOString()
      })
    })
  }

  // Simulate real-time device updates (only when deviceManager is not available)
  if (!deviceManager) {
    setInterval(() => {
      // Simulate device status updates
      const updates = [
        {
          type: 'device_update',
          deviceId: 'filament-001',
          timestamp: new Date().toISOString(),
          payload: {
            weight: Math.random() * 1000 + 100,
            temperature: Math.random() * 15 + 20,
            batteryLevel: Math.random() * 100,
            isSleeping: Math.random() > 0.8
          }
        },
        {
          type: 'device_update', 
          deviceId: 'conveyor-001',
          timestamp: new Date().toISOString(),
          payload: {
            speed: Math.random() * 100,
            isRunning: Math.random() > 0.1,
            position: Math.random() * 1000,
            load: Math.random() * 100
          }
        },
        {
          type: 'device_update',
          deviceId: 'qc-001', 
          timestamp: new Date().toISOString(),
          payload: {
            lastInspection: {
              classification: ['A', 'B', 'C', 'D', 'F'][Math.floor(Math.random() * 5)],
              confidence: Math.random() * 0.4 + 0.6
            }
          }
        }
      ]

      // Send random update every 15-30 seconds
      if (Math.random() > 0.7) {
        const update = updates[Math.floor(Math.random() * updates.length)]
        io.emit('device_update', update)
      }

      // Occasionally send alerts
      if (Math.random() > 0.95) {
        const alert = {
          id: `alert_${Date.now()}`,
          deviceId: ['filament-001', 'conveyor-001', 'qc-001'][Math.floor(Math.random() * 3)],
          deviceName: '3dPot Device',
          severity: Math.random() > 0.7 ? 'critical' : 'warning',
          title: 'Test Alert',
          message: 'This is a test alert for development',
          timestamp: new Date().toISOString(),
          acknowledged: false
        }
        
        io.emit('alert', alert)
      }
    }, 20000) // Every 20 seconds
  }

  // Handle periodic device heartbeats
  setInterval(() => {
    io.emit('heartbeat', {
      serverTime: new Date().toISOString(),
      connectedClients: io.engine.clientsCount,
      uptime: process.uptime(),
      deviceManager: !!deviceManager
    })
  }, 30000) // Every 30 seconds
}

// Utility functions for sending updates
export function broadcastDeviceUpdate(io, deviceType, data) {
  io.to(`device_${deviceType}`).emit('device_update', {
    type: 'device_update',
    deviceId: `${deviceType}-001`,
    deviceType,
    timestamp: new Date().toISOString(),
    payload: data
  })
  
  logger.logWebSocket('broadcast_device_update', 'server', {
    deviceType,
    data: Object.keys(data)
  })
}

export function broadcastAlert(io, alert) {
  io.emit('alert', {
    ...alert,
    timestamp: new Date().toISOString()
  })
  
  logger.logWebSocket('broadcast_alert', 'server', {
    alertId: alert.id,
    severity: alert.severity
  })
}

export function sendCommandResponse(socket, success, message, data = {}) {
  socket.emit('command_response', {
    success,
    message,
    data,
    timestamp: new Date().toISOString()
  })
  
  logger.logWebSocket('command_response', socket.id, {
    success,
    message,
    hasData: Object.keys(data).length > 0
  })
}

export function sendSystemAlert(io, severity, title, message, data = {}) {
  const alert = {
    id: `system_${Date.now()}`,
    type: 'system',
    severity,
    title,
    message,
    timestamp: new Date().toISOString(),
    data
  }
  
  io.emit('system_alert', alert)
  
  logger.system('System alert sent', { severity, title, message })
}