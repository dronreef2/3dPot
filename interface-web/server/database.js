import Database from 'better-sqlite3'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let db

export function initializeDatabase() {
  try {
    // Create database connection
    const dbPath = path.join(__dirname, '../data/3dpot.db')
    db = new Database(dbPath)
    
    // Enable foreign keys
    db.pragma('foreign_keys = ON')
    
    // Create tables
    createTables()
    
    console.log('✅ Database initialized successfully')
    return db
  } catch (error) {
    console.error('❌ Database initialization failed:', error)
    throw error
  }
}

function createTables() {
  // Device status table
  db.exec(`
    CREATE TABLE IF NOT EXISTS devices (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      device_id TEXT UNIQUE NOT NULL,
      device_name TEXT NOT NULL,
      device_type TEXT NOT NULL CHECK(device_type IN ('filament', 'conveyor', 'qc')),
      status TEXT NOT NULL CHECK(status IN ('online', 'offline', 'warning', 'error')),
      ip_address TEXT,
      version TEXT,
      last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
      data TEXT, -- JSON data
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // Filament readings table
  db.exec(`
    CREATE TABLE IF NOT EXISTS filament_readings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      device_id TEXT NOT NULL,
      weight REAL NOT NULL,
      temperature REAL,
      humidity REAL,
      battery_level INTEGER,
      estimated_time REAL,
      is_sleeping BOOLEAN DEFAULT FALSE,
      calibration_mode BOOLEAN DEFAULT FALSE,
      alert_threshold_min REAL DEFAULT 50,
      alert_threshold_max REAL DEFAULT 900,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (device_id) REFERENCES devices (device_id) ON DELETE CASCADE
    )
  `)

  // Conveyor data table
  db.exec(`
    CREATE TABLE IF NOT EXISTS conveyor_data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      device_id TEXT NOT NULL,
      speed REAL NOT NULL,
      direction TEXT CHECK(direction IN ('forward', 'reverse', 'stopped')) DEFAULT 'stopped',
      mode TEXT CHECK(mode IN ('manual', 'automatic')) DEFAULT 'manual',
      is_running BOOLEAN DEFAULT FALSE,
      emergency_stop BOOLEAN DEFAULT FALSE,
      position REAL,
      load REAL,
      motor_temperature REAL,
      status_led TEXT CHECK(status_led IN ('green', 'yellow', 'red', 'off')) DEFAULT 'off',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (device_id) REFERENCES devices (device_id) ON DELETE CASCADE
    )
  `)

  // QC inspections table
  db.exec(`
    CREATE TABLE IF NOT EXISTS qc_inspections (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      device_id TEXT NOT NULL,
      inspection_id TEXT UNIQUE NOT NULL,
      classification TEXT CHECK(classification IN ('A', 'B', 'C', 'D', 'F')) NOT NULL,
      confidence REAL NOT NULL,
      defect_type TEXT,
      image_path TEXT,
      camera_status TEXT CHECK(camera_status IN ('connected', 'disconnected', 'calibrating')) DEFAULT 'connected',
      led_status TEXT CHECK(led_status IN ('green', 'yellow', 'red', 'off')) DEFAULT 'off',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (device_id) REFERENCES devices (device_id) ON DELETE CASCADE
    )
  `)

  // System alerts table
  db.exec(`
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      device_id TEXT,
      device_name TEXT,
      severity TEXT CHECK(severity IN ('info', 'warning', 'critical')) NOT NULL,
      title TEXT NOT NULL,
      message TEXT NOT NULL,
      acknowledged BOOLEAN DEFAULT FALSE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // System analytics table
  db.exec(`
    CREATE TABLE IF NOT EXISTS analytics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      metric_name TEXT NOT NULL,
      metric_value REAL NOT NULL,
      metric_unit TEXT,
      period TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // Create indexes for better performance
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(device_type)
    CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)
    CREATE INDEX IF NOT EXISTS idx_filament_readings_device ON filament_readings(device_id)
    CREATE INDEX IF NOT EXISTS idx_filament_readings_created ON filament_readings(created_at)
    CREATE INDEX IF NOT EXISTS idx_conveyor_data_device ON conveyor_data(device_id)
    CREATE INDEX IF NOT EXISTS idx_conveyor_data_created ON conveyor_data(created_at)
    CREATE INDEX IF NOT EXISTS idx_qc_inspections_device ON qc_inspections(device_id)
    CREATE INDEX IF NOT EXISTS idx_qc_inspections_created ON qc_inspections(created_at)
    CREATE INDEX IF NOT EXISTS idx_alerts_device ON alerts(device_id)
    CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)
    CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)
  `)
}

export function getDatabase() {
  if (!db) {
    throw new Error('Database not initialized. Call initializeDatabase() first.')
  }
  return db
}

