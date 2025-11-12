import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConversation } from '@/contexts/ConversationContext';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Message } from '@/types';
import { formatTimestamp } from '@/utils/helpers';
import toast from 'react-hot-toast';

interface ChatInterfaceProps {
  sessionId: string;
  userId?: string;
}

export function ChatInterface({ sessionId, userId }: ChatInterfaceProps) {
  const {
    state,
    addUserMessage,
    setCurrentMessage,
    getCurrentMessages,
    setCurrentSession,
  } = useConversation();

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { sendMessage, isConnected: wsConnected } = useWebSocket(sessionId, userId, {
    autoConnect: true,
    onConnect: () => {
      console.log('✅ Conectado ao WebSocket');
    },
    onDisconnect: () => {
      console.log('🔌 Desconectado do WebSocket');
    },
    onError: (error) => {
      console.error('❌ Erro WebSocket:', error);
    },
  });

  // Auto scroll para última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages[sessionId]]);

  // Definir sessão atual
  useEffect(() => {
    setCurrentSession(sessionId);
  }, [sessionId, setCurrentSession]);

  // Enviar mensagem
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || !wsConnected) {
      if (!wsConnected) {
        toast.error('Conecte-se ao assistente antes de enviar mensagens');
      }
      return;
    }

    const message = inputValue.trim();
    
    try {
      // Adicionar mensagem do usuário
      addUserMessage(message);
      
      // Enviar via WebSocket
      await sendMessage(message);
      
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      toast.error('Erro ao enviar mensagem');
    }
  };

  // Submit com Enter (Shift + Enter para nova linha)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Gerar nova sessão
  const handleNewSession = () => {
    const newSessionId = `session_${Date.now()}`;
    window.location.href = `/chat/${newSessionId}`;
  };

  const currentMessages = getCurrentMessages();

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Assistente IA 3dPot</h2>
            <p className="text-sm text-gray-500">
              Especialista em especificações técnicas
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Status da conexão */}
          <div className={`flex items-center space-x-2 ${wsConnected ? 'text-green-600' : 'text-red-600'}`}>
            {wsConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
            <span className="text-sm">
              {wsConnected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>

          {/* Botão nova sessão */}
          <button
            onClick={handleNewSession}
            className="px-3 py-1.5 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors"
          >
            Nova Sessão
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {currentMessages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4 max-w-md">
              <Bot className="w-16 h-16 text-gray-300 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold text-gray-700">
                  Bem-vindo ao Assistente IA 3dPot
                </h3>
                <p className="text-gray-500 mt-2">
                  Descreva seu projeto de prototipagem 3D e eu vou extrair as especificações técnicas automaticamente.
                </p>
              </div>
              <div className="bg-primary-50 p-4 rounded-lg border border-primary-200">
                <h4 className="font-medium text-primary-800 mb-2">Exemplos do que você pode me contar:</h4>
                <ul className="text-sm text-primary-700 space-y-1 text-left">
                  <li>• "Preciso de uma peça de 100x50x30mm em ABS"</li>
                  <li>• "Quero uma adaptação para Arduino com tolerância de 0.1mm"</li>
                  <li>• "Criar um suporte para sensor de temperatura"</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence>
          {currentMessages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>

        {/* Loading/typing indicator */}
        {state.isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex items-start space-x-3"
          >
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div className="bg-white rounded-lg p-3 shadow-sm border">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Banner */}
      {state.error && (
        <div className="bg-red-50 border-t border-red-200 p-3">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{state.error}</span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={wsConnected ? "Descreva seu projeto de prototipagem..." : "Conectando ao assistente..."}
              disabled={!wsConnected}
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:text-gray-500"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
              }}
            />
          </div>
          
          <button
            type="submit"
            disabled={!inputValue.trim() || !wsConnected || state.isTyping}
            className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {state.isTyping ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        
        {!wsConnected && (
          <p className="text-sm text-red-600 mt-2 flex items-center">
            <WifiOff className="w-4 h-4 mr-1" />
            Não conectado ao assistente IA
          </p>
        )}
      </div>
    </div>
  );
}

// Componente para cada mensagem
function MessageBubble({ message }: { message: Message }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex items-start space-x-3 max-w-[80%] ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          message.isUser 
            ? 'bg-primary-600 text-white' 
            : 'bg-primary-100 text-primary-600'
        }`}>
          {message.isUser ? (
            <User className="w-5 h-5" />
          ) : (
            <Bot className="w-5 h-5" />
          )}
        </div>

        {/* Message Content */}
        <div className="space-y-2">
          <div className={`p-3 rounded-lg ${
            message.isUser 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-900 border border-gray-200'
          }`}>
            <p className="whitespace-pre-wrap">{message.content}</p>
            
            {/* Timestamp */}
            <p className={`text-xs mt-1 ${
              message.isUser ? 'text-primary-200' : 'text-gray-500'
            }`}>
              {formatTimestamp(message.timestamp)}
            </p>
          </div>

          {/* Extracted Specs (only for agent messages) */}
          {!message.isUser && message.extractedSpecs && (
            <SpecsCard specs={message.extractedSpecs} confidence={message.confidence || 0} />
          )}
        </div>
      </div>
    </motion.div>
  );
}

// Componente para exibir especificações extraídas
function SpecsCard({ specs, confidence }: { specs: any, confidence: number }) {
  const confidenceColor = confidence >= 0.7 ? 'text-green-600' : confidence >= 0.4 ? 'text-yellow-600' : 'text-red-600';
  const confidenceBg = confidence >= 0.7 ? 'bg-green-50' : confidence >= 0.4 ? 'bg-yellow-50' : 'bg-red-50';
  
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900">Especificações Extraídas</h4>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${confidenceBg} ${confidenceColor}`}>
          Confiança: {Math.round(confidence * 100)}%
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        {specs.dimensions && Object.keys(specs.dimensions).length > 0 && (
          <div>
            <span className="text-gray-600">Dimensões:</span>
            <p className="font-medium">
              {specs.dimensions.width ? `${specs.dimensions.width}mm` : ''}
              {specs.dimensions.height && specs.dimensions.width ? ` × ${specs.dimensions.height}mm` : specs.dimensions.height ? `${specs.dimensions.height}mm` : ''}
              {specs.dimensions.depth && specs.dimensions.width && specs.dimensions.height ? ` × ${specs.dimensions.depth}mm` : specs.dimensions.depth ? `${specs.dimensions.depth}mm` : ''}
            </p>
          </div>
        )}

        {specs.material && (
          <div>
            <span className="text-gray-600">Material:</span>
            <p className="font-medium">{specs.material}</p>
          </div>
        )}

        {specs.functionality && (
          <div>
            <span className="text-gray-600">Funcionalidade:</span>
            <p className="font-medium">{specs.functionality}</p>
          </div>
        )}

        {specs.complexity && (
          <div>
            <span className="text-gray-600">Complexidade:</span>
            <p className={`font-medium ${
              specs.complexity === 'Alto' ? 'text-red-600' : 
              specs.complexity === 'Médio' ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {specs.complexity}
            </p>
          </div>
        )}
      </div>

      {specs.extractionMethod && (
        <div className="mt-2 pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500">
            Método: {specs.extractionMethod}
          </span>
        </div>
      )}
    </div>
  );
}