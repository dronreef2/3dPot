# Sprint 9 - Operations Runbook
# 3dPot Platform - Guia de Operações e Resposta a Incidentes

**Versão:** 1.0  
**Data:** Novembro 2025  
**Autor:** Equipe 3dPot  
**Objetivo:** Fornecer procedimentos padronizados para detecção, triagem e resolução de incidentes em produção.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Detecção de Incidentes](#detecção-de-incidentes)
3. [Triagem Inicial](#triagem-inicial)
4. [Procedimentos de Rollback](#procedimentos-de-rollback)
5. [Investigação com Audit Logs](#investigação-com-audit-logs)
6. [Checklist Pós-Incidente](#checklist-pós-incidente)
7. [Troubleshooting Comum](#troubleshooting-comum)

---

## Visão Geral

Este runbook documenta procedimentos operacionais para o ambiente de produção do 3dPot, incluindo:

- **Observabilidade**: Logs estruturados, métricas Prometheus, request/trace IDs
- **Disaster Recovery**: Scripts de backup/restore (PostgreSQL + Storage)
- **Segurança**: MFA, rate limiting, audit logging
- **Performance**: Monitoramento de latência, taxa de erro, uso de recursos

**Stack de Observabilidade:**
- **Logs**: structlog (JSON) + request_id/trace_id
- **Métricas**: Prometheus (expostas em `/metrics`)
- **Auditoria**: Tabela `audit_log` no PostgreSQL
- **Tracing**: X-Request-ID e X-Trace-Id headers

---

## Detecção de Incidentes

### 1. Métricas Críticas para Monitorar

#### 1.1 HTTP Errors (5xx)

**Métrica:**
```prometheus
# Taxa de erros 5xx
rate(http_requests_total{status=~"5.."}[5m])

# Alerta: > 5% de erros 5xx
(
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) > 0.05
```

**Ação Imediata:**
1. Verificar logs estruturados para exceptions:
   ```bash
   # Filtrar por status_code >= 500
   jq 'select(.status_code >= 500)' /var/log/3dpot/app.log | tail -n 50
   ```
2. Identificar endpoints afetados (campo `path` nos logs)
3. Verificar trace_id para rastrear requisições completas

#### 1.2 Latência

**Métrica:**
```prometheus
# P95 de latência por endpoint
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# Alerta: P95 > 2s
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
) > 2
```

**Ação Imediata:**
1. Verificar campo `duration_ms` nos logs
2. Identificar endpoints lentos: `grep "duration_ms" /var/log/3dpot/app.log | sort -k duration_ms -n`
3. Verificar carga de DB/Redis

#### 1.3 Rate Limiting

**Métrica:**
```prometheus
# Taxa de rate limit hits
rate(rate_limit_hits_total[5m])

# Por IP/usuário
rate_limit_hits_total{reason="login_attempts_exceeded"}
```

**Ação Imediata:**
1. Verificar audit logs para `RATE_LIMIT_EXCEEDED`
2. Identificar IPs/usuários suspeitos
3. Considerar blocklist temporária se for ataque

#### 1.4 Falhas de Autenticação

**Métrica:**
```prometheus
# Taxa de falhas de login
rate(auth_failures_total[5m])

# MFA failures
rate(auth_failures_total{reason="mfa_failed"}[5m])
```

**Ação Imediata:**
1. Verificar audit logs: `action="LOGIN"`, `success=false`
2. Identificar padrões (força bruta, credential stuffing)
3. Verificar se é incidente de segurança

#### 1.5 Permissões Negadas

**Métrica:**
```prometheus
# Rate de permission denied
rate(permission_denied_total[5m])
```

**Ação Imediata:**
1. Audit logs: `action="PERMISSION_DENIED"`
2. Verificar se mudanças recentes em roles/permissions
3. Verificar se usuários afetados são legítimos

---

## Triagem Inicial

### Checklist de Diagnóstico Rápido

Quando um incidente é detectado, seguir esta ordem:

#### ✅ 1. Verificar Saúde dos Serviços

```bash
# Health check da API
curl https://api.3dpot.com/health

# Status do PostgreSQL
docker exec -it 3dpot-db psql -U postgres -c "SELECT version();"

# Status do Redis
docker exec -it 3dpot-redis redis-cli ping

# Status do Storage (MinIO/S3)
mc admin info myminio/
```

**Expectativa:**
- API: `{"status": "healthy", "service": "3dpot-backend"}`
- PostgreSQL: retorno de versão
- Redis: `PONG`
- Storage: status operacional

#### ✅ 2. Verificar Logs Estruturados

```bash
# Últimas 100 linhas (JSON)
tail -n 100 /var/log/3dpot/app.log | jq

# Filtrar por erro
tail -n 1000 /var/log/3dpot/app.log | jq 'select(.level == "error")'

# Por trace_id específico
grep "trace_id_aqui" /var/log/3dpot/app.log | jq

# Por request_id específico
grep "request_id_aqui" /var/log/3dpot/app.log | jq
```

#### ✅ 3. Verificar Carga do Sistema

```bash
# CPU, memória, disco
top
htop
df -h

# Conexões de rede
netstat -an | grep ESTABLISHED | wc -l

# Processos Python/FastAPI
ps aux | grep python
```

#### ✅ 4. Verificar Banco de Dados

```sql
-- Conexões ativas
SELECT count(*) FROM pg_stat_activity;

-- Queries lentas (> 1s)
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '1 second'
ORDER BY duration DESC;

-- Locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Tamanho do DB
SELECT pg_size_pretty(pg_database_size('3dpot_v2'));
```

#### ✅ 5. Verificar Audit Events Recentes

```sql
-- Últimos 50 eventos de auditoria
SELECT * FROM audit_log 
ORDER BY timestamp DESC 
LIMIT 50;

-- Eventos de segurança (últimas 24h)
SELECT action, user_id, ip_address, timestamp, details
FROM audit_log
WHERE action IN ('LOGIN', 'MFA_CHALLENGE_FAILED', 'RATE_LIMIT_EXCEEDED', 'PERMISSION_DENIED')
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

---

## Procedimentos de Rollback

### Quando Fazer Rollback

- **Deploy recente** causou errors 5xx ou degradação severa
- **Mudanças de schema** incompatíveis
- **Incidente de segurança** relacionado a código novo

### 1. Rollback de Código (Git/Docker)

#### Opção A: Rollback via Git Tag

```bash
# Listar releases
git tag -l

# Checkout para versão anterior
git checkout v2.0.5

# Rebuild e redeploy
docker-compose build backend
docker-compose up -d backend
```

#### Opção B: Rollback via Docker Image Tag

```bash
# Verificar imagens disponíveis
docker images 3dpot-backend

# Usar versão anterior
docker-compose down backend
docker-compose up -d -f docker-compose.yml \
  --scale backend=1 \
  -e BACKEND_IMAGE_TAG=v2.0.5
```

### 2. Rollback de Banco de Dados (com DR)

**⚠️ CUIDADO: Rollback de DB é destrutivo!**

Usar apenas em casos críticos (corrupção, falha catastrófica).

#### Pré-requisitos
1. Ter backup recente (`scripts/dr/backup.py`)
2. Janela de manutenção (downtime)
3. Aprovação de stakeholders

#### Procedimento

```bash
# 1. Listar backups disponíveis
python scripts/dr/restore.py --list

# Output exemplo:
# 2025-11-20_02-00-00 | database+storage | 1.2GB | manifest OK

# 2. Fazer backup do estado ATUAL (safety)
python scripts/dr/backup.py \
  --type full \
  --output /backups/emergency_$(date +%Y%m%d_%H%M%S)

# 3. Parar aplicação (evitar writes)
docker-compose stop backend

# 4. Restore do backup escolhido
python scripts/dr/restore.py \
  --backup-dir /backups/2025-11-20_02-00-00 \
  --confirm

# Será solicitado confirmação:
# "This will OVERWRITE database. Type 'RESTORE' to confirm: RESTORE"

# 5. Verificar integridade
python scripts/dr/restore.py \
  --backup-dir /backups/2025-11-20_02-00-00 \
  --verify

# 6. Restart aplicação
docker-compose up -d backend

# 7. Verificar saúde
curl https://api.3dpot.com/health
```

### 3. Rollback Parcial (Feature Flags)

Se disponível, desabilitar features via env vars:

```bash
# Desabilitar MFA globalmente
export MFA_ENABLED=false
docker-compose restart backend

# Desabilitar rate limiting
export RATE_LIMIT_ENABLED=false
docker-compose restart backend
```

---

## Investigação com Audit Logs

### Queries Úteis

#### 1. Investigar Usuário Suspeito

```sql
-- Todas ações de um usuário (últimas 24h)
SELECT action, ip_address, timestamp, details
FROM audit_log
WHERE user_id = 'user-uuid-aqui'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

#### 2. Investigar IP Suspeito

```sql
-- Atividade de um IP
SELECT action, user_id, username, timestamp, details
FROM audit_log
WHERE ip_address = '192.168.1.100'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

#### 3. Rastrear Request Específica

```sql
-- Via request_id (se armazenado em details)
SELECT *
FROM audit_log
WHERE details::text LIKE '%request_id_aqui%'
ORDER BY timestamp;
```

#### 4. Padrões de Falha de Login

```sql
-- Tentativas falhadas por usuário (últimas 24h)
SELECT username, COUNT(*) as failed_attempts, 
       array_agg(DISTINCT ip_address) as ips
FROM audit_log
WHERE action = 'LOGIN'
  AND details->>'success' = 'false'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY username
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;
```

#### 5. Eventos de MFA

```sql
-- Falhas de MFA (possível ataque)
SELECT user_id, username, ip_address, timestamp, 
       details->>'reason' as failure_reason
FROM audit_log
WHERE action = 'MFA_CHALLENGE_FAILED'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

### Exportar Audit Logs para Análise

```bash
# CSV para análise offline
psql -U postgres -d 3dpot_v2 -c \
  "COPY (SELECT * FROM audit_log WHERE timestamp > NOW() - INTERVAL '7 days') 
   TO STDOUT WITH CSV HEADER" > audit_export_$(date +%Y%m%d).csv

# JSON para ferramentas de análise
psql -U postgres -d 3dpot_v2 -t -c \
  "SELECT json_agg(row_to_json(t)) FROM (
     SELECT * FROM audit_log 
     WHERE timestamp > NOW() - INTERVAL '7 days'
   ) t" > audit_export_$(date +%Y%m%d).json
```

---

## Checklist Pós-Incidente

Após resolver um incidente:

### ✅ 1. Documentar RCA (Root Cause Analysis)

Criar issue no GitHub com template:

```markdown
## Incidente: [Título]

**Data/Hora:** 2025-11-20 14:30 UTC  
**Duração:** 45 minutos  
**Impacto:** 5% de usuários afetados (500 RPM)  
**Severidade:** P1 (Critical)

### Timeline
- 14:30 - Alerta: taxa de erro 5xx > 10%
- 14:35 - Investigação: logs apontam erro em /api/v1/projects
- 14:40 - Root cause: migration incompletoe no deploy v2.0.6
- 14:50 - Rollback para v2.0.5
- 15:00 - Verificação: sistema normal
- 15:15 - Incidente resolvido

### Root Cause
Migration `20251120_add_mfa_fields` não rodou em produção.

### Ações Corretivas
1. Adicionar smoke tests pós-deploy
2. Verificar migrations em CI/CD
3. Documentar checklist de deploy
```

### ✅ 2. Atualizar Runbook

Se o incidente revelou gaps neste runbook:

1. Adicionar novo cenário em [Troubleshooting Comum](#troubleshooting-comum)
2. Atualizar queries de auditoria
3. Documentar comandos úteis

### ✅ 3. Melhorar Alertas

Se o incidente não foi detectado rapidamente:

1. Criar/ajustar alerta Prometheus
2. Adicionar health check
3. Configurar notificações (Slack, PagerDuty, etc.)

### ✅ 4. Revisar Backups

```bash
# Garantir backup recente
python scripts/dr/backup.py --type full

# Testar restore em ambiente de staging
python scripts/dr/restore.py --backup-dir /backups/latest --verify
```

### ✅ 5. Comunicação

- [ ] Informar stakeholders sobre resolução
- [ ] Atualizar status page (se houver)
- [ ] Post-mortem em reunião de equipe

---

## Troubleshooting Comum

### Problema: "Database connection failed"

**Sintomas:**
- Erro 5xx em todas as requisições
- Logs: `psycopg2.OperationalError: could not connect`

**Diagnóstico:**
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Verificar logs do container
docker logs 3dpot-db

# Testar conexão
psql -h localhost -U postgres -d 3dpot_v2 -c "SELECT 1"
```

**Soluções:**
1. Restart do container: `docker-compose restart db`
2. Verificar variáveis de conexão (`.env`)
3. Verificar limites de conexões: `max_connections` no PostgreSQL
4. Verificar pool de conexões da aplicação

---

### Problema: "Redis connection timeout"

**Sintomas:**
- Rate limiting não funciona
- Sessions não persistem
- Logs: `redis.exceptions.TimeoutError`

**Diagnóstico:**
```bash
# Ping Redis
docker exec -it 3dpot-redis redis-cli ping

# Verificar memória
docker exec -it 3dpot-redis redis-cli INFO memory

# Verificar conexões
docker exec -it 3dpot-redis redis-cli CLIENT LIST
```

**Soluções:**
1. Restart: `docker-compose restart redis`
2. Flush cache (se seguro): `redis-cli FLUSHALL`
3. Aumentar `maxmemory` se necessário

---

### Problema: "MFA codes not working"

**Sintomas:**
- Usuários reportam códigos TOTP inválidos
- Audit logs: `MFA_CHALLENGE_FAILED` em massa

**Diagnóstico:**
```bash
# Verificar relógio do servidor
date
timedatectl status

# Verificar skew de tempo
ntpq -p
```

**Soluções:**
1. Sincronizar relógio do servidor: `ntpdate pool.ntp.org`
2. Verificar timezone: `timedatectl set-timezone UTC`
3. Aumentar `valid_window` em `mfa_service.py` (temporário)

---

### Problema: "Storage full"

**Sintomas:**
- Falha ao criar projetos/uploads
- Logs: `OSError: [Errno 28] No space left on device`

**Diagnóstico:**
```bash
# Verificar uso de disco
df -h

# Top diretórios
du -sh /var/lib/docker/* | sort -h
du -sh /backups/* | sort -h
```

**Soluções:**
1. Limpar backups antigos:
   ```bash
   # Remove backups > 30 dias
   find /backups -type f -mtime +30 -delete
   ```
2. Limpar Docker volumes não usados:
   ```bash
   docker system prune -a --volumes
   ```
3. Aumentar volume (cloud provider)

---

### Problema: "High CPU usage"

**Sintomas:**
- Latência alta (P95 > 5s)
- `top` mostra Python usando 100% CPU

**Diagnóstico:**
```bash
# Profiling do processo
py-spy top --pid $(pgrep -f "uvicorn")

# Verificar queries lentas no DB
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;
```

**Soluções:**
1. Identificar endpoint/query problemático via profiling
2. Otimizar query (índices, EXPLAIN ANALYZE)
3. Adicionar cache (Redis)
4. Escalar horizontalmente (mais workers)

---

## Integração com OpenTelemetry/Jaeger (Futuro)

Este runbook documenta o estado atual (request_id/trace_id básicos). Para tracing distribuído completo:

### Roadmap
1. **Instrumentação OpenTelemetry:**
   - Adicionar `opentelemetry-instrumentation-fastapi`
   - Configurar exporters (Jaeger, Zipkin)
   - Propagar trace context via headers

2. **Correlação com Logs:**
   - Trace ID já presente nos logs (Sprint 9)
   - Integrar Jaeger UI com logs (via trace_id)

3. **Métricas por Trace:**
   - Latência por span
   - Erros por serviço
   - Dependency mapping

---

## Contatos de Emergência

| Responsável | Área | Contato |
|------------|------|---------|
| DevOps Lead | Infraestrutura | devops@3dpot.com |
| Backend Lead | API/DB | backend@3dpot.com |
| Security Lead | Incidentes de segurança | security@3dpot.com |
| On-call (24/7) | Produção | oncall@3dpot.com |

---

## Referências

- [DR Scripts README](../../scripts/dr/README.md)
- [Sprint 6 - Observabilidade](./SPRINT6-OBSERVABILIDADE-RELATORIO.md)
- [Sprint 7 - Segurança](./SPRINT7-SEGURANCA-RELATORIO.md)
- [Sprint 8 - Production Hardening](./SPRINT8-PRODUCTION-HARDENING-RELATORIO.md)
- [Métricas Prometheus](../../monitoring/prometheus/)

---

**Última Atualização:** 2025-11-20  
**Versão:** 1.0 (Sprint 9)
