import type { Device, AlertMessage } from '@types'

// Mock device data with realistic sensor readings
export const mockDevices: Record<string, Device> = {
  filament: {
    id: 'filament-001',
    name: 'Monitor ESP32 Filamento',
    type: 'filament',
    status: 'online',
    lastUpdate: new Date(),
    sensors: {
      temperature: 210.5, // Hotend temperature (°C)
      bedTemperature: 60.0, // Bed temperature (°C)
      humidity: 15.2, // Filament humidity (%)
      filamentLevel: 75, // Remaining filament percentage
      flowRate: 95.8, // Extrusion flow rate (mm³/s)
      motorTemperature: 42.1, // Stepper motor temperature (°C)
      spoolWeight: 1.2, // Current spool weight (kg)
      totalWeight: 2.5 // Original spool weight (kg)
    },
    settings: {
      targetTemperature: 210,
      targetBedTemperature: 60,
      filamentType: 'PLA',
      diameter: 1.75,
      flowMultiplier: 1.0
    }
  },

  conveyor: {
    id: 'conveyor-001',
    name: 'Esteira Arduino',
    type: 'conveyor',
    status: 'online',
    lastUpdate: new Date(),
    sensors: {
      speed: 150, // mm/s
      position: 0, // Current position (mm)
      totalDistance: 5420, // Total distance moved (mm)
      motorRPM: 85, // Motor RPM
      load: 35, // Current load (%)
      vibration: 0.2, // Vibration level (g)
      temperature: 35.4, // Motor temperature (°C)
      batteryLevel: 78 // Battery level (%)
    },
    settings: {
      speed: 150,
      acceleration: 500,
      deceleration: 500,
      maxPosition: 5000
    }
  },

  qc: {
    id: 'qc-001',
    name: 'Estação QC',
    type: 'qc',
    status: 'online',
    lastUpdate: new Date(),
    sensors: {
      imageResolution: 1080, // Image resolution (pixels)
      accuracy: 0.05, // Measurement accuracy (mm)
      defectDetection: true, // Defect detection active
      classificationAccuracy: 94.2, // AI classification accuracy (%)
      surfaceRoughness: 2.1, // Surface roughness (Ra)
      dimensionalAccuracy: 0.12, // Dimensional accuracy (mm)
      layerAdhesion: 98.5, // Layer adhesion quality (%)
      colorAccuracy: 97.8 // Color consistency (%)
    },
    settings: {
      autoFocus: true,
      flashIntensity: 80,
      aiSensitivity: 85,
      measurementUnits: 'metric'
    }
  }
}

// Mock alerts
export const mockAlerts: AlertMessage[] = [
  {
    id: 'alert-001',
    deviceId: 'filament-001',
    deviceName: 'Monitor ESP32 Filamento',
    severity: 'warning',
    title: 'Filamento Baixo',
    message: 'Nível de filamento está abaixo de 20%. Considere trocar a bobina.',
    timestamp: new Date(Date.now() - 300000), // 5 minutes ago
    acknowledged: false
  },
  {
    id: 'alert-002',
    deviceId: 'conveyor-001',
    deviceName: 'Esteira Arduino',
    severity: 'critical',
    title: 'Sobrecarga Detectada',
    message: 'Carga da esteira excedeu 90%. Verifique se há obstruções.',
    timestamp: new Date(Date.now() - 180000), // 3 minutes ago
    acknowledged: false
  },
  {
    id: 'alert-003',
    deviceId: 'qc-001',
    deviceName: 'Estação QC',
    severity: 'info',
    title: 'Análise Concluída',
    message: 'Análise de qualidade da peça #001 foi concluída com 94% de aprovação.',
    timestamp: new Date(Date.now() - 60000), // 1 minute ago
    acknowledged: false
  }
]

// Mock analytics data
export const mockAnalytics = {
  production: {
    today: 24,
    week: 156,
    month: 743,
    trend: 'up' as const
  },
  quality: {
    passRate: 94.2,
    avgClassification: 'A' as const,
    topDefects: ['layer_shift', 'stringing', 'surface_roughness']
  },
  system: {
    uptime: 8960, // seconds (2h 29m)
    activeDevices: 3,
    totalDevices: 3
  }
}

// Mock chart data
export const mockChartData = {
  labels: [
    '00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
    '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
    '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'
  ],
  datasets: [
    {
      label: 'Produção (peças)',
      data: [2, 1, 0, 0, 1, 2, 3, 5, 4, 6, 5, 4, 6, 7, 5, 6, 4, 3, 2, 1, 0, 1, 2, 1],
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 2,
    },
    {
      label: 'Qualidade (%)',
      data: [92, 95, 88, 90, 96, 94, 93, 95, 97, 94, 96, 95, 97, 94, 96, 95, 93, 94, 95, 96, 94, 95, 93, 94],
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      borderColor: 'rgb(34, 197, 94)',
      borderWidth: 2,
    },
    {
      label: 'Temperatura Média (°C)',
      data: [210, 212, 209, 211, 210, 213, 212, 211, 210, 212, 211, 210, 213, 212, 211, 210, 212, 211, 210, 209, 211, 212, 210, 211],
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      borderColor: 'rgb(239, 68, 68)',
      borderWidth: 2,
    }
  ]
}

// Function to generate random data updates
export const generateRandomUpdate = (device: Device): Device => {
  const updatedDevice = { ...device }
  
  // Add small random variations to sensor readings
  if (updatedDevice.sensors.temperature !== undefined) {
    updatedDevice.sensors.temperature += (Math.random() - 0.5) * 4 // ±2°C
    updatedDevice.sensors.temperature = Math.round(updatedDevice.sensors.temperature * 10) / 10
  }
  
  if (updatedDevice.sensors.filamentLevel !== undefined) {
    updatedDevice.sensors.filamentLevel = Math.max(0, Math.min(100, 
      updatedDevice.sensors.filamentLevel - Math.random() * 0.1))
  }
  
  if (updatedDevice.sensors.humidity !== undefined) {
    updatedDevice.sensors.humidity += (Math.random() - 0.5) * 2 // ±1%
    updatedDevice.sensors.humidity = Math.round(updatedDevice.sensors.humidity * 10) / 10
  }
  
  if (updatedDevice.sensors.speed !== undefined) {
    updatedDevice.sensors.speed += (Math.random() - 0.5) * 10 // ±5 mm/s
  }
  
  updatedDevice.lastUpdate = new Date()
  
  return updatedDevice
}

// Function to generate random alerts
export const generateRandomAlert = (): AlertMessage | null => {
  // 5% chance of generating an alert
  if (Math.random() > 0.95) {
    const deviceIds = Object.keys(mockDevices)
    const deviceId = deviceIds[Math.floor(Math.random() * deviceIds.length)]
    const device = mockDevices[deviceId]
    
    const alertTypes = [
      {
        severity: 'warning' as const,
        title: 'Valor fora do range',
        message: 'Sensor detectou valor fora do range esperado. Verificando...'
      },
      {
        severity: 'info' as const,
        title: 'Manutenção sugerida',
        message: 'Dispositivo funcionando por mais de 24h. Considere manutenção preventiva.'
      }
    ]
    
    const alertType = alertTypes[Math.floor(Math.random() * alertTypes.length)]
    
    return {
      id: `alert-${Date.now()}`,
      deviceId: deviceId,
      deviceName: device.name,
      severity: alertType.severity,
      title: alertType.title,
      message: alertType.message,
      timestamp: new Date(),
      acknowledged: false
    }
  }
  
  return null
}