// Utility functions for database operations
export const deviceQueries = {
  // Insert or update device
  upsertDevice: db.prepare(`
    INSERT INTO devices (device_id, device_name, device_type, status, ip_address, version, data, last_update)
    VALUES (@device_id, @device_name, @device_type, @status, @ip_address, @version, @data, CURRENT_TIMESTAMP)
    ON CONFLICT(device_id) DO UPDATE SET
      device_name = excluded.device_name,
      status = excluded.status,
      ip_address = excluded.ip_address,
      version = excluded.version,
      data = excluded.data,
      last_update = CURRENT_TIMESTAMP
  `),

  // Get all devices
  getAllDevices: db.prepare(`
    SELECT * FROM devices ORDER BY device_type, device_name
  `),

  // Get device by ID
  getDevice: db.prepare(`
    SELECT * FROM devices WHERE device_id = ?
  `),

  // Get device by type
  getDeviceByType: db.prepare(`
    SELECT * FROM devices WHERE device_type = ? ORDER BY created_at DESC LIMIT 1
  `)
}

export const filamentQueries = {
  // Insert filament reading
  insertReading: db.prepare(`
    INSERT INTO filament_readings (
      device_id, weight, temperature, humidity, battery_level, estimated_time,
      is_sleeping, calibration_mode, alert_threshold_min, alert_threshold_max
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `),

  // Get recent readings
  getRecentReadings: db.prepare(`
    SELECT * FROM filament_readings 
    WHERE device_id = ? AND created_at > datetime('now', '-24 hours')
    ORDER BY created_at DESC LIMIT 100
  `),

  // Get historical data
  getHistoricalData: db.prepare(`
    SELECT 
      DATE(created_at) as date,
      AVG(weight) as avg_weight,
      AVG(temperature) as avg_temperature,
      MIN(battery_level) as min_battery,
      COUNT(*) as reading_count
    FROM filament_readings
    WHERE device_id = ? AND created_at >= date('now', '-30 days')
    GROUP BY DATE(created_at)
    ORDER BY date DESC
  `)
}

export const conveyorQueries = {
  // Insert conveyor data
  insertData: db.prepare(`
    INSERT INTO conveyor_data (
      device_id, speed, direction, mode, is_running, emergency_stop,
      position, load, motor_temperature, status_led
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `),

  // Get recent data
  getRecentData: db.prepare(`
    SELECT * FROM conveyor_data
    WHERE device_id = ? AND created_at > datetime('now', '-24 hours')
    ORDER BY created_at DESC LIMIT 100
  `)
}

export const qcQueries = {
  // Insert inspection
  insertInspection: db.prepare(`
    INSERT INTO qc_inspections (
      device_id, inspection_id, classification, confidence, defect_type,
      image_path, camera_status, led_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `),

  // Get recent inspections
  getRecentInspections: db.prepare(`
    SELECT * FROM qc_inspections
    WHERE device_id = ? AND created_at > datetime('now', '-24 hours')
    ORDER BY created_at DESC LIMIT 50
  `),

  // Get quality statistics
  getQualityStats: db.prepare(`
    SELECT 
      classification,
      COUNT(*) as count,
      AVG(confidence) as avg_confidence,
      COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
    FROM qc_inspections
    WHERE device_id = ? AND created_at >= date('now', '-7 days')
    GROUP BY classification
    ORDER BY count DESC
  `)
}

export const alertQueries = {
  // Insert alert
  insertAlert: db.prepare(`
    INSERT INTO alerts (device_id, device_name, severity, title, message, acknowledged)
    VALUES (?, ?, ?, ?, ?, ?)
  `),

  // Get recent alerts
  getRecentAlerts: db.prepare(`
    SELECT * FROM alerts
    WHERE created_at > datetime('now', '-7 days')
    ORDER BY created_at DESC LIMIT 50
  `),

  // Get unacknowledged alerts
  getUnacknowledgedAlerts: db.prepare(`
    SELECT * FROM alerts
    WHERE acknowledged = FALSE
    ORDER BY created_at DESC
  `),

  // Acknowledge alert
  acknowledgeAlert: db.prepare(`
    UPDATE alerts SET acknowledged = TRUE WHERE id = ?
  `)
}

export const analyticsQueries = {
  // Insert metric
  insertMetric: db.prepare(`
    INSERT INTO analytics (metric_name, metric_value, metric_unit, period)
    VALUES (?, ?, ?, ?)
  `),

  // Get metrics by period
  getMetrics: db.prepare(`
    SELECT * FROM analytics
    WHERE period = ? AND created_at >= date('now', '-30 days')
    ORDER BY created_at DESC
  `)
}