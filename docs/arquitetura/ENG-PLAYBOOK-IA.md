# Playbook de Engenharia com IA

**Versão:** 1.0  
**Data:** Novembro 2025  
**Propósito:** Guia prático para usar IA em sprints de evolução de software

---

## 📖 Índice

1. [Visão Geral](#visão-geral)
2. [Fases/Sprints Recomendadas](#fases-sprints-recomendadas)
3. [Boas Práticas de Uso de IA](#boas-práticas-de-uso-de-ia)
4. [Exemplos de Prompts](#exemplos-de-prompts)
5. [Checklists de Production-Readiness](#checklists-de-production-readiness)
6. [Ferramentas e Recursos](#ferramentas-e-recursos)
7. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 Visão Geral

### O Método: Sprints com IA

Este playbook documenta um método comprovado para evoluir projetos de software usando IA como acelerador. A abordagem consiste em:

1. **Dividir evolução em sprints temáticas** (estrutura, testes, observabilidade, segurança, etc.)
2. **Usar IA para diagnosticar, planejar e implementar** cada sprint
3. **Validar continuamente** com testes automatizados e scans de segurança
4. **Documentar aprendizados** em relatórios de sprint reutilizáveis

### Quando Usar Este Método

✅ **Cenários Ideais:**
- Repositórios com código funcional mas desorganizado
- Projetos com baixa cobertura de testes (< 60%)
- Sistemas sem observabilidade adequada
- Aplicações que precisam de hardening de segurança
- Preparação para ambientes de produção

❌ **Não Recomendado Para:**
- Projetos greenfield (começando do zero)
- Código legado sem testes e sem entendimento
- Sistemas críticos em produção sem ambiente de staging
- Prazos muito apertados (< 1 semana por sprint)

### Benefícios Esperados

Baseado na experiência do projeto 3dPot:

| Métrica | Antes | Depois (9 Sprints) | Ganho |
|---------|-------|-------------------|-------|
| **Cobertura de Testes** | 40% | 85% | +45% |
| **Testes Totais** | 93 | 748 | +655 |
| **Observabilidade** | Básica | Avançada | Logs + Metrics + Trace |
| **Segurança** | JWT | JWT + Rate + Audit + RBAC + MFA | 5+ camadas |
| **Production-Ready** | 40% | 98% | +58% |
| **Tempo Investido** | - | ~9 sprints | 2-4 semanas |

### Princípios Fundamentais

1. **Incrementalismo Controlado**: Cada sprint adiciona uma camada específica
2. **Validação Contínua**: Testes e scans em cada mudança
3. **Zero Regressões**: Mudanças sempre aditivas e retrocompatíveis
4. **IA como Colaboradora**: IA sugere, humano valida
5. **Documentação Viva**: Cada sprint documenta seu impacto

---

## 🏗️ Fases/Sprints Recomendadas

### Fase 1: Fundação (Sprints 1-2)

**Objetivo:** Estabelecer base sólida de estrutura e testes

#### Sprint 1: Reorganização e Estrutura
- **Foco:** Organizar repositório em estrutura navegável
- **Duração:** 1-2 dias
- **Entregas:** Diretórios organizados, README atualizado, STRUCTURE.md
- **Impacto:** +80% navegabilidade, onboarding mais fácil

#### Sprint 2: Testes Básicos
- **Foco:** Cobrir módulos críticos com testes unitários
- **Duração:** 3-5 dias
- **Entregas:** 150-200 testes, cobertura 70%+
- **Impacto:** +30-40% cobertura, confiança em refatorações

**Checkpoint:** Você tem código organizado e testável? ✅ Prossiga para Fase 2

---

### Fase 2: Consolidação (Sprints 3-5)

**Objetivo:** Expandir cobertura e estabelecer ferramentas

#### Sprint 3: Integração + CLI
- **Foco:** Consolidar testes de integração, criar CLI
- **Duração:** 2-3 dias
- **Entregas:** CLI com 8-10 comandos, 5-10 testes E2E
- **Impacto:** Ferramentas de dev, testes de fluxo completo

#### Sprint 4: Cobertura + CI
- **Foco:** Módulos secundários, fortalecer CI/CD
- **Duração:** 3-4 dias
- **Entregas:** 80-120 testes, CI com coverage
- **Impacto:** +10% cobertura, CI automatizado

#### Sprint 5: Qualidade Final
- **Foco:** 100% serviços com testes, performance baseline
- **Duração:** 2-3 dias
- **Entregas:** Todos serviços testados, benchmarks
- **Impacto:** 85%+ cobertura, baseline de performance

**Checkpoint:** Você tem 85%+ cobertura e CI funcional? ✅ Prossiga para Fase 3

---

### Fase 3: Production-Ready (Sprints 6-9)

**Objetivo:** Preparar para produção com observabilidade e segurança

#### Sprint 6: Observabilidade
- **Foco:** Logging estruturado, métricas, tracing
- **Duração:** 2-3 dias
- **Entregas:** Logs JSON, /metrics, request_id
- **Impacto:** Debugging eficiente, monitoramento

#### Sprint 7: Segurança Base
- **Foco:** Rate limiting, audit logging, RBAC
- **Duração:** 2-3 dias
- **Entregas:** Rate limiter, audit logs, RBAC
- **Impacto:** Proteção contra abuso, rastreabilidade

#### Sprint 8: Hardening
- **Foco:** Escala horizontal, security gates
- **Duração:** 2-3 dias
- **Entregas:** Rate limiting distribuído, CI security
- **Impacto:** Escalabilidade, pipeline seguro

#### Sprint 9: Operações + DR
- **Foco:** MFA, disaster recovery, runbook
- **Duração:** 3-4 dias
- **Entregas:** MFA/2FA, scripts DR, runbook 500+ linhas
- **Impacto:** 98% production-ready

**Checkpoint:** Você tem 98%+ production-ready? ✅ Deploy para produção!

---

### Sequência Visual

```
┌─────────────────────────────────────────────────────────┐
│                    FASE 1: FUNDAÇÃO                     │
│  Sprint 1 (Estrutura) → Sprint 2 (Testes Básicos)      │
│  Ganho: +30-40% cobertura, código organizado           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 FASE 2: CONSOLIDAÇÃO                    │
│  Sprint 3 (CLI) → Sprint 4 (CI) → Sprint 5 (Qualidade) │
│  Ganho: +15% cobertura, CI automatizado, CLI           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               FASE 3: PRODUCTION-READY                  │
│  Sprint 6 (Obs) → Sprint 7 (Sec) → Sprint 8 (Hard)     │
│  → Sprint 9 (Ops+DR)                                    │
│  Ganho: Observabilidade + Segurança + Ops              │
└─────────────────────────────────────────────────────────┘
                            ↓
                  🚀 PRODUCTION READY (98%)
```

---

## 🤖 Boas Práticas de Uso de IA

### 1. Como Escrever Prompts Eficazes

#### Estrutura de Prompt Recomendada

```
[PAPEL DA IA]
Você é um [especialista em X].

[CONTEXTO]
- Repositório: [URL]
- Stack: [tecnologias]
- Estado atual: [métricas]

[PROBLEMA]
[Descrição clara do problema]

[OBJETIVO]
[O que você quer alcançar]

[TAREFAS QUE VOCÊ DEVE EXECUTAR]
1. [Tarefa específica 1]
2. [Tarefa específica 2]
...

[FORMATO DE SAÍDA]
1. [O que você espera receber]
2. [Formato preferido]

[RESTRIÇÕES]
- NÃO [ação indesejada]
- SEMPRE [ação obrigatória]

[MÉTRICAS DE SUCESSO]
- [Critério 1]
- [Critério 2]
```

#### Exemplo de Prompt Eficaz

```
Você é um especialista em testes de software.

[CONTEXTO]
- Repositório: https://github.com/user/project
- Stack: Python/FastAPI
- Cobertura atual: 40%

[PROBLEMA]
O serviço budgeting_service.py (~500 linhas) não tem testes unitários.

[OBJETIVO]
Criar 40-50 testes unitários cobrindo happy paths, edge cases e error handling.

[TAREFAS]
1. Analisar budgeting_service.py e identificar métodos públicos
2. Criar test_budgeting_service.py seguindo convenção pytest
3. Implementar testes para cada método público
4. Usar mocks para dependências externas (API Octopart)
5. Validar que todos os testes passam

[FORMATO DE SAÍDA]
1. Arquivo test_budgeting_service.py completo
2. Resumo de testes criados (nome, propósito)
3. Comandos para executar testes

[RESTRIÇÕES]
- NÃO modificar budgeting_service.py
- NÃO criar testes que dependam de APIs externas reais
- USAR mocks/stubs apropriados

[MÉTRICAS]
- 40+ testes criados
- Todos os métodos públicos cobertos
- Tempo de execução < 5 segundos
```

### 2. Como Interpretar Respostas da IA

#### Sinais de Boa Resposta ✅

- **Específica:** Código concreto, não pseudocódigo genérico
- **Completa:** Cobre todos os pontos solicitados
- **Testável:** Inclui exemplos de uso ou testes
- **Documentada:** Explica decisões e trade-offs
- **Contextual:** Considera stack e convenções do projeto

#### Sinais de Resposta Problemática ⚠️

- **Genérica:** "Você poderia fazer X ou Y..."
- **Incompleta:** Falta partes importantes do código
- **Não testável:** Sem exemplos ou validação
- **Sem contexto:** Ignora stack ou estrutura existente
- **Insegura:** Sugere práticas inseguras (secrets hardcoded, etc.)

#### O Que Fazer Com Respostas Problemáticas

1. **Refinar o Prompt:** Adicione mais contexto ou seja mais específico
2. **Dividir em Partes:** Se muito complexo, divida em tarefas menores
3. **Dar Exemplos:** Mostre código existente como referência
4. **Iterar:** Use a resposta como ponto de partida e refine

### 3. Como Validar com Testes e Scans

#### Validação Obrigatória Após Cada Sprint

```bash
# 1. Testes Unitários
pytest tests/unit/ -v
# ✅ Todos devem passar

# 2. Testes de Integração
pytest tests/integration/ -v
# ✅ Todos devem passar

# 3. Testes E2E (se aplicável)
pytest tests/e2e/ -v
# ✅ Todos devem passar

# 4. Coverage
pytest --cov=src --cov-report=html --cov-fail-under=70
# ✅ >= threshold configurado

# 5. Linting
pylint src/
# ✅ Score >= 8.0

# 6. Type Checking (se aplicável)
mypy src/
# ✅ 0 erros

# 7. Security Scan
bandit -r src/ -ll
# ✅ 0 issues críticos

# 8. Dependency Scan
pip-audit --desc
# ✅ 0 vulnerabilidades críticas não mitigadas
```

#### Checklist de Validação

```markdown
## Validação Pós-Sprint

### Funcional
- [ ] Todos os testes passam (unit + integration + e2e)
- [ ] Build/run funciona sem erros
- [ ] Funcionalidades existentes não quebradas

### Qualidade
- [ ] Coverage >= threshold
- [ ] Linting sem erros críticos
- [ ] Type checking sem erros (se aplicável)
- [ ] Código segue convenções do projeto

### Segurança
- [ ] 0 secrets hardcoded
- [ ] 0 vulnerabilidades críticas (Bandit/SAST)
- [ ] 0 vulnerabilidades críticas (pip-audit/Safety)
- [ ] Dependências atualizadas

### Documentação
- [ ] README atualizado (se aplicável)
- [ ] Docstrings para novos métodos públicos
- [ ] Relatório de sprint criado
- [ ] Changelog atualizado (se aplicável)
```

### 4. Iteração e Refinamento

#### Ciclo de Feedback

```
1. Escrever Prompt → 2. IA Gera Código → 3. Revisar Código
                          ↑                        ↓
                    6. Validar ← 5. Aplicar ← 4. Refinar
                          ↓
                    7. Documentar
```

#### Quando Iterar

- **Primeira tentativa:** Sempre revise e valide
- **Se testes falham:** Refine o prompt ou corrija manualmente
- **Se código não segue padrões:** Adicione exemplos ao prompt
- **Se resposta genérica:** Seja mais específico no prompt

#### Como Iterar Eficientemente

1. **Mantenha histórico:** Salve prompts que funcionaram
2. **Documente problemas:** Anote o que não funcionou e por quê
3. **Construa biblioteca:** Crie biblioteca de prompts reutilizáveis
4. **Compartilhe:** Compartilhe prompts eficazes com a equipe

---

## 📝 Exemplos de Prompts

### Exemplo 1: Prompt Ruim → Bom

#### ❌ Prompt Ruim

```
Crie testes para o meu serviço de autenticação.
```

**Problemas:**
- Muito genérico
- Sem contexto (stack, framework)
- Sem especificar o que testar
- Sem restrições
- Sem critérios de sucesso

#### ✅ Prompt Bom

```
Você é um especialista em testes de segurança.

[CONTEXTO]
- Repositório: https://github.com/user/api
- Stack: Python/FastAPI
- Autenticação: JWT com refresh tokens
- Arquivo: backend/services/auth_service.py (300 linhas)

[OBJETIVO]
Criar 30-40 testes unitários para auth_service.py cobrindo:
- Login (sucesso, falha, credenciais inválidas)
- Registro (sucesso, usuário duplicado, validações)
- Geração de tokens (access + refresh)
- Validação de tokens (válido, expirado, inválido)
- Refresh de tokens
- Logout

[TAREFAS]
1. Analisar auth_service.py
2. Criar test_auth_service.py usando pytest
3. Implementar testes com fixtures para usuários de teste
4. Usar freezegun para controlar tempo (testar expiração)
5. Mockar hash de senhas e JWT encoding/decoding

[FORMATO DE SAÍDA]
1. Arquivo test_auth_service.py completo
2. Fixtures necessárias
3. Comando para executar: pytest tests/unit/services/test_auth_service.py -v

[RESTRIÇÕES]
- NÃO usar banco de dados real (usar mocks/fixtures)
- NÃO expor senhas em logs de teste
- SEMPRE testar tanto sucesso quanto falha
- Testes devem ser determinísticos (sem randomness)

[MÉTRICAS]
- 30-40 testes criados
- Cobertura do auth_service >= 85%
- Tempo de execução < 3 segundos
```

**Por que é melhor:**
- Contexto completo (stack, framework, arquivo)
- Objetivo específico (30-40 testes, cenários claros)
- Tarefas detalhadas (análise, fixtures, mocks)
- Formato de saída claro
- Restrições de segurança
- Métricas mensuráveis

---

### Exemplo 2: Prompt para Observabilidade

#### ✅ Prompt Eficaz

```
Você é um especialista em observabilidade de sistemas distribuídos.

[CONTEXTO]
- Repositório: https://github.com/user/backend
- Stack: Python 3.11 + FastAPI 0.104
- Logging atual: print() statements
- Objetivo: Production-ready observability

[PROBLEMA]
Sistema não tem observabilidade adequada para produção. Logs não estruturados, sem métricas, sem correlação de requisições.

[OBJETIVO]
Implementar observabilidade production-ready com:
1. Logging estruturado (JSON para prod, console para dev)
2. Métricas Prometheus (/metrics endpoint)
3. Request ID para correlação

[TAREFAS]
1. Implementar logging estruturado:
   - Usar structlog
   - Formato JSON para produção
   - Formato console colorido para dev
   - Configurar via LOG_LEVEL e LOG_FORMAT env vars
   - Criar backend/observability/logging_config.py

2. Implementar request ID middleware:
   - Gerar UUID único por requisição
   - Adicionar header X-Request-ID
   - Propagar em todos os logs
   - Criar backend/observability/request_id.py

3. Implementar métricas Prometheus:
   - Endpoint /metrics
   - Métricas HTTP: requests_total, duration_seconds, in_progress
   - Labels: method, endpoint, status
   - Criar backend/observability/metrics.py

4. Criar middleware de logging automático:
   - Logar todas as requisições
   - Incluir: method, path, status, duration, request_id
   - Logs especiais para 4xx/5xx
   - Excluir /health por padrão

5. Documentar:
   - Como configurar (env vars)
   - Exemplos de logs JSON
   - Exemplos de queries Prometheus
   - Criar docs/OBSERVABILITY.md

[FORMATO DE SAÍDA]
1. Arquivos criados:
   - backend/observability/__init__.py
   - backend/observability/logging_config.py
   - backend/observability/request_id.py
   - backend/observability/metrics.py
2. Exemplo de log JSON
3. Lista de métricas expostas
4. Documentação OBSERVABILITY.md
5. Instruções de integração no main.py

[RESTRIÇÕES]
- NÃO logar dados sensíveis (passwords, tokens)
- NÃO logar health checks (muito ruído)
- Configuração via environment variables (.env)
- Suporte a desenvolvimento (logs legíveis)
- Performance overhead < 5ms por requisição

[MÉTRICAS]
- Logs estruturados em JSON para prod
- Request ID em 100% dos logs
- /metrics retornando métricas válidas Prometheus
- Documentação completa
- 0 dados sensíveis em logs
```

---

### Exemplo 3: Prompt para Segurança

#### ✅ Prompt Eficaz

```
Você é um especialista em segurança de aplicações web.

[CONTEXTO]
- Repositório: https://github.com/user/api
- Stack: Python/FastAPI
- Autenticação: JWT
- Observabilidade: Logs estruturados (Sprint 6)

[PROBLEMA]
API vulnerável a abuso (sem rate limiting), sem auditoria de ações críticas, controle de acesso básico.

[OBJETIVO]
Implementar camada de segurança com:
1. Rate limiting (proteção contra abuso)
2. Audit logging (rastreamento de ações)
3. RBAC melhorado (controle de acesso granular)

[TAREFAS]
1. Rate Limiting (Token Bucket):
   - Algoritmo Token Bucket (permite bursts)
   - Limites por endpoint:
     - /auth/login: 10 req/min
     - /auth/register: 10 req/min
     - APIs caras: 30 req/min
     - Default: 60 req/min
   - Diferenciar IP e usuário autenticado
   - Retornar 429 com headers: X-RateLimit-Limit, Remaining, Retry-After
   - Configurável via env vars
   - Criar backend/observability/rate_limiting.py

2. Audit Logging:
   - Tabela audit_logs (não deletar jamais)
   - Registrar:
     - Login/logout (sucesso/falha)
     - Mudanças de permissões
     - Acesso a recursos sensíveis
   - Campos: timestamp, user_id, action, resource, result, ip, user_agent, request_id
   - Integrar com logging estruturado
   - Criar backend/services/audit_service.py

3. RBAC:
   - Roles: USER, ADMIN
   - Decorator @require_role("admin")
   - Validar em endpoints sensíveis
   - Retornar 403 se sem permissão
   - Logar tentativas de acesso negado

4. Testes:
   - 40+ testes de segurança
   - Rate limiting (hit limit, 429)
   - Audit logging (ações registradas)
   - RBAC (autorizado/negado)

5. Documentar:
   - Políticas de rate limiting
   - Como consultar audit logs
   - Estrutura de RBAC
   - Criar docs/SECURITY.md

[FORMATO DE SAÍDA]
1. Arquivos criados:
   - backend/observability/rate_limiting.py
   - backend/services/audit_service.py
   - backend/core/authorization.py
   - tests/unit/test_security.py
2. Instruções de integração
3. Exemplos de audit logs
4. Documentação SECURITY.md

[RESTRIÇÕES]
- NÃO expor informações em erros (user exists, etc.)
- Rate limiting não deve afetar usuários legítimos
- Audit logs NUNCA modificáveis/deletáveis
- RBAC fail-safe (negar por padrão)
- 0 secrets hardcoded

[MÉTRICAS]
- Rate limiting retornando 429
- Audit trail de 100% ações críticas
- RBAC bloqueando acessos não autorizados
- 40+ testes passando
- 0 secrets em código
```

---

## ✅ Checklists de Production-Readiness

### Checklist Geral (98% Production-Ready)

#### 1. Código e Arquitetura ✅

```markdown
- [ ] Estrutura de diretórios clara e documentada
- [ ] Separação de concerns (models, services, routers, etc.)
- [ ] Configuração via environment variables (.env)
- [ ] 0 secrets hardcoded
- [ ] Linting configurado e passando (score >= 8.0)
- [ ] Type hints (Python) ou TypeScript
- [ ] Docstrings/JSDoc para métodos públicos
```

#### 2. Testes ✅

```markdown
- [ ] Cobertura >= 85%
- [ ] Testes unitários para todos os serviços
- [ ] Testes de integração consolidados
- [ ] Testes E2E para fluxos críticos (5-10 fluxos)
- [ ] Testes de CLI (se aplicável)
- [ ] Testes de segurança (40+ testes)
- [ ] Testes executam em < 5 minutos
- [ ] 0 testes flakey (intermitentes)
- [ ] Mocks apropriados (sem dependências externas)
```

#### 3. Observabilidade ✅

```markdown
- [ ] Logging estruturado (JSON para prod, console para dev)
- [ ] Request ID em todos os logs
- [ ] Trace ID para distributed tracing
- [ ] Métricas Prometheus (/metrics)
- [ ] Métricas HTTP (requests, duration, errors)
- [ ] Métricas de negócio (se aplicável)
- [ ] Health checks (/health, /healthz)
- [ ] Readiness checks (DB, Redis, etc.)
- [ ] 0 dados sensíveis em logs
```

#### 4. Segurança ✅

```markdown
- [ ] Autenticação robusta (JWT + refresh tokens)
- [ ] Rate limiting por endpoint
- [ ] Rate limiting distribuído (se multi-instância)
- [ ] Audit logging para ações críticas
- [ ] RBAC com validação de ownership
- [ ] MFA/2FA (opcional ou obrigatório)
- [ ] HTTPS obrigatório em produção
- [ ] CORS configurado adequadamente
- [ ] Headers de segurança (CSP, X-Frame-Options, etc.)
- [ ] Input validation e sanitization
- [ ] SQL injection protection (ORM)
- [ ] XSS protection
- [ ] CSRF protection (se stateful)
```

#### 5. CI/CD ✅

```markdown
- [ ] Pipeline automatizado (GitHub Actions, GitLab CI, etc.)
- [ ] Jobs separados (unit, integration, e2e, lint, coverage)
- [ ] Security gates:
  - [ ] SAST (Bandit, ESLint security, etc.)
  - [ ] Dependency scanning (Safety, npm audit, etc.)
  - [ ] Secret scanning (TruffleHog, etc.)
- [ ] Coverage reporting (Codecov, Coveralls)
- [ ] Badges de status no README
- [ ] Política de merge (CI must pass)
- [ ] Deploy automatizado (staging)
```

#### 6. Segurança - Scans ✅

```markdown
- [ ] SAST executado e documentado
- [ ] Dependency scan executado
- [ ] 0 vulnerabilidades críticas não mitigadas
- [ ] Vulnerabilidades médias justificadas
- [ ] Security summary documentado
- [ ] Dependências críticas atualizadas
```

#### 7. Operações ✅

```markdown
- [ ] Operations runbook (500+ linhas):
  - [ ] Detecção de incidentes
  - [ ] Triagem inicial
  - [ ] Procedimentos de rollback
  - [ ] Investigação com audit logs
  - [ ] Troubleshooting comum
  - [ ] Checklist pós-incidente
- [ ] Scripts de backup automatizados
- [ ] Scripts de restore validados
- [ ] Disaster recovery testado
- [ ] RPO < 24h, RTO < 30 min
- [ ] Procedimentos de escalação documentados
```

#### 8. Documentação ✅

```markdown
- [ ] README completo e atualizado:
  - [ ] Quick start (5 minutos)
  - [ ] Instalação e configuração
  - [ ] Comandos principais
  - [ ] Exemplos de uso
  - [ ] Badges de status
- [ ] Estrutura documentada (STRUCTURE.md)
- [ ] Guia de contribuição (CONTRIBUTING.md)
- [ ] Documentação de API (Swagger/OpenAPI)
- [ ] Runbook operacional
- [ ] Guia de observabilidade
- [ ] Guia de segurança
- [ ] Changelog atualizado
- [ ] Relatórios de sprint
```

#### 9. Infraestrutura 🔄

```markdown
- [ ] Containerização (Dockerfile)
- [ ] Docker Compose para dev
- [ ] Orquestração (K8s manifests ou equivalente)
- [ ] Configuração por ambiente (.env)
- [ ] Secrets management (Vault, AWS Secrets Manager, etc.)
- [ ] Monitoramento (Prometheus + Grafana)
- [ ] Alerting configurado (Alertmanager)
- [ ] Backups agendados (cron/systemd)
- [ ] Load balancing (se multi-instância)
- [ ] Auto-scaling (se necessário)
```

#### 10. Compliance 🔄 (Opcional)

```markdown
- [ ] LGPD/GDPR compliance (se aplicável)
- [ ] SOC 2 / ISO 27001 (se necessário)
- [ ] Penetration testing externo
- [ ] Audit logs retention policy (90+ dias)
- [ ] Data encryption at rest
- [ ] Data encryption in transit (TLS)
- [ ] Privacy policy documentada
- [ ] Terms of service documentados
```

**Legenda:**
- ✅ Implementado (baseado em 3dPot Sprint 9)
- 🔄 Parcial ou próximos passos

---

### Checklist por Sprint

#### Sprint 1: Estrutura
```markdown
- [ ] Diretórios organizados (src, tests, docs, scripts)
- [ ] Arquivos na raiz reduzidos (>70%)
- [ ] README atualizado
- [ ] STRUCTURE.md criado
- [ ] MIGRATION_GUIDE.md (se aplicável)
- [ ] .gitignore atualizado
- [ ] Build/testes funcionando
```

#### Sprint 2: Testes Básicos
```markdown
- [ ] 150+ testes unitários
- [ ] 5-7 módulos críticos cobertos
- [ ] Cobertura >= 70%
- [ ] Coverage reporting configurado
- [ ] Tempo de execução < 1 minuto
- [ ] TESTING.md documentado
```

#### Sprint 3: Integração + CLI
```markdown
- [ ] Testes de integração consolidados
- [ ] CLI com 8-10 comandos
- [ ] 5-10 testes E2E
- [ ] CLI documentada
- [ ] Testes CLI criados
```

#### Sprint 4: Cobertura + CI
```markdown
- [ ] 80-120 novos testes
- [ ] 3-5 módulos secundários cobertos
- [ ] CI/CD configurado
- [ ] Jobs separados (unit, lint, coverage)
- [ ] Coverage threshold enforced
- [ ] Badges no README
```

#### Sprint 5: Qualidade Final
```markdown
- [ ] 100% serviços com testes
- [ ] Cobertura >= 85%
- [ ] Framework de performance
- [ ] Benchmarks documentados
- [ ] QUALITY_REPORT.md
```

#### Sprint 6: Observabilidade
```markdown
- [ ] Logging estruturado (JSON + console)
- [ ] Request ID implementado
- [ ] /metrics endpoint
- [ ] Middleware de logging
- [ ] OBSERVABILITY.md
```

#### Sprint 7: Segurança Base
```markdown
- [ ] Rate limiting implementado
- [ ] Audit logging implementado
- [ ] RBAC funcional
- [ ] 0 secrets hardcoded
- [ ] 40+ testes de segurança
- [ ] SECURITY.md
```

#### Sprint 8: Hardening
```markdown
- [ ] Rate limiting distribuído (Redis)
- [ ] RBAC granular (ownership)
- [ ] CI/CD security gates
- [ ] Métricas de segurança
- [ ] Runbook inicial
```

#### Sprint 9: Ops + DR
```markdown
- [ ] MFA/2FA implementado
- [ ] Scripts backup/restore
- [ ] Trace ID implementado
- [ ] Runbook 500+ linhas
- [ ] Security scans executados
- [ ] 0 vulnerabilidades críticas
- [ ] Production-ready >= 98%
```

---

## 🛠️ Ferramentas e Recursos

### Ferramentas por Categoria

#### Testes
- **Python:** pytest, pytest-cov, pytest-mock, freezegun
- **JavaScript:** jest, vitest, mocha, chai
- **Java:** JUnit, TestNG, Mockito
- **Go:** testing package, testify

#### Observabilidade
- **Logging:** structlog (Python), winston/pino (JS), logback (Java), zap/logrus (Go)
- **Métricas:** Prometheus, StatsD, OpenTelemetry
- **Tracing:** Jaeger, Zipkin, OpenTelemetry
- **Monitoramento:** Grafana, Datadog, New Relic

#### Segurança
- **SAST:** Bandit (Python), ESLint security, SpotBugs (Java), gosec (Go)
- **Dependency Scan:** Safety, pip-audit (Python), npm audit (JS), OWASP Dependency Check
- **Secret Scan:** TruffleHog, git-secrets, detect-secrets
- **Penetration Test:** OWASP ZAP, Burp Suite

#### CI/CD
- **Plataformas:** GitHub Actions, GitLab CI, Jenkins, CircleCI
- **Coverage:** Codecov, Coveralls, SonarQube
- **Badges:** Shields.io

#### Infraestrutura
- **Containers:** Docker, Podman
- **Orquestração:** Kubernetes, Docker Compose, Nomad
- **Secrets:** Vault, AWS Secrets Manager, Azure Key Vault

### Recursos de Aprendizado

#### Documentação Oficial
- [Pytest Documentation](https://docs.pytest.org/)
- [Structlog Documentation](https://www.structlog.org/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

#### Guias e Tutoriais
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App](https://12factor.net/)
- [SRE Books (Google)](https://sre.google/books/)

---

## 🔧 Solução de Problemas

### Problema 1: IA Gera Código Muito Genérico

**Sintomas:**
- Código com muitos comentários "# TODO"
- Pseudocódigo em vez de implementação real
- Falta de integração com código existente

**Soluções:**
1. ✅ Adicione mais contexto ao prompt (stack, framework, versões)
2. ✅ Forneça exemplos de código existente
3. ✅ Seja específico sobre o que você quer (não "criar testes", mas "criar 40 testes pytest para auth_service.py")
4. ✅ Peça código executável, não exemplos

---

### Problema 2: Testes Gerados Falham

**Sintomas:**
- Testes não passam ao executar
- Imports incorretos
- Mocks não configurados

**Soluções:**
1. ✅ Revise e ajuste imports manualmente
2. ✅ Verifique se mocks estão configurados corretamente
3. ✅ Execute testes incrementalmente (1-2 por vez)
4. ✅ Peça para IA revisar testes falhando (forneça erro)

---

### Problema 3: Código Não Segue Padrões do Projeto

**Sintomas:**
- Estilo diferente (camelCase vs snake_case)
- Estrutura de arquivos não alinhada
- Convenções de nomenclatura diferentes

**Soluções:**
1. ✅ Inclua exemplos de código existente no prompt
2. ✅ Especifique padrões explicitamente (PEP 8, Airbnb style, etc.)
3. ✅ Use linters para validar (pylint, eslint)
4. ✅ Peça para IA refatorar seguindo padrões

---

### Problema 4: Muitas Mudanças de Uma Vez

**Sintomas:**
- Difícil de revisar
- Não sabe o que mudou
- Risco de quebrar algo

**Soluções:**
1. ✅ Divida sprint em tarefas menores
2. ✅ Aplique mudanças incrementalmente
3. ✅ Execute testes após cada mudança
4. ✅ Use controle de versão (commits pequenos)

---

### Problema 5: CI/CD Quebrando Após Sprint

**Sintomas:**
- Pipeline falhando
- Testes passam localmente mas falham no CI
- Coverage abaixo do threshold

**Soluções:**
1. ✅ Execute CI localmente antes (act para GitHub Actions)
2. ✅ Verifique dependências (requirements.txt atualizado?)
3. ✅ Revise configuração do CI (.github/workflows/)
4. ✅ Ajuste threshold de coverage se necessário

---

## 🎓 Conclusão

Este playbook documenta um método comprovado para evoluir projetos de software usando IA. A chave do sucesso é:

1. **Dividir em Sprints:** Incrementos pequenos e validáveis
2. **Prompts Eficazes:** Contexto, objetivo, restrições, métricas
3. **Validação Contínua:** Testes, scans, reviews
4. **Documentação Viva:** Relatórios de sprint, aprendizados
5. **IA como Parceira:** IA sugere, humano valida e refina

### Próximos Passos

1. **Escolha Sua Sprint:** Comece com Sprint 1 (Estrutura) se novo, ou Sprint 6 (Observabilidade) se código já testado
2. **Adapte os Prompts:** Use AI-SPRINT-PROMPTS.md como base
3. **Execute e Valide:** Siga checklists de validação
4. **Documente:** Crie relatórios de sprint
5. **Itere:** Refine prompts baseado em resultados

### Recursos Adicionais

- **Framework Completo:** [AI-SPRINT-FRAMEWORK.md](./AI-SPRINT-FRAMEWORK.md)
- **Prompts Reutilizáveis:** [AI-SPRINT-PROMPTS.md](./AI-SPRINT-PROMPTS.md)
- **Exemplo Real:** Sprints 1-9 do projeto 3dPot

---

**Versão:** 1.0  
**Última Atualização:** Novembro 2025  
**Baseado em:** 3dPot Sprints 1-9  
**Status:** Production-Ready Playbook

---

## 📞 Feedback e Contribuições

Este playbook é um documento vivo. Se você usar este método em seu projeto:

1. **Compartilhe resultados:** Métricas antes/depois
2. **Documente ajustes:** Prompts que funcionaram melhor
3. **Relate problemas:** Desafios encontrados e soluções
4. **Sugira melhorias:** Novas sprints, ferramentas, práticas

**Happy Engineering with AI! 🚀**
