# 3dPot - Estrutura do Repositório

Este documento descreve a organização do repositório 3dPot após a reorganização estrutural.

> **📢 ATUALIZAÇÃO (Nov 2024):** Backend consolidado! Todos os endpoints (Modelagem + IoT) agora estão unificados em `backend/main.py` com routers em `backend/routers/`. A duplicação `backend/` vs `backend/app/` foi resolvida mantendo apenas modelos IoT específicos em `backend/app/models/` para evitar conflitos.

## 📋 Visão Geral

O repositório foi reorganizado para melhorar a clareza, manutenibilidade e facilitar o onboarding de novos contribuidores. A estrutura atual separa claramente código de produção, testes, scripts utilitários, documentação e artefatos gerados.

### 🎯 Mudanças Principais na Consolidação do Backend

- ✅ **Entry Point Único:** `backend/main.py` agora inclui TODAS as rotas (modelagem, simulação, IoT, etc.)
- ✅ **Routers Unificados:** Todos em `backend/routers/` (antes: backend/routes/ + backend/app/routers/)
- ✅ **Sem Duplicação:** Removidos arquivos backup (*_backup.py, *_original*.py)
- ✅ **Imports Consistentes:** Todos os módulos usam prefixo `backend.*`
- ✅ **Models Separados:** IoT models mantidos em `backend/app/models/` para evitar conflitos User/Project

## 📁 Estrutura de Diretórios

