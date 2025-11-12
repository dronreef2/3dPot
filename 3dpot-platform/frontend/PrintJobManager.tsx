// Exemplo de Componente React atualizado para usar os novos serviços Sprint 6+
// Arquivo: src/components/PrintJobManager.tsx

import React, { useState, useEffect } from 'react';
import { print3DService } from '@/services/print3dService';
import { collaborationService } from '@/services/collaborationService';
import { conversationWebSocket } from '@/services/websocket';
import toast from 'react-hot-toast';

// Types
interface PrintJob {
  id: string;
  modelId: string;
  printerId: string;
  status: 'queued' | 'processing' | 'printing' | 'completed' | 'failed';
  progress: number;
  createdAt: Date;
}

interface Printer {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'printing' | 'error';
  temperature: number;
  bedTemperature: number;
}

export const PrintJobManager: React.FC = () => {
  // Estados
  const [jobs, setJobs] = useState<PrintJob[]>([]);
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPrinter, setSelectedPrinter] = useState<string>('');
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);

  // Efeitos
  useEffect(() => {
    loadInitialData();
    setupWebSocket();
    setupEventListeners();

    return () => {
      // Cleanup
      if (isWebSocketConnected) {
        conversationWebSocket.disconnect();
      }
    };
  }, []);

  // Carregar dados iniciais
  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      // Carregar impressoras
      const printersList = await print3DService.loadPrinters();
      setPrinters(printersList);

      // Carregar fila de jobs
      const queue = await print3DService.getQueue();
      setJobs(queue);

      console.log('✅ Dados carregados:', { printers: printersList.length, jobs: queue.length });
    } catch (error) {
      console.error('❌ Erro ao carregar dados:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  // Configurar WebSocket para tempo real
  const setupWebSocket = async () => {
    try {
      await conversationWebSocket.connectToPrinting();
      setIsWebSocketConnected(true);
      toast.success('Conectado ao monitoramento de impressão');
    } catch (error) {
      console.error('❌ Erro ao conectar WebSocket:', error);
      toast.error('Erro ao conectar monitoramento');
    }
  };

  // Configurar listeners de eventos
  const setupEventListeners = () => {
    // Job atualizado
    const unsubscribeJobUpdate = print3DService.on('job_updated', (job: PrintJob) => {
      setJobs(prev => prev.map(j => j.id === job.id ? job : j));
      
      if (job.status === 'completed') {
        toast.success(`Job ${job.id} concluído!`);
      } else if (job.status === 'failed') {
        toast.error(`Job ${job.id} falhou`);
      }
    });

    // Progresso de impressão
    const unsubscribeProgress = print3DService.on('print_progress', (progress: any) => {
      toast.loading(`Impressão: ${progress.progress}%`);
    });

    // Status da impressora
    const unsubscribePrinter = print3DService.on('printer_status_changed', (printer: Printer) => {
      setPrinters(prev => prev.map(p => p.id === printer.id ? printer : p));
    });

    // WebSocket de impressão
    const unsubscribeWs = conversationWebSocket.onPrintingEvent((event) => {
      console.log('📡 WebSocket event:', event);
    });

    // Retornar funções de cleanup
    return () => {
      unsubscribeJobUpdate();
      unsubscribeProgress();
      unsubscribePrinter();
      unsubscribeWs();
    };
  };

  // Submeter job de impressão
  const handleSubmitJob = async (modelId: string, settings: any) => {
    if (!selectedPrinter) {
      toast.error('Selecione uma impressora');
      return;
    }

    try {
      setIsLoading(true);
      
      const jobConfig = {
        modelId,
        printerId: selectedPrinter,
        settings: {
          layerHeight: 0.2,
          infill: 20,
          printSpeed: 50,
          nozzleTemperature: 200,
          bedTemperature: 60,
          ...settings
        }
      };

      const jobId = await print3DService.submitJob(jobConfig);
      
      toast.success(`Job ${jobId} submetido com sucesso!`);
      
      // Recarregar fila
      const queue = await print3DService.getQueue();
      setJobs(queue);
      
    } catch (error) {
      console.error('❌ Erro ao submeter job:', error);
      toast.error('Erro ao submeter job de impressão');
    } finally {
      setIsLoading(false);
    }
  };

  // Cancelar job
  const handleCancelJob = async (jobId: string) => {
    try {
      await print3DService.cancelJob(jobId);
      toast.success('Job cancelado');
      
      // Atualizar estado local
      setJobs(prev => prev.map(j => 
        j.id === jobId ? { ...j, status: 'cancelled' } : j
      ));
      
    } catch (error) {
      console.error('❌ Erro ao cancelar job:', error);
      toast.error('Erro ao cancelar job');
    }
  };

  // Pausar job
  const handlePauseJob = async (jobId: string) => {
    try {
      await print3DService.pauseJob(jobId);
      toast.success('Job pausado');
      
      // Atualizar estado
      setJobs(prev => prev.map(j => 
        j.id === jobId ? { ...j, status: 'paused' } : j
      ));
      
    } catch (error) {
      console.error('❌ Erro ao pausar job:', error);
      toast.error('Erro ao pausar job');
    }
  };

  // Retomar job
  const handleResumeJob = async (jobId: string) => {
    try {
      await print3DService.resumeJob(jobId);
      toast.success('Job retomado');
      
      // Atualizar estado
      setJobs(prev => prev.map(j => 
        j.id === jobId ? { ...j, status: 'printing' } : j
      ));
      
    } catch (error) {
      console.error('❌ Erro ao retomar job:', error);
      toast.error('Erro ao retomar job');
    }
  };

  // Criar sessão de colaboração para o job
  const handleStartCollaboration = async (jobId: string) => {
    try {
      const job = jobs.find(j => j.id === jobId);
      if (!job) return;

      const userProfile = {
        id: 'current-user',
        username: 'Usuário Atual',
        email: 'usuario@example.com'
      };

      const sessionId = await collaborationService.createSession(job.modelId, userProfile);
      
      // Conectar ao WebSocket de colaboração
      await conversationWebSocket.connectToCollaboration(sessionId, userProfile.id);
      
      toast.success(`Sessão de colaboração iniciada: ${sessionId}`);
      
    } catch (error) {
      console.error('❌ Erro ao iniciar colaboração:', error);
      toast.error('Erro ao iniciar sessão de colaboração');
    }
  };

  // Calibrar impressora
  const handleCalibratePrinter = async (printerId: string, type: string) => {
    try {
      await print3DService.calibratePrinter(printerId, type);
      toast.success('Calibração iniciada');
    } catch (error) {
      console.error('❌ Erro ao calibrar:', error);
      toast.error('Erro ao calibrar impressora');
    }
  };

  // Estimar tempo de impressão
  const estimatePrintTime = async (modelId: string, settings: any) => {
    try {
      const modelData = { /* dados do modelo */ };
      const estimatedTime = await print3DService.estimatePrintTime(settings, modelData);
      
      const hours = Math.floor(estimatedTime / 3600);
      const minutes = Math.floor((estimatedTime % 3600) / 60);
      
      toast.success(`Tempo estimado: ${hours}h ${minutes}min`);
      
      return estimatedTime;
    } catch (error) {
      console.error('❌ Erro ao estimar tempo:', error);
      toast.error('Erro ao estimar tempo de impressão');
    }
  };

  // Renderizar lista de jobs
  const renderJobsList = () => {
    if (jobs.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          Nenhum job na fila
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="border rounded-lg p-4 bg-white shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">Job {job.id}</h3>
                <p className="text-sm text-gray-600">Modelo: {job.modelId}</p>
                <p className="text-sm text-gray-600">Impressora: {job.printerId}</p>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded text-sm ${
                  job.status === 'completed' ? 'bg-green-100 text-green-800' :
                  job.status === 'failed' ? 'bg-red-100 text-red-800' :
                  job.status === 'printing' ? 'bg-blue-100 text-blue-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {job.status}
                </span>
                
                {job.status === 'printing' && (
                  <span className="text-sm">{job.progress}%</span>
                )}
              </div>
            </div>

            {job.status === 'printing' && (
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="mt-4 flex space-x-2">
              {job.status === 'queued' && (
                <button
                  onClick={() => handleCancelJob(job.id)}
                  className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Cancelar
                </button>
              )}
              
              {job.status === 'printing' && (
                <>
                  <button
                    onClick={() => handlePauseJob(job.id)}
                    className="px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                  >
                    Pausar
                  </button>
                  <button
                    onClick={() => handleCancelJob(job.id)}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Cancelar
                  </button>
                </>
              )}
              
              {job.status === 'paused' && (
                <button
                  onClick={() => handleResumeJob(job.id)}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Retomar
                </button>
              )}
              
              <button
                onClick={() => handleStartCollaboration(job.id)}
                className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
              >
                Colaborar
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Renderizar lista de impressoras
  const renderPrintersList = () => {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {printers.map(printer => (
          <div key={printer.id} className="border rounded-lg p-4 bg-white shadow">
            <h3 className="font-semibold">{printer.name}</h3>
            <div className="mt-2 space-y-1">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Status:</span>
                <span className={`text-sm ${
                  printer.status === 'online' ? 'text-green-600' :
                  printer.status === 'error' ? 'text-red-600' :
                  printer.status === 'printing' ? 'text-blue-600' :
                  'text-gray-600'
                }`}>
                  {printer.status}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Nozzle:</span>
                <span className="text-sm">{printer.temperature}°C</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Bed:</span>
                <span className="text-sm">{printer.bedTemperature}°C</span>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <button
                onClick={() => setSelectedPrinter(printer.id)}
                className={`w-full px-3 py-1 rounded ${
                  selectedPrinter === printer.id 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {selectedPrinter === printer.id ? 'Selecionada' : 'Selecionar'}
              </button>
              
              <button
                onClick={() => handleCalibratePrinter(printer.id, 'auto')}
                className="w-full px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
              >
                Calibrar
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Gerenciador de Impressão 3D</h1>

      {/* Status da conexão */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <div className="flex items-center space-x-4">
          <div className={`w-3 h-3 rounded-full ${
            isWebSocketConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-sm">
            WebSocket: {isWebSocketConnected ? 'Conectado' : 'Desconectado'}
          </span>
          <span className="text-sm text-gray-600">
            Impressoras: {printers.length} | Jobs: {jobs.length}
          </span>
        </div>
      </div>

      {/* Grid principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Coluna esquerda - Jobs */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Fila de Impressão</h2>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando...</p>
            </div>
          ) : (
            renderJobsList()
          )}
        </div>

        {/* Coluna direita - Impressoras */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Impressoras</h2>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Carregando...</p>
            </div>
          ) : (
            renderPrintersList()
          )}
        </div>
      </div>

      {/* Formulário para submeter job */}
      <div className="mt-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Submeter Novo Job</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Modelo ID</label>
            <input 
              type="text" 
              className="w-full border rounded px-3 py-2"
              placeholder="model-123"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Layer Height</label>
            <input 
              type="number" 
              step="0.05"
              defaultValue="0.2"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Infill (%)</label>
            <input 
              type="number"
              defaultValue="20"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Velocidade</label>
            <input 
              type="number"
              defaultValue="50"
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>

        <div className="mt-4 flex space-x-4">
          <button
            onClick={() => {
              const modelId = 'model-demo';
              const settings = {
                layerHeight: 0.2,
                infill: 20,
                printSpeed: 50
              };
              handleSubmitJob(modelId, settings);
            }}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            disabled={!selectedPrinter || isLoading}
          >
            Submeter Job
          </button>
          
          <button
            onClick={() => {
              const modelId = 'model-demo';
              const settings = {
                layerHeight: 0.2,
                infill: 20,
                printSpeed: 50
              };
              estimatePrintTime(modelId, settings);
            }}
            className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            disabled={isLoading}
          >
            Estimar Tempo
          </button>
        </div>

        {!selectedPrinter && (
          <p className="mt-2 text-red-600 text-sm">
            ⚠️ Selecione uma impressora antes de submeter um job
          </p>
        )}
      </div>
    </div>
  );
};

export default PrintJobManager;
