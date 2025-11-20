# Framework de Sprints com IA - Extraído do Projeto 3dPot

**Versão:** 1.0  
**Data:** Novembro 2025  
**Baseado em:** Sprints 1-9 do projeto 3dPot

---

## 📋 Visão Geral

Este documento apresenta um framework reutilizável de sprints orientadas por IA, extraído da experiência bem-sucedida das Sprints 1-9 do projeto 3dPot, que evoluiu um repositório complexo de 40% para 98% de production-readiness.

### Princípios Fundamentais

1. **Evolução Incremental**: Cada sprint adiciona uma camada específica de qualidade
2. **IA como Acelerador**: IA diagnostica, planeja, implementa e valida
3. **Validação Contínua**: Testes e scans em cada sprint
4. **Documentação Viva**: Cada sprint documenta seu impacto e aprendizados
5. **Zero Regressões**: Mudanças são sempre aditivas e retrocompatíveis

---

## 📊 Estrutura das Sprints 1-9 do 3dPot

### Resumo Executivo

| Sprint | Foco | Principais Entregas | Métricas | Status |
|--------|------|---------------------|----------|--------|
| **Sprint 1** | Reorganização e Estrutura | 145 arquivos reorganizados, estrutura clara de diretórios | Navegabilidade +80% | ✅ |
| **Sprint 2** | Qualidade e Testes Básicos | 191 testes unitários, 6 serviços críticos cobertos | Cobertura: 40% → 72% | ✅ |
| **Sprint 3** | Integração, CLI e E2E | CLI unificada (13 comandos), 9 testes E2E, testes de integração consolidados | 50% redução redundância | ✅ |
| **Sprint 4** | Cobertura Ampliada e CI | 200+ novos testes, 11 testes E2E, 34 testes CLI, CI/CD aprimorado | Cobertura: 72% → 80% | ✅ |
| **Sprint 5** | Qualidade Final | 177 novos testes, 100% serviços cobertos, framework de performance | Cobertura: 80% → 85% | ✅ |
| **Sprint 6** | Observabilidade | Logging estruturado, métricas Prometheus, request tracing | Observabilidade: 0% → 85% | ✅ |
| **Sprint 7** | Segurança Base | Rate limiting, audit logging, RBAC, gestão de secrets | Segurança: 60% → 85% | ✅ |
| **Sprint 8** | Hardening e Escala | Rate limiting distribuído (Redis), RBAC granular, CI/CD security gates | Production-ready: 90% → 95% | ✅ |
| **Sprint 9** | Operações, DR e MFA | MFA/2FA, Disaster Recovery, distributed tracing, operations runbook | Production-ready: 95% → 98% | ✅ |

### Evolução de Métricas

```
Início (Pré-Sprint 1):
├─ Testes: ~93 unitários
├─ Cobertura: ~40%
├─ Documentação: Desorganizada (arquivos na raiz)
├─ Observabilidade: Básica
├─ Segurança: Autenticação JWT básica
└─ Production-Ready: ~40%

Fim (Pós-Sprint 9):
├─ Testes: 748 testes (669 unit, 49 CLI, 30 E2E)
├─ Cobertura: ~85%
├─ Documentação: Estruturada (docs/, 655 linhas de runbook)
├─ Observabilidade: Logs estruturados + Métricas + Tracing
├─ Segurança: Rate limiting + Audit + RBAC + MFA/2FA
└─ Production-Ready: 98%
```

---

## 🎯 Framework Genérico de Sprints com IA

### Sprint 1: Reorganização e Legibilidade

**Objetivo:** Estabelecer estrutura clara e navegável do repositório

**Pré-requisitos:**
- Repositório existente com código funcional
- Acesso de escrita ao repositório
- Identificação de arquivos desorganizados

**Tarefas Principais:**
1. Auditar estrutura atual de diretórios
2. Identificar categorias naturais (docs, tests, scripts, src)
3. Propor nova estrutura hierárquica
4. Mover arquivos para locais apropriados
5. Atualizar imports e referências
6. Criar/atualizar README com nova estrutura
7. Adicionar guias de migração se necessário