```
3dPot/
├── backend/                    # ✅ Backend Python UNIFICADO (Modelagem + IoT)
│   ├── main.py                # ✅ Entry point ÚNICO da aplicação
│   ├── routers/               # ✅ TODOS os endpoints consolidados
│   │   ├── auth.py           # Autenticação JWT
│   │   ├── conversational.py # IA conversacional (Minimax)
│   │   ├── modeling.py       # Modelagem 3D (CadQuery, OpenSCAD)
│   │   ├── simulation.py     # Simulação física (PyBullet)
│   │   ├── budgeting.py      # Orçamento inteligente
│   │   ├── devices.py        # IoT: Gerenciamento de dispositivos
│   │   ├── monitoring.py     # IoT: Monitoramento em tempo real
│   │   ├── alerts.py         # IoT: Sistema de alertas
│   │   ├── projects.py       # IoT: Gestão de projetos
│   │   ├── health.py         # Health checks
│   │   └── websocket.py      # WebSocket para tempo real
│   ├── models/               # Modelos SQLAlchemy
│   │   ├── __init__.py      # Modelos principais (User, Project, etc.)
│   │   ├── simulation.py    # Modelos de simulação
│   │   ├── budgeting.py     # Modelos de orçamento
│   │   ├── iot_device.py    # Modelos IoT específicos
│   │   ├── iot_alert.py
│   │   └── iot_sensor_data.py
│   ├── app/                  # ✅ MANTIDO: Modelos IoT específicos
│   │   └── models/          # User/Project IoT (evita conflito com modelos principais)
│   │       ├── user.py
│   │       ├── project.py
│   │       ├── device.py
│   │       ├── alert.py
│   │       └── sensor_data.py
│   ├── core/                 # Configurações centralizadas
│   │   └── config.py        # Settings e variáveis de ambiente
│   ├── services/             # Lógica de negócio (17 serviços)
│   │   ├── auth_service.py
│   │   ├── modeling_service.py
│   │   ├── simulation_service.py
│   │   ├── budgeting_service.py
│   │   ├── minimax_service.py
│   │   └── ...
│   ├── schemas/              # Schemas Pydantic para validação
│   ├── middleware/           # Middlewares (autenticação, CORS, etc.)
│   └── tests/                # Testes específicos do backend
│
├── frontend/                   # Frontend da aplicação
│   ├── src/                   # Código-fonte React/Vue
│   ├── demos/                 # Páginas HTML de demonstração
│   │   ├── demo_lgm_integrado.html
│   │   ├── modelagem-inteligente.html
│   │   └── workflow_dashboard.html
│   └── package.json
│
├── interface-web/              # Interface web alternativa
│   ├── src/                   # Código-fonte
│   ├── server/                # Servidor web
│   └── monitoring/            # Monitoramento da interface
│
├── tests/                      # Testes principais do projeto
│   ├── integration/           # Testes de integração
│   │   ├── test_integration.py
│   │   ├── test_integration_core.py
│   │   ├── test_integration_final.py
│   │   ├── test_minimax_service.py
│   │   ├── teste_endpoint_lgm.py
│   │   └── teste_integracao_completa.py
│   └── unit/                  # Testes unitários
│       ├── test_3d_models.py
│       ├── test_arduino/
│       ├── test_esp32/
│       └── test_raspberry_pi/
│
├── scripts/                    # Scripts utilitários
│   ├── validacao/             # Scripts de validação
│   │   ├── validate_openscad_models.py
│   │   ├── syntax_validator.py
│   │   ├── quick_openscad_check.py
│   │   ├── improved_validator.py
│   │   └── fix_code_quality.py
│   ├── dados/                 # Geração de dados
│   │   └── generate_sample_data.py
│   ├── monitoramento/         # Monitoramento do sistema
│   │   ├── workflow_monitor.py
│   │   └── optimize_workflows.py
│   ├── demos/                 # Scripts de demonstração
│   │   ├── demonstracao_sistema.py
│   │   ├── lgm_integration_example.py
│   │   ├── sistema_modelagem_lgm_integrado.py
│   │   ├── slant3d_integration.py
│   │   ├── servidor_integracao.py
│   │   ├── test-auth-system.py
│   │   ├── teste-minimax-standalone.py
│   │   ├── teste-rapido-minimax.py
│   │   ├── teste-sistema-modelagem-sprint3.py
│   │   └── teste-standalone-sprint3.py
│   ├── start-sprint1.sh       # Scripts de inicialização
│   ├── start-sprint2.py
│   ├── deploy-sprint7.sh
│   └── performance_monitor.py
│
├── docs/                       # Documentação do projeto
│   ├── sprints/               # Documentação de sprints (21 arquivos)
│   │   ├── SPRINT1-*.md
│   │   ├── SPRINT2-*.md
│   │   ├── PLANO-SPRINT*.md
│   │   └── TAREFA-SPRINT*.md
│   ├── relatorios/            # Relatórios de desenvolvimento (35 arquivos)
│   │   ├── RELATORIO-*.md
│   │   ├── RESUMO-*.md
│   │   ├── ENTREGA-*.md
│   │   └── DASHBOARD-*.md
│   ├── validacao/             # Relatórios de validação (18 arquivos)
│   │   ├── CI_*.md
│   │   ├── VALIDATION_*.md
│   │   └── E2E-TEST-EXECUTION-REPORT.md
│   ├── arquitetura/           # Documentação arquitetural (11 arquivos)
│   │   ├── ARQUITETURA-3DPOT-EVOLUTIVA.md
│   │   ├── PLANO_EXECUCAO_3DPOT.md
│   │   ├── TODO.md
│   │   └── TEMPLATES_FERRAMENTAS_PRATICAS.md
│   ├── guias/                 # Guias e tutoriais (13 arquivos)
│   │   ├── README-IMPLEMENTACAO.md
│   │   ├── README-MODELAGEM-INTELIGENTE.md
│   │   ├── GUIA-*.md
│   │   └── exemplo-uso-endpoint-integrado.md
│   ├── architecture/          # Documentação de arquitetura detalhada
│   ├── installation/          # Guias de instalação
│   └── planning/              # Planejamento e roadmaps
│
├── outputs/                    # Artefatos gerados (ignorado pelo git)
│   ├── relatorios/            # Relatórios JSON
│   │   ├── final_validation_report.json
│   │   ├── quick_validation_report.json
│   │   ├── syntax_validation_report.json
│   │   └── validation_report.json
│   ├── workflows_status.json
│   └── workspace.json
│
├── external_api/               # Integrações com APIs externas
│   ├── data_sources/          # Fontes de dados externas
│   └── function_utils.py
│
├── modelos-3d/                 # Arquivos de modelos 3D
│   ├── openscad/
│   └── stl/
│
├── monitoring/                 # Monitoramento da aplicação
├── nginx/                      # Configuração NGINX
├── assets/                     # Recursos estáticos
├── projetos/                   # Projetos de exemplo
├── publicacoes/                # Publicações e artigos
│
├── .github/                    # Workflows GitHub Actions
├── .gitignore                  # Arquivos ignorados pelo Git
├── docker-compose.yml          # Configuração Docker
├── docker-compose.dev.yml      # Configuração Docker para desenvolvimento
├── requirements.txt            # Dependências Python
├── requirements-test.txt       # Dependências de teste
├── pyproject.toml             # Configuração do projeto Python
├── pytest.ini                 # Configuração do pytest
├── setup-3dpot.sh             # Script de setup
├── run_tests.sh               # Script para executar testes
├── README.md                  # Documentação principal
├── CHANGELOG.md               # Registro de mudanças
├── CODE_OF_CONDUCT.md         # Código de conduta
├── CONTRIBUTING.md            # Guia de contribuição
└── STRUCTURE.md               # Este arquivo
```

