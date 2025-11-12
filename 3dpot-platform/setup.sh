#!/bin/bash
# 3dPot Platform Setup Script
# Criado em: 2025-11-12 22:42:43
# Autor: MiniMax Agent

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
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

# Banner
echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    3dPot Platform Setup                      ║
║               Prototipagem Sob Demanda v2.0                  ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado. Por favor instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose não está instalado. Por favor instale o Docker Compose primeiro."
    exit 1
fi

log_info "Verificando Docker..."
docker --version
docker-compose --version || docker compose version

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    log_info "Criando arquivo .env..."
    cp .env.example .env
    log_success "Arquivo .env criado. Você pode editá-lo para configurar APIs externas."
else
    log_warning "Arquivo .env já existe, pulando criação."
fi

# Verificar se as portas estão disponíveis
log_info "Verificando portas disponíveis..."

PORTS_TO_CHECK=(5432 6379 9000 9001 5672 1883 8000)
PORTS_IN_USE=()

for port in "${PORTS_TO_CHECK[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        PORTS_IN_USE+=($port)
    fi
done

if [ ${#PORTS_IN_USE[@]} -gt 0 ]; then
    log_warning "As seguintes portas estão em uso: ${PORTS_IN_USE[*]}"
    log_warning "Isso pode causar problemas. Considere parar os serviços nessas portas."
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Setup cancelado pelo usuário."
        exit 1
    fi
fi

# Criar diretórios necessários
log_info "Criando diretórios..."
mkdir -p logs
mkdir -p uploads/models
mkdir -p uploads/uploads

log_success "Diretórios criados"

# Baixar imagens Docker se necessário
log_info "Verificando imagens Docker..."

IMAGES_NEEDED=(
    "postgres:15-alpine"
    "redis:7-alpine"
    "minio/minio:latest"
    "rabbitmq:3.12-management-alpine"
    "eclipse-mosquitto:2.0"
)

for image in "${IMAGES_NEEDED[@]}"; do
    if ! docker image inspect "$image" &> /dev/null; then
        log_info "Baixando imagem: $image"
        docker pull "$image"
    else
        log_success "Imagem já existe: $image"
    fi
done

# Construir imagem do API Gateway
log_info "Construindo API Gateway..."
cd services/api-gateway
docker build -t 3dpot-api-gateway .
cd ../..

log_success "API Gateway construído"

# Resetar dados (opcional)
read -p "Resetar todos os dados? (isso apagará todos os dados existentes) (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Resetando dados..."
    docker-compose down -v
    log_success "Dados resetados"
else
    log_info "Pular reset de dados"
fi

# Iniciar serviços
log_info "Iniciando serviços Docker..."
docker-compose up -d

# Aguardar inicialização
log_info "Aguardando inicialização dos serviços..."

# Função para verificar se um serviço está respondendo
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    return 1
}

# Verificar cada serviço
services_to_check=(
    "Database:http://localhost:5432"
    "Redis:http://localhost:6379"
    "MinIO:http://localhost:9000/minio/health/live"
    "RabbitMQ:http://localhost:15672"
    "MQTT:http://localhost:1883"
    "API Gateway:http://localhost:8000/health"
)

all_healthy=true
for service in "${services_to_check[@]}"; do
    IFS=':' read -r name url <<< "$service"
    
    log_info "Verificando $name..."
    if check_service "$name" "$url"; then
        log_success "$name está saudável"
    else
        log_error "$name não respondeu a tempo"
        all_healthy=false
    fi
done

# Status final
echo
if [ "$all_healthy" = true ]; then
    log_success "🎉 3dPot Platform inicializada com sucesso!"
    echo
    echo -e "${GREEN}=== URLs de Acesso ===${NC}"
    echo -e "${BLUE}API Gateway:${NC} http://localhost:8000"
    echo -e "${BLUE}API Docs:${NC}  http://localhost:8000/docs"
    echo -e "${BLUE}MinIO:${NC}     http://localhost:9001 (login: 3dpot / 3dpot123minio)"
    echo -e "${BLUE}RabbitMQ:${NC}  http://localhost:15672 (login: 3dpot / 3dpot123)"
    echo
    echo -e "${GREEN}=== Comandos Úteis ===${NC}"
    echo -e "${YELLOW}docker-compose logs -f${NC}      # Ver logs em tempo real"
    echo -e "${YELLOW}docker-compose down${NC}          # Parar serviços"
    echo -e "${YELLOW}docker-compose up -d${NC}         # Iniciar serviços"
    echo
    echo -e "${GREEN}=== Próximos Passos ===${NC}"
    echo "1. Configure as chaves das APIs no arquivo .env"
    echo "2. Acesse http://localhost:8000/docs para explorar a API"
    echo "3. Execute os scripts de desenvolvimento:"
    echo "   ./scripts/dev-setup.sh"
    echo
else
    log_error "❌ Alguns serviços não inicializaram corretamente"
    echo
    echo -e "${YELLOW}=== Comandos para Debug ===${NC}"
    echo -e "${YELLOW}docker-compose ps${NC}             # Ver status dos containers"
    echo -e "${YELLOW}docker-compose logs${NC}           # Ver logs dos containers"
    echo -e "${YELLOW}docker-compose logs [service]${NC} # Ver logs de um serviço específico"
    exit 1
fi

log_success "Setup concluído! 🎯"