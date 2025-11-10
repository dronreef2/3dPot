import express from 'express'
import { analyticsQueries, deviceQueries, getDatabase } from '../database.js'

const router = express.Router()

// Get production analytics
router.get('/production', async (req, res) => {
  try {
    const { period = 'day' } = req.query
    
    const db = getDatabase()
    
    // Get production data based on period
    let data = []
    let dateFormat = ''
    let dateRange = ''
    
    if (period === 'day') {
      dateFormat = 'strftime("%H:00", created_at) as time'
      dateRange = 'date(created_at) = date("now")'
    } else if (period === 'week') {
      dateFormat = 'strftime("%Y-%m-%d", created_at) as time'
      dateRange = 'created_at >= date("now", "-7 days")'
    } else if (period === 'month') {
      dateFormat = 'strftime("%Y-%m-%d", created_at) as time'
      dateRange = 'created_at >= date("now", "-30 days")'
    }
    
    // For now, generate mock data since we don't have real production data
    data = generateMockProductionData(period)
    
    res.json({
      success: true,
      data: {
        period,
        data: data,
        summary: {
          totalProduced: data.reduce((sum, item) => sum + (item.production || 0), 0),
          avgQuality: data.reduce((sum, item) => sum + (item.quality || 0), 0) / data.length || 0,
          peakHour: data.reduce((max, item) => 
            (item.production || 0) > (max.production || 0) ? item : max
          )
        }
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching production analytics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch production analytics',
      timestamp: new Date().toISOString()
    })
  }
})

// Get quality analytics
router.get('/quality', async (req, res) => {
  try {
    const { period = 'day' } = req.query
    
    const db = getDatabase()
    
    // Get quality distribution
    const qualityData = db.prepare(`
      SELECT 
        classification,
        COUNT(*) as count,
        AVG(confidence) as avg_confidence,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-7 days')
      GROUP BY classification
      ORDER BY classification
    `).all()
    
    // Get defect analysis
    const defectAnalysis = db.prepare(`
      SELECT 
        defect_type,
        COUNT(*) as frequency,
        AVG(confidence) as avg_confidence
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-7 days')
        AND defect_type != 'none'
        AND defect_type IS NOT NULL
      GROUP BY defect_type
      ORDER BY frequency DESC
      LIMIT 10
    `).all()
    
    // Get quality trend over time
    const qualityTrend = db.prepare(`
      SELECT 
        date(created_at) as date,
        COUNT(*) as total_inspections,
        SUM(CASE WHEN classification IN ('A', 'B') THEN 1 ELSE 0 END) as passed,
        COUNT(*) - SUM(CASE WHEN classification IN ('A', 'B') THEN 1 ELSE 0 END) as failed,
        AVG(confidence) as avg_confidence
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-7 days')
      GROUP BY date
      ORDER BY date
    `).all()
    
    res.json({
      success: true,
      data: {
        period,
        distribution: qualityData,
        defects: defectAnalysis,
        trend: qualityTrend,
        summary: {
          totalInspected: qualityData.reduce((sum, item) => sum + item.count, 0),
          passRate: qualityData
            .filter(item => ['A', 'B'].includes(item.classification))
            .reduce((sum, item) => sum + item.percentage, 0),
          avgConfidence: qualityData.length > 0 ? 
            qualityData.reduce((sum, item) => sum + (item.avg_confidence * item.count), 0) / 
            qualityData.reduce((sum, item) => sum + item.count, 0) : 0
        }
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching quality analytics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch quality analytics',
      timestamp: new Date().toISOString()
    })
  }
})

// Get device analytics
router.get('/devices', async (req, res) => {
  try {
    const db = getDatabase()
    
    // Get device status summary
    const deviceStatus = deviceQueries.getAllDevices.all()
    
    // Get uptime statistics
    const uptimeStats = deviceStatus.map(device => {
      // In production, this would be calculated from actual logs
      return {
        deviceId: device.device_id,
        deviceName: device.device_name,
        deviceType: device.device_type,
        status: device.status,
        uptime: Math.random() * 24 + 1, // 1-25 hours
        lastUpdate: device.last_update
      }
    })
    
    // Get performance metrics
    const performanceMetrics = {
      filament: {
        avgWeight: Math.random() * 500 + 200,
        batteryDrain: Math.random() * 10 + 5,
        temperature: Math.random() * 10 + 20
      },
      conveyor: {
        avgSpeed: Math.random() * 50 + 25,
        efficiency: Math.random() * 20 + 80,
        errorRate: Math.random() * 2
      },
      qc: {
        inspectionTime: Math.random() * 3 + 1,
        accuracy: Math.random() * 10 + 90,
        falsePositive: Math.random() * 5
      }
    }
    
    res.json({
      success: true,
      data: {
        devices: deviceStatus,
        uptime: uptimeStats,
        performance: performanceMetrics
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching device analytics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch device analytics',
      timestamp: new Date().toISOString()
    })
  }
})

// Get system overview
router.get('/overview', async (req, res) => {
  try {
    const db = getDatabase()
    
    // Get overall system metrics
    const totalDevices = deviceQueries.getAllDevices.all().length
    const onlineDevices = deviceQueries.getAllDevices.all().filter(d => d.status === 'online').length
    
    // Get recent alerts
    const recentAlerts = db.prepare(`
      SELECT * FROM alerts
      WHERE created_at >= date('now', '-24 hours')
      ORDER BY created_at DESC
      LIMIT 10
    `).all()
    
    // Calculate uptime percentage
    const uptime = totalDevices > 0 ? (onlineDevices / totalDevices) * 100 : 0
    
    // Get production summary
    const productionSummary = {
      today: Math.floor(Math.random() * 100) + 50,
      week: Math.floor(Math.random() * 500) + 300,
      month: Math.floor(Math.random() * 2000) + 1500
    }
    
    // Get quality summary
    const qualitySummary = {
      passRate: Math.random() * 20 + 80,
      avgClassification: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
      totalInspected: Math.floor(Math.random() * 1000) + 500
    }
    
    res.json({
      success: true,
      data: {
        system: {
          totalDevices,
          onlineDevices,
          uptime: uptime.toFixed(1),
          status: uptime > 90 ? 'healthy' : uptime > 70 ? 'warning' : 'critical'
        },
        production: productionSummary,
        quality: qualitySummary,
        alerts: recentAlerts.length,
        recentAlerts: recentAlerts.slice(0, 5)
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching system overview:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch system overview',
      timestamp: new Date().toISOString()
    })
  }
})

// Get alerts analytics
router.get('/alerts', async (req, res) => {
  try {
    const { period = 'day' } = req.query
    
    const db = getDatabase()
    
    let dateRange = '24 hours'
    if (period === 'week') dateRange = '7 days'
    if (period === 'month') dateRange = '30 days'
    
    // Get alert distribution by severity
    const alertDistribution = db.prepare(`
      SELECT 
        severity,
        COUNT(*) as count,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
      FROM alerts
      WHERE created_at >= datetime('now', '-${dateRange}')
      GROUP BY severity
      ORDER BY count DESC
    `).all()
    
    // Get alerts by device
    const alertsByDevice = db.prepare(`
      SELECT 
        COALESCE(device_name, 'Unknown') as device_name,
        COUNT(*) as count,
        MAX(severity) as max_severity
      FROM alerts
      WHERE created_at >= datetime('now', '-${dateRange}')
      GROUP BY device_name
      ORDER BY count DESC
    `).all()
    
    // Get alert trend over time
    const alertTrend = db.prepare(`
      SELECT 
        strftime('%Y-%m-%d %H:00', created_at) as time,
        COUNT(*) as count,
        severity
      FROM alerts
      WHERE created_at >= datetime('now', '-${dateRange}')
      GROUP BY time, severity
      ORDER BY time
    `).all()
    
    // Get unacknowledged alerts
    const unacknowledgedAlerts = db.prepare(`
      SELECT * FROM alerts
      WHERE acknowledged = FALSE
      ORDER BY created_at DESC
      LIMIT 10
    `).all()
    
    res.json({
      success: true,
      data: {
        period,
        distribution: alertDistribution,
        byDevice: alertsByDevice,
        trend: alertTrend,
        unacknowledged: unacknowledgedAlerts,
        summary: {
          total: alertDistribution.reduce((sum, item) => sum + item.count, 0),
          critical: alertDistribution.find(item => item.severity === 'critical')?.count || 0,
          unacknowledged: unacknowledgedAlerts.length
        }
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching alerts analytics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch alerts analytics',
      timestamp: new Date().toISOString()
    })
  }
})

// Helper function to generate mock production data
function generateMockProductionData(period) {
  const data = []
  
  if (period === 'day') {
    // Hourly data for today
    for (let hour = 0; hour < 24; hour++) {
      data.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        production: Math.floor(Math.random() * 10) + 2,
        quality: Math.random() * 20 + 80,
        efficiency: Math.random() * 25 + 70
      })
    }
  } else if (period === 'week') {
    // Daily data for this week
    const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    days.forEach((day, index) => {
      data.push({
        time: day,
        production: Math.floor(Math.random() * 50) + 20,
        quality: Math.random() * 15 + 85,
        efficiency: Math.random() * 20 + 75
      })
    })
  } else {
    // Monthly data
    for (let week = 1; week <= 4; week++) {
      data.push({
        time: `Sem ${week}`,
        production: Math.floor(Math.random() * 200) + 100,
        quality: Math.random() * 10 + 88,
        efficiency: Math.random() * 15 + 80
      })
    }
  }
  
  return data
}

export { router as analyticsRoutes }