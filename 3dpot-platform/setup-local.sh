#!/bin/bash
# 3dPot Platform Local Setup (sem Docker)
# Criado em: 2025-11-12 22:42:43
# Autor: MiniMax Agent

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║              3dPot Platform Setup (Local)                    ║
║               Prototipagem Sob Demanda v2.0                  ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado"
    exit 1
fi

# Verificar PostgreSQL
if ! command -v psql &> /dev/null; then
    log_warning "PostgreSQL não encontrado. Instalar: sudo apt install postgresql postgresql-contrib"
fi

# Verificar Redis
if ! command -v redis-server &> /dev/null; then
    log_warning "Redis não encontrado. Instalar: sudo apt install redis-server"
fi

# Verificar MinIO
if ! command -v minio &> /dev/null; then
    log_warning "MinIO não encontrado. Instalando via Docker ou download manual"
fi

# Criar diretórios
log_info "Criando diretórios..."
mkdir -p logs data/minio data/postgres data/redis

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    log_info "Criando arquivo .env..."
    cat > .env << 'EOF'
# 3dPot Platform Configuration (Local)
DATABASE_URL=postgresql://3dpot:3dpot123@localhost:5432/3dpot_dev
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=3dpot
MINIO_SECRET_KEY=3dpot123minio
RABBITMQ_URL=amqp://localhost:5672
MQTT_BROKER=mqtt://localhost:1883
JWT_SECRET=3dpot-secret-key-2025-super-secure-32-chars-minimum
ENVIRONMENT=development
EOF
    log_success "Arquivo .env criado"
fi

# Instalar dependências Python
log_info "Instalando dependências Python..."
cd services/api-gateway

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

cd ../../..

log_success "Dependências Python instaladas"

# Setup database local (se PostgreSQL estiver disponível)
if command -v psql &> /dev/null; then
    log_info "Configurando PostgreSQL local..."
    
    # Criar usuário e database
    sudo -u postgres psql << EOF
CREATE USER 3dpot WITH PASSWORD '3dpot123';
CREATE DATABASE 3dpot_dev OWNER 3dpot;
GRANT ALL PRIVILEGES ON DATABASE 3dpot_dev TO 3dpot;
EOF
    
    # Executar schema
    if [ -f "init-scripts/01-init-database.sql" ]; then
        PGPASSWORD=3dpot123 psql -U 3dpot -h localhost -d 3dpot_dev -f init-scripts/01-init-database.sql
    fi
    
    log_success "PostgreSQL configurado"
fi

log_success "✅ Setup local concluído!"
echo
echo -e "${GREEN}=== Próximos Passos ===${NC}"
echo "1. Iniciar PostgreSQL: sudo systemctl start postgresql"
echo "2. Iniciar Redis: sudo systemctl start redis-server"
echo "3. Iniciar MinIO: ./minio server data/minio"
echo "4. Iniciar API Gateway: cd services/api-gateway && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo
echo -e "${BLUE}URLs:${NC}"
echo "API Gateway: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"