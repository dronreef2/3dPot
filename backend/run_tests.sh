#!/bin/bash

# Script para executar testes automatizados
# Sistema de Prototipagem Sob Demanda

set -e  # Para em caso de erro

echo "🧪 Iniciando execução de testes automatizados..."
echo "================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_color() {
    echo -e "${2}${1}${NC}"
}

# Verifica se estamos no diretório correto
if [ ! -f "pytest.ini" ]; then
    print_color "❌ Erro: Execute este script a partir do diretório backend/" $RED
    exit 1
fi

# Verifica se as dependências estão instaladas
print_color "🔍 Verificando dependências..." $BLUE
if ! python -c "import pytest" 2>/dev/null; then
    print_color "📦 Instalando dependências de teste..." $YELLOW
    pip install -r requirements-test.txt
fi

# Verifica estrutura de testes
if [ ! -d "tests" ]; then
    print_color "❌ Erro: Diretório tests não encontrado!" $RED
    exit 1
fi

print_color "✅ Estrutura de testes verificada" $GREEN

# Função para executar tipos específicos de teste
run_test_suite() {
    local test_type=$1
    local test_pattern=$2
    local description=$3
    
    print_color "🧪 Executando: $description" $BLUE
    echo "Pattern: $test_pattern"
    echo "----------------------------------------"
    
    case $test_type in
        "unit")
            pytest tests/unit/ -v --tb=short
            ;;
        "integration")
            pytest tests/integration/ -v --tb=short
            ;;
        "websocket")
            pytest tests/unit/test_websocket.py -v --tb=short
            ;;
        "all")
            pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html:htmlcov
            ;;
        "coverage")
            pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80
            ;;
        *)
            pytest $test_pattern -v --tb=short
            ;;
    esac
    
    local exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        print_color "✅ $description - PASSOU" $GREEN
    else
        print_color "❌ $description - FALHOU (código: $exit_code)" $RED
    fi
    
    return $exit_code
}

# Função para executar análise de qualidade
run_quality_checks() {
    print_color "🔍 Executando análise de qualidade de código..." $BLUE
    echo "================================================="
    
    # Black - Formatação
    print_color "📝 Verificando formatação com Black..." $YELLOW
    if black --check --diff . ; then
        print_color "✅ Formatação Black - OK" $GREEN
    else
        print_color "⚠️  Formatação Black - Problemas encontrados" $YELLOW
        echo "💡 Execute 'black .' para corrigir"
    fi
    
    echo ""
    
    # isort - Import sorting
    print_color "📦 Verificando imports com isort..." $YELLOW
    if isort --check-only --diff . ; then
        print_color "✅ Import sorting - OK" $GREEN
    else
        print_color "⚠️  Import sorting - Problemas encontrados" $YELLOW
        echo "💡 Execute 'isort .' para corrigir"
    fi
    
    echo ""
    
    # flake8 - Linting
    print_color "🔍 Executando flake8 linting..." $YELLOW
    if flake8 app/ tests/ --count --statistics ; then
        print_color "✅ Linting flake8 - OK" $GREEN
    else
        print_color "⚠️  Linting flake8 - Problemas encontrados" $YELLOW
    fi
    
    echo ""
    
    # mypy - Type checking
    print_color "🔍 Executando mypy type checking..." $YELLOW
    if mypy app/ --ignore-missing-imports ; then
        print_color "✅ Type checking - OK" $GREEN
    else
        print_color "⚠️  Type checking - Problemas encontrados" $YELLOW
    fi
    
    echo ""
    
    # bandit - Security analysis
    print_color "🔒 Executando análise de segurança com bandit..." $YELLOW
    if bandit -r app/ -f json -o bandit-report.json ; then
        print_color "✅ Security analysis - OK" $GREEN
    else
        print_color "⚠️  Security analysis - Problemas encontrados" $YELLOW
    fi
}

