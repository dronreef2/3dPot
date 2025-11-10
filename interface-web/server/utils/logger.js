/**
 * Sistema de Logging Centralizado
 * 
 * Sistema de logs estruturado para o 3dPot
 * com diferentes níveis e formatação JSON
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Configurações de logging
const config = {
  level: process.env.LOG_LEVEL || 'info',
  format: process.env.LOG_FORMAT || 'json', // 'json' ou 'simple'
  file: {
    enabled: process.env.LOG_TO_FILE !== 'false',
    path: process.env.LOG_PATH || path.join(__dirname, '../../logs'),
    maxSize: process.env.LOG_MAX_SIZE || '10MB',
    maxFiles: parseInt(process.env.LOG_MAX_FILES) || 5
  },
  console: {
    enabled: process.env.LOG_TO_CONSOLE !== 'false',
    colorize: process.env.LOG_COLORIZE === 'true'
  }
}

class Logger {
  constructor() {
    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3,
      trace: 4
    }
    
    this.currentLevel = this.levels[config.level] || this.levels.info
    this.logDir = config.file.path
    
    // Criar diretório de logs se não existir
    if (config.file.enabled) {
      this.ensureLogDirectory()
    }
    
    // Cache de arquivos de log
    this.logFiles = new Map()
  }

  ensureLogDirectory() {
    try {
      if (!fs.existsSync(this.logDir)) {
        fs.mkdirSync(this.logDir, { recursive: true })
      }
    } catch (error) {
      console.error('Erro ao criar diretório de logs:', error.message)
    }
  }

  getLogFile(category = 'app') {
    const today = new Date().toISOString().split('T')[0]
    const filename = `3dpot-${category}-${today}.log`
    const filepath = path.join(this.logDir, filename)
    
    if (!this.logFiles.has(filepath)) {
      this.logFiles.set(filepath, fs.createWriteStream(filepath, { flags: 'a' }))
    }
    
    return this.logFiles.get(filepath)
  }

  formatMessage(level, message, meta = {}) {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      level: level.toUpperCase(),
      message,
      pid: process.pid,
      ...meta
    }
    
    if (config.format === 'json') {
      return JSON.stringify(logEntry)
    } else {
      return `[${timestamp}] ${level.toUpperCase()}: ${message} ${Object.keys(meta).length > 0 ? JSON.stringify(meta) : ''}`
    }
  }

  writeToFile(level, formattedMessage, category = 'app') {
    if (!config.file.enabled) return
    
    try {
      const logFile = this.getLogFile(category)
      logFile.write(formattedMessage + '\n')
    } catch (error) {
      console.error('Erro ao escrever no arquivo de log:', error.message)
    }
  }

  writeToConsole(level, formattedMessage) {
    if (!config.console.enabled) return
    
    const colors = {
      error: '\x1b[31m',    // Vermelho
      warn: '\x1b[33m',     // Amarelo
      info: '\x1b[36m',     // Ciano
      debug: '\x1b[37m',    // Branco
      trace: '\x1b[90m'     // Cinza
    }
    
    const reset = '\x1b[0m'
    const colorCode = colors[level] || ''
    
    if (config.console.colorize) {
      console.log(colorCode + formattedMessage + reset)
    } else {
      console.log(formattedMessage)
    }
  }

  shouldLog(level) {
    return this.levels[level] <= this.currentLevel
  }

  log(level, message, meta = {}) {
    if (!this.shouldLog(level)) return
    
    const formattedMessage = this.formatMessage(level, message, meta)
    
    // Determinar categoria do log
    let category = 'app'
    if (meta.device) {
      category = `device-${meta.device}`
    } else if (meta.service) {
      category = `service-${meta.service}`
    }
    
    this.writeToFile(level, formattedMessage, category)
    this.writeToConsole(level, formattedMessage)
  }

  // Métodos de conveniência
  error(message, meta = {}) {
    this.log('error', message, { error: true, ...meta })
  }

  warn(message, meta = {}) {
    this.log('warn', message, { warning: true, ...meta })
  }

  info(message, meta = {}) {
    this.log('info', message, meta)
  }

  debug(message, meta = {}) {
    this.log('debug', message, meta)
  }

  trace(message, meta = {}) {
    this.log('trace', message, meta)
  }

  // Métodos especializados
  system(message, meta = {}) {
    this.log('info', message, { category: 'system', ...meta })
  }

  device(device, message, meta = {}) {
    this.log('info', message, { category: 'device', device, ...meta })
  }

  network(message, meta = {}) {
    this.log('info', message, { category: 'network', ...meta })
  }

  security(message, meta = {}) {
    this.log('warn', message, { category: 'security', ...meta })
  }

  performance(message, meta = {}) {
    this.log('debug', message, { category: 'performance', ...meta })
  }

  // Logging estruturado
  withContext(context) {
    return {
      error: (message, meta = {}) => this.error(message, { context, ...meta }),
      warn: (message, meta = {}) => this.warn(message, { context, ...meta }),
      info: (message, meta = {}) => this.info(message, { context, ...meta }),
      debug: (message, meta = {}) => this.debug(message, { context, ...meta }),
      trace: (message, meta = {}) => this.trace(message, { context, ...meta })
    }
  }

  // Performance monitoring
  startTimer(label) {
    const start = Date.now()
    return {
      end: (meta = {}) => {
        const duration = Date.now() - start
        this.performance(`${label} completed`, { 
          duration, 
          label, 
          ...meta 
        })
        return duration
      }
    }
  }

  // Error tracking
  trackError(error, context = {}) {
    this.error('Error occurred', {
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      },
      context
    })
  }

  // API request logging
  logRequest(req, res, duration) {
    const meta = {
      method: req.method,
      url: req.url,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      statusCode: res.statusCode,
      duration
    }
    
    if (req.user) {
      meta.userId = req.user.userId
      meta.username = req.user.username
    }
    
    this.network(`${req.method} ${req.url} - ${res.statusCode}`, meta)
  }

  // WebSocket logging
  logWebSocket(event, socketId, data = {}) {
    this.network(`WebSocket ${event}`, {
      socketId,
      ...data
    })
  }

  // Database logging
  logDatabase(operation, table, duration, meta = {}) {
    this.debug(`DB ${operation} on ${table}`, {
      operation,
      table,
      duration,
      ...meta
    })
  }

  // Device communication logging
  logDeviceCommunication(device, direction, message, meta = {}) {
    const context = direction === 'inbound' ? 'received' : 'sent'
    this.device(device, `${context}: ${message}`, { direction, ...meta })
  }

  // Cleanup
  close() {
    this.logFiles.forEach((fileStream) => {
      fileStream.end()
    })
    this.logFiles.clear()
  }

  // Rotação de logs
  rotateLogs() {
    if (!config.file.enabled) return
    
    try {
      const files = fs.readdirSync(this.logDir)
      const logFiles = files.filter(file => file.startsWith('3dpot-'))
      
      // Ordenar por data de modificação (mais antigos primeiro)
      logFiles.sort((a, b) => {
        const statA = fs.statSync(path.join(this.logDir, a))
        const statB = fs.statSync(path.join(this.logDir, b))
        return statA.mtime.getTime() - statB.mtime.getTime()
      })
      
      // Remover arquivos além do limite
      if (logFiles.length > config.file.maxFiles) {
        const filesToDelete = logFiles.slice(0, logFiles.length - config.file.maxFiles)
        filesToDelete.forEach(file => {
          const filepath = path.join(this.logDir, file)
          fs.unlinkSync(filepath)
          this.info(`Log file removed`, { file })
        })
      }
      
    } catch (error) {
      this.error('Error during log rotation', { error: error.message })
    }
  }
}

// Instância singleton
const logger = new Logger()

// Rotação automática de logs (diária)
setInterval(() => {
  logger.rotateLogs()
}, 24 * 60 * 60 * 1000) // 24 horas

// Cleanup ao terminar o processo
process.on('SIGTERM', () => {
  logger.close()
})

process.on('SIGINT', () => {
  logger.close()
})

export { logger }
export default logger
