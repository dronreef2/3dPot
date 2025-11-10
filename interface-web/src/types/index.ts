// Device types
export type DeviceType = 'filament' | 'conveyor' | 'qc';

export type DeviceStatus = 'online' | 'offline' | 'warning' | 'error';

// Base device interface
export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  lastUpdate: Date;
  ipAddress: string;
  version: string;
}

// Filament Monitor specific data
export interface FilamentData {
  weight: number; // grams
  temperature: number; // celsius
  humidity: number; // percentage
  batteryLevel: number; // percentage
  estimatedTime: number; // hours
  isSleeping: boolean;
  calibrationMode: boolean;
  alertThreshold: {
    min: number;
    max: number;
  };
}

// Conveyor Belt specific data
export interface ConveyorData {
  speed: number; // rpm
  direction: 'forward' | 'reverse' | 'stopped';
  mode: 'manual' | 'automatic';
  isRunning: boolean;
  emergencyStop: boolean;
  position: number; // mm
  load: number; // percentage
  motorTemperature: number; // celsius
  statusLED: 'green' | 'yellow' | 'red' | 'off';
}

// QC Station specific data
export interface QCData {
  lastInspection: {
    id: string;
    timestamp: Date;
    classification: 'A' | 'B' | 'C' | 'D' | 'F';
    confidence: number; // 0-1
    defectType?: string;
    imagePath?: string;
  };
  statistics: {
    totalInspected: number;
    passRate: number; // percentage
    avgConfidence: number;
    commonDefects: string[];
  };
  cameraStatus: 'connected' | 'disconnected' | 'calibrating';
  ledStatus: 'green' | 'yellow' | 'red' | 'off';
}

// Extended device interfaces
export interface FilamentDevice extends Device {
  data: FilamentData;
}

export interface ConveyorDevice extends Device {
  data: ConveyorData;
}

export interface QCDevice extends Device {
  data: QCData;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: Date;
}

export interface DeviceStatusResponse extends ApiResponse<Device> {}

export interface AnalyticsData {
  production: {
    today: number;
    week: number;
    month: number;
    trend: 'up' | 'down' | 'stable';
  };
  quality: {
    passRate: number;
    avgClassification: string;
    topDefects: string[];
  };
  system: {
    uptime: number;
    activeDevices: number;
    totalDevices: number;
  };
}

// Chart data types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
    borderWidth?: number;
  }[];
}

export interface TimeSeriesData {
  timestamp: Date;
  value: number;
  deviceId: string;
}

// Settings and configuration
export interface AppSettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'pt-BR' | 'en-US' | 'es-ES';
  notifications: {
    enabled: boolean;
    sound: boolean;
    vibration: boolean;
  };
  refreshInterval: number; // seconds
  compactMode: boolean;
}

export interface DeviceSettings {
  id: string;
  name: string;
  thresholds: {
    warning: number;
    critical: number;
  };
  alerts: {
    email: boolean;
    push: boolean;
    telegram: boolean;
  };
  automation: {
    enabled: boolean;
    rules: AutomationRule[];
  };
}

export interface AutomationRule {
  id: string;
  name: string;
  trigger: 'threshold' | 'schedule' | 'status';
  conditions: Record<string, any>;
  actions: AutomationAction[];
  enabled: boolean;
}

export interface AutomationAction {
  type: 'email' | 'webhook' | 'device_control' | 'notification';
  parameters: Record<string, any>;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'device_update' | 'alert' | 'command_response' | 'heartbeat';
  deviceId: string;
  timestamp: Date;
  payload: any;
}

export interface AlertMessage {
  id: string;
  deviceId: string;
  deviceName: string;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}