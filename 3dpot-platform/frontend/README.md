# 3dPot Platform - Frontend

Interface React moderna para a plataforma de prototipagem 3D com assistente IA Minimax M2.

## 🚀 Funcionalidades

### ✅ Sprint 2-3: Conversação IA Completa
- **Interface React Chat** com design responsivo e moderno
- **WebSocket Real-time** para comunicação instantânea
- **Integração Minimax M2 Agent** para processamento inteligente
- **Spec Extractor** com confidence scoring automático
- **Sistema de conversação em tempo real** com status visual
- **Histórico de conversas** com filtros e estatísticas
- **Dashboard** com status do sistema e métricas

## 🛠️ Tecnologias

### Frontend Stack
- **React 18** - Framework principal
- **TypeScript** - Tipagem estática
- **Vite** - Build tool e dev server
- **TailwindCSS** - Estilização utility-first
- **Framer Motion** - Animações fluidas
- **React Router** - Navegação SPA
- **Axios** - Cliente HTTP
- **Socket.io Client** - WebSocket client
- **Zustand** - State management (preparado)
- **React Hot Toast** - Notificações
- **Lucide React** - Ícones SVG

### Recursos Implementados
- **Context API** para estado global da conversação
- **Custom Hooks** para WebSocket e gestão de estado
- **Componentes modulares** reutilizáveis
- **TypeScript interfaces** para type safety
- **Responsive design** mobile-first
- **Error handling** robusto
- **Loading states** e feedback visual
- **Proxy configurado** para desenvolvimento

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/           # Componentes React
│   │   └── ChatInterface.tsx # Interface principal do chat
│   ├── pages/               # Páginas da aplicação
│   │   ├── DashboardPage.tsx # Dashboard com status
│   │   ├── ChatPage.tsx      # Página do chat
│   │   └── HistoryPage.tsx   # Histórico de conversas
│   ├── services/            # Serviços e APIs
│   │   ├── api.ts           # Cliente HTTP Axios
│   │   └── websocket.ts     # WebSocket manager
│   ├── hooks/              # Custom hooks
│   │   └── useWebSocket.ts  # Hook para WebSocket
│   ├── contexts/           # React contexts
│   │   └── ConversationContext.tsx # Estado global
│   ├── types/              # TypeScript types
│   │   ├── index.ts        # Tipos gerais
│   │   └── conversation.ts # Tipos de conversação
│   ├── utils/              # Utilitários
│   │   ├── config.ts       # Configurações
│   │   └── helpers.ts      # Funções auxiliares
│   ├── App.tsx             # Componente principal
│   ├── main.tsx            # Entry point
│   └── index.css           # Estilos globais
├── public/                 # Assets estáticos
├── package.json            # Dependências
├── vite.config.ts          # Configuração Vite
├── tailwind.config.js      # Configuração TailwindCSS
├── tsconfig.json           # Configuração TypeScript
└── .env                    # Variáveis de ambiente
```

## 🚀 Instalação e Execução

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn
- Backend 3dPot rodando (porta 8000)

### Instalação
```bash
# Navegar para o diretório frontend
cd frontend

# Instalar dependências
npm install
# ou
yarn install
```

### Desenvolvimento
```bash
# Iniciar servidor de desenvolvimento
npm run dev
# ou
yarn dev

# Acessar: http://localhost:3000
```

### Build para Produção
```bash
# Criar build otimizado
npm run build
# ou
yarn build

# Preview do build
npm run preview
# ou
yarn preview
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=3dPot Platform
VITE_NODE_ENV=development
```

### Proxy (Desenvolvimento)
O `vite.config.ts` já inclui proxy configurado:
- `/api` → `http://localhost:8000/api`
- `/ws` → `ws://localhost:8000/ws`

### URLs da API
- **API REST**: `http://localhost:8000/api`
- **WebSocket**: `ws://localhost:8000/ws`
- **Health Check**: `http://localhost:8000/health`
- **Documentação**: `http://localhost:8000/docs`

## 🎯 Funcionalidades Implementadas

