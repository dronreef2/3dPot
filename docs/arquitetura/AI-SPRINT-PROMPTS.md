# Prompts Reutilizáveis para Sprints com IA

**Versão:** 1.0  
**Data:** Novembro 2025  
**Uso:** Copie e adapte estes prompts para seus repositórios

---

## 📋 Como Usar Este Documento

1. **Identifique a Sprint**: Escolha qual sprint você quer executar (1-9)
2. **Copie o Prompt**: Copie o prompt correspondente
3. **Substitua Placeholders**: Preencha [REPO_URL], [STACK], etc.
4. **Execute com IA**: Cole no seu assistente de IA (GitHub Copilot, ChatGPT, Claude)
5. **Valide Resultados**: Revise e teste as mudanças propostas
6. **Itere se Necessário**: Refine o prompt baseado nos resultados

---

## 🎯 Sprint 1: Reorganização e Estrutura

### Prompt Template

```
Você é um assistente sênior de engenharia especializado em reorganização de repositórios.

[CONTEXTO]
Repositório: [REPO_URL]
Stack principal: [LINGUAGEM/STACK, ex: Python/FastAPI, Node.js/Express, Java/Spring]
Tamanho do repositório: [PEQUENO < 50 arquivos | MÉDIO 50-200 | GRANDE > 200]

[PROBLEMA]
O repositório está desorganizado com muitos arquivos na raiz, dificultando navegação e onboarding de novos desenvolvedores.

[OBJETIVO]
Reorganizar o repositório em uma estrutura clara e navegável, seguindo as melhores práticas para [LINGUAGEM/STACK].

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Auditar Estrutura Atual**
   - Listar todos os arquivos na raiz
   - Identificar tipos/categorias de arquivos
   - Contar arquivos por categoria

2. **Propor Nova Estrutura**
   - Criar hierarquia de diretórios apropriada:
     - src/ ou backend/ (código principal)
     - tests/ (todos os testes)
     - docs/ (documentação, subdividida por tipo)
     - scripts/ (utilitários, subdivididos por função)
     - [OUTROS específicos do stack]
   - Explicar razão de cada diretório

3. **Executar Reorganização**
   - Mover arquivos para locais apropriados
   - Atualizar imports/require/include statements
   - Atualizar paths em configs (package.json, setup.py, etc.)
   - Preservar histórico do git (usar git mv)

4. **Atualizar Documentação**
   - Criar/atualizar README.md com nova estrutura
   - Criar STRUCTURE.md detalhando organização
   - Criar MIGRATION_GUIDE.md se houver código em desenvolvimento
   - Atualizar .gitignore conforme necessário

5. **Validar**
   - Garantir que build/testes continuem funcionando
   - Verificar se todos os imports foram corrigidos
   - Confirmar que CI/CD não quebrou

[FORMATO DE SAÍDA]

1. **Relatório de Auditoria**: Lista de arquivos por categoria
2. **Proposta de Estrutura**: Árvore de diretórios com justificativas
3. **Plano de Migração**: Sequência de comandos git mv
4. **Arquivos Modificados**: Lista de arquivos com imports atualizados
5. **Documentação Gerada**:
   - STRUCTURE.md
   - MIGRATION_GUIDE.md (se aplicável)
   - README.md atualizado

[RESTRIÇÕES]

- NÃO quebrar funcionalidade existente
- NÃO modificar lógica de negócio
- NÃO remover arquivos importantes
- PRESERVAR histórico do git (usar git mv, não delete+create)
- Manter compatibilidade com CI/CD existente
- Arquivos essenciais podem permanecer na raiz (README, LICENSE, etc.)

[MÉTRICAS DE SUCESSO]

- Redução de arquivos na raiz em >= 70%
- Estrutura de diretórios clara e autodescritiva
- Build e testes continuam passando
- Documentação atualizada e completa
```

### Exemplo de Uso (3dPot)

