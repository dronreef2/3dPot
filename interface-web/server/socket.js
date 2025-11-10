// Socket.IO handlers for real-time communication

export function setupSocketHandlers(io) {
  // Handle client connections
  io.on('connection', (socket) => {
    console.log(`🔗 Client connected: ${socket.id}`)

    // Join default room
    socket.join('dashboard')

    // Send initial connection confirmation
    socket.emit('connection_confirmed', {
      id: socket.id,
      timestamp: new Date().toISOString(),
      message: 'Conectado ao servidor 3dPot'
    })

    // Handle client requests for device status
    socket.on('request_device_status', () => {
      // In production, this would query the real devices
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
    })

    // Handle device control commands
    socket.on('device_control', (data) => {
      const { deviceType, action, parameters } = data
      
      console.log(`📡 Device control: ${deviceType} - ${action}`, parameters)
      
      // In production, this would send commands to actual devices
      // For now, we'll simulate the response
      
      const response = {
        success: true,
        deviceType,
        action,
        parameters,
        timestamp: new Date().toISOString(),
        message: `Comando ${action} executado com sucesso em ${deviceType}`
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
    })

    // Handle alert acknowledgment
    socket.on('acknowledge_alert', (data) => {
      const { alertId } = data
      
      console.log(`✅ Alert acknowledged: ${alertId}`)
      
      // In production, update database
      // For now, just broadcast the acknowledgment
      io.emit('alert_acknowledged', {
        alertId,
        timestamp: new Date().toISOString()
      })
    })

    // Handle device-specific subscriptions
    socket.on('subscribe_device', (data) => {
      const { deviceType } = data
      const room = `device_${deviceType}`
      socket.join(room)
      console.log(`📡 Client ${socket.id} subscribed to ${room}`)
    })

    socket.on('unsubscribe_device', (data) => {
      const { deviceType } = data
      const room = `device_${deviceType}`
      socket.leave(room)
      console.log(`📡 Client ${socket.id} unsubscribed from ${room}`)
    })

    // Handle disconnection
    socket.on('disconnect', (reason) => {
      console.log(`🔌 Client disconnected: ${socket.id} - ${reason}`)
    })
  })

  // Simulate real-time device updates
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

  // Handle periodic device heartbeats
  setInterval(() => {
    io.emit('heartbeat', {
      serverTime: new Date().toISOString(),
      connectedClients: io.engine.clientsCount,
      uptime: process.uptime()
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
}

export function broadcastAlert(io, alert) {
  io.emit('alert', {
    ...alert,
    timestamp: new Date().toISOString()
  })
}

export function sendCommandResponse(socket, success, message, data = {}) {
  socket.emit('command_response', {
    success,
    message,
    data,
    timestamp: new Date().toISOString()
  })
}