# Menu principal
echo ""
print_color "🎯 Menu de Testes:" $BLUE
echo "1) Testes unitários"
echo "2) Testes de integração"
echo "3) Testes WebSocket"
echo "4) Cobertura de código (80%+)"
echo "5) Todos os testes"
echo "6) Análise de qualidade apenas"
echo "7) Testes + Qualidade"
echo "8) Executar teste específico (pattern)"
echo "9) Help"
echo ""
read -p "Escolha uma opção (1-9): " choice

case $choice in
    1)
        print_color "🎯 Executando testes unitários..." $BLUE
        run_test_suite "unit" "tests/unit/" "Testes Unitários"
        ;;
    2)
        print_color "🎯 Executando testes de integração..." $BLUE
        run_test_suite "integration" "tests/integration/" "Testes de Integração"
        ;;
    3)
        print_color "🎯 Executando testes WebSocket..." $BLUE
        run_test_suite "websocket" "tests/unit/test_websocket.py" "Testes WebSocket"
        ;;
    4)
        print_color "🎯 Executando análise de cobertura..." $BLUE
        run_test_suite "coverage" "tests/" "Cobertura de Código"
        ;;
    5)
        print_color "🎯 Executando todos os testes..." $BLUE
        run_test_suite "all" "tests/" "Todos os Testes"
        ;;
    6)
        print_color "🎯 Executando análise de qualidade..." $BLUE
        run_quality_checks
        ;;
    7)
        print_color "🎯 Executando testes + qualidade..." $BLUE
        echo "=== TESTES ==="
        run_test_suite "unit" "tests/unit/" "Testes Unitários" || true
        echo ""
        echo "=== QUALIDADE ==="
        run_quality_checks
        ;;
    8)
        echo ""
        read -p "Digite o padrão do teste: " pattern
        print_color "🎯 Executando padrão: $pattern" $BLUE
        run_test_suite "custom" "$pattern" "Teste Customizado"
        ;;
    9)
        print_color "📖 Help - Informações sobre os testes:" $BLUE
        echo ""
        echo "📁 Estrutura de Testes:"
        echo "├── tests/"
        echo "│   ├── conftest.py         # Configurações globais"
        echo "│   ├── unit/              # Testes unitários"
        echo "│   │   ├── test_auth.py   # Testes de autenticação"
        echo "│   │   ├── test_devices.py # Testes de dispositivos"
        echo "│   │   ├── test_health.py # Testes de health checks"
        echo "│   │   ├── test_projects.py # Testes de projetos"
        echo "│   │   └── test_websocket.py # Testes de WebSocket"
        echo "│   └── integration/       # Testes de integração"
        echo "│       └── test_integration.py"
        echo ""
        echo "🎯 Tipos de Testes:"
        echo "• Unit: Testam componentes individuais"
        echo "• Integration: Testam interação entre componentes"
        echo "• WebSocket: Testam comunicação em tempo real"
        echo ""
        echo "📊 Cobertura:"
        echo "• Mínimo: 80%"
        echo "• Relatórios: HTML em htmlcov/"
        echo ""
        echo "🔍 Qualidade:"
        echo "• Black: Formatação de código"
        echo "• isort: Ordenação de imports"
        echo "• flake8: Linting"
        echo "• mypy: Verificação de tipos"
        echo "• bandit: Análise de segurança"
        ;;
    *)
        print_color "❌ Opção inválida!" $RED
        exit 1
        ;;
esac

# Relatório final
echo ""
print_color "📊 RELATÓRIO FINAL" $BLUE
echo "================================================="

if [ -f "htmlcov/index.html" ]; then
    print_color "📈 Cobertura HTML disponível em: htmlcov/index.html" $GREEN
fi

if [ -f "bandit-report.json" ]; then
    print_color "🔒 Relatório de segurança em: bandit-report.json" $GREEN
fi

print_color "✅ Execução de testes concluída!" $GREEN
echo ""
print_color "🎯 Próximos passos:" $BLUE
echo "• Revisar relatórios de cobertura"
echo "• Corrigir problemas de qualidade encontrados"
echo "• Implementar WebSocket para dispositivos IoT"
echo "• Desenvolver dashboard web"
echo "• Configurar pipeline CI/CD"
echo ""