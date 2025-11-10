import express from 'express'
import { 
  deviceQueries, 
  filamentQueries, 
  conveyorQueries,
  getDatabase 
} from '../database.js'

const router = express.Router()

// Get all devices
router.get('/', async (req, res) => {
  try {
    const devices = deviceQueries.getAllDevices.all()
    
    // Convert JSON data strings to objects
    const formattedDevices = devices.reduce((acc, device) => {
      const deviceData = device.data ? JSON.parse(device.data) : {}
      acc[device.device_type] = {
        ...device,
        data: deviceData,
        lastUpdate: new Date(device.last_update)
      }
      return acc
    }, {})
    
    res.json({
      success: true,
      data: formattedDevices,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching devices:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch devices',
      timestamp: new Date().toISOString()
    })
  }
})

// Get specific device by type
router.get('/:type', async (req, res) => {
  try {
    const { type } = req.params
    
    if (!['filament', 'conveyor', 'qc'].includes(type)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid device type'
      })
    }
    
    const device = deviceQueries.getDeviceByType.get(type)
    
    if (!device) {
      return res.status(404).json({
        success: false,
        error: 'Device not found'
      })
    }
    
    // Parse JSON data
    device.data = device.data ? JSON.parse(device.data) : {}
    device.lastUpdate = new Date(device.last_update)
    
    res.json({
      success: true,
      data: device,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching device:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch device',
      timestamp: new Date().toISOString()
    })
  }
})

// Update device configuration
router.put('/:type/config', async (req, res) => {
  try {
    const { type } = req.params
    const config = req.body
    
    // In production, this would update the actual device configuration
    // For now, we'll just log it and return success
    
    console.log(`Updating ${type} config:`, config)
    
    res.json({
      success: true,
      message: `Configuration updated for ${type}`,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error updating device config:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to update device configuration',
      timestamp: new Date().toISOString()
    })
  }
})

// Control device
router.post('/:type/control', async (req, res) => {
  try {
    const { type } = req.params
    const { action, parameters } = req.body
    
    if (!action) {
      return res.status(400).json({
        success: false,
        error: 'Action is required'
      })
    }
    
    console.log(`Controlling ${type}: ${action}`, parameters)
    
    // Simulate device control
    const controlResults = {
      filament: {
        'calibrate': { message: 'Calibração iniciada' },
        'sleep': { message: 'Modo sleep ativado' },
        'wake': { message: 'Dispositivo acordado' }
      },
      conveyor: {
        'set_speed': { message: 'Velocidade ajustada' },
        'set_direction': { message: 'Direção alterada' },
        'toggle_mode': { message: 'Modo alternado' },
        'emergency_stop': { message: 'Parada de emergência ativada' },
        'start': { message: 'Esteira iniciada' },
        'stop': { message: 'Esteira parada' }
      },
      qc: {
        'inspect': { message: 'Inspeção iniciada' },
        'start_monitoring': { message: 'Monitoramento iniciado' },
        'stop_inspection': { message: 'Inspeção parada' }
      }
    }
    
    const result = controlResults[type]?.[action] || { message: 'Comando executado' }
    
    res.json({
      success: true,
      data: {
        action,
        parameters,
        result
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error controlling device:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to control device',
      timestamp: new Date().toISOString()
    })
  }
})

// Health check for device
router.get('/:type/health', async (req, res) => {
  try {
    const { type } = req.params
    
    // Simulate health check
    const health = {
      status: 'healthy',
      lastPing: new Date().toISOString(),
      uptime: Math.floor(Math.random() * 86400) + 3600, // 1-24 hours
      temperature: Math.random() * 20 + 25, // 25-45°C
      signal: Math.random() * 20 + 80 // 80-100%
    }
    
    res.json({
      success: true,
      data: health,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error checking device health:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to check device health',
      timestamp: new Date().toISOString()
    })
  }
})

// Get historical data
router.get('/:type/history', async (req, res) => {
  try {
    const { type } = req.params
    const { period = 'day' } = req.query
    
    let historicalData = []
    
    if (type === 'filament') {
      if (period === 'day') {
        // Get hourly data for today
        const db = getDatabase()
        historicalData = db.prepare(`
          SELECT 
            strftime('%H:00', created_at) as hour,
            AVG(weight) as weight,
            AVG(temperature) as temperature,
            AVG(battery_level) as battery
          FROM filament_readings
          WHERE date(created_at) = date('now')
          GROUP BY hour
          ORDER BY hour
        `).all()
      } else if (period === 'week') {
        // Get daily data for this week
        const db = getDatabase()
        historicalData = db.prepare(`
          SELECT 
            date(created_at) as date,
            AVG(weight) as weight,
            AVG(temperature) as temperature,
            AVG(battery_level) as battery,
            COUNT(*) as readings
          FROM filament_readings
          WHERE created_at >= date('now', '-7 days')
          GROUP BY date
          ORDER BY date
        `).all()
      } else {
        // Get monthly data
        const db = getDatabase()
        historicalData = db.prepare(`
          SELECT 
            date(created_at) as date,
            AVG(weight) as weight,
            AVG(temperature) as temperature,
            AVG(battery_level) as battery,
            COUNT(*) as readings
          FROM filament_readings
          WHERE created_at >= date('now', '-30 days')
          GROUP BY date
          ORDER BY date
        `).all()
      }
    } else if (type === 'conveyor') {
      if (period === 'day') {
        const db = getDatabase()
        historicalData = db.prepare(`
          SELECT 
            strftime('%H:00', created_at) as hour,
            AVG(speed) as speed,
            AVG(load) as load,
            SUM(CASE WHEN is_running = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as running_percentage
          FROM conveyor_data
          WHERE date(created_at) = date('now')
          GROUP BY hour
          ORDER BY hour
        `).all()
      } else {
        // Similar logic for other periods
        historicalData = [
          { time: '00:00', value: Math.random() * 100 },
          { time: '06:00', value: Math.random() * 100 },
          { time: '12:00', value: Math.random() * 100 },
          { time: '18:00', value: Math.random() * 100 }
        ]
      }
    } else if (type === 'qc') {
      // QC historical data
      historicalData = [
        { classification: 'A', count: Math.floor(Math.random() * 50) + 20 },
        { classification: 'B', count: Math.floor(Math.random() * 30) + 10 },
        { classification: 'C', count: Math.floor(Math.random() * 20) + 5 },
        { classification: 'D', count: Math.floor(Math.random() * 10) + 2 },
        { classification: 'F', count: Math.floor(Math.random() * 5) + 1 }
      ]
    }
    
    res.json({
      success: true,
      data: historicalData,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching historical data:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch historical data',
      timestamp: new Date().toISOString()
    })
  }
})

export { router as deviceRoutes }