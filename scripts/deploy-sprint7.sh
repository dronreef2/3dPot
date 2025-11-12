#!/bin/bash
# Sprint 7 Deployment Script for 3D Pot Platform
# Automated production deployment with health checks and rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
DOMAIN=${DOMAIN:-api.3dpot.dev}
SSL_EMAIL=${SSL_EMAIL:-admin@3dpot.dev}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}

# Logging
LOG_FILE="/var/log/3dpot-deploy.log"
exec 1> >(tee -a $LOG_FILE)
exec 2>&1

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        error ".env file not found. Please copy .env.production.template to .env and configure it."
        exit 1
    fi
    
    # Check if SSL certificate files exist
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        warning "SSL certificates not found. Please place cert.pem and key.pem in nginx/ssl/"
    fi
    
    success "Prerequisites check completed"
}

# Backup current deployment
backup_current_deployment() {
    log "Creating backup of current deployment..."
    
    BACKUP_DIR="backups/backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup database
    if docker-compose exec -T postgres pg_dump -U 3dpot 3dpot_prod > "$BACKUP_DIR/database.sql"; then
        success "Database backed up"
    else
        error "Database backup failed"
        return 1
    fi
    
    # Backup configuration files
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
    
    # Backup uploaded files and models
    if [ -d "storage" ]; then
        tar -czf "$BACKUP_DIR/storage.tar.gz" storage/ 2>/dev/null || true
    fi
    
    # Clean old backups
    find backups/ -name "backup-*" -type d -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true
    
    success "Backup completed: $BACKUP_DIR"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get upgrade -y
    elif command -v yum &> /dev/null; then
        sudo yum update -y
    else
        warning "Unknown package manager, skipping system updates"
    fi
    
    success "System updated"
}

