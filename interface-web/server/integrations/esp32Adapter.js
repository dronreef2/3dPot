/**
 * ESP32 Monitor de Filamento - Adaptador de Comunicação
 * 
 * Integra com o ESP32 através de MQTT e WebSocket
 * Protocolo baseado em JSON para comunicação bidirecional
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import mqtt from 'mqtt'
import WebSocket from 'ws'
import EventEmitter from 'events'
import { logger } from '../utils/logger.js'

class ESP32Adapter extends EventEmitter {
  constructor(config = {}) {
    super()
    
    this.config = {
      mqttServer: process.env.MQTT_SERVER || 'localhost',
      mqttPort: parseInt(process.env.MQTT_PORT) || 1883,
      mqttUsername: process.env.MQTT_USERNAME || '',
      mqttPassword: process.env.MQTT_PASSWORD || '',
      deviceId: 'esp32_filament_monitor_001',
      wsPort: process.env.ESP32_WS_PORT || 81,
      heartbeatInterval: 30000, // 30 segundos
      commandTimeout: 5000, // 5 segundos
      ...config
    }
    
    this.deviceStatus = {
      id: this.config.deviceId,
      type: 'filament',
      connected: false,
      lastSeen: null,
      firmware: '2.0',
      config: {
        sleepMode: 'active',
        calibrationOffset: 0.0,
        calibrationScale: 1.0,
        alertThresholds: {
          weightMin: 50.0,
          temperatureMax: 50.0,
          batteryMin: 20.0
        }
      }
    }
    
    this.mqttClient = null
    this.websocket = null
    this.commandQueue = []
    this.isConnected = false
    
    logger.info('ESP32 Adapter inicializado', { deviceId: this.deviceId })
  }

  async connect() {
    try {
      await this.connectMQTT()
      await this.connectWebSocket()
      this.startHeartbeat()
      this.setupEventHandlers()
      
      this.isConnected = true
      this.deviceStatus.connected = true
      this.deviceStatus.lastSeen = new Date().toISOString()
      
      this.emit('connected', this.deviceStatus)
      logger.info('ESP32 conectado com sucesso', { deviceId: this.deviceId })
      
    } catch (error) {
      logger.error('Falha ao conectar ESP32', { error: error.message })
      this.emit('error', error)
      throw error
    }
  }

  async connectMQTT() {
    return new Promise((resolve, reject) => {
      const mqttOptions = {
        port: this.config.mqttPort,
        username: this.config.mqttUsername,
        password: this.config.mqttPassword,
        clientId: `3dpot_esp32_${Date.now()}`,
        keepalive: 60,
        reconnectPeriod: 5000,
        clean: true
      }

      this.mqttClient = mqtt.connect(
        `mqtt://${this.config.mqttServer}`,
        mqttOptions
      )

      this.mqttClient.on('connect', () => {
        logger.info('MQTT conectado', { server: this.config.mqttServer })
        
        // Inscrever em tópicos do ESP32
        this.mqttClient.subscribe('3dpot/filament/status')
        this.mqttClient.subscribe('3dpot/filament/data')
        this.mqttClient.subscribe('3dpot/filament/alerts')
        this.mqttClient.subscribe('3dpot/filament/response')
        
        resolve()
      })

      this.mqttClient.on('error', (error) => {
        logger.error('MQTT erro', { error: error.message })
        reject(error)
      })

      this.mqttClient.on('message', (topic, message) => {
        this.handleMQTTMessage(topic, message)
      })
    })
  }

  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      const wsUrl = `ws://localhost:${this.config.wsPort}`
      
      this.websocket = new WebSocket(wsUrl)
      
      this.websocket.on('open', () => {
        logger.info('WebSocket conectado', { url: wsUrl })
        resolve()
      })

      this.websocket.on('error', (error) => {
        logger.error('WebSocket erro', { error: error.message })
        reject(error)
      })

      this.websocket.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString())
          this.handleWebSocketMessage(message)
        } catch (error) {
          logger.error('Erro ao processar mensagem WebSocket', { error: error.message })
        }
      })
    })
  }

  handleMQTTMessage(topic, message) {
    try {
      const payload = JSON.parse(message.toString())
      const timestamp = new Date().toISOString()

      switch (topic) {
        case '3dpot/filament/status':
          this.handleStatusUpdate(payload, timestamp)
          break
          
        case '3dpot/filament/data':
          this.handleDataUpdate(payload, timestamp)
          break
          
        case '3dpot/filament/alerts':
          this.handleAlert(payload, timestamp)
          break
          
        case '3dpot/filament/response':
          this.handleResponse(payload, timestamp)
          break
          
        default:
          logger.warn('Tópico MQTT não reconhecido', { topic })
      }
    } catch (error) {
      logger.error('Erro ao processar mensagem MQTT', { 
        topic, 
        error: error.message 
      })
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
    logger.debug('Status ESP32 atualizado', this.deviceStatus)
  }

  handleDataUpdate(payload, timestamp) {
    const filamentData = {
      deviceId: this.deviceStatus.id,
      timestamp,
      weight: payload.weight,
      temperature: payload.temperature,
      humidity: payload.humidity,
      batteryLevel: payload.batteryLevel,
      isSleeping: payload.isSleeping || false,
      uptime: payload.uptime,
      wifiSignal: payload.wifiSignal,
      memoryUsage: payload.memoryUsage
    }
    
    this.emit('dataUpdate', filamentData)
    
    // Verificar thresholds e enviar alertas
    this.checkThresholds(filamentData)
    
    logger.debug('Dados ESP32 recebidos', { weight: payload.weight, temp: payload.temperature })
  }

  handleAlert(payload, timestamp) {
    const alert = {
      id: `esp32_${Date.now()}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'filament',
      severity: payload.severity || 'warning',
      title: payload.title || 'Alerta ESP32',
      message: payload.message,
      timestamp,
      acknowledged: false,
      data: payload.data || {}
    }
    
    this.emit('alert', alert)
    logger.warn('Alerta ESP32 recebido', { severity: alert.severity, message: alert.message })
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
      logger.debug('Comando ESP32 processado', { commandId, success })
    }
  }

  handleWebSocketMessage(message) {
    const { type, data, commandId } = message
    
    switch (type) {
      case 'status':
        this.handleStatusUpdate(data, new Date().toISOString())
        break
        
      case 'data':
        this.handleDataUpdate(data, new Date().toISOString())
        break
        
      case 'alert':
        this.handleAlert(data, new Date().toISOString())
        break
        
      case 'response':
        if (commandId) {
          this.handleResponse(data, new Date().toISOString())
        }
        break
        
      default:
        logger.warn('Tipo de mensagem WebSocket não reconhecido', { type })
    }
  }

  checkThresholds(data) {
    const thresholds = this.deviceStatus.config.alertThresholds
    
    // Verificar peso mínimo
    if (data.weight < thresholds.weightMin) {
      this.sendAlert('warning', 'Peso Baixo', 
        `Peso do filamento: ${data.weight.toFixed(1)}g (min: ${thresholds.weightMin}g)`)
    }
    
    // Verificar temperatura máxima
    if (data.temperature > thresholds.temperatureMax) {
      this.sendAlert('critical', 'Temperatura Alta', 
        `Temperatura: ${data.temperature.toFixed(1)}°C (max: ${thresholds.temperatureMax}°C)`)
    }
    
    // Verificar bateria mínima
    if (data.batteryLevel < thresholds.batteryMin) {
      this.sendAlert('critical', 'Bateria Baixa', 
        `Nível da bateria: ${data.batteryLevel.toFixed(1)}% (min: ${thresholds.batteryMin}%)`)
    }
  }

  sendAlert(severity, title, message, data = {}) {
    const alert = {
      id: `esp32_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      deviceId: this.deviceStatus.id,
      deviceType: 'filament',
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
      
      // Adicionar timeout
      const timeout = setTimeout(() => {
        this.commandQueue = this.commandQueue.filter(cmd => cmd.id !== commandId)
        reject(new Error(`Timeout: Comando ${action} não respondida`))
      }, this.config.commandTimeout)
      
      this.commandQueue.push({ ...command, timeout })
      
      // Enviar via MQTT
      this.mqttClient.publish(
        '3dpot/filament/command',
        JSON.stringify(command),
        { qos: 1 }
      )
      
      // Enviar via WebSocket
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify({
          type: 'command',
          data: command
        }))
      }
      
      logger.info('Comando ESP32 enviado', { action, commandId })
      
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

  startHeartbeat() {
    setInterval(() => {
      if (this.isConnected) {
        this.mqttClient.publish(
          '3dpot/filament/ping',
          JSON.stringify({
            timestamp: new Date().toISOString(),
            serverTime: Date.now()
          })
        )
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
  async calibrate(scale = null, offset = null) {
    const parameters = { scale, offset }
    return this.sendCommand('calibrate', parameters)
  }

  async setSleepMode(mode) {
    return this.sendCommand('set_sleep_mode', { mode })
  }

  async performTare() {
    return this.sendCommand('tare')
  }

  async setAlertThresholds(thresholds) {
    return this.sendCommand('set_thresholds', thresholds)
  }

  async requestStatus() {
    return this.sendCommand('get_status')
  }

  async requestCalibration() {
    return this.sendCommand('get_calibration')
  }

  async getDeviceStatus() {
    return {
      ...this.deviceStatus,
      connected: this.isConnected,
      commandQueueLength: this.commandQueue.length,
      mqttConnected: this.mqttClient?.connected || false,
      websocketConnected: this.websocket?.readyState === WebSocket.OPEN
    }
  }

  async disconnect() {
    this.isConnected = false
    this.deviceStatus.connected = false
    
    if (this.mqttClient) {
      this.mqttClient.end()
    }
    
    if (this.websocket) {
      this.websocket.close()
    }
    
    this.commandQueue.forEach(cmd => clearTimeout(cmd.timeout))
    this.commandQueue = []
    
    this.emit('disconnected')
    logger.info('ESP32 desconectado', { deviceId: this.deviceId })
  }

  // Getters para interface
  get deviceId() {
    return this.config.deviceId
  }

  get deviceType() {
    return 'filament'
  }

  isOnline() {
    return this.isConnected
  }
}

export default ESP32Adapter
