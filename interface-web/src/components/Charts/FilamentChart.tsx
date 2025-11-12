import { useRef, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import { useDevice } from '../contexts/DeviceContext'

export function FilamentChart() {
  const chartRef = useRef<any>(null)
  const { state: deviceState } = useDevice()
  
  const filamentDevice = deviceState.devices.filament
  
  // Generate mock historical data
  const generateHistoricalData = () => {
    const hours = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date()
      hour.setHours(hour.getHours() - (23 - i))
      return hour.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    })
    
    const weightData = hours.map((_, index) => {
      // Simulate decreasing weight over time
      const baseWeight = filamentDevice?.data?.weight || 500
      const decrease = index * 2 + Math.random() * 5
      return Math.max(0, baseWeight - decrease)
    })
    
    const temperatureData = hours.map(() => {
      const baseTemp = filamentDevice?.data?.temperature || 25
      return baseTemp + (Math.random() - 0.5) * 5
    })
    
    return {
      labels: hours,
      datasets: [
        {
          label: 'Peso (g)',
          data: weightData,
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Temperatura (°C)',
          data: temperatureData,
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          borderColor: 'rgb(245, 158, 11)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          yAxisID: 'y1',
        }
      ]
    }
  }

  const data = generateHistoricalData()

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Tempo'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Peso (g)'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Temperatura (°C)'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  }

  // Update options for dark mode
  useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark')
    if (isDark) {
      options.scales.x.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.scales.y.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.scales.x.title.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y.title.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y1.title.color = 'rgba(156, 163, 175, 0.8)'
      options.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)'
    }
  }, [])

  return (
    <div className="relative h-80">
      <Line 
        ref={chartRef}
        data={data} 
        options={options}
      />
      
      {!filamentDevice && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 bg-opacity-75">
          <div className="text-center">
            <div className="text-gray-400 dark:text-gray-600 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Conecte o monitor ESP32 para ver o histórico
            </p>
          </div>
        </div>
      )}
    </div>
  )
}