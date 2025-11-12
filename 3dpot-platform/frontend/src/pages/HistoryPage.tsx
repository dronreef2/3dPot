import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, MessageSquare, Clock, TrendingUp, AlertCircle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { ConversationSession } from '@/types';
import { apiService } from '@/services/api';
import { formatTimestamp } from '@/utils/helpers';
import toast from 'react-hot-toast';

export function HistoryPage() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.getConversationSessions();
      setSessions(data);
    } catch (error) {
      console.error('Erro ao carregar sessões:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar histórico';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = () => {
    const newSessionId = `session_${Date.now()}`;
    navigate(`/chat/${newSessionId}`);
  };

  const handleOpenSession = (sessionId: string) => {
    navigate(`/chat/${sessionId}`);
  };

  const filteredSessions = sessions.filter(session => {
    if (filter === 'all') return true;
    return session.status === filter;
  });

  const getStatusBadge = (status: string) => {
    const badges = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      archived: 'bg-gray-100 text-gray-800'
    };

    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-400';
    if (confidence >= 0.7) return 'text-green-600';
    if (confidence >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
          <p className="text-gray-600">Carregando histórico...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <h2 className="text-xl font-semibold text-gray-900">Erro ao Carregar</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadSessions}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <MessageSquare className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Histórico de Conversas</h1>
                <p className="text-sm text-gray-600">
                  {sessions.length} sessões {filter !== 'all' && `(${filter})`}
                </p>
              </div>
            </div>
            
            <button
              onClick={handleNewSession}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Nova Conversa</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex space-x-4">
          {(['all', 'active', 'completed'] as const).map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === filterType
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {filterType === 'all' ? 'Todas' : 
               filterType === 'active' ? 'Ativas' : 'Concluídas'}
            </button>
          ))}
        </div>
      </div>

      {/* Sessions List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {filteredSessions.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'all' ? 'Nenhuma conversa encontrada' : 
               filter === 'active' ? 'Nenhuma conversa ativa' : 'Nenhuma conversa concluída'}
            </h3>
            <p className="text-gray-600 mb-6">
              {filter === 'all' ? 'Comece uma nova conversa com nosso assistente IA' : 
               `Não há conversas ${filter === 'active' ? 'ativas' : 'concluídas'}`}
            </p>
            <button
              onClick={handleNewSession}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Iniciar Nova Conversa</span>
            </button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredSessions.map((session) => (
              <motion.div
                key={session.sessionId}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -2 }}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleOpenSession(session.sessionId)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 truncate max-w-[200px]">
                        {session.title || 'Sessão sem título'}
                      </h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimestamp(session.createdAt)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(session.status)}`}>
                    {session.status === 'active' ? 'Ativa' : 
                     session.status === 'completed' ? 'Concluída' : 'Arquivada'}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Mensagens:</span>
                    <span className="font-medium text-gray-900">{session.messageCount}</span>
                  </div>
                  
                  {session.lastConfidence && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Confiança:</span>
                      <span className={`font-medium ${getConfidenceColor(session.lastConfidence)}`}>
                        {Math.round(session.lastConfidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      Atualizada {formatTimestamp(session.updatedAt)}
                    </span>
                    <TrendingUp className="w-4 h-4 text-gray-400" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}