```
Repositório: https://github.com/dronreef2/3dPot
Stack principal: Python/FastAPI + React
Tamanho: GRANDE (>200 arquivos)

Resultado: 145 arquivos reorganizados, redução de 80% na raiz
```

---

## 🧪 Sprint 2: Testes Básicos de Unidade

### Prompt Template

```
Você é um especialista em testes de software e qualidade de código.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Framework de testes: [pytest, jest, JUnit, etc.]
Cobertura atual: [PERCENTUAL, ex: 40%]

[PROBLEMA]
O repositório tem cobertura de testes insuficiente, especialmente em módulos críticos de negócio.

[OBJETIVO]
Implementar testes unitários abrangentes para os 5-7 módulos mais críticos, elevando a cobertura de [ATUAL]% para ~70-75%.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Mapear Módulos Críticos**
   - Listar todos os módulos/serviços do projeto
   - Identificar quais NÃO têm testes
   - Priorizar por criticidade de negócio:
     - 🔴 ALTA: Core business logic, usados em fluxos principais
     - 🟡 MÉDIA: Importantes mas não bloqueantes
     - 🟢 BAIXA: Auxiliares ou em desenvolvimento
   - Selecionar top 5-7 de criticidade ALTA

2. **Criar Testes Unitários**
   Para cada módulo selecionado:
   - Criar arquivo de teste seguindo convenção ([test_*.py, *.test.js, etc.])
   - Implementar 20-50 testes cobrindo:
     - Happy paths (cenários principais)
     - Edge cases (limites, valores extremos)
     - Error handling (exceções, erros)
     - Validações de dados
     - Mocks de dependências externas
   - Organizar em classes/describes por funcionalidade
   - Nomear testes descritivamente (test_should_*, test_when_then_*)

3. **Configurar Coverage Reporting**
   - Adicionar ferramenta de coverage ([pytest-cov, jest --coverage, jacoco])
   - Configurar threshold mínimo (70%)
   - Gerar relatórios HTML para visualização
   - Adicionar coverage ao CI/CD

4. **Documentar Padrões**
   - Criar guia de testes (TESTING.md)
   - Documentar estrutura de testes
   - Explicar uso de mocks/fixtures
   - Fornecer exemplos de bons testes

5. **Validar Qualidade**
   - Todos os testes devem passar
   - Coverage >= 70%
   - Tempo de execução < 1 minuto
   - Sem testes flakey (intermitentes)

[FORMATO DE SAÍDA]

1. **Mapeamento de Módulos**: Tabela com nome, criticidade, linhas de código
2. **Testes Implementados**: Lista de arquivos criados com número de testes
3. **Relatório de Coverage**: % antes e depois, por módulo
4. **Documentação**:
   - TESTING.md com padrões e exemplos
   - README.md atualizado com comandos de teste
5. **Relatório de Sprint**: Resumo executivo das mudanças

[RESTRIÇÕES]

- NÃO modificar código de produção (exceto para testabilidade)
- NÃO criar testes que dependam de serviços externos reais
- USAR mocks/stubs para dependências externas
- NÃO criar testes flakey ou com sleeps
- Seguir convenções existentes de testes

[MÉTRICAS DE SUCESSO]

- 150-200 novos testes unitários
- 5-7 módulos críticos cobertos
- Cobertura aumenta >= 30 pontos percentuais
- Tempo de execução < 1 minuto
- 0 regressões (testes antigos continuam passando)
```

### Exemplo de Uso (3dPot)

```
Stack: Python/FastAPI
Framework: pytest
Cobertura atual: 40%

Módulos priorizados:
1. budgeting_service.py (48 testes)
2. modeling_service.py (41 testes)
3. print3d_service.py (43 testes)
4. simulation_service.py (32 testes)
5. production_service.py (27 testes)

Resultado: 191 testes novos, cobertura de 40% → 72%
```

---

## 🔗 Sprint 3: Integração + CLI

### Prompt Template