## 🎯 Principais Mudanças

### 1. Documentação Organizada
- **96 arquivos markdown** movidos da raiz para subdiretórios organizados em `docs/`
- Separação clara entre sprints, relatórios, validação, arquitetura e guias
- Mantidos apenas README.md, CHANGELOG.md, CODE_OF_CONDUCT.md e CONTRIBUTING.md na raiz

### 2. Testes Consolidados
- **7 arquivos de teste de integração** movidos para `tests/integration/`
- **5 scripts de teste/demo** movidos para `scripts/demos/`
- Estrutura de testes agora segue padrão pytest consistente

### 3. Scripts Organizados
- **5 scripts de validação** em `scripts/validacao/`
- **1 script de dados** em `scripts/dados/`
- **2 scripts de monitoramento** em `scripts/monitoramento/`
- **10 scripts de demonstração** em `scripts/demos/`
- Scripts de startup organizados em `scripts/`

### 4. Outputs Separados
- **6 arquivos JSON de relatórios** movidos para `outputs/`
- Diretório `outputs/` adicionado ao `.gitignore`
- Artefatos gerados não mais poluem o repositório

### 5. Frontend Organizado
- **3 arquivos HTML de demonstração** movidos para `frontend/demos/`
- Separação clara entre aplicação principal e demos

## 🚀 Como Usar

### Executar Testes
```bash
# Todos os testes
pytest

# Apenas testes de integração
pytest tests/integration/

# Apenas testes unitários
pytest tests/unit/
```

### Executar Scripts de Validação
```bash
# Validar modelos OpenSCAD
python scripts/validacao/validate_openscad_models.py

# Validar sintaxe
python scripts/validacao/syntax_validator.py
```

### Executar Scripts de Demonstração
```bash
# Demonstração do sistema
python scripts/demos/demonstracao_sistema.py

# Exemplo de integração LGM
python scripts/demos/lgm_integration_example.py
```

### Monitoramento
```bash
# Monitorar workflows
python scripts/monitoramento/workflow_monitor.py

# Otimizar workflows
python scripts/monitoramento/optimize_workflows.py
```

## 📚 Navegação na Documentação

- **Para entender a arquitetura**: veja `docs/arquitetura/ARQUITETURA-3DPOT-EVOLUTIVA.md`
- **Para implementação**: veja `docs/guias/README-IMPLEMENTACAO.md`
- **Para histórico de sprints**: navegue em `docs/sprints/`
- **Para relatórios de progresso**: navegue em `docs/relatorios/`
- **Para validação e CI**: navegue em `docs/validacao/`

## 🔄 Migração para Novos Contribuidores

Se você tinha branches ou trabalho em andamento baseado na estrutura antiga:

1. **Atualize sua branch local**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Atualize imports em seus arquivos Python**:
   - Testes: se você importava de arquivos na raiz, agora eles estão em `tests/integration/` ou `scripts/`
   - Scripts: caminhos relativos podem ter mudado

3. **Atualize referências a documentação**:
   - Documentos markdown agora estão em subdiretórios de `docs/`
   - Links relativos em markdown podem precisar de ajuste

4. **Arquivos de saída**:
   - Se você gerava relatórios JSON, agora devem ir para `outputs/`
   - O diretório `outputs/` é ignorado pelo git

## 📝 Notas Importantes

- O diretório `outputs/` **não é versionado** no Git - é apenas para artefatos locais
- Testes agora são descobertos automaticamente pelo pytest em `tests/`
- Scripts de demonstração não devem ser usados em produção
- Documentação de sprints é histórica e mantida para referência

## 🤝 Contribuindo

Ao contribuir com o projeto:

1. **Novos testes**: coloque em `tests/integration/` ou `tests/unit/`
2. **Novos scripts**: coloque na subpasta apropriada de `scripts/`
3. **Nova documentação**: coloque na subpasta apropriada de `docs/`
4. **Relatórios gerados**: configure para salvar em `outputs/` (não versionado)

Para mais detalhes, veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📧 Contato

Para questões sobre a estrutura do repositório ou migração de código, abra uma issue no GitHub.
