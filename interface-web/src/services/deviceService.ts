import axios from 'axios'
import type { 
  Device, 
  FilamentDevice, 
  ConveyorDevice, 
  QCDevice, 
  DeviceStatus,
  FilamentData,
  ConveyorData,
  QCData,
  ApiResponse 
} from '@types'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

class DeviceService {
  // Mock data generators for development
  private generateMockFilamentData(): FilamentData {
    return {
      weight: Math.random() * 1000 + 100, // 100-1100g
      temperature: Math.random() * 15 + 20, // 20-35°C
      humidity: Math.random() * 30 + 40, // 40-70%
      batteryLevel: Math.random() * 100, // 0-100%
      estimatedTime: Math.random() * 24, // 0-24 hours
      isSleeping: Math.random() > 0.8,
      calibrationMode: Math.random() > 0.9,
      alertThreshold: { min: 50, max: 900 }
    }
  }

  private generateMockConveyorData(): ConveyorData {
    return {
      speed: Math.random() * 100, // 0-100 rpm
      direction: Math.random() > 0.5 ? 'forward' : 'stopped',
      mode: Math.random() > 0.3 ? 'automatic' : 'manual',
      isRunning: Math.random() > 0.2,
      emergencyStop: false,
      position: Math.random() * 1000, // 0-1000mm
      load: Math.random() * 100, // 0-100%
      motorTemperature: Math.random() * 20 + 25, // 25-45°C
      statusLED: Math.random() > 0.7 ? 'yellow' : 'green'
    }
  }

  private generateMockQCData(): QCData {
    const classifications = ['A', 'B', 'C', 'D', 'F'] as const
    const defects = ['none', 'layer_shift', 'stringing', 'under_extrusion', 'over_extrusion', 'poor_surface', 'dimensional_error', 'support_marks', 'warping']
    
    return {
      lastInspection: {
        id: `qc_${Date.now()}`,
        timestamp: new Date(),
        classification: classifications[Math.floor(Math.random() * classifications.length)],
        confidence: Math.random() * 0.4 + 0.6, // 0.6-1.0
        defectType: Math.random() > 0.7 ? defects[Math.floor(Math.random() * defects.length)] : 'none',
        imagePath: '/images/last_inspection.jpg'
      },
      statistics: {
        totalInspected: Math.floor(Math.random() * 1000) + 100,
        passRate: Math.random() * 30 + 70, // 70-100%
        avgConfidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
        commonDefects: defects.slice(0, 3)
      },
      cameraStatus: Math.random() > 0.9 ? 'disconnected' : 'connected',
      ledStatus: Math.random() > 0.8 ? 'red' : 'green'
    }
  }

  // Mock devices for development
  private createMockDevices() {
    const now = new Date()
    
    return {
      filament: {
        id: 'filament-001',
        name: 'Monitor ESP32 Filamento',
        type: 'filament' as const,
        status: 'online' as DeviceStatus,
        lastUpdate: now,
        ipAddress: '192.168.1.101',
        version: '2.0',
        data: this.generateMockFilamentData()
      } as FilamentDevice,
      
      conveyor: {
        id: 'conveyor-001',
        name: 'Esteira Arduino',
        type: 'conveyor' as const,
        status: 'online' as DeviceStatus,
        lastUpdate: now,
        ipAddress: '192.168.1.102',
        version: '2.0',
        data: this.generateMockConveyorData()
      } as ConveyorDevice,
      
      qc: {
        id: 'qc-001',
        name: 'Estação QC Raspberry Pi',
        type: 'qc' as const,
        status: 'online' as DeviceStatus,
        lastUpdate: now,
        ipAddress: '192.168.1.103',
        version: '2.0',
        data: this.generateMockQCData()
      } as QCDevice
    }
  }

  async getAllDevices() {
    try {
      // In development, return mock data
      if (import.meta.env.DEV) {
        return this.createMockDevices()
      }

      // In production, fetch from real API
      const response = await api.get<ApiResponse<{ filament?: FilamentDevice; conveyor?: ConveyorDevice; qc?: QCDevice }>>('/devices')
      return response.data.data || {}
    } catch (error) {
      console.warn('Failed to fetch devices, using mock data:', error)
      return this.createMockDevices()
    }
  }

