#!/bin/bash

# Script de backup automático para 3dPot
# Executado via cron para backups regulares

set -e

BACKUP_DIR="/backups"
DATA_DIR="/data"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/3dpot-backup-$DATE.tar.gz"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Função de log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $BACKUP_DIR/backup.log
}

log "Iniciando backup do sistema 3dPot..."

# Fazer backup do banco de dados
log "Fazendo backup do banco de dados..."
if [ -f "$DATA_DIR/3dpot.db" ]; then
    cp "$DATA_DIR/3dpot.db" "$BACKUP_DIR/3dpot-db-$DATE.db"
else
    log "Aviso: Banco de dados não encontrado em $DATA_DIR/3dpot.db"
fi

# Fazer backup dos logs
log "Fazendo backup dos logs..."
if [ -d "/app/logs" ]; then
    tar -czf "$BACKUP_DIR/3dpot-logs-$DATE.tar.gz" -C /app logs || true
fi

# Fazer backup das configurações
log "Fazendo backup das configurações..."
tar -czf "$BACKUP_DIR/3dpot-configs-$DATE.tar.gz" \
    /app/server \
    /etc/nginx/conf.d \
    /etc/letsencrypt/live \
    2>/dev/null || true

# Fazer backup dos uploads e dados do usuário
log "Fazendo backup dos dados do usuário..."
tar -czf "$BACKUP_DIR/3dpot-data-$DATE.tar.gz" \
    /var/www/static \
    2>/dev/null || true

# Criar arquivo de metadados
cat > "$BACKUP_DIR/3dpot-meta-$DATE.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "version": "1.0.0",
    "hostname": "$(hostname)",
    "kernel": "$(uname -r)",
    "docker_version": "$(docker --version)",
    "files": [
        "3dpot-db-$DATE.db",
        "3dpot-logs-$DATE.tar.gz",
        "3dpot-configs-$DATE.tar.gz",
        "3dpot-data-$DATE.tar.gz"
    ]
}
EOF

# Comprimir todos os backups
log "Comprimindo backups..."
tar -czf $BACKUP_FILE \
    "$BACKUP_DIR/3dpot-db-$DATE.db" \
    "$BACKUP_DIR/3dpot-logs-$DATE.tar.gz" \
    "$BACKUP_DIR/3dpot-configs-$DATE.tar.gz" \
    "$BACKUP_DIR/3dpot-data-$DATE.tar.gz" \
    "$BACKUP_DIR/3dpot-meta-$DATE.json"

# Remover arquivos individuais
rm -f "$BACKUP_DIR/3dpot-db-$DATE.db"
rm -f "$BACKUP_DIR/3dpot-logs-$DATE.tar.gz"
rm -f "$BACKUP_DIR/3dpot-configs-$DATE.tar.gz"
rm -f "$BACKUP_DIR/3dpot-data-$DATE.tar.gz"
rm -f "$BACKUP_DIR/3dpot-meta-$DATE.json"

# Verificar tamanho do backup
BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
log "Backup criado: $BACKUP_FILE ($BACKUP_SIZE)"

# Limpar backups antigos
log "Limpando backups com mais de $RETENTION_DAYS dias..."
find $BACKUP_DIR -name "3dpot-backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Manter apenas os últimos 10 backups
ls -t $BACKUP_DIR/3dpot-backup-*.tar.gz | tail -n +11 | xargs -r rm

# Verificar espaço em disco
DISK_USAGE=$(df $BACKUP_DIR | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    log "AVISO: Uso de disco alto no diretório de backup ($DISK_USAGE%)"
fi

log "Backup concluído com sucesso!"

# Verificar integridade do backup
if tar -tzf $BACKUP_FILE >/dev/null 2>&1; then
    log "Verificação de integridade: OK"
else
    log "ERRO: Backup corrompido!"
    exit 1
fi

# Enviar notificação (se configurado)
if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Backup 3dPot concluído: $BACKUP_FILE ($BACKUP_SIZE)\"}" \
        $SLACK_WEBHOOK || true
fi

log "Processo de backup finalizado."