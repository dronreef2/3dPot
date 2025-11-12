# 🚀 3dPot Platform - Prototipagem Sob Demanda v2.0

**Criado em:** 2025-11-12 22:42:43  
**Autor:** MiniMax Agent

## 📋 Sobre o Projeto

A plataforma 3dPot foi evoluída para uma **solução completa de prototipagem sob demanda** que integra:

- 🤖 **Conversação com IA** para captura de requisitos
- 🔧 **Hardware legado** (ESP32, Arduino, Raspberry Pi)  
- 🎯 **Geração automática de modelos 3D** via NVIDIA APIs
- 💰 **Orçamentos automáticos** com integração Octopart
- 📊 **Simulação e eficiência** com Three.js e PyBullet
- 🌐 **API Gateway unificado** FastAPI + PostgreSQL + Redis

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA 3dPot v2.0                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Frontend (React) ──→ API Gateway (FastAPI) ──→ Backend Services       │
│                                                                       │
│  ├── Conversação IA (Minimax M2)                                       │
│  ├── Geração 3D (NVIDIA NIM + OpenSCAD)                               │
│  ├── Orçamento (Octopart API)                                          │
│  ├── Simulação (Three.js + PyBullet)                                   │
│  └── Hardware Bridge (MQTT)                                             │
│                                                                       │
│  Database Layer: PostgreSQL + Redis + MinIO + RabbitMQ                │
└─────────────────────────────────────────────────────────────────────────┘
```

## ⚡ Início Rápido

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.11+** (para desenvolvimento local)
- **Git** para clone do repositório

### 1. Clone e Setup

```bash
# Clone o repositório
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot/3dpot-platform

# Execute o setup automático
./setup.sh
```

### 2. Configure APIs Externas

Edite o arquivo `.env` criado:

```bash
# APIs externas (obter chaves nos respectivos sites)
MINIMAX_API_KEY=seu_api_key_minimax
NVIDIA_API_KEY=seu_api_key_nvidia  
OCTOPART_API_KEY=seu_api_key_octopart

# Configurações locais (já configuradas pelo setup)
DATABASE_URL=postgresql://3dpot:3dpot123@postgres:5432/3dpot_dev
REDIS_URL=redis://redis:6379
MQTT_BROKER=mqtt://mosquitto:1883
```

### 3. Acesse a Plataforma

- **API Gateway:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs
- **MinIO Storage:** http://localhost:9001 (login: 3dpot / 3dpot123minio)
- **RabbitMQ Management:** http://localhost:15672 (login: 3dpot / 3dpot123)

## 🔧 Desenvolvimento

### Comandos Docker

```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Resetar dados (cuidado!)
docker-compose down -v
docker-compose up -d
```

### Desenvolvimento Local

```bash
# API Gateway (FastAPI)
cd services/api-gateway
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Estrutura do Projeto

```
3dpot-platform/
├── docker-compose.yml           # Infraestrutura completa
├── .env.example                 # Configuração de exemplo
├── setup.sh                     # Script de setup automático
│
├── init-scripts/               # Scripts SQL de inicialização
│   └── 01-init-database.sql
│
├── mqtt/                       # Configuração Mosquitto
│   └── mosquitto.conf
│
└── services/
    └── api-gateway/            # API Gateway FastAPI
        ├── main.py             # Aplicação principal
        ├── requirements.txt    # Dependências Python
        ├── Dockerfile          # Container da API
        ├── database/           # Configuração database
        ├── models/             # Modelos SQLAlchemy
        ├── services/           # Serviços de negócio
        └── utils/              # Utilitários
```

## 🌟 Funcionalidades

### 1. **Conversação com IA** 🤖
- WebSocket para chat em tempo real
- Integração Minimax M2 Agent
- Extração automática de requisitos técnicos
- Validação e armazenamento de especificações

**Endpoint:** `ws://localhost:8000/ws/conversation/{session_id}`

### 2. **Hardware Bridge** 🔌
- Ponte MQTT ↔ REST API
- Suporte ESP32, Arduino, Raspberry Pi
- Telemetria em tempo real
- Controle remoto de dispositivos

**Endpoints:**
- `GET /hardware/devices/status` - Lista dispositivos
- `GET /hardware/devices/{id}/telemetry` - Telemetria
- `POST /hardware/devices/{id}/send-command` - Enviar comando

### 3. **Geração de Modelos 3D** 🎯
- NVIDIA NIM API para geração automática
- Fallback OpenSCAD para casos complexos
- Validação e correção automática
- Armazenamento MinIO

**Endpoint:** `POST /models/generate`

### 4. **Sistema de Orçamento** 💰
- Integração Octopart API para preços
- Cálculo automático de materiais
- Estimativa de mão de obra
- Markup configurável

**Endpoint:** `POST /budgets/generate`

### 5. **API Gateway Unificado** 🌐
- Autenticação JWT
- Rate limiting
- Request/response logging
- Métricas e health checks

