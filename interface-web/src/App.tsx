import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { Layout } from '@components/Layout'
import { ProtectedRoute } from '@components/ProtectedRoute'
import { Login } from '@pages/Login'
import { Dashboard } from '@pages/Dashboard'
import { FilamentMonitor } from '@pages/FilamentMonitor'
import { ConveyorControl } from '@pages/ConveyorControl'
import { QCStation } from '@pages/QCStation'
import { Projects } from '@pages/Projects'
import { Settings } from '@pages/Settings'
import { Reports } from '@pages/Reports'
import { useWebSocket } from '@hooks/useWebSocket'
import { DeviceProvider } from '../contexts/DeviceContext'
import { AuthProvider, useAuth } from '../contexts/AuthContext'
import { useTheme } from '@hooks/useTheme'
import type { AppSettings } from '../types'

const defaultSettings: AppSettings = {
  theme: 'auto',
  language: 'pt-BR',
  notifications: {
    enabled: true,
    sound: true,
    vibration: true,
  },
  refreshInterval: 30,
  compactMode: false,
}

// Main App Content Component (inside AuthProvider)
function AppContent() {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const { isDark, toggleTheme } = useTheme(settings.theme)
  const { connectionStatus } = useWebSocket()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    // Apply theme to document
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('3dpot-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...defaultSettings, ...parsed })
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    }
  }, [])

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    const updated = { ...settings, ...newSettings }
    setSettings(updated)
    localStorage.setItem('3dpot-settings', JSON.stringify(updated))
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando 3dPot Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route path="/*" element={
          <ProtectedRoute>
            <DeviceProvider>
              <Layout
                settings={settings}
                onSettingsChange={updateSettings}
                onThemeToggle={toggleTheme}
                connectionStatus={connectionStatus}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/projects" element={<Projects />} />
                  <Route path="/filament" element={
                    <ProtectedRoute requiredPermission="devices:view">
                      <FilamentMonitor />
                    </ProtectedRoute>
                  } />
                  <Route path="/conveyor" element={
                    <ProtectedRoute requiredPermission="devices:view">
                      <ConveyorControl />
                    </ProtectedRoute>
                  } />
                  <Route path="/qc" element={
                    <ProtectedRoute requiredPermission="devices:view">
                      <QCStation />
                    </ProtectedRoute>
                  } />
                  <Route path="/settings" element={
                    <ProtectedRoute requiredPermission="settings:manage">
                      <Settings settings={settings} onSettingsChange={updateSettings} />
                    </ProtectedRoute>
                  } />
                  <Route path="/reports" element={
                    <ProtectedRoute requiredPermission="reports:view">
                      <Reports />
                    </ProtectedRoute>
                  } />
                </Routes>
              </Layout>
            </DeviceProvider>
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  )
}

// Main App Component with Providers
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--toast-bg)',
              color: 'var(--toast-color)',
              border: '1px solid var(--toast-border)',
            },
            success: {
              iconTheme: {
                primary: '#10B981',
                secondary: '#FFFFFF',
              },
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#FFFFFF',
              },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App