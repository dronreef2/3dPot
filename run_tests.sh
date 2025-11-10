#!/bin/bash

# Script de execução de testes para o projeto 3dPot
# Permite executar diferentes tipos de testes de forma fácil

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "=============================================="
echo "         3dPot Test Runner"
echo "=============================================="
echo -e "${NC}"

# Verifica se o diretório atual é o correto
if [ ! -f "README.md" ] || [ ! -d "tests" ]; then
    print_error "Execute este script no diretório raiz do projeto 3dPot"
    exit 1
fi

# Verifica se pytest está instalado
if ! command -v pytest &> /dev/null; then
    print_warning "pytest não encontrado. Instalando dependências de teste..."
    pip install -r requirements-test.txt
fi

# Função para executar todos os testes
run_all_tests() {
    print_status "Executando todos os testes..."
    pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
    print_success "Todos os testes concluídos!"
}

# Função para executar testes unitários
run_unit_tests() {
    print_status "Executando testes unitários..."
    pytest tests/unit/ -v --cov=interface-web/server
    print_success "Testes unitários concluídos!"
}

# Função para executar testes de integração
run_integration_tests() {
    print_status "Executando testes de integração..."
    pytest tests/integration/ -v
    print_success "Testes de integração concluídos!"
}

# Função para executar testes de hardware
run_hardware_tests() {
    print_status "Executando testes de hardware..."
    pytest tests/unit/ -m "arduino or esp32 or raspberry_pi" -v
    print_success "Testes de hardware concluídos!"
}

# Função para executar testes de modelos 3D
run_3d_tests() {
    print_status "Executando testes de modelos 3D..."
    pytest tests/unit/test_3d_models.py -v
    print_success "Testes de modelos 3D concluídos!"
}

# Função para executar testes de estrutura do projeto
run_structure_tests() {
    print_status "Executando testes de estrutura do projeto..."
    pytest tests/unit/test_project_structure.py -v
    print_success "Testes de estrutura concluídos!"
}

# Função para executar testes com coverage detalhado
run_coverage_report() {
    print_status "Executando testes com relatório de cobertura detalhado..."
    pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-fail-under=70
    print_success "Relatório de cobertura gerado em tests/coverage_html/"
    if command -v open &> /dev/null; then
        open tests/coverage_html/index.html
    fi
}

# Função para executar testes em modo paralelo
run_parallel_tests() {
    print_status "Executando testes em paralelo..."
    pytest tests/ -n auto -v
    print_success "Testes paralelos concluídos!"
}

# Função para executar testes específicos de componente
run_component_test() {
    local component=$1
    if [ -z "$component" ]; then
        print_error "Especifique o componente: arduino, esp32, raspberry_pi, 3d_models, structure"
        return 1
    fi
    
    case $component in
        "arduino")
            run_hardware_tests_filter "arduino"
            ;;
        "esp32")
            run_hardware_tests_filter "esp32"
            ;;
        "raspberry_pi")
            run_hardware_tests_filter "raspberry_pi"
            ;;
        "3d_models"|"3d")
            run_3d_tests
            ;;
        "structure"|"proj")
            run_structure_tests
            ;;
        "integration"|"integ")
            run_integration_tests
            ;;
        *)
            print_error "Componente não reconhecido: $component"
            print_error "Componentes disponíveis: arduino, esp32, raspberry_pi, 3d_models, structure, integration"
            return 1
            ;;
    esac
}

# Função auxiliar para filtrar testes por componente
run_hardware_tests_filter() {
    local filter=$1
    pytest tests/unit/ -k "$filter" -v
    print_success "Testes de $filter concluídos!"
}

# Função para verificar código antes de commit
pre_commit_check() {
    print_status "Executando verificação pré-commit..."
    
    # Executa testes rápidos
    print_status "Executando testes unitários..."
    pytest tests/unit/ -x --tb=short
    
    # Verifica formatação
    print_status "Verificando formatação do código..."
    black --check tests/ || print_warning "Código não formatado. Execute 'black tests/'"
    
    # Verifica imports
    print_status "Verificando organização de imports..."
    isort --check-only tests/ || print_warning "Imports não organizados. Execute 'isort tests/'"
    
    # Verifica linting
    print_status "Executando linting..."
    flake8 tests/ || print_warning "Problemas de linting encontrados."
    
    print_success "Verificação pré-commit concluída!"
}

# Função para mostrar ajuda
show_help() {
    echo -e "${BLUE}Uso:${NC}"
    echo "  $0 [comando] [opções]"
    echo ""
    echo -e "${BLUE}Comandos disponíveis:${NC}"
    echo "  all                    Executa todos os testes"
    echo "  unit                   Executa apenas testes unitários"
    echo "  integration            Executa testes de integração"
    echo "  hardware               Executa testes de hardware (Arduino, ESP32, Raspberry Pi)"
    echo "  3d                     Executa testes de modelos 3D"
    echo "  structure              Executa testes de estrutura do projeto"
    echo "  coverage               Executa testes com relatório de cobertura detalhado"
    echo "  parallel               Executa testes em paralelo"
    echo "  component <nome>       Executa testes de um componente específico"
    echo "  pre-commit             Executa verificação completa antes de commit"
    echo "  help                   Mostra esta ajuda"
    echo ""
    echo -e "${BLUE}Componentes para 'component':${NC}"
    echo "  arduino               Testes do Arduino"
    echo "  esp32                 Testes do ESP32"
    echo "  raspberry_pi          Testes do Raspberry Pi"
    echo "  3d_models             Testes dos modelos 3D"
    echo "  structure             Testes de estrutura do projeto"
    echo "  integration           Testes de integração"
    echo ""
    echo -e "${BLUE}Exemplos:${NC}"
    echo "  $0 all"
    echo "  $0 unit"
    echo "  $0 component arduino"
    echo "  $0 coverage"
    echo "  $0 pre-commit"
}

# Processa argumentos da linha de comando
case ${1:-help} in
    "all")
        run_all_tests
        ;;
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "hardware")
        run_hardware_tests
        ;;
    "3d")
        run_3d_tests
        ;;
    "structure")
        run_structure_tests
        ;;
    "coverage")
        run_coverage_report
        ;;
    "parallel")
        run_parallel_tests
        ;;
    "component")
        run_component_test "$2"
        ;;
    "pre-commit")
        pre_commit_check
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Comando não reconhecido: $1"
        show_help
        exit 1
        ;;
esac