import { useRef, useEffect } from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { useDevice } from '../contexts/DeviceContext'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export function QCChart() {
  const chartRef = useRef<any>(null)
  const { state: deviceState } = useDevice()
  
  const qcDevice = deviceState.devices.qc
  
  // Generate mock quality data
  const generateQualityData = () => {
    const classifications = ['A', 'B', 'C', 'D', 'F']
    const colors = [
      'rgb(34, 197, 94)', // A - Green
      'rgb(59, 130, 246)', // B - Blue  
      'rgb(245, 158, 11)', // C - Yellow
      'rgb(249, 115, 22)', // D - Orange
      'rgb(239, 68, 68)', // F - Red
    ]
    
    const data = classifications.map((_, index) => {
      // Simulate different distribution
      const baseValue = qcDevice?.data?.statistics.passRate || 80
      if (index === 0) return baseValue * 0.6 // A grade - 60% of passes
      if (index === 1) return baseValue * 0.25 // B grade - 25% of passes
      if (index === 2) return baseValue * 0.1 // C grade - 10% of passes
      if (index === 3) return baseValue * 0.04 // D grade - 4% of passes
      return baseValue * 0.01 // F grade - 1% of fails
    })
    
    return {
      labels: classifications,
      datasets: [
        {
          label: 'Peças por Classificação',
          data: data,
          backgroundColor: colors.map(color => color.replace('rgb', 'rgba').replace(')', ', 0.8)')),
          borderColor: colors,
          borderWidth: 1,
        }
      ]
    }
  }

  const data = generateQualityData()

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          title: (context: any) => {
            const grade = context[0].label
            return `Classificação ${grade}`
          },
          label: (context: any) => {
            return `Peças: ${context.parsed.y.toFixed(0)}`
          },
          afterLabel: (context: any) => {
            const total = data.datasets[0].data.reduce((a: number, b: number) => a + b, 0)
            const percentage = ((context.parsed.y / total) * 100).toFixed(1)
            return `Porcentagem: ${percentage}%`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
          callback: function(value: any) {
            return value + ' peças'
          }
        }
      }
    },
  }

  // Update options for dark mode
  useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark')
    if (isDark) {
      options.scales.x.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)'
    }
  }, [])

  return (
    <div className="relative h-64">
      <Bar 
        ref={chartRef}
        data={data} 
        options={options}
      />
      
      {!qcDevice && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 bg-opacity-75">
          <div className="text-center">
            <div className="text-gray-400 dark:text-gray-600 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Conecte a estação QC para ver análise de qualidade
            </p>
          </div>
        </div>
      )}
    </div>
  )
}