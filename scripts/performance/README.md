# Performance Testing - 3dPot v2.0

Este diretório contém scripts para testes de performance e carga do sistema 3dPot.

## Scripts Disponíveis

### 1. benchmark_services.py
Mede performance de operações críticas do sistema.

**Uso:**
```bash
# Executar todos os benchmarks
python scripts/performance/benchmark_services.py

# Benchmark de serviço específico
python scripts/performance/benchmark_services.py --service budgeting
python scripts/performance/benchmark_services.py --service simulation
python scripts/performance/benchmark_services.py --service optimization
python scripts/performance/benchmark_services.py --service marketplace

# Customizar número de iterações
python scripts/performance/benchmark_services.py --iterations 100
```

**Serviços testados:**
- **Budgeting**: Cálculos de custo de material, impressão e orçamento total
- **Simulation**: Cálculos de tensão, deslocamento e fator de segurança
- **Cost Optimization**: Seleção de material, desconto em lote e otimização de batch
- **Marketplace**: Busca de componentes, cálculo de pedido e taxa de fornecedor

**Métricas reportadas:**
- Tempo médio de execução (ms)
- Tempo mediano (ms)
- Tempo mínimo/máximo (ms)
- Desvio padrão (ms)
- Throughput (operações/segundo)

### 2. load_test.py
Simula carga no sistema com múltiplos usuários simultâneos.

**Uso:**
```bash
# Teste básico (10 usuários, 10 segundos)
python scripts/performance/load_test.py

# Teste com mais usuários
python scripts/performance/load_test.py --users 50

# Teste de maior duração
python scripts/performance/load_test.py --users 25 --duration 60

# Teste de stress
python scripts/performance/load_test.py --users 100 --duration 30
```

**Parâmetros:**
- `--users`: Número de usuários simultâneos (default: 10)
- `--duration`: Duração do teste em segundos (default: 10)

**Métricas reportadas:**
- Total de requisições
- Taxa de sucesso
- Throughput (requisições/segundo)
- Tempo de resposta (média, mediana, min/max, percentis P50/P90/P95/P99)
- Análise de performance com recomendações

## Métricas Esperadas

### Benchmarks (50 iterações)
Valores de referência em ambiente de desenvolvimento:

| Operação | Tempo Médio | Throughput |
|----------|-------------|------------|
| Cálculo de Material | < 0.1 ms | > 10,000 ops/s |
| Cálculo de Impressão | < 0.1 ms | > 10,000 ops/s |
| Orçamento Total | < 0.2 ms | > 5,000 ops/s |
| Tensão Estrutural | < 0.1 ms | > 10,000 ops/s |
| Busca de Componentes | < 5 ms | > 200 ops/s |
| Total de Pedido | < 0.5 ms | > 2,000 ops/s |

### Load Test (10 usuários, 10s)
Valores de referência:

| Métrica | Valor Esperado |
|---------|----------------|
| Taxa de Sucesso | > 99% |
| Throughput | > 50 req/s |
| Tempo de Resposta Médio | < 100 ms |
| P95 | < 200 ms |
| P99 | < 500 ms |

## Interpretação dos Resultados

### Tempo de Resposta
- ✅ **Excelente**: < 100ms
- ⚠️  **Aceitável**: 100-500ms
- ❌ **Alto**: > 500ms

### Taxa de Sucesso
- ✅ **Excelente**: >= 99%
- ⚠️  **Aceitável**: 95-99%
- ❌ **Baixa**: < 95%

### Throughput
- ✅ **Alto**: >= 100 req/s
- ⚠️  **Médio**: 50-100 req/s
- ❌ **Baixo**: < 50 req/s

## Observações

⚠️ **Importante:**
- Estes testes medem performance de operações simuladas/mock
- Para testes em ambiente real, configure banco de dados e APIs externas
- Resultados variam com hardware, carga do sistema e configurações
- Use estes scripts como baseline para comparações ao longo do tempo

## Próximos Passos

Para testes mais robustos em ambiente de produção, considere:
- Ferramentas profissionais: Locust, JMeter, k6
- Testes de stress (carga crescente até falha)
- Testes de spike (picos repentinos de carga)
- Monitoramento de recursos (CPU, memória, I/O)
- Testes com banco de dados real
- Testes de APIs externas (com rate limiting)

## Autor

Sprint 5 - Quality & Performance Testing
Data: 2025-11-19
