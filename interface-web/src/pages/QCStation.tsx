import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  MagnifyingGlassIcon,
  CameraIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '@contexts/DeviceContext'
import { deviceService } from '@services/deviceService'
import { QCChart } from '@components/Charts/QCChart'
import toast from 'react-hot-toast'
import type { QCData } from '@types'

export function QCStation() {
  const { state: deviceState } = useDevice()
  const [isInspecting, setIsInspecting] = useState(false)
  const [statistics, setStatistics] = useState<any>(null)

  const qcDevice = deviceState.devices.qc
  const data = qcDevice?.data as QCData | undefined

  useEffect(() => {
    // Load statistics
    const loadStatistics = async () => {
      try {
        const stats = await deviceService.getQCStatistics('day')
        setStatistics(stats)
      } catch (error) {
        console.warn('Failed to load QC statistics:', error)
      }
    }
    
    loadStatistics()
    
    // Refresh statistics every 30 seconds
    const interval = setInterval(loadStatistics, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleInspection = async () => {
    if (!qcDevice) {
      toast.error('Dispositivo não encontrado')
      return
    }
    
    setIsInspecting(true)
    try {
      await deviceService.performQCInspection()
      toast.success('🔍 Inspeção iniciada')
      
      // Simulate inspection completion
      setTimeout(() => {
        setIsInspecting(false)
        toast.success('✅ Inspeção concluída')
      }, 3000)
    } catch (error) {
      setIsInspecting(false)
      toast.error('❌ Erro na inspeção')
    }
  }

  const handleGenerateReport = async () => {
    try {
      const blob = await deviceService.generateQCReport('pdf')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `qc-report-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('📄 Relatório gerado')
    } catch (error) {
      toast.error('❌ Erro ao gerar relatório')
    }
  }

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'A': return 'text-green-600 bg-green-100 dark:bg-green-900'
      case 'B': return 'text-blue-600 bg-blue-100 dark:bg-blue-900'
      case 'C': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900'
      case 'D': return 'text-orange-600 bg-orange-100 dark:bg-orange-900'
      case 'F': return 'text-red-600 bg-red-100 dark:bg-red-900'
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Estação de Controle de Qualidade
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Inspeção automática por IA com Raspberry Pi
          </p>
        </div>
      </div>

      {/* Status Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {/* Camera Status Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <CameraIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className={`w-3 h-3 rounded-full ${
              data?.cameraStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Câmera</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data?.cameraStatus === 'connected' ? 'Conectada' : 'Offline'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {data?.cameraStatus === 'calibrating' ? 'Calibrando...' : 'Ativa'}
            </p>
          </div>
        </div>

        {/* Last Inspection Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <MagnifyingGlassIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className={`px-2 py-1 text-xs font-medium rounded-full ${
              getClassificationColor(data?.lastInspection.classification || 'F')
            }`}>
              {data?.lastInspection.classification || '--'}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Última Inspeção</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data?.lastInspection.confidence ? 
                `${(data.lastInspection.confidence * 100).toFixed(1)}%` : 
                '--'
              }
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {data?.lastInspection.defectType || 'Nenhum defeito'}
            </p>
          </div>
        </div>

        {/* Pass Rate Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircleIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Dia</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Taxa de Aprovação</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data?.statistics.passRate ? 
                `${data.statistics.passRate.toFixed(1)}%` : 
                '--'
              }
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {data?.statistics.totalInspected || 0} peças inspecionadas
            </p>
          </div>
        </div>

        {/* LED Status Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className={`w-3 h-3 rounded-full ${
              data?.ledStatus === 'green' ? 'bg-green-500' :
              data?.ledStatus === 'yellow' ? 'bg-yellow-500' :
              data?.ledStatus === 'red' ? 'bg-red-500' : 'bg-gray-500'
            }`} />
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Status LED</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {data?.ledStatus === 'green' ? 'Verde' :
               data?.ledStatus === 'yellow' ? 'Amarelo' :
               data?.ledStatus === 'red' ? 'Vermelho' : '--'
              }
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Sistema {data?.ledStatus === 'green' ? 'Normal' : 'Atenção'}
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
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Controle de Inspeção
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button
            onClick={handleInspection}
            disabled={isInspecting || data?.cameraStatus !== 'connected'}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isInspecting ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <MagnifyingGlassIcon className="w-5 h-5" />
            )}
            <span>{isInspecting ? 'Inspecionando...' : 'Nova Inspeção'}</span>
          </button>

          <button
            onClick={() => {
              toast.success('📊 Calibração iniciada')
              // Simulate calibration
              setTimeout(() => toast.success('✅ Calibração concluída'), 2000)
            }}
            disabled={data?.cameraStatus !== 'connected'}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CameraIcon className="w-5 h-5" />
            <span>Calibrar</span>
          </button>

          <button
            onClick={handleGenerateReport}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <DocumentTextIcon className="w-5 h-5" />
            <span>Gerar Relatório</span>
          </button>
        </div>
      </motion.div>

      {/* Last Inspection Details */}
      {data?.lastInspection && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Detalhes da Última Inspeção
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Classificação:</span>
                  <span className={`px-2 py-1 text-sm font-medium rounded-full ${
                    getClassificationColor(data.lastInspection.classification)
                  }`}>
                    {data.lastInspection.classification}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Confiança:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(data.lastInspection.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Tipo de Defeito:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {data.lastInspection.defectType || 'Nenhum'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Timestamp:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {new Date(data.lastInspection.timestamp).toLocaleString('pt-BR')}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Imagem da Peça
              </h3>
              <div className="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <CameraIcon className="w-12 h-12 mx-auto mb-2" />
                  <p className="text-sm">Imagem da inspeção</p>
                  <p className="text-xs">Clique para visualizar</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Statistics and Charts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Quality Statistics */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Estatísticas de Qualidade
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Total Inspecionado:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {data?.statistics.totalInspected || 0} peças
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Taxa de Aprovação:</span>
              <span className="font-medium text-green-600">
                {data?.statistics.passRate.toFixed(1) || 0}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Confiança Média:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {(data?.statistics.avgConfidence * 100).toFixed(1) || 0}%
              </span>
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-400 mb-2">Defeitos Mais Comuns:</p>
              <div className="space-y-1">
                {data?.statistics.commonDefects.slice(0, 3).map((defect, index) => (
                  <div key={defect} className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-500">
                      {index + 1}. {defect.replace('_', ' ')}
                    </span>
                    <span className="text-red-600 dark:text-red-400">
                      {Math.floor(Math.random() * 20) + 5}%
                    </span>
                  </div>
                )) || (
                  <p className="text-sm text-gray-500 dark:text-gray-500">Nenhum defeito registrado</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Análise de Qualidade
          </h2>
          <QCChart />
        </div>
      </motion.div>
    </div>
  )
}