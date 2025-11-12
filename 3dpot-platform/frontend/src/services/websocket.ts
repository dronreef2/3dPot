import { io, Socket } from 'socket.io-client';
import { Message, ConversationResponse } from '@/types';
import { getWebSocketUrl, API_ENDPOINTS } from '@/utils/config';

export interface CollaborationWebSocketEvent {
  type: 'participant_joined' | 'participant_left' | 'cursor_move' | 'model_selection' | 'model_edit' | 'annotation_added' | 'message_sent' | 'video_call_started' | 'screen_share_started';
  data: any;
  userId: string;
  timestamp: Date;
}

export class ConversationWebSocket {
  private socket: Socket | null = null;
  private sessionId: string | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor() {
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
  }

  /**
   * Conecta ao WebSocket para uma sessão específica
   */
  async connect(sessionId: string, userId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.sessionId = sessionId;
        this.userId = userId || 'anonymous';

        const wsUrl = getWebSocketUrl();
        
        this.socket = io(wsUrl, {
          transports: ['websocket'],
          timeout: 10000,
          forceNew: true,
        });

        this.socket.on('connect', () => {
          console.log('✅ WebSocket conectado:', this.socket?.id);
          this.reconnectAttempts = 0;
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ Erro na conexão WebSocket:', error);
          this.reconnectAttempts++;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject(new Error(`Falha ao conectar após ${this.maxReconnectAttempts} tentativas`));
          }
        });

        this.socket.on('disconnect', (reason) => {
          console.log('🔌 WebSocket desconectado:', reason);
        });

