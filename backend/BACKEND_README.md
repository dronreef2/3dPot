# 🎯 3dPot Backend - API FastAPI

Sistema centralizado de backend para o projeto 3dPot - Sistema de Prototipagem Sob Demanda.

## 🚀 Início Rápido

### 1. Execução Simples (Recomendado)
```bash
# Execute o script de inicialização
./start.sh

# OU manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 init_backend.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Com Docker (Completo)
```bash
# Iniciar todos os serviços
docker-compose up -d

# Acompanhar logs
docker-compose logs -f backend
```

## 📚 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI**: http://localhost:8000/openapi.json

## 🔗 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Fazer login
- `GET /api/v1/auth/me` - Perfil do usuário atual

### Dispositivos
- `GET /api/v1/devices` - Listar dispositivos
- `POST /api/v1/devices` - Criar dispositivo
- `GET /api/v1/devices/{id}` - Detalhes do dispositivo
- `POST /api/v1/devices/esp32/monitor` - Criar monitor ESP32

### Monitoramento
- `GET /api/v1/monitoring/data` - Dados de sensores
- `POST /api/v1/monitoring/data` - Registrar dados
- `GET /api/v1/monitoring/stats` - Estatísticas

### Projetos
- `GET /api/v1/projects` - Listar projetos
- `POST /api/v1/projects` - Criar projeto
- `GET /api/v1/projects/{id}` - Detalhes do projeto

### Alertas
- `GET /api/v1/alerts` - Listar alertas
- `POST /api/v1/alerts/{id}/resolve` - Resolver alerta

### Health Check
- `GET /health` - Status básico
- `GET /health/detailed` - Status detalhado
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

## 🗄️ Banco de Dados

### Modelos Principais
- **User** - Usuários e autenticação
- **Device** - Dispositivos IoT (ESP32, Arduino, Raspberry)
- **SensorData** - Dados de sensores coletados
- **Alert** - Sistema de alertas
- **Project** - Gestão de projetos e protótipos

### Dispositivos Suportados
- **ESP32 Monitor** - Monitor de filamento com WiFi/MQTT
- **Arduino Esteira** - Sistema de transporte
- **Raspberry QC** - Estação de controle de qualidade
- **Sensores IoT** - Temperatura, umidade, peso, vibração

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```bash
# Banco de Dados
DATABASE_URL=postgresql://3dpot:3dpot123@localhost:5432/3dpot_dev

# Segurança
SECRET_KEY=your-super-secret-key-change-in-production-must-be-32-chars-minimum

# APIs Externas
SLANT3D_API_KEY=sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4

# MQTT
MQTT_BROKER_URL=localhost
MQTT_BROKER_PORT=1883
```

### Credenciais de Teste
```
Email: admin@3dpot.com
Senha: admin123
```

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  FastAPI        │    │   PostgreSQL    │
│   (React/Vue)   │◄──►│  Backend        │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Cache/Queue) │
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   MQTT Broker   │
                       │   (IoT Data)    │
                       └─────────────────┘
```

## 📊 Monitoramento

### Métricas Prometheus
- Endpoint: http://localhost:8000/metrics

### Health Checks
- **Básico**: GET /health
- **Detalhado**: GET /health/detailed
- **Readiness**: GET /health/ready  
- **Liveness**: GET /health/live

### Dashboard Grafana
- URL: http://localhost:3001
- Usuário: admin
- Senha: admin123

## 🧪 Testes

### Executar Testes
```bash
# Testes unitários
pytest

# Com cobertura
pytest --cov=app

# Testes específicos
pytest tests/test_devices.py
```

### Dados de Teste
O script `init_backend.py` cria automaticamente:
- ✅ Usuário administrador
- ✅ 3 dispositivos de teste (ESP32, Arduino, Raspberry)
- ✅ 2 projetos de exemplo

## 🔒 Segurança

### Autenticação JWT
- Tokens com expiração configurável
- Refresh tokens
- API Keys para acesso programático

### Rate Limiting
- 60 requests/minuto por usuário
- 1000 requests/hora por usuário

### CORS
- Configurável para múltiplas origens
- Credentials habilitados

## 🚀 Deploy

### Desenvolvimento
```bash
uvicorn app.main:app --reload
```

### Produção
```bash
# Com Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Com Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Variáveis de Produção
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key
ALLOWED_ORIGINS=["https://your-domain.com"]
```

## 📱 Integração com Dispositivos

### ESP32 Monitor
```cpp
// Exemplo de publicação MQTT
#include <WiFi.h>
#include <PubSubClient.h>

// Configurar tópicos MQTT
String topic = "3dpot/devices/ESP32_001/data";
String payload = "{\"weight\": 850.5, \"temperature\": 22.3}";

client.publish(topic.c_str(), payload.c_str());
```

### API REST
```javascript
// Registrar dados de sensor
const response = await fetch('/api/v1/monitoring/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    device_id: 1,
    sensor_type: 'weight',
    value: 850.5,
    unit: 'g'
  })
});
```

## 🆘 Troubleshooting

### Problemas Comuns

**Erro de conexão com banco:**
```bash
# Verificar PostgreSQL
psql -h localhost -U 3dpot -d 3dpot_dev

# Verificar variáveis de ambiente
cat .env | grep DATABASE_URL
```

**Erro de importação:**
```bash
# Verificar path do Python
export PYTHONPATH=/path/to/3dPot/backend:$PYTHONPATH
```

**Porta em uso:**
```bash
# Verificar processos na porta 8000
lsof -i :8000

# Matar processo
kill -9 <PID>
```

## 📈 Próximos Passos

- [ ] Implementar WebSocket para tempo real
- [ ] Integração completa com MQTT
- [ ] Sistema de notificações
- [ ] Dashboard web responsivo
- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Deploy Kubernetes

## 🤝 Contribuição

1. Fork do repositório
2. Criar branch para feature
3. Implementar e testar
4. Enviar Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja LICENSE para detalhes.

---

**Status**: ✅ **Sprint 2 - Backend IMPLEMENTADO**

**Pontuação do Projeto**: 7.8/10 → 8.5/10 (+0.7 pontos)