```
Você é um especialista em testes de integração e ferramentas de linha de comando.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Testes unitários: [QUANTIDADE existente]
CLI existente: [SIM/NÃO]

[OBJETIVO]
Consolidar testes de integração e criar CLI unificada para demos e ferramentas de desenvolvimento.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Auditar Testes de Integração**
   - Listar todos os arquivos de testes de integração
   - Identificar duplicações ou redundâncias
   - Agrupar por tipo (backend core, API, hardware, etc.)

2. **Consolidar Testes**
   - Unificar testes duplicados em arquivos principais
   - Organizar em classes/describes lógicos
   - Eliminar cenários redundantes
   - Manter testes específicos separados se necessário
   - Usar pytest.skip() ou equivalente para dependências opcionais

3. **Criar CLI Unificada**
   - Estrutura sugerida:
     ```
     scripts/cli/
     ├── __init__.py
     ├── __main__.py (permite python -m scripts.cli)
     └── main.py (implementação)
     ```
   - Implementar 8-10 comandos úteis:
     - setup: Configuração inicial
     - test: Executar testes
     - lint: Verificar código
     - demo-[feature]: Demonstrações
     - validate: Validações diversas
     - [OUTROS específicos do projeto]
   - Usar argparse, click ou typer
   - Adicionar help text completo

4. **Implementar Testes E2E**
   - Identificar 2-5 fluxos críticos de usuário
   - Criar testes end-to-end para cada fluxo
   - Usar ferramentas apropriadas (pytest, Playwright, Selenium)
   - Garantir isolamento (cada teste independente)

5. **Documentar**
   - README com seção de CLI
   - Exemplos de uso para cada comando
   - Guia de testes de integração
   - Atualizar CI/CD se necessário

[FORMATO DE SAÍDA]

1. **Análise de Duplicação**: Quais testes foram consolidados
2. **CLI Implementada**: Lista de comandos com descrição
3. **Testes E2E**: Fluxos cobertos
4. **Documentação**:
   - README.md atualizado
   - CLI_GUIDE.md (se aplicável)
5. **Relatório de Sprint**

[RESTRIÇÕES]

- NÃO remover testes válidos
- NÃO quebrar testes existentes
- CLI deve ser fácil de usar (help integrado)
- E2E devem ser determinísticos (não flakey)
- Documentar dependências da CLI

[MÉTRICAS DE SUCESSO]

- Redução de duplicação >= 50%
- CLI funcional com 8+ comandos
- 5-10 testes E2E cobrindo fluxos críticos
- Documentação completa e exemplos
```

---

## 📊 Sprint 4: Cobertura Ampliada + CI

### Prompt Template

```
Você é um especialista em CI/CD e testes automatizados.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Cobertura atual: [PERCENTUAL]
CI/CD: [GitHub Actions, GitLab CI, Jenkins, etc.]

[OBJETIVO]
Expandir cobertura de testes para módulos secundários, adicionar testes CLI e E2E, e fortalecer pipeline CI/CD.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Cobrir Módulos Secundários**
   - Identificar 3-5 módulos secundários sem testes
   - Criar 20-40 testes para cada módulo
   - Focar em funcionalidades mais usadas

2. **Expandir E2E**
   - Adicionar 3-5 novos fluxos E2E
   - Cobrir cenários avançados e edge cases
   - Incluir testes de erro (400, 404, 500)

3. **Testar CLI**
   - Criar 20-30 testes para comandos CLI
   - Testar saídas, exit codes, help text
   - Mockar operações destrutivas

4. **Fortalecer CI/CD**
   - Criar jobs separados:
     - unit-tests
     - integration-tests
     - e2e-tests (se aplicável)
     - lint
     - coverage
   - Adicionar coverage reporting (Codecov, Coveralls)
   - Configurar threshold de cobertura
   - Adicionar status badges ao README
   - Implementar política de merge (CI must pass)

5. **Documentar Pipeline**
   - README com badges de CI
   - Instruções para rodar testes localmente
   - Troubleshooting de CI

[FORMATO DE SAÍDA]

1. **Testes Criados**: Resumo por categoria
2. **Pipeline CI/CD**: Diagrama ou descrição dos jobs
3. **Coverage Report**: Antes/depois
4. **Documentação**:
   - README.md com badges
   - CI_CD.md (se complexo)
5. **Relatório de Sprint**

[RESTRIÇÕES]

- CI deve executar em < 5-10 minutos
- Testes E2E não devem depender de infraestrutura externa
- Coverage threshold deve ser realista (70-80%)
- Documentar dependências de CI

[MÉTRICAS DE SUCESSO]

- 80-120 novos testes unitários
- 3-5 novos fluxos E2E
- 20-30 testes CLI
- CI/CD funcionando com jobs separados
- Coverage +5-10 pontos percentuais
```

