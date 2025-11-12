import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChatInterface } from '@/components/ChatInterface';
import { useConversation } from '@/contexts/ConversationContext';
import { apiService } from '@/services/api';
import { Loader2, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { setSessions, setError, state } = useConversation();
  const [isLoading, setIsLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);

  // Carregar sessões existentes
  useEffect(() => {
    const loadSessions = async () => {
      try {
        setIsLoading(true);
        const sessions = await apiService.getConversationSessions();
        setSessions(sessions);
        setLoadError(null);
      } catch (error) {
        console.error('Erro ao carregar sessões:', error);
        const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar sessões';
        setLoadError(errorMessage);
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    loadSessions();
  }, [setSessions, setError]);

  // Verificar se a sessão existe, se não, criar nova
  useEffect(() => {
    if (sessionId && !isLoading && !loadError) {
      const sessionExists = state.sessions.find(s => s.sessionId === sessionId);
      
      if (!sessionExists && state.sessions.length > 0) {
        // Se a sessão não existe e temos outras sessões, redirecionar para a mais recente
        const mostRecentSession = state.sessions[0];
        navigate(`/chat/${mostRecentSession.sessionId}`, { replace: true });
      }
    }
  }, [sessionId, state.sessions, isLoading, loadError, navigate]);

  // Estados de carregamento
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
          <p className="text-gray-600">Carregando sessões...</p>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <h2 className="text-xl font-semibold text-gray-900">Erro ao Carregar</h2>
          <p className="text-gray-600">{loadError}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  // Se não tem sessionId, criar nova
  if (!sessionId) {
    const newSessionId = `session_${Date.now()}`;
    navigate(`/chat/${newSessionId}`, { replace: true });
    return null;
  }

  // Verificar se a sessão existe ou criar nova automaticamente
  const sessionExists = state.sessions.find(s => s.sessionId === sessionId);
  
  if (!sessionExists) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Nova Sessão</h2>
          <p className="text-gray-600">Iniciando conversa...</p>
          <Loader2 className="w-6 h-6 animate-spin mx-auto text-primary-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatInterface sessionId={sessionId} />
    </div>
  );
}