import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  ChevronRightIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { useNavigate } from 'react-router-dom'
import { useDevice } from '@contexts/DeviceContext'
import type { Device, FilamentDevice, ConveyorDevice, QCDevice } from '@types'

interface DeviceCardProps {
  id: 'filament' | 'conveyor' | 'qc'
  name: string
  type: 'filament' | 'conveyor' | 'qc'
  icon: React.ComponentType<{ className?: string }>
  device?: FilamentDevice | ConveyorDevice | QCDevice
  status: 'online' | 'offline' | 'warning' | 'error'
  lastUpdate?: Date
}

const statusConfig = {
  online: {
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900',
    icon: CheckCircleIcon,
    text: 'Online'
  },
  offline: {
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900',
    icon: XCircleIcon,
    text: 'Offline'
  },
  warning: {
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900',
    icon: ExclamationTriangleIcon,
    text: 'Aviso'
  },
  error: {
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900',
    icon: ExclamationTriangleIcon,
    text: 'Erro'
  }
}

function formatTimeAgo(date: Date): string {
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'Agora'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}min atrás`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h atrás`
  return `${Math.floor(diffInSeconds / 86400)}d atrás`
}

function getDeviceSummary(device: FilamentDevice | ConveyorDevice | QCDevice) {
  if (device.type === 'filament') {
    return {
      primary: `${device.data.weight.toFixed(1)}g`,
      secondary: `${device.data.temperature.toFixed(1)}°C`,
      status: device.data.isSleeping ? '休眠中' : 'Ativo',
      progress: (device.data.weight / 1000) * 100 // Percentage of 1kg
    }
  }
  
  if (device.type === 'conveyor') {
    return {
      primary: `${device.data.speed.toFixed(0)} RPM`,
      secondary: device.data.isRunning ? '运行中' : '停止',
      status: device.data.mode === 'automatic' ? 'Automático' : 'Manual',
      progress: (device.data.speed / 100) * 100
    }
  }
  
  if (device.type === 'qc') {
    return {
      primary: device.data.lastInspection.classification,
      secondary: `${(device.data.lastInspection.confidence * 100).toFixed(1)}%`,
      status: 'Aguardando...',
      progress: device.data.lastInspection.confidence * 100
    }
  }
  
  return {
    primary: '--',
    secondary: '--',
    status: 'Desconhecido',
    progress: 0
  }
}

export function DeviceCard({ id, name, type, icon: Icon, device, status, lastUpdate }: DeviceCardProps) {
  const navigate = useNavigate()
  const { dispatch } = useDevice()
  const [isHovered, setIsHovered] = useState(false)
  
  const config = statusConfig[status]
  const StatusIcon = config.icon
  const summary = device ? getDeviceSummary(device) : null

  const handleCardClick = () => {
    navigate(`/${type}`)
  }

  const getStatusIndicator = () => {
    return (
      <div className={`flex items-center space-x-1 ${config.color}`}>
        <div className={`w-2 h-2 rounded-full ${config.color.replace('text-', 'bg-')}`} />
        <span className="text-xs font-medium">{config.text}</span>
      </div>
    )
  }

  const getQuickAction = () => {
    if (type === 'conveyor' && device) {
      const conveyorData = (device as ConveyorDevice).data
      if (conveyorData.emergencyStop) {
        return (
          <button
            onClick={(e) => {
              e.stopPropagation()
              // Emergency stop action would be handled here
            }}
            className="px-2 py-1 text-xs font-medium text-white bg-red-600 rounded hover:bg-red-700 transition-colors"
          >
            Parar Emergência
          </button>
        )
      }
    }
    
    if (type === 'filament' && device) {
      const filamentData = (device as FilamentDevice).data
      if (filamentData.calibrationMode) {
        return (
          <button
            onClick={(e) => {
              e.stopPropagation()
              // Calibrate action would be handled here
            }}
            className="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Calibrar
          </button>
        )
      }
    }
    
    return null
  }

  return (
    <motion.div
      className="device-card cursor-pointer"
      onClick={handleCardClick}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 ${config.bgColor} rounded-lg`}>
            <Icon className={`w-5 h-5 ${config.color}`} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {name}
            </h3>
            {getStatusIndicator()}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {getQuickAction()}
          <ChevronRightIcon 
            className={`w-4 h-4 text-gray-400 transition-transform ${
              isHovered ? 'transform translate-x-1' : ''
            }`} 
          />
        </div>
      </div>

      {/* Device Data */}
      {device && summary ? (
        <div className="space-y-3">
          {/* Primary metric */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {type === 'filament' ? 'Peso' : 
                 type === 'conveyor' ? 'Velocidade' : 'Classificação'}
              </p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {summary.primary}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {type === 'filament' ? 'Temperatura' : 
                 type === 'conveyor' ? 'Estado' : 'Confiança'}
              </p>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {summary.secondary}
              </p>
            </div>
          </div>

          {/* Progress bar for devices that have it */}
          {summary.progress > 0 && (
            <div>
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                <span>Progresso</span>
                <span>{Math.round(summary.progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    summary.progress > 80 ? 'bg-green-500' :
                    summary.progress > 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(summary.progress, 100)}%` }}
                />
              </div>
            </div>
          )}

          {/* Additional status info */}
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center space-x-1">
              <StatusIcon className="w-3 h-3" />
              <span>{summary.status}</span>
            </span>
            {lastUpdate && (
              <span className="flex items-center space-x-1">
                <ClockIcon className="w-3 h-3" />
                <span>{formatTimeAgo(lastUpdate)}</span>
              </span>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <XCircleIcon className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">Dispositivo não encontrado</p>
            </div>
          </div>
        </div>
      )}

      {/* Device specific information */}
      {device && type === 'filament' && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Bateria:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {(device as FilamentDevice).data.batteryLevel.toFixed(0)}%
              </span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Tempo estimado:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {(device as FilamentDevice).data.estimatedTime.toFixed(1)}h
              </span>
            </div>
          </div>
        </div>
      )}

      {device && type === 'conveyor' && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Posição:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {(device as ConveyorDevice).data.position.toFixed(0)}mm
              </span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Carga:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {(device as ConveyorDevice).data.load.toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {device && type === 'qc' && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-1 gap-2 text-xs">
            <div>
              <span className="text-gray-500 dark:text-gray-400">Última inspeção:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {formatTimeAgo((device as QCDevice).data.lastInspection.timestamp)}
              </span>
            </div>
            <div>
              <span className="text-gray-500 dark:text-gray-400">Total inspecionado:</span>
              <span className="ml-1 font-medium text-gray-700 dark:text-gray-300">
                {(device as QCDevice).data.statistics.totalInspected} peças
              </span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}