**Entregáveis Mínimos:**
- [ ] Estrutura de diretórios clara e documentada
- [ ] Arquivos organizados por categoria
- [ ] README.md atualizado com nova estrutura
- [ ] STRUCTURE.md ou equivalente
- [ ] MIGRATION_GUIDE.md (se aplicável)
- [ ] .gitignore atualizado

**Métricas de Sucesso:**
- Redução de arquivos na raiz (>70%)
- Navegabilidade melhorada (feedback qualitativo)
- Zero quebras de funcionalidade

**Checklist de Validação:**
- [ ] Build/testes continuam funcionando
- [ ] Imports corrigidos
- [ ] Documentação reflete nova estrutura
- [ ] CI/CD ajustado (se necessário)

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Analisou 145 arquivos desorganizados
- Planejamento: Propôs categorias (sprints, relatorios, validacao, arquitetura)
- Implementação: Moveu arquivos e atualizou referências
- Documentação: Gerou REORGANIZATION_SUMMARY.md

---

### Sprint 2: Testes Básicos de Unidade/Integridade

**Objetivo:** Estabelecer base sólida de testes para componentes críticos

**Pré-requisitos:**
- Estrutura de diretórios organizada
- Framework de testes configurado (pytest, jest, etc.)
- Identificação de módulos críticos

**Tarefas Principais:**
1. Mapear serviços/módulos críticos sem testes
2. Priorizar por criticidade de negócio
3. Criar testes unitários para top 5-7 módulos
4. Configurar coverage reporting
5. Documentar padrões de teste
6. Estabelecer threshold mínimo (70%)

**Entregáveis Mínimos:**
- [ ] 150+ testes unitários novos
- [ ] Cobertura de 5+ módulos críticos
- [ ] Coverage report configurado
- [ ] Documentação de padrões de teste
- [ ] Threshold de cobertura no CI

**Métricas de Sucesso:**
- Cobertura de código: +30-40 pontos percentuais
- Tempo de execução: < 1 minuto
- Zero falsos positivos

**Checklist de Validação:**
- [ ] Testes passam localmente e no CI
- [ ] Coverage >= threshold (70%)
- [ ] Mocks apropriados para dependências externas
- [ ] Testes bem nomeados e organizados
- [ ] Documentação de edge cases

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Identificou 11 serviços sem testes
- Planejamento: Priorizou por criticidade (budgeting, modeling, simulation)
- Implementação: Gerou 191 testes unitários
- Validação: Coverage subiu de 40% para 72%

---

### Sprint 3: Integração + CLI

**Objetivo:** Consolidar testes de integração e criar ferramentas de linha de comando

**Pré-requisitos:**
- Testes unitários básicos implementados
- Módulos principais bem testados
- Identificação de fluxos integrados

**Tarefas Principais:**
1. Auditar testes de integração existentes
2. Consolidar testes duplicados
3. Criar CLI unificada para demos/ferramentas
4. Implementar testes E2E para fluxos críticos (2-5)
5. Documentar comandos CLI
6. Adicionar testes para CLI

**Entregáveis Mínimos:**
- [ ] Testes de integração consolidados
- [ ] CLI unificada com 8-10 comandos
- [ ] 5-10 testes E2E básicos
- [ ] Documentação de CLI
- [ ] Testes da CLI

**Métricas de Sucesso:**
- Redução de duplicação em testes: >50%
- CLI funcional com ajuda integrada
- E2E cobrindo fluxos críticos de usuário

**Checklist de Validação:**
- [ ] Testes de integração organizados
- [ ] CLI executável e documentada
- [ ] E2E testam fluxos completos
- [ ] Sem duplicação de cenários
- [ ] Documentação de uso da CLI

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Identificou 8 arquivos de integração duplicados
- Planejamento: Consolidou em 1 arquivo principal + 4 específicos
- Implementação: CLI com 13 comandos, 9 testes E2E
- Documentação: Guias de uso e exemplos

---

### Sprint 4: Cobertura Ampliada + CI Básico

**Objetivo:** Expandir cobertura de testes e automatizar verificações

**Pré-requisitos:**
- Testes básicos e integração implementados
- Pipeline CI/CD existente ou criável
- Módulos secundários identificados

**Tarefas Principais:**
1. Cobrir módulos secundários com testes
2. Expandir testes E2E (mais 5-10 fluxos)
3. Adicionar testes para CLI
4. Configurar CI/CD com:
   - Execução de testes unitários
   - Execução de testes E2E
   - Coverage reporting
   - Linting básico
