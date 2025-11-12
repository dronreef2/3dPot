import { useEffect, useRef, useCallback } from 'react';
import { ConversationWebSocket } from '@/services/websocket';
import { useConversation } from '@/contexts/ConversationContext';
import { ConversationResponse } from '@/types';
import toast from 'react-hot-toast';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: (reason: string) => void;
  onError?: (error: string) => void;
}

export function useWebSocket(sessionId: string, userId?: string, options: UseWebSocketOptions = {}) {
  const { autoConnect = false } = options;
  const wsRef = useRef<ConversationWebSocket | null>(null);
  const { 
    addAgentResponse, 
    setConnectionStatus, 
    setTyping, 
    setError,
    setLoading 
  } = useConversation();

  // Inicializar WebSocket
  const connect = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      
      const ws = new ConversationWebSocket();
      await ws.connect(sessionId, userId);
      
      wsRef.current = ws;
      setConnectionStatus(true);
      
      // Registrar event listeners
      const removeConnectionListeners = ws.onConnectionEvent((event, data) => {
        switch (event) {
          case 'connect':
            toast.success('Conectado ao assistente IA');
            options.onConnect?.();
            break;
          case 'disconnect':
            toast('Desconectado do assistente', { icon: '⚠️' });
            setConnectionStatus(false);
            options.onDisconnect?.(data?.reason || 'Unknown');
            break;
          case 'connect_error':
            toast.error('Erro ao conectar com o assistente');
            setConnectionStatus(false);
            options.onError?.(data?.error?.message || 'Connection error');
            break;
          case 'error':
            toast.error('Erro na comunicação');
            options.onError?.(data?.error?.message || 'WebSocket error');
            break;
        }
      });

      // Listener para mensagens do agente
      const removeAgentListener = ws.onAgentResponse((response: ConversationResponse) => {
        addAgentResponse(sessionId, response);
      });

      // Listener para status de digitação
      const removeTypingListener = ws.onTyping((isTyping: boolean) => {
        setTyping(isTyping);
      });

      // Listener para erros específicos
      const removeErrorListener = ws.onError((error: string) => {
        toast.error(`Erro: ${error}`);
        setError(error);
      });

      setLoading(false);

      // Cleanup function
      return () => {
        removeConnectionListeners();
        removeAgentListener();
        removeTypingListener();
        removeErrorListener();
      };

    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
      setError(error instanceof Error ? error.message : 'Erro de conexão');
      setLoading(false);
      setConnectionStatus(false);
    }
  }, [sessionId, userId, setConnectionStatus, setTyping, setError, setLoading, addAgentResponse]);

  // Desconectar
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
      setConnectionStatus(false);
    }
  }, [setConnectionStatus]);

  // Enviar mensagem
  const sendMessage = useCallback(async (message: string) => {
    if (!wsRef.current) {
      throw new Error('WebSocket não está conectado');
    }

    try {
      setLoading(true);
      await wsRef.current.sendMessage(message);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setError(error instanceof Error ? error.message : 'Erro ao enviar mensagem');
      setLoading(false);
    }
  }, [setLoading, setError]);

  // Verificar conexão
  const isConnected = useCallback(() => {
    return wsRef.current?.isConnected() || false;
  }, []);

  // Auto-connect quando configurado
  useEffect(() => {
    let cleanup: (() => void) | undefined;

    if (autoConnect && sessionId) {
      connect().then((cleanupFn) => {
        cleanup = cleanupFn;
      });
    }

    return () => {
      if (cleanup) {
        cleanup();
      }
      disconnect();
    };
  }, [autoConnect, sessionId, connect, disconnect]);

  return {
    connect,
    disconnect,
    sendMessage,
    isConnected,
    isConnected: wsRef.current?.isConnected() || false,
  };
}