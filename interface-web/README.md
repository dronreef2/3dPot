# 3dPot Control Center - Interface Web Mobile Responsiva

Sistema de controle centralizado e responsivo para o projeto 3dPot, integrando os 3 dispositivos de hardware através de uma interface web moderna e intuitiva.

## 🚀 Características Principais

### 📱 Design Mobile-First
- Interface totalmente responsiva para smartphones, tablets e desktop
- Layout adaptativo com navegação otimizada para touch
- PWA (Progressive Web App) para instalação em dispositivos móveis
- Tema claro/escuro automático com sistema de preferências

### 🖥️ Dashboard Unificado
- **Monitor ESP32 Filamento**: Monitoramento em tempo real de peso, temperatura e bateria
- **Esteira Arduino**: Controle de velocidade, direção e modo de operação
- **Estação QC**: Inspeção automática por IA com classificação A/B/C/D/F

### 📊 Analytics e Relatórios
- Gráficos interativos com Chart.js
- Relatórios automáticos em PDF, CSV e JSON
- Análise de tendências de qualidade e produção
- Estatísticas detalhadas por dispositivo

### 🔄 Comunicação em Tempo Real
- WebSocket para atualizações instantâneas
- Notificações push para alertas críticos
- Controle remoto de todos os dispositivos
- Sincronização automática de dados

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18** + **TypeScript** - Interface de usuário moderna
- **Vite** - Build tool otimizado e rápido
- **Tailwind CSS** - Framework CSS utilitário
- **Chart.js** - Gráficos interativos responsivos
- **Framer Motion** - Animações fluidas
- **Socket.io Client** - Comunicação em tempo real

### Backend
- **Node.js** + **Express** - Servidor API
- **Socket.io** - WebSocket server
- **SQLite** - Banco de dados local
- **PDFKit** - Geração de relatórios PDF

### Funcionalidades Avançadas
- **PWA** com service worker
- **WebSocket** para tempo real
- **Context API** para gerenciamento de estado
- **Custom hooks** para lógica reutilizável
- **Responsive design** mobile-first

## 📦 Instalação e Configuração

### Pré-requisitos
- Node.js 16+ 
- npm ou yarn
- Git

### 1. Clonar e Instalar Dependências
```bash
# Frontend
cd interface-web
npm install

# Backend
cd server
npm install
```

### 2. Executar em Desenvolvimento
```bash
# Terminal 1 - Frontend (porta 3000)
cd interface-web
npm run dev

# Terminal 2 - Backend (porta 5000)
cd server
npm run dev
```

### 3. Build para Produção
```bash
# Frontend
cd interface-web
npm run build

# Backend
cd server
npm start
```

## 🎯 Estrutura do Projeto

```
interface-web/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── DeviceCard.tsx   # Cards de dispositivos
│   │   ├── Charts/          # Gráficos responsivos
│   │   ├── Navigation/      # Menu mobile
│   │   └── Layout.tsx       # Layout principal
│   ├── pages/               # Páginas principais
│   │   ├── Dashboard.tsx    # Dashboard principal
│   │   ├── FilamentMonitor.tsx
│   │   ├── ConveyorControl.tsx
│   │   ├── QCStation.tsx
│   │   ├── Settings.tsx
│   │   └── Reports.tsx
│   ├── hooks/               # Custom hooks
│   ├── services/            # APIs e WebSocket
│   ├── contexts/            # React contexts
│   ├── types/               # TypeScript types
│   └── utils/               # Utilitários
├── server/                  # Backend Node.js
│   ├── routes/              # API routes
│   ├── socket.js            # WebSocket handlers
│   ├── database.js          # Database operations
│   └── index.js             # Servidor principal
├── public/                  # Assets estáticos
└── dist/                    # Build de produção
```

## 📱 Funcionalidades por Dispositivo

### 🧵 Monitor ESP32 Filamento
- **Leitura em tempo real**: Peso, temperatura, umidade
- **Controle de energia**: Modo deep sleep, calibração
- **Alertas personalizados**: Limites configuráveis
- **Histórico visual**: Gráficos de consumo ao longo do tempo
- **Estimativas**: Tempo restante baseado no consumo

### 🏭 Esteira Arduino Transportadora
- **Controle manual**: Velocidade, direção, start/stop
- **Modo automático**: Operação autônoma programável
- **Monitoramento**: Posição, carga, temperatura do motor
- **Segurança**: Parada de emergência, sensores de proteção
- **Diagnóstico**: Status LED, comunicação, falhas

