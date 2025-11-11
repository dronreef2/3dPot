import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, MessageCircle, Sparkles, HelpCircle } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { apiClient, ConversationalRequest, ConversationalResponse } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  clarifications?: string[];
  extractedSpecs?: Record<string, any>;
}

interface ConversationalInterfaceProps {
  projectId: string;
  conversationId?: string;
  onSpecificationsExtracted?: (specs: Record<string, any>) => void;
}

export const ConversationalInterface: React.FC<ConversationalInterfaceProps> = ({
  projectId,
  conversationId,
  onSpecificationsExtracted,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(conversationId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuthStore();

  // Start conversation if needed
  const startConversationMutation = useMutation({
    mutationFn: () => apiClient.startConversation(projectId),
    onSuccess: (data) => {
      setCurrentConversationId(data.id);
      // Add welcome message
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: `Olá ${user?.fullName || user?.username}! Sou seu assistente de prototipagem. Por favor, descreva o projeto que você gostaria de criar em detalhes. ${projectId ? 'Vou ajudá-lo a extrair as especificações técnicas e gerar um modelo 3D automatizado.' : ''}`,
        timestamp: new Date(),
      }]);
    },
    onError: () => {
      toast.error('Erro ao iniciar conversa');
    },
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!currentConversationId) {
        const newConv = await apiClient.startConversation(projectId);
        setCurrentConversationId(newConv.id);
      }

      const request: ConversationalRequest = {
        message,
        conversationId: currentConversationId,
        projectId,
      };

      return apiClient.sendMessage(request);
    },
    onMutate: () => {
      setIsTyping(true);
    },
    onSuccess: (data: ConversationalResponse) => {
      // Add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: inputMessage,
        timestamp: new Date(),
      };

      // Add assistant response
      const assistantMessage: Message = {
        id: data.messageId,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        clarifications: data.clarificationsNeeded,
        extractedSpecs: data.extractedSpecs,
      };

      setMessages(prev => [...prev, userMessage, assistantMessage]);
      setInputMessage('');

      // Notify parent component about extracted specifications
      if (onSpecificationsExtracted && Object.keys(data.extractedSpecs).length > 0) {
        onSpecificationsExtracted(data.extractedSpecs);
      }

      // Show helpful tips for clarifications
      if (data.clarificationsNeeded.length > 0) {
        setTimeout(() => {
          toast.success('Especificações coletadas! Continue descriminando para mais detalhes.');
        }, 2000);
      }
    },
    onError: () => {
      toast.error('Erro ao enviar mensagem');
      setIsTyping(false);
    },
    onSettled: () => {
      setIsTyping(false);
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input on component mount
  useEffect(() => {
    if (!currentConversationId) {
      startConversationMutation.mutate();
    }
    inputRef.current?.focus();
  }, [currentConversationId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || sendMessageMutation.isPending) return;

    sendMessageMutation.mutate(inputMessage.trim());
  };

  const handleClarification = (clarification: string) => {
    setInputMessage(`Sobre ${clarification}: `);
    inputRef.current?.focus();
  };

  const formatMessage = (content: string) => {
    // Basic markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-full">
            <MessageCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">Assistente de Prototipagem</h3>
            <p className="text-blue-100 text-sm">
              Conversação Inteligente • Minimax M2 AI
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '400px' }}>
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <span className="text-xs font-medium text-purple-600">IA Assistant</span>
                  </div>
                )}
                
                <div
                  dangerouslySetInnerHTML={{
                    __html: formatMessage(message.content),
                  }}
                />
                
                <div className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </div>

                {/* Extracted specifications */}
                {message.extractedSpecs && Object.keys(message.extractedSpecs).length > 0 && (
                  <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded">
                    <p className="text-xs font-medium text-green-800 mb-1">
                      ✅ Especificações Extraídas:
                    </p>
                    <div className="text-xs text-green-700">
                      {message.extractedSpecs.categoria && (
                        <div>Categoria: {message.extractedSpecs.categoria}</div>
                      )}
                      {message.extractedSpecs.material && (
                        <div>Material: {message.extractedSpecs.material}</div>
                      )}
                    </div>
                  </div>
                )}

                {/* Clarifications needed */}
                {message.clarifications && message.clarifications.length > 0 && (
                  <div className="mt-3 space-y-1">
                    <p className="text-xs font-medium text-yellow-800 mb-2">
                      💡 Para melhorar, você poderia especificar:
                    </p>
                    {message.clarifications.map((clarification, index) => (
                      <button
                        key={index}
                        onClick={() => handleClarification(clarification)}
                        className="block w-full text-left text-xs p-2 bg-yellow-50 border border-yellow-200 rounded hover:bg-yellow-100 transition-colors"
                      >
                        <HelpCircle className="w-3 h-3 inline mr-1" />
                        {clarification}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-xs text-gray-600">Pensando...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Descreva seu projeto em detalhes..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={sendMessageMutation.isPending}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || sendMessageMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2">
          💡 Dicas: Mencione dimensões, materiais, funcionalidades e restrições para melhor resultado
        </div>
      </form>
    </div>
  );
};