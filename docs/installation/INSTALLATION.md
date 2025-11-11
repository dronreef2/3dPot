# Guia de Instalação - 3dPot v2.0

**Sistema de Prototipagem Sob Demanda**

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+ (recomendado) ou CentOS 8+
- **macOS**: Big Sur 11.0+
- **Windows**: WSL2 com Ubuntu 20.04+

### Software Base
- **Docker** 24.0+ e **Docker Compose** v2.0+
- **Node.js** 18.0+ e **npm** 9.0+
- **Python** 3.10+ e **pip** 23.0+
- **Git** 2.35+

### Hardware Recomendado
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recomendado)
- **Storage**: 50GB+ free space
- **GPU**: Opcional para aceleração 3D

## 🚀 Instalação Rápida

### 1. Clone do Repositório
```bash
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot
```

### 2. Configuração de Ambiente
```bash
# Copiar arquivos de configuração
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Editar configurações (importante para produção!)
nano .env
```

### 3. Build e Startup
```bash
# Build dos containers
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### 4. Acessar Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin123)

## 📦 Instalação Detalhada

### Backend (FastAPI)

#### 1. Ambiente Virtual Python
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 2. Configuração do Banco
```bash
# PostgreSQL via Docker
docker run -d \
  --name 3dpot-postgres \
  -e POSTGRES_DB=3dpot_v2 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Executar migrações
alembic upgrade head
```

#### 3. Configuração Redis
```bash
# Redis via Docker
docker run -d \
  --name 3dpot-redis \
  -p 6379:6379 \
  redis:7-alpine
```

#### 4. Configuração MinIO (S3 Storage)
```bash
# MinIO via Docker
docker run -d \
  --name 3dpot-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v minio-data:/data \
  minio/minio server /data --console-address ":9001"

# Criar bucket
aws --endpoint-url http://localhost:9000 s3 mb s3://3dpot-models \
  --region us-east-1 \
  --profile minio
```

#### 5. Variáveis de Ambiente
```bash
# backend/.env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/3dpot_v2
REDIS_HOST=localhost
REDIS_PORT=6379

# APIs Externas
MINIMAX_API_KEY=your_minimax_api_key
OCTOPART_API_KEY=your_octopart_api_key
DIGIKEY_API_KEY=your_digikey_api_key

# Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=3dpot-models

# Security
SECRET_KEY=your_super_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

#### 6. Executar Backend
```bash
# Desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (React)

#### 1. Dependências Node.js
```bash
cd frontend
npm install
```

#### 2. Configuração Environment
```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
VITE_STORAGE_URL=http://localhost:9000
```

#### 3. Build e Desenvolvimento
```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build
npm run preview
```

### Hardware Legado (Preservação)

#### Arduino
```bash
# Arduino IDE ou PlatformIO
# Upload dos códigos em codigos/arduino/

# Configurar porta serial
sudo usermod -a -G dialout $USER
```

#### ESP32
```bash
# Arduino IDE ou ESP32-IDF
# Upload dos códigos em codigos/esp32/

# Configurar WiFi
# Editar credenciais em cada arquivo .ino
```

#### Raspberry Pi
```bash
# Instalar dependências Python
pip install opencv-python picamera2 RPi.GPIO flask

# Executar códigos em codigos/raspberry-pi/
python estacao_qc.py
```

## 🔧 Configuração Avançada

### Docker Compose Personalizado

#### Multi-environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
    environment:
      - ENVIRONMENT=development

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend/src:/app/src
    environment:
      - VITE_API_URL=http://localhost:8000
```

#### Production Deployment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

  backend:
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped

  frontend:
    build:
      target: production
    restart: unless-stopped
```

### Configuração SSL/TLS

#### Certificado Auto-assinado (Desenvolvimento)
```bash
# Gerar certificado
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Configuração Nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /api {
        proxy_pass http://backend:8000;
    }
    
    location / {
        proxy_pass http://frontend:3000;
    }
}
```

### Monitoramento e Logs

#### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: '3dpot-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

#### Grafana Dashboards
```bash
# Importar dashboards pré-configurados
curl -X POST \
  http://admin:admin123@localhost:3001/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana/dashboard.json
