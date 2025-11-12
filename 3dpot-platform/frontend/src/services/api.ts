import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse, ConversationSession } from '@/types';
import { getApiBaseUrl, API_ENDPOINTS } from '@/utils/config';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 30000, // Aumentado para operações mais longas como slicing e render
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Configura interceptors da requisição e resposta
   */
  private setupInterceptors(): void {
    // Request interceptor para adicionar token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor para tratamento de erros
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado - limpar do localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Busca lista de sessões de conversação
   */
  async getConversationSessions(userId?: number): Promise<ConversationSession[]> {
    try {
      const response: AxiosResponse = await this.client.get('/conversations/sessions', {
        params: userId ? { user_id: userId } : {}
      });
      
      return response.data.sessions || [];
    } catch (error) {
      console.error('Erro ao buscar sessões:', error);
      throw error;
    }
  }

  /**
   * Busca mensagens de uma sessão específica
   */
  async getSessionMessages(sessionId: string, limit: number = 50): Promise<any[]> {
    try {
      const response: AxiosResponse = await this.client.get(
        `/conversations/sessions/${sessionId}/messages`,
        { params: { limit } }
      );
      
      return response.data.messages || [];
    } catch (error) {
      console.error('Erro ao buscar mensagens da sessão:', error);
      throw error;
    }
  }

  /**
   * Busca status do sistema (health check)
   */
  async getSystemHealth(): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar status do sistema:', error);
      throw error;
    }
  }

  /**
   * Busca modelo 3D por ID
   */
  async getModel(modelId: string): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.get(`/models/${modelId}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar modelo:', error);
      throw error;
    }
  }

  /**
   * Lista modelos 3D do usuário
   */
  async getUserModels(userId?: number): Promise<any[]> {
    try {
      const response: AxiosResponse = await this.client.get('/models', {
        params: userId ? { user_id: userId } : {}
      });
      
      return response.data.models || [];
    } catch (error) {
      console.error('Erro ao buscar modelos do usuário:', error);
      throw error;
    }
  }

  /**
   * Gera orçamento para projeto
   */
  async generateBudget(projectId: string): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.post('/budgets/generate', {
        project_id: projectId
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar orçamento:', error);
      throw error;
    }
  }

  /**
   * Busca status de hardware
   */
  async getHardwareStatus(): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.get('/hardware/status');
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar status do hardware:', error);
      throw error;
    }
  }

  /**
   * Autenticação - Login
   */
  async login(email: string, password: string): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.post('/auth/login', {
        email,
        password
      });
      
      // Salvar tokens no localStorage
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
      }
      if (response.data.refresh_token) {
        localStorage.setItem('auth_refresh_token', response.data.refresh_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  }

  /**
   * Autenticação - Registro
   */
  async register(email: string, password: string, name: string): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.post('/auth/register', {
        email,
        password,
        name
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro no registro:', error);
      throw error;
    }
  }

  /**
   * Autenticação - Logout
   */
  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } catch (error) {
      console.error('Erro no logout:', error);
    } finally {
      // Limpar tokens localmente independentemente do resultado
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_refresh_token');
    }
  }

  /**
   * Autenticação - Verificar se está logado
   */
  async getCurrentUser(): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar usuário atual:', error);
      throw error;
    }
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<any> {
    try {
      const refreshToken = localStorage.getItem('auth_refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response: AxiosResponse = await this.client.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Erro no refresh token:', error);
      throw error;
    }
  }

  // ===== SPRINT 6+ API METHODS =====

  /**
   * 3D Printing API Methods
   */
  async getPrinters() {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.PRINTING.PRINTERS);
    return response.data;
  }

  async createPrinter(printerData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.PRINTERS, printerData);
    return response.data;
  }

  async getMaterials() {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.PRINTING.MATERIALS);
    return response.data;
  }

  async createMaterial(materialData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.MATERIALS, materialData);
    return response.data;
  }

  async submitPrintJob(jobData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.JOBS, jobData);
    return response.data;
  }

  async getJobStatus(jobId: string) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.PRINTING.STATUS(jobId));
    return response.data;
  }

  async cancelJob(jobId: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.CANCEL(jobId));
    return response.data;
  }

  async getPrintQueue() {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.PRINTING.QUEUE);
    return response.data;
  }

  async sliceModel(modelData: any, settings: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.SLICE, {
      modelData,
      settings
    });
    return response.data;
  }

  async generateGCode(modelId: string, settings: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.GENERATE_GCODE, {
      modelId,
      settings
    });
    return response.data;
  }

  async calibratePrinter(printerId: string, calibrationType: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.CALIBRATE(printerId), {
      type: calibrationType
    });
    return response.data;
  }

  async estimatePrintTime(settings: any, modelData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.PRINTING.ESTIMATE_TIME, {
      settings,
      modelData
    });
    return response.data;
  }

  /**
   * Collaboration API Methods
   */
  async createCollaborationSession(sessionData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.SESSIONS, sessionData);
    return response.data;
  }

  async getCollaborationSessions() {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.COLLABORATION.SESSIONS);
    return response.data;
  }

  async addParticipant(sessionId: string, participantData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.PARTICIPANTS(sessionId), participantData);
    return response.data;
  }

  async sendMessage(sessionId: string, messageData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.MESSAGES(sessionId), messageData);
    return response.data;
  }

  async getMessages(sessionId: string, limit: number = 50) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.COLLABORATION.MESSAGES(sessionId), {
      params: { limit }
    });
    return response.data;
  }

  async createAnnotation(sessionId: string, annotationData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.ANNOTATIONS(sessionId), annotationData);
    return response.data;
  }

  async startVideoCall(sessionId: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.VIDEO_CALL(sessionId));
    return response.data;
  }

  async startScreenShare(sessionId: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.SCREEN_SHARE(sessionId));
    return response.data;
  }

  async startRecording(sessionId: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.COLLABORATION.RECORDING(sessionId));
    return response.data;
  }

  /**
   * Marketplace API Methods
   */
  async createListing(listingData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.MARKETPLACE.LISTINGS, listingData);
    return response.data;
  }

  async getListings(searchParams?: any) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.MARKETPLACE.SEARCH, {
      params: searchParams
    });
    return response.data;
  }

  async getListing(id: string) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.MARKETPLACE.LISTING(id));
    return response.data;
  }

  async createTransaction(transactionData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.MARKETPLACE.TRANSACTIONS, transactionData);
    return response.data;
  }

  async createPaymentIntent(amount: number, currency: string = 'usd', metadata?: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.MARKETPLACE.PAYMENTS_INTENT, {
      amount,
      currency,
      metadata
    });
    return response.data;
  }

  async addReview(reviewData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.MARKETPLACE.REVIEWS, reviewData);
    return response.data;
  }

  async getReviews(listingId: string) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.MARKETPLACE.REVIEWS, {
      params: { listingId }
    });
    return response.data;
  }

  /**
   * Cloud Rendering API Methods
   */
  async createRenderCluster(clusterData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.CLUSTERS, clusterData);
    return response.data;
  }

  async getRenderClusters() {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.CLOUD_RENDERING.CLUSTERS);
    return response.data;
  }

  async submitRenderJob(jobData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.JOBS, jobData);
    return response.data;
  }

  async getRenderJob(jobId: string) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.CLOUD_RENDERING.JOB(jobId));
    return response.data;
  }

  async getRenderJobStatus(jobId: string) {
    const response: AxiosResponse = await this.client.get(API_ENDPOINTS.CLOUD_RENDERING.JOB_STATUS(jobId));
    return response.data;
  }

  async cancelRenderJob(jobId: string) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.JOB_CANCEL(jobId));
    return response.data;
  }

  async submitBatchRenderJob(batchData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.BATCH_JOBS, batchData);
    return response.data;
  }

  async createRenderPreset(presetData: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.PRESETS, presetData);
    return response.data;
  }

  async estimateRenderCost(renderParams: any) {
    const response: AxiosResponse = await this.client.post(API_ENDPOINTS.CLOUD_RENDERING.ESTIMATES, renderParams);
    return response.data;
  }
}

// Instância singleton
export const apiService = new ApiService();