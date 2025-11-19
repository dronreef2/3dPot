#!/bin/bash

# Script de Deploy Automatizado para 3dPot
# Inclui SSL/HTTPS com Let's Encrypt, backup, monitoring e rollback
# Autor: MiniMax Agent
# Versão: 1.0

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
DOMAIN="3dpot.com.br"
EMAIL="admin@3dpot.com.br"
BACKUP_DIR="/opt/3dpot-backups"
LOG_FILE="/var/log/3dpot-deploy.log"
PROJECT_DIR="/opt/3dpot"
COMPOSE_FILE="docker-compose.yml"

# Funções utilitárias
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    echo "[ERROR] $1" >> $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
    echo "[WARNING] $1" >> $LOG_FILE
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
    echo "[INFO] $1" >> $LOG_FILE
}

# Verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."
    
    # Verificar se está rodando como root ou com sudo
    if [[ $EUID -eq 0 ]]; then
        error "Este script não deve ser executado como root. Execute como usuário do sistema."
    fi
    
    # Verificar se Docker está instalado
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Instale Docker primeiro."
    fi
    
    # Verificar se Docker Compose está instalado
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado. Instale Docker Compose primeiro."
    fi
    
    # Verificar se o domínio resolve
    if ! nslookup $DOMAIN &> /dev/null; then
        warning "Domínio $DOMAIN não resolve. Certifique-se de que o DNS esteja configurado."
    fi
    
    log "Pré-requisitos verificados com sucesso!"
}

# Configurar diretórios
setup_directories() {
    log "Configurando diretórios..."
    
    # Criar diretórios necessários
    sudo mkdir -p $PROJECT_DIR
    sudo mkdir -p $BACKUP_DIR
    sudo mkdir -p /var/log/3dpot
    sudo mkdir -p /etc/3dpot
    
    # Definir permissões
    sudo chown $USER:$USER $PROJECT_DIR
    sudo chown $USER:$USER $BACKUP_DIR
    sudo chmod 755 $PROJECT_DIR
    sudo chmod 755 $BACKUP_DIR
    
    log "Diretórios configurados!"
}

# Criar arquivo .env se não existir
create_env_file() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        log "Criando arquivo .env..."
        
        cat > $PROJECT_DIR/.env << EOF
# Configurações do Sistema 3dPot
# Gerado automaticamente em $(date)

# URLs e domínios
FRONTEND_URL=https://$DOMAIN
DOMAIN=$DOMAIN

# JWT
JWT_SECRET=$(openssl rand -base64 32)
JWT_EXPIRATION=1h
REFRESH_TOKEN_EXPIRATION=7d

# Email (configurar conforme necessário)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Grafana
GRAFANA_ADMIN_PASSWORD=admin123

# Configurações de produção
NODE_ENV=production
LOG_LEVEL=info

# Hardware (configurar conforme hardware real)
ESP32_MQTT_BROKER=mqtt://mqtt-broker:1883
ARDUINO_SERIAL_PORT=/dev/ttyACM0
RPI_API_URL=http://raspberry-pi:5000

# Portas
FRONTEND_PORT=80
BACKEND_PORT=3000
NGINX_PORT=80
NGINX_SSL_PORT=443
EOF
        
        log "Arquivo .env criado! Configure as variáveis conforme necessário."
    else
        info "Arquivo .env já existe."
    fi
}

# Backup da instalação atual
backup_current() {
    if [ -d "$PROJECT_DIR" ] && [ "$(ls -A $PROJECT_DIR)" ]; then
        log "Fazendo backup da instalação atual..."
        
        BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf $BACKUP_FILE -C $(dirname $PROJECT_DIR) $(basename $PROJECT_DIR)
        
        # Manter apenas os últimos 10 backups
        ls -t $BACKUP_DIR/backup-*.tar.gz | tail -n +11 | xargs -r rm
        
        log "Backup criado: $BACKUP_FILE"
    else
        info "Nenhuma instalação anterior encontrada para backup."
    fi
}

