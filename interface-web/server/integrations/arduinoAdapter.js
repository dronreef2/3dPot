/**
 * Arduino Esteira Transportadora - Adaptador de Comunicação
 * 
 * Integra com o Arduino através de comunicação serial via USB
 * Protocolo baseado em comandos simples e respostas estruturadas
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import { SerialPort } from 'serialport'
import { ReadlineParser } from '@serialport/parser-readline'
import EventEmitter from 'events'
import { logger } from '../utils/logger.js'

class ArduinoAdapter extends EventEmitter {
  constructor(config = {}) {
    super()
    
    this.config = {
      port: process.env.ARDUINO_SERIAL_PORT || '/dev/ttyUSB0',
      baudRate: parseInt(process.env.ARDUINO_BAUD_RATE) || 9600,
      deviceId: 'arduino_conveyor_001',
      heartbeatInterval: 15000, // 15 segundos
      commandTimeout: 3000, // 3 segundos
      maxRetries: 3,
      ...config
    }
    
    this.deviceStatus = {
      id: this.config.deviceId,
      type: 'conveyor',
      connected: false,
      lastSeen: null,
      firmware: '2.0',
      state: 'IDLE',
      mode: 'manual',
      currentSpeed: 0,
      maxSpeed: 200,
      totalPieces: 0,
      totalRuntime: 0,
      errorCount: 0,
      lastError: null
    }
    
    this.serialPort = null
    this.parser = null
    this.isConnected = false
    this.commandQueue = []
    this.pendingCommands = new Map()
    
    logger.info('Arduino Adapter inicializado', { 
      deviceId: this.config.deviceId,
      port: this.config.port 
    })
  }

  async connect() {
    try {
      await this.connectSerial()
      this.startHeartbeat()
      this.setupEventHandlers()
      
      this.isConnected = true
      this.deviceStatus.connected = true
      this.deviceStatus.lastSeen = new Date().toISOString()
      
      this.emit('connected', this.deviceStatus)
      logger.info('Arduino conectado com sucesso', { deviceId: this.deviceId })
      
      // Enviar comando de inicialização
      await this.initializeDevice()
      
    } catch (error) {
      logger.error('Falha ao conectar Arduino', { error: error.message })
      this.emit('error', error)
      throw error
    }
  }

  async connectSerial() {
    return new Promise((resolve, reject) => {
      this.serialPort = new SerialPort({
        path: this.config.port,
        baudRate: this.config.baudRate
      }, (err) => {
        if (err) {
          reject(new Error(`Erro ao abrir porta serial: ${err.message}`))
          return
        }
        
        this.parser = this.serialPort.pipe(new ReadlineParser({ delimiter: '\n' }))
        
        this.parser.on('data', (data) => {
          this.handleIncomingData(data)
        })
        
        this.serialPort.on('error', (error) => {
          logger.error('Erro na porta serial', { error: error.message })
          this.emit('error', error)
        })
        
        this.serialPort.on('close', () => {
          this.handleDisconnection()
        })
        
        logger.info('Porta serial aberta', { 
          port: this.config.port,
          baudRate: this.config.baudRate 
        })
        resolve()
      })
    })
  }

  handleIncomingData(data) {
    const timestamp = new Date().toISOString()
    const cleanData = data.toString().trim()
    
    // Log para debug (sem dados sensíveis)
    logger.debug('Dados recebidos do Arduino', { 
      length: cleanData.length,
      preview: cleanData.substring(0, 50)
    })
    
    try {
      // Tentar parser como JSON primeiro
      if (cleanData.startsWith('{')) {
        const jsonData = JSON.parse(cleanData)
        this.handleJSONMessage(jsonData, timestamp)
      } else {
        // Parser como protocolo de texto simples
        this.handleTextMessage(cleanData, timestamp)
      }
    } catch (error) {
      logger.error('Erro ao processar dados do Arduino', { 
        data: cleanData.substring(0, 100),
        error: error.message 
      })
    }
  }

  handleJSONMessage(data, timestamp) {
    const { type, payload } = data
    
    switch (type) {
      case 'STATUS':
        this.handleStatusUpdate(payload, timestamp)
        break
      case 'DATA':
        this.handleDataUpdate(payload, timestamp)
        break
      case 'ALERT':
        this.handleAlert(payload, timestamp)
        break
      case 'RESPONSE':
        this.handleResponse(payload, timestamp)
        break
      default:
        logger.warn('Tipo JSON não reconhecido', { type })
    }
  }

  handleTextMessage(data, timestamp) {
    // Protocolo de texto simples baseado no código do Arduino
    const [command, ...params] = data.split(':')
    
    switch (command.toUpperCase()) {
      case 'STATE':
        this.handleStateUpdate(params[0], timestamp)
        break
      case 'SPEED':
        this.handleSpeedUpdate(parseInt(params[0]) || 0, timestamp)
        break
      case 'MODE':
        this.handleModeUpdate(params[0], timestamp)
        break
      case 'PIECES':
        this.handlePiecesUpdate(parseInt(params[0]) || 0, timestamp)
        break
      case 'RUNTIME':
        this.handleRuntimeUpdate(parseInt(params[0]) || 0, timestamp)
        break
      case 'ERROR':
        this.handleError(params.join(':'), timestamp)
        break
      case 'OK':
        this.handleOKResponse(params[0], timestamp)
        break
      case 'ERR':
        this.handleErrorResponse(params.join(':'), timestamp)
        break
      default:
        logger.debug('Comando de texto não processado', { command })
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
    logger.debug('Status Arduino atualizado', { 
      state: payload.state, 
      speed: payload.currentSpeed 
    })
  }

  handleDataUpdate(payload, timestamp) {
    const conveyorData = {
      deviceId: this.deviceStatus.id,
      timestamp,
      speed: payload.speed || 0,
      position: payload.position || 0,
      load: payload.load || 0,
      isRunning: payload.isRunning || false,
      mode: payload.mode || 'manual',
      encoderCount: payload.encoderCount || 0,
      temperature: payload.temperature || 0,
      current: payload.current || 0
    }
    
    this.emit('dataUpdate', conveyorData)
    logger.debug('Dados Arduino recebidos', { 
      speed: payload.speed, 
      isRunning: payload.isRunning 
    })
  }

  handleAlert(payload, timestamp) {
    const alert = {
      id: `arduino_${Date.now()}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'conveyor',
      severity: payload.severity || 'warning',
      title: payload.title || 'Alerta Arduino',
      message: payload.message,
      timestamp,
      acknowledged: false,
      data: payload.data || {}
    }
    
    this.emit('alert', alert)
    logger.warn('Alerta Arduino recebido', { 
      severity: alert.severity, 
      message: alert.message 
    })
  }

  handleResponse(payload, timestamp) {
    const { commandId, success, result, error } = payload
    
    const pending = this.pendingCommands.get(commandId)
    if (pending) {
      clearTimeout(pending.timeout)
      this.pendingCommands.delete(commandId)
      
      const response = {
        commandId,
        success,
        result,
        error,
        timestamp
      }
      
      this.emit('commandResponse', response)
      logger.debug('Comando Arduino processado', { commandId, success })
    }
  }

  handleStateUpdate(state, timestamp) {
    this.deviceStatus.state = state
    this.deviceStatus.lastSeen = timestamp
    
    this.emit('stateChange', { state, timestamp })
    logger.debug('Estado Arduino alterado', { state })
  }

  handleSpeedUpdate(speed, timestamp) {
    this.deviceStatus.currentSpeed = speed
    this.deviceStatus.lastSeen = timestamp
    
    this.emit('speedUpdate', { speed, timestamp })
  }

  handleModeUpdate(mode, timestamp) {
    this.deviceStatus.mode = mode
    this.deviceStatus.lastSeen = timestamp
    
    this.emit('modeChange', { mode, timestamp })
  }

  handlePiecesUpdate(pieces, timestamp) {
    this.deviceStatus.totalPieces = pieces
    this.deviceStatus.lastSeen = timestamp
    
    this.emit('piecesUpdate', { pieces, timestamp })
  }

  handleRuntimeUpdate(runtime, timestamp) {
    this.deviceStatus.totalRuntime = runtime
    this.deviceStatus.lastSeen = timestamp
    
    this.emit('runtimeUpdate', { runtime, timestamp })
  }

  handleError(errorMessage, timestamp) {
    this.deviceStatus.errorCount++
    this.deviceStatus.lastError = errorMessage
    this.deviceStatus.lastSeen = timestamp
    
    this.sendAlert('error', 'Erro do Sistema', errorMessage)
    
    logger.error('Erro Arduino', { error: errorMessage })
  }

  handleOKResponse(commandId, timestamp) {
    const pending = this.pendingCommands.get(commandId)
    if (pending) {
      clearTimeout(pending.timeout)
      this.pendingCommands.delete(commandId)
      
      this.emit('commandResponse', {
        commandId,
        success: true,
        result: 'OK',
        timestamp
      })
    }
  }

  handleErrorResponse(errorMessage, timestamp) {
    // Tentar extrair o commandId do início da mensagem
    const match = errorMessage.match(/^(\w+):(.+)$/)
    if (match) {
      const commandId = match[1]
      const error = match[2]
      
      const pending = this.pendingCommands.get(commandId)
      if (pending) {
        clearTimeout(pending.timeout)
        this.pendingCommands.delete(commandId)
        
        this.emit('commandResponse', {
          commandId,
          success: false,
          error,
          timestamp
        })
      }
    }
  }

  handleDisconnection() {
    this.isConnected = false
    this.deviceStatus.connected = false
    
    this.emit('disconnected')
    logger.warn('Arduino desconectado', { deviceId: this.deviceId })
  }

  sendAlert(severity, title, message, data = {}) {
    const alert = {
      id: `arduino_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'conveyor',
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
      
      // Serializar comando
      let serializedCommand
      if (this.supportsJSON()) {
        serializedCommand = JSON.stringify({
          type: 'COMMAND',
          payload: command
        })
      } else {
        // Protocolo de texto simples
        serializedCommand = `${commandId}:${action}`
        if (Object.keys(parameters).length > 0) {
          serializedCommand += ':' + JSON.stringify(parameters)
        }
      }
      
      // Adicionar timeout
      const timeout = setTimeout(() => {
        this.pendingCommands.delete(commandId)
        reject(new Error(`Timeout: Comando ${action} não respondida`))
      }, this.config.commandTimeout)
      
      this.pendingCommands.set(commandId, { timeout, action })
      
      // Enviar comando
      this.serialPort.write(serializedCommand + '\n', (err) => {
        if (err) {
          clearTimeout(timeout)
          this.pendingCommands.delete(commandId)
          reject(err)
          return
        }
        
        logger.info('Comando Arduino enviado', { action, commandId })
      })
      
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

  supportsJSON() {
    // Verificar se o Arduino suporta JSON (pode ser configurado)
    return this.deviceStatus.firmware >= '2.0'
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

  async initializeDevice() {
    try {
      // Configurações iniciais
      await this.sendCommand('SET_CONFIG', {
        ledIndicators: true,
        soundAlerts: true,
        maxSpeed: 200,
        minSpeed: 10
      })
      
      // Solicitar status inicial
      await this.sendCommand('GET_STATUS')
      
      logger.info('Arduino inicializado com sucesso')
    } catch (error) {
      logger.error('Erro ao inicializar Arduino', { error: error.message })
    }
  }

  // Métodos de controle específicos
  async start() {
    return this.sendCommand('START')
  }

  async stop() {
    return this.sendCommand('STOP')
  }

  async pause() {
    return this.sendCommand('PAUSE')
  }

  async setSpeed(speed) {
    return this.sendCommand('SET_SPEED', { speed })
  }

  async setMode(mode) {
    return this.sendCommand('SET_MODE', { mode })
  }

  async emergencyStop() {
    return this.sendCommand('EMERGENCY_STOP')
  }

  async reset() {
    return this.sendCommand('RESET')
  }

  async calibrate() {
    return this.sendCommand('CALIBRATE')
  }

  async getStatus() {
    return this.sendCommand('GET_STATUS')
  }

  async getConfig() {
    return this.sendCommand('GET_CONFIG')
  }

  async setConfig(config) {
    return this.sendCommand('SET_CONFIG', config)
  }

  async getDeviceStatus() {
    return {
      ...this.deviceStatus,
      connected: this.isConnected,
      pendingCommands: this.pendingCommands.size,
      portOpen: this.serialPort?.isOpen || false
    }
  }

  async disconnect() {
    this.isConnected = false
    this.deviceStatus.connected = false
    
    if (this.serialPort && this.serialPort.isOpen) {
      this.serialPort.close()
    }
    
    // Limpar timeouts pendentes
    this.pendingCommands.forEach(({ timeout }) => clearTimeout(timeout))
    this.pendingCommands.clear()
    
    this.emit('disconnected')
    logger.info('Arduino desconectado', { deviceId: this.deviceId })
  }

  // Getters para interface
  get deviceId() {
    return this.config.deviceId
  }

  get deviceType() {
    return 'conveyor'
  }

  isOnline() {
    return this.isConnected && this.serialPort?.isOpen
  }
}

export default ArduinoAdapter
