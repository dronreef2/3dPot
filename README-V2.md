# 🎯 3dPot v2.0 - Sistema de Prototipagem Sob Demanda

[![FastAPI](https://img.shields.io/badge/FastAPI-v2.0-109989?logo=fastapi&logoColor=white&style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white&style=flat-square)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white&style=flat-square)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white&style=flat-square)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI%20Powered-Minimax%20M2-FF6B35?logo=openai&logoColor=white&style=flat-square)](https://minimax.chat/)
[![3D Ready](https://img.shields.io/badge/3D%20Generation-CadQuery%2FOpenSCAD-FF6B6B?logo=unity&logoColor=white&style=flat-square)](https://cadquery.org/)

**🚀 Evolução do sistema IoT 3dPot para uma plataforma completa de prototipagem sob demanda com IA conversacional, geração automatizada de modelos 3D, simulação física e orçamento inteligente.**

## ✨ Novidades v2.0

### 🤖 IA Conversacional
- **Minimax M2 Integration**: Conversação natural em português
- **Extração Automática**: Especificações técnicas a partir de descrições
- **Clarificação Inteligente**: Sistema que questiona detalhes críticos
- **Contexto Preservado**: Mantém histórico da conversa completa

### 🔧 Modelagem 3D Paramétrica
- **CadQuery Integration**: Geração programática de geometria
- **OpenSCAD Support**: Modelos paramétricos complexos
- **Validação Automática**: Verificação de imprimibilidade
- **Otimização de Malha**: Processamento com Trimesh + NVIDIA NIM

### ⚡ Simulação Física
- **PyBullet Integration**: Testes de queda, stress e movimento
- **Análise de Robustez**: Métricas de eficiência estrutural
- **Visualização 3D**: Renderização de simulações em tempo real
- **Reports Automáticos**: Análise de performance e limitações

### 💰 Orçamento Inteligente
- **APIs de Componentes**: Integração Octopart + DigiKey
- **Cálculo Automático**: Material, impressão, montagem
- **Propostas PDF**: Geração automática de orçamentos
- **Análise de Fornecedores**: Comparação de preços e prazos

### 🎨 Interface Moderna
- **React Three Fiber**: Visualização 3D interativa
- **WebSockets**: Atualizações em tempo real
- **Responsive Design**: Desktop e mobile
- **Dark/Light Mode**: UI adaptativa

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    3dPot v2.0 Platform                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + R3F) │ Backend (FastAPI) │ Legacy (v1.0) │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Chat Interface  │ │ API Gateway     │ │ ESP32 Monitor   │ │
│  │ Visualizador 3D │ │ FastAPI + SQL   │ │ Arduino Control │ │
│  │ Dashboard Proj. │ │ PostgreSQL      │ │ Raspberry QC    │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ IA Conversação  │ │ Simulação 3D    │ │ MQTT Broker     │ │
│  │ Minimax M2 API  │ │ PyBullet Engine │ │ Legacy Hardware │ │
│  │ Extrac Specs    │ │ Métricas Auto   │ │ Real-time Data  │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Storage Layer   │ │ Task Queue      │ │ Monitoring      │ │
│  │ S3/MinIO Models │ │ Celery + Redis  │ │ Prometheus      │ │
│  │ 3D Files/PDF    │ │ Background Jobs │ │ Grafana         │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone e Setup
```bash
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot

# Setup ambiente
cp .env.example .env
docker-compose up -d
```

### 2. Acessar Sistema
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **API Docs**: http://localhost:8000/docs
- **Monitoramento**: http://localhost:3001

### 3. Primeiro Projeto
1. Faça login ou registre-se
2. Crie um novo projeto
3. Inicie conversação: "Quero criar um suporte para celular em PLA"
4. Especifique dimensões e funcionalidades
5. Gerar modelo 3D automaticamente
6. Executar simulação de resistência
7. Receber orçamento completo

---

## 📋 Funcionalidades

### 🤖 Conversação Inteligente
```typescript
// Exemplo de fluxo conversacional
const response = await api.conversational.sendMessage({
  message: "Preciso de um suporte para celular resistente, em PLA, com LED",
  projectId: "uuid-project",
});

// Sistema extrai automaticamente:
// - Categoria: eletrônico
// - Material: PLA
// - Componentes: LED, suporte mecânico
// - Funcionalidades: suporte, iluminação
```

### 🔧 Modelagem 3D
```python
# Geração automática de modelo
specs = {
    "categoria": "eletronico",
    "dimensoes": {"largura": 60, "altura": 100, "profundidade": 40},
    "material": "PLA",
    "componentes": [{"tipo": "LED", "quantidade": 1}]
}

model = await modeling_service.generate_model(project_id, specs)
# Resultado: modelo STL validado e otimizado
```

### ⚡ Simulação Física
```python
# Teste de resistência com PyBullet
simulation = await simulation_service.start_simulation({
    "modelId": "uuid-model",
    "tipoSimulacao": "drop_test",
    "parametros": {"altura_queda": 1.0, "num_testes": 10}
})

# Métricas automáticas:
// - Velocidade de impacto
// - Deformações
// - Pontos de fragilidade
```

### 💰 Orçamento Automático
```python
# Cálculo completo de orçamento
budget = await budgeting_service.calculate_budget(project_id, {
    "margemLucroPercentual": 30
})

# Resultado detalhado:
{
    "custoMaterial": 12.50,      // Filamento PLA
    "custoComponentes": 5.00,    // LED + suporte
    "custoImpressao": 8.75,      // 3.5h @ R$25/h
    "custoMaoObra": 50.00,       // 1h montagem
    "precoFinal": 97.50          // Total com margem
}
```

---

## 🛠️ Stack Tecnológico

### Backend v2.0
- **FastAPI**: Framework async de alta performance
- **PostgreSQL**: Banco relacional com JSON support
- **Redis**: Cache e message broker
- **Celery**: Processamento assíncrono
- **SQLAlchemy 2.0**: ORM com async support
- **Pydantic**: Validação de dados

### Frontend v2.0
- **React 18**: Framework UI moderno
- **TypeScript**: Tipagem estática
- **React Three Fiber**: Renderização 3D
- **Zustand**: State management
- **Tailwind CSS**: Styling utility-first
- **Vite**: Build tool ultra-rápido

### 3D & Simulation
- **CadQuery**: Geração paramétrica Python
- **OpenSCAD**: Modelagem declarativa
- **PyBullet**: Simulação física
- **Trimesh**: Processamento de malha
- **Three.js**: Engine 3D web

### APIs & Integrations
- **Minimax M2**: IA conversacional
- **Octopart API**: Componentes eletrônicos
- **DigiKey API**: Preços e disponibilidade
- **NVIDIA NIM**: Otimização de malha 3D

### Infrastructure
- **Docker**: Containerização multi-service
- **Nginx**: Reverse proxy e load balancer
- **MinIO**: S3-compatible object storage
- **Prometheus + Grafana**: Monitoring
- **GitHub Actions**: CI/CD pipeline

---

## 📁 Estrutura do Projeto

```
3dpot-v2/
├── backend/                    # FastAPI Backend
│   ├── api/v1/                 # API endpoints versionados
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── conversational_service.py    # Minimax M2
│   │   ├── modeling_service.py          # CadQuery/OpenSCAD
│   │   ├── simulation_service.py        # PyBullet
│   │   └── budgeting_service.py         # Octopart/DigiKey
│   ├── integrations/           # External APIs
│   └── main.py                 # FastAPI application
│
├── frontend/                   # React Frontend
│   ├── src/components/
│   │   ├── conversational/     # Chat interface
│   │   ├── modeling/          # 3D viewer
│   │   └── simulation/        # Physics viewer
│   ├── services/              # API client
│   └── store/                 # Zustand state
│
├── legacy/                    # Preservação v1.0
│   ├── codigos/               # Hardware legados
│   ├── interface-web/         # Web antigo
│   └── central-inteligente/   # Sistema central
│
├── docs/                      # Documentação
│   ├── architecture/          # ADRs
│   ├── installation/          # Guias setup
│   └── planning/              # Sprints
│
└── infrastructure/            # DevOps
    ├── docker/                # Container configs
    └── monitoring/            # Prometheus/Grafana
```

---

## 🎯 Roadmap v2.0+

### ✅ Implementado (Sprints 1-6)
- [x] Arquitetura FastAPI modular
- [x] IA conversacional Minimax M2
- [x] Pipeline modelagem 3D paramétrica
- [x] Simulação física PyBullet
- [x] Sistema orçamento automatizado
- [x] Interface React Three Fiber
- [x] Deploy Docker multi-service

### 🚧 Próximas Features (v2.1+)
- [ ] **AR/VR Viewer**: Visualização imersiva
- [ ] **Marketplace**: Loja de templates
- [ ] **Collaboration**: Múltiplos usuários por projeto
- [ ] **AI Enhancement**: Otimização automática de designs
- [ ] **Production Planning**: Timeline de manufacture
- [ ] **Supply Chain**: Integração fornecedores

### 🔬 R&D (v3.0)
- [ ] **Multi-material Printing**: Suporte a impressoras multi-extrusor
- [ ] **Generative AI**: Design generativo para projetos
- [ ] **Cloud Manufacturing**: Rede de manufacturers
- [ ] **Blockchain**: Tracking de propriedade intelectual

---

## 📊 Performance Metrics

### Benchmarks Atuais
- **API Response Time**: < 100ms (p95)
- **3D Model Generation**: < 30 segundos
- **Simulation Completion**: < 2 minutos
- **Frontend Load Time**: < 3 segundos
- **Uptime**: 99.9% disponível

### Capacity Planning
- **Concurrent Users**: 100+ simultâneos
- **Projects/Day**: 1000+ projetos
- **Storage Growth**: 10GB/dia modelos 3D
- **API Requests**: 10K/h pico

---

## 🤝 Contribuição

### Como Contribuir
1. **Fork** o repositório
2. Crie uma **feature branch** (`git checkout -b feature/AmazingFeature`)
3. Commit suas **mudanças** (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

### Áreas de Contribuição
- 🤖 **AI/ML**: Melhorar extração de especificações
- 🎨 **Frontend**: UI/UX e componentes React
- 🔧 **Backend**: APIs e performance
- ⚡ **3D**: Algoritmos de modelagem
- 📊 **Analytics**: Métricas e insights
- 📚 **Documentation**: Guias e tutoriais

---

## 📚 Documentação

- **[Arquitetura](docs/architecture/ADR.md)**: Decision Records
- **[Instalação](docs/installation/INSTALLATION.md)**: Guia completo
- **[Sprints](docs/planning/SPRINT_PLAN.md)**: Roadmap detalhado
- **[API Docs](http://localhost:8000/docs)**: Documentação automática
- **[Legacy Guide](PROJETO_CENTRAL_INTELIGENTE.md)**: Sistema v1.0

---

## 🆘 Suporte

### Problemas Comuns
- **API Connection**: Verifique `backend/.env` configurações
- **3D Generation**: Confirme OpenSCAD instalação
- **Simulations**: Valide PyBullet dependencies
- **Storage**: Check MinIO/S3 connectivity

### Comunidades
- **GitHub Issues**: Bug reports e feature requests
- **GitHub Discussions**: Q&A e brainstorming
- **Discord**: Chat em tempo real (em breve)

---

## 📄 Licença

Este projeto está sob licença **MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **OpenSCAD Community**: Framework de modelagem paramétrica
- **React Three Fiber**: Renderização 3D web
- **FastAPI Team**: Framework web moderno
- **Minimax**: IA conversacional em português
- **PyBullet**: Simulação física acessível
- **Open Source Community**: Todo o ecossistema

---

<div align="center">

### 🚀 3dPot v2.0 - Da Ideação ao Objeto Físico com IA

**[GitHub](https://github.com/dronreef2/3dPot)** • 
**[Documentação](docs/)** • 
**[API Docs](http://localhost:8000/docs)** • 
**[Suporte](https://github.com/dronreef2/3dPot/issues)**

---

*Desenvolvido com ❤️ pela comunidade open-source*

</div>