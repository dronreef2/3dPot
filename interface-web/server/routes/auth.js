/**
 * Rotas de Autenticação
 * 
 * Endpoints para login, logout, refresh token e gerenciamento de usuários
 * 
 * Autor: 3dPot Project
 * Data: 2025-11-10
 */

import express from 'express'
import { body, validationResult } from 'express-validator'
import { logger } from '../utils/logger.js'

const router = express.Router()

// Middleware para extrair o serviço de autenticação
router.use((req, res, next) => {
  req.authService = req.app.get('authService')
  next()
})

// Validação
const loginValidation = [
  body('username')
    .trim()
    .isLength({ min: 1 })
    .withMessage('Username é obrigatório'),
  body('password')
    .isLength({ min: 1 })
    .withMessage('Password é obrigatório')
]

const changePasswordValidation = [
  body('currentPassword')
    .isLength({ min: 1 })
    .withMessage('Senha atual é obrigatória'),
  body('newPassword')
    .isLength({ min: 6 })
    .withMessage('Nova senha deve ter pelo menos 6 caracteres')
]

const createUserValidation = [
  body('username')
    .trim()
    .isLength({ min: 3 })
    .withMessage('Username deve ter pelo menos 3 caracteres'),
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Email inválido'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Senha deve ter pelo menos 6 caracteres'),
  body('role')
    .isIn(['admin', 'operator', 'viewer'])
    .withMessage('Role deve ser admin, operator ou viewer')
]

// Helpers
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req)
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Dados inválidos',
      details: errors.array()
    })
  }
  next()
}

// Rotas

// POST /api/auth/login
router.post('/login', loginValidation, handleValidationErrors, async (req, res) => {
  try {
    const { username, password } = req.body
    const clientInfo = {
      ip: req.ip,
      userAgent: req.get('User-Agent')
    }
    
    const result = await req.authService.login(username, password, clientInfo)
    
    if (result.success) {
      // Definir cookies seguros
      res.cookie('accessToken', result.tokens.accessToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 24 * 60 * 60 * 1000 // 24 horas
      })
      
      res.cookie('refreshToken', result.tokens.refreshToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 7 * 24 * 60 * 60 * 1000 // 7 dias
      })
      
      logger.info('User logged in successfully', {
        userId: result.user.id,
        username: result.user.username
      })
    }
    
    res.json(result)
    
  } catch (error) {
    logger.error('Login error', { error: error.message })
    res.status(500).json({
      error: 'Erro interno do servidor'
    })
  }
})

// POST /api/auth/refresh
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.cookies
    
    if (!refreshToken) {
      return res.status(401).json({
        error: 'Refresh token não fornecido'
      })
    }
    
    const tokens = await req.authService.refresh(refreshToken)
    
    // Atualizar cookies
    res.cookie('accessToken', tokens.accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000
    })
    
    res.cookie('refreshToken', tokens.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000
    })
    
    res.json({
      success: true,
      tokens
    })
    
  } catch (error) {
    logger.error('Token refresh error', { error: error.message })
    res.status(401).json({
      error: 'Token refresh falhou'
    })
  }
})

// POST /api/auth/logout
router.post('/logout', async (req, res) => {
  try {
    const { refreshToken } = req.cookies
    
    if (refreshToken) {
      await req.authService.logout(refreshToken)
    }
    
    // Limpar cookies
    res.clearCookie('accessToken')
    res.clearCookie('refreshToken')
    
    res.json({
      success: true,
      message: 'Logout realizado com sucesso'
    })
    
  } catch (error) {
    logger.error('Logout error', { error: error.message })
    res.status(500).json({
      error: 'Erro interno do servidor'
    })
  }
})

// GET /api/auth/me
router.get('/me', async (req, res) => {
  const authService = req.app.get('authService')
  
  // Apply authentication middleware manually
  const authMiddleware = authService.authenticate()
  authMiddleware(req, res, async () => {
  try {
    const userProfile = await req.authService.getUserProfile(req.user.userId)
    
    res.json({
      success: true,
      user: userProfile
    })
    
  } catch (error) {
    logger.error('Get profile error', { error: error.message, userId: req.user?.userId })
    res.status(404).json({
      error: 'Usuário não encontrado'
    })
  }
  })
})

// POST /api/auth/change-password
router.post('/change-password', 
  (req, res, next) => {
    const authService = req.app.get('authService')
    authService.authenticate()(req, res, next)
  },
  changePasswordValidation,
  handleValidationErrors,
  async (req, res) => {
    try {
      const { currentPassword, newPassword } = req.body
      
      const result = await req.authService.changePassword(
        req.user.userId,
        currentPassword,
        newPassword
      )
      
      if (result.success) {
        // Invalidar todos os refresh tokens do usuário
        // Em uma implementação real, você manteria uma lista de tokens válidos
      }
      
      res.json(result)
      
    } catch (error) {
      logger.error('Change password error', { 
        error: error.message, 
        userId: req.user.userId 
      })
      res.status(400).json({
        error: error.message
      })
    }
  }
)

// GET /api/auth/users (apenas admin)
router.get('/users', 
  (req, res, next) => {
    const authService = req.app.get('authService')
    authService.authenticate()(req, res, () => {
      authService.authorize('users:manage')(req, res, next)
    })
  },
  async (req, res) => {
    try {
      const users = req.authService.getActiveUsers()
      
      res.json({
        success: true,
        users
      })
      
    } catch (error) {
      logger.error('Get users error', { 
        error: error.message, 
        userId: req.user.userId 
      })
      res.status(500).json({
        error: 'Erro interno do servidor'
      })
    }
  }
)

// POST /api/auth/users (criar usuário - apenas admin)
router.post('/users',
  (req, res, next) => {
    const authService = req.app.get('authService')
    authService.authenticate()(req, res, () => {
      authService.authorize('users:manage')(req, res, next)
    })
  },
  createUserValidation,
  handleValidationErrors,
  async (req, res) => {
    try {
      const userData = req.body
      const newUser = await req.authService.createUser(userData)
      
      logger.info('User created', {
        createdBy: req.user.username,
        newUser: newUser.username
      })
      
      res.status(201).json({
        success: true,
        user: newUser
      })
      
    } catch (error) {
      logger.error('Create user error', { 
        error: error.message, 
        userId: req.user.userId 
      })
      res.status(400).json({
        error: error.message
      })
    }
  }
)

// PUT /api/auth/users/:userId
router.put('/users/:userId',
  (req, res, next) => {
    const authService = req.app.get('authService')
    authService.authenticate()(req, res, () => {
      authService.authorize('users:manage')(req, res, next)
    })
  },
  async (req, res) => {
    try {
      const { userId } = req.params
      const updates = req.body
      
      const updatedUser = await req.authService.updateUserProfile(userId, updates)
      
      logger.info('User updated', {
        updatedBy: req.user.username,
        userId,
        updates: Object.keys(updates)
      })
      
      res.json({
        success: true,
        user: updatedUser
      })
      
    } catch (error) {
      logger.error('Update user error', { 
        error: error.message, 
        userId: req.user.userId 
      })
      res.status(400).json({
        error: error.message
      })
    }
  }
)

// GET /api/auth/health
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'auth'
  })
})

export { router as authRoutes }