**Endpoints:**
- `GET /health` - Health check
- `POST /auth/login` - Login
- `GET /docs` - Documentação Swagger

## 📊 Base de Dados

### Schema Principal

```sql
-- Usuários e Projetos
users (id, email, password_hash, role, organization)
projects (id, name, description, user_id, status, project_type)

-- Conversação IA
conversation_sessions (id, session_id, user_id, title, status)
specifications (id, project_id, conversation_id, requirements, extracted_params)

-- Hardware e Telemetria  
hardware_devices (id, device_id, device_type, name, status, configuration)
device_telemetry (id, device_id, metric_type, value, recorded_at)
alerts (id, device_id, alert_type, severity, message)

-- Modelos e Simulações
model_3d (id, project_id, name, file_path, generation_method)
simulations (id, project_id, model_id, simulation_type, results, efficiency_score)
budgets (id, project_id, material_cost, labor_cost, final_price)

-- Jobs Assíncronos
jobs (id, job_type, job_data, status, progress, result)
```

## 🔐 Autenticação

### Usuários Padrão

```sql
-- Criados automaticamente pelo setup
admin@3dpot.local / admin123 (Administrator)
operator@3dpot.local / operator123 (Operator)  
viewer@3dpot.local / viewer123 (Viewer)
```

### JWT Tokens

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@3dpot.local", "password": "admin123"}'

# Usar token nos requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/hardware/devices/status
```

## 🧪 Testes

### Teste de Integração

```bash
# Executar todos os testes
./scripts/test-integration.sh

# Teste específico
curl -f http://localhost:8000/health

# Teste de autenticação
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@3dpot.local", "password": "admin123"}'
```

## 📡 MQTT Topics

### Hardware Legado

```bash
# Formato: 3dpot/{device_type}/{device_id}/{metric}

# ESP32 Monitor de Filamento
3dpot/esp32/filament-001/weight    # {"weight_g": 250.5, "percentage": 42.1}
3dpot/esp32/filament-001/status    # {"temperature": 65, "humidity": 45}

# Arduino Esteira
3dpot/arduino/conveyor-001/status  # {"speed": 150, "object_detected": true}
3dpot/arduino/conveyor-001/alert   # {"message": "Objeto detectado", "severity": "info"}

# Raspberry Pi QC
3dpot/raspberry/qc-001/qc_result   # {"result": "pass", "score": 95.5, "defects": []}
3dpot/raspberry/qc-001/status      # {"camera_active": true, "led_ring": true}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. **Portas em Uso**

```bash
# Verificar portas ocupadas
netstat -tuln | grep :8000
lsof -i :8000

# Parar serviço específico
sudo kill -9 $(lsof -t -i:8000)
```

#### 2. **Database Connection Failed**

```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Resetar database
docker-compose down -v
docker-compose up -d
```

#### 3. **Redis Connection Failed**

```bash
# Verificar Redis
docker-compose logs redis

# Limpar cache Redis
docker exec -it 3dpot-redis redis-cli FLUSHALL
```

#### 4. **MQTT Not Connecting**

```bash
# Verificar Mosquitto
docker-compose logs mosquitto

# Testar conexão MQTT
mosquitto_pub -h localhost -t test/topic -m "hello world"
mosquitto_sub -h localhost -t test/topic
```

### Logs Detalhados

```bash
# Ver logs de todos os serviços
docker-compose logs

# Logs de serviço específico
docker-compose logs api-gateway
docker-compose logs postgres
docker-compose logs redis

# Logs em tempo real
docker-compose logs -f api-gateway
```

## 🚀 Próximos Passos

### Sprint 2-3: Conversação IA
- [x] Minimax M2 Agent integration
- [x] WebSocket real-time
- [ ] Interface React chat
- [ ] Spec extractor enhancement

### Sprint 4-5: Geração 3D
- [x] NVIDIA NIM API integration
- [x] OpenSCAD fallback
- [ ] CadQuery pipeline
- [ ] STL validator enhancement

### Sprint 6-7: Simulação
- [ ] Three.js viewer
- [ ] PyBullet physics
- [ ] NVIDIA Ray Tracing
- [ ] Efficiency calculator

### Sprint 8-9: Orçamentos
- [x] Octopart API integration
- [x] Cost calculator
- [ ] PDF generator
- [ ] Email integration

### Sprint 10-11: Production
- [ ] Kubernetes manifests
- [ ] Monitoring (Prometheus/Grafana)
- [ ] CI/CD pipeline
- [ ] SSL/HTTPS setup

## 📞 Suporte

### Issues e Bugs

- **GitHub Issues:** [Reportar problema](https://github.com/dronreef2/3dPot/issues)
- **Documentação API:** http://localhost:8000/docs

### Contato

- **Autor:** MiniMax Agent
- **Data de Criação:** 2025-11-12 22:42:43
- **Versão:** 2.0.0

---

**🎯 3dPot Platform - Transformando Ideias em Protótipos Automatizados!**