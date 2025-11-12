# Integração de Serviços Sprint 6+

Este documento explica como usar os serviços TypeScript atualizados para conectar com os novos endpoints do backend Sprint 6+.

## 📋 Visão Geral

Os seguintes serviços foram atualizados para usar os novos endpoints do backend:

- `print3dService.ts` - Impressão 3D
- `collaborationService.ts` - Colaboração em tempo real
- `marketplaceService.ts` - Marketplace de modelos
- `cloudRenderingService.ts` - Renderização na nuvem
- `api.ts` - Serviço base com axios configurado
- `websocket.ts` - WebSocket para tempo real

## 🚀 Configuração

### 1. Variáveis de Ambiente

Configure as seguintes variáveis em um arquivo `.env` na raiz do frontend:

```env
# URLs da API
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Stripe (Marketplace)
VITE_STRIPE_PUBLIC_KEY=pk_test_...

# NVIDIA NIM (Cloud Rendering)
VITE_NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
```

### 2. Importação dos Serviços

```typescript
// Importações principais
import { print3DService } from '@/services/print3dService';
import { collaborationService } from '@/services/collaborationService';
import { marketplaceService } from '@/services/marketplaceService';
import { cloudRenderingService } from '@/services/cloudRenderingService';
import { conversationWebSocket } from '@/services/websocket';
```

## 📖 Exemplos de Uso

### 1. Impressão 3D

```typescript
import { print3DService } from '@/services/print3dService';

// Criar job de impressão
async function submitPrintJob() {
  try {
    const jobConfig = {
      modelId: 'model-123',
      printerId: 'printer-456',
      materialId: 'pla-blue',
      settings: {
        layerHeight: 0.2,
        infill: 20,
        printSpeed: 50,
        nozzleTemperature: 200,
        bedTemperature: 60
      }
    };

    const jobId = await print3DService.submitJob(jobConfig);
    console.log('Job criado:', jobId);
  } catch (error) {
    console.error('Erro ao criar job:', error);
  }
}

// Monitorar progresso
function monitorPrintJob(jobId: string) {
  print3DService.on('job_updated', (job) => {
    console.log(`Job ${job.id}: ${job.progress}%`);
  });

  print3DService.on('print_progress', (progress) => {
    console.log(`Progresso: ${progress.progress}%`);
  });
}

// Listar impressoras
async function listPrinters() {
  try {
    const printers = await print3DService.loadPrinters();
    console.log('Impressoras disponíveis:', printers);
  } catch (error) {
    console.error('Erro ao listar impressoras:', error);
  }
}
```

### 2. Colaboração em Tempo Real

```typescript
import { collaborationService } from '@/services/collaborationService';
import { conversationWebSocket } from '@/services/websocket';

// Criar sessão de colaboração
async function createCollaborationSession() {
  try {
    const sessionData = {
      modelId: 'model-123',
      user: {
        id: 'user-456',
        username: 'João Silva',
        email: 'joao@example.com'
      }
    };

    const sessionId = await collaborationService.createSession('model-123', sessionData.user);
    console.log('Sessão criada:', sessionId);

    // Conectar ao WebSocket
    await conversationWebSocket.connectToCollaboration(sessionId, 'user-456');

    // Registrar eventos de colaboração
    const unsubscribe = conversationWebSocket.onCollaborationEvent((event) => {
      switch (event.type) {
        case 'participant_joined':
          console.log('Participante entrou:', event.data);
          break;
        case 'cursor_move':
          console.log('Cursor movido:', event.data);
          break;
        case 'model_edit':
          console.log('Modelo editado:', event.data);
          break;
      }
    });

    return () => unsubscribe();
  } catch (error) {
    console.error('Erro ao criar sessão:', error);
  }
}

// Enviar mensagem
async function sendMessage(sessionId: string) {
  try {
    await collaborationService.sendMessage(sessionId, {
      content: 'Vamos trabalhar juntos neste modelo!',
      type: 'text'
    });
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
  }
}
```

### 3. Marketplace

```typescript
import { marketplaceService } from '@/services/marketplaceService';

// Criar listing
async function createModelListing() {
  try {
    const listingData = {
      title: 'Modelo 3D Personalizado',
      description: 'Um modelo de alta qualidade para impressão 3D',
      price: 29.99,
      category: 'toys',
      tags: ['custom', 'high-quality', 'printable'],
      modelFile: modelFile,
      thumbnail: thumbnailFile,
      visibility: 'public'
    };

    const listing = await marketplaceService.createListing(listingData);
    console.log('Listing criado:', listing.id);
  } catch (error) {
    console.error('Erro ao criar listing:', error);
  }
}

// Buscar modelos
async function searchModels() {
  try {
    const searchParams = {
      q: 'impressão 3D',
      category: 'toys',
      priceMin: 0,
      priceMax: 100,
      sortBy: 'popularity'
    };

    const results = await marketplaceService.search(searchParams);
    console.log('Resultados da busca:', results.listings);
  } catch (error) {
    console.error('Erro na busca:', error);
  }
}

// Fazer purchase
async function purchaseModel(listingId: string) {
  try {
    const transaction = await marketplaceService.purchase(listingId, {
      paymentMethod: 'card',
      quantity: 1
    });

    console.log('Purchase realizada:', transaction.id);
  } catch (error) {
    console.error('Erro no purchase:', error);
  }
}
```

