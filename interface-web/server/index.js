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
import { initializeDatabase } from './database.js'
import { deviceRoutes } from './routes/devices.js'
import { qcRoutes } from './routes/qc.js'
import { analyticsRoutes } from './routes/analytics.js'
import { setupSocketHandlers } from './socket.js'

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
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true }))

// Initialize database
await initializeDatabase()

// API Routes
app.use('/api/devices', deviceRoutes)
app.use('/api/qc', qcRoutes)
app.use('/api/analytics', analyticsRoutes)

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  })
})

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
setupSocketHandlers(io)

// Background tasks
// Send periodic updates to clients
cron.schedule('*/10 * * * * *', () => {
  // This would send real device updates in production
  console.log('Background task: sending device updates...')
})

// Start server
server.listen(PORT, () => {
  console.log(`🚀 3dPot Backend Server running on port ${PORT}`)
  console.log(`📡 WebSocket server ready on port ${PORT}`)
  console.log(`🌐 Frontend can connect at http://localhost:3000`)
  console.log(`🔧 API available at http://localhost:${PORT}/api`)
})

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully...')
  server.close(() => {
    console.log('✅ Process terminated')
  })
})

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, shutting down gracefully...')
  server.close(() => {
    console.log('✅ Process terminated')
  })
})

export { io }