### 🔍 Estação QC Raspberry Pi
- **IA de inspeção**: Detecção automática de defeitos
- **Classificação**: Sistema A/B/C/D/F com confiança
- **Análise estatística**: Tendências, padrões, eficiência
- **Relatórios automáticos**: PDF, CSV, análise detalhada
- **Interface visual**: LED indicators, dashboard em tempo real

## 🔧 API Endpoints

### Dispositivos
- `GET /api/devices` - Status de todos os dispositivos
- `GET /api/devices/:type` - Status de dispositivo específico
- `PUT /api/devices/:type/config` - Configurar dispositivo
- `POST /api/devices/:type/control` - Controlar dispositivo
- `GET /api/devices/:type/health` - Verificar saúde

### QC Station
- `POST /api/qc/inspect` - Executar inspeção
- `GET /api/qc/statistics` - Estatísticas de qualidade
- `GET /api/qc/inspections` - Histórico de inspeções
- `GET /api/qc/report` - Gerar relatório

### Analytics
- `GET /api/analytics/production` - Dados de produção
- `GET /api/analytics/quality` - Análise de qualidade
- `GET /api/analytics/devices` - Performance dos dispositivos
- `GET /api/analytics/overview` - Visão geral do sistema

## 🌐 WebSocket Events

### Cliente → Servidor
- `request_device_status` - Solicitar status dos dispositivos
- `device_control` - Enviar comando para dispositivo
- `acknowledge_alert` - Reconhecer alerta
- `subscribe_device` - Inscrever-se em updates de dispositivo

### Servidor → Cliente
- `device_update` - Atualização de status do dispositivo
- `alert` - Novo alerta do sistema
- `command_response` - Resposta de comando
- `heartbeat` - Pulsação de conexão

## 📊 Recursos de UI/UX

### Design System
- **Paleta de cores**: Sistema de cores semânticas (primary, success, warning, error)
- **Tipografia**: Inter font com escala responsiva
- **Espaçamento**: Sistema de espaçamento consistente
- **Componentes**: Library de componentes reutilizáveis

### Responsividade
- **Mobile first**: Design otimizado para dispositivos móveis
- **Breakpoints**: xs (320px), sm (640px), md (768px), lg (1024px), xl (1280px)
- **Grid system**: Flexbox e CSS Grid para layouts
- **Touch friendly**: Botões e controles otimizados para toque

### Interações
- **Animações**: Framer Motion para transições fluidas
- **Loading states**: Indicadores de carregamento
- **Error handling**: Tratamento gracioso de erros
- **Toast notifications**: Feedback visual para ações

## 🔐 Segurança e Performance

### Segurança
- **CORS** configurado adequadamente
- **Helmet** para headers de segurança
- **Input validation** em todos os endpoints
- **Rate limiting** para APIs críticas

### Performance
- **Code splitting** automático
- **Lazy loading** de componentes
- **Service Worker** para cache
- **Compression** gzip habilitado
- **Database indexing** para queries otimizadas

## 🚀 Deployment

### Ambiente de Desenvolvimento
```bash
# Instalar dependências
npm install

# Executar desenvolvimento
npm run dev
```

### Ambiente de Produção
```bash
# Build frontend
npm run build

# Build e iniciar backend
npm run start
```

### Docker (Opcional)
```dockerfile
# Dockerfile example
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 5000
CMD ["npm", "start"]
```

## 🧪 Testes

### Testes Unitários
```bash
npm run test
```

### Testes E2E
```bash
npm run test:e2e
```

### Linting
```bash
npm run lint
```

## 📝 Documentação Adicional

- **TypeScript Types**: `src/types/index.ts`
- **API Documentation**: Disponível em `/api/docs` quando servidor ativo
- **Component Stories**: Documentação interativa de componentes
- **WebSocket Protocol**: Especificação de eventos em `server/socket.js`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🎉 Conclusão

A Interface Web Mobile Responsiva do 3dPot oferece uma solução completa e moderna para o controle e monitoramento dos dispositivos de hardware, proporcionando:

- ✅ **Experiência de usuário excepcional** em todos os dispositivos
- ✅ **Integração em tempo real** com os 3 sistemas de hardware
- ✅ **Análise avançada** com gráficos e relatórios profissionais
- ✅ **Escalabilidade** para futuras expansões do projeto
- ✅ **Manutenibilidade** com código TypeScript bem estruturado

O sistema está pronto para deployment e uso em ambiente de produção, oferecendo uma base sólida para o ecossistema 3dPot! 🚀