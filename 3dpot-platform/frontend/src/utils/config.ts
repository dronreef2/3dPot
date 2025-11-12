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

  // Sprint 6+ Endpoints
  
  // 3D Printing
  PRINTING: {
    BASE: '/api/printing',
    PRINTERS: '/printers',
    MATERIALS: '/materials',
    JOBS: '/jobs',
    QUEUE: '/queue',
    STATUS: (jobId: string) => `/jobs/${jobId}/status`,
    CANCEL: (jobId: string) => `/jobs/${jobId}/cancel`,
    SLICE: '/slice',
    GENERATE_GCODE: '/generate-gcode',
    CALIBRATE: (printerId: string) => `/printers/${printerId}/calibrate`,
    PRINTER_STATUS: (printerId: string) => `/printers/${printerId}/status`,
    ESTIMATE_TIME: '/estimate-time',
    ESTIMATE_MATERIAL: '/estimate-material',
    ANALYZE_PRINTABILITY: '/analyze-printability',
    DETECT_ISSUES: (jobId: string) => `/jobs/${jobId}/issues`,
    GENERATE_SUPPORTS: '/generate-supports',
    OPTIMIZE_SUPPORTS: '/optimize-supports',
    REORDER_QUEUE: '/queue/reorder',
    CLOUD_SUBMIT: '/cloud/submit',
    CLOUD_TRACK: (cloudJobId: string) => `/cloud/jobs/${cloudJobId}`,
    STATISTICS: (userId: string) => `/statistics/${userId}`,
    FAILURE_ANALYSIS: (jobId: string) => `/jobs/${jobId}/failure-analysis`,
    UPLOAD: '/upload',
    DOWNLOAD_GCODE: (jobId: string) => `/jobs/${jobId}/gcode`,
    DOWNLOAD_PREVIEW: (jobId: string) => `/jobs/${jobId}/preview',
    HARDWARE_CONNECT: '/hardware/connect',
    HARDWARE_DISCONNECT: '/hardware/disconnect',
    HARDWARE_STATUS: (printerId: string) => `/hardware/status/${printerId}`,
  },

  // Collaboration
  COLLABORATION: {
    BASE: '/api/collaboration',
    SESSIONS: '/sessions',
    PARTICIPANTS: (sessionId: string) => `/sessions/${sessionId}/participants`,
    MESSAGES: (sessionId: string) => `/sessions/${sessionId}/messages`,
    ANNOTATIONS: (sessionId: string) => `/sessions/${sessionId}/annotations`,
    VIDEO_CALL: (sessionId: string) => `/sessions/${sessionId}/video`,
    SCREEN_SHARE: (sessionId: string) => `/sessions/${sessionId}/screen-share`,
    RECORDING: (sessionId: string) => `/sessions/${sessionId}/recording`,
    PERMISSIONS: (sessionId: string) => `/sessions/${sessionId}/permissions`,
    INVITATIONS: (sessionId: string) => `/sessions/${sessionId}/invitations`,
    CURSOR: (sessionId: string) => `/sessions/${sessionId}/cursor`,
    ACTIVITY: (sessionId: string) => `/sessions/${sessionId}/activity`,
    WS: (sessionId: string) => `/ws/${sessionId}`,
  },

  // Marketplace
  MARKETPLACE: {
    BASE: '/api/marketplace',
    LISTINGS: '/listings',
    SEARCH: '/search',
    TRANSACTIONS: '/transactions',
    PAYMENTS_INTENT: '/payments/intent',
    WEBHOOKS_STRIPE: '/webhooks/stripe',
    REVIEWS: '/reviews',
    WISHLIST: '/wishlist',
    SELLER_PROFILE: '/seller-profile',
    CATEGORIES: '/categories',
    TAGS: '/tags',
    PROMOTIONS: '/promotions',
    LISTING: (id: string) => `/listings/${id}`,
    TRANSACTION: (id: string) => `/transactions/${id}`,
    REVIEW: (id: string) => `/reviews/${id}`,
  },

  // Cloud Rendering
  CLOUD_RENDERING: {
    BASE: '/api/rendering',
    CLUSTERS: '/clusters',
    JOBS: '/jobs',
    PRESETS: '/presets',
    BATCH_JOBS: '/batch-jobs',
    ESTIMATES: '/estimates',
    CLUSTER: (id: string) => `/clusters/${id}`,
    JOB: (id: string) => `/jobs/${id}`,
    JOB_STATUS: (id: string) => `/jobs/${id}/status`,
    JOB_CANCEL: (id: string) => `/jobs/${id}/cancel`,
    BATCH_JOB: (id: string) => `/batch-jobs/${id}`,
    MONITOR: (id: string) => `/monitor/${id}`,
  },

  // Legacy Endpoints (Sprints 1-5)
  MODELS: '/models',
  MODEL: (modelId: string) => `/models/${modelId}`,

  BUDGETS: '/budgets',
  GENERATE_BUDGET: '/budgets/generate',

  HARDWARE: '/hardware',
  HARDWARE_STATUS: '/hardware/status',

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