# Instalar/renovar certificado SSL
setup_ssl() {
    log "Configurando SSL com Let's Encrypt..."
    
    # Instalar certbot se não estiver instalado
    if ! command -v certbot &> /dev/null; then
        log "Instalando Certbot..."
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Parar Nginx se estiver rodando
    sudo docker-compose -f $PROJECT_DIR/$COMPOSE_FILE stop nginx || true
    
    # Obter/renovar certificado
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        log "Renovando certificado SSL..."
        sudo certbot renew
    else
        log "Obtendo novo certificado SSL..."
        sudo certbot certonly --standalone --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN -d www.$DOMAIN
    fi
    
    # Copiar certificados para o diretório do projeto
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/nginx/ssl/3dpot.crt
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/nginx/ssl/3dpot.key
    sudo chown $USER:$USER $PROJECT_DIR/nginx/ssl/3dpot.*
    sudo chmod 644 $PROJECT_DIR/nginx/ssl/3dpot.crt
    sudo chmod 600 $PROJECT_DIR/nginx/ssl/3dpot.key
    
    # Configurar renovação automática
    echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'sudo systemctl reload nginx'" | sudo crontab -
    
    log "SSL configurado com sucesso!"
}

# Deploy da aplicação
deploy_application() {
    log "Fazendo deploy da aplicação..."
    
    cd $PROJECT_DIR
    
    # Construir imagens
    log "Construindo imagens Docker..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # Iniciar serviços
    log "Iniciando serviços..."
    docker-compose -f $COMPOSE_FILE up -d
    
    # Aguardar serviços ficarem saudáveis
    log "Aguardando serviços ficarem disponíveis..."
    sleep 30
    
    # Verificar status dos serviços
    docker-compose -f $COMPOSE_FILE ps
}

# Configurar firewall
setup_firewall() {
    log "Configurando firewall..."
    
    if command -v ufw &> /dev/null; then
        # Permitir SSH, HTTP e HTTPS
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # Permitir portas de monitoramento (apenas local)
        sudo ufw allow from 172.20.0.0/16 to any port 9090
        sudo ufw allow from 172.20.0.0/16 to any port 3001
        sudo ufw allow from 172.20.0.0/16 to any port 1880
        
        # Habilitar firewall
        sudo ufw --force enable
        
        log "Firewall configurado!"
    else
        warning "UFW não encontrado. Configure o firewall manualmente."
    fi
}

# Configurar monitoramento
setup_monitoring() {
    log "Configurando sistema de monitoramento..."
    
    # Verificar se Grafana está rodando
    if curl -f http://localhost:3001 &> /dev/null; then
        log "Grafana disponível em http://localhost:3001"
        log "Usuário: admin, Senha: admin123"
        log "Configure as senhas e dashboards após o primeiro login!"
    else
        warning "Grafana não está respondendo."
    fi
    
    # Verificar Prometheus
    if curl -f http://localhost:9090 &> /dev/null; then
        log "Prometheus disponível em http://localhost:9090"
    else
        warning "Prometheus não está respondendo."
    fi
}

# Verificar saúde do sistema
health_check() {
    log "Executando verificação de saúde..."
    
    # Verificar se todos os containers estão rodando
    if ! docker-compose -f $PROJECT_DIR/$COMPOSE_FILE ps | grep -q "Up"; then
        error "Alguns containers não estão rodando."
    fi
    
    # Verificar conectividade HTTP
    if ! curl -f http://localhost/health &> /dev/null; then
        error "Nginx não está respondendo."
    fi
    
    # Verificar backend
    if ! curl -f http://localhost/api/health &> /dev/null; then
        error "Backend não está respondendo."
    fi
    
    # Verificar se o site carrega
    if ! curl -I http://localhost/ | grep -q "200 OK"; then
        error "Frontend não está carregando."
    fi
    
    log "Verificação de saúde concluída com sucesso!"
}

# Configurar logrotate
setup_logrotate() {
    log "Configurando rotação de logs..."
    
    sudo tee /etc/logrotate.d/3dpot > /dev/null << EOF
$PROJECT_DIR/**/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -f $PROJECT_DIR/$COMPOSE_FILE restart > /dev/null 2>&1
    endscript
}
EOF
    
    log "Logrotate configurado!"
}