        this.socket.on('error', (error) => {
          console.error('❌ Erro WebSocket:', error);
        });

      } catch (error) {
        console.error('❌ Erro ao criar WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Desconecta do WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.sessionId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Envia mensagem para o agente IA
   */
  async sendMessage(message: string): Promise<void> {
    if (!this.socket || !this.socket.connected) {
      throw new Error('WebSocket não está conectado');
    }

    const messageData = {
      message,
      session_id: this.sessionId,
      user_id: this.userId
    };

    this.socket.emit('user_message', messageData);
  }

  /**
   * Registra listener para mensagens do agente
   */
  onAgentResponse(callback: (response: ConversationResponse) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    this.socket.on('agent_response', callback);

    // Retorna função para remover o listener
    return () => {
      this.socket?.off('agent_response', callback);
    };
  }

  /**
   * Registra listener para eventos de conexão
   */
  onConnectionEvent(callback: (event: string, data?: any) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    const handlers = {
      connect: () => callback('connect'),
      disconnect: (reason: string) => callback('disconnect', { reason }),
      connect_error: (error: Error) => callback('connect_error', { error }),
      error: (error: Error) => callback('error', { error })
    };

    // Registrar listeners
    Object.entries(handlers).forEach(([event, handler]) => {
      this.socket!.on(event, handler);
    });

    // Retorna função para remover todos os listeners
    return () => {
      Object.entries(handlers).forEach(([event, handler]) => {
        this.socket?.off(event, handler);
      });
    };
  }

  /**
   * Registra listener para erros
   */
  onError(callback: (error: string) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    this.socket.on('error', callback);

    return () => {
      this.socket?.off('error', callback);
    };
  }

  /**
   * Registra listener para eventos de digitação
   */
  onTyping(callback: (isTyping: boolean) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    this.socket.on('typing', callback);

    return () => {
      this.socket?.off('typing', callback);
    };
  }

  /**
   * Verifica se está conectado
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Obtém status da conexão
   */
  getConnectionStatus(): 'connected' | 'connecting' | 'disconnected' {
    if (!this.socket) return 'disconnected';
    if (this.socket.connected) return 'connected';
    return 'connecting';
  }

  // ===== SPRINT 6+ COLLABORATION METHODS =====

  /**
   * Conecta ao WebSocket de colaboração para uma sessão específica
   */
  async connectToCollaboration(sessionId: string, userId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.sessionId = sessionId;
        this.userId = userId || 'anonymous';

        const wsUrl = `${getWebSocketUrl()}${API_ENDPOINTS.COLLABORATION.WS(sessionId)}`;
        
        this.socket = io(wsUrl, {
          transports: ['websocket'],
          timeout: 15000,
          forceNew: true,
          query: {
            sessionId,
            userId: this.userId
          }
        });

        this.setupCollaborationHandlers(resolve, reject);
      } catch (error) {
        console.error('❌ Erro ao criar WebSocket de colaboração:', error);
        reject(error);
      }
    });
  }

  /**
   * Conecta ao WebSocket de impressão 3D para monitoramento em tempo real
   */
  async connectToPrinting(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${getWebSocketUrl()}${API_ENDPOINTS.PRINTING.BASE}/ws`;
        
        this.socket = io(wsUrl, {
          transports: ['websocket'],
          timeout: 10000,
          forceNew: true
        });

        this.setupPrintingHandlers(resolve, reject);
      } catch (error) {
        console.error('❌ Erro ao criar WebSocket de impressão:', error);
        reject(error);
      }
    });
  }

  private setupCollaborationHandlers(resolve: () => void, reject: (error: Error) => void) {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✅ WebSocket de colaboração conectado');
      this.reconnectAttempts = 0;
      resolve();
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ Erro na conexão WebSocket de colaboração:', error);
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        reject(new Error(`Falha ao conectar após ${this.maxReconnectAttempts} tentativas`));
      }
    });

    // Collaboration-specific events
    this.socket.on('participant_joined', (data) => {
      console.log('👤 Participante entrou na sessão:', data);
    });

    this.socket.on('participant_left', (data) => {
      console.log('👤 Participante saiu da sessão:', data);
    });

    this.socket.on('cursor_move', (data) => {
      console.log('🖱️ Cursor movido:', data);
    });

    this.socket.on('model_selection', (data) => {
      console.log('🎯 Modelo selecionado:', data);
    });

    this.socket.on('model_edit', (data) => {
      console.log('✏️ Modelo editado:', data);
    });

    this.socket.on('annotation_added', (data) => {
      console.log('💬 Anotação adicionada:', data);
    });

    this.socket.on('video_call_started', (data) => {
      console.log('📹 Chamada de vídeo iniciada:', data);
    });

    this.socket.on('screen_share_started', (data) => {
      console.log('🖥️ Compartilhamento de tela iniciado:', data);
    });
  }

  private setupPrintingHandlers(resolve: () => void, reject: (error: Error) => void) {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✅ WebSocket de impressão conectado');
      this.reconnectAttempts = 0;
      resolve();
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ Erro na conexão WebSocket de impressão:', error);
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        reject(new Error(`Falha ao conectar após ${this.maxReconnectAttempts} tentativas`));
      }
    });

    // Printing-specific events
    this.socket.on('job_update', (data) => {
      console.log('🖨️ Atualização do job:', data);
    });

    this.socket.on('printer_status', (data) => {
      console.log('📊 Status da impressora:', data);
    });

    this.socket.on('queue_update', (data) => {
      console.log('📋 Atualização da fila:', data);
    });

    this.socket.on('slice_progress', (data) => {
      console.log('🔪 Progresso do slicing:', data);
    });

    this.socket.on('print_progress', (data) => {
      console.log('🖨️ Progresso da impressão:', data);
    });
  }

  /**
   * Envia evento de colaboração
   */
  sendCollaborationEvent(event: Omit<CollaborationWebSocketEvent, 'userId' | 'timestamp'>): void {
    if (!this.socket || !this.socket.connected) {
      throw new Error('WebSocket não está conectado');
    }

    const eventData = {
      ...event,
      userId: this.userId,
      timestamp: new Date().toISOString()
    };

    this.socket.emit(event.type, eventData);
  }

  /**
   * Registra listener para eventos de colaboração
   */
  onCollaborationEvent(callback: (event: CollaborationWebSocketEvent) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    const events: Array<CollaborationWebSocketEvent['type']> = [
      'participant_joined',
      'participant_left', 
      'cursor_move',
      'model_selection',
      'model_edit',
      'annotation_added',
      'message_sent',
      'video_call_started',
      'screen_share_started'
    ];

    const handlers = events.map(eventType => {
      const handler = (data: any) => {
        callback({
          type: eventType,
          data,
          userId: data.userId || 'unknown',
          timestamp: new Date()
        });
      };
      this.socket!.on(eventType, handler);
      return { eventType, handler };
    });

    // Retorna função para remover todos os listeners
    return () => {
      handlers.forEach(({ eventType, handler }) => {
        this.socket?.off(eventType, handler);
      });
    };
  }

  /**
   * Registra listener para eventos de impressão 3D
   */
  onPrintingEvent(callback: (event: any) => void): () => void {
    if (!this.socket) {
      throw new Error('WebSocket não está conectado');
    }

    const events = ['job_update', 'printer_status', 'queue_update', 'slice_progress', 'print_progress'];
    
    const handlers = events.map(eventType => {
      const handler = (data: any) => callback({ type: eventType, data });
      this.socket!.on(eventType, handler);
      return { eventType, handler };
    });

    return () => {
      handlers.forEach(({ eventType, handler }) => {
        this.socket?.off(eventType, handler);
      });
    };
  }
}
}