/**
 * Sistema de Autenticação JWT
 * 
 * Gerencia autenticação, autorização e tokens JWT
 * para o sistema 3dPot
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import jwt from 'jsonwebtoken'
import bcrypt from 'bcryptjs'
import crypto from 'crypto'
import { logger } from '../utils/logger.js'

class AuthService {
  constructor() {
    this.secret = process.env.JWT_SECRET || '3dpot-secret-key-2025'
    this.refreshSecret = process.env.JWT_REFRESH_SECRET || '3dpot-refresh-secret-2025'
    this.tokenExpiry = process.env.JWT_EXPIRY || '24h'
    this.refreshTokenExpiry = process.env.JWT_REFRESH_EXPIRY || '7d'
    this.maxLoginAttempts = 5
    this.lockoutTime = 15 * 60 * 1000 // 15 minutos
    this.saltRounds = 12
    
    // Usuários padrão (em produção, usar banco de dados)
    this.users = new Map()
    this.loginAttempts = new Map()
    this.refreshTokens = new Set()
    
    this.initializeDefaultUsers()
    
    logger.info('AuthService inicializado', {
      tokenExpiry: this.tokenExpiry,
      refreshTokenExpiry: this.refreshTokenExpiry
    })
  }

  initializeDefaultUsers() {
    // Usuário admin padrão
    const adminUser = {
      id: 'admin-001',
      username: 'admin',
      email: 'admin@3dpot.local',
      password: this.hashPassword('admin123'),
      role: 'admin',
      permissions: [
        'device:read',
        'device:write',
        'device:control',
        'analytics:read',
        'analytics:write',
        'system:admin',
        'users:manage'
      ],
      createdAt: new Date().toISOString(),
      lastLogin: null,
      isActive: true
    }
    
    // Usuário operador
    const operatorUser = {
      id: 'operator-001',
      username: 'operator',
      email: 'operator@3dpot.local',
      password: this.hashPassword('operator123'),
      role: 'operator',
      permissions: [
        'device:read',
        'device:control',
        'analytics:read'
      ],
      createdAt: new Date().toISOString(),
      lastLogin: null,
      isActive: true
    }
    
    // Usuário observador (apenas leitura)
    const viewerUser = {
      id: 'viewer-001',
      username: 'viewer',
      email: 'viewer@3dpot.local',
      password: this.hashPassword('viewer123'),
      role: 'viewer',
      permissions: [
        'device:read',
        'analytics:read'
      ],
      createdAt: new Date().toISOString(),
      lastLogin: null,
      isActive: true
    }
    
    this.users.set('admin', adminUser)
    this.users.set('operator', operatorUser)
    this.users.set('viewer', viewerUser)
    
    logger.info('Usuários padrão criados', {
      admin: adminUser.username,
      operator: operatorUser.username,
      viewer: viewerUser.username
    })
  }

  hashPassword(password) {
    return bcrypt.hashSync(password, this.saltRounds)
  }

  verifyPassword(password, hash) {
    return bcrypt.compareSync(password, hash)
  }

  generateTokens(user) {
    const payload = {
      userId: user.id,
      username: user.username,
      role: user.role,
      permissions: user.permissions
    }
    
    const accessToken = jwt.sign(payload, this.secret, {
      expiresIn: this.tokenExpiry,
      issuer: '3dpot-auth',
      subject: user.id
    })
    
    const refreshToken = jwt.sign(
      { userId: user.id, type: 'refresh' },
      this.refreshSecret,
      { expiresIn: this.refreshTokenExpiry }
    )
    
    // Armazenar refresh token
    this.refreshTokens.add(refreshToken)
    
    return { accessToken, refreshToken }
  }

  verifyAccessToken(token) {
    try {
      const decoded = jwt.verify(token, this.secret)
      return {
        valid: true,
        user: decoded
      }
    } catch (error) {
      return {
        valid: false,
        error: error.message
      }
    }
  }

  verifyRefreshToken(token) {
    try {
      const decoded = jwt.verify(token, this.refreshSecret)
      
      if (decoded.type !== 'refresh') {
        throw new Error('Token inválido')
      }
      
      if (!this.refreshTokens.has(token)) {
        throw new Error('Refresh token não encontrado')
      }
      
      return {
        valid: true,
        userId: decoded.userId
      }
    } catch (error) {
      return {
        valid: false,
        error: error.message
      }
    }
  }

  revokeRefreshToken(token) {
    this.refreshTokens.delete(token)
  }

  async login(username, password, clientInfo = {}) {
    try {
      // Verificar tentativas de login
      if (this.isAccountLocked(username)) {
        const lockoutTimeLeft = this.getLockoutTimeLeft(username)
        throw new Error(`Conta bloqueada. Tente novamente em ${Math.ceil(lockoutTimeLeft / 60000)} minutos.`)
      }
      
      const user = this.users.get(username)
      if (!user) {
        this.recordFailedAttempt(username)
        throw new Error('Credenciais inválidas')
      }
      
      if (!user.isActive) {
        throw new Error('Conta desativada')
      }
      
      if (!this.verifyPassword(password, user.password)) {
        this.recordFailedAttempt(username)
        throw new Error('Credenciais inválidas')
      }
      
      // Login bem-sucedido
      this.clearLoginAttempts(username)
      user.lastLogin = new Date().toISOString()
      
      const tokens = this.generateTokens(user)
      
      // Log da entrada
      logger.info('Login bem-sucedido', {
        username,
        role: user.role,
        lastLogin: user.lastLogin,
        clientIP: clientInfo.ip,
        userAgent: clientInfo.userAgent
      })
      
      return {
        success: true,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          permissions: user.permissions,
          lastLogin: user.lastLogin
        },
        tokens
      }
      
    } catch (error) {
      logger.warn('Falha no login', {
        username,
        error: error.message,
        clientIP: clientInfo.ip,
        userAgent: clientInfo.userAgent
      })
      
      return {
        success: false,
        error: error.message
      }
    }
  }

  async refresh(refreshToken) {
    const verification = this.verifyRefreshToken(refreshToken)
    
    if (!verification.valid) {
      throw new Error('Refresh token inválido')
    }
    
    const user = Array.from(this.users.values()).find(u => u.id === verification.userId)
    if (!user || !user.isActive) {
      throw new Error('Usuário não encontrado ou inativo')
    }
    
    // Gerar novos tokens
    const tokens = this.generateTokens(user)
    
    // Revogar token antigo
    this.revokeRefreshToken(refreshToken)
    
    logger.info('Token renovado', {
      userId: user.id,
      username: user.username
    })
    
    return tokens
  }

  async logout(refreshToken) {
    this.revokeRefreshToken(refreshToken)
    
    logger.info('Logout realizado', {
      refreshToken: refreshToken.substring(0, 20) + '...'
    })
    
    return { success: true }
  }

  async changePassword(userId, currentPassword, newPassword) {
    const user = Array.from(this.users.values()).find(u => u.id === userId)
    if (!user) {
      throw new Error('Usuário não encontrado')
    }
    
    if (!this.verifyPassword(currentPassword, user.password)) {
      throw new Error('Senha atual incorreta')
    }
    
    if (newPassword.length < 6) {
      throw new Error('Nova senha deve ter pelo menos 6 caracteres')
    }
    
    user.password = this.hashPassword(newPassword)
    
    logger.info('Senha alterada', {
      userId,
      username: user.username
    })
    
    return { success: true }
  }

  async createUser(userData) {
    const { username, email, password, role = 'viewer' } = userData
    
    if (this.users.has(username)) {
      throw new Error('Nome de usuário já existe')
    }
    
    const user = {
      id: `user_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      username,
      email,
      password: this.hashPassword(password),
      role,
      permissions: this.getDefaultPermissions(role),
      createdAt: new Date().toISOString(),
      lastLogin: null,
      isActive: true
    }
    
    this.users.set(username, user)
    
    logger.info('Usuário criado', {
      userId: user.id,
      username,
      role
    })
    
    return {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      permissions: user.permissions,
      createdAt: user.createdAt
    }
  }

  async getUserProfile(userId) {
    const user = Array.from(this.users.values()).find(u => u.id === userId)
    if (!user) {
      throw new Error('Usuário não encontrado')
    }
    
    return {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      permissions: user.permissions,
      lastLogin: user.lastLogin,
      createdAt: user.createdAt
    }
  }

  async updateUserProfile(userId, updates) {
    const user = Array.from(this.users.values()).find(u => u.id === userId)
    if (!user) {
      throw new Error('Usuário não encontrado')
    }
    
    // Atualizar campos permitidos
    if (updates.email) user.email = updates.email
    if (updates.role && this.hasPermission(userId, 'users:manage')) {
      user.role = updates.role
      user.permissions = this.getDefaultPermissions(updates.role)
    }
    if (updates.isActive !== undefined && this.hasPermission(userId, 'users:manage')) {
      user.isActive = updates.isActive
    }
    
    logger.info('Perfil de usuário atualizado', {
      userId,
      username: user.username,
      updates: Object.keys(updates)
    })
    
    return this.getUserProfile(userId)
  }

  hasPermission(userId, permission) {
    const user = Array.from(this.users.values()).find(u => u.id === userId)
    return user ? user.permissions.includes(permission) : false
  }

  getDefaultPermissions(role) {
    const rolePermissions = {
      admin: [
        'device:read',
        'device:write',
        'device:control',
        'analytics:read',
        'analytics:write',
        'system:admin',
        'users:manage'
      ],
      operator: [
        'device:read',
        'device:control',
        'analytics:read'
      ],
      viewer: [
        'device:read',
        'analytics:read'
      ]
    }
    
    return rolePermissions[role] || rolePermissions.viewer
  }

  isAccountLocked(username) {
    const attempts = this.loginAttempts.get(username)
    return attempts && attempts.count >= this.maxLoginAttempts && 
           (Date.now() - attempts.lastAttempt) < this.lockoutTime
  }

  recordFailedAttempt(username) {
    const attempts = this.loginAttempts.get(username) || { count: 0, lastAttempt: 0 }
    attempts.count++
    attempts.lastAttempt = Date.now()
    this.loginAttempts.set(username, attempts)
    
    logger.warn('Tentativa de login falhada', {
      username,
      attemptCount: attempts.count,
      maxAttempts: this.maxLoginAttempts
    })
  }

  clearLoginAttempts(username) {
    this.loginAttempts.delete(username)
  }

  getLockoutTimeLeft(username) {
    const attempts = this.loginAttempts.get(username)
    if (!attempts) return 0
    
    return this.lockoutTime - (Date.now() - attempts.lastAttempt)
  }

  generateCSRFToken() {
    return crypto.randomBytes(32).toString('hex')
  }

  validateCSRFToken(token, sessionToken) {
    return token === sessionToken
  }

  // Middleware para Express
  authenticate() {
    return (req, res, next) => {
      const token = this.extractToken(req)
      
      if (!token) {
        return res.status(401).json({
          error: 'Token de acesso não fornecido'
        })
      }
      
      const verification = this.verifyAccessToken(token)
      
      if (!verification.valid) {
        return res.status(401).json({
          error: 'Token de acesso inválido'
        })
      }
      
      req.user = verification.user
      next()
    }
  }

  authorize(requiredPermission) {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({
          error: 'Usuário não autenticado'
        })
      }
      
      if (!req.user.permissions.includes(requiredPermission)) {
        return res.status(403).json({
          error: 'Permissão insuficiente'
        })
      }
      
      next()
    }
  }

  extractToken(req) {
    const authHeader = req.headers.authorization
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7)
    }
    
    // Tentar cookie como fallback
    return req.cookies?.accessToken
  }

  getActiveUsers() {
    return Array.from(this.users.values())
      .filter(user => user.isActive)
      .map(user => ({
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        lastLogin: user.lastLogin,
        createdAt: user.createdAt
      }))
  }

  cleanup() {
    // Limpar tokens expirados e tentativas antigas
    this.refreshTokens.clear()
    this.loginAttempts.clear()
    
    logger.info('AuthService cleanup concluído')
  }
}

export default AuthService
