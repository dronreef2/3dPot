import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse, ConversationSession } from '@/types';
import { getApiBaseUrl } from '@/utils/config';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 10000,
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
}

// Instância singleton
export const apiService = new ApiService();