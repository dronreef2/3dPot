import { io, Socket } from 'socket.io-client';
import { Message, ConversationResponse } from '@/types';
import { getWebSocketUrl } from '@/utils/config';

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
}