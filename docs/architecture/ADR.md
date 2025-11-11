# ADRs - 3dPot v2.0

**Date:** 11 de novembro de 2025  
**Status:** Accepted  
**Deciders:** Arquiteto Principal, MiniMax Agent

## ADR-001: Arquitetura Monolítica Modular

### Context
O projeto 3dPot v1.0 tinha uma arquitetura distribuída com múltiplos componentes separados (Flask backend, Node.js frontend, hardware legados). A evolução para v2.0 requer uma plataforma de prototipagem sob demanda mais unificada e escalável.

### Decision
Adotar **arquitetura monolítica modular** para MVP, com preparação para evolução futura para microserviços.

### Rationale
- **Simplicidade**: Uma aplicação única é mais fácil de desenvolver, testar e deployar
- **Consistência**: Transações ACID e consistência de dados garantidas
- **Performance**: Comunicação interna mais eficiente (sem network calls)
- **Custo**: Menos infraestrutura e operacionais overhead
- **Escalabilidade Horizontal**: Possibilidade de escalar componentes individualmente no futuro

### Consequences
**Positive:**
- Desenvolvimento mais rápido e simples
- Menor complexidade operacional
- Transações de dados consistentes
- Debugging mais fácil

**Negative:**
- Mais difícil escalar componentes individualmente
- Deploys maiores (todo ou nada)
- Possível coupling entre módulos

### Implementation
- Backend: FastAPI com estrutura modular (api/, services/, models/, schemas/)
- Frontend: React + React Three Fiber
- Database: PostgreSQL para consistência transacional
- Storage: S3/MinIO para objetos

### Future Considerations
- Preparar para split em microserviços quando necessário
- Usar event-driven architecture para reduzir coupling
- Implementar circuit breakers para resiliência

---

## ADR-002: FastAPI como Framework Backend

### Context
O backend v1.0 usava Flask. A evolução v2.0 precisa de melhor performance, documentação automática, validação de dados e suporte assíncrono nativo.

### Decision
Migrar de Flask para **FastAPI** como framework backend principal.

### Rationale
- **Performance**: Async/await nativo, performance comparable ao Node.js e Go
- **Documentação Automática**: OpenAPI/Swagger integrado
- **Validação de Dados**: Pydantic integrado com TypeScript
- **Type Safety**: Type hints obrigatórios
- **Async Support**: Melhor suporte para I/O bound operations
- **Comunidade**: Crescimento rápido e boa adoção

### Consequences
**Positive:**
- API automática documentada
- Validação robusta de dados
- Melhor performance para APIs
- Desenvolvimento mais rápido com type hints
- Futuro-proofing com async/await

**Negative:**
- Curva de aprendizado para equipe Flask
- Migração de código existente
- Dependências diferentes

### Implementation
- Endpoints RESTful versionados (/api/v1/)
- Pydantic schemas para validação
- SQLAlchemy 2.0 async support
- OpenAPI documentation automático

---

## ADR-003: React Three Fiber para Visualização 3D

### Context
A interface v1.0 não tinha visualização 3D interativa. O v2.0 precisa de renderização 3D para modelos gerados, simulações e experiência do usuário imersiva.

### Decision
Usar **React Three Fiber** como biblioteca principal para renderização 3D no frontend.

### Rationale
- **React Integration**: Componentes React para 3D
- **Three.js Power**: Acesso completo ao Three.js ecosystem
- **Performance**: Rendering otimizado com React
- **Developer Experience**: JSX para 3D scenes
- **Community**: Grande comunidade e documentação
- **Flexibilidade**: Suporte para GLTF, STL, OBJ

### Consequences
**Positive:**
- Componentes React reutilizáveis para 3D
- Performance otimizada
- Integração fácil com estado React
- Suporte a múltiplos formatos 3D
- Animações fluidas

**Negative:**
- Tamanho do bundle aumentado
- Curva de aprendizado para desenvolvedores frontend
- Dependência do WebGL

### Implementation
- `@react-three/fiber` para core rendering
- `@react-three/drei` para helpers
- Suporte a GLTF, STL, OBJ
- Controles de câmera (OrbitControls)
- Carregamento assíncrono de modelos

---

## ADR-004: Minimax M2 para Conversação Inteligente

### Context
O sistema v2.0 precisa extrair especificações técnicas automaticamente através de conversação natural com usuários.

### Decision
Integrar **Minimax M2 API** como agente conversacional principal.

### Rationale
- **Português Nativo**: Melhor suporte para conversação em português
- **Multiturn Conversations**: Suporte a conversas contextuais
- **Technical Understanding**: Especializado em extração de especificações
- **API Stability**: API madura e documentada
- **Cost Effective**: Pricing competitivo

### Consequences
**Positive:**
- Conversação natural em português
- Extração automática de especificações
- Contexto mantido entre mensagens
- Fallback para APIs legadas

**Negative:**
- Dependência externa de terceiros
- Custos por requisição
- Rate limits aplicáveis

### Implementation
- Service layer isolado para Minimax API
- Schema de dados estruturado para especificações
- Fallback para conversação simples se API indisponível
- Cache de conversas no banco de dados

---

## ADR-005: PostgreSQL como Banco Principal

### Context
O v1.0 não tinha banco de dados centralizado. O v2.0 precisa de persistência robusta para usuários, projetos, conversas, modelos e orçamentos.

### Decision
Usar **PostgreSQL** como banco de dados principal.

