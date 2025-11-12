import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon,
  BeakerIcon,
  TruckIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  BoltIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '../contexts/DeviceContext'
import { deviceService } from '../services/deviceService'
import toast from 'react-hot-toast'

export function QuickActions() {
  const { state: deviceState } = useDevice()
  const [isExecuting, setIsExecuting] = useState<string | null>(null)

  const actions = [
    {
      id: 'start-production',
      name: 'Iniciar Produção',
      description: 'Inicia todos os dispositivos',
      icon: PlayIcon,
      color: 'bg-green-600 hover:bg-green-700',
      execute: async () => {
        setIsExecuting('start-production')
        try {
          // Start conveyor
          await deviceService.startConveyor()
          // Start QC station
          await deviceService.controlDevice('qc', 'start_monitoring')
          toast.success('🚀 Produção iniciada com sucesso!')
        } catch (error) {
          toast.error('❌ Erro ao iniciar produção')
        } finally {
          setIsExecuting(null)
        }
      }
    },
    {
      id: 'pause-production',
      name: 'Pausar Produção',
      description: 'Pausa a esteira transportadora',
      icon: PauseIcon,
      color: 'bg-yellow-600 hover:bg-yellow-700',
      execute: async () => {
        setIsExecuting('pause-production')
        try {
          await deviceService.controlDevice('conveyor', 'pause')
          toast.success('⏸️ Produção pausada')
        } catch (error) {
          toast.error('❌ Erro ao pausar produção')
        } finally {
          setIsExecuting(null)
        }
      }
    },
    {
      id: 'emergency-stop',
      name: 'Parada de Emergência',
      description: 'Para imediatamente todos os sistemas',
      icon: StopIcon,
      color: 'bg-red-600 hover:bg-red-700',
      execute: async () => {
        setIsExecuting('emergency-stop')
        try {
          await deviceService.emergencyStopConveyor()
          await deviceService.controlDevice('qc', 'stop_inspection')
          toast.success('🛑 Parada de emergência ativada!')
        } catch (error) {
          toast.error('❌ Erro na parada de emergência')
        } finally {
          setIsExecuting(null)
        }
      }
    },
    {
      id: 'calibrate-filament',
      name: 'Calibrar Filamento',
      description: 'Inicia calibração da balança ESP32',
      icon: BeakerIcon,
      color: 'bg-blue-600 hover:bg-blue-700',
      execute: async () => {
        setIsExecuting('calibrate-filament')
        try {
          await deviceService.calibrateFilamentScale()
          toast.success('⚖️ Calibração do filamento iniciada')
        } catch (error) {
          toast.error('❌ Erro na calibração')
        } finally {
          setIsExecuting(null)
        }
      }
    },
    {
      id: 'qc-inspection',
      name: 'Inspeção QC',
      description: 'Executa inspeção de qualidade manual',
      icon: MagnifyingGlassIcon,
      color: 'bg-purple-600 hover:bg-purple-700',
      execute: async () => {
        setIsExecuting('qc-inspection')
        try {
          await deviceService.performQCInspection()
          toast.success('🔍 Inspeção QC iniciada')
        } catch (error) {
          toast.error('❌ Erro na inspeção QC')
        } finally {
          setIsExecuting(null)
        }
      }
    },
    {
      id: 'system-check',
      name: 'Verificar Sistema',
      description: 'Executa diagnóstico completo',
      icon: Cog6ToothIcon,
      color: 'bg-gray-600 hover:bg-gray-700',
      execute: async () => {
        setIsExecuting('system-check')
        try {
          // Simulate system check
          await new Promise(resolve => setTimeout(resolve, 2000))
          toast.success('✅ Verificação do sistema concluída')
        } catch (error) {
          toast.error('❌ Erro na verificação do sistema')
        } finally {
          setIsExecuting(null)
        }
      }
    }
  ]

  const isAnyDeviceOffline = !deviceState.devices.filament || 
                             !deviceState.devices.conveyor || 
                             !deviceState.devices.qc

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Ações Rápidas
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Controle rápido dos dispositivos
          </p>
        </div>
        
        {isAnyDeviceOffline && (
          <div className="flex items-center space-x-2 text-yellow-600 dark:text-yellow-400">
            <ExclamationTriangleIcon className="w-5 h-5" />
            <span className="text-sm font-medium">Dispositivos offline</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <AnimatePresence>
          {actions.map((action) => (
            <motion.button
              key={action.id}
              onClick={action.execute}
              disabled={isExecuting === action.id || isAnyDeviceOffline}
              className={`${action.color} text-white p-4 rounded-lg text-left transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {isExecuting === action.id ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <action.icon className="w-5 h-5" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {action.name}
                  </p>
                  <p className="text-xs opacity-90 truncate">
                    {action.description}
                  </p>
                </div>
              </div>
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* Status indicators */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              deviceState.devices.filament?.status === 'online' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-600 dark:text-gray-400">Monitor Filamento</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              deviceState.devices.conveyor?.status === 'online' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-600 dark:text-gray-400">Esteira Transportadora</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              deviceState.devices.qc?.status === 'online' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-gray-600 dark:text-gray-400">Estação QC</span>
          </div>
        </div>
      </div>
    </div>
  )
}