### Chat Interface
- ✅ Interface de chat moderna com React
- ✅ WebSocket real-time integrado
- ✅ Mensagens de usuário e agente
- ✅ Status de conexão visual
- ✅ Indicadores de digitação
- ✅ Scroll automático
- ✅ Suporte a múltiplas sessões

### Spec Extractor
- ✅ Confirmação de confiança
- ✅ Dimensões extraídas (L x A x P)
- ✅ Material detectado
- ✅ Funcionalidade classificada
- ✅ Nível de complexidade
- ✅ Método de extração

### Histórico de Conversas
- ✅ Lista de sessões anteriores
- ✅ Filtros por status (ativas/concluídas)
- ✅ Contador de mensagens
- ✅ Última confiança média
- ✅ Timestamps formatados
- ✅ Navegação rápida

### Dashboard
- ✅ Status dos serviços em tempo real
- ✅ Métricas do sistema
- ✅ Ações rápidas
- ✅ Indicadores de saúde
- ✅ Links de navegação

### WebSocket Manager
- ✅ Conexão automática
- ✅ Reconexão inteligente
- ✅ Gestão de eventos
- ✅ Error handling
- ✅ Status tracking

## 🔄 Fluxo de Uso

1. **Dashboard** → Status do sistema e navegação
2. **Nova Conversa** → Cria `session_${timestamp}`
3. **Chat Interface** → Integração WebSocket
4. **Mensagem** → Envia via WebSocket para Minimax M2
5. **Resposta** → Processa e extrai especificações
6. **Confidence Score** → Avalia qualidade da extração
7. **Histórico** → Salva conversas para consulta

## 🛡️ Error Handling

### Níveis de Error Handling
1. **Component Level** - Error boundaries
2. **Hook Level** - WebSocket errors
3. **Service Level** - API failures
4. **Context Level** - State errors

### Estados de Loading
- `isLoading` - Carregamento geral
- `isTyping` - Agente digitando
- `connecting` - WebSocket conectando
- `error` - Estado de erro atual

### User Feedback
- Toast notifications
- Status indicators
- Error banners
- Loading spinners

## 🚀 Próximos Passos

### Sprint 4-5: 3D Model Generation
- Visualizador Three.js
- Integração NVIDIA NIM
- Preview de modelos
- Download de STL

### Sprint 6-7: Frontend Development
- Dashboard completo
- Sistema de projetos
- Upload de arquivos
- Mobile responsiveness

### Sprint 8-11: Features Avançadas
- Sistema de orçamentos
- Simulação de física
- Múltiplos usuários
- Analytics avançados

## 📱 Responsividade

### Breakpoints
- `sm` - 640px+ (Mobile)
- `md` - 768px+ (Tablet) 
- `lg` - 1024px+ (Desktop)
- `xl` - 1280px+ (Large)

### Mobile Features
- Touch-friendly buttons
- Swipe gestures (futuro)
- Responsive chat
- Mobile-optimized forms

## 🎨 Design System

### Cores
- **Primary**: Blue (`primary-500` = #3B82F6)
- **Success**: Green (`success-500` = #22C55E)
- **Warning**: Yellow (`warning-500` = #F59E0B)
- **Danger**: Red (`danger-500` = #EF4444)

### Typography
- **Headings**: `font-bold` + responsive sizes
- **Body**: `text-base` (16px) base
- **Captions**: `text-sm` (14px) subtle
- **Code**: `font-mono` monospace

### Spacing
- **Small**: `space-y-4` (16px)
- **Medium**: `space-y-6` (24px)  
- **Large**: `space-y-8` (32px)

## 📊 Performance

### Otimizações Implementadas
- Lazy loading de componentes
- Memoização de componentes pesados
- Debounce em inputs
- Throttle em eventos
- Virtual scrolling (futuro)

### Bundle Size
- **Vite** - HMR rápido
- **Tree shaking** automático
- **Code splitting** por rotas
- **Asset optimization** automática

---

**Status**: ✅ Sprint 2-3 Completo  
**Próximo**: Sprint 4-5 (3D Model Generation)  
**Autor**: MiniMax Agent  
**Data**: 2025-11-12 22:54:36