5. Estabelecer políticas de merge (CI deve passar)

**Entregáveis Mínimos:**
- [ ] 80-120 novos testes unitários
- [ ] 3-5 novos fluxos E2E
- [ ] 20-30 testes CLI
- [ ] CI/CD com jobs separados
- [ ] Coverage threshold enforced

**Métricas de Sucesso:**
- Cobertura: +5-10 pontos percentuais
- CI executando em < 5 minutos
- Testes E2E cobrindo 80% dos fluxos de usuário

**Checklist de Validação:**
- [ ] CI/CD configurado e funcionando
- [ ] Todos os jobs passando
- [ ] Coverage reportado corretamente
- [ ] Política de merge configurada
- [ ] Documentação do pipeline

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Identificou 8 serviços secundários sem testes
- Planejamento: Priorizou Minimax, Conversational, Slant3D
- Implementação: 200+ testes, 11 E2E, 34 CLI, CI aprimorado
- Validação: Coverage de 72% para 80%

---

### Sprint 5: Qualidade Final de Código

**Objetivo:** Atingir 100% de cobertura de serviços e estabelecer métricas de qualidade

**Pré-requisitos:**
- Cobertura de módulos principais e secundários
- CI/CD funcional
- Ferramentas de qualidade identificadas

**Tarefas Principais:**
1. Cobrir TODOS os serviços restantes
2. Implementar testes de performance/carga (básicos)
3. Refinar CLI com utilitários centralizados
4. Expandir E2E para cenários avançados
5. Documentar estado de qualidade
6. Estabelecer roadmap para Release Candidate

**Entregáveis Mínimos:**
- [ ] 100% dos serviços com testes
- [ ] Framework de performance básico
- [ ] 3-5 novos fluxos E2E avançados
- [ ] Utilitários CLI centralizados
- [ ] Relatório de qualidade

**Métricas de Sucesso:**
- Cobertura: 85%+
- 0 serviços sem testes
- Benchmarks de performance documentados

**Checklist de Validação:**
- [ ] Todos os serviços testados
- [ ] Performance baseline estabelecida
- [ ] E2E cobrindo edge cases
- [ ] Documentação completa de qualidade
- [ ] Roadmap para produção definido

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: 7 serviços secundários restantes sem testes
- Planejamento: CloudRendering, Collaboration, Marketplace, etc.
- Implementação: 177 testes, framework de performance
- Validação: 100% serviços cobertos, cobertura 85%

---

### Sprint 6: Observabilidade

**Objetivo:** Implementar logging estruturado, métricas e tracing básico

**Pré-requisitos:**
- Base de testes sólida (85%+ cobertura)
- Identificação de pontos de instrumentação
- Decisão sobre ferramentas (Prometheus, ELK, etc.)

**Tarefas Principais:**
1. Implementar logging estruturado (JSON + console)
2. Adicionar métricas Prometheus (HTTP, serviços, erros)
3. Implementar request IDs para rastreamento
4. Criar middleware de logging automático
5. Configurar formatadores por ambiente (dev/prod)
6. Documentar padrões de observabilidade

**Entregáveis Mínimos:**
- [ ] Logging estruturado implementado
- [ ] Métricas Prometheus básicas
- [ ] Request ID em todos os logs
- [ ] Middleware de logging automático
- [ ] Endpoint /metrics
- [ ] Documentação de observabilidade

**Métricas de Sucesso:**
- Logs estruturados em JSON para prod
- Métricas HTTP disponíveis
- Correlation via request_id funcionando

**Checklist de Validação:**
- [ ] Logs em formato correto (JSON/console)
- [ ] Métricas acessíveis via /metrics
- [ ] Request IDs únicos e propagados
- [ ] Documentação de campos de log
- [ ] Exemplos de queries/dashboards

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Observabilidade básica existente
- Planejamento: Structlog + Prometheus + middleware
- Implementação: Logging config, metrics, request_id middleware
- Validação: Testes de observabilidade, documentação

---

### Sprint 7: Segurança Base

**Objetivo:** Implementar controles de segurança essenciais

