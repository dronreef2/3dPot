# Disaster Recovery Scripts - 3dPot v2.0

## Sprint 9: Backup and Restore Procedures

Este diretório contém scripts para backup e restore de dados críticos do sistema 3dPot.

## 📋 Pré-requisitos

### Ferramentas Necessárias
- **PostgreSQL Client Tools** (`pg_dump`, `pg_restore`, `psql`)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install postgresql-client
  
  # macOS
  brew install postgresql
  
  # Verificar instalação
  pg_dump --version
  ```

- **Python 3.8+** (já incluído no ambiente)

### Variáveis de Ambiente
Configure as seguintes variáveis antes de executar os scripts:

```bash
# Database connection
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=3dpot_dev
export POSTGRES_USER=3dpot
export POSTGRES_PASSWORD=3dpot123

# Backup directory (opcional)
export BACKUP_DIR=./backups

# Storage directory (opcional)
export STORAGE_DIR=./storage
```

Ou use um arquivo `.env` (carregado automaticamente se disponível).

## 🔄 Backup

### Uso Básico

```bash
# Backup completo (database + storage)
python scripts/dr/backup.py

# Apenas database (mais rápido)
python scripts/dr/backup.py --skip-storage

# Especificar diretório de backup
python scripts/dr/backup.py --backup-dir /path/to/backups

# Manter apenas últimos 3 backups
python scripts/dr/backup.py --keep 3
```

### Saída Esperada

```
2025-11-20 14:30:00 - INFO - Backup service initialized. Backup dir: ./backups
2025-11-20 14:30:01 - INFO - Available disk space: 50000.00 MB
2025-11-20 14:30:02 - INFO - Starting database backup...
2025-11-20 14:30:15 - INFO - Database backup completed: ./backups/db_backup_20251120_143000.sql
2025-11-20 14:30:15 - INFO - Backup size: 125.50 MB
2025-11-20 14:30:16 - INFO - Starting storage backup...
2025-11-20 14:30:30 - INFO - Storage backup completed: ./backups/storage_backup_20251120_143000.tar.gz
2025-11-20 14:30:30 - INFO - Backup size: 450.25 MB
2025-11-20 14:30:31 - INFO - Backup manifest created: ./backups/backup_manifest_20251120_143000.json
2025-11-20 14:30:32 - INFO - Backup completed successfully!

✅ Backup completed successfully!
Database: ./backups/db_backup_20251120_143000.sql
Storage: ./backups/storage_backup_20251120_143000.tar.gz
Manifest: ./backups/backup_manifest_20251120_143000.json
```

### Arquivos Gerados

Para cada backup, são criados 3 arquivos:

1. **`db_backup_<timestamp>.sql`** - Dump do PostgreSQL (formato custom, compactado)
2. **`storage_backup_<timestamp>.tar.gz`** - Arquivo tar.gz com arquivos de storage
3. **`backup_manifest_<timestamp>.json`** - Manifesto com metadados do backup

Exemplo de manifesto:
```json
{
  "timestamp": "20251120_143000",
  "backup_date": "2025-11-20T14:30:00",
  "database": {
    "host": "localhost",
    "port": "5432",
    "database": "3dpot_dev",
    "backup_file": "./backups/db_backup_20251120_143000.sql",
    "size_mb": 125.5
  },
  "storage": {
    "backup_file": "./backups/storage_backup_20251120_143000.tar.gz",
    "size_mb": 450.25
  },
  "total_size_mb": 575.75
}
```

### Automação com Cron

Backup diário às 3:00 AM:
```bash
# Editar crontab
crontab -e

# Adicionar linha
0 3 * * * cd /path/to/3dPot && /usr/bin/python3 scripts/dr/backup.py --keep 7 >> logs/backup.log 2>&1
```

Backup semanal completo:
```bash
# Domingo às 2:00 AM
0 2 * * 0 cd /path/to/3dPot && /usr/bin/python3 scripts/dr/backup.py --keep 4 >> logs/backup_weekly.log 2>&1
```

## 🔙 Restore

### Listar Backups Disponíveis

```bash
python scripts/dr/restore.py --list
```

Saída:
```
📦 Available backups:
--------------------------------------------------------------------------------
Timestamp: 20251120_143000
Date: 2025-11-20T14:30:00
Size: 575.75 MB
Manifest: ./backups/backup_manifest_20251120_143000.json
--------------------------------------------------------------------------------
Timestamp: 20251119_143000
Date: 2025-11-19T14:30:00
Size: 550.25 MB
Manifest: ./backups/backup_manifest_20251119_143000.json
--------------------------------------------------------------------------------
```

### Restore Completo

```bash
# Restore database + storage
python scripts/dr/restore.py --timestamp 20251120_143000

