# 3dPot CLI - Interface Unificada de Linha de Comando

Ferramenta unificada para executar demos, validações e monitoramento do projeto 3dPot.

## 🚀 Início Rápido

```bash
# Ver ajuda geral
python scripts/cli/main.py --help

# Executar uma demo
python scripts/cli/main.py demo minimax

# Validar modelos OpenSCAD
python scripts/cli/main.py validate openscad

# Monitorar workflows
python scripts/cli/main.py monitor workflows
```

## 📋 Comandos Disponíveis

### 1. `demo` - Demonstrações do Sistema

Execute demonstrações interativas dos componentes do sistema.

```bash
# Demo de integração com Minimax M2
python scripts/cli/main.py demo minimax

# Demo de modelagem 3D
python scripts/cli/main.py demo modeling

# Demo do sistema completo
python scripts/cli/main.py demo system

# Demo de integração LGM
python scripts/cli/main.py demo lgm

# Demo do sistema de autenticação
python scripts/cli/main.py demo auth
```

**Scripts integrados:**
- `teste-minimax-standalone.py`
- `teste-sistema-modelagem-sprint3.py`
- `demonstracao_sistema.py`
- `lgm_integration_example.py`
- `test-auth-system.py`

### 2. `validate` - Validações

Execute validações de código e modelos.

```bash
# Validar todos os modelos OpenSCAD
python scripts/cli/main.py validate openscad

# Validação rápida de OpenSCAD
python scripts/cli/main.py validate openscad --quick

# Validar sintaxe do código Python
python scripts/cli/main.py validate syntax

# Validar qualidade do código
python scripts/cli/main.py validate quality
```

**Scripts integrados:**
- `validate_openscad_models.py`
- `quick_openscad_check.py`
- `syntax_validator.py`
- `fix_code_quality.py`

### 3. `monitor` - Monitoramento

Monitore workflows e performance do sistema.

```bash
# Monitorar workflows GitHub Actions
python scripts/cli/main.py monitor workflows

# Monitorar workflows com sugestões de otimização
python scripts/cli/main.py monitor workflows --optimize

# Monitorar performance do sistema
python scripts/cli/main.py monitor performance
```

**Scripts integrados:**
- `workflow_monitor.py`
- `optimize_workflows.py`
- `performance_monitor.py`

## 🔧 Uso como Módulo Python

A CLI também pode ser executada como módulo Python:

```bash
# Forma alternativa de executar comandos
python -m scripts.cli demo minimax
python -m scripts.cli validate openscad
python -m scripts.cli monitor workflows
```

## 📚 Documentação de Comandos

### Ajuda Contextual

Todos os comandos suportam `--help`:

```bash
# Ajuda geral
python scripts/cli/main.py --help

# Ajuda do comando demo
python scripts/cli/main.py demo --help

# Ajuda do comando validate
python scripts/cli/main.py validate --help

# Ajuda do comando monitor
python scripts/cli/main.py monitor --help
```

### Opções Específicas

Alguns subcomandos têm opções específicas:

```bash
# Validação rápida de OpenSCAD
python scripts/cli/main.py validate openscad --quick

# Monitoramento com otimizações
python scripts/cli/main.py monitor workflows --optimize
```

## 🎯 Exemplos de Uso

### Cenário 1: Testar Integração Minimax

```bash
# Execute a demo do Minimax
python scripts/cli/main.py demo minimax

# A demo irá:
# 1. Verificar configuração da API
# 2. Testar conexão
# 3. Enviar mensagens de exemplo
# 4. Extrair especificações
```

### Cenário 2: Validar Antes de Commit

```bash
# Validar qualidade do código
python scripts/cli/main.py validate quality

# Validar sintaxe Python
python scripts/cli/main.py validate syntax

# Validar modelos 3D
python scripts/cli/main.py validate openscad --quick
```

### Cenário 3: Monitoramento de CI/CD

```bash
# Verificar status dos workflows
python scripts/cli/main.py monitor workflows

# Obter sugestões de otimização
python scripts/cli/main.py monitor workflows --optimize
```

## 🔄 Compatibilidade com Scripts Antigos

Os scripts originais ainda funcionam para compatibilidade:

```bash
# Forma antiga (ainda funciona)
python scripts/demos/teste-minimax-standalone.py

# Forma nova (recomendada)
python scripts/cli/main.py demo minimax
```

**Recomendação:** Use a CLI unificada para melhor experiência.

## 🛠️ Desenvolvimento

### Estrutura da CLI

```
scripts/cli/
├── __init__.py          # Módulo CLI
├── __main__.py          # Entry point para python -m
└── main.py              # Implementação principal
```

### Adicionar Novo Comando

Para adicionar um novo comando à CLI:

1. Adicione a função de configuração em `main.py`
2. Adicione a função de execução correspondente
3. Conecte ao parser principal em `main()`

Exemplo:

```python
# 1. Configurar subcomando
def setup_new_subcommands(subparsers):
    new_parser = subparsers.add_parser('new', help='Novo comando')
    # Adicionar opções...

# 2. Implementar função de execução
def run_new_command():
    print("🚀 Executando novo comando...")
    # Implementação...

# 3. Conectar em main()
if args.command == 'new':
    run_new_command()
```

## 📖 Documentação Adicional

- **Relatório Sprint 3:** `docs/arquitetura/SPRINT3-SCRIPTS-CLI-E2E-RELATORIO.md`
- **README Principal:** `README.md` (seção CLI Unificada)
- **Scripts de Demo:** `scripts/demos/`
- **Scripts de Validação:** `scripts/validacao/`
- **Scripts de Monitoramento:** `scripts/monitoramento/`

## 🐛 Troubleshooting

### Comando não encontrado

```bash
# Erro: ModuleNotFoundError

# Solução: Execute do diretório raiz do projeto
cd /path/to/3dPot
python scripts/cli/main.py <comando>
```

### Script não tem função main()

```bash
# Aviso: Script não tem função main()

# Isso é normal para alguns scripts antigos
# A CLI tentará executá-los diretamente
# Ou sugerirá executar o script original
```

### Dependências faltando

```bash
# Erro: ImportError

# Instale as dependências necessárias
pip install -r requirements.txt
```

## 📝 Changelog

### v1.0.0 (Sprint 3 - 19/11/2025)

- ✅ Primeira versão da CLI unificada
- ✅ 13 comandos implementados
- ✅ 3 categorias principais (demo, validate, monitor)
- ✅ Help contextual completo
- ✅ Compatibilidade com scripts antigos

## 🎯 Próximas Versões

### v1.1.0 (Planejado para Sprint 4)

- Adicionar cores e formatação rica (rich/click)
- Adicionar barra de progresso para comandos longos
- Consolidar lógica em CLI (não apenas chamar scripts)
- Adicionar testes automatizados para CLI
- Adicionar mais comandos de utilidade

---

**Desenvolvido na Sprint 3**  
**Versão:** 1.0.0  
**Data:** 19/11/2025
