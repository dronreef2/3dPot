#!/bin/bash

# 3dPot v2.0 - Script de Inicialização do Sprint 1
# Configura ambiente de desenvolvimento local com Docker

set -e

echo "🚀 Iniciando 3dPot v2.0 - Sprint 1"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale o Docker."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose."
    exit 1
fi

print_status "Docker e Docker Compose encontrados"

# Create necessary directories
print_status "Criando diretórios necessários..."
mkdir -p database/init
mkdir -p database/migrations
mkdir -p redis
mkdir -p rabbitmq
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning
mkdir -p monitoring/prometheus
mkdir -p storage/uploads
mkdir -p storage/logs

# Create Redis configuration
print_status "Configurando Redis..."
cat > redis/redis.conf << EOF
# Redis configuration for 3dPot
port 6379
bind 0.0.0.0
timeout 0
tcp-keepalive 300
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
EOF

# Create RabbitMQ configuration
print_status "Configurando RabbitMQ..."
cat > rabbitmq/rabbitmq.conf << EOF
# RabbitMQ configuration for 3dPot
default_user = 3dpot
default_pass = 3dpot123
default_user_tags = administrator
default_permissions = .* .* .*
listeners.tcp.default = 5672
management.tcp.port = 15672
log.file.level = info
log.console = true
log.console.level = info
EOF

# Create Prometheus configuration
print_status "Configurando Prometheus..."
cat > monitoring/prometheus.yml << EOF
# Prometheus configuration for 3dPot
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: '3dpot-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15672']

rule_files:
  - "rules/*.yml"
EOF

# Create Grafana provisioning configuration
print_status "Configurando Grafana..."
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1
providers:
  - name: '3dPot Dashboard'
    orgId: 1
    folder: '3dPot'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Criando arquivo .env..."
    cp backend/.env.example .env
    print_warning "Por favor, edite o arquivo .env com suas configurações"
fi

# Build Docker images
print_status "Construindo imagens Docker..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Start services
print_status "Iniciando serviços..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
print_status "Aguardando serviços ficarem prontos..."
sleep 30

# Check service health
print_status "Verificando saúde dos serviços..."

# Check PostgreSQL
if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U 3dpot -d 3dpot_dev; then
    print_success "PostgreSQL está rodando"
else
    print_error "PostgreSQL não está respondendo"
fi

# Check Redis
if docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping; then
    print_success "Redis está rodando"
else
    print_error "Redis não está respondendo"
fi

# Check MinIO
if curl -f http://localhost:9000/minio/health/live; then
    print_success "MinIO está rodando"
else
    print_warning "MinIO pode não estar completamente pronto"
fi

# Check Backend health
if curl -f http://localhost:8000/health; then
    print_success "Backend está rodando"
else
    print_warning "Backend pode não estar completamente pronto"
fi

# Check Frontend
if curl -f http://localhost:3000; then
    print_success "Frontend está rodando"
else
    print_warning "Frontend pode não estar completamente pronto"
fi

print_status "Serviços iniciados!"
echo ""
echo "🌐 URLs de Acesso:"
echo "===================================="
echo "Frontend (React):      http://localhost:3000"
echo "Backend API (FastAPI): http://localhost:8000"
echo "Documentação API:      http://localhost:8000/docs"
echo "MinIO Console:         http://localhost:9001 (minioadmin/minioadmin123)"
echo "Grafana:              http://localhost:3001 (admin/admin123)"
echo "Prometheus:           http://localhost:9090"
echo "RabbitMQ Management:  http://localhost:15672 (3dpot/3dpot123)"
echo ""
echo "📊 Databases:"
echo "PostgreSQL: localhost:5432 (3dpot/3dpot123/3dpot_dev)"
echo "Redis:      localhost:6379 (password: redis123)"
echo ""
echo "📝 Comandos Úteis:"
echo "docker-compose -f docker-compose.dev.yml logs -f backend"
echo "docker-compose -f docker-compose.dev.yml logs -f frontend"
echo "docker-compose -f docker-compose.dev.yml down"
echo ""

print_success "3dPot v2.0 Sprint 1 iniciado com sucesso!"
print_warning "Lembre-se de configurar as chaves de API no arquivo .env"