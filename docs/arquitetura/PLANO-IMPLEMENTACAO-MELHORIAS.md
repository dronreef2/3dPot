# Plano de Implementação de Melhorias 3dPot

**Data**: 2024-11-19  
**Versão**: 1.0  
**Base**: Análise Pós-Reorganização v1.0  
**Status**: 📋 PLANEJAMENTO

---

## 📊 Visão Geral do Plano

Este documento detalha o plano de implementação das melhorias identificadas na análise pós-reorganização do repositório 3dPot.

### Resumo Executivo

- **Total de Tasks**: 13 tarefas identificadas
- **Estimativa Total**: 57-76 horas de trabalho
- **Sprints Recomendados**: 4 sprints de 1 semana cada
- **Prioridades**: 4 tarefas ALTA, 5 tarefas MÉDIA, 4 tarefas BAIXA

---

## 🎯 Sprint 1 - Correções Críticas (Semana 1)

**Objetivo**: Resolver problemas críticos de estrutura e facilitar onboarding

**Duração**: 5-7 dias  
**Estimativa Total**: 7-10 horas

### Task 1.1 - Remover Arquivos de Backup ⚡

**Prioridade**: ALTA  
**Tipo**: LIMPEZA  
**Estimativa**: 15 minutos

**Descrição**:
Remover arquivos de backup que poluem o repositório e causam confusão.

**Arquivos a Remover**:
```
backend/main_backup.py
backend/main_original_problematic.py
```

**Passos**:
1. Verificar que arquivos estão no git history
2. Remover arquivos com `git rm`
3. Commit e push
4. Atualizar .gitignore para prevenir futuros backups:
   ```gitignore
   # Backup files
   *_backup.py
   *_original*.py
   *.bak
   ```

**Critério de Sucesso**:
- [ ] Arquivos removidos do repositório
- [ ] Git history preservado
- [ ] .gitignore atualizado

---

### Task 1.2 - Consolidar Estrutura Backend 🏗️

**Prioridade**: ALTA  
**Tipo**: REFACTOR  
**Estimativa**: 4-6 horas

**Descrição**:
Unificar as duas estruturas de backend (`backend/` e `backend/app/`) em uma única estrutura consistente.

**Problema Atual**:
```
backend/
├── main.py              # Entry point 1
├── models/              # Modelos SQLAlchemy Sprint 1-5
├── services/            # Serviços Sprint 1-5
├── routers/             # Routers Sprint 1-5
└── app/
    ├── main.py          # Entry point 2
    ├── models/          # Modelos IoT
    ├── services/        # Serviços IoT
    └── routers/         # Routers IoT
```

**Estrutura Proposta**:
```
backend/
├── main.py              # Entry point ÚNICO
├── core/
│   ├── config.py
│   ├── database.py
│   └── exceptions.py
├── models/              # TODOS os modelos SQLAlchemy
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   ├── simulation.py
│   ├── budgeting.py
│   ├── device.py        # Migrado de app/
│   ├── alert.py         # Migrado de app/
│   └── sensor_data.py   # Migrado de app/
├── schemas/             # Schemas Pydantic
│   ├── __init__.py
│   ├── user.py
│   ├── project.py
│   └── iot.py           # Migrado de app/
├── routers/             # TODOS os routers
│   ├── __init__.py
│   ├── auth.py
│   ├── conversational.py
│   ├── modeling.py
│   ├── simulation.py
│   ├── budgeting.py
│   ├── devices.py       # Migrado de app/
│   ├── alerts.py        # Migrado de app/
│   └── monitoring.py    # Migrado de app/
├── services/            # TODOS os serviços
│   ├── __init__.py
│   ├── auth_service.py
│   ├── modeling_service.py
│   ├── minimax_service.py
│   ├── device_service.py      # Migrado de app/
│   └── monitoring_service.py  # Migrado de app/
├── middleware/
│   └── auth.py
└── tests/               # Testes do backend
    ├── test_integration.py
    └── test_unit.py
```

