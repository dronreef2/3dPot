import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import axios from 'axios'

interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'operator' | 'viewer'
  createdAt: string
  lastLogin?: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  refreshToken: () => Promise<boolean>
  hasPermission: (permission: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  const navigate = useNavigate()

  // Configure axios defaults
  useEffect(() => {
    // Add request interceptor to include auth token
    axios.interceptors.request.use(
      (config) => {
        const token = sessionStorage.getItem('accessToken')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Add response interceptor to handle auth errors
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshed = await refreshToken()
          if (!refreshed) {
            logout()
            navigate('/login')
          }
        }
        return Promise.reject(error)
      }
    )
  }, [navigate])

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = sessionStorage.getItem('accessToken')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await axios.get('/api/auth/me', {
        withCredentials: true,
        timeout: 5000
      })

      if (response.data.success) {
        setUser(response.data.user)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      // Clear invalid token
      sessionStorage.removeItem('accessToken')
    } finally {
      setIsLoading(false)
    }
  }

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await axios.post('/api/auth/login', 
        { username, password },
        {
          withCredentials: true,
          timeout: 10000
        }
      )

      if (response.data.success && response.data.user && response.data.tokens) {
        // Store token
        sessionStorage.setItem('accessToken', response.data.tokens.accessToken)
        
        // Set user state
        setUser(response.data.user)
        
        toast.success(`Bem-vindo, ${response.data.user.username}!`)
        return true
      }

      throw new Error(response.data.error || 'Login failed')
    } catch (error: any) {
      console.error('Login error:', error)
      
      const errorMessage = error.response?.data?.error || 
                          error.message || 
                          'Erro interno. Tente novamente.'
      
      toast.error(errorMessage)
      return false
    }
  }, [])

  const logout = useCallback(() => {
    try {
      // Call logout endpoint
      axios.post('/api/auth/logout', {}, {
        withCredentials: true
      }).catch((error) => {
        console.error('Logout error:', error)
      })
    } finally {
      // Clear local state regardless of API call result
      sessionStorage.removeItem('accessToken')
      setUser(null)
      toast.success('Logout realizado com sucesso')
    }
  }, [])

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const response = await axios.post('/api/auth/refresh', {}, {
        withCredentials: true,
        timeout: 5000
      })

      if (response.data.success && response.data.tokens) {
        sessionStorage.setItem('accessToken', response.data.tokens.accessToken)
        return true
      }

      return false
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
  }, [])

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false

    const permissions: Record<string, string[]> = {
      admin: [
        'users:manage',
        'devices:control',
        'devices:view',
        'projects:manage',
        'projects:view',
        'reports:view',
        'reports:export',
        'settings:manage'
      ],
      operator: [
        'devices:control',
        'devices:view',
        'projects:manage',
        'projects:view',
        'reports:view'
      ],
      viewer: [
        'devices:view',
        'projects:view',
        'reports:view'
      ]
    }

    const userPermissions = permissions[user.role] || []
    return userPermissions.includes(permission)
  }, [user])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshToken,
    hasPermission
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}