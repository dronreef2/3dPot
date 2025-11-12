// Tipos para conversação e chat
export interface Message {
  id: string;
  content: string;
  timestamp: string;
  isUser: boolean;
  sessionId: string;
  extractedSpecs?: ExtractedSpecs;
  confidence?: number;
}

export interface ExtractedSpecs {
  dimensions?: {
    width?: number;
    height?: number;
    depth?: number;
  };
  material?: string;
  functionality?: string;
  complexity?: 'Baixo' | 'Médio' | 'Alto';
  rawText?: string;
  extractionMethod?: string;
}

export interface ConversationResponse {
  response: string;
  extractedSpecs: ExtractedSpecs;
  confidence: number;
  timestamp: string;
  fallback?: boolean;
}

export interface ConversationSession {
  sessionId: string;
  title: string;
  status: 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastConfidence?: number;
}

export interface WebSocketMessage {
  type: 'user_message' | 'agent_response' | 'typing' | 'error' | 'connection_established';
  data: any;
  timestamp: string;
  sessionId?: string;
}