```

## 🧪 Testes

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html

# Testes específicos
python -m pytest tests/unit/test_modeling_service.py -v
python -m pytest tests/integration/test_api_endpoints.py -v
```

### Frontend Tests
```bash
cd frontend
npm test

# Coverage
npm run test -- --coverage

# E2E tests
npm run test:e2e
```

### Testes de Integração
```bash
# Teste completo do pipeline
python tests/e2e/test_complete_workflow.py

# Teste de hardware (requer hardware conectado)
python tests/hardware/test_arduino_integration.py
python tests/hardware/test_esp32_mqtt.py
```

## 📊 Performance Tuning

### Backend Optimization
```python
# main.py - FastAPI optimization
app = FastAPI(
    title="3dPot v2.0",
    # Performance optimizations
    docs_url=None,  # Disable docs in production
    redoc_url=None,
    openapi_url=None,
)

# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

### Frontend Optimization
```javascript
// vite.config.ts - Build optimization
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three', '@react-three/fiber', '@react-three/drei'],
          'ui': ['@headlessui/react', '@heroicons/react'],
        },
      },
    },
  },
});
```

### Database Optimization
```sql
-- PostgreSQL performance tuning
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Backend não inicia
```bash
# Verificar logs
docker-compose logs backend

# Verificar dependências
pip install -r backend/requirements.txt

# Verificar banco
psql -h localhost -U postgres -d 3dpot_v2
```

#### 2. Frontend não carrega
```bash
# Limpar cache
rm -rf frontend/node_modules frontend/.vite
npm install

# Verificar API connectivity
curl http://localhost:8000/api/v1/health
```

#### 3. Modelos 3D não geram
```bash
# Verificar OpenSCAD installation
openscad --version

# Verificar permissões de storage
chmod 755 storage/
ls -la storage/
```

#### 4. Simulação PyBullet falha
```bash
# Reinstalar PyBullet
pip uninstall pybullet
pip install pybullet

# Verificar dependências OpenGL
glxinfo | grep OpenGL
```

### Logs Debugging
```bash
# Backend logs detalhados
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug

# Frontend logs do navegador
# F12 → Console

# Docker logs
docker-compose logs -f backend frontend
```

### Reset Completo
```bash
# Parar serviços
docker-compose down

# Limpar dados
docker volume prune -f
rm -rf storage/*

# Rebuild completo
docker-compose build --no-cache
docker-compose up -d
```

## 🔐 Configuração de Produção

### Environment Variables
```bash
# production.env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/3dpot_v2
REDIS_URL=redis://prod-redis:6379
S3_ENDPOINT_URL=https://your-s3-endpoint.com
MINIMAX_API_KEY=your_production_api_key
SECRET_KEY=your_super_secure_secret_key
```

### SSL/HTTPS
```bash
# Let's Encrypt
certbot --nginx -d yourdomain.com

# Renew automatically
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Backup Strategy
```bash
# Database backup script
#!/bin/bash
pg_dump -h localhost -U postgres 3dpot_v2 > backup_$(date +%Y%m%d).sql

# S3 backup
aws s3 sync storage/ s3://your-backup-bucket/storage/

# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### Monitoring
```bash
# Health checks
curl -f http://localhost:8000/api/v1/health || exit 1

# Resource monitoring
docker stats

# Log monitoring
tail -f backend.log | grep ERROR
```

## 📞 Suporte

### Documentação
- **API Docs**: http://localhost:8000/docs
- **ADR**: docs/architecture/ADR.md
- **Guia de Desenvolvimento**: docs/development/

### Comunidade
- **GitHub Issues**: https://github.com/dronreef2/3dPot/issues
- **Discussions**: https://github.com/dronreef2/3dPot/discussions
- **Wiki**: https://github.com/dronreef2/3dPot/wiki

### Contribuição
1. Fork o repositório
2. Crie uma feature branch
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**3dPot v2.0** - Sistema de Prototipagem Sob Demanda  
*Desenvolvido com ❤️ pela comunidade open-source*