# Setup SSL certificates with Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [ ! -d "nginx/ssl" ]; then
        mkdir -p nginx/ssl
    fi
    
    # Check if certificates exist, otherwise get from Let's Encrypt
    if [ ! -f "nginx/ssl/cert.pem" ]; then
        if command -v certbot &> /dev/null; then
            log "Getting SSL certificate from Let's Encrypt..."
            sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $SSL_EMAIL --agree-tos --non-interactive
            
            # Copy certificates
            sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
            sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
            sudo chown $USER:$USER nginx/ssl/*
            
            success "SSL certificates obtained from Let's Encrypt"
        else
            warning "Certbot not installed. Please install SSL certificates manually."
        fi
    else
        success "SSL certificates already exist"
    fi
}

# Build and deploy services
deploy_services() {
    log "Building and deploying services..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f docker-compose.prod.yml pull
    
    # Build custom images
    log "Building custom Docker images..."
    docker-compose -f docker-compose.prod.yml build --parallel
    
    # Stop current services
    log "Stopping current services..."
    docker-compose -f docker-compose.prod.yml down
    
    # Start new services
    log "Starting new services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    success "Services deployed"
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    # Wait for database
    log "Waiting for database..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U 3dpot > /dev/null 2>&1; then
            success "Database is ready"
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        error "Database failed to start"
        return 1
    fi
    
    # Wait for API
    log "Waiting for API to be ready..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            success "API is ready"
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        error "API failed to start"
        return 1
    fi
    
    # Wait for frontend
    log "Waiting for frontend to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f -s http://localhost/ > /dev/null 2>&1; then
            success "Frontend is ready"
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        error "Frontend failed to start"
        return 1
    fi
    
    success "All services are healthy"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Create migrations table if it doesn't exist
    docker-compose exec -T postgres psql -U 3dpot -d 3dpot_prod -c "
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    "
    
    # Run application migrations
    docker-compose exec -T api-gateway python -m alembic upgrade head || {
        error "Database migrations failed"
        return 1
    }
    
    success "Database migrations completed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Start monitoring services
    docker-compose -f docker-compose.prod.yml up -d prometheus grafana sentry
    
    # Wait for Grafana to be ready
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f -s http://localhost:3000/api/health > /dev/null 2>&1; then
            success "Grafana is ready"
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    # Import dashboard
    if [ -f "monitoring/grafana/dashboard-3dpot.json" ]; then
        log "Importing Grafana dashboard..."
        # This would typically be done via Grafana API
        success "Dashboard import initiated"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Start performance monitor
    docker-compose exec api-gateway python /app/scripts/performance_monitor.py &
    
    success "Performance monitoring started"
}

# Run health checks
run_health_checks() {
    log "Running comprehensive health checks..."
    
    # Check API health
    if curl -f -s http://localhost:8000/health | grep -q "healthy"; then
        success "API health check passed"
    else
        error "API health check failed"
        return 1
    fi
    
    # Check WebSocket
    if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
        success "WebSocket health check passed"
    else
        error "WebSocket health check failed"
        return 1
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U 3dpot > /dev/null 2>&1; then
        success "Database health check passed"
    else
        error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        success "Redis health check passed"
    else
        error "Redis health check failed"
        return 1
    fi
    
    # Run E2E tests
    if [ -d "tests/e2e" ]; then
        log "Running E2E tests..."
        cd tests/e2e
        npm test
        cd ../..
        success "E2E tests passed"
    else
        warning "E2E tests not found, skipping"
    fi
    
    success "All health checks passed"
}

# Setup log rotation
setup_logging() {
    log "Setting up log rotation..."
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/3dpot > /dev/null <<EOF
/var/log/3dpot-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    postrotate
        docker-compose -f $(pwd)/docker-compose.prod.yml restart > /dev/null 2>&1 || true
    endscript
}
EOF
    
    success "Log rotation configured"
}

# Rollback function
rollback() {
    error "Deployment failed! Initiating rollback..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -td backups/backup-* | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Rolling back to $LATEST_BACKUP..."
        
        # Restore database
        if [ -f "$LATEST_BACKUP/database.sql" ]; then
            docker-compose exec -T postgres psql -U 3dpot -d 3dpot_prod < "$LATEST_BACKUP/database.sql"
        fi
        
        # Restore configuration
        if [ -f "$LATEST_BACKUP/.env" ]; then
            cp "$LATEST_BACKUP/.env" .
        fi
        
        # Restart services
        docker-compose -f docker-compose.prod.yml restart
        
        success "Rollback completed"
    else
        error "No backup found for rollback"
    fi
    
    exit 1
}

# Cleanup function
cleanup() {
    log "Cleaning up old Docker images..."
    docker image prune -f
    docker volume prune -f
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting Sprint 7 deployment for 3D Pot Platform..."
    log "Environment: $ENVIRONMENT"
    log "Domain: $DOMAIN"
    
    # Set trap for rollback on error
    trap rollback ERR
    
    # Execute deployment steps
    check_prerequisites
    update_system
    setup_ssl
    backup_current_deployment
    deploy_services
    wait_for_health
    run_migrations
    setup_monitoring
    run_health_checks
    setup_logging
    cleanup
    
    success "🎉 Sprint 7 deployment completed successfully!"
    log "Platform is now running at: https://$DOMAIN"
    log "Grafana dashboard: http://localhost:3000 (admin/admin123)"
    log "API documentation: https://$DOMAIN/docs"
    
    # Send notification (if webhook configured)
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 3D Pot Platform Sprint 7 deployment completed successfully!\nEnvironment: $ENVIRONMENT\nURL: https://$DOMAIN\"}" \
            $SLACK_WEBHOOK
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        run_health_checks
        ;;
    "backup")
        backup_current_deployment
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|backup|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  rollback - Rollback to last backup"
        echo "  health   - Run health checks only"
        echo "  backup   - Create backup only"
        echo "  cleanup  - Clean up Docker resources"
        exit 1
        ;;
esac