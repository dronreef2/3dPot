import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Layout } from '@components/Layout'
import { Dashboard } from '@pages/Dashboard'
import { FilamentMonitor } from '@pages/FilamentMonitor'
import { ConveyorControl } from '@pages/ConveyorControl'
import { QCStation } from '@pages/QCStation'
import { Settings } from '@pages/Settings'
import { Reports } from '@pages/Reports'
import { useWebSocket } from '@hooks/useWebSocket'
import { DeviceProvider } from '@contexts/DeviceContext'
import { useTheme } from '@hooks/useTheme'
import type { AppSettings } from '@types'

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

function App() {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const { isDark, toggleTheme } = useTheme(settings.theme)
  const { connectionStatus } = useWebSocket()

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

  return (
    <DeviceProvider>
      <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
        <Layout
          settings={settings}
          onSettingsChange={updateSettings}
          onThemeToggle={toggleTheme}
          connectionStatus={connectionStatus}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/filament" element={<FilamentMonitor />} />
            <Route path="/conveyor" element={<ConveyorControl />} />
            <Route path="/qc" element={<QCStation />} />
            <Route path="/settings" element={<Settings settings={settings} onSettingsChange={updateSettings} />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Layout>
      </div>
    </DeviceProvider>
  )
}

export default App