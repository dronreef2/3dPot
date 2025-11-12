import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import type { 
  Device, 
  FilamentDevice, 
  ConveyorDevice, 
  QCDevice, 
  DeviceStatus,
  AlertMessage 
} from '../types'
import { mockDevices, mockAlerts, generateRandomUpdate, generateRandomAlert } from '../data/mockData'

interface DeviceState {
  devices: {
    filament?: FilamentDevice
    conveyor?: ConveyorDevice
    qc?: QCDevice
  }
  alerts: AlertMessage[]
  isLoading: boolean
  error: string | null
}

type DeviceAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_DEVICE'; payload: { type: 'filament' | 'conveyor' | 'qc'; device: any } }
  | { type: 'ADD_ALERT'; payload: AlertMessage }
  | { type: 'ACKNOWLEDGE_ALERT'; payload: string }
  | { type: 'CLEAR_ALERTS' }
  | { type: 'SET_DEVICES'; payload: DeviceState['devices'] }

interface DeviceContextType {
  state: DeviceState
  dispatch: React.Dispatch<DeviceAction>
  refreshDevices: () => Promise<void>
  acknowledgeAlert: (alertId: string) => void
  getDeviceStatus: (type: 'filament' | 'conveyor' | 'qc') => DeviceStatus
  isAnyDeviceOnline: () => boolean
}

const DeviceContext = createContext<DeviceContextType | undefined>(undefined)

const initialState: DeviceState = {
  devices: {
    filament: mockDevices.filament,
    conveyor: mockDevices.conveyor,
    qc: mockDevices.qc
  },
  alerts: mockAlerts,
  isLoading: false,
  error: null,
}

function deviceReducer(state: DeviceState, action: DeviceAction): DeviceState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false }
    
    case 'UPDATE_DEVICE':
      return {
        ...state,
        devices: {
          ...state.devices,
          [action.payload.type]: action.payload.device
        }
      }
    
    case 'ADD_ALERT':
      return {
        ...state,
        alerts: [action.payload, ...state.alerts].slice(0, 50) // Keep only last 50 alerts
      }
    
    case 'ACKNOWLEDGE_ALERT':
      return {
        ...state,
        alerts: state.alerts.map(alert =>
          alert.id === action.payload ? { ...alert, acknowledged: true } : alert
        )
      }
    
    case 'CLEAR_ALERTS':
      return { ...state, alerts: [] }
    
    case 'SET_DEVICES':
      return { ...state, devices: action.payload, isLoading: false }
    
    default:
      return state
  }
}

export function DeviceProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(deviceReducer, initialState)

  const refreshDevices = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Generate updated mock data with random variations
      const updatedDevices = {
        filament: generateRandomUpdate(mockDevices.filament),
        conveyor: generateRandomUpdate(mockDevices.conveyor),
        qc: generateRandomUpdate(mockDevices.qc)
      }
      
      dispatch({ type: 'SET_DEVICES', payload: updatedDevices })
      
      // Randomly generate new alerts
      const newAlert = generateRandomAlert()
      if (newAlert) {
        dispatch({ type: 'ADD_ALERT', payload: newAlert })
      }
      
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' })
    }
  }

  const acknowledgeAlert = (alertId: string) => {
    dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: alertId })
  }

  const getDeviceStatus = (type: 'filament' | 'conveyor' | 'qc'): DeviceStatus => {
    const device = state.devices[type]
    return device?.status || 'offline'
  }

  const isAnyDeviceOnline = (): boolean => {
    return Object.values(state.devices).some(device => device?.status === 'online')
  }

  // Initialize devices on mount
  useEffect(() => {
    refreshDevices()
    
    // Set up polling for device updates
    const interval = setInterval(refreshDevices, 30000) // Every 30 seconds
    return () => clearInterval(interval)
  }, [])

  // Set up real-time updates via WebSocket
  useEffect(() => {
    const handleDeviceUpdate = (update: any) => {
      dispatch({ 
        type: 'UPDATE_DEVICE', 
        payload: { 
          type: update.deviceType, 
          device: update.deviceData 
        } 
      })
    }

    const handleAlert = (alert: AlertMessage) => {
      dispatch({ type: 'ADD_ALERT', payload: alert })
    }

    // This would be set up by the WebSocket hook
    window.addEventListener('device_update', handleDeviceUpdate)
    window.addEventListener('alert', handleAlert)

    return () => {
      window.removeEventListener('device_update', handleDeviceUpdate)
      window.removeEventListener('alert', handleAlert)
    }
  }, [])

  const value: DeviceContextType = {
    state,
    dispatch,
    refreshDevices,
    acknowledgeAlert,
    getDeviceStatus,
    isAnyDeviceOnline,
  }

  return (
    <DeviceContext.Provider value={value}>
      {children}
    </DeviceContext.Provider>
  )
}

export function useDevice() {
  const context = useContext(DeviceContext)
  if (context === undefined) {
    throw new Error('useDevice must be used within a DeviceProvider')
  }
  return context
}