---

## ✅ Sprint 5: Qualidade Final

### Prompt Template

```
Você é um especialista em qualidade de software e performance.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Cobertura atual: [PERCENTUAL]
Serviços sem testes: [QUANTIDADE]

[OBJETIVO]
Atingir 100% de cobertura de serviços e estabelecer baseline de performance.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Completar Cobertura de Serviços**
   - Identificar TODOS os serviços/módulos restantes sem testes
   - Criar testes para cada um (15-30 testes por serviço)
   - Priorizar cobertura de happy paths e error handling

2. **Performance Testing**
   - Criar script de benchmark para operações críticas
   - Medir:
     - Tempo médio de execução
     - Throughput (ops/segundo)
     - Latência p50, p95, p99
   - Estabelecer baseline documentada
   - Identificar gargalos óbvios

3. **Refinar CLI**
   - Adicionar utilitários centralizados (se aplicável)
   - Melhorar mensagens de erro
   - Adicionar validações de input
   - Criar testes para novos utilitários

4. **Expandir E2E Avançado**
   - Adicionar 3-5 cenários avançados
   - Testar combinações complexas
   - Incluir testes de erro e recuperação

5. **Documentar Estado de Qualidade**
   - Relatório de cobertura completo
   - Benchmarks de performance
   - Roadmap para Release Candidate

[FORMATO DE SAÍDA]

1. **Testes Implementados**: Por serviço
2. **Performance Benchmarks**: Tabela de métricas
3. **Relatório de Qualidade**: Estado atual completo
4. **Documentação**:
   - QUALITY_REPORT.md
   - PERFORMANCE_BASELINE.md
   - Roadmap para produção
5. **Relatório de Sprint**

[RESTRIÇÕES]

- NÃO otimizar prematuramente
- Performance baseline é para referência, não otimização
- Todos os serviços DEVEM ter testes básicos
- Documentação deve ser objetiva

[MÉTRICAS DE SUCESSO]

- 100% dos serviços com testes
- Cobertura >= 85%
- Benchmarks estabelecidos e documentados
- Roadmap claro para Release Candidate
```

---

## 📡 Sprint 6: Observabilidade

### Prompt Template

