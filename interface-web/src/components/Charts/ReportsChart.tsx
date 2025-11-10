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

interface ReportsChartProps {
  period: 'day' | 'week' | 'month'
}

export function ReportsChart({ period }: ReportsChartProps) {
  const chartRef = useRef<any>(null)

  // Generate data based on period
  const generateData = () => {
    let labels: string[] = []
    let productionData: number[] = []
    let qualityData: number[] = []
    let efficiencyData: number[] = []

    if (period === 'day') {
      // Hourly data for today
      labels = Array.from({ length: 24 }, (_, i) => `${i}:00`)
      productionData = labels.map(() => Math.floor(Math.random() * 10) + 2)
      qualityData = labels.map(() => Math.random() * 15 + 85) // 85-100%
      efficiencyData = labels.map(() => Math.random() * 25 + 70) // 70-95%
    } else if (period === 'week') {
      // Daily data for this week
      const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
      labels = days
      productionData = days.map(() => Math.floor(Math.random() * 50) + 20)
      qualityData = days.map(() => Math.random() * 10 + 88)
      efficiencyData = days.map(() => Math.random() * 20 + 75)
    } else {
      // Weekly data for this month
      const weeks = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
      labels = weeks
      productionData = weeks.map(() => Math.floor(Math.random() * 200) + 100)
      qualityData = weeks.map(() => Math.random() * 8 + 90)
      efficiencyData = weeks.map(() => Math.random() * 15 + 80)
    }

    return {
      labels,
      datasets: [
        {
          label: 'Produção (peças)',
          data: productionData,
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          yAxisID: 'y',
        },
        {
          label: 'Qualidade (%)',
          data: qualityData,
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderColor: 'rgb(34, 197, 94)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          yAxisID: 'y1',
        },
        {
          label: 'Eficiência (%)',
          data: efficiencyData,
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

  const data = generateData()

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
        callbacks: {
          title: (context: any) => {
            return `${context[0].label}`
          },
          label: (context: any) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y
            if (label.includes('Produção')) {
              return `${label}: ${value.toFixed(0)} peças`
            } else {
              return `${label}: ${value.toFixed(1)}%`
            }
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Produção (peças)'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Percentual (%)'
        },
        grid: {
          drawOnChartArea: false,
        },
        min: 0,
        max: 100,
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
          callback: function(value: any) {
            return value + '%'
          }
        }
      },
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
  }

  // Update options for dark mode
  useEffect(() => {
    const isDark = document.documentElement.classList.contains('dark')
    if (isDark) {
      options.scales.x.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.scales.y.grid.color = 'rgba(75, 85, 99, 0.3)'
      options.scales.x.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y.ticks.color = 'rgba(156, 163, 175, 0.8)'
      options.scales.y1.ticks.color = 'rgba(156, 163, 175, 0.8)'
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
    </div>
  )
}