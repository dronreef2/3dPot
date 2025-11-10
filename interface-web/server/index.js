import express from 'express'
import { createServer } from 'http'
import { Server } from 'socket.io'
import cors from 'cors'
import helmet from 'helmet'
import compression from 'compression'
import morgan from 'morgan'
import path from 'path'
import { fileURLToPath } from 'url'
import cron from 'node-cron'
import cookieParser from 'cookie-parser'
import { initializeDatabase } from './database.js'
import { deviceRoutes } from './routes/devices.js'
import { qcRoutes } from './routes/qc.js'
import { analyticsRoutes } from './routes/analytics.js'
import { authRoutes } from './routes/auth.js'
import { setupSocketHandlers } from './socket.js'
import DeviceManager from './integrations/deviceManager.js'
import AuthService from './services/authService.js'
import { logger } from './utils/logger.js'

// Get current directory
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const server = createServer(app)
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST", "PUT", "DELETE"]
  }
})

const PORT = process.env.PORT || 5000

// Initialize services
const authService = new AuthService()
const deviceManager = new DeviceManager()

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for development
}))
app.use(compression())
app.use(morgan('combined'))
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true
}))
app.use(cookieParser())
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true }))

// Request logging
app.use((req, res, next) => {
  const start = Date.now()
  res.on('finish', () => {
    const duration = Date.now() - start
    logger.logRequest(req, res, duration)
  })
  next()
})

// Initialize database
await initializeDatabase()

// Initialize device manager
await deviceManager.initialize()
deviceManager.setSocketIO(io)

// API Routes
app.use('/api/auth', authRoutes)
app.use('/api/devices', deviceRoutes)
app.use('/api/qc', qcRoutes)
app.use('/api/analytics', analyticsRoutes)

// Inject services for routes
app.set('authService', authService)
app.set('deviceManager', deviceManager)

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const systemHealth = deviceManager.getSystemHealth()
    const dbStatus = await checkDatabaseHealth()
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      database: dbStatus,
      devices: systemHealth
    })
  } catch (error) {
    logger.error('Health check failed', { error: error.message })
    res.status(500).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    })
  }
})

// Helper function to check database health
async function checkDatabaseHealth() {
  try {
    // Simple database query to test connection
    // This would be implemented based on your database setup
    return {
      status: 'connected',
      responseTime: Math.random() * 10 // Mock response time
    }
  } catch (error) {
    return {
      status: 'disconnected',
      error: error.message
    }
  }
}

// Serve static files from public directory
app.use(express.static(path.join(__dirname, '../public')))

// Fallback to index.html for client-side routing
app.get('*', (req, res) => {
  if (req.path.startsWith('/api/')) {
    return res.status(404).json({ error: 'API endpoint not found' })
  }
  res.sendFile(path.join(__dirname, '../public/index.html'))
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err)
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'production' 
      ? 'Internal server error' 
      : err.message
  })
})

// Setup Socket.IO handlers
setupSocketHandlers(io, deviceManager)

// Background tasks
// Send periodic updates to clients
cron.schedule('*/10 * * * * *', async () => {
  try {
    // Get device status and broadcast updates
    const deviceStatus = await deviceManager.getAllDevicesStatus()
    io.to('dashboard').emit('device_status_bulk', deviceStatus)
  } catch (error) {
    logger.error('Background device status update failed', { error: error.message })
  }
})

// System monitoring
cron.schedule('*/5 * * * *', async () => {
  try {
    const systemHealth = deviceManager.getSystemHealth()
    if (systemHealth.overall === 'critical') {
      logger.warn('System health critical', systemHealth)
      io.emit('system_alert', {
        severity: 'critical',
        title: 'System Health Critical',
        message: 'Multiple devices are offline',
        timestamp: new Date().toISOString()
      })
    }
  } catch (error) {
    logger.error('System monitoring failed', { error: error.message })
  }
})

// Start server
server.listen(PORT, () => {
  logger.system('3dPot Backend Server started', {
    port: PORT,
    environment: process.env.NODE_ENV || 'development'
  })
  console.log(`🚀 3dPot Backend Server running on port ${PORT}`)
  console.log(`📡 WebSocket server ready on port ${PORT}`)
  console.log(`🌐 Frontend can connect at http://localhost:3000`)
  console.log(`🔧 API available at http://localhost:${PORT}/api`)
  console.log(`🔐 Auth endpoints at http://localhost:${PORT}/api/auth`)
})

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.system('SIGTERM received, shutting down gracefully...')
  await shutdown()
})

process.on('SIGINT', async () => {
  logger.system('SIGINT received, shutting down gracefully...')
  await shutdown()
})

async function shutdown() {
  try {
    // Stop accepting new connections
    server.close()
    
    // Shutdown device manager
    await deviceManager.shutdown()
    
    // Cleanup services
    authService.cleanup()
    logger.close()
    
    process.exit(0)
  } catch (error) {
    logger.error('Error during shutdown', { error: error.message })
    process.exit(1)
  }
}

export { io }