**Pré-requisitos:**
- Observabilidade implementada
- Autenticação básica existente
- Identificação de vetores de ataque

**Tarefas Principais:**
1. Implementar rate limiting (token bucket)
2. Adicionar audit logging para ações críticas
3. Fortalecer gestão de secrets (.env, variáveis)
4. Implementar/melhorar RBAC
5. Configurar limites por endpoint
6. Criar testes de segurança

**Entregáveis Mínimos:**
- [ ] Rate limiting implementado
- [ ] Audit logging para ações críticas
- [ ] Gestão segura de secrets
- [ ] RBAC funcional
- [ ] Testes de segurança (40+)
- [ ] Documentação de segurança

**Métricas de Sucesso:**
- Rate limiting funcionando (429 em abuse)
- Audit trail completo
- 0 secrets em código

**Checklist de Validação:**
- [ ] Rate limiting testado
- [ ] Audit logs capturando ações
- [ ] Secrets via environment variables
- [ ] RBAC bloqueando acessos não autorizados
- [ ] Testes de segurança passando
- [ ] Documentação de políticas

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Autenticação JWT básica existente
- Planejamento: Rate limiting + audit + RBAC
- Implementação: Token bucket, audit service, security config
- Validação: 57+ testes de segurança

---

### Sprint 8: Hardening e Escala

**Objetivo:** Preparar para escala horizontal e hardening de segurança

**Pré-requisitos:**
- Segurança base implementada
- Observabilidade funcional
- Infraestrutura de cache disponível (Redis)

**Tarefas Principais:**
1. Implementar rate limiting distribuído (Redis)
2. Adicionar RBAC granular com ownership
3. Criar CI/CD security gates (Bandit, Safety, etc.)
4. Adicionar métricas de segurança
5. Documentar runbook operacional (inicial)
6. Testes de escala básicos

**Entregáveis Mínimos:**
- [ ] Rate limiting distribuído
- [ ] RBAC granular
- [ ] Security gates no CI/CD
- [ ] Métricas de segurança
- [ ] Runbook operacional inicial
- [ ] Testes de hardening

**Métricas de Sucesso:**
- Rate limiting compartilhado entre instâncias
- 0 vulnerabilidades críticas não mitigadas
- CI falhando em detecção de vulnerabilidades

**Checklist de Validação:**
- [ ] Rate limiting com Redis funcional
- [ ] RBAC validando ownership
- [ ] Security scans no CI
- [ ] Métricas de segurança em /metrics
- [ ] Runbook documentado
- [ ] Testes de failover (rate limiting)

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Rate limiting in-memory não escalável
- Planejamento: Redis backend + RBAC granular + security gates
- Implementação: RedisRateLimiter, Authorization, CI security jobs
- Validação: Production-ready de 90% para 95%

---

### Sprint 9: Operações, DR e MFA

**Objetivo:** Completar preparação para produção com MFA e disaster recovery

**Pré-requisitos:**
- Sistema em 95% production-ready
- Observabilidade e segurança implementadas
- Identificação de dados críticos

**Tarefas Principais:**
1. Implementar MFA/2FA (TOTP)
2. Criar scripts de backup automatizados
3. Criar scripts de restore com validação
4. Implementar distributed tracing (trace_id)
5. Criar operations runbook completo (500+ linhas)
6. Executar security scans finais
7. Documentar procedimentos de DR

**Entregáveis Mínimos:**
- [ ] MFA/2FA implementado
- [ ] Scripts de backup/restore
- [ ] Distributed tracing (trace_id)
- [ ] Operations runbook (500+ linhas)
- [ ] Security scans executados
- [ ] Documentação de DR
- [ ] Testes de MFA e DR

**Métricas de Sucesso:**
- MFA funcional e retrocompatível
- RPO < 24h, RTO < 30 min
- Trace_id em todos os logs
- 0 vulnerabilidades críticas

**Checklist de Validação:**
- [ ] MFA enrollment e login funcionando
- [ ] Backup/restore testados
- [ ] Trace_id propagado
- [ ] Runbook completo e validado
- [ ] Security scans documentados
- [ ] DR drill planejado