# Função de rollback
rollback() {
    if [ -z "$1" ]; then
        echo "Uso: $0 rollback <arquivo-backup.tar.gz>"
        exit 1
    fi
    
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        error "Arquivo de backup não encontrado: $backup_file"
    fi
    
    warning "Executando rollback..."
    warning "Esta ação irá parar a aplicação e restaurar a versão do backup."
    
    read -p "Confirma o rollback? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Rollback cancelado."
        exit 0
    fi
    
    # Parar aplicação atual
    docker-compose -f $PROJECT_DIR/$COMPOSE_FILE down
    
    # Fazer backup da versão atual
    if [ -d "$PROJECT_DIR" ]; then
        cp -r $PROJECT_DIR "$PROJECT_DIR.backup.$(date +%Y%m%d-%H%M%S)"
    fi
    
    # Restaurar backup
    tar -xzf $backup_file -C $(dirname $PROJECT_DIR)
    
    # Reiniciar aplicação
    cd $PROJECT_DIR
    docker-compose -f $COMPOSE_FILE up -d
    
    log "Rollback concluído!"
}

# Mostrar status
show_status() {
    log "Status do sistema 3dPot:"
    
    echo -e "\n${BLUE}=== CONTAINERS ===${NC}"
    docker-compose -f $PROJECT_DIR/$COMPOSE_FILE ps
    
    echo -e "\n${BLUE}=== USO DE RECURSOS ===${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    echo -e "\n${BLUE}=== LOGS RECENTES ===${NC}"
    docker-compose -f $PROJECT_DIR/$COMPOSE_FILE logs --tail=20
    
    echo -e "\n${BLUE}=== URLs DISPONÍVEIS ===${NC}"
    echo "Frontend: https://$DOMAIN"
    echo "Grafana: http://localhost:3001 (admin/admin123)"
    echo "Prometheus: http://localhost:9090"
    echo "Node-RED: http://localhost:1880"
}

# Função principal
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_directories
            create_env_file
            backup_current
            setup_ssl
            deploy_application
            setup_firewall
            setup_monitoring
            setup_logrotate
            health_check
            
            log "=========================================="
            log "🎉 DEPLOY CONCLUÍDO COM SUCESSO! 🎉"
            log "=========================================="
            log "URLs disponíveis:"
            log "- Frontend: https://$DOMAIN"
            log "- API: https://$DOMAIN/api"
            log "- Grafana: http://localhost:3001"
            log "- Prometheus: http://localhost:9090"
            log ""
            log "Próximos passos:"
            log "1. Configure as variáveis no arquivo $PROJECT_DIR/.env"
            log "2. Configure as senhas do Grafana e outros serviços"
            log "3. Configure o hardware real (ESP32, Arduino, Raspberry Pi)"
            log "4. Configure alertas no Grafana/Prometheus"
            log ""
            log "Para monitorar: $0 status"
            log "Para rollback: $0 rollback <arquivo-backup.tar.gz>"
            ;;
            
        "rollback")
            rollback "$2"
            ;;
            
        "status")
            show_status
            ;;
            
        "backup")
            backup_current
            ;;
            
        "logs")
            if [ -n "$2" ]; then
                docker-compose -f $PROJECT_DIR/$COMPOSE_FILE logs -f "$2"
            else
                docker-compose -f $PROJECT_DIR/$COMPOSE_FILE logs
            fi
            ;;
            
        "restart")
            log "Reiniciando serviços..."
            docker-compose -f $PROJECT_DIR/$COMPOSE_FILE restart
            health_check
            ;;
            
        "stop")
            log "Parando serviços..."
            docker-compose -f $PROJECT_DIR/$COMPOSE_FILE down
            ;;
            
        "update")
            log "Atualizando aplicação..."
            backup_current
            git pull origin main || true
            deploy_application
            health_check
            ;;
            
        *)
            echo "Uso: $0 {deploy|rollback|status|backup|logs|restart|stop|update}"
            echo ""
            echo "Comandos disponíveis:"
            echo "  deploy     - Deploy completo do sistema"
            echo "  rollback   - Rollback para versão anterior"
            echo "  status     - Mostrar status do sistema"
            echo "  backup     - Fazer backup da instalação atual"
            echo "  logs       - Ver logs (seguir com nome do serviço)"
            echo "  restart    - Reiniciar todos os serviços"
            echo "  stop       - Parar todos os serviços"
            echo "  update     - Atualizar aplicação (git pull + deploy)"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"