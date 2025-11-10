import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  BeakerIcon, 
  TruckIcon, 
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  DocumentChartBarIcon,
  BellIcon,
  WifiIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline'
import { motion, AnimatePresence } from 'framer-motion'
import { useDevice } from '@contexts/DeviceContext'
import type { AppSettings } from '@types'

interface LayoutProps {
  children: ReactNode
  settings: AppSettings
  onSettingsChange: (settings: Partial<AppSettings>) => void
  onThemeToggle: () => void
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
}

const navigationItems = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Monitor Filamento', href: '/filament', icon: BeakerIcon },
  { name: 'Esteira', href: '/conveyor', icon: TruckIcon },
  { name: 'Estação QC', href: '/qc', icon: MagnifyingGlassIcon },
  { name: 'Relatórios', href: '/reports', icon: DocumentChartBarIcon },
  { name: 'Configurações', href: '/settings', icon: Cog6ToothIcon },
]

const getConnectionStatusColor = (status: string) => {
  switch (status) {
    case 'connected': return 'text-green-500'
    case 'connecting': return 'text-yellow-500'
    case 'error': return 'text-red-500'
    default: return 'text-gray-500'
  }
}

const getConnectionStatusText = (status: string) => {
  switch (status) {
    case 'connected': return 'Conectado'
    case 'connecting': return 'Conectando...'
    case 'error': return 'Erro de conexão'
    default: return 'Desconectado'
  }
}

export function Layout({ children, settings, onSettingsChange, onThemeToggle, connectionStatus }: LayoutProps) {
  const location = useLocation()
  const { state: deviceState, acknowledgeAlert } = useDevice()
  
  const unacknowledgedAlerts = deviceState.alerts.filter(alert => !alert.acknowledged)
  const isMobile = window.innerWidth < 768

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Header */}
      {isMobile && (
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">3d</span>
              </div>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">3dPot</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Connection Status */}
              <div className="flex items-center space-x-1">
                <WifiIcon className={`w-4 h-4 ${getConnectionStatusColor(connectionStatus)}`} />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {getConnectionStatusText(connectionStatus)}
                </span>
              </div>
              
              {/* Theme Toggle */}
              <button
                onClick={onThemeToggle}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                {settings.theme === 'dark' ? (
                  <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                ) : (
                  <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                )}
              </button>
              
              {/* Notifications */}
              <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                <BellIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                {unacknowledgedAlerts.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unacknowledgedAlerts.length > 9 ? '9+' : unacknowledgedAlerts.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </header>
      )}

      <div className="flex">
        {/* Desktop Sidebar */}
        {!isMobile && (
          <aside className="w-64 bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 min-h-screen">
            {/* Logo */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">3d</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">3dPot</h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Control Center</p>
                </div>
              </div>
            </div>

            {/* Connection Status */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300">Status</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    connectionStatus === 'connected' ? 'bg-green-500' :
                    connectionStatus === 'connecting' ? 'bg-yellow-500' :
                    connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
                  }`} />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {getConnectionStatusText(connectionStatus)}
                  </span>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="p-4 space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </nav>

            {/* Alerts */}
            {unacknowledgedAlerts.length > 0 && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 mt-4">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Alertas Recentes
                </h3>
                <div className="space-y-2">
                  {unacknowledgedAlerts.slice(0, 3).map((alert) => (
                    <div
                      key={alert.id}
                      className="p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
                    >
                      <p className="text-xs font-medium text-red-800 dark:text-red-200">
                        {alert.title}
                      </p>
                      <p className="text-xs text-red-600 dark:text-red-300">
                        {alert.message}
                      </p>
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="text-xs text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 mt-1"
                      >
                        Reconhecer
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </aside>
        )}

        {/* Main Content */}
        <main className={`flex-1 ${!isMobile ? 'p-6' : 'pb-20'}`}>
          {/* Desktop Header */}
          {!isMobile && (
            <header className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {navigationItems.find(item => item.href === location.pathname)?.name || 'Dashboard'}
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Sistema de controle para impressora 3D
                  </p>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* Theme Toggle */}
                  <button
                    onClick={onThemeToggle}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    {settings.theme === 'dark' ? (
                      <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    ) : (
                      <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    )}
                  </button>
                  
                  {/* Notifications */}
                  <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                    <BellIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    {unacknowledgedAlerts.length > 0 && (
                      <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {unacknowledgedAlerts.length > 9 ? '9+' : unacknowledgedAlerts.length}
                      </span>
                    )}
                  </button>
                </div>
              </div>
            </header>
          )}

          {/* Page Content */}
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-2 py-2">
          <div className="flex justify-around">
            {navigationItems.slice(0, 4).map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex flex-col items-center p-2 rounded-lg text-xs transition-colors ${
                    isActive
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mb-1" />
                  <span className="truncate">{item.name.split(' ')[0]}</span>
                </Link>
              )
            })}
          </div>
        </nav>
      )}
    </div>
  )
}