### 4. Cloud Rendering

```typescript
import { cloudRenderingService } from '@/services/cloudRenderingService';

// Submeter job de render
async function submitRenderJob() {
  try {
    const jobConfig = {
      modelId: 'model-123',
      configuration: {
        resolution: { width: 1920, height: 1080 },
        quality: {
          level: 'high',
          samples: 256,
          maxRayDepth: 4
        }
      },
      priority: 'normal'
    };

    const jobId = await cloudRenderingService.submitRenderJob(
      'model-123',
      jobConfig.configuration,
      'normal'
    );

    console.log('Job de render submetido:', jobId);
    
    // Monitorar progresso
    cloudRenderingService.on('job_progress', (progress) => {
      console.log(`Render: ${progress.percent}%`);
    });

    return jobId;
  } catch (error) {
    console.error('Erro ao submeter job:', error);
  }
}

// Estimar custo
async function estimateRenderCost() {
  try {
    const renderParams = {
      resolution: { width: 1920, height: 1080 },
      quality: 'high',
      duration: 3600 // 1 hora
    };

    const estimate = await cloudRenderingService.estimateCost(renderParams);
    console.log('Custo estimado:', estimate.totalCost);
  } catch (error) {
    console.error('Erro ao estimar custo:', error);
  }
}
```

### 5. WebSocket para Tempo Real

```typescript
import { conversationWebSocket } from '@/services/websocket';

// Conectar para impressão 3D
async function connectPrintingWebSocket() {
  try {
    await conversationWebSocket.connectToPrinting();
    
    const unsubscribe = conversationWebSocket.onPrintingEvent((event) => {
      switch (event.type) {
        case 'job_update':
          console.log('Job atualizado:', event.data);
          break;
        case 'printer_status':
          console.log('Status da impressora:', event.data);
          break;
        case 'print_progress':
          console.log('Progresso:', event.data.progress, '%');
          break;
      }
    });

    return unsubscribe;
  } catch (error) {
    console.error('Erro ao conectar WebSocket:', error);
  }
}
```

## 🔧 Configuração do Axios

O `apiService` já está configurado com:

- **Base URL**: Automático baseado no ambiente (dev/prod)
- **Timeout**: 30 segundos para operações longas
- **Headers**: JSON por padrão
- **Autenticação**: JWT token automático via localStorage
- **Interceptors**: 
  - Request: Adiciona token Bearer
  - Response: Trata erros 401 (token expirado)

```typescript
import { apiService } from '@/services/api';

// Usar diretamente
async function customApiCall() {
  try {
    const response = await apiService.get('/custom/endpoint');
    return response.data;
  } catch (error) {
    console.error('Erro na API:', error);
  }
}
```

## 📡 Endpoints Mapeados

### Sprint 6+ Endpoints

**3D Printing:**
- `GET /api/printing/printers` - Listar impressoras
- `POST /api/printing/printers` - Criar impressora
- `POST /api/printing/jobs` - Submeter job
- `GET /api/printing/jobs/{id}/status` - Status do job
- `POST /api/printing/jobs/{id}/cancel` - Cancelar job
- `GET /api/printing/queue` - Fila de impressão

**Collaboration:**
- `POST /api/collaboration/sessions` - Criar sessão
- `GET /api/collaboration/sessions` - Listar sessões
- `POST /api/collaboration/sessions/{id}/participants` - Adicionar participante
- `POST /api/collaboration/sessions/{id}/messages` - Enviar mensagem
- `WS /api/collaboration/ws/{id}` - WebSocket da sessão

**Marketplace:**
- `POST /api/marketplace/listings` - Criar listing
- `GET /api/marketplace/search` - Buscar listings
- `POST /api/marketplace/transactions` - Criar transação
- `POST /api/marketplace/payments/intent` - Payment intent Stripe
- `POST /api/marketplace/reviews` - Adicionar review

**Cloud Rendering:**
- `POST /api/rendering/jobs` - Submeter job
- `GET /api/rendering/jobs/{id}/status` - Status do job
- `GET /api/rendering/clusters` - Listar clusters
- `POST /api/rendering/batch-jobs` - Batch jobs
- `GET /api/rendering/estimates` - Estimar custo

## ⚠️ Notas Importantes

1. **Autenticação**: Os serviços automaticamente incluem o JWT token
2. **WebSocket**: Reconexão automática configurada
3. **Error Handling**: Todos os métodos incluem try/catch
4. **Eventos**: Sistema de eventos para atualizações em tempo real
5. **Cache**: Alguns serviços implementam cache local
6. **Validação**: Dados são validados antes do envio

## 🔍 Debug

Para debug, ative os logs:

```typescript
// Ativar logs detalhados
localStorage.setItem('debug', 'true');

// Verificar conexões
console.log('WebSocket status:', conversationWebSocket.getConnectionStatus());
console.log('Jobs ativos:', cloudRenderingService.getActiveJobs());
```

## 📚 Próximos Passos

1. Integrar serviços nos componentes React
2. Implementar UI para cada funcionalidade
3. Adicionar testes unitários
4. Configurar monitoramento
5. Otimizar performance