```
Você é um especialista em observabilidade e sistemas distribuídos.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Framework web: [FastAPI, Express, Spring Boot, etc.]
Observabilidade atual: [BÁSICA/NENHUMA]

[OBJETIVO]
Implementar observabilidade production-ready com logging estruturado, métricas e tracing.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Logging Estruturado**
   - Implementar logger estruturado (structlog, winston, etc.)
   - Suportar dois formatos:
     - JSON para produção
     - Console formatado para desenvolvimento
   - Configurar níveis via environment (LOG_LEVEL)
   - Campos padrão:
     - timestamp (ISO 8601)
     - level (info, error, etc.)
     - logger name
     - event/message
     - service name
     - version
     - request_id (próximo passo)
   - Criar utilitário get_logger() ou equivalente

2. **Request ID / Correlation ID**
   - Implementar middleware para adicionar request_id único
   - Propagar em headers (X-Request-ID)
   - Incluir em todos os logs
   - Retornar na resposta para rastreamento

3. **Métricas Prometheus**
   - Implementar endpoint /metrics
   - Métricas HTTP básicas:
     - http_requests_total (counter)
     - http_request_duration_seconds (histogram)
     - http_requests_in_progress (gauge)
   - Labels: method, endpoint, status
   - Métricas de serviço (se aplicável):
     - [service]_operations_total
     - [service]_errors_total
     - [service]_duration_seconds

4. **Middleware de Logging Automático**
   - Logar todas as requisições HTTP
   - Incluir: method, path, status, duration
   - Logs especiais para 4xx/5xx
   - Excluir health checks por padrão

5. **Documentar Observabilidade**
   - Padrões de logging
   - Como usar request_id para debugging
   - Exemplos de queries Prometheus
   - Guia de configuração

[FORMATO DE SAÍDA]

1. **Código Implementado**: Arquivos de observabilidade
2. **Exemplos de Logs**: JSON e console
3. **Métricas Expostas**: Lista e descrição
4. **Documentação**:
   - OBSERVABILITY.md
   - README.md atualizado
5. **Relatório de Sprint**

[RESTRIÇÕES]

- NÃO logar dados sensíveis (passwords, tokens)
- NÃO logar health checks (muito ruído)
- Formato JSON deve ser parseable
- Métricas devem seguir convenções Prometheus
- Performance overhead mínimo

[MÉTRICAS DE SUCESSO]

- Logs estruturados em JSON para produção
- Request ID em todos os logs
- /metrics funcional com métricas HTTP
- Middleware de logging automático
- Documentação completa
```

---

## 🔐 Sprint 7: Segurança Base

### Prompt Template

```
Você é um especialista em segurança de aplicações.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Autenticação atual: [JWT, OAuth, etc.]
Observabilidade: [IMPLEMENTADA na Sprint 6]

[OBJETIVO]
Implementar controles de segurança essenciais: rate limiting, audit logging, RBAC.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Rate Limiting**
   - Implementar algoritmo Token Bucket
   - Configurar limites por endpoint:
     - Login/Register: 10 req/min
     - APIs caras: 30 req/min
     - Outros: 60 req/min
   - Diferenciar por IP e usuário autenticado
   - Retornar 429 Too Many Requests
   - Headers: X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After
   - Configurável via environment variables

2. **Audit Logging**
   - Criar serviço de audit logging
   - Registrar ações críticas:
     - Login/logout (sucesso e falha)
     - Mudanças de permissões
     - Acesso a recursos sensíveis
     - Mudanças em configurações
   - Campos do audit log:
     - timestamp
     - user_id
     - action
     - resource
     - result (success/failure)
     - ip_address
     - user_agent
     - request_id (para correlação)
   - Armazenar em tabela separada (não deletar)

3. **RBAC (Role-Based Access Control)**
   - Definir roles: USER, ADMIN, [outros específicos]
   - Implementar decorators/middleware de autorização
   - Validar permissões em endpoints sensíveis
   - Retornar 403 Forbidden se sem permissão
   - Logar tentativas de acesso negado

4. **Gestão Segura de Secrets**
   - Validar que TODAS as configs vêm de .env
   - NÃO ter secrets hardcoded
   - Criar .env.example com placeholders
   - Documentar variáveis obrigatórias e opcionais
   - Adicionar validação de env na inicialização

5. **Testes de Segurança**
   - Criar 40+ testes:
     - Rate limiting (hit limit, resposta 429)
     - Audit logging (ações registradas)
     - RBAC (acesso autorizado/negado)
     - Validação de secrets

6. **Documentar Segurança**
   - Políticas de rate limiting
   - Como usar audit logs
   - Estrutura de RBAC
   - Guia de configuração segura

[FORMATO DE SAÍDA]

1. **Código Implementado**: Rate limiter, audit service, RBAC
2. **Testes de Segurança**: Cobertura de cenários
3. **Documentação**:
   - SECURITY.md
   - .env.example
   - Guia de RBAC
4. **Relatório de Sprint**

[RESTRIÇÕES]

- NÃO expor informações sensíveis em erros
- Rate limiting não deve afetar usuários legítimos
- Audit logs NÃO podem ser modificados/deletados
- RBAC deve ser fail-safe (negar por padrão)
- Secrets NUNCA em código

[MÉTRICAS DE SUCESSO]

- Rate limiting funcionando (429 em abuse)
- Audit trail completo de ações críticas
- RBAC bloqueando acessos não autorizados
- 0 secrets hardcoded
- 40+ testes de segurança passando
```

