import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Cog6ToothIcon,
  BellIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  SunIcon,
  MoonIcon,
  GlobeAltIcon,
  LanguageIcon
} from '@heroicons/react/24/outline'
import type { AppSettings } from '../types'

interface SettingsProps {
  settings: AppSettings
  onSettingsChange: (settings: Partial<AppSettings>) => void
}

export function Settings({ settings, onSettingsChange }: SettingsProps) {
  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'devices' | 'advanced'>('general')

  const tabs = [
    { id: 'general', name: 'Geral', icon: Cog6ToothIcon },
    { id: 'notifications', name: 'Notificações', icon: BellIcon },
    { id: 'devices', name: 'Dispositivos', icon: DevicePhoneMobileIcon },
    { id: 'advanced', name: 'Avançado', icon: ComputerDesktopIcon },
  ]

  const languages = [
    { code: 'pt-BR', name: 'Português (Brasil)', flag: '🇧🇷' },
    { code: 'en-US', name: 'English (United States)', flag: '🇺🇸' },
    { code: 'es-ES', name: 'Español (España)', flag: '🇪🇸' },
  ]

  const themes = [
    { value: 'light', name: 'Claro', icon: SunIcon },
    { value: 'dark', name: 'Escuro', icon: MoonIcon },
    { value: 'auto', name: 'Automático', icon: ComputerDesktopIcon },
  ]

  const handleSettingChange = (key: keyof AppSettings, value: any) => {
    onSettingsChange({ [key]: value })
  }

  const handleNotificationChange = (key: keyof AppSettings['notifications'], value: any) => {
    onSettingsChange({
      notifications: {
        ...settings.notifications,
        [key]: value
      }
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Configurações
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Personalize a interface e comportamento do sistema
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
            className="card"
          >
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Configurações Gerais
                  </h2>
                  
                  {/* Theme Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Tema da Interface
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {themes.map((theme) => {
                        const Icon = theme.icon
                        return (
                          <button
                            key={theme.value}
                            onClick={() => handleSettingChange('theme', theme.value)}
                            className={`flex items-center space-x-3 p-3 border rounded-lg transition-colors ${
                              settings.theme === theme.value
                                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                            }`}
                          >
                            <Icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              {theme.name}
                            </span>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Language Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Idioma
                    </label>
                    <select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                    >
                      {languages.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.flag} {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Refresh Interval */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Intervalo de Atualização: {settings.refreshInterval}s
                    </label>
                    <input
                      type="range"
                      min="5"
                      max="300"
                      step="5"
                      value={settings.refreshInterval}
                      onChange={(e) => handleSettingChange('refreshInterval', Number(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                    />
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>5s</span>
                      <span>60s</span>
                      <span>300s</span>
                    </div>
                  </div>

                  {/* Compact Mode */}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Modo Compacto
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Reduz espaçamento para mostrar mais informações
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.compactMode}
                        onChange={(e) => handleSettingChange('compactMode', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Settings */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Configurações de Notificações
                  </h2>
                  
                  {/* Enable Notifications */}
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Habilitar Notificações
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Receber alertas do sistema
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.enabled}
                        onChange={(e) => handleNotificationChange('enabled', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  {/* Sound Notifications */}
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Som de Notificação
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Reproduzir som para alertas
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.sound}
                        onChange={(e) => handleNotificationChange('sound', e.target.checked)}
                        className="sr-only peer"
                        disabled={!settings.notifications.enabled}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600 opacity-50"></div>
                    </label>
                  </div>

                  {/* Vibration Notifications */}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Vibração
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Vibrar para notificações importantes
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.vibration}
                        onChange={(e) => handleNotificationChange('vibration', e.target.checked)}
                        className="sr-only peer"
                        disabled={!settings.notifications.enabled}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600 opacity-50"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Devices Settings */}
            {activeTab === 'devices' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Configurações de Dispositivos
                  </h2>
                  
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <p className="mb-4">
                      Configure limiares e comportamentos dos dispositivos conectados.
                    </p>
                    
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                        <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                          Monitor ESP32 Filamento
                        </h3>
                        <p className="text-blue-600 dark:text-blue-300 text-sm">
                          Configuração automática baseada no peso atual do filamento
                        </p>
                      </div>
                      
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                        <h3 className="font-medium text-green-800 dark:text-green-200 mb-2">
                          Esteira Arduino
                        </h3>
                        <p className="text-green-600 dark:text-green-300 text-sm">
                          Controle de velocidade e modo automático/manual
                        </p>
                      </div>
                      
                      <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                        <h3 className="font-medium text-purple-800 dark:text-purple-200 mb-2">
                          Estação QC Raspberry Pi
                        </h3>
                        <p className="text-purple-600 dark:text-purple-300 text-sm">
                          Configuração de limiares de qualidade e tipos de defeito
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Advanced Settings */}
            {activeTab === 'advanced' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Configurações Avançadas
                  </h2>
                  
                  <div className="space-y-4">
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                      <h3 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                        Modo Desenvolvedor
                      </h3>
                      <p className="text-yellow-600 dark:text-yellow-300 text-sm">
                        Ativa logs detalhados e simulação de dados para desenvolvimento
                      </p>
                      <div className="mt-3">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            defaultChecked={import.meta.env.DEV}
                            disabled
                          />
                          <span className="text-sm text-yellow-700 dark:text-yellow-300">
                            Habilitado (Ambiente de desenvolvimento)
                          </span>
                        </label>
                      </div>
                    </div>
                    
                    <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <h3 className="font-medium text-red-800 dark:text-red-200 mb-2">
                        Limpar Dados
                      </h3>
                      <p className="text-red-600 dark:text-red-300 text-sm mb-3">
                        Remove todos os dados salvos e restaura configurações padrão
                      </p>
                      <button
                        onClick={() => {
                          if (confirm('Tem certeza que deseja restaurar todas as configurações?')) {
                            localStorage.clear()
                            window.location.reload()
                          }
                        }}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                      >
                        Restaurar Padrões
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}