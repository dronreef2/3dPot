/**
 * Raspberry Pi Estação QC - Adaptador de Comunicação
 * 
 * Integra com o Raspberry Pi através de API REST e WebSocket
 * Protocolo baseado em JSON para comunicação bidirecional
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import axios from 'axios'
import WebSocket from 'ws'
import EventEmitter from 'events'
import { logger } from '../utils/logger.js'

class RaspberryPiAdapter extends EventEmitter {
  constructor(config = {}) {
    super()
    
    this.config = {
      host: process.env.RASPBERRY_PI_HOST || '192.168.1.100',
      port: parseInt(process.env.RASPBERRY_PI_PORT) || 5000,
      username: process.env.RASPBERRY_PI_USER || 'pi',
      password: process.env.RASPBERRY_PI_PASSWORD || '',
      deviceId: 'raspberry_pi_qc_001',
      heartbeatInterval: 30000, // 30 segundos
      commandTimeout: 10000, // 10 segundos
      maxRetries: 3,
      apiTimeout: 5000, // 5 segundos para API
      ...config
    }
    
    this.baseURL = `http://${this.config.host}:${this.config.port}`
    this.wsURL = `ws://${this.config.host}:${this.config.port}/ws`
    
    this.deviceStatus = {
      id: this.config.deviceId,
      type: 'qc',
      connected: false,
      lastSeen: null,
      firmware: '2.0',
      cameraStatus: false,
      ledStatus: 'off',
      databaseStatus: false,
      cpuUsage: 0,
      memoryUsage: 0,
      diskUsage: 0,
      piecesAnalyzed: 0,
      avgProcessingTime: 0,
      lastAnalysis: null
    }
    
    this.websocket = null
    this.isConnected = false
    this.commandQueue = []
    this.authToken = null
    this.apiClient = null
    
    this.setupAPIClient()
    
    logger.info('Raspberry Pi Adapter inicializado', { 
      deviceId: this.config.deviceId,
      host: this.config.host,
      port: this.config.port 
    })
  }

  setupAPIClient() {
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: this.config.apiTimeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': '3dPot-Backend/1.0'
      }
    })

    // Interceptor para autenticação
    this.apiClient.interceptors.request.use((config) => {
      if (this.authToken) {
        config.headers['Authorization'] = `Bearer ${this.authToken}`
      }
      return config
    })

    // Interceptor para tratamento de erros
    this.apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          logger.warn('Token expirado, tentando reautenticar...')
          return this.authenticate().then(() => {
            error.config.headers['Authorization'] = `Bearer ${this.authToken}`
            return this.apiClient.request(error.config)
          })
        }
        return Promise.reject(error)
      }
    )
  }

  async connect() {
    try {
      await this.authenticate()
      await this.connectWebSocket()
      await this.getInitialStatus()
      this.startHeartbeat()
      this.setupEventHandlers()
      
      this.isConnected = true
      this.deviceStatus.connected = true
      this.deviceStatus.lastSeen = new Date().toISOString()
      
      this.emit('connected', this.deviceStatus)
      logger.info('Raspberry Pi QC conectado com sucesso', { deviceId: this.deviceId })
      
    } catch (error) {
      logger.error('Falha ao conectar Raspberry Pi QC', { error: error.message })
      this.emit('error', error)
      throw error
    }
  }

  async authenticate() {
    try {
      const response = await this.apiClient.post('/api/auth/login', {
        username: this.config.username,
        password: this.config.password
      })
      
      this.authToken = response.data.token
      logger.info('Autenticação Raspberry Pi bem-sucedida', { 
        deviceId: this.config.deviceId 
      })
      
    } catch (error) {
      logger.error('Falha na autenticação Raspberry Pi', { 
        error: error.message,
        host: this.config.host 
      })
      throw new Error('Falha na autenticação com Raspberry Pi')
    }
  }

  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      this.websocket = new WebSocket(this.wsURL, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      })
      
      this.websocket.on('open', () => {
        logger.info('WebSocket Raspberry Pi conectado', { url: this.wsURL })
        resolve()
      })

      this.websocket.on('error', (error) => {
        logger.error('Erro WebSocket Raspberry Pi', { error: error.message })
        reject(error)
      })

      this.websocket.on('close', () => {
        this.handleDisconnection()
      })

      this.websocket.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString())
          this.handleWebSocketMessage(message)
        } catch (error) {
          logger.error('Erro ao processar mensagem WebSocket', { 
            error: error.message 
          })
        }
      })
    })
  }

  handleWebSocketMessage(message) {
    const { type, payload } = message
    const timestamp = new Date().toISOString()

    switch (type) {
      case 'status':
        this.handleStatusUpdate(payload, timestamp)
        break
        
      case 'inspection_result':
        this.handleInspectionResult(payload, timestamp)
        break
        
      case 'alert':
        this.handleAlert(payload, timestamp)
        break
        
      case 'system_update':
        this.handleSystemUpdate(payload, timestamp)
        break
        
      case 'response':
        this.handleResponse(payload, timestamp)
        break
        
      default:
        logger.warn('Tipo de mensagem WebSocket não reconhecido', { type })
    }
  }

  handleStatusUpdate(payload, timestamp) {
    this.deviceStatus = {
      ...this.deviceStatus,
      ...payload,
      lastSeen: timestamp,
      connected: true
    }
    
    this.emit('statusUpdate', this.deviceStatus)
    logger.debug('Status Raspberry Pi QC atualizado', { 
      cameraStatus: payload.cameraStatus,
      piecesAnalyzed: payload.piecesAnalyzed 
    })
  }

  handleInspectionResult(payload, timestamp) {
    const inspectionData = {
      deviceId: this.deviceStatus.id,
      timestamp,
      pieceId: payload.piece_id,
      qualityClass: payload.quality_class,
      confidence: payload.confidence,
      defectsFound: payload.defects_found,
      area: payload.area,
      aspectRatio: payload.aspect_ratio,
      contrast: payload.contrast,
      imagePath: payload.image_path,
      processingTime: payload.processing_time
    }
    
    this.emit('inspectionResult', inspectionData)
    
    // Atualizar estatísticas
    this.deviceStatus.piecesAnalyzed++
    this.deviceStatus.avgProcessingTime = 
      (this.deviceStatus.avgProcessingTime + payload.processing_time) / 2
    this.deviceStatus.lastAnalysis = timestamp
    
    logger.debug('Resultado de inspeção recebido', { 
      pieceId: payload.piece_id,
      qualityClass: payload.quality_class,
      confidence: payload.confidence 
    })
  }

  handleAlert(payload, timestamp) {
    const alert = {
      id: `raspberry_pi_${Date.now()}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'qc',
      severity: payload.severity || 'warning',
      title: payload.title || 'Alerta QC',
      message: payload.message,
      timestamp,
      acknowledged: false,
      data: payload.data || {}
    }
    
    this.emit('alert', alert)
    logger.warn('Alerta Raspberry Pi QC recebido', { 
      severity: alert.severity, 
      message: alert.message 
    })
  }

  handleSystemUpdate(payload, timestamp) {
    // Atualizar informações do sistema
    this.deviceStatus.cpuUsage = payload.cpu_usage
    this.deviceStatus.memoryUsage = payload.memory_usage
    this.deviceStatus.diskUsage = payload.disk_usage
    this.deviceStatus.ledStatus = payload.led_status
    
    this.emit('systemUpdate', {
      ...payload,
      timestamp
    })
  }

  handleResponse(payload, timestamp) {
    const { commandId, success, result, error } = payload
    
    const pendingCommand = this.commandQueue.find(cmd => cmd.id === commandId)
    if (pendingCommand) {
      clearTimeout(pendingCommand.timeout)
      this.commandQueue = this.commandQueue.filter(cmd => cmd.id !== commandId)
      
      const response = {
        commandId,
        success,
        result,
        error,
        timestamp
      }
      
      this.emit('commandResponse', response)
      logger.debug('Comando Raspberry Pi QC processado', { commandId, success })
    }
  }

  handleDisconnection() {
    this.isConnected = false
    this.deviceStatus.connected = false
    
    this.emit('disconnected')
    logger.warn('Raspberry Pi QC desconectado', { deviceId: this.deviceId })
  }

  sendAlert(severity, title, message, data = {}) {
    const alert = {
      id: `raspberry_pi_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'qc',
      severity,
      title,
      message,
      timestamp: new Date().toISOString(),
      acknowledged: false,
      data
    }
    
    this.emit('alert', alert)
  }

  async sendCommand(action, parameters = {}) {
    return new Promise((resolve, reject) => {
      const commandId = `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const command = {
        id: commandId,
        action,
        parameters,
        timestamp: new Date().toISOString()
      }
      
      // Enviar via WebSocket
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify({
          type: 'command',
          payload: command
        }))
      }
      
      // Adicionar timeout
      const timeout = setTimeout(() => {
        this.commandQueue = this.commandQueue.filter(cmd => cmd.id !== commandId)
        reject(new Error(`Timeout: Comando ${action} não respondida`))
      }, this.config.commandTimeout)
      
      this.commandQueue.push({ ...command, timeout })
      
      logger.info('Comando Raspberry Pi QC enviado', { action, commandId })
      
      // Aguardar resposta
      this.once(`response_${commandId}`, (response) => {
        if (response.success) {
          resolve(response.result)
        } else {
          reject(new Error(response.error || 'Comando falhou'))
        }
      })
    })
  }

  async getInitialStatus() {
    try {
      const response = await this.apiClient.get('/api/status')
      this.handleStatusUpdate(response.data, new Date().toISOString())
    } catch (error) {
      logger.error('Erro ao obter status inicial', { error: error.message })
    }
  }

  startHeartbeat() {
    setInterval(async () => {
      if (this.isConnected) {
        try {
          await this.sendCommand('PING', { timestamp: Date.now() })
        } catch (error) {
          logger.debug('Heartbeat falhou', { error: error.message })
        }
      }
    }, this.config.heartbeatInterval)
  }

  setupEventHandlers() {
    // Processar respostas de comando
    this.on('commandResponse', (response) => {
      const commandId = response.commandId || 'unknown'
      this.emit(`response_${commandId}`, response)
    })
  }

  // Métodos de controle específicos
  async startInspection() {
    return this.sendCommand('start_inspection')
  }

  async stopInspection() {
    return this.sendCommand('stop_inspection')
  }

  async setLEDStatus(status) {
    return this.sendCommand('set_led', { status })
  }

  async getStatistics() {
    return this.apiClient.get('/api/statistics')
  }

  async getInspections(limit = 100) {
    return this.apiClient.get('/api/inspections', {
      params: { limit }
    })
  }

  async generateReport(format = 'pdf') {
    return this.apiClient.get('/api/report', {
      params: { format }
    })
  }

  async getCameraStatus() {
    return this.apiClient.get('/api/camera/status')
  }

  async calibrateCamera() {
    return this.sendCommand('calibrate_camera')
  }

  async getSystemInfo() {
    return this.apiClient.get('/api/system/info')
  }

  async setQualityStandards(standards) {
    return this.sendCommand('set_quality_standards', standards)
  }

  async getQualityStandards() {
    return this.sendCommand('get_quality_standards')
  }

  async getDeviceStatus() {
    return {
      ...this.deviceStatus,
      connected: this.isConnected,
      commandQueueLength: this.commandQueue.length,
      websocketConnected: this.websocket?.readyState === WebSocket.OPEN,
      authenticated: !!this.authToken
    }
  }

  async disconnect() {
    this.isConnected = false
    this.deviceStatus.connected = false
    
    if (this.websocket) {
      this.websocket.close()
    }
    
    this.commandQueue.forEach(cmd => clearTimeout(cmd.timeout))
    this.commandQueue = []
    
    this.emit('disconnected')
    logger.info('Raspberry Pi QC desconectado', { deviceId: this.deviceId })
  }

  // Getters para interface
  get deviceId() {
    return this.config.deviceId
  }

  get deviceType() {
    return 'qc'
  }

  isOnline() {
    return this.isConnected
  }
}

export default RaspberryPiAdapter