---

## 🛡️ Sprint 8: Hardening e Escala

### Prompt Template

```
Você é um especialista em escalabilidade e hardening de segurança.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Rate limiting atual: In-memory
Infraestrutura: [Redis disponível? Docker? Kubernetes?]

[OBJETIVO]
Preparar para escala horizontal com rate limiting distribuído e adicionar security gates no CI/CD.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Rate Limiting Distribuído**
   - Implementar backend Redis para rate limiting
   - Manter fallback para in-memory se Redis indisponível
   - Configurar via RATE_LIMIT_BACKEND=redis|in-memory
   - TTL automático para limpeza
   - Métricas: rate_limit_hits_total

2. **RBAC Granular**
   - Adicionar validação de ownership
   - Exemplo: Usuário só pode editar seus próprios recursos
   - Implementar has_permission(user, action, resource)
   - Testes de ownership

3. **CI/CD Security Gates**
   - Adicionar jobs de segurança:
     - SAST (Bandit, ESLint security, etc.)
     - Dependency scanning (Safety, npm audit, Snyk)
     - Secret scanning (TruffleHog, git-secrets)
   - Configurar para FAIL o build em vulnerabilidades críticas
   - Gerar relatórios de segurança
   - Badge de security status no README

4. **Métricas de Segurança**
   - Expor métricas de segurança no /metrics:
     - rate_limit_hits_total
     - auth_failures_total
     - permission_denied_total
   - Permitir alertas baseados em thresholds

5. **Documentar Operações**
   - Runbook inicial de operações
   - Troubleshooting comum
   - Como escalar horizontalmente
   - Guia de security gates

[FORMATO DE SAÍDA]

1. **Código Implementado**: Redis rate limiter, RBAC granular
2. **Pipeline CI/CD**: Security gates configurados
3. **Métricas**: Lista de métricas de segurança
4. **Documentação**:
   - OPERATIONS_RUNBOOK.md (inicial)
   - SECURITY_GATES.md
5. **Relatório de Sprint**

[RESTRIÇÕES]

- Redis deve ser opcional (fallback in-memory)
- Security gates não devem ter muitos falsos positivos
- Runbook deve ser prático e acionável
- Documentar como executar scans localmente

[MÉTRICAS DE SUCESSO]

- Rate limiting compartilhado entre instâncias (Redis)
- RBAC validando ownership
- CI falhando em vulnerabilidades críticas
- 0 vulnerabilidades críticas não mitigadas
- Runbook operacional documentado
```

---

## 🚀 Sprint 9: Operações, DR e MFA

### Prompt Template

