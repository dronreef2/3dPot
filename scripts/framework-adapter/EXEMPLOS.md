# Exemplos de Uso do Framework Adapter

Este documento apresenta exemplos práticos de como usar o Framework Adapter em diferentes cenários.

---

## 📚 Índice

1. [Cenário 1: Projeto Node.js Inicial (Sem Testes)](#cenário-1-projeto-nodejs-inicial-sem-testes)
2. [Cenário 2: API Python com Testes Parciais](#cenário-2-api-python-com-testes-parciais)
3. [Cenário 3: Microserviço Java Maduro](#cenário-3-microserviço-java-maduro)
4. [Cenário 4: Aplicação Go em Produção](#cenário-4-aplicação-go-em-produção)
5. [Cenário 5: Projeto Legado PHP](#cenário-5-projeto-legado-php)

---

## Cenário 1: Projeto Node.js Inicial (Sem Testes)

### Contexto
Você tem uma API REST em Node.js/Express que foi desenvolvida rapidamente para MVP. 
O código funciona mas não tem testes, observabilidade ou segurança além de autenticação básica.

### Comando

```bash
python framework_adapter.py \
  --repo-url "https://github.com/startup/product-api" \
  --stack "Node.js/Express + MongoDB" \
  --objectives "API REST para catálogo de produtos com busca, filtros e recomendações" \
  --test-coverage "sem testes" \
  --observability "nenhuma - apenas console.log()" \
  --security "JWT básico" \
  --documentation "mínima - apenas README básico" \
  --output ./product-api-framework
```

### Análise Esperada

**Estágio Estimado:** Sprint 1-2

**Roadmap Sugerido (6 sprints):**
1. **Sprint 1: Reorganização e Estrutura** [HIGH]
2. **Sprint 2: Testes Básicos** [HIGH] - Configurar Jest, criar primeiros testes
3. **Sprint 3: Integração + CLI** [MEDIUM] - Testes de integração, criar CLI de dev
4. **Sprint 4: Cobertura + CI** [MEDIUM] - Expandir testes, configurar GitHub Actions
5. **Sprint 5: Qualidade Final** [MEDIUM] - 100% serviços testados
6. **Sprint 6: Observabilidade** [HIGH] - Winston + Prometheus

### Prompts Adaptados Gerados

1. Prompt para reorganização (Sprint 1)
2. Prompt para testes com Jest (Sprint 2)
3. Prompt para observabilidade com Winston (Sprint 6)

### Próximos Passos Recomendados

1. ✅ Executar Sprint 1 primeiro (estrutura)
2. ✅ Seguir com Sprint 2 (testes é crítico)
3. ✅ Pular para Sprint 6 se observabilidade for urgente
4. ⚠️ NÃO pular testes - é a base para tudo

---

## Cenário 2: API Python com Testes Parciais

### Contexto
API em Python/FastAPI com alguns testes (cobertura ~50%), mas sem observabilidade 
adequada e segurança básica. Precisa preparar para produção.

### Comando

```bash
python framework_adapter.py \
  --repo-url "https://github.com/empresa/analytics-api" \
  --stack "Python/FastAPI + PostgreSQL + Redis" \
  --objectives "API de analytics com agregações complexas e cache distribuído" \
  --test-coverage "~50% - módulos principais testados" \
  --observability "logs básicos com logging module" \
  --security "JWT + refresh tokens" \
  --documentation "moderada - README + alguns guias" \
  --output ./analytics-api-framework
```

### Análise Esperada

**Estágio Estimado:** Sprint 2-3

**Roadmap Sugerido (6 sprints):**
1. **Sprint 1: Completar Testes** [HIGH] - Chegar a 70%+
2. **Sprint 2: Integração + CLI** [MEDIUM] - Consolidar testes
3. **Sprint 3: Qualidade Final** [MEDIUM] - 85%+ cobertura
4. **Sprint 4: Observabilidade** [HIGH] - Structlog + Prometheus
5. **Sprint 5: Segurança Base** [HIGH] - Rate limiting + audit logging
6. **Sprint 6: Hardening** [MEDIUM] - Rate limiting distribuído (Redis)

### Prompts Adaptados Gerados

1. Prompt para completar testes (foco em pytest)
2. Prompt para observabilidade (structlog + Prometheus)
3. Prompt para segurança (rate limiting + audit)

### Próximos Passos Recomendados

1. ✅ Completar Sprint 1 (chegar a 70% cobertura)
2. ✅ Pular para Sprint 4 (observabilidade é crítica para prod)
3. ✅ Executar Sprint 5 (segurança antes de produção)
4. 📊 Considerar Sprint 6 se multi-instância

---

## Cenário 3: Microserviço Java Maduro

### Contexto
Microserviço em Spring Boot com boa base de testes (80%), observabilidade com 
Micrometer, mas precisa de hardening de segurança e procedures de DR.

### Comando

```bash
python framework_adapter.py \
  --repo-url "https://github.com/corp/inventory-service" \
  --stack "Java/Spring Boot + MySQL + Kafka" \
  --objectives "Microserviço de gestão de inventário com eventos assíncronos" \
  --test-coverage "~80% - testes robustos com JUnit e Mockito" \
  --observability "logs estruturados (Logback) + métricas (Micrometer) + tracing (Jaeger)" \
  --security "OAuth2 + RBAC básico" \
  --documentation "extensa - OpenAPI + guias de deploy" \
  --output ./inventory-service-framework
```

### Análise Esperada

**Estágio Estimado:** Sprint 5-6

**Roadmap Sugerido (4 sprints):**
1. **Sprint 1: Qualidade Final** [MEDIUM] - Chegar a 85%+
2. **Sprint 2: Segurança Avançada** [HIGH] - RBAC granular + audit logging
3. **Sprint 3: Hardening** [HIGH] - Security gates no CI/CD
4. **Sprint 4: Operações + DR** [HIGH] - Backup/restore + runbook

### Prompts Adaptados Gerados

1. Prompt para testes finais (JUnit 5 + AssertJ)
2. Prompt para segurança avançada (Spring Security + audit)
3. Prompt para DR (scripts de backup/restore)

### Próximos Passos Recomendados

1. ✅ Sprint 2 é prioritária (segurança avançada)
2. ✅ Seguir com Sprint 3 (hardening)
3. ✅ Finalizar com Sprint 4 (DR para production-ready)
4. 📊 Sprint 1 pode ser opcional se 80% for suficiente

---

## Cenário 4: Aplicação Go em Produção

### Contexto
Serviço em Go já em produção, mas sem observabilidade adequada e procedures 
formalizados de operações. Precisa melhorar para escalar.

### Comando

```bash
python framework_adapter.py \
  --repo-url "https://github.com/tech/notification-service" \
  --stack "Go + PostgreSQL + RabbitMQ" \
  --objectives "Serviço de notificações com múltiplos canais (email, SMS, push)" \
  --test-coverage "~60% - testes básicos com testing package" \
  --observability "logs básicos com log package" \
  --security "API keys + rate limiting básico" \
  --documentation "moderada - README + docs de API" \
  --output ./notification-service-framework
```

### Análise Esperada

**Estágio Estimado:** Sprint 3-5

**Roadmap Sugerido (6 sprints):**
1. **Sprint 1: Completar Testes** [HIGH] - Chegar a 75%+ com testify
2. **Sprint 2: Observabilidade** [HIGH] - Zap/Logrus + Prometheus
3. **Sprint 3: Segurança** [MEDIUM] - Melhorar rate limiting
4. **Sprint 4: Hardening** [HIGH] - Rate limiting distribuído
5. **Sprint 5: Operações** [HIGH] - Runbook completo
6. **Sprint 6: DR** [HIGH] - Backup/restore procedures

### Prompts Adaptados Gerados

1. Prompt para testes (testify + gomock)
2. Prompt para observabilidade (zap + Prometheus)
3. Prompt para operações (runbook + procedures)

### Próximos Passos Recomendados

1. ⚠️ Sprint 2 é URGENTE (observabilidade para produção)
2. ✅ Seguir com Sprint 5 (runbook operacional)
3. ✅ Sprint 1 em paralelo (melhorar cobertura)
4. 📊 Sprints 4 e 6 para estabilização

---

## Cenário 5: Projeto Legado PHP

### Contexto
Sistema legado em PHP que precisa modernização. Sem testes, estrutura 
desorganizada, segurança questionável.

### Comando

```bash
python framework_adapter.py \
  --repo-url "https://github.com/legacy/crm-system" \
  --stack "PHP 7.4 + MySQL" \
  --objectives "Sistema CRM com gestão de clientes, oportunidades e tarefas" \
  --test-coverage "sem testes" \
  --observability "nenhuma - error_log apenas" \
  --security "sessões PHP básicas" \
  --documentation "mínima - código sem comentários" \
  --output ./crm-system-framework
```

### Análise Esperada

**Estágio Estimado:** Sprint 1 (início)

**Roadmap Sugerido (6 sprints):**
1. **Sprint 1: Reorganização** [HIGH] - CRÍTICO para legado
2. **Sprint 2: Testes Básicos** [HIGH] - PHPUnit + primeiros testes
3. **Sprint 3: Integração** [MEDIUM] - Testes de integração
4. **Sprint 4: CI/CD** [HIGH] - Automatizar testes
5. **Sprint 5: Observabilidade** [HIGH] - Monolog + estruturação
6. **Sprint 6: Segurança** [HIGH] - Autenticação moderna

### Prompts Adaptados Gerados

1. Prompt para reorganização (estrutura MVC/PSR)
2. Prompt para testes (PHPUnit + configuração)
3. Prompt para observabilidade (Monolog)

### Próximos Passos Recomendados

1. ⚠️ Sprint 1 é CRÍTICA (reorganizar antes de tudo)
2. ✅ Sprint 2 em seguida (testes são base)
3. ✅ NÃO pular para sprints avançadas sem base
4. 📚 Considerar migração para PHP 8+ em Sprint 1

---

## 🎯 Padrões Observados

### Quando Começar com Sprint 1 (Estrutura)
- ✅ Código desorganizado com arquivos na raiz
- ✅ Estrutura de diretórios confusa
- ✅ Projetos legados sem padrão

### Quando Focar em Testes (Sprints 2-5)
- ✅ Cobertura < 70%
- ✅ Serviços críticos sem testes
- ✅ Preparação para refatorações

### Quando Priorizar Observabilidade (Sprint 6)
- ✅ Sistema já em produção
- ✅ Dificuldade em debugar problemas
- ✅ Preparação para escala

### Quando Focar em Segurança (Sprints 7-9)
- ✅ Sistema vai para produção
- ✅ Dados sensíveis
- ✅ Compliance (LGPD, etc.)

---

## 💡 Dicas de Personalização

### Ajustando o Roadmap

Você pode modificar o roadmap gerado:

1. **Reordenar sprints:** Se observabilidade for mais urgente que testes
2. **Pular sprints:** Se já tiver boa infraestrutura
3. **Adicionar sprints:** Para necessidades específicas
4. **Combinar sprints:** Se projeto for pequeno

### Adaptando Prompts

Os prompts gerados são templates. Você pode:

1. **Adicionar contexto específico:** Bibliotecas usadas, constraints
2. **Remover objetivos:** Se não aplicáveis
3. **Adicionar exemplos:** Do seu código existente
4. **Ajustar métricas:** Cobertura, duração, etc.

### Personalizando para Seu Time

Considere:

1. **Experiência do time:** Juniores podem precisar de mais tempo
2. **Tamanho do projeto:** Projetos grandes precisam mais sprints
3. **Prazos:** Adapte duração das sprints
4. **Infraestrutura:** Redis disponível? CI/CD existe?

---

## 📊 Tabela de Decisão Rápida

| Estado Atual | Sprint Inicial | Foco Principal | Duração Estimada |
|--------------|----------------|----------------|------------------|
| Sem testes, desorganizado | Sprint 1 | Estrutura + Testes | 2-3 semanas |
| Testes parciais (30-60%) | Sprint 2-3 | Completar testes | 1-2 semanas |
| Boa cobertura (70%+) | Sprint 5-6 | Observabilidade | 1 semana |
| Em produção, sem obs | Sprint 6 | Observabilidade | 3-5 dias |
| Tudo OK, precisa DR | Sprint 9 | Operações + DR | 3-4 dias |

---

## 🔗 Recursos Adicionais

- [README.md](./README.md) - Documentação completa da ferramenta
- [AI-SPRINT-FRAMEWORK.md](../../docs/arquitetura/AI-SPRINT-FRAMEWORK.md) - Framework completo
- [AI-SPRINT-PROMPTS.md](../../docs/arquitetura/AI-SPRINT-PROMPTS.md) - Todos os prompts
- [ENG-PLAYBOOK-IA.md](../../docs/arquitetura/ENG-PLAYBOOK-IA.md) - Playbook de engenharia

---

**Última Atualização:** Novembro 2025  
**Versão:** 1.0
