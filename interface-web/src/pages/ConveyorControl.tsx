import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TruckIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  Cog6ToothIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '../contexts/DeviceContext'
import { deviceService } from '../services/deviceService'
import toast from 'react-hot-toast'
import type { ConveyorData } from '../types'

export function ConveyorControl() {
  const { state: deviceState } = useDevice()
  const [speed, setSpeed] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const [mode, setMode] = useState<'manual' | 'automatic'>('manual')
  const [direction, setDirection] = useState<'forward' | 'reverse' | 'stopped'>('stopped')

  const conveyorDevice = deviceState.devices.conveyor
  const data = conveyorDevice?.data as ConveyorData | undefined

  useEffect(() => {
    if (data) {
      setSpeed(data.speed)
      setIsRunning(data.isRunning)
      setMode(data.mode)
      setDirection(data.direction)
    }
  }, [data])

  const handleStart = async () => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    try {
      await deviceService.startConveyor()
      setIsRunning(true)
      toast.success('▶️ Esteira iniciada')
    } catch (error) {
      toast.error('❌ Erro ao iniciar esteira')
    }
  }

  const handleStop = async () => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    try {
      await deviceService.stopConveyor()
      setIsRunning(false)
      setDirection('stopped')
      toast.success('⏹️ Esteira parada')
    } catch (error) {
      toast.error('❌ Erro ao parar esteira')
    }
  }

  const handleEmergencyStop = async () => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    try {
      await deviceService.emergencyStopConveyor()
      setIsRunning(false)
      setDirection('stopped')
      setSpeed(0)
      toast.success('🛑 Parada de emergência ativada')
    } catch (error) {
      toast.error('❌ Erro na parada de emergência')
    }
  }

  const handleSpeedChange = async (newSpeed: number) => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    setSpeed(newSpeed)
    try {
      await deviceService.setConveyorSpeed(newSpeed)
    } catch (error) {
      toast.error('❌ Erro ao ajustar velocidade')
    }
  }

  const handleDirectionChange = async (newDirection: 'forward' | 'reverse' | 'stopped') => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    setDirection(newDirection)
    try {
      await deviceService.setConveyorDirection(newDirection)
    } catch (error) {
      toast.error('❌ Erro ao alterar direção')
    }
  }

  const handleModeToggle = async () => {
    if (!conveyorDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    const newMode = mode === 'manual' ? 'automatic' : 'manual'
    setMode(newMode)
    
    try {
      await deviceService.toggleConveyorMode()
      toast.success(`🔄 Modo alterado para ${newMode}`)
    } catch (error) {
      toast.error('❌ Erro ao alterar modo')
    }
  }

  const getLEDStatusColor = (ledStatus: string) => {
    switch (ledStatus) {
      case 'green': return 'bg-green-500'
      case 'yellow': return 'bg-yellow-500'
      case 'red': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Controle da Esteira Transportadora
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Controle manual e automático da esteira Arduino
          </p>
        </div>
      </div>

      {/* Status Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {/* Status Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <TruckIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className={`w-3 h-3 rounded-full ${data ? getLEDStatusColor(data.statusLED) : 'bg-gray-400'}`} />
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? (data.isRunning ? 'Ativo' : 'Parado') : '--'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {data ? `Modo ${data.mode === 'automatic' ? 'Automático' : 'Manual'}` : '--'}
            </p>
          </div>
        </div>

        {/* Speed Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <PlayIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">RPM</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Velocidade</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.speed.toFixed(0)}` : '--'}
            </p>
            <div className="mt-2">
              <input
                type="range"
                min="0"
                max="100"
                value={speed}
                onChange={(e) => handleSpeedChange(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                disabled={mode === 'automatic'}
              />
            </div>
          </div>
        </div>

        {/* Position Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Cog6ToothIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">mm</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Posição</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.position.toFixed(0)}` : '--'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Carga: {data ? `${data.load.toFixed(0)}%` : '--'}
            </p>
          </div>
        </div>

        {/* Temperature Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">°C</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Motor</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.motorTemperature.toFixed(1)}` : '--'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {data?.motorTemperature > 50 ? 'Quente' : 'Normal'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Painel de Controle
        </h2>
        
        {/* Emergency Stop */}
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Parada de Emergência
              </h3>
              <p className="text-xs text-red-600 dark:text-red-300">
                Para imediatamente todos os movimentos
              </p>
            </div>
            <button
              onClick={handleEmergencyStop}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              PARAR
            </button>
          </div>
        </div>

        {/* Main Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Speed and Direction */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Controle de Movimento
            </h3>
            
            {/* Direction Controls */}
            <div className="flex space-x-2">
              <button
                onClick={() => handleDirectionChange('forward')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                  direction === 'forward'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
                disabled={data?.emergencyStop}
              >
                <ArrowUpIcon className="w-4 h-4" />
                <span>Frente</span>
              </button>
              
              <button
                onClick={() => handleDirectionChange('stopped')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                  direction === 'stopped'
                    ? 'bg-gray-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
                disabled={data?.emergencyStop}
              >
                <StopIcon className="w-4 h-4" />
                <span>Parar</span>
              </button>
              
              <button
                onClick={() => handleDirectionChange('reverse')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                  direction === 'reverse'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
                disabled={data?.emergencyStop}
              >
                <ArrowDownIcon className="w-4 h-4" />
                <span>Ré</span>
              </button>
            </div>

            {/* Speed Control */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Velocidade: {speed} RPM
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={speed}
                onChange={(e) => handleSpeedChange(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                disabled={mode === 'automatic' || data?.emergencyStop}
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>
          </div>

          {/* Mode and Status */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Modo de Operação
            </h3>
            
            <button
              onClick={handleModeToggle}
              className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-colors ${
                mode === 'automatic'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
              disabled={data?.emergencyStop}
            >
              <Cog6ToothIcon className="w-4 h-4" />
              <span>Modo {mode === 'automatic' ? 'Automático' : 'Manual'}</span>
            </button>

            {/* Status Indicators */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Estado:</span>
                <span className={`font-medium ${
                  data?.emergencyStop ? 'text-red-600' : 
                  data?.isRunning ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {data?.emergencyStop ? 'Emergência' : data?.isRunning ? 'Ativo' : 'Parado'}
                </span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Direção:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {data ? (data.direction === 'forward' ? 'Frente' : 
                           data.direction === 'reverse' ? 'Ré' : 'Parado') : '--'}
                </span>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">LED Status:</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${data ? getLEDStatusColor(data.statusLED) : 'bg-gray-400'}`} />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {data?.statusLED === 'green' ? 'Verde' : 
                     data?.statusLED === 'yellow' ? 'Amarelo' : 
                     data?.statusLED === 'red' ? 'Vermelho' : 'Desconhecido'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Diagnostic Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Informações de Diagnóstico
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-600 dark:text-gray-400">Versão do Firmware</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {conveyorDevice?.version || '--'}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Endereço IP</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {conveyorDevice?.ipAddress || '--'}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Última Atualização</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {conveyorDevice?.lastUpdate ? 
                new Date(conveyorDevice.lastUpdate).toLocaleString('pt-BR') : 
                '--'
              }
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}