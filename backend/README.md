# 3dPot Backend - API Centralizada

## Visão Geral
API FastAPI centralizada para o projeto 3dPot, fornecendo backend unificado para todos os dispositivos IoT.

## Arquitetura
- **FastAPI**: Framework web moderno e rápido
- **PostgreSQL**: Banco de dados principal
- **WebSocket**: Comunicação em tempo real
- **MQTT**: Protocolo IoT
- **JWT**: Autenticação e autorização
- **Redis**: Cache e sessões

## Estrutura do Projeto
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI principal
│   ├── config.py            # Configurações
│   ├── database.py          # Conexão com banco
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Esquemas Pydantic
│   ├── routers/             # Rotas da API
│   ├── services/            # Lógica de negócio
│   ├── auth/               # Autenticação
│   ├── websocket/          # WebSocket handlers
│   ├── mqtt/               # MQTT client
│   └── utils/              # Utilitários
├── tests/                  # Testes unitários
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
├── Dockerfile            # Container Docker
└── docker-compose.yml     # Orquestração de serviços
```

## Funcionalidades
- ✅ Autenticação JWT
- ✅ CRUD de dispositivos
- ✅ Monitoramento em tempo real
- ✅ Integração MQTT
- ✅ Dashboard unificado
- ✅ Documentação Swagger automática

## Setup Local
1. Clone o repositório
2. Configure as variáveis de ambiente
3. Instale dependências: `pip install -r requirements.txt`
4. Execute: `uvicorn app.main:app --reload`

## Deploy
- Docker: `docker-compose up`
- Produção: Configurar variáveis de ambiente de produção

## API Endpoints
- `/auth/` - Endpoints de autenticação
- `/devices/` - Gerenciamento de dispositivos
- `/monitoring/` - Dados de monitoramento
- `/reports/` - Relatórios e analytics
- `/websocket` - Comunicação em tempo real
