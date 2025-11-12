import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bot, 
  MessageSquare, 
  Cpu, 
  DollarSign, 
  TrendingUp, 
  Activity,
  Plus,
  Loader2,
  AlertCircle,
  CheckCircle,
  Box,
  Sparkles,
  Layers3,
  Zap,
  Users,
  Cloud,
  ShoppingCart
} from 'lucide-react';
import { motion } from 'framer-motion';
import { apiService } from '@/services/api';

interface SystemStatus {
  status: string;
  timestamp: string;
  environment: string;
  version: string;
  services: {
    database: string;
    redis: string;
    mqtt_bridge: string;
    websocket: string;
    minio: string;
  };
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSystemStatus();
    const interval = setInterval(loadSystemStatus, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, []);

  const loadSystemStatus = async () => {
    try {
      setError(null);
      const status = await apiService.getSystemHealth();
      setSystemStatus(status);
    } catch (error) {
      console.error('Erro ao carregar status do sistema:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro ao conectar com o servidor';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const getServiceIcon = (serviceName: string) => {
    switch (serviceName) {
      case 'database':
        return '🗄️';
      case 'redis':
        return '⚡';
      case 'mqtt_bridge':
        return '📡';
      case 'websocket':
        return '🔌';
      case 'minio':
        return '💾';
      default:
        return '⚙️';
    }
  };

  const getServiceStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'active':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'disconnected':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'connecting':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">3dPot Platform</h1>
                <p className="text-sm text-gray-600">
                  {systemStatus?.environment === 'development' ? 'Desenvolvimento' : 'Produção'} • v{systemStatus?.version}
                </p>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => navigate('/history')}
                className="inline-flex items-center px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors space-x-2"
              >
                <MessageSquare className="w-5 h-5" />
                <span>Histórico</span>
              </button>
              
              <button
                onClick={() => {
                  const newSessionId = `session_${Date.now()}`;
                  navigate(`/chat/${newSessionId}`);
                }}
                className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Nova Conversa</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-700">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Erro de Conexão</span>
            </div>
            <p className="text-red-600 mt-1">{error}</p>
            <button
              onClick={loadSystemStatus}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Status do Sistema</p>
                <p className="text-2xl font-bold text-green-600">
                  {systemStatus?.status === 'healthy' ? 'Saudável' : 'Erro'}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Serviços Ativos</p>
                <p className="text-2xl font-bold text-primary-600">
                  {systemStatus?.services ? Object.values(systemStatus.services).filter(s => s === 'connected' || s === 'active').length : 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-primary-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer"
            onClick={() => navigate('/chat')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Conversar com IA</p>
                <p className="text-2xl font-bold text-blue-600">Minimax M2</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate('/3d')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Modelos 3D</p>
                <p className="text-2xl font-bold text-orange-600">NVIDIA NIM</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Box className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Hardware</p>
                <p className="text-2xl font-bold text-purple-600">
                  {systemStatus?.services.mqtt_bridge === 'connected' ? 'Online' : 'Offline'}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Cpu className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate('/sprint6')}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sprint 6+</p>
                <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Advanced
                </p>
                <p className="text-xs text-gray-500">3D Printing • Collaboration • Cloud • Marketplace</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Status dos Serviços</span>
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Última verificação: {systemStatus?.timestamp ? new Date(systemStatus.timestamp).toLocaleString('pt-BR') : 'N/A'}
            </p>
          </div>

          <div className="p-6">
            {systemStatus?.services ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {Object.entries(systemStatus.services).map(([serviceName, serviceStatus]) => (
                  <div
                    key={serviceName}
                    className={`border rounded-lg p-4 ${getServiceStatusColor(serviceStatus)}`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getServiceIcon(serviceName)}</span>
                      <div>
                        <p className="font-medium capitalize">
                          {serviceName.replace('_', ' ')}
                        </p>
                        <p className="text-sm">
                          {serviceStatus === 'connected' || serviceStatus === 'active' ? 'Conectado' : 
                           serviceStatus === 'disconnected' ? 'Desconectado' : 'Conectando...'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Informações do sistema não disponíveis</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-6 text-white cursor-pointer hover:from-primary-600 hover:to-primary-700 transition-all"
            onClick={() => {
              const newSessionId = `session_${Date.now()}`;
              navigate(`/chat/${newSessionId}`);
            }}
          >
            <div className="flex items-center space-x-4">
              <Bot className="w-8 h-8" />
              <div>
                <h3 className="text-lg font-semibold">Nova Conversa IA</h3>
                <p className="text-primary-100">Inicie uma conversa com nosso especialista</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white cursor-pointer hover:from-green-600 hover:to-green-700 transition-all"
            onClick={() => navigate('/history')}
          >
            <div className="flex items-center space-x-4">
              <MessageSquare className="w-8 h-8" />
              <div>
                <h3 className="text-lg font-semibold">Ver Histórico</h3>
                <p className="text-green-100">Acesse suas conversas anteriores</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white cursor-pointer hover:from-orange-600 hover:to-orange-700 transition-all"
            onClick={() => navigate('/3d')}
          >
            <div className="flex items-center space-x-4">
              <Box className="w-8 h-8" />
              <div>
                <h3 className="text-lg font-semibold">Gerar Modelo 3D</h3>
                <p className="text-orange-100">Crie modelos com IA NVIDIA</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white cursor-pointer hover:from-blue-600 hover:to-purple-700 transition-all"
            onClick={() => navigate('/sprint6')}
          >
            <div className="flex items-center space-x-4">
              <Zap className="w-8 h-8" />
              <div>
                <h3 className="text-lg font-semibold">Sprint 6+ Features</h3>
                <p className="text-blue-100">3D Printing • Collaboration • Cloud • Marketplace</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}