**Passos de Implementação**:

1. **Análise de Conteúdo** (30min)
   - Listar todos os arquivos em `backend/app/`
   - Identificar funcionalidades únicas vs duplicadas
   - Mapear dependências entre arquivos

2. **Migração de Modelos** (1h)
   - Mover `backend/app/models/*.py` para `backend/models/`
   - Atualizar imports em todos os arquivos
   - Atualizar `backend/models/__init__.py`

3. **Migração de Schemas** (30min)
   - Mover `backend/app/schemas/*.py` para `backend/schemas/`
   - Criar `backend/schemas/iot.py` consolidado
   - Atualizar imports

4. **Migração de Routers** (1h)
   - Mover `backend/app/routers/*.py` para `backend/routers/`
   - Atualizar imports e registros no main
   - Testar endpoints

5. **Migração de Serviços** (1h)
   - Mover `backend/app/services/*.py` para `backend/services/`
   - Atualizar imports
   - Resolver conflitos de nomes

6. **Consolidar main.py** (1h)
   - Unificar funcionalidades dos dois main.py
   - Registrar todos os routers
   - Configurar middleware e CORS
   - Testar aplicação completa

7. **Remover backend/app/** (15min)
   - Garantir que tudo foi migrado
   - Remover diretório `backend/app/`
   - Commit

8. **Atualizar Documentação** (30min)
   - Atualizar README.md
   - Atualizar STRUCTURE.md
   - Atualizar imports em exemplos

**Critérios de Sucesso**:
- [ ] Diretório `backend/app/` removido
- [ ] Todos os modelos em `backend/models/`
- [ ] Todos os routers em `backend/routers/`
- [ ] Todos os serviços em `backend/services/`
- [ ] Um único `backend/main.py` funcional
- [ ] Todos os imports atualizados
- [ ] Servidor FastAPI sobe sem erros
- [ ] Todos os endpoints funcionando

**Riscos**:
- Import circular: Resolver com import tardio ou refactor
- Conflito de nomes: Renomear classes/funções conflitantes
- Quebra de testes: Atualizar imports nos testes

---

### Task 1.3 - Script de Setup Automatizado 🚀

**Prioridade**: ALTA  
**Tipo**: UX DEV  
**Estimativa**: 2-3 horas

**Descrição**:
Criar script que automatiza todo o setup do ambiente de desenvolvimento.

**Arquivo a Criar**: `scripts/setup-dev.sh`

**Funcionalidades**:
```bash
#!/bin/bash
# 3dPot - Script de Setup de Desenvolvimento Automatizado
# Versão: 1.0

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 3dPot - Setup de Desenvolvimento Automatizado v1.0"
echo "======================================================"

# 1. Verificar dependências do sistema
echo -e "\n${YELLOW}[1/8]${NC} Verificando dependências do sistema..."

command -v python3 >/dev/null 2>&1 || {
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.8+${NC}"
    exit 1
}

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION encontrado"

command -v docker >/dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️  Docker não encontrado. Funcionalidades de container limitadas.${NC}"
}

command -v docker-compose >/dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️  Docker Compose não encontrado.${NC}"
}

# 2. Criar ambiente virtual
echo -e "\n${YELLOW}[2/8]${NC} Criando ambiente virtual Python..."

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual já existe. Pulando...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Ambiente virtual criado"
fi

# 3. Ativar ambiente virtual
echo -e "\n${YELLOW}[3/8]${NC} Ativando ambiente virtual..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Ambiente virtual ativado"

# 4. Atualizar pip
echo -e "\n${YELLOW}[4/8]${NC} Atualizando pip..."
pip install --quiet --upgrade pip
echo -e "${GREEN}✓${NC} pip atualizado"

# 5. Instalar dependências Python
echo -e "\n${YELLOW}[5/8]${NC} Instalando dependências Python..."

echo "  → Instalando dependências principais..."
pip install --quiet -r requirements.txt

echo "  → Instalando dependências de teste..."
pip install --quiet -r requirements-test.txt

echo "  → Instalando dependências do backend..."
pip install --quiet -r backend/requirements.txt

echo -e "${GREEN}✓${NC} Dependências instaladas"

# 6. Configurar arquivo .env
echo -e "\n${YELLOW}[6/8]${NC} Configurando variáveis de ambiente..."

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env já existe. Pulando...${NC}"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} Arquivo .env criado a partir de .env.example"
        echo -e "${YELLOW}⚠️  IMPORTANTE: Configure suas variáveis em .env antes de rodar o backend${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example não encontrado. Crie .env manualmente.${NC}"
    fi
fi

if [ -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env já existe. Pulando...${NC}"
else
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✓${NC} backend/.env criado"
    fi
fi

# 7. Iniciar serviços Docker (se disponível)
echo -e "\n${YELLOW}[7/8]${NC} Inicializando serviços Docker..."

if command -v docker-compose >/dev/null 2>&1; then
    echo "  → Subindo PostgreSQL e Redis..."
    docker-compose up -d postgres redis || {
        echo -e "${YELLOW}⚠️  Falha ao subir containers. Continuando...${NC}"
    }
    sleep 3
    
    # Verificar se containers estão rodando
    if docker ps | grep -q postgres; then
        echo -e "${GREEN}✓${NC} PostgreSQL rodando"
    fi
    
    if docker ps | grep -q redis; then
        echo -e "${GREEN}✓${NC} Redis rodando"
    fi
else
    echo -e "${YELLOW}⚠️  Docker Compose não disponível. Configure banco manualmente.${NC}"
fi

# 8. Rodar testes básicos
echo -e "\n${YELLOW}[8/8]${NC} Validando instalação com testes..."

python -m pytest tests/unit/test_project_structure.py -v --tb=short || {
    echo -e "${RED}❌ Alguns testes falharam. Verifique a instalação.${NC}"
    exit 1
}

echo -e "${GREEN}✓${NC} Testes básicos passaram"

# Resumo final
echo -e "\n${GREEN}======================================================"
echo "✅ Setup Concluído com Sucesso!"
echo "======================================================${NC}"
echo ""
echo "📋 Próximos passos:"
echo "  1. Configure suas variáveis em .env e backend/.env"
echo "  2. Ative o ambiente virtual: source venv/bin/activate"
echo "  3. Inicie o backend: cd backend && uvicorn main:app --reload"
echo "  4. Acesse a documentação: http://localhost:8000/docs"
echo ""
echo "📚 Documentação:"
echo "  - README.md - Visão geral do projeto"
echo "  - STRUCTURE.md - Estrutura do repositório"
echo "  - docs/guias/ - Guias detalhados"
echo ""
echo "🧪 Executar testes:"
echo "  - pytest tests/unit/ - Testes unitários"
echo "  - pytest tests/integration/ - Testes de integração"
echo "  - pytest --cov=backend backend/tests/ - Cobertura do backend"
echo ""
echo "💡 Dica: Execute './scripts/setup-dev.sh --help' para mais opções"
```

**Critérios de Sucesso**:
- [ ] Script executável criado
- [ ] Verifica dependências do sistema
- [ ] Cria ambiente virtual
- [ ] Instala todas as dependências
- [ ] Configura .env
- [ ] Sobe containers Docker
- [ ] Roda testes de validação
- [ ] Documentação clara no output

---

## 🧪 Sprint 2 - Qualidade e Testes (Semana 2)

**Objetivo**: Melhorar cobertura de testes e qualidade do código

**Duração**: 5-7 dias  
**Estimativa Total**: 15-19 horas

### Task 2.1 - Consolidar Testes de Integração 🔄

**Prioridade**: MÉDIA  
**Tipo**: REFACTOR + TEST  
**Estimativa**: 3-4 horas

**Descrição**:
Unificar testes de integração similares, padronizar nomenclatura e eliminar duplicações.

**Problema Atual**:
```
tests/integration/
├── test_integration.py                # Genérico?
├── test_integration_core.py           # Core?
├── test_integration_final.py          # Final?
├── test_minimax_service.py            # Específico Minimax
├── teste_endpoint_lgm.py              # Endpoint LGM (portugês)
└── teste_integracao_completa.py       # Completa? (português)
```

**Estrutura Proposta**:
```
tests/integration/
├── README.md                          # Explicação dos testes
├── conftest.py                        # Fixtures compartilhadas
├── test_auth_integration.py           # Testes de autenticação
├── test_modeling_integration.py       # Testes de modelagem 3D
├── test_minimax_integration.py        # Testes de IA Minimax
├── test_simulation_integration.py     # Testes de simulação
├── test_budgeting_integration.py      # Testes de orçamento
└── test_iot_integration.py            # Testes de IoT
```

**Passos**:
1. **Análise de Conteúdo** (1h)
   - Ler cada arquivo de teste atual
   - Identificar duplicações
   - Mapear testes por feature/módulo

2. **Criar conftest.py** (30min)
   - Fixtures compartilhadas (client, db, user)
   - Configurações de teste
   - Mocks comuns

3. **Reorganizar por Feature** (2h)
   - Criar arquivos por módulo
   - Mover testes para arquivos corretos
   - Eliminar duplicações
   - Padronizar nomenclatura (inglês)

4. **Criar README.md** (30min)
   - Explicar cada arquivo de teste
   - Documentar como rodar
   - Listar fixtures disponíveis

**Critérios de Sucesso**:
- [ ] Nomenclatura padronizada (test_*_integration.py)
- [ ] Sem duplicação de testes
- [ ] Testes organizados por feature
- [ ] README.md explicativo
- [ ] Todos os testes passando
- [ ] Coverage mantida ou aumentada

---

### Task 2.2 - Criar Testes Unitários para Serviços 🧪

**Prioridade**: ALTA  
**Tipo**: TEST  
**Estimativa**: 8-10 horas

**Descrição**:
Adicionar testes unitários para todos os serviços críticos do backend.

**Estrutura a Criar**:
```
tests/unit/backend/
├── __init__.py
├── conftest.py                    # Fixtures e mocks
├── services/
│   ├── __init__.py
│   ├── test_auth_service.py       # 1h
│   ├── test_modeling_service.py   # 2h
│   ├── test_minimax_service.py    # 2h
│   ├── test_simulation_service.py # 2h
│   └── test_budgeting_service.py  # 1h
├── models/
│   ├── test_user_model.py
│   └── test_project_model.py
└── README.md
```

**Template de Teste Unitário**:
```python
"""
Testes Unitários para AuthService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services.auth_service import AuthService
from backend.core.exceptions import AuthenticationError

@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    return MagicMock()

@pytest.fixture
def auth_service(mock_db):
    """Instância do AuthService com DB mockado"""
    return AuthService(db=mock_db)

class TestAuthService:
    """Testes para o serviço de autenticação"""
    
    def test_login_success(self, auth_service, mock_db):
        """Testa login com credenciais válidas"""
        # Arrange
        mock_db.query().filter().first.return_value = Mock(
            id=1,
            username="testuser",
            hashed_password="$2b$12$..." # hash válido
        )
        
        # Act
        result = auth_service.login("testuser", "password123")
        
        # Assert
        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, auth_service, mock_db):
        """Testa login com credenciais inválidas"""
        # Arrange
        mock_db.query().filter().first.return_value = None
        
        # Act & Assert
        with pytest.raises(AuthenticationError):
            auth_service.login("invaliduser", "wrongpass")
    
    def test_create_user_success(self, auth_service, mock_db):
        """Testa criação de usuário"""
        # Arrange
        mock_db.query().filter().first.return_value = None  # User doesn't exist
        
        # Act
        user = auth_service.create_user(
            username="newuser",
            email="new@example.com",
            password="securepass123"
        )
        
        # Assert
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
```

**Critérios de Sucesso**:
- [ ] Testes para todos os serviços críticos
- [ ] Coverage de serviços >80%
- [ ] Testes isolados (sem dependências externas)
- [ ] Uso de mocks para DB e APIs
- [ ] Testes rápidos (<5s total)
- [ ] Documentação de cada teste

---

### Task 2.3 - Atualizar Documentação Estrutural 📚

**Prioridade**: MÉDIA  
**Tipo**: DOCUMENTAÇÃO  
**Estimativa**: 2-3 horas

**Descrição**:
Atualizar documentação para refletir mudanças da consolidação do backend e criar guia de setup.

**Arquivos a Atualizar/Criar**:

1. **README.md** (1h)
   - Corrigir seção de estrutura backend
   - Adicionar "Quick Start em 5 Minutos"
   - Atualizar comandos de teste
   - Adicionar badges de coverage

2. **STRUCTURE.md** (30min)
   - Remover menção a `backend/app/`
   - Atualizar estrutura de backend
   - Adicionar seção sobre testes

3. **docs/guias/GUIA-SETUP-DESENVOLVIMENTO.md** (1h) - NOVO
   ```markdown
   # Guia de Setup de Desenvolvimento - 3dPot
   
   ## Requisitos
   - Python 3.8+
   - Docker e Docker Compose (opcional)
   - Git
   
   ## Setup Automatizado (Recomendado)
   
   ```bash
   ./scripts/setup-dev.sh
   ```
   
   ## Setup Manual
   
   ### 1. Clone do Repositório
   ...
   
   ### 2. Ambiente Virtual
   ...
   
   ### 3. Dependências
   ...
   
   ### 4. Banco de Dados
   ...
   
   ### 5. Configuração
   ...
   
   ## Comandos Úteis
   ...
   
   ## Troubleshooting
   ...
   ```

**Critérios de Sucesso**:
- [ ] README.md atualizado e preciso
- [ ] STRUCTURE.md reflete estrutura real
- [ ] GUIA-SETUP-DESENVOLVIMENTO.md criado
- [ ] Links entre documentos funcionando
- [ ] Comandos testados e funcionando

---

## 📜 Sprint 3 - Scripts e DevEx (Semana 3)

**Objetivo**: Melhorar experiência de desenvolvimento e organização de scripts

**Duração**: 5-7 dias  
**Estimativa Total**: 11-14 horas

### Task 3.1 - Unificar Scripts de Demo 🎭

**Prioridade**: MÉDIA  
**Tipo**: REFACTOR  
**Estimativa**: 4-5 horas

**Descrição**:
Consolidar 10 scripts de demo em uma CLI unificada.

**Estrutura Proposta**:
```
scripts/demos/
├── demo.py                    # CLI principal
├── README.md                  # Documentação
├── demos/
│   ├── __init__.py
│   ├── auth_demo.py          # Consolidado de test-auth-system.py
│   ├── lgm_demo.py           # Consolidado de lgm_integration_example.py
│   ├── minimax_demo.py       # Consolidado de teste-*-minimax.py
│   ├── modeling_demo.py      # Consolidado de sistema_modelagem_*
│   └── slant3d_demo.py       # De slant3d_integration.py
└── requirements.txt          # Dependências específicas
```

**CLI Principal (demo.py)**:
```python
"""
3dPot Demo CLI - Demonstrações do Sistema
"""
import click
from demos import auth_demo, lgm_demo, minimax_demo, modeling_demo, slant3d_demo

@click.group()
def cli():
    """🎭 3dPot - Demonstrações do Sistema"""
    pass

@cli.command()
def auth():
    """🔐 Demonstração do sistema de autenticação"""
    click.echo("Iniciando demo de autenticação...")
    auth_demo.run()

@cli.command()
@click.option('--prompt', '-p', help='Prompt para o LGM')
def lgm(prompt):
    """🤖 Demonstração de integração com LGM"""
    click.echo("Iniciando demo LGM...")
    lgm_demo.run(prompt=prompt)

@cli.command()
@click.option('--message', '-m', required=True, help='Mensagem para o Minimax')
def minimax(message):
    """💬 Demonstração de IA conversacional Minimax"""
    click.echo("Iniciando demo Minimax...")
    minimax_demo.run(message=message)

@cli.command()
@click.option('--shape', type=click.Choice(['box', 'cylinder', 'sphere']))
def modeling(shape):
    """🎨 Demonstração de modelagem 3D"""
    click.echo(f"Iniciando demo de modelagem: {shape}...")
    modeling_demo.run(shape=shape)

@cli.command()
def slant3d():
    """🏭 Demonstração de integração com Slant3D"""
    click.echo("Iniciando demo Slant3D...")
    slant3d_demo.run()

@cli.command()
def all():
    """🚀 Executar todas as demonstrações"""
    click.echo("Executando todas as demos...")
    for demo in [auth_demo, lgm_demo, minimax_demo, modeling_demo, slant3d_demo]:
        try:
            demo.run()
        except Exception as e:
            click.echo(f"Erro em {demo.__name__}: {e}", err=True)

if __name__ == '__main__':
    cli()
```

**Uso**:
```bash
python scripts/demos/demo.py --help
python scripts/demos/demo.py auth
python scripts/demos/demo.py minimax -m "Hello, how are you?"
python scripts/demos/demo.py modeling --shape=box
python scripts/demos/demo.py all
```

**Passos**:
1. Criar estrutura de diretórios e CLI base (1h)
2. Refatorar script de auth (30min)
3. Refatorar scripts de LGM (1h)
4. Refatorar scripts de Minimax (1h)
5. Refatorar script de modelagem (1h)
6. Criar README.md (30min)

**Critérios de Sucesso**:
- [ ] CLI funcional com todos os comandos
- [ ] Scripts originais convertidos em módulos
- [ ] README.md com exemplos
- [ ] Testes de cada demo passando
- [ ] 10 scripts → 1 CLI + 5 módulos

---

### Task 3.2 - Criar Índice de Documentação 📖

**Prioridade**: MÉDIA  
**Tipo**: DOCUMENTAÇÃO  
**Estimativa**: 2-3 horas

**Descrição**:
Criar índice navegável para os 111 arquivos markdown em `docs/`.

**Arquivo a Criar**: `docs/INDEX.md`

**Estrutura**:
```markdown
# Índice da Documentação 3dPot

Guia completo para navegação em toda a documentação do projeto.

## 📚 Categorias

- [Guias e Tutoriais](#guias) - Como usar o sistema
- [Arquitetura](#arquitetura) - Decisões técnicas e design
- [Sprints](#sprints) - Histórico de desenvolvimento
- [Relatórios](#relatorios) - Progresso e entregas
- [Validação](#validacao) - Testes e CI/CD
- [Instalação](#instalacao) - Setup e configuração
- [Planejamento](#planejamento) - Roadmap e futuro

---

## 🎯 Guias e Tutoriais {#guias}

### Para Iniciantes
- [GUIA-SETUP-DESENVOLVIMENTO.md](guias/GUIA-SETUP-DESENVOLVIMENTO.md) - Setup em 5 minutos
- [README-IMPLEMENTACAO.md](guias/README-IMPLEMENTACAO.md) - Implementação básica

### Para Desenvolvedores
- [README-MODELAGEM-INTELIGENTE.md](guias/README-MODELAGEM-INTELIGENTE.md) - Modelagem 3D
- [exemplo-uso-endpoint-integrado.md](guias/exemplo-uso-endpoint-integrado.md) - Uso de APIs

### Por Feature
- **Autenticação**: ...
- **Modelagem 3D**: ...
- **IA Conversacional**: ...

---

## 🏗️ Arquitetura {#arquitetura}

### Visão Geral
- [ARQUITETURA-3DPOT-EVOLUTIVA.md](arquitetura/ARQUITETURA-3DPOT-EVOLUTIVA.md) - Arquitetura completa
- [ANALISE-POS-REORGANIZACAO.md](arquitetura/ANALISE-POS-REORGANIZACAO.md) - Análise atual
- [PLANO-IMPLEMENTACAO-MELHORIAS.md](arquitetura/PLANO-IMPLEMENTACAO-MELHORIAS.md) - Roadmap

### Específicos
- [TODO.md](arquitetura/TODO.md) - Tarefas pendentes
- [PLANO_EXECUCAO_3DPOT.md](arquitetura/PLANO_EXECUCAO_3DPOT.md) - Plano de execução

---

## 🏃 Sprints {#sprints}

[Lista completa de 21 documentos de sprints organizados cronologicamente]

---

## 📊 Relatórios {#relatorios}

[Lista de 35 relatórios de progresso]

---

## ✅ Validação {#validacao}

[Lista de 18 relatórios de validação e CI]

---

## 🔍 Busca Rápida

### Por Tópico
- **Setup**: [GUIA-SETUP](guias/GUIA-SETUP-DESENVOLVIMENTO.md), [README](../README.md)
- **Testes**: [Validação](validacao/), [CI Reports](validacao/CI_*.md)
- **API**: [Backend README](../backend/README.md), [Guias](guias/)
- **IoT**: [Sprints](sprints/), [Relatórios](relatorios/)

### Por Data
- **Mais Recentes**: [Sprint 6](sprints/SPRINT6-*), [Análise](arquitetura/ANALISE-POS-REORGANIZACAO.md)
- **Histórico**: [Sprint 1](sprints/SPRINT1-*), [Sprint 2](sprints/SPRINT2-*)

### Por Autor/Sprint
- [Sprint 1 - IoT Foundation](sprints/SPRINT1-CONCLUIDO.md)
- [Sprint 2 - IA Conversacional](sprints/SPRINT2-*)
- [Sprint 3 - Modelagem 3D](sprints/SPRINT3-*)
- ...
```

**Critérios de Sucesso**:
- [ ] Índice completo criado
- [ ] Links funcionando
- [ ] Categorização clara
- [ ] Busca rápida por tópico
- [ ] Fácil navegação

---

### Task 3.3 - Adicionar Pre-commit Hooks ✅

**Prioridade**: MÉDIA  
**Tipo**: UX DEV  
**Estimativa**: 1-2 horas

**Descrição**:
Configurar pre-commit hooks para validação automática de código.

**Arquivo a Criar**: `.pre-commit-config.yaml`

**Configuração**:
```yaml
# 3dPot Pre-commit Hooks Configuration
# Garante qualidade de código antes de cada commit

repos:
  # Python Code Formatting
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=100]
  
  # Python Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --ignore=E203,W503]
        exclude: ^(migrations/|tests/fixtures/)
  
  # Python Import Sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]
  
  # Python Type Checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports, --no-strict-optional]
        exclude: ^(tests/|migrations/)
  
  # YAML Validation
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
  
  # Markdown Linting
  - repo: https://github.com/markdownlint/markdownlint
    rev: v0.12.0
    hooks:
      - id: markdownlint
        args: [--rules, ~MD013]  # Ignore line length
  
  # Security Checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, backend/, -ll]
        exclude: ^tests/
```

**Setup**:
```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Rodar em todos os arquivos (primeira vez)
pre-commit run --all-files

# Atualizar hooks
pre-commit autoupdate
```

**Documentação em CONTRIBUTING.md**:
```markdown
## Pre-commit Hooks

Este projeto usa pre-commit hooks para garantir qualidade de código.

### Setup Inicial
```bash
pip install pre-commit
pre-commit install
```

### Uso
Os hooks rodam automaticamente antes de cada commit. Para rodar manualmente:

```bash
# Todos os arquivos
pre-commit run --all-files

# Apenas arquivos staged
pre-commit run

# Hook específico
pre-commit run black
```

### Bypass (use com cuidado!)
```bash
git commit --no-verify -m "mensagem"
```
```

**Critérios de Sucesso**:
- [ ] `.pre-commit-config.yaml` criado
- [ ] Hooks funcionando corretamente
- [ ] Documentação em CONTRIBUTING.md
- [ ] CI validando pre-commit

---

## 🔄 Sprint 4 - Refactors Avançados (Backlog)

**Objetivo**: Melhorias de longo prazo e refactorings maiores

**Duração**: TBD  
**Estimativa Total**: 20-30 horas

### Task 4.1 - Implementar Arquitetura em Camadas

**Prioridade**: MÉDIA (Long-term)  
**Tipo**: REFACTOR  
**Estimativa**: 12-16 horas

**Descrição**:
Refatorar backend para arquitetura em camadas (Clean Architecture / Hexagonal).

**Estrutura Proposta**: (Ver seção 3.1.2 do documento de análise)

**Status**: Backlog - Implementar após Tasks 1-3

---

### Task 4.2 - Consolidar Scripts de Validação

**Prioridade**: BAIXA  
**Tipo**: REFACTOR  
**Estimativa**: 2-3 horas

**Status**: Backlog

---

### Task 4.3 - CLI Interna Unificada

**Prioridade**: BAIXA  
**Tipo**: UX DEV  
**Estimativa**: 3-4 horas

**Status**: Backlog

---

### Task 4.4 - Internacionalização da Documentação

**Prioridade**: BAIXA  
**Tipo**: DOCUMENTAÇÃO  
**Estimativa**: 4-6 horas

**Status**: Backlog

---

## 📊 Tracking e Métricas

### Métricas de Sucesso

**Sprint 1**:
- [ ] Backend consolidado (1 estrutura única)
- [ ] Setup automatizado (<5min)
- [ ] 0 arquivos de backup

**Sprint 2**:
- [ ] Coverage de testes >75%
- [ ] Testes unitários para todos os serviços
- [ ] Documentação atualizada

**Sprint 3**:
- [ ] 10 scripts demo → 1 CLI
- [ ] Índice de docs criado
- [ ] Pre-commit hooks ativos

**Sprint 4**:
- [ ] Arquitetura em camadas
- [ ] Docs internacionalizados

### Tracking

Use GitHub Projects para tracking:

**Colunas**:
- 📋 Backlog
- 🏃 Em Progresso
- 👀 Em Revisão
- ✅ Concluído

**Labels**:
- `refactor` - Refatoração de código
- `test` - Testes
- `docs` - Documentação
- `ux-dev` - Experiência de desenvolvedor
- `priority-high` - Alta prioridade
- `priority-medium` - Média prioridade
- `priority-low` - Baixa prioridade

---

## 🎯 Resumo Executivo

### Sprints Planejados

| Sprint | Foco | Tasks | Estimativa | Status |
|--------|------|-------|------------|--------|
| Sprint 1 | Correções Críticas | 3 | 7-10h | 📋 Planejado |
| Sprint 2 | Testes e Qualidade | 3 | 15-19h | 📋 Planejado |
| Sprint 3 | Scripts e DevEx | 3 | 11-14h | 📋 Planejado |
| Sprint 4 | Refactors Avançados | 4 | 20-30h | 📋 Backlog |
| **TOTAL** | **4 Sprints** | **13 Tasks** | **53-73h** | - |

### Recomendação

**Executar em ordem**:
1. Sprint 1 → Desbloqueia desenvolvimento
2. Sprint 2 → Garante qualidade
3. Sprint 3 → Melhora produtividade
4. Sprint 4 → Evolução de longo prazo

**Pode começar hoje com**:
- Task 1.1 (15min) - Quick win
- Task 1.3 (2-3h) - Alto impacto

---

**Documento Versionado**: v1.0  
**Última Atualização**: 2024-11-19  
**Status**: 📋 PRONTO PARA EXECUÇÃO
