import { useRef, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import type { ChartData } from '@types'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface ProductionChartProps {
  data: ChartData
  height?: number
}

export function ProductionChart({ data, height = 300 }: ProductionChartProps) {
  const chartRef = useRef<any>(null)

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            family: 'Inter, system-ui, sans-serif'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          title: (context: any) => {
            return `Horário: ${context[0].label}`
          },
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y
            return `${label}: ${value.toFixed(1)}`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: true,
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          maxTicksLimit: 8,
          color: 'rgba(156, 163, 175, 0.8)',
          font: {
            size: 11
          }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
          font: {
            size: 11
          }
        }
      }
    },
    elements: {
      point: {
        radius: 3,
        hoverRadius: 6,
      },
      line: {
        tension: 0.4,
        borderWidth: 2,
      }
    },
    animation: {
      duration: 750,
      easing: 'easeInOutQuart' as const,
    }
  }

  // Update options for dark mode
  useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark')
    if (isDark) {
      options.scales.x.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.x.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.scales.y.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)'
      options.plugins.tooltip.titleColor = 'white'
      options.plugins.tooltip.bodyColor = 'white'
    }
  }, [])

  // Dynamic chart data with gradient fills
  const chartData = {
    ...data,
    datasets: data.datasets.map((dataset, index) => ({
      ...dataset,
      fill: true,
      backgroundColor: index === 0 
        ? 'rgba(59, 130, 246, 0.1)' 
        : 'rgba(34, 197, 94, 0.1)',
      borderColor: index === 0 
        ? 'rgb(59, 130, 246)' 
        : 'rgb(34, 197, 94)',
      pointBackgroundColor: index === 0 
        ? 'rgb(59, 130, 246)' 
        : 'rgb(34, 197, 94)',
      pointBorderColor: 'white',
      pointBorderWidth: 2,
      pointHoverBackgroundColor: index === 0 
        ? 'rgb(37, 99, 235)' 
        : 'rgb(22, 163, 74)',
      pointHoverBorderColor: 'white',
      pointHoverBorderWidth: 3,
    }))
  }

  return (
    <div className="relative" style={{ height: `${height}px` }}>
      <Line 
        ref={chartRef}
        data={chartData} 
        options={options}
      />
      
      {/* Loading overlay */}
      {!data.labels.length && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 bg-opacity-75">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Carregando dados...</p>
          </div>
        </div>
      )}
    </div>
  )
}