**Como a IA Foi Usada (3dPot):**
- Diagnóstico: Faltando MFA, DR e runbook operacional
- Planejamento: TOTP + backup scripts + trace_id + runbook
- Implementação: MFA service, DR scripts, trace middleware, 655 linhas de runbook
- Validação: 70+ testes, security scans, production-ready 98%

---

## 🔄 Sequência Recomendada

```
Sprint 1 (Estrutura)
    ↓
Sprint 2 (Testes Básicos)
    ↓
Sprint 3 (Integração + CLI)
    ↓
Sprint 4 (Cobertura + CI)
    ↓
Sprint 5 (Qualidade Final)
    ↓
Sprint 6 (Observabilidade)
    ↓
Sprint 7 (Segurança Base)
    ↓
Sprint 8 (Hardening)
    ↓
Sprint 9 (Ops + DR + MFA)
    ↓
Production-Ready (98%+)
```

### Dependências Entre Sprints

- **Sprint 2-5**: Focam em qualidade de código (podem ser iteradas)
- **Sprint 6**: Base para Sprint 7 (audit logging usa logging estruturado)
- **Sprint 7**: Base para Sprint 8 (hardening estende segurança)
- **Sprint 8-9**: Finalizam production-readiness

### Flexibilidade

- Sprints 2-5 podem ter mais iterações dependendo do tamanho do código
- Sprints 6-9 podem ser comprimidas se já houver observabilidade/segurança básica
- MFA (Sprint 9) pode ser antecipado se for crítico para negócio

---

## 📈 Evolução Típica de Métricas

| Métrica | Início | Sprint 2 | Sprint 5 | Sprint 9 | Ganho |
|---------|--------|----------|----------|----------|-------|
| **Cobertura de Testes** | 30-50% | 70-75% | 85%+ | 85%+ | +35-55% |
| **Testes Totais** | 50-150 | 250-400 | 600+ | 700+ | +550+ |
| **Observabilidade** | Básica | Básica | Básica | Avançada | Logs + Metrics + Trace |
| **Segurança** | JWT | JWT | JWT | JWT + Rate + Audit + RBAC + MFA | 5+ camadas |
| **Documentação** | Mínima | Média | Boa | Excelente | Runbook + Guides |
| **Production-Ready** | 40-50% | 70% | 85% | 98% | +48-58% |

---

## 🎓 Lições Aprendidas do 3dPot

### O Que Funcionou Bem

1. **Abordagem Incremental**: Cada sprint adicionou valor sem quebrar existente
2. **Testes Primeiro**: Base de testes permitiu refatorações confiáveis
3. **Documentação Contínua**: Relatórios de sprint facilitaram revisões
4. **Validação Constante**: CI/CD em cada sprint evitou regressões
5. **IA como Parceira**: IA diagnosticou, implementou e validou eficientemente

### Desafios Encontrados

1. **Duplicação de Testes**: Sprint 3 teve que consolidar testes duplicados
2. **Scope Creep**: Sprints 2-5 cresceram além do planejado (positivo)
3. **Dependências Externas**: Testes de integração requerem mocks cuidadosos
4. **Configuração de Ambiente**: .env e secrets requerem atenção

### Recomendações

1. **Comece com Sprint 1**: Estrutura clara é base para tudo
2. **Não Pule Testes**: Sprint 2-5 são fundamentais para confiança
3. **Observabilidade Antes de Segurança**: Sprint 6 antes de 7 facilita audit logging
4. **Valide Continuamente**: Rode testes e scans em cada sprint
5. **Documente Sempre**: Relatórios de sprint são valiosos para retrospectivas

---

## 📝 Template de Relatório de Sprint

Para cada sprint executada, documente:

```markdown
# Sprint X - [Título da Sprint] - RELATÓRIO

**Data:** [Data]
**Versão:** [Versão]
**Status:** ✅ CONCLUÍDO / 🔄 EM PROGRESSO

---

## 📋 Sumário Executivo

[Parágrafo resumindo a sprint]

### Principais Conquistas

- ✅ [Conquista 1]
- ✅ [Conquista 2]
- ✅ [Conquista 3]

---

## 🎯 Objetivos da Sprint

### Objetivos Primários ✅

| Objetivo | Meta | Alcançado | Status |
|----------|------|-----------|--------|
| [Nome] | [Meta] | [Valor] | ✅/⚠️/❌ |

---

## 📊 Mudanças Implementadas

### [Área 1]
[Descrição detalhada]

### [Área 2]
[Descrição detalhada]

---

## 🧪 Testes Implementados

[Descrição dos testes]

---

## 📈 Métricas de Qualidade

[Antes/Depois, cobertura, etc.]

---

## 🚀 Impacto no Sistema

[Como a sprint melhorou o sistema]

---

## 🔄 Próximos Passos

- [ ] [Item 1]
- [ ] [Item 2]

---

**Aprovado para merge em:** `main`
**Próxima sprint:** Sprint X+1
```

