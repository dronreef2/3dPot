import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import axios from 'axios'

interface LoginFormData {
  username: string
  password: string
}

interface LoginResponse {
  success: boolean
  user?: {
    id: string
    username: string
    email: string
    role: string
  }
  tokens?: {
    accessToken: string
    refreshToken: string
  }
  error?: string
}

export function Login() {
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  const navigate = useNavigate()
  const location = useLocation()
  
  const from = location.state?.from?.pathname || '/dashboard'

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.username.trim()) {
      newErrors.username = 'Username é obrigatório'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username deve ter pelo menos 3 caracteres'
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsLoading(true)
    setErrors({})

    try {
      const response = await axios.post('/api/auth/login', formData, {
        timeout: 10000,
        withCredentials: true
      })

      const data: LoginResponse = response.data

      if (data.success && data.user && data.tokens) {
        // Store tokens in memory/session storage
        sessionStorage.setItem('accessToken', data.tokens.accessToken)
        
        toast.success(`Bem-vindo, ${data.user.username}!`)
        
        // Navigate to the protected route or dashboard
        navigate(from, { replace: true })
      } else {
        setErrors({ submit: data.error || 'Erro ao fazer login' })
        toast.error(data.error || 'Erro ao fazer login')
      }

    } catch (error: any) {
      console.error('Login error:', error)
      
      if (error.response?.data?.error) {
        setErrors({ submit: error.response.data.error })
        toast.error(error.response.data.error)
      } else if (error.code === 'NETWORK_ERROR') {
        setErrors({ submit: 'Erro de rede. Verifique sua conexão.' })
        toast.error('Erro de rede. Verifique sua conexão.')
      } else {
        setErrors({ submit: 'Erro interno. Tente novamente.' })
        toast.error('Erro interno. Tente novamente.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: keyof LoginFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.3,
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-md w-full space-y-8"
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="text-center">
          <div className="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
            <svg
              className="h-10 w-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            3dPot Dashboard
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Entre com suas credenciais para acessar o sistema
          </p>
        </motion.div>

        {/* Login Form */}
        <motion.form
          variants={itemVariants}
          className="mt-8 space-y-6"
          onSubmit={handleSubmit}
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 space-y-4">
            {/* Global Error */}
            {errors.submit && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg text-sm">
                {errors.submit}
              </div>
            )}

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                  errors.username 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-primary-500'
                }`}
                placeholder="Digite seu username"
                disabled={isLoading}
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.username}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Senha
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className={`w-full px-3 py-2 pr-10 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                    errors.password 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-primary-500'
                  }`}
                  placeholder="Digite sua senha"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed dark:focus:ring-offset-gray-800"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Entrando...
                </div>
              ) : (
                'Entrar'
              )}
            </button>
          </div>

          {/* Demo Credentials */}
          <motion.div 
            variants={itemVariants}
            className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
          >
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
              Credenciais de Demonstração:
            </h3>
            <div className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
              <div><strong>Admin:</strong> admin / 123456</div>
              <div><strong>Operator:</strong> operator / 123456</div>
              <div><strong>Viewer:</strong> viewer / 123456</div>
            </div>
          </motion.div>
        </motion.form>
      </motion.div>
    </div>
  )
}