### Rationale
- **ACID Compliance**: Transações robustas para dados críticos
- **JSON Support**: JSON columns para dados flexíveis
- **Performance**: Performance excelente para queries complexas
- **Reliability**: Alta disponibilidade e backup
- **Extensions**: Suporte a extensões para funcionalidades futuras
- **SQL Standards**: Suporte completo a SQL padrão

### Consequences
**Positive:**
- Consistência de dados garantida
- Queries complexas eficientes
- Backup e recovery robustos
- Escalabilidade comprovada

**Negative:**
- Setup mais complexo que SQLite
- Requer manutenção (backups, tuning)
- Recursos de servidor necessários

### Implementation
- SQLAlchemy 2.0 ORM
- Alembic para migrações
- Connection pooling
- Read replicas para escala

---

## ADR-006: S3/MinIO para Storage de Modelos

### Context
Modelos 3D, imagens de simulação, documentos PDF e outros arquivos precisam de storage escalável e confiável.

### Decision
Usar **S3-compatible storage** (MinIO para desenvolvimento, AWS S3 para produção).

### Rationale
- **Scalability**: Escala automaticamente com demanda
- **Cost Effective**: Pay-per-use pricing
- **Reliability**: Alta disponibilidade e durability
- **API Standard**: S3 API é padrão de mercado
- **File Size**: Suporte a arquivos grandes
- **CDN Integration**: Fácil integração com CDN

### Consequences
**Positive:**
- Escalabilidade ilimitada
- Backup automático
- URLs presigned para downloads
- Integração fácil com CDN

**Negative:**
- Latência de rede
- Dependência externa
- Custos por transfer

### Implementation
- MinIO para desenvolvimento local
- AWS S3 para produção
- URLs presigned para downloads
- Versionamento de arquivos

---

## ADR-007: Celery + Redis para Tarefas Assíncronas

### Context
Operações como geração de modelos 3D, simulações físicas e cálculos de orçamento são intensivas e devem ser executadas em background.

### Decision
Usar **Celery** com **Redis** como broker e result backend.

### Rationale
- **Proven Technology**: Celery é padrão para Python async tasks
- **Redis Performance**: Baixa latência para messaging
- **Task Monitoring**: Dashboard de tarefas e retry automático
- **Scalability**: Escala horizontalmente com workers
- **Reliability**: Retry automático e failure handling

### Consequences
**Positive:**
- Jobs em background não bloqueiam API
- Retry automático em falhas
- Monitoramento de progresso
- Escalabilidade horizontal

**Negative:**
- Complexidade operacional
- Redis como single point of failure
- Debugging mais difícil

### Implementation
- Redis como broker e backend
- Task queue para modelagem, simulação, orçamento
- Progress tracking
- Error handling e retry logic

---

## ADR-008: WebSockets para Tempo Real

### Context
Usuários precisam de feedback em tempo real durante conversação, geração de modelos e execuções de simulação.

### Decision
Implementar **WebSockets** para comunicação em tempo real.

### Rationale
- **Real-time**: Atualizações instantâneas
- **Bidirectional**: Cliente e servidor podem enviar dados
- **Efficient**: Menos overhead que polling
- **User Experience**: Feedback imediato melhora UX
- **Progress Tracking**: Status de tarefas em tempo real

### Consequences
**Positive:**
- UX superior com feedback imediato
- Eficiência de rede
- Actualizações automáticas
- Progress bars dinâmicos

**Negative:**
- Mais complexo que polling
- Stateful connections
- Load balancer considerations

### Implementation
- FastAPI WebSocket support
- Socket.io no frontend
- Channels para diferentes tipos de eventos
- Authentication via JWT

---

## ADR-009: Schema Versionado para APIs

### Context
APIs evoluem com o tempo e precisam de compatibilidade com versões anteriores.

### Decision
Implementar **versionamento de schemas** usando FastAPI routers versionados.

### Rationale
- **Backward Compatibility**: Clientes antigos continuam funcionando
- **Evolution**: Novas funcionalidades sem breaking changes
- **Clear Migration Path**: Guias de migração entre versões
- **API Documentation**: Documentação clara por versão
- **Testing**: Testes por versão

### Consequences
**Positive:**
- Backward compatibility garantida
- Migrações suaves
- API stable para clientes
- Deploy de versões novas sem downtime

**Negative:**
- Manutenção de múltiplas versões
- Schema duplicado
- Testing mais complexo

### Implementation
- `/api/v1/` prefix para endpoints
- Schemas separados por versão
- Deprecation notices
- Migration guides

---

## ADR-010: Testes Automatizados com pytest

### Context
Sistema crítico de prototipagem precisa de cobertura de testes robusta para garantir qualidade.

### Decision
Adotar **pytest** como framework de testes principal com coverage target de 80%+.

### Rationale
- **Python Native**: Framework padrão para Python
- **Fixtures**: Sistema robusto de fixtures
- **Markers**: Organização de testes por categoria
- **Coverage**: Integração com coverage tools
- **Plugins**: Ecossistema rico de plugins
- **Async Support**: Suporte nativo a async/await

### Consequences
**Positive:**
- Testes mais expressivos e legíveis
- Coverage automática
- Fixtures reutilizáveis
- Testes paralelos
- Async testing

**Negative:**
- Setup inicial de testes
- Manutenção de coverage
- Tempo de execução

### Implementation
- pytest + pytest-asyncio para async
- pytest-cov para coverage
- Testes unitários, integração e E2E
- GitHub Actions para CI/CD
- Coverage reports automáticos