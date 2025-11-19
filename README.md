# 🎯 3dPot - Sistema de Prototipagem Sob Demanda v4.0

[![CI Pipeline](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/ci.yml?label=CI%20Pipeline&style=flat-square)](https://github.com/dronreef2/3dPot/actions/workflows/ci.yml)
[![Python Tests](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/python-tests.yml?label=Python%20Tests&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![Code Quality](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/code-quality.yml?label=Code%20Quality&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-80%25-green?style=flat-square)](https://github.com/dronreef2/3dPot)
[![Tests](https://img.shields.io/badge/tests-445%20passing-success?style=flat-square)](https://github.com/dronreef2/3dPot)
[![3D Models](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/openscad.yml?label=3D%20Models&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![Arduino Build](https://img.shields.io/github/actions/workflow/status/dronreef2/3dPot/arduino-build.yml?label=Arduino%20Build&style=flat-square)](https://github.com/dronreef2/3dPot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API%20Backend-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-red.svg)](https://redis.io/)
[![Total Commits](https://img.shields.io/github/commit-activity/w/dronreef2/3dPot)](https://github.com/dronreef2/3dPot/graphs/commit-activity)
[![Open Issues](https://img.shields.io/github/issues/dronreef2/3dPot)](https://github.com/dronreef2/3dPot/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed/dronreef2/3dPot)](https://github.com/dronreef2/3dPot/issues?q=is%3Aissue+is%3Aclosed)

**Ecossistema completo de prototipagem: Hardware IoT + Backend de IA para automação e design sob demanda.**

> 📚 **Nota sobre a Estrutura do Repositório**: Este repositório foi reorganizado em novembro de 2024 para melhor organização e manutenibilidade. Consulte [STRUCTURE.md](STRUCTURE.md) para detalhes da nova estrutura e [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) se você tem código em desenvolvimento.

## 🚀 Quick Start

### Setup em 5 Minutos

```bash
# 1. Clone o repositório
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot

# 2. Execute o script de setup automatizado
./setup-3dpot.sh

# 3. Configure as variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações

# 4. Inicie o backend
cd backend
python -m uvicorn main:app --reload

# 5. Acesse a documentação da API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Comandos Principais

```bash
# Rodar todos os testes (445 testes)
./run_tests.sh

# Rodar apenas testes unitários (391 testes)
pytest tests/unit/ -v

# Rodar testes de integração
pytest tests/integration/ -v

# Rodar testes E2E (20 testes)
pytest tests/e2e/ -v

# Rodar testes da CLI (34 testes)
pytest tests/unit/cli/ -v

# Verificar cobertura (threshold: 70%)
pytest tests/unit/ --cov=backend --cov-report=html --cov-fail-under=70

# Iniciar backend em modo desenvolvimento
cd backend && python -m uvicorn main:app --reload --port 8000
```

### Estrutura de Diretórios Principais

```
3dPot/
├── backend/          # ✅ API REST unificada (Modelagem + IoT)
│   ├── main.py       # Entry point único
│   ├── routers/      # Todos os endpoints consolidados
│   ├── models/       # Modelos SQLAlchemy
│   └── services/     # Lógica de negócio (17 serviços)
├── docs/             # 📚 Documentação completa
│   └── arquitetura/  # Relatórios Sprint 1-4
├── scripts/          # 🛠️ Scripts auxiliares
│   └── cli/          # CLI unificada (13 comandos)
├── tests/            # 🧪 445 testes (80% de cobertura)
│   ├── unit/         # 391 testes unitários
│   ├── integration/  # Testes de integração
│   ├── e2e/          # 20 testes E2E
│   └── cli/          # 34 testes da CLI
└── codigos/          # 💻 Firmware IoT (ESP32, Arduino, RPi)
```

## 🔥 **ATUALIZAÇÃO SPRINT 4 - QUALIDADE E CI/CD APRIMORADOS**

### 📊 Sprint 4 - Novembro 2025

**Foco:** Expansão de testes, integração CI/CD com coverage, e testes de CLI

✅ **200 novos testes unitários** para serviços secundários (391 total)  
✅ **11 novos testes E2E** cobrindo 5 fluxos adicionais (20 total)  
✅ **34 testes da CLI unificada** cobrindo parsing, roteamento e comandos  
✅ **CI/CD aprimorado** com threshold de coverage (70%) e job E2E  
✅ **80% de cobertura** de código estimada (+8pp vs Sprint 3)  

**📖 Documentação:** [Sprint 4 - Relatório Completo](docs/arquitetura/SPRINT4-QUALIDADE-CI-CLI-RELATORIO.md)

### Métricas de Qualidade

| Métrica | Sprint 3 | Sprint 4 | Melhoria |
|---------|----------|----------|----------|
| Testes Unitários | 191 | 391 | +105% |
| Testes E2E | 9 | 20 | +122% |
| Testes CLI | 0 | 34 | Novo! |
| **Total** | **212** | **445** | **+110%** |
| Cobertura | ~72% | ~80% | +8pp |
| CI Jobs | 1 | 2 | +E2E |

## 🔥 **ATUALIZAÇÃO SPRINT 1 - PROBLEMAS CRÍTICOS RESOLVIDOS**

**Data:** 2025-11-12  
**Score Anterior:** 6.5/10  
**Score Atual:** 7.8/10 (+1.3 pontos)

### ✅ **Problemas Críticos Resolvidos:**

1. **🔴 Requirements-test.txt AUSENTE** → ✅ **CRIADO E COMPLETO**
   - 63 dependências de teste incluídas
   - Framework pytest, cobertura, hardware mocks
   - Bibliotecas de linting e qualidade

2. **🔴 Credenciais Hardcoded ESP32** → ✅ **CONFIGURAÇÃO SEGURA IMPLEMENTADA**
   - `config.example.h` criado como template
   - `.gitignore` atualizado para proteger configs
   - Sistema de fallback Access Point

3. **🔴 Modelos 3D não Paramétricos** → ✅ **MODELO AVANÇADO CRIADO**
   - `universal-case-parametric.scad` (431 linhas)
   - 25+ parâmetros customizáveis
   - Documentação completa incluída

4. **🔴 Código-fonte Incompleto** → ✅ **CÓDIGO MELHORADO E ESTRUTURADO**
   - ESP32: 826 linhas com segurança
   - Arduino: Estrutura melhorada
   - Raspberry Pi: Configuração completa
   - Todos com arquivos de configuração

### 🚀 **Melhorias Implementadas:**
- **Segurança:** Sistema de configuração separado
- **Manutenibilidade:** Documentação extensa
- **Flexibilidade:** Modelos 3D totalmente paramétricos
- **Qualidade:** Estrutura de código robusta

## Visão Geral

O **3dPot** é um ecossistema completo que integra duas verticais principais:

### 🌐 **Backend API v2.0** (Sistema de Prototipagem Sob Demanda)
API REST completa baseada em FastAPI com inteligência artificial para automação de design 3D, simulação física e orçamentos inteligentes.

### 📡 **Frontend IoT** (Automação de Impressão 3D)  
Soluções hardware completas com ESP32, Arduino e Raspberry Pi para monitoramento, transporte e controle de qualidade em impressão 3D.

**Integração total:** O backend processa e otimiza projetos 3D via IA, enquanto o frontend físico coleta dados de produção em tempo real.

## 🏗️ Arquitetura do Sistema

### 📊 **Visão Geral da Arquitetura**
![Arquitetura 3dPot v2.0](assets/screenshots/arquitetura-3dpot-v2.png)
*Sistema completo: Backend FastAPI + Frontend IoT integrados*

### 🌐 **Backend API v2.0** (FastAPI + PostgreSQL + Redis)

#### **Sprints Implementados:**
- ✅ **Sprint 1:** Sistema de Autenticação JWT completo
- ✅ **Sprint 2:** Sistema Conversacional com IA Minimax  
- ✅ **Sprint 3:** Sistema de Modelagem 3D (CadQuery + Trimesh)
- ✅ **Sprint 4:** Sistema de Simulação Física (PyBullet)
- ✅ **Sprint 5:** Sistema de Orçamento Inteligente

#### **Tecnologias Backend:**
```
🔧 FastAPI         - Framework web assíncrono
🗄️ PostgreSQL      - Banco de dados principal  
🔄 Redis           - Cache e broker de tarefas
🤖 Minimax AI      - Integração conversacional
🔐 JWT             - Sistema de autenticação
⚡ Celery          - Processamento assíncrono
📦 Pydantic v2     - Validação e serialização
💻 SQLAlchemy ORM  - Mapeamento objeto-relacional
```

#### **Estrutura do Backend:**
```
backend/
├── 📄 main.py                    # ✅ Entry point UNIFICADO (Modelagem + IoT)
├── 📄 requirements.txt           # Dependências Python
├── 🏗️ routers/                   # ✅ TODOS os endpoints consolidados
│   ├── auth.py                   # Autenticação JWT
│   ├── conversational.py         # IA conversacional
│   ├── modeling.py               # Modelagem 3D
│   ├── simulation.py             # Simulação física
│   ├── budgeting.py              # Orçamento inteligente
│   ├── devices.py                # IoT: Dispositivos
│   ├── monitoring.py             # IoT: Monitoramento
│   ├── alerts.py                 # IoT: Alertas
│   ├── projects.py               # IoT: Projetos
│   └── websocket.py              # IoT: Tempo real
├── 🗄️ models/                    # Modelos SQLAlchemy
│   ├── __init__.py               # Modelos principais (User, Project)
│   ├── simulation.py             # Modelos de simulação
│   ├── budgeting.py              # Modelos de orçamento
│   └── iot_*.py                  # Modelos IoT específicos
├── 💼 services/                  # Lógica de negócio
│   ├── auth_service.py           # Serviço de autenticação
│   ├── modeling_service.py       # Serviço de modelagem
│   ├── simulation_service.py     # Serviço de simulação
│   └── budgeting_service.py      # Serviço de orçamento
├── 📋 schemas/                   # Schemas Pydantic
└── 🏗️ core/                      # Configurações e setups
│   ├── config.py                # Settings e configurações
│   └── database.py              # Engine PostgreSQL
├── 🗄️ models/                    # Modelos SQLAlchemy
│   ├── __init__.py              # Declarative Base
│   ├── user.py                  # Modelos de usuário
│   └── simulation.py            # Modelos de simulação
├── 📝 schemas/                   # Schemas Pydantic
│   ├── __init__.py              # Schemas comuns
│   └── simulation.py            # Schemas específicos
├── 🛣️ routes/                     # Endpoints da API
│   ├── auth.py                  # Autenticação
│   ├── conversational.py        # IA conversacional
│   ├── modeling.py              # Modelagem 3D
│   ├── simulation.py            # Simulação física
│   └── budgeting.py             # Orçamento inteligente
├── ⚙️ services/                   # Lógica de negócio
│   ├── auth_service.py          # Serviços auth
│   ├── modeling_service.py      # Serviços modelagem
│   └── budgeting_service.py     # Serviços orçamento
├── 🔐 middleware/                 # Middleware de segurança
│   └── auth.py                  # Autenticação HTTP
└── 🧪 tests/                     # Testes automatizados
    ├── test_integration.py      # Testes de integração
    └── test_integration_final.py # Teste final completo
```

**Status da Integração:** ✅ **100% Estruturalmente Integrado**
- 30 arquivos Python
- 12.892 linhas de código  
- 19 arquivos modificados na integração
- All imports relativos funcionando
- Pydantic v2 migration completa
- FastAPI + SQLAlchemy operacional

### 📡 **Frontend IoT** (Hardware + Software)

#### **Projetos Implementados:**
1. 🔍 **Monitor de Filamento ESP32** - Sensor de peso inteligente
2. 🚀 **Esteira Transportadora Arduino** - Automação de transporte
3. 🏭 **Estação QC Raspberry Pi** - Controle de qualidade com IA

#### **Fluxo de Integração:**
```
IA Design → API Backend → Controle IoT → Produção Física
     ↓           ↓            ↓            ↓
 Otimização → Armazenamento → Execução → Feedback
```

**Benefícios da Integração:**
- 🤖 **IA otimiza designs** no backend antes da produção
- 📊 **Dados reais** do frontend retroalimentam o sistema
- ⚡ **Automação completa** desde concepção até produto final
- 📈 **Métricas em tempo real** de qualidade e eficiência

## 📁 Estrutura do Repositório

### 🏗️ **Organização Visual**
```
3dPot/
├── 📄 README.md                          # Documentação principal
├── 🌍 backend/                           # API Backend FastAPI v2.0
│   ├── 📄 main.py                        # Entry point da aplicação
│   ├── 📄 requirements.txt               # Dependências Python
│   ├── 🏗️ core/                          # Configurações e setups
│   │   ├── config.py                    # Settings e configurações
│   │   └── database.py                  # Engine PostgreSQL
│   ├── 🗄️ models/                        # Modelos SQLAlchemy
│   │   ├── __init__.py                  # Declarative Base
│   │   ├── user.py                      # Modelos de usuário
│   │   └── simulation.py                # Modelos de simulação
│   ├── 📝 schemas/                       # Schemas Pydantic
│   │   ├── __init__.py                  # Schemas comuns
│   │   └── simulation.py                # Schemas específicos
│   ├── 🛣️ routes/                         # Endpoints da API
│   │   ├── auth.py                      # Autenticação JWT
│   │   ├── conversational.py            # IA Minimax
│   │   ├── modeling.py                  # Modelagem 3D
│   │   ├── simulation.py                # Simulação física
│   │   └── budgeting.py                 # Orçamento inteligente
│   ├── ⚙️ services/                       # Lógica de negócio
│   │   ├── auth_service.py              # Serviços auth
│   │   ├── modeling_service.py          # Serviços modelagem
│   │   └── budgeting_service.py         # Serviços orçamento
│   ├── 🔐 middleware/                     # Middleware de segurança
│   │   └── auth.py                      # Autenticação HTTP
│   ├── 🧪 tests/                         # Testes do backend
│   │   ├── test_integration.py          # Testes integração
│   │   └── test_integration_final.py    # Teste final completo
│   └── 🗂️ storage/                        # Armazenamento de arquivos
│       ├── models/                      # Modelos 3D gerados
│       └── temp/                        # Arquivos temporários
├── 📡 frontend-iot/                      # Hardware IoT original
│   ├── 📂 projetos/                      # Projetos completos
│   │   ├── esp32/monitor-filamento/      # Monitor de filamento
│   │   ├── arduino/esteira-transportadora/  # EsteTransportadora
│   │   ├── raspberry-pi/estacao-qc/      # Estação QC
│   │   └── toolchain/                    # Ferramentas auxiliares
│   ├── 💻 codigos/                       # Código fonte organizado
│   │   ├── esp32/                       # Firmware ESP32
│   │   ├── arduino/                     # Sketch Arduino
│   │   └── raspberry-pi/                # Scripts Python
│   ├── 🎯 modelos-3d/                    # Modelos OpenSCAD
│   │   ├── esp32-projetos/              # Suportes ESP32
│   │   ├── arduino-projetos/            # Componentes esteira
│   │   └── raspberry-pi-projetos/       # Cases e suportes
│   └── 🖼️ assets/screenshots/            # Galeria visual completa
├── 🧪 tests/                             # Sistema de testes (pytest)
│   ├── unit/                             # Testes unitários
│   │   ├── test_project_structure.py
│   │   ├── test_3d_models.py
│   │   ├── test_arduino/
│   │   ├── test_esp32/
│   │   └── test_raspberry_pi/
│   ├── integration/                     # Testes de integração
│   │   └── test_system_integration.py
│   ├── requirements-test.txt            # Dependências de teste
│   └── pytest.ini                      # Configuração pytest
└── 🚀 .github/workflows/                 # CI/CD Pipeline
    ├── ci.yml                          # Pipeline principal
    ├── openscad.yml                    # Validação modelos 3D
    ├── arduino-build.yml               # Build Arduino/ESP32
    ├── python-tests.yml                # Testes Python
    └── backend-api.yml                 # Deploy API Backend
```

### 🧪 **Sistema de Testes (pytest)**
O projeto inclui um **sistema completo de testes** para garantir qualidade tanto do backend quanto do frontend:

```bash
# Executar todos os testes
./run_tests.sh

# Testes unitários (Frontend IoT)
python -m pytest tests/unit/ -v

# Testes de integração (Frontend + Backend)
python -m pytest tests/integration/ -v

# Testes do Backend API
python -m pytest backend/tests/ -v

# Testes com coverage (Backend)
python -m pytest --cov=backend/ backend/tests/

# Testes específicos por projeto
python -m pytest tests/unit/test_esp32/ -v
```

**Testes Backend API:**
- ✅ **Integração completa** - Validação 30 arquivos Python, 12.892 linhas
- ✅ **Autenticação JWT** - Sistema de segurança validado
- ✅ **Modelos SQLAlchemy** - Estrutura de dados correta
- ✅ **Schemas Pydantic v2** - Validação e serialização
- ✅ **Endpoints REST** - Todas as rotas funcionando
- ✅ **Services Layer** - Lógica de negócio operacional
- ✅ **Middlewares** - Segurança HTTP implementada

**Testes Frontend IoT:**
- ✅ **Estrutura do projeto** - Validação de diretórios e arquivos
- ✅ **Modelos 3D** - Verificação OpenSCAD e organização  
- ✅ **Integração** - Comunicação entre hardware/software
- ✅ **Qualidade** - Coverage e validação de código

**Status dos Testes:** ✅ **100% Passing**
- Todas as rotas da API validadas
- Integração backend + frontend OK
- Dependências opcionais (3D libs) tratadas adequadamente

### 📋 **Checklist de Arquivos Essenciais**
Para cada projeto implementado, certifique-se de ter:
- [ ] `README.md` específico do projeto
- [ ] Código fonte na pasta `codigos/`
- [ ] Modelos 3D na pasta `modelos-3d/`
- [ ] Esquemáticos em `assets/screenshots/`
- [ ] Testes unitários em `tests/unit/`
- [ ] Documentação visual atualizada

## 🖼️ Galeria Visual

Abaixo você encontra diagramas técnicos, mockups de interface, mockups físicos dos projetos montados e visualizações dos projetos. Para uma galeria completa com descrições detalhadas, acesse: [`assets/screenshots/GALERIA-VISUAL.md`](assets/screenshots/GALERIA-VISUAL.md)

**🆕 NOVOS MOCKUPS FÍSICOS ADICIONADOS:**
- 📷 Visualizações realistas dos projetos montados com modelos 3D impressos
- 🎬 Demonstrações visuais das funcionalidades em ação
- 🔧 Guias visuais de montagem e integração
- 📊 Interfaces web com dados em tempo real

### 🏗️ Arquitetura dos Sistemas

#### **Monitor de Filamento ESP32**
![Arquitetura ESP32](assets/screenshots/arquitetura-esp32-monitor.png)
*Sistema completo de monitoramento com ESP32, interface web e integração IoT*

#### **Esteira Transportadora Arduino**
![Arquitetura Arduino](assets/screenshots/arquitetura-arduino-esteira.png)
*Controle de motores, sensores e interface de usuário para automação*

#### **Estação QC Raspberry Pi**
![Arquitetura QC](assets/screenshots/arquitetura-raspberry-qc.png)
*Sistema de visão computacional para controle de qualidade automatizado*

### 🔄 Integração do Ecossistema

#### **Fluxo 3dPot**
![Fluxo Ecossistema](assets/screenshots/fluxo-ecosistema-3dpot.png)
*Como os três projetos se integram em um ecossistema de produção inteligente*

### 🖥️ Interfaces Web

#### **Interface Monitor ESP32**
![Interface Web ESP32](assets/screenshots/interface-esp32-web.png)
*Dashboard responsivo para monitoramento de filamento em tempo real*

#### **Dashboard Estação QC**
![Dashboard QC](assets/screenshots/interface-qc-dashboard.png)
*Interface web para análise automática de qualidade com galeria de fotos*

### 🎯 Modelos 3D Técnicos

#### **Especificações dos Modelos 3D**
![Modelos 3D](assets/screenshots/modelos-3d-especificacoes.png)
*Especificações detalhadas dos modelos OpenSCAD paramétricos*

### 🔌 Esquemáticos Técnicos

#### **Monitor ESP32**
![Esquemático ESP32](assets/screenshots/esquematico-esp32-monitor.png)
*Diagrama detalhado de conexões: ESP32, HX711, células de carga*

#### **Esteira Arduino**
![Esquemático Arduino](assets/screenshots/esquematico-arduino-esteira.png)
*Esquemático completo: Arduino, motor NEMA17, sensores, controles*

#### **Estação QC**
![Esquemático QC](assets/screenshots/esquematico-raspberry-qc.png)
*Diagrama de conexões: Raspberry Pi, câmera, LED ring, motor*

#### **Sistema Integrado**
![Sistema Integrado](assets/screenshots/diagrama-sistema-integrado.png)
*Integração global: rede WiFi, MQTT, fluxo de produção*

### 🌊 **Fluxo Visual Completo do Sistema**

#### **Como os Projetos Trabalham Juntos**
![Demonstração Fluxo Completo](assets/screenshots/demonstracao-fluxo-completo.png)
*Fluxo integrado: Monitor → Transporte → QC → Produção Final*

#### **Demonstração das Interfaces em Ação**
![Demonstração Interfaces](assets/screenshots/demonstracao-interfaces-web.png)
*Interfaces web funcionando com dados reais em tempo real*

#### **Processo de Montagem dos Modelos 3D**
![Guia Montagem 3D](assets/screenshots/guia-montagem-modelos-3d.png)
*Do arquivo OpenSCAD ao projeto funcionando: impressão → montagem → integração*

### 🔄 **Ciclo Completo de Produção**

```mermaid
graph LR
    A[📦 Filamento] --> B[⚖️ Monitor ESP32]
    B --> C[📊 Interface Web]
    B --> D[🚨 Alerta Queda]
    D --> E[🔄 Reabastecimento]
    
    B --> F[🚀 Esteira Arduino]
    F --> G[📷 Sensores IR]
    G --> H[🎮 Controles Manuais]
    
    F --> I[🏭 Estação QC]
    I --> J[📷 Câmera Pi]
    J --> K[🤖 Análise OpenCV]
    K --> L[✅/❌ Aprovação]
    
    C --> M[🌐 Dashboard Central]
    H --> M
    L --> M
    M --> N[📈 Relatórios]
```

**Benefícios do Ecossistema Integrado:**
- 🔍 **Monitoramento automático** do filamento
- 🚀 **Transporte inteligente** entre estações
- 🏭 **Controle de qualidade** com IA
- 📊 **Dashboard central** com todos os dados
- 🚨 **Alertas proativos** para manutenção
- 📈 **Relatórios de produção** automáticos

📖 **Para instruções detalhadas de montagem, consulte**: [`assets/screenshots/GUIA-CONEXOES.md`](assets/screenshots/GUIA-CONEXOES.md)

---

## 🚀 Quick Start - Guia Visual para Iniciantes

### 📋 Resumo do Sistema
![Ecossistema 3dPot](assets/screenshots/fluxo-ecosistema-3dpot.png)

O **3dPot** é um ecossistema completo com **duas verticais** principais:

| Componente | Tecnologia | Função | Dificuldade |
|------------|------------|--------|-------------|
| 🌐 **Backend API** | FastAPI + IA | Prototipagem sob demanda com IA | ⭐⭐ Intermediário |
| 🔍 **Monitor IoT** | ESP32 | Pesagem inteligente do filamento | ⭐ Fácil |
| 🚀 **Esteira IoT** | Arduino | Transporte automático de peças | ⭐⭐ Intermediário |
| 🏭 **QC IoT** | Raspberry Pi | Controle de qualidade com visão | ⭐⭐⭐ Avançado |

### 🎯 Como Começar (5 Minutos)

#### 1️⃣ **Clone e Escolha a Verticial** (2 min)
```bash
# Clone o repositório
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot

# ESCOLHA UMA OPÇÃO:

# 🌐 Backend API (Recomendado para desenvolvedores)
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# 📡 Frontend IoT (Recomendado para makers)
cd frontend-iot
pip install -r requirements-test.txt
python -m pytest tests/unit/test_project_structure.py -v
```

#### 2️⃣ **Acesse a Documentação** (3 min)

**Se escolher Backend API:**
- 🌐 Swagger UI: `http://localhost:8000/docs`
- 📚 ReDoc: `http://localhost:8000/redoc`
- 🧪 Testes: `python backend/tests/test_integration_final.py`

**Se escolher Frontend IoT:**
- 👶 **Primeiro projeto**: Monitor de Filamento ESP32 (mais simples)
- 🛠️ **Segundo projeto**: Esteira Transportadora Arduino (intermediário)  
- 🏆 **Desafio**: Estação QC Raspberry Pi (avançado)
- 📖 [Guia Completo de Conexões](frontend-iot/assets/screenshots/GUIA-CONEXOES.md)
- 🖼️ [Galeria Visual Completa](frontend-iot/assets/screenshots/GALERIA-VISUAL.md)

---

## 🚀 Backend API v2.0 - Sistema de Prototipagem Sob Demanda

### 📖 **Instalação e Execução**

#### 🗄️ **Pré-requisitos**
```bash
# Instalar PostgreSQL e Redis
sudo apt install postgresql redis-server

# Configurar Redis (opcional para cache)
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### 🔧 **Configuração do Backend**

**1. Clone e Configure o Ambiente:**
```bash
# Backend API
cd backend
cp .env.example .env  # Configure suas variáveis

# Instale dependências Python (core + opcionais)
pip install -r requirements.txt

# Se quiser recursos 3D completos (opcional):
pip install cadquery trimesh pybullet

# Configure o banco de dados
createdb 3dpot_db  # ou use docker-compose se disponível
```

**2. Configure as Variáveis de Ambiente (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/3dpot_db

# Segurança
SECRET_KEY=sua-chave-secreta-super-segura
REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Minimax AI
MINIMAX_API_KEY=sua-chave-api-minimax
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=abab6.5s-chat

# Storage
MODELS_STORAGE_PATH=./storage/models
TEMP_STORAGE_PATH=./storage/temp
```

#### ⚡ **Execução**

**Método 1: Desenvolvimento (Recomendado)**
```bash
# Backend FastAPI
cd backend
python -m uvicorn main:app --reload --port 8000

# Acesse a documentação:
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
# API: http://localhost:8000/api/v1
```

**Método 2: Produção**
```bash
# Com Gunicorn
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 🧪 **Testes do Backend**

```bash
# Execute o teste de integração completo
cd backend
python tests/test_integration_final.py

# Ou use pytest
python -m pytest tests/ -v --cov=.
```

**Resultados Esperados:**
```
✅ 30 arquivos Python
✅ 12.892 linhas de código
✅ Configurações carregadas
✅ Modelos e schemas OK
✅ Rotas core conectadas
✅ Serviços core operacionais
```

### 🌐 **Endpoints da API**

| Endpoint | Método | Descrição | Autenticação |
|----------|--------|-----------|--------------|
| `/auth/login` | POST | Login JWT | ❌ |
| `/auth/register` | POST | Registro usuário | ❌ |
| `/auth/refresh` | POST | Renovar token | ✅ |
| `/conversations` | POST | IA Conversacional | ✅ |
| `/modeling/generate` | POST | Gerar modelo 3D | ✅ |
| `/simulation/run` | POST | Executar simulação | ✅ |
| `/budgeting/calculate` | POST | Calcular orçamento | ✅ |
| `/users/me` | GET | Dados do usuário | ✅ |

### 🔍 **Verificação da Instalação**

**Teste Rápido:**
```bash
# Backend está funcionando?
curl http://localhost:8000/health

# Documentação acessível?
open http://localhost:8000/docs
```

**Status da Integração:** ✅ **100% Operacional**
- FastAPI + SQLAlchemy ✅
- PostgreSQL + Redis ✅  
- JWT Authentication ✅
- Minimax AI ✅
- Pydantic v2 ✅
- Import structure ✅

---

## 🔧 Instalação Detalhada por Projeto

### 🟢 Projeto 1: Monitor de Filamento ESP32 (Recomendado para iniciantes)

![Mockup Físico ESP32](assets/screenshots/mockup-fisico-esp32-montado.png)

#### 📦 **Lista de Compras**
- ESP32 DevKit V1
- Sensor HX711 + 4x células de carga
- Protoboard + jumpers
- LED + resistor 220Ω
- Carretel de filamento para teste

#### 🔌 **Conexões (Super Simples!)**
![Esquemático ESP32](assets/screenshots/esquematico-esp32-monitor.png)

```
ESP32    →    HX711
GPIO 4   →    DOUT
GPIO 5   →    SCK
3.3V     →    VCC
GND      →    GND
GPIO 2   →    LED (+ resistor 220Ω)
```

#### 💻 **Upload do Código**
```bash
# Via Arduino IDE
1. Instale ESP32 board no Arduino IDE
2. Abra: codigos/esp32/monitor-filamento.ino
3. Selecione: ESP32 Dev Module
4. Upload!

# Via PlatformIO (Recomendado)
pio device monitoring
```

#### 🌐 **Acesse a Interface**
```
http://IP_DO_ESP32.local
```
**Dica**: O ESP32 cria automaticamente uma rede WiFi "3dPot-XXX" se não encontrar sua rede!

---

### 🟠 Projeto 2: EsteTransportadora Arduino

![Mockup Físico Esteira](assets/screenshots/mockup-fisico-arduino-esteira-montado.png)

#### 📦 **Lista de Compras**
- Arduino Uno ou Nano
- Motor NEMA17 + Driver A4988
- 2x Sensores IR
- Display LCD 16x2
- Fonte 12V 2A
- Resistores diversos

#### 🔌 **Conexões Intermediárias**
![Esquemático Arduino](assets/screenshots/esquematico-arduino-esteira.png)

#### 💻 **Código e Teste**
```bash
# Arduino IDE
1. Abra: codigos/arduino/esteira-transportadora.ino
2. Selecione: Arduino Uno
3. Upload + Monitor Serial (115200 baud)
```

#### 🎮 **Controles Disponíveis**
- Potenciômetro: Velocidade da esteira
- Botão: Parar/emergência
- Monitor Serial: Comandos de controle

---

### 🔴 Projeto 3: Estação QC Raspberry Pi

![Mockup Físico QC](assets/screenshots/mockup-fisico-raspberry-qc-montado.png)

#### 📦 **Lista de Compras**
- Raspberry Pi 4 (2GB+)
- Câmera Pi HQ
- LED Ring 12V
- Motor NEMA17 + Driver
- Fonte 12V 5A + 5V 3A

#### 🐍 **Setup do Software**
```bash
# No Raspberry Pi
sudo raspi-config  # Habilite Câmera e I2C
sudo pip install opencv-python RPi.GPIO paho-mqtt

# Clone e execute
cd 3dPot
python codigos/raspberry-pi/estacao_qc.py
```

#### 🌐 **Dashboard Web**
```
http://IP_DO_PI:5000
```
**Recursos**: Análise automática, galeria de fotos, relatórios

---

## 🧪 Sistema de Testes

### 📊 **Cobertura de Testes (Sprint 2)**

**Status Atual:** 284 testes unitários • ~72% de cobertura • Execução em < 1s

| Tipo de Teste | Quantidade | Cobertura | Status |
|---------------|------------|-----------|--------|
| **Testes Unitários** | 284 | ~72% | ✅ Passando |
| • Serviços Backend | 191 | ~72% | ✅ Implementado |
| • Hardware (Arduino/ESP32/RPi) | 52 | ~80% | ✅ Implementado |
| • Modelos 3D | 18 | ~85% | ✅ Implementado |
| • Estrutura do Projeto | 23 | ~90% | ✅ Implementado |
| **Testes de Integração** | 8 arquivos | ~60% | ⚠️ Em consolidação |
| **Testes End-to-End** | Pendente | 0% | ⏸️ Sprint 3 |

### 🎯 **Serviços com Testes Unitários**

#### ✅ **Cobertos (191 testes novos - Sprint 2)**
1. **BudgetingService** (48 testes)
   - Cálculos de custos de materiais
   - Integração com APIs de fornecedores
   - Cálculo de preço final com margens

2. **ModelingService** (41 testes)
   - Modelagem 3D paramétrica
   - Validação de imprimibilidade
   - Engines CadQuery e OpenSCAD

3. **Print3DService** (43 testes)
   - Gerenciamento de impressoras
   - Geração de G-code
   - Estimativas de tempo e custo

4. **SimulationService** (32 testes)
   - Simulações físicas (drop, stress, motion)
   - Cálculos de física
   - Sistema de cache

5. **ProductionService** (27 testes)
   - Planejamento de produção
   - Otimização de lotes
   - Controle de qualidade

6. **AuthService** (27 testes - complementar)
   - Validação de senhas
   - JWT e refresh tokens
   - Rate limiting

### 🚀 **Executando os Testes**

#### Todos os Testes
```bash
# Método 1: Script helper
./run_tests.sh all

# Método 2: Pytest direto
python -m pytest tests/ -v

# Com cobertura
python -m pytest tests/ --cov=backend --cov-report=html
```

#### Testes por Categoria
```bash
# Apenas testes unitários
./run_tests.sh unit
python -m pytest tests/unit/ -v

# Apenas testes de integração
./run_tests.sh integration
python -m pytest tests/integration/ -v

# Apenas testes de serviços
python -m pytest tests/unit/services/ -v

# Apenas testes de hardware
./run_tests.sh hardware
python -m pytest tests/unit/ -m "arduino or esp32 or raspberry_pi" -v
```

#### Testes Específicos
```bash
# Um serviço específico
python -m pytest tests/unit/services/test_budgeting_service.py -v

# Uma classe específica
python -m pytest tests/unit/services/test_modeling_service.py::TestDimensionValidation -v

# Um teste específico
python -m pytest tests/unit/services/test_print3d_service.py::TestGCodeGeneration::test_gcode_header_generation -v
```

#### Relatório de Cobertura
```bash
# Gerar relatório HTML
./run_tests.sh coverage

# Visualizar cobertura (abre no navegador)
open tests/coverage_html/index.html
```

### 📝 **Estrutura de Testes**

```
tests/
├── conftest.py                          # Fixtures globais
├── unit/                                # Testes unitários
│   ├── services/                        # ✅ Serviços backend (191 testes)
│   │   ├── test_budgeting_service.py   # 48 testes
│   │   ├── test_modeling_service.py    # 41 testes
│   │   ├── test_print3d_service.py     # 43 testes
│   │   ├── test_simulation_service.py  # 32 testes
│   │   ├── test_production_service.py  # 27 testes
│   │   └── test_auth_service.py        # 27 testes (complementar)
│   ├── test_arduino/                   # ✅ Hardware Arduino
│   ├── test_esp32/                     # ✅ Hardware ESP32
│   ├── test_raspberry_pi/              # ✅ Hardware Raspberry Pi
│   ├── test_3d_models.py               # ✅ Modelos 3D
│   └── test_project_structure.py       # ✅ Estrutura do projeto
└── integration/                         # Testes de integração
    ├── test_system_integration.py       # Testes de sistema
    ├── test_minimax_service.py          # Testes de IA
    └── teste_endpoint_lgm.py            # Testes de endpoints
```

### 🌐 **Testes End-to-End (E2E) - Sprint 3**

**Status Atual:** 9 testes E2E implementados • Cobrindo fluxos críticos

```bash
# Executar testes E2E
pytest tests/e2e/ -v

# Testes E2E específicos
pytest tests/e2e/test_workflows.py -v
```

**Fluxos cobertos:**
- ✅ Autenticação (registro, login)
- ✅ Criação de projetos
- ✅ Sistema conversacional
- ✅ Geração de orçamentos
- ✅ Fluxo completo (projeto → conversa → orçamento)

```
tests/e2e/
└── test_workflows.py                # Testes E2E principais (9 testes)
```

### 📚 **Documentação de Testes**

Para mais detalhes sobre testes e estratégia de qualidade:
- **[SPRINT2-QUALIDADE-TESTES-RELATORIO.md](docs/arquitetura/SPRINT2-QUALIDADE-TESTES-RELATORIO.md)** - Relatório Sprint 2 (Testes Unitários)
- **[SPRINT3-SCRIPTS-CLI-E2E-RELATORIO.md](docs/arquitetura/SPRINT3-SCRIPTS-CLI-E2E-RELATORIO.md)** - Relatório Sprint 3 (Integração, CLI, E2E)
- **[pytest.ini](pytest.ini)** - Configuração do pytest
- **[requirements-test.txt](requirements-test.txt)** - Dependências de teste

### 🎯 **Próximos Passos (Sprint 4)**
- [ ] Ampliar cobertura E2E (3-5 novos fluxos)
- [ ] Adicionar testes para serviços secundários (~80-120 testes)
- [ ] Integrar E2E com CI/CD pipeline
- [ ] Atingir 85% de cobertura
- [ ] Testes de performance e carga

---

## 🎯 CLI Unificada (Sprint 3)

O projeto 3dPot possui uma **interface de linha de comando unificada** para facilitar o uso de demos, validações e monitoramento.

### 🚀 Uso Básico

```bash
# Ver ajuda geral
python scripts/cli/main.py --help

# Executar demo do Minimax
python scripts/cli/main.py demo minimax

# Validar modelos OpenSCAD
python scripts/cli/main.py validate openscad

# Monitorar workflows GitHub
python scripts/cli/main.py monitor workflows
```

### 📋 Comandos Disponíveis

#### 🎬 Demo - Demonstrações do Sistema

```bash
python scripts/cli/main.py demo minimax        # Integração Minimax M2
python scripts/cli/main.py demo modeling       # Sistema de modelagem 3D
python scripts/cli/main.py demo system         # Sistema completo
python scripts/cli/main.py demo lgm            # Integração LGM
python scripts/cli/main.py demo auth           # Sistema de autenticação
```

#### ✅ Validate - Validações

```bash
python scripts/cli/main.py validate openscad              # Validar OpenSCAD
python scripts/cli/main.py validate openscad --quick      # Validação rápida
python scripts/cli/main.py validate syntax                # Sintaxe Python
python scripts/cli/main.py validate quality               # Qualidade código
```

#### 📊 Monitor - Monitoramento

```bash
python scripts/cli/main.py monitor workflows              # Workflows GitHub
python scripts/cli/main.py monitor workflows --optimize   # Com otimizações
python scripts/cli/main.py monitor performance            # Performance
```

### 📚 Documentação

Ver documentação completa da CLI em [`scripts/cli/README.md`](scripts/cli/README.md)

### 🔄 Scripts Legados

Os scripts individuais ainda funcionam para compatibilidade, mas **recomendamos usar a CLI unificada**.

---

## 🔍 Troubleshooting Comum

### 🌐 **Problemas do Backend API**

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| 🐍 `ModuleNotFoundError: No module named 'pydantic'` | Pydantic não instalado | `pip install -r backend/requirements.txt` |
| 🗄️ `psycopg2.OperationalError` | PostgreSQL desconectado | `sudo systemctl start postgresql` |
| 🔐 `jwt.exceptions.PyJWTError` | SECRET_KEY inválida | Configure `.env` com SECRET_KEY válida |
| 🤖 `MinimaxAPIError` | API key inválida | Verifique MINIMAX_API_KEY no `.env` |
| ⚡ `ConnectionError` a Redis | Redis não rodando | `sudo systemctl start redis-server` |
| 📦 `ImportError: attempted relative import` | Estrutura de pacotes | Use `python -m uvicorn main:app` (não `python main.py`) |

### 🚨 **Problemas de Hardware**

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| 🔌 ESP32 não liga | Alimentação USB | Use cabo dados + carga (não só carga) |
| ⚖️ Célula de carga instável | Vibração/ruído | Monte em superfície estável, cables curtos |
| 🚀 Motor pulando passos | Alimentação fraca | Verifique 12V 2A, reduce velocidade |
| 📷 Câmera Pi negra | Interface desabilitada | `sudo raspi-config` → Interface → Camera |

### 🌐 **Problemas de Conectividade**

| Problema | Diagnóstico | Solução |
|----------|-------------|---------|
| 📶 ESP32 sem WiFi | LED não pisca | Verifique SSID/senha no código |
| 🔌 Arduino mudo | Monitor serial vazio | Check 115200 baud, reset button |
| 🖥️ Pi dashboard offline | 404/connection refused | `ps aux \| grep python` para verificar se está rodando |

### 💻 **Problemas de Software**

```bash
# Python errors
pip install --upgrade -r requirements-test.txt

# Arduino libraries
# Use Library Manager para:
# - WiFi (ESP32)
# - LiquidCrystal (LCD)
# - AccelStepper (motores)

# OpenSCAD models
openscad -o output.stl model.scad
```

### 🔧 **Comandos de Diagnóstico Úteis**

```bash
# Backend API (FastAPI)
cd backend
python tests/test_integration_final.py  # Teste completo de integração
python -m uvicorn main:app --reload --log-level debug  # Servidor com logs detalhados
curl http://localhost:8000/health        # Health check
curl -X GET http://localhost:8000/docs   # Verificar documentação

# PostgreSQL
sudo systemctl status postgresql         # Status do banco
sudo -u postgres psql -c "SELECT version();"  # Versão instalada
sudo -u postgres psql -l                 # Listar databases

# Redis
sudo systemctl status redis-server       # Status do Redis
redis-cli ping                          # Teste de conectividade
redis-cli monitor                       # Monitor em tempo real

# ESP32
pio device list                         # Lista dispositivos
pio device monitoring                  # Monitor serial

# Arduino
ls /dev/tty*                           # Lista portas USB
screen /dev/ttyUSB0 115200            # Monitor serial manual

# Raspberry Pi
vcgencmd get_camera                   # Status da câmera
lsmod | grep i2c                      # Módulos I2C carregados
systemctl status mosquitto            # MQTT broker status
```

### 📞 **Precisa de Mais Ajuda?**

1. 🐛 **Issues**: [Abra uma issue](https://github.com/dronreef2/3dPot/issues) com fotos do problema
2. 💬 **Discussions**: [Participe das discussões](https://github.com/dronreef2/3dPot/discussions)
3. 📧 **Email**: Para problemas complexos, inclua logs e especificações do hardware

## 📚 Recursos Adicionais

### 🗂️ **Documentação Técnica**
| Recurso | Descrição | Nível |
|---------|-----------|-------|
| 🔌 [Guia de Conexões IoT](frontend-iot/assets/screenshots/GUIA-CONEXOES.md) | Diagramas esquemáticos detalhados | ⭐⭐ |
| 🖼️ [Galeria Visual IoT](frontend-iot/assets/screenshots/GALERIA-VISUAL.md) | Mockups, interfaces e diagramas | ⭐ |
| 🏗️ [Arquiteturas do Sistema](assets/screenshots/) | Diagramas técnicos de cada projeto | ⭐⭐ |
| 🎯 [Especificações 3D](frontend-iot/assets/screenshots/modelos-3d-especificacoes.png) | Modelos OpenSCAD paramétricos | ⭐⭐ |
| 📚 [Backend API Docs](http://localhost:8000/docs) | Swagger UI - Endpoints e schemas | ⭐⭐⭐ |
| 📋 [Relatório de Integração](backend/RELATORIO-INTEGRACAO-FINAL.md) | Status da integração v2.0 | ⭐⭐⭐ |

### 🛠️ **Ferramentas e Setup**
| Ferramenta | Uso | Link |
|------------|-----|------|
| Arduino IDE | Programação ESP32/Arduino | [Download](https://www.arduino.cc/en/software) |
| PlatformIO | Desenvolvimento profissional | [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=platformio.platformio-ide) |
| OpenSCAD | Modelagem 3D paramétrica | [Download](https://openscad.org/downloads.html) |
| KiCad | Design de PCBs | [Download](https://www.kicad.org/download/) |

### 📖 **Guias de Aprendizado**
- 🎓 **Iniciantes**: Comece com Monitor ESP32, leitura da galeria visual
- 🔧 **Intermediários**: Esteira Arduino, explore PlatformIO
- 🏆 **Avançados**: Estação QC, integração MQTT, dashboards
- 🌐 **IoT**: Protocolos, Home Assistant, automação residencial

### 🤝 **Comunidade e Contribuição**
- 🐛 [Issues e Bugs](https://github.com/dronreef2/3dPot/issues) - Reporte problemas
- 💡 [Feature Requests](https://github.com/dronreef2/3dPot/discussions) - Sugira melhorias
- 🤝 [Contribuições](CONTRIBUTING.md) - Como ajudar o projeto
- 📋 [Código de Conduta](CODE_OF_CONDUCT.md) - Diretrizes da comunidade

### 🎯 **Próximos Passos**

#### **Backend API v2.0:**
1. 🤖 **Configure IA Minimax** - Obtenha API key e configure conversação inteligente
2. 🗄️ **Setup PostgreSQL** - Configure banco de dados para persistência
3. 📊 **Teste endpoints** - Explore `/docs` para ver todas as funcionalidades
4. 🔗 **Integre com Frontend IoT** - Conecte hardware aos dados da API
5. 📈 **Implemente otimizações** - Use dados reais para melhorar a IA

#### **Frontend IoT:**
1. 📈 **Implemente os outros projetos** seguindo a ordem de dificuldade
2. 🔗 **Integre o ecossistema** usando MQTT para comunicação
3. 🏠 **Conecte ao Home Assistant** para automação residencial
4. 📊 **Crie dashboards customizados** com os dados coletados
5. 🤝 **Compartilhe suas modificações** com a comunidade

#### **Integração Completa:**
6. 🌐 **API ↔ IoT Integration** - Conecte os dados do backend com o hardware
7. 🚀 **Deploy Production** - Configure ambiente de produção
8. 📱 **Mobile App** - Desenvolva interface mobile para monitoramento

### ⚡ **Dicas de Produtividade**

- **Use PlatformIO** ao invés da Arduino IDE para projetos mais complexos
- **Imprima os modelos 3D** com configurações de alta qualidade (0.2mm layer height)
- **Teste cada componente** individualmente antes da integração completa
- **Mantenha backup** das configurações que funcionam
- **Documente suas modificações** para facilitar troubleshooting

---

### 🆘 **Suporte da Comunidade**

- 🐛 **Issues**: [Reportar bugs](https://github.com/dronreef2/3dPot/issues) com fotos e logs
- 💬 **Discussões**: [Perguntas e ideias](https://github.com/dronreef2/3dPot/discussions)  
- 🔧 **Wiki**: [Documentação expandida](https://github.com/dronreef2/3dPot/wiki) (em desenvolvimento)
- 📧 **Email**: Para problemas complexos, inclua especificações completas do hardware

---

## 📖 Parte 1: Insights de Projetos (Hardware + Impressão 3D)

Projetos que exploram a sinergia única entre cada hardware e a impressão 3D.

### Projetos com ESP32 / ESP8266 (Os "Objetos Inteligentes")

O forte deles é serem pequenos, baratos e com Wi-Fi. A impressão 3D permite **embutir a inteligência** diretamente no objeto, tornando-o funcional e com bom acabamento.

#### Insight 1: O Gabarito de Montagem Auto-Verificável

**Ideia:** Em uma pequena linha de montagem (até mesmo em uma bancada de hobby), você precisa garantir que cada peça seja montada corretamente.

**Execução:**
1. **Modelagem 3D:** Projete e imprima um gabarito (jig) perfeitamente moldado para a peça que você está montando. Incorpore no design pequenos espaços para sensores de contato (microswitches) ou sensores ópticos reflexivos.
2. **Hardware:** Embuta um ESP8266 no gabarito. Conecte os sensores a ele.
3. **Programação:** O ESP8266 só envia um sinal de "OK" (via MQTT ou para um painel web) quando todos os componentes da montagem são colocados no gabarito e ativam os sensores na ordem correta. Um LED no próprio gabarito fica verde.

**Por que é genial:** Você cria uma ferramenta de controle de qualidade sob demanda, customizada e inteligente por menos de 10 dólares.

#### Insight 2: O Monitor de Filamento "Universal"

**Ideia:** Saber quanto filamento resta em qualquer carretel, de qualquer marca.

**Execução:**
1. **Modelagem 3D:** Projete um suporte de carretel com um braço de alavanca. O peso do carretel pressiona uma célula de carga (sensor de peso).
2. **Hardware:** Conecte a célula de carga a um ESP32.
3. **Programação:** O ESP32 mede o peso, subtrai o peso do carretel vazio (que você informa uma vez) e calcula a porcentagem restante. Ele expõe essa informação em uma pequena página web ou envia para uma plataforma como o Home Assistant.

**Por que é genial:** É uma solução barata e adaptável a qualquer impressora 3D, resolvendo um problema comum e permitindo um melhor planejamento de impressões longas.

### Projetos com Arduino (O "Controlador Físico")

O Arduino brilha no controle preciso de motores e na interação direta com o mundo físico. A impressão 3D fornece a **estrutura mecânica e os atuadores** para esses projetos.

#### Insight 1: A Mini Esteira Transportadora Modular

**Ideia:** Criar uma pequena esteira para automatizar tarefas, como mover peças de uma etapa para outra.

**Execução:**
1. **Modelagem 3D:** Projete todos os componentes: os roletes, a estrutura lateral, os suportes para os motores e sensores. A beleza aqui é que você pode imprimir módulos e encaixá-los para fazer a esteira do tamanho que quiser.
2. **Hardware:** Um Arduino Uno controla um motor de passo (para movimento preciso) ou um motor DC com encoder. Sensores infravermelhos detectam quando um objeto chega ao fim da esteira.
3. **Programação:** O Arduino gerencia a velocidade da esteira e para o motor quando um objeto é detectado, podendo acionar outro dispositivo (como um braço robótico).

**Por que é genial:** Você constrói a base da automação industrial (movimentação de material) de forma barata e totalmente customizável para o seu espaço e necessidade.

#### Insight 2: O "Liquid Handler" para Projetos de Biologia/Química DIY

**Ideia:** Automatizar a tarefa de mover pequenas quantidades de líquido entre recipientes.

**Execução:**
1. **Modelagem 3D:** Projete um sistema de 3 eixos (X, Y, Z) usando guias lineares baratas e correias. Todas as conexões, suportes de motor e o "efetor final" que segura uma pipeta são impressos em 3D.
2. **Hardware:** Um Arduino Mega com um shield (como o RAMPS) controla 3 motores de passo para o posicionamento e um servo motor para acionar a pipeta.
3. **Programação:** O código no Arduino aceita comandos G-code simples (como em uma impressora 3D) para mover a pipeta para coordenadas específicas e aspirar/dispensar volumes definidos.

**Por que é genial:** Democratiza a automação de laboratório, permitindo a criação de ferramentas que normalmente custariam milhares de reais.

### Projetos com Raspberry Pi (O "Cérebro Central")

O Raspberry Pi é um computador completo. Ele não apenas controla, mas **orquestra, processa e serve** informações. A impressão 3D cria os "olhos e ouvidos" que alimentam o cérebro do Pi.

#### Insight: A Estação de Controle de Qualidade com Visão Computacional

**Ideia:** Inspecionar automaticamente peças recém-impressas para detectar defeitos grosseiros.

**Execução:**
1. **Modelagem 3D:** Projete uma pequena "cabine" de inspeção com iluminação LED controlada e um suporte fixo para a Câmera do Raspberry Pi, garantindo fotos consistentes. Projete também um prato giratório (acionado por um motor de passo).
2. **Hardware:** Um Raspberry Pi controla a iluminação, a câmera e o motor do prato giratório. Um Arduino pode ser usado como um "escravo" para controlar o motor com mais precisão, recebendo comandos do Pi.
3. **Programação (Python no Pi):**
   - O Pi aciona o motor para girar a peça 360 graus, tirando várias fotos.
   - Usa a biblioteca **OpenCV** para comparar as fotos tiradas com uma imagem de referência do modelo 3D renderizado.
   - Ele pode identificar defeitos como camadas faltando, deformações graves (warping) ou falhas de impressão.
   - O resultado (Aprovado/Reprovado) é exibido em um dashboard web servido pelo próprio Pi.

**Por que é genial:** Cria um sistema de "loop fechado", onde a própria tecnologia de fabricação é usada para criar uma ferramenta que melhora sua própria qualidade, integrando robótica, visão computacional e web.

## Parte 2: O Toolchain Open-Source (O Ciclo Completo: da Ideia ao Objeto Inteligente)

Este é o fluxo de trabalho de software que conecta tudo.

### 1. Modelagem 3D (Onde a forma física nasce)

- **Para Iniciantes / Simples: [Tinkercad](https://www.tinkercad.com/)**
  - Baseado em navegador, incrivelmente fácil de aprender. Ótimo para caixas, suportes e formas geométricas simples.
- **Para Engenharia / Paramétrico: [FreeCAD](https://www.freecadweb.org/) ou [Onshape](https://www.onshape.com/) (gratuito para makers)**
  - Permitem criar modelos complexos e "paramétricos" (você pode mudar uma medida e o modelo todo se ajusta). Essencial para projetos mecânicos.
- **Para Modelagem via Código: [OpenSCAD](https://openscad.org/)**
  - **Este é o link direto com a programação!** Você não desenha, você *descreve* o objeto com código. Perfeito para criar peças customizáveis, onde você só precisa alterar variáveis em um script para gerar um novo STL.

### 2. Fatiamento (Preparando o modelo para a impressão)

- **[Ultimaker Cura](https://ultimaker.com/software/ultimaker-cura)** ou **[PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/)**
  - Ambos são open-source, poderosos e compatíveis com quase todas as impressoras. Eles "fatiam" o modelo 3D em camadas e geram o G-code (as instruções que a impressora entende).

### 3. Programação do Hardware (Dando vida ao objeto)

- **[PlatformIO](https://platformio.org/)** (integrado ao **[Visual Studio Code](https://code.visualstudio.com/)** - VSCode)
  - **É o padrão ouro para desenvolvimento embarcado hoje.** É um ambiente profissional que suporta Arduino, ESP32, ESP8266 e centenas de outras placas. Gerencia bibliotecas e configurações de forma muito mais robusta que a IDE do Arduino.
  - Você pode programar em C++ (framework Arduino) ou usar **MicroPython** para os ESPs.
- **Python no Raspberry Pi**
  - Use um editor como o VSCode com a extensão Remote-SSH para programar o Pi diretamente do seu computador. Bibliotecas essenciais: `gpiozero` (fácil controle dos pinos), `paho-mqtt` (para comunicação IoT), `opencv-python` (para visão computacional), `Flask` ou `FastAPI` (para criar interfaces web).

### 4. Integração e Orquestração (Fazendo tudo conversar)

- **[Node-RED](https://nodered.org/)**
  - Roda perfeitamente em um Raspberry Pi. É a "cola" visual que une todos os seus projetos. Você pode, por exemplo, arrastar e soltar nós para criar um fluxo que:
    1. Recebe uma mensagem **MQTT** de um ESP32.
    2. Executa um script **Python** no Raspberry Pi.
    3. Envia um comando para uma API (como a da Factory AI).
    4. Mostra o status em um **dashboard** web.
- **[Mosquitto](https://mosquitto.org/)**
  - Um broker MQTT leve que você pode instalar no seu Raspberry Pi para ser o "servidor de mensagens" central para todos os seus dispositivos IoT na sua rede local.

## Licença

Este projeto é open-source e está disponível sob a licença MIT.

## 📁 Estrutura do Repositório

O repositório está organizado de forma modular para facilitar navegação e manutenção:

```
3dPot/
├── backend/              # API Backend (FastAPI)
├── frontend/            # Interface Web
│   └── demos/          # Demonstrações HTML
├── interface-web/      # Interface Web Alternativa
├── tests/              # Testes automatizados
│   ├── integration/   # Testes de integração
│   └── unit/          # Testes unitários
├── scripts/            # Scripts utilitários
│   ├── validacao/     # Scripts de validação
│   ├── dados/         # Geração de dados
│   ├── monitoramento/ # Monitoramento
│   └── demos/         # Scripts de demonstração
├── docs/               # Documentação
│   ├── sprints/       # Histórico de sprints
│   ├── relatorios/    # Relatórios de progresso
│   ├── validacao/     # Relatórios de validação
│   ├── arquitetura/   # Documentação arquitetural
│   └── guias/         # Guias e tutoriais
├── outputs/            # Artefatos gerados (não versionado)
├── external_api/       # Integrações externas
├── modelos-3d/        # Modelos 3D
└── assets/            # Recursos estáticos
```

Para detalhes completos da estrutura e guia de migração, consulte:
- 📖 [STRUCTURE.md](STRUCTURE.md) - Estrutura detalhada do repositório
- 🔄 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Guia de migração para contribuidores

## Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Autor

**Guilherme (dronreef2)** - Análise e documentação de projetos Maker
- 🔧 Desenvolvimento do Backend API v2.0 (FastAPI + IA)
- 📡 Arquitetura IoT com ESP32, Arduino, Raspberry Pi
- 🏗️ Integração completa do ecossistema 3dPot v2.0
- 📚 Documentação técnica e guias de implementação

---

## 🙏 Agradecimentos

- **Minimax AI** - Sistema conversacional integrado
- **FastAPI** - Framework web rápido e eficiente
- **PostgreSQL** - Banco de dados robusto
- **Comunidade Open Source** - Pela contribuição contínua
