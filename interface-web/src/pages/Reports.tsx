import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  DocumentTextIcon,
  ChartBarIcon,
  CalendarIcon,
  ArrowDownTrayIcon,
  PrinterIcon,
  ShareIcon
} from '@heroicons/react/24/outline'
import { useDevice } from '../contexts/DeviceContext'
import { deviceService } from '../services/deviceService'
import { ReportsChart } from '@components/Charts/ReportsChart'
import toast from 'react-hot-toast'

export function Reports() {
  const { state: deviceState } = useDevice()
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('day')
  const [selectedDevice, setSelectedDevice] = useState<'all' | 'filament' | 'conveyor' | 'qc'>('all')
  const [isGenerating, setIsGenerating] = useState(false)

  const periods = [
    { value: 'day', name: 'Hoje' },
    { value: 'week', name: 'Esta Semana' },
    { value: 'month', name: 'Este Mês' }
  ]

  const devices = [
    { value: 'all', name: 'Todos os Dispositivos' },
    { value: 'filament', name: 'Monitor Filamento' },
    { value: 'conveyor', name: 'Esteira Transportadora' },
    { value: 'qc', name: 'Estação QC' }
  ]

  // Generate mock report data
  const generateReportData = () => {
    const baseData = {
      totalInspected: Math.floor(Math.random() * 500) + 100,
      passRate: Math.random() * 20 + 80,
      totalFilament: Math.floor(Math.random() * 50) + 20,
      conveyorUsage: Math.random() * 100,
      avgQualityScore: Math.random() * 20 + 80,
      alerts: Math.floor(Math.random() * 10),
      efficiency: Math.random() * 30 + 70
    }

    return baseData
  }

  const reportData = generateReportData()

  const handleGenerateReport = async (format: 'pdf' | 'csv' | 'json') => {
    setIsGenerating(true)
    try {
      if (format === 'pdf' && selectedDevice === 'qc') {
        const blob = await deviceService.generateQCReport('pdf')
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `3dpot-report-${selectedPeriod}-${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        // Simulate report generation
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        if (format === 'csv') {
          // Create CSV content
          const csvContent = `Relatório 3dPot - ${periods.find(p => p.value === selectedPeriod)?.name}\n` +
                           `Período: ${new Date().toLocaleDateString('pt-BR')}\n` +
                           `Total Inspecionado: ${reportData.totalInspected}\n` +
                           `Taxa de Aprovação: ${reportData.passRate.toFixed(1)}%\n` +
                           `Filamento Utilizado: ${reportData.totalFilament}kg\n` +
                           `Uso da Esteira: ${reportData.conveyorUsage.toFixed(1)}%\n` +
                           `Pontuação Média: ${reportData.avgQualityScore.toFixed(1)}\n` +
                           `Alertas: ${reportData.alerts}\n` +
                           `Eficiência: ${reportData.efficiency.toFixed(1)}%`
          
          const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `3dpot-report-${selectedPeriod}-${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        } else if (format === 'json') {
          const jsonData = {
            period: selectedPeriod,
            device: selectedDevice,
            generatedAt: new Date().toISOString(),
            data: reportData,
            devices: {
              filament: deviceState.devices.filament,
              conveyor: deviceState.devices.conveyor,
              qc: deviceState.devices.qc
            }
          }
          
          const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `3dpot-report-${selectedPeriod}-${new Date().toISOString().split('T')[0]}.json`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        }
      }
      
      toast.success(`📄 Relatório ${format.toUpperCase()} gerado com sucesso!`)
    } catch (error) {
      toast.error('❌ Erro ao gerar relatório')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Relatório 3dPot',
          text: `Relatório de produção do período: ${periods.find(p => p.value === selectedPeriod)?.name}`,
          url: window.location.href
        })
      } catch (error) {
        console.log('Error sharing:', error)
      }
    } else {
      // Fallback: copy to clipboard
      const shareText = `Relatório 3dPot - ${periods.find(p => p.value === selectedPeriod)?.name}\n` +
                       `Taxa de Aprovação: ${reportData.passRate.toFixed(1)}%\n` +
                       `Total Inspecionado: ${reportData.totalInspected} peças`
      navigator.clipboard.writeText(shareText)
      toast.success('📋 Relatório copiado para a área de transferência')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Relatórios e Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Análise detalhada de performance e qualidade
          </p>
        </div>
      </div>

      {/* Report Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Configuração do Relatório
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Período de Análise
            </label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              {periods.map((period) => (
                <option key={period.value} value={period.value}>
                  {period.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Dispositivo
            </label>
            <select
              value={selectedDevice}
              onChange={(e) => setSelectedDevice(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              {devices.map((device) => (
                <option key={device.value} value={device.value}>
                  {device.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Report Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Total</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Peças Inspecionadas</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {reportData.totalInspected}
            </p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              +{Math.floor(Math.random() * 20 + 5)} desde ontem
            </p>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Qualidade</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Taxa de Aprovação</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {reportData.passRate.toFixed(1)}%
            </p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              Meta: 95%
            </p>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <DocumentTextIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Matéria-prima</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Filamento Utilizado</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {reportData.totalFilament}kg
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              R$ {(reportData.totalFilament * 120).toFixed(2)} em custos
            </p>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Eficiência</div>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Produtividade</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {reportData.efficiency.toFixed(1)}%
            </p>
            <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
              {reportData.alerts} alertas ativos
            </p>
          </div>
        </div>
      </motion.div>

      {/* Charts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Análise de Tendências
        </h2>
        <ReportsChart period={selectedPeriod} />
      </motion.div>

      {/* Detailed Statistics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Estatísticas por Dispositivo
          </h3>
          <div className="space-y-4">
            {[
              { name: 'Monitor ESP32', status: 'online', uptime: '99.2%', efficiency: 94 },
              { name: 'Esteira Arduino', status: 'online', uptime: '97.8%', efficiency: 89 },
              { name: 'Estação QC', status: 'online', uptime: '98.5%', efficiency: 96 }
            ].map((device, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{device.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Uptime: {device.uptime}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {device.efficiency}% eficiência
                  </p>
                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    device.status === 'online' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {device.status === 'online' ? 'Online' : 'Offline'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Principais Indicadores
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Tempo médio de inspeção:</span>
              <span className="font-medium text-gray-900 dark:text-white">2.3s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Taxa de falso positivo:</span>
              <span className="font-medium text-gray-900 dark:text-white">1.2%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Erro de classificação:</span>
              <span className="font-medium text-gray-900 dark:text-white">0.8%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Tempo médio de parada:</span>
              <span className="font-medium text-gray-900 dark:text-white">15min/dia</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Custo por peça:</span>
              <span className="font-medium text-gray-900 dark:text-white">R$ 0.42</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Ações do Relatório
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => handleGenerateReport('pdf')}
            disabled={isGenerating}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {isGenerating ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <ArrowDownTrayIcon className="w-5 h-5" />
            )}
            <span>PDF</span>
          </button>

          <button
            onClick={() => handleGenerateReport('csv')}
            disabled={isGenerating}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {isGenerating ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <ArrowDownTrayIcon className="w-5 h-5" />
            )}
            <span>CSV</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <PrinterIcon className="w-5 h-5" />
            <span>Imprimir</span>
          </button>

          <button
            onClick={handleShare}
            className="flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            <ShareIcon className="w-5 h-5" />
            <span>Compartilhar</span>
          </button>
        </div>
      </motion.div>
    </div>
  )
}