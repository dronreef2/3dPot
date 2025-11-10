/**
 * DeviceManager - Gerenciador de Dispositivos
 * 
 * Coordena todos os adaptadores de hardware e fornece uma interface unificada
 * para o sistema de controle centralizado
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import EventEmitter from 'events'
import ESP32Adapter from './esp32Adapter.js'
import ArduinoAdapter from './arduinoAdapter.js'
import RaspberryPiAdapter from './raspberryPiAdapter.js'
import { logger } from '../utils/logger.js'
import { broadcastDeviceUpdate, broadcastAlert } from '../socket.js'

class DeviceManager extends EventEmitter {
  constructor() {
    super()
    
    this.adapters = new Map()
    this.deviceStatus = new Map()
    this.isInitialized = false
    this.healthCheckInterval = null
    
    // Configurações de dispositivos
    this.deviceConfigs = {
      esp32: {
        enabled: process.env.ESP32_ENABLED === 'true',
        mqttServer: process.env.MQTT_SERVER,
        mqttPort: parseInt(process.env.MQTT_PORT) || 1883,
        wsPort: parseInt(process.env.ESP32_WS_PORT) || 81
      },
      arduino: {
        enabled: process.env.ARDUINO_ENABLED === 'true',
        port: process.env.ARDUINO_SERIAL_PORT || '/dev/ttyUSB0',
        baudRate: parseInt(process.env.ARDUINO_BAUD_RATE) || 9600
      },
      raspberryPi: {
        enabled: process.env.RASPBERRY_PI_ENABLED === 'true',
        host: process.env.RASPBERRY_PI_HOST,
        port: parseInt(process.env.RASPBERRY_PI_PORT) || 5000
      }
    }
    
    logger.info('DeviceManager inicializado', { deviceCount: Object.keys(this.deviceConfigs).length })
  }

  async initialize() {
    try {
      // Inicializar adaptadores habilitados
      await this.initializeAdapters()
      
      // Configurar event handlers
      this.setupEventHandlers()
      
      // Iniciar health checks
      this.startHealthChecks()
      
      this.isInitialized = true
      this.emit('initialized')
      
      logger.info('DeviceManager inicializado com sucesso', {
        devices: Array.from(this.adapters.keys())
      })
      
    } catch (error) {
      logger.error('Erro ao inicializar DeviceManager', { error: error.message })
      this.emit('error', error)
      throw error
    }
  }

  async initializeAdapters() {
    const initializations = []
    
    // Inicializar ESP32
    if (this.deviceConfigs.esp32.enabled) {
      const esp32Adapter = new ESP32Adapter(this.deviceConfigs.esp32)
      this.adapters.set('esp32', esp32Adapter)
      initializations.push(this.initializeAdapter('esp32', esp32Adapter))
    }
    
    // Inicializar Arduino
    if (this.deviceConfigs.arduino.enabled) {
      const arduinoAdapter = new ArduinoAdapter(this.deviceConfigs.arduino)
      this.adapters.set('arduino', arduinoAdapter)
      initializations.push(this.initializeAdapter('arduino', arduinoAdapter))
    }
    
    // Inicializar Raspberry Pi
    if (this.deviceConfigs.raspberryPi.enabled) {
      const raspberryPiAdapter = new RaspberryPiAdapter(this.deviceConfigs.raspberryPi)
      this.adapters.set('raspberryPi', raspberryPiAdapter)
      initializations.push(this.initializeAdapter('raspberryPi', raspberryPiAdapter))
    }
    
    // Aguardar todas as inicializações
    await Promise.allSettled(initializations)
  }

  async initializeAdapter(deviceType, adapter) {
    try {
      await adapter.connect()
      
      // Configurar status inicial
      const status = await adapter.getDeviceStatus()
      this.deviceStatus.set(deviceType, status)
      
      logger.info(`${deviceType} conectado com sucesso`)
      
    } catch (error) {
      logger.error(`Erro ao conectar ${deviceType}`, { error: error.message })
      
      // Tentar reconectar após delay
      setTimeout(() => {
        this.reconnectDevice(deviceType)
      }, 30000) // 30 segundos
    }
  }

  setupEventHandlers() {
    this.adapters.forEach((adapter, deviceType) => {
      // Status updates
      adapter.on('statusUpdate', (status) => {
        this.deviceStatus.set(deviceType, status)
        this.emit('deviceStatusUpdate', { deviceType, status })
        logger.debug(`Status ${deviceType} atualizado`, { status: status.connected })
      })
      
      // Data updates
      adapter.on('dataUpdate', (data) => {
        this.emit('deviceDataUpdate', { deviceType, data })
        
        // Broadcast para clientes WebSocket
        if (this.io) {
          broadcastDeviceUpdate(this.io, deviceType, data)
        }
      })
      
      // Inspection results (apenas para Raspberry Pi)
      if (deviceType === 'raspberryPi') {
        adapter.on('inspectionResult', (result) => {
          this.emit('inspectionResult', result)
          logger.info('Resultado de inspeção recebido', {
            pieceId: result.pieceId,
            qualityClass: result.qualityClass,
            confidence: result.confidence
          })
        })
      }
      
      // Alerts
      adapter.on('alert', (alert) => {
        this.emit('deviceAlert', alert)
        
        // Broadcast para clientes WebSocket
        if (this.io) {
          broadcastAlert(this.io, alert)
        }
        
        logger.warn('Alerta de dispositivo recebido', {
          device: deviceType,
          severity: alert.severity,
          message: alert.message
        })
      })
      
      // Command responses
      adapter.on('commandResponse', (response) => {
        this.emit('commandResponse', response)
        logger.debug('Resposta de comando', {
          device: deviceType,
          commandId: response.commandId,
          success: response.success
        })
      })
      
      // Connection events
      adapter.on('connected', (status) => {
        this.deviceStatus.set(deviceType, status)
        this.emit('deviceConnected', { deviceType, status })
        logger.info(`${deviceType} conectado`)
      })
      
      adapter.on('disconnected', () => {
        const status = this.deviceStatus.get(deviceType) || {}
        status.connected = false
        this.deviceStatus.set(deviceType, status)
        this.emit('deviceDisconnected', { deviceType })
        logger.warn(`${deviceType} desconectado`)
        
        // Tentar reconectar
        setTimeout(() => {
          this.reconnectDevice(deviceType)
        }, 10000) // 10 segundos
      })
      
      adapter.on('error', (error) => {
        this.emit('deviceError', { deviceType, error })
        logger.error(`Erro no dispositivo ${deviceType}`, { error: error.message })
      })
    })
  }

  startHealthChecks() {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck()
    }, 60000) // A cada minuto
  }

  async performHealthCheck() {
    const healthStatus = {
      timestamp: new Date().toISOString(),
      devices: {}
    }
    
    for (const [deviceType, adapter] of this.adapters) {
      try {
        const status = await adapter.getDeviceStatus()
        healthStatus.devices[deviceType] = {
          online: adapter.isOnline(),
          connected: status.connected,
          lastSeen: status.lastSeen,
          health: 'healthy'
        }
        
        // Verificar se está muito tempo sem dados
        if (status.lastSeen) {
          const lastSeen = new Date(status.lastSeen)
          const timeSinceLastSeen = Date.now() - lastSeen.getTime()
          
          if (timeSinceLastSeen > 300000) { // 5 minutos
            healthStatus.devices[deviceType].health = 'stale'
            logger.warn(`${deviceType} com dados desatualizados`, {
              lastSeen: status.lastSeen
            })
          }
        }
        
      } catch (error) {
        healthStatus.devices[deviceType] = {
          online: false,
          connected: false,
          health: 'error',
          error: error.message
        }
        
        logger.error(`Health check falhou para ${deviceType}`, { error: error.message })
      }
    }
    
    this.emit('healthCheck', healthStatus)
  }

  async reconnectDevice(deviceType) {
    const adapter = this.adapters.get(deviceType)
    if (!adapter) {
      logger.warn(`Adaptador ${deviceType} não encontrado para reconexão`)
      return
    }
    
    try {
      logger.info(`Tentando reconectar ${deviceType}...`)
      await adapter.connect()
      
      const status = await adapter.getDeviceStatus()
      this.deviceStatus.set(deviceType, status)
      
      logger.info(`${deviceType} reconectado com sucesso`)
      
    } catch (error) {
      logger.error(`Falha ao reconectar ${deviceType}`, { error: error.message })
      
      // Tentar novamente após delay maior
      setTimeout(() => {
        this.reconnectDevice(deviceType)
      }, 60000) // 1 minuto
    }
  }

  // Métodos de controle público
  
  async getAllDevicesStatus() {
    const status = {}
    
    for (const [deviceType, adapter] of this.adapters) {
      try {
        status[deviceType] = await adapter.getDeviceStatus()
      } catch (error) {
        status[deviceType] = {
          ...this.deviceStatus.get(deviceType),
          error: error.message
        }
      }
    }
    
    return status
  }

  async getDeviceStatus(deviceType) {
    const adapter = this.adapters.get(deviceType)
    if (!adapter) {
      throw new Error(`Dispositivo ${deviceType} não encontrado`)
    }
    
    return adapter.getDeviceStatus()
  }

  async sendDeviceCommand(deviceType, action, parameters = {}) {
    const adapter = this.adapters.get(deviceType)
    if (!adapter) {
      throw new Error(`Dispositivo ${deviceType} não encontrado`)
    }
    
    if (!adapter.isOnline()) {
      throw new Error(`Dispositivo ${deviceType} está offline`)
    }
    
    return adapter.sendCommand(action, parameters)
  }

  async controlDevice(deviceType, command, parameters = {}) {
    try {
      const result = await this.sendDeviceCommand(deviceType, command, parameters)
      
      logger.info(`Comando enviado para ${deviceType}`, {
        command,
        parameters
      })
      
      return {
        success: true,
        deviceType,
        command,
        result,
        timestamp: new Date().toISOString()
      }
      
    } catch (error) {
      logger.error(`Erro ao enviar comando para ${deviceType}`, {
        command,
        error: error.message
      })
      
      return {
        success: false,
        deviceType,
        command,
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  // Métodos específicos por dispositivo
  
  // ESP32 (Monitor de Filamento)
  async calibrateFilament(scale = null, offset = null) {
    return this.controlDevice('esp32', 'calibrate', { scale, offset })
  }

  async setFilamentThresholds(thresholds) {
    return this.controlDevice('esp32', 'set_thresholds', thresholds)
  }

  async getFilamentData() {
    return this.sendDeviceCommand('esp32', 'get_status')
  }

  // Arduino (Esteira)
  async controlConveyor(command, parameters = {}) {
    return this.controlDevice('arduino', command, parameters)
  }

  async setConveyorSpeed(speed) {
    return this.controlDevice('arduino', 'set_speed', { speed })
  }

  async emergencyStopConveyor() {
    return this.controlDevice('arduino', 'emergency_stop')
  }

  // Raspberry Pi (QC Station)
  async startQCInspection() {
    return this.controlDevice('raspberryPi', 'start_inspection')
  }

  async stopQCInspection() {
    return this.controlDevice('raspberryPi', 'stop_inspection')
  }

  async getQCStatistics() {
    const adapter = this.adapters.get('raspberryPi')
    if (adapter) {
      return adapter.getStatistics()
    }
    throw new Error('Adaptador QC não disponível')
  }

  async getQCInspections(limit = 100) {
    const adapter = this.adapters.get('raspberryPi')
    if (adapter) {
      return adapter.getInspections(limit)
    }
    throw new Error('Adaptador QC não disponível')
  }

  async generateQCReport(format = 'pdf') {
    const adapter = this.adapters.get('raspberryPi')
    if (adapter) {
      return adapter.generateReport(format)
    }
    throw new Error('Adaptador QC não disponível')
  }

  // Gerenciamento de dispositivos
  async enableDevice(deviceType) {
    this.deviceConfigs[deviceType].enabled = true
    const adapter = this.adapters.get(deviceType)
    if (adapter) {
      await this.initializeAdapter(deviceType, adapter)
    }
  }

  async disableDevice(deviceType) {
    this.deviceConfigs[deviceType].enabled = false
    const adapter = this.adapters.get(deviceType)
    if (adapter) {
      await adapter.disconnect()
      this.adapters.delete(deviceType)
    }
  }

  async restartDevice(deviceType) {
    const adapter = this.adapters.get(deviceType)
    if (adapter) {
      await adapter.disconnect()
      await this.initializeAdapter(deviceType, adapter)
    }
  }

  // Getters
  getDevices() {
    return Array.from(this.adapters.keys())
  }

  getDeviceConfig(deviceType) {
    return this.deviceConfigs[deviceType]
  }

  isDeviceOnline(deviceType) {
    const adapter = this.adapters.get(deviceType)
    return adapter ? adapter.isOnline() : false
  }

  getSystemHealth() {
    const health = {
      timestamp: new Date().toISOString(),
      overall: 'healthy',
      devices: {},
      statistics: {
        totalDevices: this.adapters.size,
        onlineDevices: 0,
        offlineDevices: 0
      }
    }
    
    for (const [deviceType, adapter] of this.adapters) {
      const isOnline = adapter.isOnline()
      health.devices[deviceType] = isOnline ? 'online' : 'offline'
      
      if (isOnline) {
        health.statistics.onlineDevices++
      } else {
        health.statistics.offlineDevices++
      }
    }
    
    if (health.statistics.offlineDevices > 0) {
      health.overall = health.statistics.offlineDevices === health.statistics.totalDevices 
        ? 'critical' 
        : 'degraded'
    }
    
    return health
  }

  // Cleanup
  async shutdown() {
    logger.info('Iniciando shutdown do DeviceManager...')
    
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval)
    }
    
    const disconnectPromises = []
    this.adapters.forEach((adapter) => {
      disconnectPromises.push(adapter.disconnect())
    })
    
    await Promise.allSettled(disconnectPromises)
    
    this.adapters.clear()
    this.deviceStatus.clear()
    this.isInitialized = false
    
    logger.info('DeviceManager finalizado')
    this.emit('shutdown')
  }

  // Setter para acessar o io do socket
  setSocketIO(io) {
    this.io = io
  }
}

export default DeviceManager