# Apenas database (mais rápido)
python scripts/dr/restore.py --timestamp 20251120_143000 --skip-storage
```

### Restore Destrutivo (Drop e Recria Database)

⚠️ **ATENÇÃO**: Esta operação **apaga completamente** o banco de dados existente!

```bash
# Requer flag --confirm para segurança
python scripts/dr/restore.py --timestamp 20251120_143000 --drop-existing --confirm
```

### Restore para Ambiente Diferente

```bash
# Configurar variáveis para o ambiente de destino
export POSTGRES_HOST=staging-db.example.com
export POSTGRES_PORT=5432
export POSTGRES_DB=3dpot_staging
export POSTGRES_USER=staging_user
export POSTGRES_PASSWORD=staging_pass

# Executar restore
python scripts/dr/restore.py --timestamp 20251120_143000 --confirm --drop-existing
```

## 📊 Recomendações de Frequência

### Ambiente de Produção

| Tipo | Frequência | Retenção | Comando |
|------|-----------|----------|---------|
| **Backup Incremental** | Diário | 7 dias | `backup.py --skip-storage --keep 7` |
| **Backup Completo** | Semanal | 4 semanas | `backup.py --keep 4` |
| **Backup Mensal** | Mensal | 6 meses | `backup.py` (armazenar separadamente) |

### Ambiente de Staging/Dev

| Tipo | Frequência | Retenção |
|------|-----------|----------|
| **Backup Completo** | Semanal | 2 semanas |

## 🔒 Segurança

### Armazenamento Seguro de Backups

1. **Criptografia em repouso**
   ```bash
   # Criptografar backup com GPG
   gpg --symmetric --cipher-algo AES256 db_backup_20251120_143000.sql
   ```

2. **Upload para armazenamento remoto**
   ```bash
   # AWS S3
   aws s3 cp backups/ s3://my-3dpot-backups/$(date +%Y%m%d)/ --recursive
   
   # Google Cloud Storage
   gsutil -m cp -r backups/* gs://my-3dpot-backups/$(date +%Y%m%d)/
   ```

3. **Permissões restritas**
   ```bash
   # Apenas owner pode ler/escrever
   chmod 600 backups/*.sql
   chmod 700 backups/
   ```

## ✅ Checklist de Validação

### Após Backup
- [ ] Verificar que todos os arquivos foram criados (db, storage, manifest)
- [ ] Conferir tamanho dos arquivos (não devem ser 0 bytes)
- [ ] Validar JSON do manifesto
- [ ] Testar restore em ambiente de teste (recomendado mensalmente)

### Após Restore
- [ ] Verificar logs para erros críticos
- [ ] Testar conectividade com o banco
- [ ] Verificar integridade de dados críticos
- [ ] Executar health checks da aplicação
- [ ] Validar permissões de usuários

## 🆘 Troubleshooting

### Erro: "pg_dump: command not found"
```bash
# Instalar PostgreSQL client tools
sudo apt-get install postgresql-client  # Ubuntu/Debian
brew install postgresql                  # macOS
```

### Erro: "Insufficient disk space"
```bash
# Verificar espaço disponível
df -h

# Limpar backups antigos manualmente
rm backups/db_backup_20251101_*.sql
rm backups/storage_backup_20251101_*.tar.gz
```

### Erro: "Permission denied" no restore
```bash
# Verificar permissões do usuário no PostgreSQL
psql -U postgres -c "\du"

# Conceder permissões necessárias
psql -U postgres -c "ALTER USER 3dpot WITH SUPERUSER;"
```

### Backup/Restore muito lento
```bash
# Usar backup paralelo (PostgreSQL 9.3+)
pg_dump -j 4 ...  # 4 jobs paralelos

# Ou usar snapshot do storage
# (implementação futura)
```

## 📝 Logs

Os scripts registram logs em:
- **stdout**: Informações gerais e progresso
- **stderr**: Erros e avisos

Redirecionar para arquivo:
```bash
python scripts/dr/backup.py 2>&1 | tee logs/backup_$(date +%Y%m%d).log
```

## 🔄 Próximos Passos (Sprint 10+)

- [ ] Backup incremental (WAL archiving)
- [ ] Backup contínuo (Point-in-Time Recovery)
- [ ] Integração com cloud storage (S3, GCS, Azure Blob)
- [ ] Criptografia automática de backups
- [ ] Dashboard de status de backups
- [ ] Alertas de falha de backup (PagerDuty, Slack)
- [ ] Testes automatizados de restore
- [ ] Backup de configurações (environment, secrets via vault)

## 📞 Suporte

Em caso de problemas com DR:
1. Verificar logs em `logs/`
2. Consultar documentação do PostgreSQL
3. Abrir issue no GitHub com logs completos
