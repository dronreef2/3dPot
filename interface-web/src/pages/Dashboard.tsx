import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BeakerIcon, 
  TruckIcon, 
  MagnifyingGlassIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '@contexts/DeviceContext'
import { DeviceCard } from '@components/DeviceCard'
import { ProductionChart } from '@components/Charts/ProductionChart'
import { QuickActions } from '@components/QuickActions'
import type { AnalyticsData, ChartData } from '@types'

export function Dashboard() {
  const { state: deviceState, refreshDevices } = useDevice()
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const devices = [
    {
      id: 'filament',
      name: 'Monitor ESP32',
      type: 'filament' as const,
      icon: BeakerIcon,
      device: deviceState.devices.filament,
      status: deviceState.devices.filament?.status || 'offline',
      lastUpdate: deviceState.devices.filament?.lastUpdate,
    },
    {
      id: 'conveyor',
      name: 'Esteira Arduino',
      type: 'conveyor' as const,
      icon: TruckIcon,
      device: deviceState.devices.conveyor,
      status: deviceState.devices.conveyor?.status || 'offline',
      lastUpdate: deviceState.devices.conveyor?.lastUpdate,
    },
    {
      id: 'qc',
      name: 'Estação QC',
      type: 'qc' as const,
      icon: MagnifyingGlassIcon,
      device: deviceState.devices.qc,
      status: deviceState.devices.qc?.status || 'offline',
      lastUpdate: deviceState.devices.qc?.lastUpdate,
    }
  ]

  const onlineDevices = devices.filter(d => d.status === 'online').length
  const offlineDevices = devices.filter(d => d.status === 'offline').length
  const warningDevices = devices.filter(d => d.status === 'warning').length

  // Generate mock analytics data
  const generateAnalytics = (): AnalyticsData => ({
    production: {
      today: Math.floor(Math.random() * 50) + 20,
      week: Math.floor(Math.random() * 300) + 200,
      month: Math.floor(Math.random() * 1200) + 800,
      trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as 'up' | 'down' | 'stable'
    },
    quality: {
      passRate: Math.random() * 20 + 80, // 80-100%
      avgClassification: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
      topDefects: ['layer_shift', 'stringing', 'under_extrusion', 'surface_roughness'].slice(0, 2)
    },
    system: {
      uptime: Math.floor(Math.random() * 86400) + 7200, // 2-24 hours in seconds
      activeDevices: onlineDevices,
      totalDevices: 3
    }
  })

  // Generate mock chart data
  const generateChartData = (): ChartData => {
    const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    return {
      labels: hours,
      datasets: [
        {
          label: 'Produção (peças)',
          data: hours.map(() => Math.floor(Math.random() * 10) + 1),
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 2,
        },
        {
          label: 'Qualidade (%)',
          data: hours.map(() => Math.random() * 20 + 80),
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderColor: 'rgb(34, 197, 94)',
          borderWidth: 2,
        }
      ]
    }
  }

  const chartData = generateChartData()

  useEffect(() => {
    setAnalytics(generateAnalytics())
    
    // Update analytics every 30 seconds
    const interval = setInterval(() => {
      setAnalytics(generateAnalytics())
    }, 30000)
    
    return () => clearInterval(interval)
  }, [deviceState.devices])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await refreshDevices()
    setTimeout(() => setIsRefreshing(false), 1000)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard Principal
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Visão geral do sistema de produção
          </p>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="mt-4 sm:mt-0 btn-primary flex items-center space-x-2 disabled:opacity-50"
        >
          <ArrowTrendingUpIcon className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>{isRefreshing ? 'Atualizando...' : 'Atualizar'}</span>
        </button>
      </div>

      {/* System Status Overview */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircleIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Dispositivos Online</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {onlineDevices}/3
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Alertas Ativos</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {deviceState.alerts.filter(a => !a.acknowledged).length}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <ClockIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Uptime</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {analytics ? Math.floor(analytics.system.uptime / 3600) : 0}h
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <ArrowTrendingUpIcon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Taxa de Qualidade</p>
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {analytics ? Math.round(analytics.quality.passRate) : 0}%
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Device Cards */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {devices.map((device) => (
          <motion.div key={device.id} variants={itemVariants}>
            <DeviceCard
              id={device.id}
              name={device.name}
              type={device.type}
              icon={device.icon}
              device={device.device}
              status={device.status}
              lastUpdate={device.lastUpdate}
            />
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <QuickActions />
        </motion.div>
      </motion.div>

      {/* Production Chart */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="card">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Produção em Tempo Real
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Acompanhamento das últimas 24 horas
            </p>
          </div>
          <ProductionChart data={chartData} />
        </motion.div>
      </motion.div>

      {/* Analytics Summary */}
      {analytics && (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          <motion.div variants={itemVariants} className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Estatísticas de Produção
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Hoje</span>
                <span className="font-medium">{analytics.production.today} peças</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Esta semana</span>
                <span className="font-medium">{analytics.production.week} peças</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Este mês</span>
                <span className="font-medium">{analytics.production.month} peças</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Tendência</span>
                <span className={`font-medium ${
                  analytics.production.trend === 'up' ? 'text-green-600' :
                  analytics.production.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {analytics.production.trend === 'up' ? '↗️ Crescendo' :
                   analytics.production.trend === 'down' ? '↘️ Diminuindo' : '➡️ Estável'}
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Qualidade e Defeitos
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Taxa de Aprovação</span>
                <span className="font-medium text-green-600">
                  {Math.round(analytics.quality.passRate)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Classificação Média</span>
                <span className="font-medium">{analytics.quality.avgClassification}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400 block mb-2">
                  Defeitos Mais Comuns
                </span>
                <div className="space-y-1">
                  {analytics.quality.topDefects.map((defect, index) => (
                    <div key={defect} className="flex justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-500">
                        {index + 1}. {defect.replace('_', ' ')}
                      </span>
                      <span className="text-red-600 dark:text-red-400">
                        {Math.floor(Math.random() * 20) + 5}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}