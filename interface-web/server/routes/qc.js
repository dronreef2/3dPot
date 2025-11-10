import express from 'express'
import { qcQueries, alertQueries, getDatabase } from '../database.js'

const router = express.Router()

// Perform QC inspection
router.post('/inspect', async (req, res) => {
  try {
    // In production, this would trigger actual inspection
    // For now, we'll simulate an inspection
    
    const inspection = {
      id: `qc_${Date.now()}`,
      classification: ['A', 'B', 'C', 'D', 'F'][Math.floor(Math.random() * 5)],
      confidence: Math.random() * 0.4 + 0.6,
      defectType: Math.random() > 0.7 ? 
        ['layer_shift', 'stringing', 'under_extrusion', 'surface_roughness'][Math.floor(Math.random() * 4)] : 
        'none',
      timestamp: new Date().toISOString()
    }
    
    // Store in database
    const db = getDatabase()
    const insertResult = qcQueries.insertInspection.run(
      'qc-001',
      inspection.id,
      inspection.classification,
      inspection.confidence,
      inspection.defectType,
      null, // image_path
      'connected',
      inspection.confidence > 0.8 ? 'green' : inspection.confidence > 0.6 ? 'yellow' : 'red'
    )
    
    res.json({
      success: true,
      data: inspection,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error performing inspection:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to perform inspection',
      timestamp: new Date().toISOString()
    })
  }
})

// Get QC statistics
router.get('/statistics', async (req, res) => {
  try {
    const { period = 'day' } = req.query
    
    const db = getDatabase()
    
    let dateFilter = '1 day'
    if (period === 'week') dateFilter = '7 days'
    if (period === 'month') dateFilter = '30 days'
    
    // Get quality statistics
    const stats = db.prepare(`
      SELECT 
        classification,
        COUNT(*) as count,
        AVG(confidence) as avg_confidence,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-${dateFilter}')
      GROUP BY classification
      ORDER BY count DESC
    `).all()
    
    // Calculate overall statistics
    const totalInspected = stats.reduce((sum, stat) => sum + stat.count, 0)
    const passRate = stats
      .filter(stat => ['A', 'B'].includes(stat.classification))
      .reduce((sum, stat) => sum + stat.percentage, 0)
    
    const avgConfidence = totalInspected > 0 ? 
      stats.reduce((sum, stat) => sum + (stat.avg_confidence * stat.count), 0) / totalInspected : 0
    
    // Get common defects
    const defects = db.prepare(`
      SELECT 
        defect_type,
        COUNT(*) as count
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-${dateFilter}')
        AND defect_type != 'none'
        AND defect_type IS NOT NULL
      GROUP BY defect_type
      ORDER BY count DESC
      LIMIT 5
    `).all()
    
    const commonDefects = defects.map(defect => defect.defect_type)
    
    const statistics = {
      totalInspected,
      passRate,
      avgConfidence,
      commonDefects,
      period,
      breakdown: stats
    }
    
    res.json({
      success: true,
      data: statistics,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching QC statistics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch QC statistics',
      timestamp: new Date().toISOString()
    })
  }
})

// Get recent inspections
router.get('/inspections', async (req, res) => {
  try {
    const { limit = 50, deviceId = 'qc-001' } = req.query
    
    const inspections = qcQueries.getRecentInspections.all(deviceId)
    
    res.json({
      success: true,
      data: inspections,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching inspections:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch inspections',
      timestamp: new Date().toISOString()
    })
  }
})

// Generate QC report
router.get('/report', async (req, res) => {
  try {
    const { format = 'pdf', period = 'day' } = req.query
    
    if (format === 'pdf') {
      // Generate PDF report
      const PDFDocument = (await import('pdfkit')).default
      const doc = new PDFDocument()
      
      // Set response headers
      res.setHeader('Content-Type', 'application/pdf')
      res.setHeader('Content-Disposition', `attachment; filename="qc-report-${period}-${new Date().toISOString().split('T')[0]}.pdf"`)
      
      // Pipe the PDF to response
      doc.pipe(res)
      
      // Add content to PDF
      doc.fontSize(20).text('3dPot QC Report', { align: 'center' })
      doc.moveDown()
      doc.fontSize(12).text(`Report Period: ${period}`)
      doc.text(`Generated: ${new Date().toLocaleDateString()}`)
      doc.moveDown()
      
      // Add statistics
      doc.fontSize(16).text('Quality Statistics', { underline: true })
      doc.moveDown(0.5)
      
      const stats = await qcQueries.getQualityStats('qc-001')
      stats.forEach(stat => {
        doc.fontSize(12).text(`Classification ${stat.classification}: ${stat.count} pieces (${stat.percentage.toFixed(1)}%)`)
      })
      
      doc.end()
    } else {
      // Return JSON data for other formats
      const stats = await qcQueries.getQualityStats('qc-001')
      const data = {
        period,
        generatedAt: new Date().toISOString(),
        statistics: stats
      }
      
      if (format === 'json') {
        res.setHeader('Content-Type', 'application/json')
        res.json(data)
      } else {
        res.status(400).json({
          success: false,
          error: 'Unsupported format'
        })
      }
    }
  } catch (error) {
    console.error('Error generating report:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to generate report',
      timestamp: new Date().toISOString()
    })
  }
})

// Get inspection by ID
router.get('/inspections/:inspectionId', async (req, res) => {
  try {
    const { inspectionId } = req.params
    
    const db = getDatabase()
    const inspection = db.prepare(`
      SELECT * FROM qc_inspections WHERE inspection_id = ?
    `).get(inspectionId)
    
    if (!inspection) {
      return res.status(404).json({
        success: false,
        error: 'Inspection not found'
      })
    }
    
    res.json({
      success: true,
      data: inspection,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching inspection:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch inspection',
      timestamp: new Date().toISOString()
    })
  }
})

// Update camera settings
router.put('/camera', async (req, res) => {
  try {
    const { brightness, contrast, exposure } = req.body
    
    console.log('Updating camera settings:', { brightness, contrast, exposure })
    
    // In production, this would update actual camera settings
    res.json({
      success: true,
      message: 'Camera settings updated',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error updating camera settings:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to update camera settings',
      timestamp: new Date().toISOString()
    })
  }
})

// Get quality trends
router.get('/trends', async (req, res) => {
  try {
    const { period = 'week' } = req.query
    
    const db = getDatabase()
    let dateGrouping = 'day'
    let dateRange = '7 days'
    
    if (period === 'month') {
      dateGrouping = 'week'
      dateRange = '30 days'
    } else if (period === 'year') {
      dateGrouping = 'month'
      dateRange = '365 days'
    }
    
    const trends = db.prepare(`
      SELECT 
        strftime('%Y-%m-%d', created_at) as date,
        COUNT(*) as total_inspections,
        AVG(CASE WHEN classification IN ('A', 'B') THEN 1.0 ELSE 0.0 END) * 100 as pass_rate,
        AVG(confidence) as avg_confidence
      FROM qc_inspections
      WHERE device_id = 'qc-001' 
        AND created_at >= date('now', '-${dateRange}')
      GROUP BY date
      ORDER BY date
    `).all()
    
    res.json({
      success: true,
      data: trends,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error fetching quality trends:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to fetch quality trends',
      timestamp: new Date().toISOString()
    })
  }
})

export { router as qcRoutes }