  async getDevice(type: 'filament' | 'conveyor' | 'qc') {
    try {
      if (import.meta.env.DEV) {
        const devices = this.createMockDevices()
        return devices[type]
      }

      const response = await api.get<ApiResponse<FilamentDevice | ConveyorDevice | QCDevice>>(`/devices/${type}`)
      return response.data.data
    } catch (error) {
      console.warn(`Failed to fetch ${type} device:`, error)
      const devices = this.createMockDevices()
      return devices[type]
    }
  }

  async updateDeviceConfig(type: 'filament' | 'conveyor' | 'qc', config: any) {
    try {
      const response = await api.put<ApiResponse<void>>(`/devices/${type}/config`, config)
      return response.data
    } catch (error) {
      console.warn(`Failed to update ${type} config:`, error)
      throw error
    }
  }

  async controlDevice(type: 'filament' | 'conveyor' | 'qc', action: string, params?: any) {
    try {
      const response = await api.post<ApiResponse<any>>(`/devices/${type}/control`, {
        action,
        params
      })
      return response.data
    } catch (error) {
      console.warn(`Failed to control ${type} device:`, error)
      throw error
    }
  }

  // ESP32 Filament Monitor specific methods
  async setFilamentThreshold(threshold: { min: number; max: number }) {
    return this.updateDeviceConfig('filament', { alertThreshold: threshold })
  }

  async calibrateFilamentScale() {
    return this.controlDevice('filament', 'calibrate')
  }

  async putFilamentToSleep() {
    return this.controlDevice('filament', 'sleep')
  }

  async wakeFilamentUp() {
    return this.controlDevice('filament', 'wake')
  }

  // Conveyor Belt specific methods
  async setConveyorSpeed(speed: number) {
    return this.controlDevice('conveyor', 'set_speed', { speed })
  }

  async setConveyorDirection(direction: 'forward' | 'reverse' | 'stopped') {
    return this.controlDevice('conveyor', 'set_direction', { direction })
  }

  async toggleConveyorMode() {
    return this.controlDevice('conveyor', 'toggle_mode')
  }

  async emergencyStopConveyor() {
    return this.controlDevice('conveyor', 'emergency_stop')
  }

  async startConveyor() {
    return this.controlDevice('conveyor', 'start')
  }

  async stopConveyor() {
    return this.controlDevice('conveyor', 'stop')
  }

  // QC Station specific methods
  async performQCInspection() {
    return this.controlDevice('qc', 'inspect')
  }

  async getQCStatistics(period: 'day' | 'week' | 'month' = 'day') {
    try {
      const response = await api.get<ApiResponse<any>>(`/qc/statistics?period=${period}`)
      return response.data.data
    } catch (error) {
      console.warn('Failed to fetch QC statistics:', error)
      return null
    }
  }

  async generateQCReport(format: 'pdf' | 'csv' = 'pdf') {
    try {
      const response = await api.get(`/qc/report?format=${format}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.warn('Failed to generate QC report:', error)
      throw error
    }
  }

  // Health check methods
  async checkDeviceHealth(type: 'filament' | 'conveyor' | 'qc') {
    try {
      const response = await api.get<ApiResponse<{ status: string; lastPing: Date; uptime: number }>>(`/devices/${type}/health`)
      return response.data.data
    } catch (error) {
      console.warn(`Failed to check ${type} health:`, error)
      return { status: 'unknown', lastPing: new Date(), uptime: 0 }
    }
  }

  // Historical data methods
  async getHistoricalData(type: 'filament' | 'conveyor' | 'qc', period: 'hour' | 'day' | 'week' = 'day') {
    try {
      const response = await api.get<ApiResponse<any[]>>(`/devices/${type}/history?period=${period}`)
      return response.data.data || []
    } catch (error) {
      console.warn(`Failed to fetch ${type} historical data:`, error)
      return []
    }
  }
}

export const deviceService = new DeviceService()