```
Você é um especialista em operações, disaster recovery e autenticação avançada.

[CONTEXTO]
Repositório: [REPO_URL]
Stack: [LINGUAGEM/STACK]
Banco de dados: [PostgreSQL, MySQL, MongoDB, etc.]
Production-readiness: [PERCENTUAL atual, ex: 95%]

[OBJETIVO]
Completar preparação para produção com MFA, disaster recovery e runbook operacional completo.

[TAREFAS QUE VOCÊ DEVE EXECUTAR]

1. **Multi-Factor Authentication (MFA/2FA)**
   - Implementar TOTP (Time-based One-Time Password)
   - Bibliotecas: pyotp, speakeasy, etc.
   - Funcionalidades:
     - Gerar secret TOTP
     - Gerar QR code para apps autenticadores
     - Validar códigos TOTP (janela de tolerância)
     - Backup codes (10 códigos únicos, one-time use)
   - Integração com login:
     - Login retorna mfa_required=true se MFA habilitado
     - Challenge token (JWT de 5 min)
     - Endpoint para validar MFA e obter tokens finais
   - Endpoints:
     - POST /mfa/enable (inicia enrollment, retorna QR)
     - POST /mfa/confirm (confirma com primeiro código)
     - POST /mfa/disable (desabilita MFA)
     - POST /mfa/verify (valida código durante login)
   - Configuração:
     - MFA_ENABLED=true|false
     - MFA_REQUIRED_FOR_ADMIN=true|false
   - Retrocompatível: MFA opcional por padrão

2. **Disaster Recovery (DR)**
   - Script de backup:
     - Backup de banco de dados (pg_dump, mysqldump, mongodump)
     - Backup de storage (arquivos, uploads)
     - Manifest JSON com metadados (timestamp, size, checksums)
     - Validação de espaço em disco
     - Logging estruturado
   - Script de restore:
     - Restore de banco de dados
     - Restore de storage
     - Validação de manifest
     - Validação de integridade
     - Confirmação interativa
   - Configuração:
     - Retenção (dias)
     - Destino de backup (local, S3, etc.)
   - Documentar:
     - Como executar backups
     - Como restaurar
     - RPO/RTO esperados
     - Procedimento de DR drill

3. **Distributed Tracing**
   - Implementar trace_id adicional ao request_id
   - Propagar trace_id em headers (X-Trace-Id)
   - Incluir em logs estruturados
   - Permitir correlação de eventos entre múltiplas requisições

4. **Operations Runbook Completo**
   - Criar runbook de 500+ linhas com:
     1. **Detecção de Incidentes**
        - Métricas críticas (5xx, latência, rate limit)
        - Queries Prometheus para alertas
        - Como filtrar logs
     2. **Triagem Inicial**
        - Health checks de DB, Redis, serviços externos
        - Como usar request_id/trace_id
     3. **Procedimentos de Rollback**
        - Como reverter para release anterior
        - Validação pós-rollback
     4. **Investigação com Audit Logs**
        - Padrões de busca
        - Filtros úteis
     5. **Checklist Pós-Incidente**
        - RCA (Root Cause Analysis)
        - Documentação de incidente
     6. **Troubleshooting Comum**
        - Redis indisponível
        - DB lento
        - Falha em backup/restore

5. **Testes Completos**
   - Testes MFA (40+ testes):
     - Enrollment, verification, backup codes
   - Testes DR (30+ testes):
     - Backup, restore, manifest validation
   - Testes de trace_id

6. **Security Scans Finais**
   - Executar SAST (Bandit, etc.)
   - Executar dependency scan (Safety, pip-audit, etc.)
   - Documentar vulnerabilidades encontradas
   - Mitigar vulnerabilidades críticas
   - Criar SECURITY_SUMMARY.md

[FORMATO DE SAÍDA]

1. **Código Implementado**: MFA service, DR scripts, trace middleware
2. **Runbook Operacional**: OPERATIONS_RUNBOOK.md (500+ linhas)
3. **Scripts DR**: backup.py, restore.py, README
4. **Security Summary**: SECURITY_SUMMARY.md
5. **Documentação**:
   - Guia de MFA para usuários
   - Guia de DR para ops
   - README atualizado
6. **Relatório de Sprint**: Incluindo production-readiness %

[RESTRIÇÕES]

- MFA deve ser retrocompatível
- Backup/restore não devem corromper dados
- Runbook deve ser prático, não teórico
- Security scans devem ser documentados
- 0 vulnerabilidades críticas não mitigadas

[MÉTRICAS DE SUCESSO]

- MFA funcional e testado
- RPO < 24h, RTO < 30 min (com backups diários)
- Trace_id em todos os logs
- Runbook completo (500+ linhas)
- 0 vulnerabilidades críticas
- Production-readiness >= 98%
```

---