---

## 🎯 Checklist Final de Production-Readiness

Baseado no estado do 3dPot pós-Sprint 9 (98%):

### Código e Testes ✅
- [ ] Cobertura de testes >= 85%
- [ ] Testes unitários para todos os serviços
- [ ] Testes de integração consolidados
- [ ] Testes E2E para fluxos críticos
- [ ] Testes de performance básicos

### Observabilidade ✅
- [ ] Logging estruturado (JSON + console)
- [ ] Métricas Prometheus (/metrics)
- [ ] Request IDs para correlação
- [ ] Trace IDs para distributed tracing
- [ ] Health checks (/health)

### Segurança ✅
- [ ] Autenticação robusta (JWT + refresh)
- [ ] Rate limiting (distribuído se multi-instância)
- [ ] Audit logging para ações críticas
- [ ] RBAC com controle de ownership
- [ ] MFA/2FA opcional ou obrigatório
- [ ] Gestão segura de secrets (.env)
- [ ] Security scans no CI/CD (Bandit, Safety, pip-audit)
- [ ] 0 vulnerabilidades críticas não mitigadas

### Operações ✅
- [ ] Operations runbook (500+ linhas)
- [ ] Scripts de backup automatizados
- [ ] Scripts de restore validados
- [ ] Disaster recovery testado
- [ ] Procedimentos de rollback documentados
- [ ] Troubleshooting guides

### CI/CD ✅
- [ ] Pipeline automatizado
- [ ] Testes unitários no CI
- [ ] Testes E2E no CI
- [ ] Coverage reporting
- [ ] Security gates (Bandit, Safety, etc.)
- [ ] Política de merge (CI must pass)

### Documentação ✅
- [ ] README completo e atualizado
- [ ] Estrutura documentada (STRUCTURE.md)
- [ ] Guias de instalação
- [ ] Documentação de API (Swagger/OpenAPI)
- [ ] Runbook operacional
- [ ] Relatórios de sprint
- [ ] Security summary

### Infraestrutura 🔄
- [ ] Containerização (Docker)
- [ ] Orquestração (K8s, Docker Compose)
- [ ] Configuração por ambiente (.env)
- [ ] Monitoramento (Prometheus + Grafana)
- [ ] Alerting configurado
- [ ] Backups agendados (cron/systemd)

### Compliance 🔄 (Opcional)
- [ ] LGPD/GDPR compliance
- [ ] SOC 2 / ISO 27001
- [ ] Penetration testing externo
- [ ] Audit logs retention policy
- [ ] Data encryption at rest/transit

**Legend:**
- ✅ Implementado no 3dPot (Sprint 9)
- 🔄 Parcial ou próximos passos

---

## 💡 Conclusão

Este framework demonstrou eficácia comprovada ao evoluir o 3dPot de 40% para 98% production-readiness em 9 sprints. A chave do sucesso foi:

1. **Incrementalismo**: Cada sprint adiciona valor mensurável
2. **IA como Acelerador**: Diagnóstico, implementação e validação assistidos
3. **Validação Contínua**: Testes e scans em cada sprint
4. **Documentação Viva**: Aprendizados capturados e reutilizáveis

**Próximos Passos Recomendados:**
- Adaptar prompts genéricos para seu contexto (ver AI-SPRINT-PROMPTS.md)
- Seguir o playbook de engenharia (ver ENG-PLAYBOOK-IA.md)
- Executar sprints sequencialmente
- Documentar e ajustar conforme necessário

---

**Versão do Framework:** 1.0  
**Última Atualização:** Novembro 2025  
**Baseado em:** 3dPot Sprints 1-9  
**Status:** Production-Ready Framework
