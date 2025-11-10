import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BeakerIcon,
  BatteryIcon,
  ThermometerIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '@contexts/DeviceContext'
import { deviceService } from '@services/deviceService'
import { FilamentChart } from '@components/Charts/FilamentChart'
import toast from 'react-hot-toast'
import type { FilamentData } from '@types'

export function FilamentMonitor() {
  const { state: deviceState } = useDevice()
  const [isCalibrating, setIsCalibrating] = useState(false)
  const [isSleeping, setIsSleeping] = useState(false)
  const [threshold, setThreshold] = useState({ min: 50, max: 900 })

  const filamentDevice = deviceState.devices.filament
  const data = filamentDevice?.data as FilamentData | undefined

  useEffect(() => {
    if (data) {
      setIsSleeping(data.isSleeping)
      setThreshold(data.alertThreshold)
    }
  }, [data])

  const handleCalibrate = async () => {
    if (!filamentDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    setIsCalibrating(true)
    try {
      await deviceService.calibrateFilamentScale()
      toast.success('⚖️ Calibração iniciada')
      
      // Simulate calibration completion
      setTimeout(() => {
        setIsCalibrating(false)
        toast.success('✅ Calibração concluída')
      }, 3000)
    } catch (error) {
      setIsCalibrating(false)
      toast.error('❌ Erro na calibração')
    }
  }

  const handleSleep = async () => {
    if (!filamentDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    try {
      if (isSleeping) {
        await deviceService.wakeFilamentUp()
        setIsSleeping(false)
        toast.success('🔔 ESP32 acordado')
      } else {
        await deviceService.putFilamentToSleep()
        setIsSleeping(true)
        toast.success('😴 ESP32 em modo sleep')
      }
    } catch (error) {
      toast.error('❌ Erro ao controlar dispositivo')
    }
  }

  const handleThresholdUpdate = async () => {
    if (!filamentDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    try {
      await deviceService.setFilamentThreshold(threshold)
      toast.success('📊 Limites atualizados')
    } catch (error) {
      toast.error('❌ Erro ao atualizar limites')
    }
  }

  const getBatteryColor = (level: number) => {
    if (level > 50) return 'text-green-600 dark:text-green-400'
    if (level > 20) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getWeightStatus = (weight: number) => {
    if (weight < threshold.min) return { status: 'low', color: 'text-red-600', text: 'Fio baixo' }
    if (weight > threshold.max) return { status: 'high', color: 'text-blue-600', text: 'Sobrecarga' }
    return { status: 'normal', color: 'text-green-600', text: 'Normal' }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Monitor ESP32 de Filamento
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitoramento em tempo real do consumo de filamento
          </p>
        </div>
      </div>

      {/* Status Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {/* Weight Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <BeakerIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            {data && (
              <div className={`text-sm font-medium ${getWeightStatus(data.weight).color}`}>
                {getWeightStatus(data.weight).text}
              </div>
            )}
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Peso Atual</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.weight.toFixed(1)}g` : '--'}
            </p>
            {data && (
              <div className="mt-2">
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                  <span>Progresso</span>
                  <span>{((data.weight / 1000) * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      data.weight < threshold.min ? 'bg-red-500' :
                      data.weight > threshold.max ? 'bg-blue-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min((data.weight / 1000) * 100, 100)}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Temperature Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <ThermometerIcon className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Ambiente</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Temperatura</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.temperature.toFixed(1)}°C` : '--'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Umidade: {data ? `${data.humidity.toFixed(1)}%` : '--'}
            </p>
          </div>
        </div>

        {/* Battery Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <BatteryIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className={`text-sm font-medium ${data ? getBatteryColor(data.batteryLevel) : 'text-gray-500'}`}>
              {data ? `${data.batteryLevel.toFixed(0)}%` : '--'}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Bateria</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.batteryLevel.toFixed(0)}%` : '--'}
            </p>
            <div className="mt-2">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    data && data.batteryLevel > 50 ? 'bg-green-500' :
                    data && data.batteryLevel > 20 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${data ? data.batteryLevel : 0}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Estimated Time Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <ClockIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {isSleeping ? 'Dormindo' : 'Ativo'}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Tempo Estimado</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data ? `${data.estimatedTime.toFixed(1)}h` : '--'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {isSleeping ? 'Modo deep sleep' : 'Consumo ativo'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Ações de Controle
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={handleCalibrate}
            disabled={isCalibrating || isSleeping}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCalibrating ? (
              <ArrowPathIcon className="w-5 h-5 animate-spin" />
            ) : (
              <CpuChipIcon className="w-5 h-5" />
            )}
            <span>{isCalibrating ? 'Calibrando...' : 'Calibrar'}</span>
          </button>

          <button
            onClick={handleSleep}
            disabled={!data}
            className={`flex items-center justify-center space-x-2 px-4 py-3 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              isSleeping 
                ? 'bg-green-600 hover:bg-green-700' 
                : 'bg-gray-600 hover:bg-gray-700'
            }`}
          >
            {isSleeping ? (
              <CheckCircleIcon className="w-5 h-5" />
            ) : (
              <CpuChipIcon className="w-5 h-5" />
            )}
            <span>{isSleeping ? 'Acordar' : 'Dormir'}</span>
          </button>

          <button
            onClick={() => {
              // Quick threshold adjustment
              const newThreshold = {
                min: Math.max(10, data ? data.weight * 0.1 : 50),
                max: Math.min(1000, data ? data.weight * 0.95 : 900)
              }
              setThreshold(newThreshold)
              toast.success('Limites ajustados automaticamente')
            }}
            disabled={!data}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ExclamationTriangleIcon className="w-5 h-5" />
            <span>Auto-limits</span>
          </button>

          <button
            onClick={() => {
              // Reset to defaults
              setThreshold({ min: 50, max: 900 })
              toast.success('Limites restaurados ao padrão')
            }}
            disabled={!data}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowPathIcon className="w-5 h-5" />
            <span>Reset</span>
          </button>
        </div>
      </motion.div>

      {/* Threshold Configuration */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Configuração de Alertas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Peso Mínimo (g)
            </label>
            <input
              type="number"
              value={threshold.min}
              onChange={(e) => setThreshold(prev => ({ ...prev, min: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              min="1"
              max="500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Peso Máximo (g)
            </label>
            <input
              type="number"
              value={threshold.max}
              onChange={(e) => setThreshold(prev => ({ ...prev, max: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              min="100"
              max="2000"
            />
          </div>
        </div>
        <div className="mt-4 flex space-x-3">
          <button
            onClick={handleThresholdUpdate}
            className="btn-primary"
          >
            Salvar Configurações
          </button>
          <button
            onClick={() => setThreshold({ min: 50, max: 900 })}
            className="btn-secondary"
          >
            Restaurar Padrão
          </button>
        </div>
      </motion.div>

      {/* Charts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Histórico de Consumo
        </h2>
        <FilamentChart />
      </motion.div>
    </div>
  )
}