## 🎯 Dicas de Uso dos Prompts

### Antes de Executar

1. **Conheça seu Repositório**
   - Tamanho, stack, frameworks
   - Estado atual de testes e docs
   - Limitações de infraestrutura

2. **Adapte os Placeholders**
   - [REPO_URL]: URL do seu repositório
   - [STACK]: Python/FastAPI, Node.js/Express, etc.
   - [PERCENTUAL]: Cobertura atual, production-readiness
   - [QUANTIDADE]: Número de módulos, testes, etc.

3. **Ajuste Metas**
   - Se repositório pequeno: reduzir número de testes/serviços
   - Se repositório grande: aumentar escopo

### Durante a Execução

1. **Valide Incrementalmente**
   - Não aceite todas as mudanças de uma vez
   - Revise código gerado
   - Execute testes frequentemente

2. **Itere se Necessário**
   - Se resultados não satisfatórios, refine o prompt
   - Adicione mais contexto ou restrições
   - Peça exemplos específicos

3. **Documente Aprendizados**
   - Anote o que funcionou
   - Anote ajustes feitos ao prompt
   - Crie relatório de sprint

### Depois da Execução

1. **Valide Completamente**
   - Execute todos os testes
   - Verifique builds
   - Revise documentação gerada

2. **Atualize Métricas**
   - Cobertura de testes
   - Production-readiness %
   - Número de vulnerabilidades

3. **Compartilhe Resultados**
   - Relatório de sprint
   - Aprendizados
   - Próximos passos

---

## 📊 Checklist de Execução de Sprint

Para cada sprint, use este checklist:

```markdown
## Sprint X - [Título]

### Pré-Execução
- [ ] Prompt adaptado com placeholders preenchidos
- [ ] Repositório em estado limpo (commits salvos)
- [ ] Ambiente de desenvolvimento configurado
- [ ] Ferramentas necessárias instaladas

### Execução
- [ ] Prompt enviado à IA
- [ ] Código gerado revisado
- [ ] Mudanças aplicadas incrementalmente
- [ ] Testes executados continuamente
- [ ] Documentação gerada revisada

### Validação
- [ ] Todos os testes passando (unit + integration + E2E)
- [ ] Build funcionando
- [ ] Coverage >= threshold
- [ ] Linting passando
- [ ] CI/CD passando (se aplicável)
- [ ] Documentação atualizada

### Pós-Execução
- [ ] Relatório de sprint criado
- [ ] Métricas atualizadas
- [ ] Commits organizados
- [ ] PR criado (se aplicável)
- [ ] Próxima sprint planejada
```

---

## 🔄 Adaptando para Outras Linguagens/Stacks

### Python → JavaScript/TypeScript

- pytest → jest / vitest
- structlog → winston / pino
- pyotp → speakeasy / otplib
- Bandit → ESLint security plugins
- Safety → npm audit / Snyk

### Python → Java/Spring

- pytest → JUnit / TestNG
- structlog → Logback / Log4j2
- pyotp → GoogleAuth / TOTP libraries
- Bandit → SpotBugs / SonarQube
- Safety → OWASP Dependency Check

### Python → Go

- pytest → testing package / testify
- structlog → zap / logrus
- pyotp → go-otp / pquerna/otp
- Bandit → gosec
- Safety → govulncheck

---

## 💡 Conclusão

Estes prompts são templates genéricos baseados na experiência do 3dPot. A chave do sucesso é:

1. **Adaptar ao Contexto**: Preencher placeholders com informações reais
2. **Validar Continuamente**: Não confiar cegamente, sempre testar
3. **Iterar**: Refinar prompts baseado em resultados
4. **Documentar**: Criar relatórios de sprint para referência futura

**Próximo Passo:** Leia o ENG-PLAYBOOK-IA.md para boas práticas de uso de IA em engenharia.

---

**Versão:** 1.0  
**Última Atualização:** Novembro 2025  
**Baseado em:** 3dPot Sprints 1-9
