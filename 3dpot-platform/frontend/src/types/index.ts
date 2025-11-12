// Tipos gerais da aplicação
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  createdAt: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
}

// Tipos para WebSocket
export interface WebSocketConnection {
  id: string;
  isConnected: boolean;
  lastPing: string | null;
  error: string | null;
}

// Tipos para UI
export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

// Tipos para formulário
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select';
  value: string;
  placeholder?: string;
  required?: boolean;
  validation?: string[];
}

export interface FormState {
  fields: Record<string, FormField>;
  isValid: boolean;
  errors: Record<string, string>;
}