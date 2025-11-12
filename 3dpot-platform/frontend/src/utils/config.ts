// Configurações de URLs da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function getApiBaseUrl(): string {
  // Em desenvolvimento, usar proxy configurado no vite.config.ts
  if (import.meta.env.DEV) {
    return '/api';
  }
  
  // Em produção, usar URL completa
  return `${API_BASE_URL}/api`;
}

export function getWebSocketUrl(): string {
  // Em desenvolvimento, usar proxy configurado no vite.config.ts
  if (import.meta.env.DEV) {
    return '/ws';
  }
  
  // Em produção, usar URL completa
  return `${WS_BASE_URL}/ws`;
}

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/auth/login',
  REGISTER: '/auth/register', 
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',

  // Conversations
  CONVERSATIONS: '/conversations',
  SESSIONS: '/conversations/sessions',
  SESSION_MESSAGES: (sessionId: string) => `/conversations/sessions/${sessionId}/messages`,

  // WebSocket
  WS_CONVERSATION: (sessionId: string) => `/ws/conversation/${sessionId}`,

  // Models
  MODELS: '/models',
  MODEL: (modelId: string) => `/models/${modelId}`,

  // Budgets
  BUDGETS: '/budgets',
  GENERATE_BUDGET: '/budgets/generate',

  // Hardware
  HARDWARE: '/hardware',
  HARDWARE_STATUS: '/hardware/status',

  // Health
  HEALTH: '/health',
};

export const WEBSOCKET_EVENTS = {
  USER_MESSAGE: 'user_message',
  AGENT_RESPONSE: 'agent_response',
  TYPING: 'typing',
  ERROR: 'error',
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  CONNECT_ERROR: 'connect_error',
};

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

export const VALIDATION_RULES = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 6,
  SESSION_ID: /^[a-zA-Z0-9_-]+$/,
};